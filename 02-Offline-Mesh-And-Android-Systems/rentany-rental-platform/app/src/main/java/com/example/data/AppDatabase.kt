package com.example.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Database(
    entities = [
        UserProfileEntity::class,
        RentalItemEntity::class,
        BookingEntity::class,
        ChatMessageEntity::class,
        AppSettingsEntity::class,
        CartItemEntity::class
    ],
    version = 4,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userProfileDao(): UserProfileDao
    abstract fun rentalItemDao(): RentalItemDao
    abstract fun bookingDao(): BookingDao
    abstract fun chatMessageDao(): ChatMessageDao
    abstract fun appSettingsDao(): AppSettingsDao
    abstract fun cartItemDao(): CartItemDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "rentany_database"
                )
                .fallbackToDestructiveMigration()
                .addCallback(object : Callback() {
                    override fun onCreate(db: SupportSQLiteDatabase) {
                        super.onCreate(db)
                        // Trigger async initial data seed
                        INSTANCE?.let { database ->
                            CoroutineScope(Dispatchers.IO).launch {
                                seedInitialData(database)
                            }
                        }
                    }
                })
                .build()
                INSTANCE = instance
                instance
            }
        }

        suspend fun seedInitialData(db: AppDatabase) {
            // Seed profile
            db.userProfileDao().insertOrReplace(
                UserProfileEntity(
                    id = 1,
                    name = "Rohan Patel",
                    email = "rohanpatel@gmail.com",
                    phone = "+91 98765 43210",
                    dob = "15 May 1997",
                    gender = "Male",
                    address = "G-102, Sharnam Sky, Science City Road, Ahmedabad, Gujarat - 380060",
                    kycVerified = true,
                    walletBalance = 2450.0
                )
            )

            // Seed app settings
            db.appSettingsDao().insertOrReplace(
                AppSettingsEntity(
                    id = 1,
                    bookingUpdates = true,
                    messagesNotification = true,
                    offersNotification = false,
                    systemUpdates = true,
                    showOnlineStatus = true,
                    showPhoneNumber = false,
                    profileVisibilityPublic = true,
                    isDarkMode = false,
                    searchRadiusKm = 10,
                    useCurrentLocation = true,
                    backendUrl = "https://rentany-6hdf.onrender.com",
                    syncEnabled = true
                )
            )

            // Seed rental items
            db.rentalItemDao().insertAll(
                listOf(
                    RentalItemEntity(
                        id = 1,
                        name = "DSLR Camera",
                        category = "Electronics",
                        pricePerDay = 500.0,
                        securityDeposit = 2000.0,
                        description = "Canon EOS 200D II DSLR Camera with 18-55mm lens. Perfect for travel photography and high-quality portraits. Extremely well-maintained, user-friendly, and lightweight.",
                        imageUrl = "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=500",
                        rating = 4.8,
                        reviewsCount = 120,
                        ownerName = "Rohan Patel",
                        ownerRating = 4.9,
                        ownerReviewsCount = 85,
                        latitude = 23.0753,
                        longitude = 72.5076
                    ),
                    RentalItemEntity(
                        id = 2,
                        name = "Dinner Set",
                        category = "Utensils",
                        pricePerDay = 200.0,
                        securityDeposit = 1000.0,
                        description = "Luxurious ceramic dinner set, 24 pieces. Suitable for formal dinners, small family gatherings, or festival occasions.",
                        imageUrl = "https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&q=80&w=500",
                        rating = 4.6,
                        reviewsCount = 45,
                        ownerName = "Aarav Shah",
                        ownerRating = 4.5,
                        ownerReviewsCount = 12,
                        latitude = 23.0782,
                        longitude = 72.5115
                    ),
                    RentalItemEntity(
                        id = 3,
                        name = "HD Projector",
                        category = "Electronics",
                        pricePerDay = 600.0,
                        securityDeposit = 3000.0,
                        description = "Epson Full HD portable home theater projector. Built-in sound, HDMI and USB inputs, dual-band Wi-Fi. Ideal for terrace cinema nights or business pitches.",
                        imageUrl = "https://images.unsplash.com/photo-1535016120720-40c646be5580?auto=format&fit=crop&q=80&w=500",
                        rating = 4.7,
                        reviewsCount = 32,
                        ownerName = "Kabir Mehta",
                        ownerRating = 4.6,
                        ownerReviewsCount = 20,
                        latitude = 23.0725,
                        longitude = 72.5042
                    ),
                    RentalItemEntity(
                        id = 4,
                        name = "Bose Sound System",
                        category = "Electronics",
                        pricePerDay = 800.0,
                        securityDeposit = 2000.0,
                        description = "Bose Solo Soundbar Series II. Clear, crystal voice amplification and cinematic deep bass. Easily pairs via Bluetooth or optical cable.",
                        imageUrl = "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&q=80&w=500",
                        rating = 4.9,
                        reviewsCount = 88,
                        ownerName = "Rohan Patel",
                        ownerRating = 4.9,
                        ownerReviewsCount = 85,
                        latitude = 23.0740,
                        longitude = 72.5085
                    ),
                    RentalItemEntity(
                        id = 5,
                        name = "Camping Tent",
                        category = "Camping",
                        pricePerDay = 400.0,
                        securityDeposit = 1500.0,
                        description = "Coleman Sundome 4-Person camping tent. Completely waterproof, excellent ventilation system, and takes less than 10 minutes to pitch. Perfect for weekend getaways.",
                        imageUrl = "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&q=80&w=500",
                        rating = 4.5,
                        reviewsCount = 18,
                        ownerName = "Pooja Trivedi",
                        ownerRating = 4.7,
                        ownerReviewsCount = 9,
                        latitude = 23.0801,
                        longitude = 72.5099
                    ),
                    RentalItemEntity(
                        id = 6,
                        name = "Drill Machine",
                        category = "Tools",
                        pricePerDay = 300.0,
                        securityDeposit = 800.0,
                        description = "Bosch GSB professional impact drill kit. Includes 100 accessories (drill bits, hammers, pliers, screws). High performance and robust build for all DIY needs.",
                        imageUrl = "https://images.unsplash.com/photo-1504148455328-c376907d081c?auto=format&fit=crop&q=80&w=500",
                        rating = 4.4,
                        reviewsCount = 12,
                        ownerName = "Rajesh Kumar",
                        ownerRating = 4.3,
                        ownerReviewsCount = 14,
                        latitude = 23.0711,
                        longitude = 72.5122
                    )
                )
            )

            // Seed initial chats
            db.chatMessageDao().insertMessage(
                ChatMessageEntity(
                    itemId = 1,
                    senderName = "Rohan Patel",
                    messageText = "Hi! Is the camera still available on May 20?",
                    isUserMessage = false,
                    timestamp = System.currentTimeMillis() - 600000
                )
            )
            db.chatMessageDao().insertMessage(
                ChatMessageEntity(
                    itemId = 1,
                    senderName = "Me",
                    messageText = "Yes, it is available.",
                    isUserMessage = true,
                    timestamp = System.currentTimeMillis() - 500000
                )
            )
        }
    }
}
