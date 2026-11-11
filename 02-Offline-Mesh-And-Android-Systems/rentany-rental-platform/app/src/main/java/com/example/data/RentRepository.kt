package com.example.data

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.withContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.CoroutineDispatcher
import com.example.data.api.RentApiService
import com.example.data.api.RetrofitClient

class RentRepository(
    private val db: AppDatabase,
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {

    val userProfile: Flow<UserProfileEntity?> = db.userProfileDao().getUserProfile()
    val rentalItems: Flow<List<RentalItemEntity>> = db.rentalItemDao().getAllItems()
    val bookings: Flow<List<BookingEntity>> = db.bookingDao().getAllBookings()
    val settings: Flow<AppSettingsEntity?> = db.appSettingsDao().getSettings()
    val allMessages: Flow<List<ChatMessageEntity>> = db.chatMessageDao().getAllMessages()
    val cartItems: Flow<List<CartItemEntity>> = db.cartItemDao().getAllCartItems()

    fun getMessagesForItem(itemId: Int): Flow<List<ChatMessageEntity>> {
        return db.chatMessageDao().getMessagesForItem(itemId)
    }

    private suspend fun getApiService(): RentApiService? {
        val currentSettings = db.appSettingsDao().getSettings().firstOrNull()
        val url = if (currentSettings != null && currentSettings.backendUrl.isNotEmpty()) {
            currentSettings.backendUrl
        } else {
            "https://rentany-6hdf.onrender.com"
        }
        return RetrofitClient.getService(url)
    }

    suspend fun checkAndSeedDatabase() {
        withContext(ioDispatcher) {
            val items = db.rentalItemDao().getAllItems().firstOrNull()
            if (items.isNullOrEmpty()) {
                AppDatabase.seedInitialData(db)
            }
            // Trigger auto sync on startup if enabled
            syncWithBackend()
        }
    }

    suspend fun syncWithBackend(): Boolean {
        return withContext(ioDispatcher) {
            val api = getApiService() ?: return@withContext false
            try {
                // 1. Pull / Push Profile
                try {
                    val remoteProfile = api.getUserProfile()
                    db.userProfileDao().insertOrReplace(remoteProfile)
                } catch (e: Exception) {
                    val localProfile = db.userProfileDao().getUserProfile().firstOrNull()
                    if (localProfile != null) {
                        api.updateUserProfile(localProfile)
                    }
                }

                // 2. Pull / Push Settings
                try {
                    val remoteSettings = api.getAppSettings()
                    val localSettings = db.appSettingsDao().getSettings().firstOrNull()
                    if (localSettings != null) {
                        db.appSettingsDao().insertOrReplace(
                            remoteSettings.copy(
                                backendUrl = localSettings.backendUrl,
                                syncEnabled = localSettings.syncEnabled
                            )
                        )
                    } else {
                        db.appSettingsDao().insertOrReplace(remoteSettings)
                    }
                } catch (e: Exception) {
                    val localSettings = db.appSettingsDao().getSettings().firstOrNull()
                    if (localSettings != null) {
                        api.updateAppSettings(localSettings)
                    }
                }

                // 3. Pull Rental Items
                val remoteItems = api.getRentalItems()
                if (remoteItems.isNotEmpty()) {
                    db.rentalItemDao().insertAll(remoteItems)
                }

                // 4. Pull Bookings
                val remoteBookings = api.getBookings()
                for (booking in remoteBookings) {
                    db.bookingDao().insertBooking(booking)
                }

                true
            } catch (e: Exception) {
                e.printStackTrace()
                false
            }
        }
    }

    suspend fun fetchMessagesFromBackend(itemId: Int) {
        withContext(ioDispatcher) {
            val api = getApiService() ?: return@withContext
            try {
                val remoteMessages = api.getMessagesForItem(itemId)
                for (msg in remoteMessages) {
                    db.chatMessageDao().insertMessage(msg)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    suspend fun insertBooking(booking: BookingEntity): Long {
        return withContext(ioDispatcher) {
            val localId = db.bookingDao().insertBooking(booking)
            val api = getApiService()
            if (api != null) {
                try {
                    api.insertBooking(booking.copy(id = localId.toInt()))
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            localId
        }
    }

    suspend fun insertMessage(message: ChatMessageEntity): Long {
        return withContext(ioDispatcher) {
            val localId = db.chatMessageDao().insertMessage(message)
            val api = getApiService()
            if (api != null) {
                try {
                    api.insertMessage(message.copy(id = localId.toInt()))
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            localId
        }
    }

    suspend fun insertRentalItem(item: RentalItemEntity): Long {
        return withContext(ioDispatcher) {
            val localId = db.rentalItemDao().insertItem(item)
            val api = getApiService()
            if (api != null) {
                try {
                    api.insertRentalItem(item.copy(id = localId.toInt()))
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            localId
        }
    }

    suspend fun updateUserProfile(profile: UserProfileEntity) {
        withContext(ioDispatcher) {
            db.userProfileDao().insertOrReplace(profile)
            val api = getApiService()
            if (api != null) {
                try {
                    api.updateUserProfile(profile)
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }

    suspend fun updateAppSettings(settings: AppSettingsEntity) {
        withContext(ioDispatcher) {
            db.appSettingsDao().insertOrReplace(settings)
            val api = getApiService()
            if (api != null) {
                try {
                    api.updateAppSettings(settings)
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }

    suspend fun toggleBookmark(itemId: Int, currentBookmarkState: Boolean) {
        withContext(ioDispatcher) {
            db.rentalItemDao().updateBookmark(itemId, !currentBookmarkState)
        }
    }

    suspend fun addWalletBalance(amount: Double) {
        withContext(ioDispatcher) {
            val currentProfile = db.userProfileDao().getUserProfile().firstOrNull()
            if (currentProfile != null) {
                db.userProfileDao().insertOrReplace(
                    currentProfile.copy(walletBalance = currentProfile.walletBalance + amount)
                )
                // If sync is enabled, update remote profile
                val api = getApiService()
                if (api != null) {
                    try {
                        api.updateUserProfile(currentProfile.copy(walletBalance = currentProfile.walletBalance + amount))
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
            }
        }
    }

    suspend fun insertCartItem(item: CartItemEntity): Long {
        return withContext(ioDispatcher) {
            db.cartItemDao().insertCartItem(item)
        }
    }

    suspend fun deleteCartItem(id: Int) {
        withContext(ioDispatcher) {
            db.cartItemDao().deleteCartItem(id)
        }
    }

    suspend fun clearCart() {
        withContext(ioDispatcher) {
            db.cartItemDao().clearCart()
        }
    }

    suspend fun getCartItemByItemId(itemId: Int): CartItemEntity? {
        return withContext(ioDispatcher) {
            db.cartItemDao().getCartItemByItemId(itemId)
        }
    }
}

