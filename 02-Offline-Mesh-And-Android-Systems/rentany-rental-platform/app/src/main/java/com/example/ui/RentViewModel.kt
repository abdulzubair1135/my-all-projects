package com.example.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.data.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

sealed class Screen {
    object Splash : Screen()
    object Login : Screen()
    object SignUp : Screen()
    object Home : Screen()
    object Explore : Screen()
    object ExploreMap : Screen()
    data class ItemDetails(val itemId: Int) : Screen()
    data class Booking(val itemId: Int) : Screen()
    data class Payment(val itemId: Int, val bookingDays: Int, val deliveryType: String) : Screen()
    data class BookingConfirmed(val itemId: Int, val itemName: String, val itemImageUrl: String, val totalPrice: Double, val dates: String) : Screen()
    object MyBookings : Screen()
    object MyWallet : Screen()
    data class Chat(val itemId: Int) : Screen()
    object AddRental : Screen()
    object Profile : Screen()
    object Categories : Screen()
    object Settings : Screen()
    object AccountSettings : Screen()
    object Security : Screen()
    object PaymentMethods : Screen()
    object Notifications : Screen()
    object Privacy : Screen()
    object Location : Screen()
    object CloudSyncSettings : Screen()
    object HelpSupport : Screen()
    object About : Screen()
    object MoreFeatures : Screen()
    object Inbox : Screen()
    object Cart : Screen()
}

class RentViewModel(private val repository: RentRepository) : ViewModel() {

