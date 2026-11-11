package com.example.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "user_profile")
data class UserProfileEntity(
    @PrimaryKey val id: Int = 1,
    val name: String,
    val email: String,
    val phone: String,
    val dob: String,
    val gender: String,
    val address: String,
    val kycVerified: Boolean,
    val walletBalance: Double = 2450.0
)

@Entity(tableName = "rental_items")
data class RentalItemEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val name: String,
    val category: String,
    val pricePerDay: Double,
    val securityDeposit: Double,
    val description: String,
    val imageUrl: String,
    val rating: Double,
    val reviewsCount: Int,
    val ownerName: String,
    val ownerRating: Double,
    val ownerReviewsCount: Int,
    val latitude: Double,
    val longitude: Double,
    val isBookmarked: Boolean = false
)

@Entity(tableName = "bookings")
data class BookingEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val itemId: Int,
    val itemName: String,
    val itemImageUrl: String,
    val startDate: String,
    val endDate: String,
    val deliveryType: String, // "Self Pickup" or "Delivery"
    val totalPrice: Double,
    val status: String, // "Upcoming", "Ongoing", "Completed"
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "chat_messages")
data class ChatMessageEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val itemId: Int,
    val senderName: String,
    val messageText: String,
    val timestamp: Long = System.currentTimeMillis(),
    val isUserMessage: Boolean
)

@Entity(tableName = "app_settings")
data class AppSettingsEntity(
    @PrimaryKey val id: Int = 1,
    val bookingUpdates: Boolean = true,
    val messagesNotification: Boolean = true,
    val offersNotification: Boolean = false,
    val systemUpdates: Boolean = true,
    val showOnlineStatus: Boolean = true,
    val showPhoneNumber: Boolean = false,
    val profileVisibilityPublic: Boolean = true,
    val isDarkMode: Boolean = false,
    val searchRadiusKm: Int = 10,
    val useCurrentLocation: Boolean = true,
    val backendUrl: String = "",
    val syncEnabled: Boolean = false
)

@Entity(tableName = "cart_items")
data class CartItemEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val itemId: Int,
    val itemName: String,
    val itemImageUrl: String,
    val pricePerDay: Double,
    val securityDeposit: Double,
    val durationDays: Int = 1,
    val deliveryType: String = "Self Pickup"
)
