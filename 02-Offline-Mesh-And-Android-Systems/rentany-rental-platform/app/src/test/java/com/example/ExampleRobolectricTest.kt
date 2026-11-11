package com.example

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.example.data.*
import com.example.ui.RentViewModel
import com.example.ui.Screen
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.setMain
import kotlinx.coroutines.test.resetMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowLooper

// Helper extensions for testing Room Flows
suspend fun <T> Flow<T?>.firstNonNull(): T {
    var value = this.first()
    while (value == null) {
        delay(10)
        ShadowLooper.idleMainLooper()
        value = this.first()
    }
    return value
}

suspend fun <T> Flow<List<T>>.firstNonEmpty(): List<T> {
    var value = this.first()
    while (value.isEmpty()) {
        delay(10)
        ShadowLooper.idleMainLooper()
        value = this.first()
    }
    return value
}

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class ExampleRobolectricTest {

    private lateinit var db: AppDatabase
    private lateinit var repository: RentRepository
    private lateinit var viewModel: RentViewModel

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        // In-memory Room Database for ultra fast, isolated test environment
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        repository = RentRepository(db, Dispatchers.Main)
        viewModel = RentViewModel(repository)
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun `read string from context`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val appName = context.getString(R.string.app_name)
        assertEquals("RentAny", appName)
    }

    @Test
    fun `database initial seeding populates correct profile and items`() = runBlocking {
        AppDatabase.seedInitialData(db)

        val profile = repository.userProfile.firstNonNull()
        assertNotNull(profile)
        assertEquals("Rohan Patel", profile.name)
        assertEquals(2450.0, profile.walletBalance, 0.01)

        val items = repository.rentalItems.firstNonEmpty()
        assertEquals(6, items.size)
        assertEquals("Drill Machine", items.first().name) // ordered by id DESC
    }

    @Test
    fun `viewModel navigation flow works correctly`() = runBlocking {
        val job = launch { viewModel.currentScreen.collect {} }
        delay(10)
        ShadowLooper.idleMainLooper()

        assertEquals(Screen.Splash, viewModel.currentScreen.value)

        viewModel.navigateTo(Screen.Login)
        delay(10)
        ShadowLooper.idleMainLooper()
        assertEquals(Screen.Login, viewModel.currentScreen.value)

        viewModel.navigateTo(Screen.Home)
        delay(10)
        ShadowLooper.idleMainLooper()
        assertEquals(Screen.Home, viewModel.currentScreen.value)

        viewModel.navigateBack()
        delay(10)
        ShadowLooper.idleMainLooper()
        assertEquals(Screen.Login, viewModel.currentScreen.value)

        job.cancel()
    }

    @Test
    fun `viewModel publishing new item inserts item into database`() = runBlocking {
        AppDatabase.seedInitialData(db)

        val jobItems = launch { viewModel.itemsState.collect {} }
        val jobProfile = launch { viewModel.profileState.collect {} }

        // Let the state flows initialize
        ShadowLooper.idleMainLooper()
        val startInit = System.currentTimeMillis()
        while (viewModel.profileState.value == null && System.currentTimeMillis() - startInit < 2000) {
            delay(10)
            ShadowLooper.idleMainLooper()
        }

        viewModel.addFormName.value = "Sony Headphones"
        viewModel.addFormCategory.value = "Electronics"
        viewModel.addFormPrice.value = "250"
        viewModel.addFormSecurityDeposit.value = "1000"
        viewModel.addFormDescription.value = "Noise canceling Sony WH-1000XM4 headphones."

        var successCalled = false
        viewModel.publishRentalItem {
            successCalled = true
        }

        // Let Robolectric execute publishRentalItem coroutine
        ShadowLooper.idleMainLooper()

        // Wait up to 2 seconds for successCalled to be true (handles Dispatchers.IO execution)
        val start = System.currentTimeMillis()
        while (!successCalled && System.currentTimeMillis() - start < 2000) {
            delay(10)
            ShadowLooper.idleMainLooper()
        }

        assertEquals(true, successCalled)
        
        // Wait up to 2 seconds for stateflow items to count 7
        val itemsStart = System.currentTimeMillis()
        while (viewModel.itemsState.value.size != 7 && System.currentTimeMillis() - itemsStart < 2000) {
            delay(10)
            ShadowLooper.idleMainLooper()
        }
        
        val items = viewModel.itemsState.value
        assertEquals(7, items.size)
        val published = items.find { it.name == "Sony Headphones" }
        assertNotNull(published)
        assertEquals(250.0, published?.pricePerDay ?: 0.0, 0.01)

        jobItems.cancel()
        jobProfile.cancel()
    }

    @Test
    fun `viewModel adding wallet money updates balance`() = runBlocking {
        AppDatabase.seedInitialData(db)

        val jobProfile = launch { viewModel.profileState.collect {} }

        // Let state flow initialize
        ShadowLooper.idleMainLooper()
        val startInit = System.currentTimeMillis()
        while (viewModel.profileState.value == null && System.currentTimeMillis() - startInit < 2000) {
            delay(10)
            ShadowLooper.idleMainLooper()
        }

        viewModel.addWalletMoney(500.0)
        ShadowLooper.idleMainLooper()

        // Wait up to 2 seconds for wallet balance to be updated to 2950.0
        val start = System.currentTimeMillis()
        while ((viewModel.profileState.value?.walletBalance ?: 0.0) != 2950.0 && System.currentTimeMillis() - start < 2000) {
            delay(10)
            ShadowLooper.idleMainLooper()
        }

        assertEquals(2950.0, viewModel.profileState.value?.walletBalance ?: 0.0, 0.01)

        jobProfile.cancel()
    }
}