    // Central state
    val profileState: StateFlow<UserProfileEntity?> = repository.userProfile
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)

    val itemsState: StateFlow<List<RentalItemEntity>> = repository.rentalItems
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val bookingsState: StateFlow<List<BookingEntity>> = repository.bookings
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val settingsState: StateFlow<AppSettingsEntity?> = repository.settings
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)

    val allMessagesState: StateFlow<List<ChatMessageEntity>> = repository.allMessages
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val cartItemsState: StateFlow<List<CartItemEntity>> = repository.cartItems
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    // Navigation Backstack
    private val _backstack = MutableStateFlow<List<Screen>>(listOf(Screen.Splash))
    val currentScreen: StateFlow<Screen> = _backstack
        .map { it.lastOrNull() ?: Screen.Home }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Screen.Splash)

    // Search and Filter State
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _selectedCategory = MutableStateFlow<String?>(null)
    val selectedCategory: StateFlow<String?> = _selectedCategory.asStateFlow()

    // Temporary/Draft values (Add Rental Item)
    val addFormName = MutableStateFlow("")
    val addFormCategory = MutableStateFlow("Electronics")
    val addFormPrice = MutableStateFlow("")
    val addFormSecurityDeposit = MutableStateFlow("")
    val addFormDescription = MutableStateFlow("")
    val addFormImageUrl = MutableStateFlow("")

    // Booking configuration state
    val bookingStartDate = MutableStateFlow("May 20, 2026")
    val bookingEndDate = MutableStateFlow("May 23, 2026")
    val bookingDeliveryType = MutableStateFlow("Self Pickup") // or "Delivery"

    // Sync state
    private val _syncStatus = MutableStateFlow<String?>(null)
    val syncStatus: StateFlow<String?> = _syncStatus.asStateFlow()

    init {
        viewModelScope.launch {
            repository.checkAndSeedDatabase()
        }
        // Auto-sync every 30 seconds for real-time experience
        viewModelScope.launch {
            while (true) {
                kotlinx.coroutines.delay(30_000L)
                repository.syncWithBackend()
            }
        }
    }

    // Navigation actions
    fun navigateTo(screen: Screen) {
        val currentList = _backstack.value.toMutableList()
        // Prevent duplicate consecutive screens
        if (currentList.lastOrNull() != screen) {
            currentList.add(screen)
            _backstack.value = currentList
        }
        if (screen is Screen.Chat) {
            viewModelScope.launch {
                repository.fetchMessagesFromBackend(screen.itemId)
            }
        }
    }

    fun triggerSync(onResult: (Boolean) -> Unit = {}) {
        viewModelScope.launch {
            _syncStatus.value = "Syncing..."
            val success = repository.syncWithBackend()
            _syncStatus.value = if (success) "Sync successful" else "Sync failed"
            onResult(success)
        }
    }

    fun clearSyncStatus() {
        _syncStatus.value = null
    }

    fun navigateBack(): Boolean {
        val currentList = _backstack.value.toMutableList()
        if (currentList.size > 1) {
            currentList.removeAt(currentList.size - 1)
            _backstack.value = currentList
            return true
        }
        return false
    }

    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
    }

    fun selectCategory(category: String?) {
        _selectedCategory.value = if (_selectedCategory.value == category) null else category
    }

    // Business interactions
    fun toggleBookmark(itemId: Int, currentBookmark: Boolean) {
        viewModelScope.launch {
            repository.toggleBookmark(itemId, currentBookmark)
        }
    }

    fun addWalletMoney(amount: Double) {
        viewModelScope.launch {
            repository.addWalletBalance(amount)
        }
    }

    fun getDefaultCategoryImageUrl(cat: String): String {
        return when (cat) {
            "Electronics" -> "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=500"
            "Utensils" -> "https://images.unsplash.com/photo-1543087903-1ac2ec7aa8c5?auto=format&fit=crop&q=80&w=500"
            "Furniture" -> "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&q=80&w=500"
            "Tools" -> "https://images.unsplash.com/photo-1530124566582-ab05130f9cd1?auto=format&fit=crop&q=80&w=500"
            "Party Items" -> "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&q=80&w=500"
            "Sports" -> "https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&q=80&w=500"
            "Camping" -> "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&q=80&w=500"
            else -> "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=500"
        }
    }

    fun publishRentalItem(onSuccess: () -> Unit) {
        viewModelScope.launch {
            val price = addFormPrice.value.toDoubleOrNull() ?: 0.0
            val deposit = addFormSecurityDeposit.value.toDoubleOrNull() ?: 0.0
            val finalImgUrl = addFormImageUrl.value.ifEmpty { getDefaultCategoryImageUrl(addFormCategory.value) }
            val newItem = RentalItemEntity(
                name = addFormName.value.ifEmpty { "Unnamed Item" },
                category = addFormCategory.value,
                pricePerDay = price,
                securityDeposit = deposit,
                description = addFormDescription.value.ifEmpty { "No description provided." },
                imageUrl = finalImgUrl,
                rating = 5.0,
                reviewsCount = 1,
                ownerName = profileState.value?.name ?: "Rohan Patel",
                ownerRating = 4.9,
                ownerReviewsCount = 85,
                latitude = 23.0760,
                longitude = 72.5090
            )
            repository.insertRentalItem(newItem)
            // Reset form
            addFormName.value = ""
            addFormPrice.value = ""
            addFormSecurityDeposit.value = ""
            addFormDescription.value = ""
            addFormImageUrl.value = ""
            onSuccess()
        }
    }

    fun submitBooking(itemId: Int, totalPrice: Double, itemName: String, itemImageUrl: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            val booking = BookingEntity(
                itemId = itemId,
                itemName = itemName,
                itemImageUrl = itemImageUrl,
                startDate = bookingStartDate.value,
                endDate = bookingEndDate.value,
                deliveryType = bookingDeliveryType.value,
                totalPrice = totalPrice,
                status = "Upcoming"
            )
            repository.insertBooking(booking)
            onSuccess()
        }
    }

    fun getMessagesForItem(itemId: Int): Flow<List<ChatMessageEntity>> {
        return repository.getMessagesForItem(itemId)
    }

    fun sendChatMessage(itemId: Int, text: String) {
        if (text.isBlank()) return
        viewModelScope.launch {
            repository.insertMessage(
                ChatMessageEntity(
                    itemId = itemId,
                    senderName = "Me",
                    messageText = text,
                    isUserMessage = true
                )
            )
        }
    }

    fun updateProfile(profile: UserProfileEntity) {
        viewModelScope.launch {
            repository.updateUserProfile(profile)
        }
    }

    fun updateSettings(settings: AppSettingsEntity) {
        viewModelScope.launch {
            repository.updateAppSettings(settings)
        }
    }

    fun addToCart(item: RentalItemEntity, days: Int = 1, deliveryType: String = "Self Pickup", onSuccess: () -> Unit = {}) {
        viewModelScope.launch {
            val existing = cartItemsState.value.find { it.itemId == item.id }
            if (existing != null) {
                repository.insertCartItem(existing.copy(durationDays = existing.durationDays + days))
            } else {
                val cartItem = CartItemEntity(
                    itemId = item.id,
                    itemName = item.name,
                    itemImageUrl = item.imageUrl,
                    pricePerDay = item.pricePerDay,
                    securityDeposit = item.securityDeposit,
                    durationDays = days,
                    deliveryType = deliveryType
                )
                repository.insertCartItem(cartItem)
            }
            onSuccess()
        }
    }

    fun updateCartItemDuration(cartItemId: Int, newDuration: Int) {
        if (newDuration < 1) return
        viewModelScope.launch {
            val current = cartItemsState.value.find { it.id == cartItemId }
            if (current != null) {
                repository.insertCartItem(current.copy(durationDays = newDuration))
            }
        }
    }

    fun updateCartItemDeliveryType(cartItemId: Int, deliveryType: String) {
        viewModelScope.launch {
            val current = cartItemsState.value.find { it.id == cartItemId }
            if (current != null) {
                repository.insertCartItem(current.copy(deliveryType = deliveryType))
            }
        }
    }

    fun removeFromCart(cartItemId: Int) {
        viewModelScope.launch {
            repository.deleteCartItem(cartItemId)
        }
    }

    fun clearCart() {
        viewModelScope.launch {
            repository.clearCart()
        }
    }

    fun checkoutCart(onSuccess: () -> Unit) {
        viewModelScope.launch {
            val cartItems = cartItemsState.value
            if (cartItems.isEmpty()) return@launch

            for (cartItem in cartItems) {
                val totalPrice = (cartItem.pricePerDay * cartItem.durationDays) + cartItem.securityDeposit
                val booking = BookingEntity(
                    itemId = cartItem.itemId,
                    itemName = cartItem.itemName,
                    itemImageUrl = cartItem.itemImageUrl,
                    startDate = bookingStartDate.value,
                    endDate = bookingEndDate.value,
                    deliveryType = cartItem.deliveryType,
                    totalPrice = totalPrice,
                    status = "Upcoming"
                )
                repository.insertBooking(booking)
            }
            repository.clearCart()
            onSuccess()
        }
    }
}


class RentViewModelFactory(private val repository: RentRepository) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(RentViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return RentViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
