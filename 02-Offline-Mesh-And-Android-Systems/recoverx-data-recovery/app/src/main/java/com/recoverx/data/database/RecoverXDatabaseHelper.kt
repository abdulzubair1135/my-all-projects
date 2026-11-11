package com.recoverx.data.database

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import com.recoverx.data.entities.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class RecoverXDatabaseHelper(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        const val DATABASE_NAME = "recoverx.db"
        const val DATABASE_VERSION = 1

        // Table Names
        const val TABLE_SCAN_SESSIONS = "scan_sessions"
        const val TABLE_DISCOVERED_ITEMS = "discovered_items"
        const val TABLE_RECOVERY_RECORDS = "recovery_records"
        const val TABLE_SCAN_ERRORS = "scan_errors"
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE $TABLE_SCAN_SESSIONS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_type TEXT NOT NULL,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                sources_inspected TEXT NOT NULL,
                files_inspected INTEGER NOT NULL DEFAULT 0,
                candidate_count INTEGER NOT NULL DEFAULT 0,
                error_count INTEGER NOT NULL DEFAULT 0
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $TABLE_DISCOVERED_ITEMS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                uri_string TEXT NOT NULL,
                display_name TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                date_modified INTEGER NOT NULL,
                category TEXT NOT NULL,
                classification TEXT NOT NULL,
                readability TEXT NOT NULL,
                relative_path TEXT,
                original_extension TEXT,
                detected_extension TEXT,
                is_mime_mismatch INTEGER NOT NULL DEFAULT 0,
                hash_sha256 TEXT,
                FOREIGN KEY (session_id) REFERENCES $TABLE_SCAN_SESSIONS(id) ON DELETE CASCADE
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $TABLE_RECOVERY_RECORDS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                source_uri TEXT NOT NULL,
                destination_uri TEXT,
                destination_path TEXT,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                bytes_written INTEGER NOT NULL DEFAULT 0,
                validation_summary TEXT,
                error_message TEXT
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $TABLE_SCAN_ERRORS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                error_category TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """.trimIndent())
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS $TABLE_SCAN_ERRORS")
        db.execSQL("DROP TABLE IF EXISTS $TABLE_RECOVERY_RECORDS")
        db.execSQL("DROP TABLE IF EXISTS $TABLE_DISCOVERED_ITEMS")
        db.execSQL("DROP TABLE IF EXISTS $TABLE_SCAN_SESSIONS")
        onCreate(db)
    }

    // DAO Methods
    suspend fun insertScanSession(session: ScanSession): Long = withContext(Dispatchers.IO) {
        val cv = ContentValues().apply {
            put("scan_type", session.scanType.name)
            put("start_time", session.startTimeMs)
            put("end_time", session.endTimeMs)
            put("status", session.status)
            put("sources_inspected", session.sourcesInspected)
            put("files_inspected", session.filesInspected)
            put("candidate_count", session.candidateCount)
            put("error_count", session.errorCount)
        }
        writableDatabase.insert(TABLE_SCAN_SESSIONS, null, cv)
    }

    suspend fun updateScanSession(session: ScanSession) = withContext(Dispatchers.IO) {
        val cv = ContentValues().apply {
            put("end_time", session.endTimeMs)
            put("status", session.status)
            put("files_inspected", session.filesInspected)
            put("candidate_count", session.candidateCount)
            put("error_count", session.errorCount)
        }
        writableDatabase.update(TABLE_SCAN_SESSIONS, cv, "id = ?", arrayOf(session.id.toString()))
    }

    suspend fun getRecentScanSessions(limit: Int = 20): List<ScanSession> = withContext(Dispatchers.IO) {
        val list = mutableListOf<ScanSession>()
        val cursor = readableDatabase.query(
            TABLE_SCAN_SESSIONS,
            null,
            null,
            null,
            null,
            null,
            "start_time DESC",
            limit.toString()
        )
        cursor.use {
            while (it.moveToNext()) {
                list.add(it.toScanSession())
            }
        }
        list
    }

    suspend fun insertDiscoveredItems(items: List<DiscoveredItem>): List<DiscoveredItem> = withContext(Dispatchers.IO) {
        val resultList = ArrayList<DiscoveredItem>(items.size)
        val db = writableDatabase
        db.beginTransaction()
        try {
            for (item in items) {
                val cv = ContentValues().apply {
                    put("session_id", item.sessionId)
                    put("uri_string", item.uriString)
                    put("display_name", item.displayName)
                    put("mime_type", item.mimeType)
                    put("size_bytes", item.sizeBytes)
                    put("date_modified", item.dateModifiedMs)
                    put("category", item.category.name)
                    put("classification", item.classification.name)
                    put("readability", item.readability.name)
                    put("relative_path", item.relativePath)
                    put("original_extension", item.originalExtension)
                    put("detected_extension", item.detectedExtension)
                    put("is_mime_mismatch", if (item.isMimeMismatch) 1 else 0)
                    put("hash_sha256", item.hashSha256)
                }
                val rowId = db.insert(TABLE_DISCOVERED_ITEMS, null, cv)
                resultList.add(item.copy(id = rowId))
            }
            db.setTransactionSuccessful()
        } finally {
            db.endTransaction()
        }
        resultList
    }

    suspend fun getDiscoveredItemById(id: Long): DiscoveredItem? = withContext(Dispatchers.IO) {
        val cursor = readableDatabase.query(
            TABLE_DISCOVERED_ITEMS,
            null,
            "id = ?",
            arrayOf(id.toString()),
            null,
            null,
            null
        )
        cursor.use {
            if (it.moveToFirst()) {
                return@withContext it.toDiscoveredItem()
            }
        }
        null
    }

    suspend fun getRecoveryRecordById(id: Long): RecoveryRecord? = withContext(Dispatchers.IO) {
        val cursor = readableDatabase.query(
            TABLE_RECOVERY_RECORDS,
            null,
            "id = ?",
            arrayOf(id.toString()),
            null,
            null,
            null
        )
        cursor.use {
            if (it.moveToFirst()) {
                return@withContext it.toRecoveryRecord()
            }
        }
        null
    }

    suspend fun getDiscoveredItems(
        sessionId: Long? = null,
        category: FileCategory? = null,
        classification: CandidateClassification? = null,
        limit: Int = 100
    ): List<DiscoveredItem> = withContext(Dispatchers.IO) {
        val list = mutableListOf<DiscoveredItem>()
        val selectionClauses = mutableListOf<String>()
        val selectionArgs = mutableListOf<String>()

        if (sessionId != null) {
            selectionClauses.add("session_id = ?")
            selectionArgs.add(sessionId.toString())
        }
        if (category != null) {
            selectionClauses.add("category = ?")
            selectionArgs.add(category.name)
        }
        if (classification != null) {
            selectionClauses.add("classification = ?")
            selectionArgs.add(classification.name)
        }

        val selection = if (selectionClauses.isEmpty()) null else selectionClauses.joinToString(" AND ")
        val args = if (selectionArgs.isEmpty()) null else selectionArgs.toTypedArray()

        val cursor = readableDatabase.query(
            TABLE_DISCOVERED_ITEMS,
            null,
            selection,
            args,
            null,
            null,
            "id DESC",
            limit.toString()
        )
        cursor.use {
            while (it.moveToNext()) {
                list.add(it.toDiscoveredItem())
            }
        }
        list
    }

    suspend fun insertRecoveryRecord(record: RecoveryRecord): Long = withContext(Dispatchers.IO) {
        val cv = ContentValues().apply {
            put("item_id", record.itemId)
            put("original_name", record.originalName)
            put("source_uri", record.sourceUri)
            put("destination_uri", record.destinationUri)
            put("destination_path", record.destinationPath)
            put("start_time", record.startTimeMs)
            put("end_time", record.endTimeMs)
            put("status", record.status.name)
            put("bytes_written", record.bytesWritten)
            put("validation_summary", record.validationSummary)
            put("error_message", record.errorMessage)
        }
        writableDatabase.insert(TABLE_RECOVERY_RECORDS, null, cv)
    }

    suspend fun updateRecoveryRecord(record: RecoveryRecord) = withContext(Dispatchers.IO) {
        val cv = ContentValues().apply {
            put("end_time", record.endTimeMs)
            put("status", record.status.name)
            put("bytes_written", record.bytesWritten)
            put("validation_summary", record.validationSummary)
            put("error_message", record.errorMessage)
        }
        writableDatabase.update(TABLE_RECOVERY_RECORDS, cv, "id = ?", arrayOf(record.id.toString()))
    }

    suspend fun getRecoveryRecords(limit: Int = 50): List<RecoveryRecord> = withContext(Dispatchers.IO) {
        val list = mutableListOf<RecoveryRecord>()
        val cursor = readableDatabase.query(
            TABLE_RECOVERY_RECORDS,
            null,
            null,
            null,
            null,
            null,
            "start_time DESC",
            limit.toString()
        )
        cursor.use {
            while (it.moveToNext()) {
                list.add(it.toRecoveryRecord())
            }
        }
        list
    }

    suspend fun clearAllHistory() = withContext(Dispatchers.IO) {
        val db = writableDatabase
        db.delete(TABLE_SCAN_ERRORS, null, null)
        db.delete(TABLE_RECOVERY_RECORDS, null, null)
        db.delete(TABLE_DISCOVERED_ITEMS, null, null)
        db.delete(TABLE_SCAN_SESSIONS, null, null)
    }

    private fun Cursor.toScanSession(): ScanSession {
        return ScanSession(
            id = getLong(getColumnIndexOrThrow("id")),
            scanType = ScanType.valueOf(getString(getColumnIndexOrThrow("scan_type"))),
            startTimeMs = getLong(getColumnIndexOrThrow("start_time")),
            endTimeMs = getLong(getColumnIndexOrThrow("end_time")),
            status = getString(getColumnIndexOrThrow("status")),
            sourcesInspected = getString(getColumnIndexOrThrow("sources_inspected")),
            filesInspected = getInt(getColumnIndexOrThrow("files_inspected")),
            candidateCount = getInt(getColumnIndexOrThrow("candidate_count")),
            errorCount = getInt(getColumnIndexOrThrow("error_count"))
        )
    }

    private fun Cursor.toDiscoveredItem(): DiscoveredItem {
        return DiscoveredItem(
            id = getLong(getColumnIndexOrThrow("id")),
            sessionId = getLong(getColumnIndexOrThrow("session_id")),
            uriString = getString(getColumnIndexOrThrow("uri_string")),
            displayName = getString(getColumnIndexOrThrow("display_name")),
            mimeType = getString(getColumnIndexOrThrow("mime_type")),
            sizeBytes = getLong(getColumnIndexOrThrow("size_bytes")),
            dateModifiedMs = getLong(getColumnIndexOrThrow("date_modified")),
            category = FileCategory.valueOf(getString(getColumnIndexOrThrow("category"))),
            classification = CandidateClassification.valueOf(getString(getColumnIndexOrThrow("classification"))),
            readability = ReadabilityStatus.valueOf(getString(getColumnIndexOrThrow("readability"))),
            relativePath = getString(getColumnIndexOrThrow("relative_path")),
            originalExtension = getString(getColumnIndexOrThrow("original_extension")),
            detectedExtension = getString(getColumnIndexOrThrow("detected_extension")),
            isMimeMismatch = getInt(getColumnIndexOrThrow("is_mime_mismatch")) == 1,
            hashSha256 = getString(getColumnIndexOrThrow("hash_sha256"))
        )
    }

    private fun Cursor.toRecoveryRecord(): RecoveryRecord {
        return RecoveryRecord(
            id = getLong(getColumnIndexOrThrow("id")),
            itemId = getLong(getColumnIndexOrThrow("item_id")),
            originalName = getString(getColumnIndexOrThrow("original_name")),
            sourceUri = getString(getColumnIndexOrThrow("source_uri")),
            destinationUri = getString(getColumnIndexOrThrow("destination_uri")),
            destinationPath = getString(getColumnIndexOrThrow("destination_path")),
            startTimeMs = getLong(getColumnIndexOrThrow("start_time")),
            endTimeMs = getLong(getColumnIndexOrThrow("end_time")),
            status = RecoveryStatus.valueOf(getString(getColumnIndexOrThrow("status"))),
            bytesWritten = getLong(getColumnIndexOrThrow("bytes_written")),
            validationSummary = getString(getColumnIndexOrThrow("validation_summary")),
            errorMessage = getString(getColumnIndexOrThrow("error_message"))
        )
    }
}
