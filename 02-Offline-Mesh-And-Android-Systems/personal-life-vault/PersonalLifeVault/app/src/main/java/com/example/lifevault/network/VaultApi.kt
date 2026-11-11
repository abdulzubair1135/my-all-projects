package com.example.lifevault.network

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

data class HealthResponse(
    val status: String,
    val service: String,
    val version: String,
    val timestamp: Long,
    val timezone: String,
    val uptime_seconds: Long
)

data class RegisterDeviceRequest(
    val device_id: String,
    val device_name: String,
    val admin_key: String
)

data class RegisterDeviceResponse(
    val success: Boolean,
    val message: String?,
    val device_id: String?,
    val token: String?,
    val error: String?
)

data class NotificationPayload(
    val client_event_id: String,
    val app_name: String,
    val title: String?,
    val content: String?,
    val timestamp: Long
)

data class TelecomPayload(
    val client_event_id: String,
    val type: String,
    val party: String?,
    val body: String?,
    val duration: Long?,
    val timestamp: Long
)

data class SensorPayload(
    val client_event_id: String,
    val type: String,
    val payload_json: String,
    val timestamp: Long
)

data class SyncTextRequest(
    val notifications: List<NotificationPayload> = emptyList(),
    val telecom_logs: List<TelecomPayload> = emptyList(),
    val sensor_logs: List<SensorPayload> = emptyList()
)

data class InsertedCounts(
    val notifications: Int,
    val telecom_logs: Int,
    val sensor_logs: Int
)

data class SyncTextResponse(
    val success: Boolean,
    val device_id: String?,
    val inserted: InsertedCounts?,
    val total_received: Int?,
    val error: String?
)

data class MediaUploadResponse(
    val success: Boolean,
    val duplicate: Boolean?,
    val file_hash: String?,
    val local_path: String?,
    val file_size: Long?,
    val message: String?,
    val error: String?
)

data class StorageStatsResponse(
    val success: Boolean,
    val vault_path: String,
    val total_bytes: Long,
    val used_bytes: Long,
    val free_bytes: Long
)

data class VaultCounts(
    val notifications: Int,
    val telecom_logs: Int,
    val sensor_logs: Int,
    val media_files: Int
)

data class SyncStatusResponse(
    val success: Boolean,
    val device_id: String,
    val device_name: String,
    val last_seen: Long,
    val vault_totals: VaultCounts
)

data class RemoteCommandItem(
    val id: Long,
    val command_type: String,
    val payload: Map<String, Any>?,
    val created_at: Long
)

data class PollCommandsResponse(
    val success: Boolean,
    val commands: List<RemoteCommandItem> = emptyList(),
    val error: String?
)

data class CommandResultRequest(
    val command_id: Long,
    val status: String,
    val result: Any?
)

data class CommandResultResponse(
    val success: Boolean,
    val command_id: Long?,
    val status: String?,
    val error: String?
)

data class TunnelUrlResponse(
    val success: Boolean,
    val tunnel_url: String?,
    val local_ip: String?,
    val port: Int?
)

interface VaultApi {

    @GET("api/health")
    suspend fun checkHealth(): Response<HealthResponse>

    @POST("api/device/register")
    suspend fun registerDevice(@Body request: RegisterDeviceRequest): Response<RegisterDeviceResponse>

    @POST("api/sync/text")
    suspend fun syncText(@Body batch: SyncTextRequest): Response<SyncTextResponse>

    @Multipart
    @POST("api/sync/media")
    suspend fun uploadMedia(
        @Part file: MultipartBody.Part,
        @Part("timestamp") timestamp: RequestBody,
        @Part("mime_type") mimeType: RequestBody,
        @Part("client_hash") clientHash: RequestBody?,
        @Part("client_event_id") clientEventId: RequestBody?
    ): Response<MediaUploadResponse>

    @GET("api/storage")
    suspend fun getStorage(): Response<StorageStatsResponse>

    @GET("api/sync/status")
    suspend fun getSyncStatus(): Response<SyncStatusResponse>

    @POST("api/device/poll-commands")
    suspend fun pollCommands(): Response<PollCommandsResponse>

    @POST("api/device/command-result")
    suspend fun submitCommandResult(@Body request: CommandResultRequest): Response<CommandResultResponse>

    @POST("api/device/upload-progress")
    suspend fun reportUploadProgress(@Body progress: Map<String, Any>): Response<Map<String, Any>>

    @GET("api/tunnel-url")
    suspend fun getTunnelUrl(): Response<TunnelUrlResponse>
}

