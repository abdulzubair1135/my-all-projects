package com.example.data.api

import com.example.data.*
import retrofit2.http.*

interface RentApiService {
    @GET("api/profile")
    suspend fun getUserProfile(): UserProfileEntity

    @POST("api/profile")
    suspend fun updateUserProfile(@Body profile: UserProfileEntity): UserProfileEntity

    @GET("api/items")
    suspend fun getRentalItems(): List<RentalItemEntity>

    @POST("api/items")
    suspend fun insertRentalItem(@Body item: RentalItemEntity): RentalItemEntity

    @GET("api/bookings")
    suspend fun getBookings(): List<BookingEntity>

    @POST("api/bookings")
    suspend fun insertBooking(@Body booking: BookingEntity): BookingEntity

    @GET("api/chats/{itemId}")
    suspend fun getMessagesForItem(@Path("itemId") itemId: Int): List<ChatMessageEntity>

    @POST("api/chats")
    suspend fun insertMessage(@Body message: ChatMessageEntity): ChatMessageEntity

    @GET("api/settings")
    suspend fun getAppSettings(): AppSettingsEntity

    @POST("api/settings")
    suspend fun updateAppSettings(@Body settings: AppSettingsEntity): AppSettingsEntity
}
