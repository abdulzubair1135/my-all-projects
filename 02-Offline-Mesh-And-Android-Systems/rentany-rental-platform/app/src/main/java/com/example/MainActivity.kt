package com.example

import android.os.Bundle
import android.widget.Toast
import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.speech.RecognizerIntent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.data.*
import com.example.ui.*
import com.example.ui.theme.RentAnyTheme
import com.example.ui.theme.RentAnyGreen
import com.example.ui.theme.RentAnyGreenDark
import com.example.ui.theme.RentAnyGold
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var viewModel: RentViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val app = application as RentAnyApplication
        val factory = RentViewModelFactory(app.repository)
        viewModel = ViewModelProvider(this, factory)[RentViewModel::class.java]

        // Custom back button handling
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (!viewModel.navigateBack()) {
                    finish()
                }
            }
        })

        setContent {
            val currentScreen by viewModel.currentScreen.collectAsStateWithLifecycle()
            val settingsState by viewModel.settingsState.collectAsStateWithLifecycle()
            val isDarkTheme = settingsState?.isDarkMode ?: false

            RentAnyTheme(darkTheme = isDarkTheme) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    RentAnyAppContent(viewModel = viewModel, currentScreen = currentScreen)
                }
            }
        }
    }
}

@OptIn(ExperimentalAnimationApi::class)
@Composable
fun RentAnyAppContent(viewModel: RentViewModel, currentScreen: Screen) {
    // Dynamic Responsive design: check if expanded screen width (tablets)
    BoxWithConstraints(modifier = Modifier.fillMaxSize()) {
        val isExpanded = maxWidth >= 600.dp

        if (isExpanded && currentScreen !is Screen.Splash && currentScreen !is Screen.Login) {
            // Split layout or sidebar for wide screens (tablets)
            Row(modifier = Modifier.fillMaxSize()) {
                // Left side: Sidebar Navigation
                Column(
                    modifier = Modifier
                        .width(240.dp)
                        .fillMaxHeight()
                        .background(MaterialTheme.colorScheme.surfaceVariant)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "RentAny",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = RentAnyGreen,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    SidebarItem(
                        icon = Icons.Default.Home,
                        label = "Home",
                        selected = currentScreen is Screen.Home,
                        onClick = { viewModel.navigateTo(Screen.Home) }
                    )
                    SidebarItem(
                        icon = Icons.Default.Category,
                        label = "Categories",
                        selected = currentScreen is Screen.Categories,
                        onClick = { viewModel.navigateTo(Screen.Categories) }
                    )
                    SidebarItem(
                        icon = Icons.Default.Add,
                        label = "Publish",
                        selected = currentScreen is Screen.AddRental,
                        onClick = { viewModel.navigateTo(Screen.AddRental) }
                    )
                    SidebarItem(
                        icon = Icons.Default.DateRange,
                        label = "My Bookings",
                        selected = currentScreen is Screen.MyBookings,
                        onClick = { viewModel.navigateTo(Screen.MyBookings) }
                    )
                    SidebarItem(
                        icon = Icons.Default.Person,
                        label = "Profile",
                        selected = currentScreen is Screen.Profile || currentScreen is Screen.Settings,
                        onClick = { viewModel.navigateTo(Screen.Profile) }
                    )
                }

                // Divider
                VerticalDivider(color = MaterialTheme.colorScheme.outlineVariant)

                // Right side: Main screen content with transitions
                Box(modifier = Modifier.fillMaxSize()) {
                    AnimatedContent(
                        targetState = currentScreen,
                        transitionSpec = {
                            fadeIn() with fadeOut()
                        }
                    ) { screen ->
                        ScreenRenderer(viewModel = viewModel, screen = screen, isExpanded = true)
                    }
                }
            }
        } else {
            // Standard layout for mobile/vertical screens
            Scaffold(
                bottomBar = {
                    if (currentScreen !is Screen.Splash && currentScreen !is Screen.Login) {
                        RentAnyBottomBar(viewModel = viewModel, currentScreen = currentScreen)
                    }
                }
            ) { innerPadding ->
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                ) {
                    AnimatedContent(
                        targetState = currentScreen,
                        transitionSpec = {
                            slideInHorizontally(initialOffsetX = { 300 }) + fadeIn() with
                                    slideOutHorizontally(targetOffsetX = { -300 }) + fadeOut()
                        }
                    ) { screen ->
                        ScreenRenderer(viewModel = viewModel, screen = screen, isExpanded = false)
                    }
                }
            }
        }
    }
}

@Composable
fun SidebarItem(
    icon: ImageVector,
    label: String,
    selected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(12.dp),
        color = if (selected) MaterialTheme.colorScheme.primary else Color.Transparent,
        contentColor = if (selected) Color.White else MaterialTheme.colorScheme.onSurface,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Icon(imageVector = icon, contentDescription = label)
            Text(text = label, fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal)
        }
    }
}

@Composable
fun ScreenRenderer(viewModel: RentViewModel, screen: Screen, isExpanded: Boolean) {
    when (screen) {
        is Screen.Splash -> SplashScreenView(viewModel)
        is Screen.Login -> LoginScreenView(viewModel)
        is Screen.SignUp -> SignUpScreenView(viewModel)
        is Screen.Home -> HomeScreenView(viewModel, isExpanded)
        is Screen.Explore -> ExploreScreenView(viewModel)
        is Screen.ExploreMap -> ExploreMapScreenView(viewModel)
        is Screen.Cart -> CartScreenView(viewModel)
        is Screen.ItemDetails -> ItemDetailsScreenView(viewModel, screen.itemId)
        is Screen.Booking -> BookingScreenView(viewModel, screen.itemId)
        is Screen.Payment -> PaymentScreenView(viewModel, screen.itemId, screen.bookingDays, screen.deliveryType)
        is Screen.BookingConfirmed -> BookingConfirmedScreenView(viewModel, screen.itemId, screen.itemName, screen.itemImageUrl, screen.totalPrice, screen.dates)
        is Screen.MyBookings -> MyBookingsScreenView(viewModel)
        is Screen.MyWallet -> MyWalletScreenView(viewModel)
        is Screen.Chat -> ChatScreenView(viewModel, screen.itemId)
        is Screen.AddRental -> AddRentalScreenView(viewModel)
        is Screen.Profile -> ProfileScreenView(viewModel)
        is Screen.Categories -> CategoriesScreenView(viewModel)
        is Screen.Settings -> SettingsScreenView(viewModel)
        is Screen.AccountSettings -> AccountSettingsView(viewModel)
        is Screen.Security -> SecuritySettingsView(viewModel)
        is Screen.PaymentMethods -> PaymentMethodsView(viewModel)
        is Screen.Notifications -> NotificationSettingsView(viewModel)
        is Screen.Privacy -> PrivacySettingsView(viewModel)
        is Screen.Location -> LocationSettingsView(viewModel)
        is Screen.CloudSyncSettings -> CloudSyncSettingsView(viewModel)
        is Screen.HelpSupport -> HelpSupportView(viewModel)
        is Screen.About -> AboutRentAnyView(viewModel)
        is Screen.MoreFeatures -> MoreFeaturesView(viewModel)
        is Screen.Inbox -> InboxScreenView(viewModel)
    }
}

@Composable
fun RentAnyBottomBar(viewModel: RentViewModel, currentScreen: Screen) {
    NavigationBar(
        containerColor = MaterialTheme.colorScheme.surface,
        tonalElevation = 8.dp
    ) {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
            label = { Text("Home") },
            selected = currentScreen is Screen.Home,
            onClick = { viewModel.navigateTo(Screen.Home) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Search, contentDescription = "Explore") },
            label = { Text("Explore") },
            selected = currentScreen is Screen.Explore || currentScreen is Screen.ExploreMap,
            onClick = { viewModel.navigateTo(Screen.Explore) }
        )
        NavigationBarItem(
            icon = {
                Surface(
                    shape = CircleShape,
                    color = RentAnyGreen,
                    modifier = Modifier.size(32.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(Icons.Default.Add, contentDescription = "List", tint = Color.White, modifier = Modifier.size(20.dp))
                    }
                }
            },
            label = { Text("List") },
            selected = currentScreen is Screen.AddRental,
            onClick = { viewModel.navigateTo(Screen.AddRental) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.DateRange, contentDescription = "Activity") },
            label = { Text("Activity") },
            selected = currentScreen is Screen.MyBookings,
            onClick = { viewModel.navigateTo(Screen.MyBookings) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Person, contentDescription = "Profile") },
            label = { Text("Profile") },
            selected = currentScreen is Screen.Profile || currentScreen is Screen.Settings,
            onClick = { viewModel.navigateTo(Screen.Profile) }
        )
    }
}

// ================= SPLASH SCREEN =================
@Composable
fun SplashScreenView(viewModel: RentViewModel) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier.padding(24.dp)
        ) {
            Spacer(modifier = Modifier.height(16.dp))

            // Main Dual-Color Logo
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "Rent",
                    style = MaterialTheme.typography.displayMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Text(
                    text = "Any",
                    style = MaterialTheme.typography.displayMedium,
                    fontWeight = FontWeight.Bold,
                    color = RentAnyGreen
                )
            }

            Text(
                text = "Rent. Return. Repeat",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Use our generated image asset
            val context = LocalContext.current
            val imageResId = remember {
                val resId = context.resources.getIdentifier(
                    "img_rentany_hero_1782900008071",
                    "drawable",
                    context.packageName
                )
                if (resId != 0) resId else null
            }

            if (imageResId != null) {
                Image(
                    painter = painterResource(id = imageResId),
                    contentDescription = "RentAny Hero Illustration",
                    modifier = Modifier
                        .size(260.dp)
                        .clip(RoundedCornerShape(24.dp)),
                    contentScale = ContentScale.Crop
                )
            } else {
                // Fallback representation if not found
                Icon(
                    imageVector = Icons.Default.Share,
                    contentDescription = "Sharing illustration",
                    tint = RentAnyGreen,
                    modifier = Modifier.size(120.dp)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Rent. Return. Repeat",
                textAlign = TextAlign.Center,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            // Page indicators matching Screen 1 dot sliders
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(vertical = 12.dp)
            ) {
                Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(RentAnyGreen))
                Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(MaterialTheme.colorScheme.outlineVariant))
                Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(MaterialTheme.colorScheme.outlineVariant))
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { viewModel.navigateTo(Screen.Login) },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(24.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("get_started_button")
            ) {
                Text(
                    text = "Get Started",
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
                    fontSize = 16.sp
                )
            }
        }
    }
}

// ================= LOGIN SCREEN =================
@Composable
fun GoogleAccountRow(
    name: String,
    email: String,
    isAdd: Boolean = false,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = if (isAdd) MaterialTheme.colorScheme.outlineVariant else RentAnyGreen.copy(alpha = 0.15f),
                modifier = Modifier.size(36.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    if (isAdd) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    } else {
                        Text(
                            text = name.first().toString(),
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen
                        )
                    }
                }
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = name,
                    fontWeight = FontWeight.Bold,
                    style = MaterialTheme.typography.bodyMedium
                )
                Text(
                    text = email,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            if (!isAdd) {
                Surface(
                    shape = CircleShape,
                    color = RentAnyGreen.copy(alpha = 0.1f),
                    modifier = Modifier.size(16.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            text = "G",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreenView(viewModel: RentViewModel) {
    var email by remember { mutableStateOf("rohanpatel@gmail.com") }
    var password by remember { mutableStateOf("password123") }
    var emailError by remember { mutableStateOf<String?>(null) }
    var passwordError by remember { mutableStateOf<String?>(null) }
    var showGoogleChooser by remember { mutableStateOf(false) }
    var googleVerifyingAccount by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current

    if (showGoogleChooser) {
        AlertDialog(
            onDismissRequest = { 
                if (googleVerifyingAccount == null) {
                    showGoogleChooser = false 
                }
            },
            title = {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Surface(
                        shape = CircleShape,
                        color = RentAnyGreen.copy(alpha = 0.1f),
                        modifier = Modifier.size(36.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = Icons.Default.AccountCircle,
                                contentDescription = null,
                                tint = RentAnyGreen
                            )
                        }
                    }
                    Text(
                        text = "Verify with Google",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
            },
            text = {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    if (googleVerifyingAccount == null) {
                        Text(
                            text = "Choose a Google Account to securely log in and verify your identity on RentAny.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            GoogleAccountRow(
                                name = "Rohan Patel",
                                email = "rohanpatel@gmail.com",
                                onClick = {
                                    googleVerifyingAccount = "rohanpatel@gmail.com"
                                }
                            )

                            GoogleAccountRow(
                                name = "Diksha Singh",
                                email = "dikshasinghgun2006@gmail.com",
                                onClick = {
                                    googleVerifyingAccount = "dikshasinghgun2006@gmail.com"
                                }
                            )

                            GoogleAccountRow(
                                name = "Use another account",
                                email = "Sign in with a different Google account",
                                isAdd = true,
                                onClick = {
                                    googleVerifyingAccount = "custom"
                                }
                            )
                        }
                    } else {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            CircularProgressIndicator(
                                color = RentAnyGreen,
                                modifier = Modifier.size(48.dp)
                            )
                            
                            Text(
                                text = "Securing Google connection...",
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleMedium,
                                color = MaterialTheme.colorScheme.onSurface
                            )

                            var statusText by remember { mutableStateOf("Contacting authentication servers...") }
                            
                            LaunchedEffect(Unit) {
                                kotlinx.coroutines.delay(800)
                                statusText = "Verifying email & password signatures..."
                                kotlinx.coroutines.delay(800)
                                statusText = "Syncing Google Verified credentials..."
                                kotlinx.coroutines.delay(600)
                                
                                val verifiedName = when (googleVerifyingAccount) {
                                    "rohanpatel@gmail.com" -> "Rohan Patel"
                                    "dikshasinghgun2006@gmail.com" -> "Diksha Singh"
                                    else -> "RentAny User"
                                }
                                val verifiedEmail = if (googleVerifyingAccount == "custom") "new.user@gmail.com" else googleVerifyingAccount!!
                                
                                val verifiedProfile = UserProfileEntity(
                                    id = 1,
                                    name = verifiedName,
                                    email = verifiedEmail,
                                    phone = if (verifiedName == "Rohan Patel") "+91 98765 43210" else "+91 87654 32109",
                                    dob = "15 May 1997",
                                    gender = "Female",
                                    address = "G-102, Sharnam Sky, Science City Road, Ahmedabad, Gujarat - 380060",
                                    kycVerified = true,
                                    walletBalance = 2450.0
                                )
                                viewModel.updateProfile(verifiedProfile)
                                Toast.makeText(context, "Google Verification successful! Welcome, $verifiedName.", Toast.LENGTH_LONG).show()
                                
                                showGoogleChooser = false
                                googleVerifyingAccount = null
                                viewModel.navigateTo(Screen.Home)
                            }

                            Text(
                                text = statusText,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }
            },
            confirmButton = {
                if (googleVerifyingAccount == null) {
                    TextButton(onClick = { showGoogleChooser = false }) {
                        Text("Cancel", color = RentAnyGreen)
                    }
                }
            }
        )
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Spacer(modifier = Modifier.height(48.dp))

            Text(
                text = "Welcome Back 👋",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )

            Text(
                text = "Login to continue to the neighborhood marketplace",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.6f)
            )

            Spacer(modifier = Modifier.height(16.dp))

            OutlinedTextField(
                value = email,
                onValueChange = { 
                    email = it
                    emailError = null
                },
                label = { Text("Email or Phone") },
                modifier = Modifier.fillMaxWidth().testTag("email_input"),
                singleLine = true,
                isError = emailError != null,
                supportingText = if (emailError != null) {
                    { Text(emailError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                leadingIcon = { Icon(Icons.Default.Email, contentDescription = null) }
            )

            OutlinedTextField(
                value = password,
                onValueChange = { 
                    password = it
                    passwordError = null
                },
                label = { Text("Password") },
                modifier = Modifier.fillMaxWidth().testTag("password_input"),
                singleLine = true,
                isError = passwordError != null,
                supportingText = if (passwordError != null) {
                    { Text(passwordError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                visualTransformation = PasswordVisualTransformation(),
                leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null) }
            )

            Text(
                text = "Forgot Password?",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = RentAnyGreen,
                modifier = Modifier
                    .align(Alignment.End)
                    .clickable { }
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    emailError = null
                    passwordError = null

                    val isEmailEmpty = email.trim().isEmpty()
                    val isEmailValid = if (isEmailEmpty) {
                        false
                    } else {
                        val isEmailPattern = android.util.Patterns.EMAIL_ADDRESS.matcher(email.trim()).matches()
                        val isPhonePattern = email.trim().all { it.isDigit() || it == '+' || it == ' ' || it == '-' } && email.trim().replace(" ", "").replace("-", "").replace("+", "").length >= 10
                        isEmailPattern || isPhonePattern
                    }

                    val isPasswordValid = password.length >= 6

                    if (isEmailEmpty) {
                        emailError = "Email or Phone cannot be empty"
                    } else if (!isEmailValid) {
                        emailError = "Please enter a valid email or 10-digit phone number"
                    }

                    if (password.isEmpty()) {
                        passwordError = "Password cannot be empty"
                    } else if (!isPasswordValid) {
                        passwordError = "Password must be at least 6 characters"
                    }

                    if (emailError == null && passwordError == null) {
                        val finalName = if (email.contains("rohan", ignoreCase = true)) "Rohan Patel" else if (email.contains("diksha", ignoreCase = true)) "Diksha Singh" else email.substringBefore("@").replaceFirstChar { it.uppercase() }
                        val updatedProfile = UserProfileEntity(
                            id = 1,
                            name = finalName,
                            email = if (email.contains("@")) email else "$email@example.com",
                            phone = if (email.contains("@")) "+91 98765 43210" else email,
                            dob = "15 May 1997",
                            gender = "Female",
                            address = "G-102, Sharnam Sky, Science City Road, Ahmedabad, Gujarat - 380060",
                            kycVerified = true,
                            walletBalance = 2450.0
                        )
                        viewModel.updateProfile(updatedProfile)
                        viewModel.triggerSync()
                        Toast.makeText(context, "Welcome back, $finalName!", Toast.LENGTH_SHORT).show()
                        viewModel.navigateTo(Screen.Home)
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("login_button")
            ) {
                Text("Login", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            Text(
                text = "or continue with",
                style = MaterialTheme.typography.bodySmall,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth()
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = { showGoogleChooser = true },
                    modifier = Modifier.weight(1f).testTag("google_login_button"),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.AccountBox,
                        contentDescription = "Google Logo",
                        tint = RentAnyGreen
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Google", color = MaterialTheme.colorScheme.onBackground)
                }

                OutlinedButton(
                    onClick = { viewModel.navigateTo(Screen.Home) },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = "Apple Logo",
                        tint = MaterialTheme.colorScheme.onBackground
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Apple", color = MaterialTheme.colorScheme.onBackground)
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                Text("Don't have an account? ")
                Text(
                    text = "Sign Up",
                    fontWeight = FontWeight.Bold,
                    color = RentAnyGreen,
                    modifier = Modifier.clickable { viewModel.navigateTo(Screen.SignUp) }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignUpScreenView(viewModel: RentViewModel) {
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    
    var nameError by remember { mutableStateOf<String?>(null) }
    var emailError by remember { mutableStateOf<String?>(null) }
    var phoneError by remember { mutableStateOf<String?>(null) }
    var passwordError by remember { mutableStateOf<String?>(null) }
    var confirmPasswordError by remember { mutableStateOf<String?>(null) }
    
    val context = LocalContext.current

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Spacer(modifier = Modifier.height(32.dp))

            Text(
                text = "Create Account 📝",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )

            Text(
                text = "Sign up to join the neighborhood marketplace",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.6f)
            )

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = name,
                onValueChange = { 
                    name = it
                    nameError = null
                },
                label = { Text("Full Name") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                isError = nameError != null,
                supportingText = if (nameError != null) {
                    { Text(nameError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                leadingIcon = { Icon(Icons.Default.Person, contentDescription = null) }
            )

            OutlinedTextField(
                value = email,
                onValueChange = { 
                    email = it
                    emailError = null
                },
                label = { Text("Email Address") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                isError = emailError != null,
                supportingText = if (emailError != null) {
                    { Text(emailError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                leadingIcon = { Icon(Icons.Default.Email, contentDescription = null) }
            )

            OutlinedTextField(
                value = phone,
                onValueChange = { 
                    phone = it
                    phoneError = null
                },
                label = { Text("Phone Number") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                isError = phoneError != null,
                supportingText = if (phoneError != null) {
                    { Text(phoneError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                leadingIcon = { Icon(Icons.Default.Phone, contentDescription = null) }
            )

            OutlinedTextField(
                value = password,
                onValueChange = { 
                    password = it
                    passwordError = null
                },
                label = { Text("Password") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                isError = passwordError != null,
                supportingText = if (passwordError != null) {
                    { Text(passwordError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                visualTransformation = PasswordVisualTransformation(),
                leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null) }
            )

            OutlinedTextField(
                value = confirmPassword,
                onValueChange = { 
                    confirmPassword = it
                    confirmPasswordError = null
                },
                label = { Text("Confirm Password") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                isError = confirmPasswordError != null,
                supportingText = if (confirmPasswordError != null) {
                    { Text(confirmPasswordError!!, color = MaterialTheme.colorScheme.error) }
                } else null,
                visualTransformation = PasswordVisualTransformation(),
                leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null) }
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    nameError = null
                    emailError = null
                    phoneError = null
                    passwordError = null
                    confirmPasswordError = null

                    if (name.trim().isEmpty()) {
                        nameError = "Name cannot be empty"
                    }
                    if (email.trim().isEmpty()) {
                        emailError = "Email cannot be empty"
                    } else if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email.trim()).matches()) {
                        emailError = "Please enter a valid email"
                    }
                    if (phone.trim().isEmpty()) {
                        phoneError = "Phone number cannot be empty"
                    } else if (phone.trim().length < 10) {
                        phoneError = "Phone number must be at least 10 digits"
                    }
                    if (password.isEmpty()) {
                        passwordError = "Password cannot be empty"
                    } else if (password.length < 6) {
                        passwordError = "Password must be at least 6 characters"
                    }
                    if (confirmPassword != password) {
                        confirmPasswordError = "Passwords do not match"
                    }

                    if (nameError == null && emailError == null && phoneError == null && 
                        passwordError == null && confirmPasswordError == null) {
                        
                        val updatedProfile = UserProfileEntity(
                            id = 1,
                            name = name.trim(),
                            email = email.trim(),
                            phone = phone.trim(),
                            dob = "01 Jan 2000",
                            gender = "Male",
                            address = "Configure your address in profile settings",
                            kycVerified = true,
                            walletBalance = 500.0
                        )
                        viewModel.updateProfile(updatedProfile)
                        viewModel.triggerSync()
                        Toast.makeText(context, "Registration successful! Welcome, ${name.trim()}!", Toast.LENGTH_SHORT).show()
                        viewModel.navigateTo(Screen.Home)
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("Register", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.weight(1f))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                Text("Already have an account? ")
                Text(
                    text = "Login",
                    fontWeight = FontWeight.Bold,
                    color = RentAnyGreen,
                    modifier = Modifier.clickable { viewModel.navigateTo(Screen.Login) }
                )
            }
        }
    }
}


// ================= HOME SCREEN =================
@Composable
fun HomeScreenView(viewModel: RentViewModel, isExpanded: Boolean) {
    val context = LocalContext.current
    val voiceSearchLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val data = result.data
            val results = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val spokenText = results?.firstOrNull() ?: ""
            if (spokenText.isNotEmpty()) {
                viewModel.updateSearchQuery(spokenText)
            }
        }
    }

    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()
    val selectedCategory by viewModel.selectedCategory.collectAsStateWithLifecycle()
    val cartItems by viewModel.cartItemsState.collectAsStateWithLifecycle()
    val profile by viewModel.profileState.collectAsStateWithLifecycle()

    val walletBalance = profile?.walletBalance ?: 2450.0

    val topCategories = listOf(
        Pair("Vehicles", Icons.Default.DirectionsCar),
        Pair("Electronics", Icons.Default.Devices),
        Pair("Real Estate", Icons.Default.HomeWork),
        Pair("Furniture", Icons.Default.Chair),
        Pair("More", Icons.Default.GridView)
    )

    val filteredItems = items.filter { item ->
        val matchesSearch = item.name.contains(searchQuery, ignoreCase = true) ||
                item.description.contains(searchQuery, ignoreCase = true) ||
                item.category.contains(searchQuery, ignoreCase = true)
        val matchesCategory = selectedCategory == null || item.category == selectedCategory
        matchesSearch && matchesCategory
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Location & Wallet Header
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Current Location",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.clickable { viewModel.navigateTo(Screen.Location) }
                    ) {
                        Icon(
                            imageVector = Icons.Default.LocationOn,
                            contentDescription = "Location Pin",
                            tint = RentAnyGreen,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(2.dp))
                        Text(
                            text = "Bangalore, India",
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.titleMedium
                        )
                        Icon(
                            imageVector = Icons.Default.KeyboardArrowDown,
                            contentDescription = "Select Location",
                            tint = MaterialTheme.colorScheme.onSurface,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    // Wallet Balance Chip
                    Surface(
                        onClick = { viewModel.navigateTo(Screen.MyWallet) },
                        shape = RoundedCornerShape(20.dp),
                        color = RentAnyGreen.copy(alpha = 0.15f),
                        border = BorderStroke(1.dp, RentAnyGreen.copy(alpha = 0.3f))
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.AccountBalanceWallet,
                                contentDescription = "Wallet",
                                tint = RentAnyGreen,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = "₹${walletBalance.toInt()}",
                                color = RentAnyGreen,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }
                    }

                    // Bell Notification Button
                    Surface(
                        shape = CircleShape,
                        color = MaterialTheme.colorScheme.surfaceVariant,
                        modifier = Modifier.size(40.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            IconButton(onClick = { viewModel.navigateTo(Screen.Notifications) }) {
                                Icon(
                                    imageVector = Icons.Default.Notifications,
                                    contentDescription = "Notifications",
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                            Surface(
                                color = Color.Red,
                                shape = CircleShape,
                                modifier = Modifier
                                    .align(Alignment.TopEnd)
                                    .padding(4.dp)
                                    .size(8.dp)
                            ) {}
                        }
                    }
                }
            }
        }

        // Search Bar
        item {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { viewModel.updateSearchQuery(it) },
                placeholder = { Text("Search anything to rent...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("search_bar"),
                shape = RoundedCornerShape(12.dp),
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Search", tint = RentAnyGreen) },
                trailingIcon = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(end = 4.dp)
                    ) {
                        if (searchQuery.isNotEmpty()) {
                            IconButton(
                                onClick = { viewModel.updateSearchQuery("") },
                                modifier = Modifier.testTag("search_clear_button")
                            ) {
                                Icon(Icons.Default.Clear, contentDescription = "Clear")
                            }
                        }
                        IconButton(
                            onClick = {
                                val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                                    putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                                    putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak now to search...")
                                }
                                try {
                                    voiceSearchLauncher.launch(intent)
                                } catch (e: ActivityNotFoundException) {
                                    Toast.makeText(context, "Voice Search not supported on this device", Toast.LENGTH_SHORT).show()
                                }
                            },
                            modifier = Modifier.testTag("voice_search_button")
                        ) {
                            Icon(
                                imageVector = Icons.Default.Mic,
                                contentDescription = "Voice Search",
                                tint = RentAnyGreen
                            )
                        }
                        IconButton(onClick = { viewModel.navigateTo(Screen.Categories) }) {
                            Icon(
                                imageVector = Icons.Default.Tune,
                                contentDescription = "Filter",
                                tint = RentAnyGreen
                            )
                        }
                    }
                }
            )
        }

        // Promo Banner card
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(130.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = RentAnyGreenDark)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = "Flat 20% OFF",
                            color = Color.White,
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "On First Rental | Code: RENT20",
                            color = Color.White.copy(alpha = 0.9f),
                            fontSize = 12.sp
                        )
                        Spacer(modifier = Modifier.height(10.dp))
                        Button(
                            onClick = { viewModel.navigateTo(Screen.Explore) },
                            colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 4.dp),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text("Book Now", color = RentAnyGreenDark, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                        }
                    }

                    // Car Illustration Image
                    AsyncImage(
                        model = "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&q=80&w=300",
                        contentDescription = "Car Promo",
                        modifier = Modifier
                            .size(100.dp)
                            .clip(RoundedCornerShape(12.dp)),
                        contentScale = ContentScale.Crop
                    )
                }
            }
        }

        // Top Categories Header
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Top Categories",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "See all",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = RentAnyGreen,
                    modifier = Modifier.clickable { viewModel.navigateTo(Screen.Categories) }
                )
            }
        }

        // Categories circular icons row
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                topCategories.forEach { cat ->
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier
                            .clickable { viewModel.selectCategory(if (cat.first == "More") null else cat.first) }
                            .padding(4.dp)
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = RentAnyGreen.copy(alpha = 0.12f),
                            modifier = Modifier.size(54.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = cat.second,
                                    contentDescription = cat.first,
                                    tint = RentAnyGreen,
                                    modifier = Modifier.size(26.dp)
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = cat.first,
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }
        }

        // Nearby Rentals Header
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Nearby Rentals",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "See all",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    color = RentAnyGreen,
                    modifier = Modifier.clickable { viewModel.navigateTo(Screen.Explore) }
                )
            }
        }

        // Nearby Rentals Horizontal Row
        item {
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                items(filteredItems) { item ->
                    Card(
                        onClick = { viewModel.navigateTo(Screen.ItemDetails(item.id)) },
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                        modifier = Modifier.width(180.dp)
                    ) {
                        Column {
                            Box {
                                AsyncImage(
                                    model = item.imageUrl,
                                    contentDescription = item.name,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(110.dp),
                                    contentScale = ContentScale.Crop
                                )
                                Surface(
                                    shape = RoundedCornerShape(8.dp),
                                    color = Color.Black.copy(alpha = 0.6f),
                                    modifier = Modifier
                                        .align(Alignment.BottomEnd)
                                        .padding(6.dp)
                                ) {
                                    Text(
                                        text = "1.2 km",
                                        color = Color.White,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                    )
                                }
                            }
                            Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                Text(
                                    text = item.name,
                                    fontWeight = FontWeight.Bold,
                                    style = MaterialTheme.typography.bodyMedium,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "₹${item.pricePerDay.toInt()} / day",
                                        color = RentAnyGreen,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 13.sp
                                    )
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(Icons.Default.Star, contentDescription = null, tint = RentAnyGold, modifier = Modifier.size(12.dp))
                                        Text(text = "${item.rating}", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Section Trending Here
        item {
            Text(
                text = "Trending Here",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }

        // Item Cards layout
        if (filteredItems.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = "No items",
                            tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f),
                            modifier = Modifier.size(48.dp)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "No rental items match your criteria.",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        } else {
            if (isExpanded) {
                val chunkedItems = filteredItems.chunked(2)
                items(chunkedItems) { chunk ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        chunk.forEach { item ->
                            Box(modifier = Modifier.weight(1f)) {
                                RentalItemGridCard(item, viewModel)
                            }
                        }
                        if (chunk.size < 2) {
                            Spacer(modifier = Modifier.weight(1f))
                        }
                    }
                }
            } else {
                items(filteredItems) { item ->
                    RentalItemRowCard(item, viewModel)
                }
            }
        }
    }
}

data class CategoryItem(val name: String, val icon: ImageVector, val itemCount: String)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RentalItemRowCard(item: RentalItemEntity, viewModel: RentViewModel) {
    Card(
        onClick = { viewModel.navigateTo(Screen.ItemDetails(item.id)) },
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            AsyncImage(
                model = item.imageUrl,
                contentDescription = item.name,
                modifier = Modifier
                    .size(90.dp)
                    .clip(RoundedCornerShape(8.dp)),
                contentScale = ContentScale.Crop
            )

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = item.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )

                    IconButton(
                        onClick = { viewModel.toggleBookmark(item.id, item.isBookmarked) },
                        modifier = Modifier.size(24.dp)
                    ) {
                        Icon(
                            imageVector = if (item.isBookmarked) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                            contentDescription = "Bookmark",
                            tint = if (item.isBookmarked) Color.Red else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Text(
                    text = item.category,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(modifier = Modifier.height(4.dp))

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = "Rating",
                        tint = RentAnyGold,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = "${item.rating}",
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.bodySmall
                    )
                    Text(
                        text = "(${item.reviewsCount})",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(modifier = Modifier.height(4.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "₹${item.pricePerDay.toInt()}",
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen,
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = " / day",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    Surface(
                        shape = RoundedCornerShape(6.dp),
                        color = RentAnyGreen.copy(alpha = 0.12f)
                    ) {
                        Text(
                            text = "1.2 km",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RentalItemGridCard(item: RentalItemEntity, viewModel: RentViewModel) {
    Card(
        onClick = { viewModel.navigateTo(Screen.ItemDetails(item.id)) },
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column {
            Box(modifier = Modifier.height(120.dp)) {
                AsyncImage(
                    model = item.imageUrl,
                    contentDescription = item.name,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
                IconButton(
                    onClick = { viewModel.toggleBookmark(item.id, item.isBookmarked) },
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp)
                ) {
                    Icon(
                        imageVector = if (item.isBookmarked) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                        contentDescription = "Bookmark",
                        tint = if (item.isBookmarked) Color.Red else Color.White
                    )
                }
            }
            Column(modifier = Modifier.padding(12.dp)) {
                Text(text = item.name, fontWeight = FontWeight.Bold, maxLines = 1)
                Row(
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(text = "₹${item.pricePerDay.toInt()}/day", color = RentAnyGreen, fontWeight = FontWeight.Bold)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Star, contentDescription = null, tint = RentAnyGold, modifier = Modifier.size(14.dp))
                        Text(text = "${item.rating}", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}


// ================= EXPLORE SCREEN =================
@Composable
fun ExploreScreenView(viewModel: RentViewModel) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()
    var selectedTag by remember { mutableStateOf("All") }

    val recentSearches = listOf("Bike", "Laptop", "Camera", "Flat")
    val tags = listOf("All", "Nearby", "Instant Book", "Free Delivery")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Top Header
        Surface(
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 4.dp,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Explore Rentals",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    IconButton(onClick = { viewModel.navigateTo(Screen.ExploreMap) }) {
                        Icon(
                            imageVector = Icons.Default.Map,
                            contentDescription = "Map View",
                            tint = RentAnyGreen
                        )
                    }
                }

                // Search Bar
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { viewModel.updateSearchQuery(it) },
                    placeholder = { Text("Search bikes, laptops, cameras, flats...") },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Search", tint = RentAnyGreen) },
                    trailingIcon = {
                        Row {
                            IconButton(onClick = { }) {
                                Icon(Icons.Default.Mic, contentDescription = "Mic", tint = RentAnyGreen)
                            }
                            IconButton(onClick = { viewModel.navigateTo(Screen.Categories) }) {
                                Icon(Icons.Default.Tune, contentDescription = "Filter", tint = RentAnyGreen)
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                )

                // Recent Searches
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(text = "Recent Searches", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(recentSearches) { search ->
                            SuggestionChip(
                                onClick = { viewModel.updateSearchQuery(search) },
                                label = { Text(search) },
                                icon = { Icon(Icons.Default.History, contentDescription = null, modifier = Modifier.size(14.dp)) }
                            )
                        }
                    }
                }

                // Filter Tags
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(tags) { tag ->
                        FilterChip(
                            selected = selectedTag == tag,
                            onClick = { selectedTag = tag },
                            label = { Text(tag) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = RentAnyGreen,
                                selectedLabelColor = Color.White
                            )
                        )
                    }
                }
            }
        }

        val filteredList = items.filter { item ->
            val matchesQuery = item.name.contains(searchQuery, ignoreCase = true) ||
                    item.category.contains(searchQuery, ignoreCase = true)
            when (selectedTag) {
                "Nearby" -> matchesQuery && item.latitude > 0
                "Instant Book" -> matchesQuery && item.rating >= 4.7
                "Free Delivery" -> matchesQuery && item.pricePerDay <= 600
                else -> matchesQuery
            }
        }

        LazyColumn(
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            items(filteredList) { item ->
                RentalItemRowCard(item = item, viewModel = viewModel)
            }
        }
    }
}

// ================= EXPLORE MAP SCREEN =================
@Composable
fun ExploreMapScreenView(viewModel: RentViewModel) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val selectedItem = items.firstOrNull() ?: RentalItemEntity(
        id = 1, name = "Royal Enfield Classic 350", category = "Vehicles", pricePerDay = 499.0,
        securityDeposit = 2000.0, description = "Well maintained bike", imageUrl = "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&q=80&w=500",
        rating = 4.8, reviewsCount = 128, ownerName = "Arjun Singh", ownerRating = 4.9, ownerReviewsCount = 85, latitude = 23.0753, longitude = 72.5076
    )

    Box(modifier = Modifier.fillMaxSize()) {
        // Map Canvas simulation
        Canvas(modifier = Modifier.fillMaxSize()) {
            drawRect(color = Color(0xFFE5E7EB))
            // Draw simulated map grid lines
            val w = size.width
            val h = size.height
            for (i in 0..10) {
                drawLine(
                    color = Color.White,
                    start = Offset(0f, h * i / 10f),
                    end = Offset(w, h * i / 10f),
                    strokeWidth = 12f
                )
                drawLine(
                    color = Color.White,
                    start = Offset(w * i / 10f, 0f),
                    end = Offset(w * i / 10f, h),
                    strokeWidth = 12f
                )
            }
        }

        // Price Pins overlaid on map
        Box(modifier = Modifier.fillMaxSize()) {
            // Pin 1
            Surface(
                color = RentAnyGreen,
                shape = RoundedCornerShape(16.dp),
                shadowElevation = 6.dp,
                modifier = Modifier
                    .align(Alignment.Center)
                    .offset(x = (-60).dp, y = (-80).dp)
                    .clickable { viewModel.navigateTo(Screen.ItemDetails(1)) }
            ) {
                Text(
                    text = "₹499",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                )
            }

            // Pin 2
            Surface(
                color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(16.dp),
                shadowElevation = 6.dp,
                modifier = Modifier
                    .align(Alignment.Center)
                    .offset(x = 80.dp, y = (-140).dp)
            ) {
                Text(
                    text = "₹1,100",
                    color = RentAnyGreenDark,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                )
            }

            // Pin 3
            Surface(
                color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(16.dp),
                shadowElevation = 6.dp,
                modifier = Modifier
                    .align(Alignment.Center)
                    .offset(x = (-100).dp, y = 60.dp)
            ) {
                Text(
                    text = "₹200",
                    color = RentAnyGreenDark,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                )
            }

            // Pin 4
            Surface(
                color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(16.dp),
                shadowElevation = 6.dp,
                modifier = Modifier
                    .align(Alignment.Center)
                    .offset(x = 90.dp, y = 80.dp)
            ) {
                Text(
                    text = "₹12,000",
                    color = RentAnyGreenDark,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                )
            }
        }

        // Top Search Bar
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = MaterialTheme.colorScheme.surface,
            shadowElevation = 6.dp,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .align(Alignment.TopCenter)
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = { viewModel.navigateBack() }) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                }
                Text(
                    text = "Bangalore, India",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                IconButton(onClick = { viewModel.navigateTo(Screen.Explore) }) {
                    Icon(Icons.Default.List, contentDescription = "List View", tint = RentAnyGreen)
                }
            }
        }

        // Bottom Selected Item Sheet
        Card(
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .align(Alignment.BottomCenter)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    AsyncImage(
                        model = selectedItem.imageUrl,
                        contentDescription = selectedItem.name,
                        modifier = Modifier
                            .size(70.dp)
                            .clip(RoundedCornerShape(12.dp)),
                        contentScale = ContentScale.Crop
                    )

                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = selectedItem.name,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Star, contentDescription = null, tint = RentAnyGold, modifier = Modifier.size(14.dp))
                            Text(text = " ${selectedItem.rating} (128 reviews) • 1.2 km", style = MaterialTheme.typography.bodySmall)
                        }
                        Text(
                            text = "₹${selectedItem.pricePerDay.toInt()} / day",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen
                        )
                    }

                    IconButton(onClick = { viewModel.toggleBookmark(selectedItem.id, selectedItem.isBookmarked) }) {
                        Icon(
                            imageVector = if (selectedItem.isBookmarked) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                            contentDescription = "Wishlist",
                            tint = if (selectedItem.isBookmarked) Color.Red else MaterialTheme.colorScheme.onSurface
                        )
                    }
                }

                Button(
                    onClick = { viewModel.navigateTo(Screen.ItemDetails(selectedItem.id)) },
                    colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                ) {
                    Text("View Details", fontWeight = FontWeight.Bold, color = Color.White, fontSize = 15.sp)
                }
            }
        }
    }
}

// ================= BOOKING CONFIRMED SCREEN =================
@Composable
fun BookingConfirmedScreenView(
    viewModel: RentViewModel,
    itemId: Int,
    itemName: String,
    itemImageUrl: String,
    totalPrice: Double,
    dates: String
) {
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
    ) {
        // Confetti header background
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(RentAnyGreen.copy(alpha = 0.12f))
                .padding(vertical = 36.dp, horizontal = 24.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Surface(
                    shape = CircleShape,
                    color = RentAnyGreen,
                    modifier = Modifier.size(80.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = "Success Checkmark",
                            tint = Color.White,
                            modifier = Modifier.size(48.dp)
                        )
                    }
                }

                Text(
                    text = "Booking Confirmed!",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = RentAnyGreenDark
                )

                Text(
                    text = "Your booking has been confirmed. Enjoy your ride!",
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Details Card
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        AsyncImage(
                            model = if (itemImageUrl.isNotEmpty()) itemImageUrl else "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&q=80&w=500",
                            contentDescription = itemName,
                            modifier = Modifier
                                .size(64.dp)
                                .clip(RoundedCornerShape(8.dp)),
                            contentScale = ContentScale.Crop
                        )
                        Column {
                            Text(text = if (itemName.isNotEmpty()) itemName else "Royal Enfield Classic 350", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                            Text(text = "Booking ID: RNT2024051401", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }

                    HorizontalDivider()

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Rental Dates:", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(text = if (dates.isNotEmpty()) dates else "14 May, 10:00 AM - 16 May, 10:00 AM", fontWeight = FontWeight.Bold)
                    }

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Total Amount Paid:", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text(text = "₹${totalPrice.toInt()}", fontWeight = FontWeight.Bold, color = RentAnyGreen)
                    }
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = { viewModel.navigateTo(Screen.MyBookings) },
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.weight(1f).height(48.dp)
                ) {
                    Text("View Booking", fontWeight = FontWeight.Bold)
                }

                OutlinedButton(
                    onClick = { Toast.makeText(context, "Guidelines downloaded to your device", Toast.LENGTH_SHORT).show() },
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.weight(1f).height(48.dp)
                ) {
                    Text("Guidelines", fontWeight = FontWeight.Bold)
                }
            }

            Button(
                onClick = {
                    val shareIntent = Intent(Intent.ACTION_SEND).apply {
                        type = "text/plain"
                        putExtra(Intent.EXTRA_TEXT, "I just booked $itemName on RentAny! Check out RentAny for easy rentals.")
                    }
                    context.startActivity(Intent.createChooser(shareIntent, "Share Booking"))
                },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp)
            ) {
                Icon(Icons.Default.Share, contentDescription = "Share", tint = Color.White)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Share Booking", fontWeight = FontWeight.Bold, color = Color.White, fontSize = 16.sp)
            }
        }
    }
}

// ================= MY WALLET SCREEN =================
@Composable
fun MyWalletScreenView(viewModel: RentViewModel) {
    val profile by viewModel.profileState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val walletBalance = profile?.walletBalance ?: 2450.0

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
    ) {
        // Header
        Surface(
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 4.dp,
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                IconButton(onClick = { viewModel.navigateBack() }) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                }
                Text("My Wallet", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            }
        }

        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            // Main Green Balance Card
            Card(
                colors = CardDefaults.cardColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Total Balance", color = Color.White.copy(alpha = 0.8f), style = MaterialTheme.typography.bodyMedium)
                            Text("₹${walletBalance.toInt()}", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold, color = Color.White)
                        }

                        Button(
                            onClick = { Toast.makeText(context, "Add Money option opened", Toast.LENGTH_SHORT).show() },
                            colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                            shape = RoundedCornerShape(12.dp),
                            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                        ) {
                            Text("+ Add Money", color = RentAnyGreen, fontWeight = FontWeight.Bold)
                        }
                    }

                    HorizontalDivider(color = Color.White.copy(alpha = 0.2f))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Wallet Balance: ₹2,250", color = Color.White.copy(alpha = 0.9f), fontSize = 13.sp)
                        Text("Security Deposit: ₹200", color = Color.White.copy(alpha = 0.9f), fontSize = 13.sp)
                    }
                }
            }

            // Quick Actions Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                listOf(
                    Pair("Add Money", Icons.Default.AddCircle),
                    Pair("Withdraw", Icons.Default.AccountBalance),
                    Pair("History", Icons.Default.ReceiptLong),
                    Pair("Offers", Icons.Default.LocalOffer)
                ).forEach { action ->
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier
                            .clickable { Toast.makeText(context, "${action.first} clicked", Toast.LENGTH_SHORT).show() }
                            .padding(8.dp)
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = RentAnyGreen.copy(alpha = 0.12f),
                            modifier = Modifier.size(52.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(action.second, contentDescription = action.first, tint = RentAnyGreen)
                            }
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(action.first, style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Invite & Earn Banner
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CardGiftcard, contentDescription = null, tint = RentAnyGreen, modifier = Modifier.size(36.dp))
                        Column {
                            Text("Invite & Earn", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                            Text("Invite friends & get ₹100 cashback", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }

                    Button(
                        onClick = { Toast.makeText(context, "Referral link copied!", Toast.LENGTH_SHORT).show() },
                        colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text("Invite Now", fontSize = 12.sp)
                    }
                }
            }

            // Recent Transactions
            Text("Recent Transactions", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)

            listOf(
                Triple("Royal Enfield Classic 350", "- ₹998", "14 May 2024"),
                Triple("Referral Bonus", "+ ₹100", "12 May 2024"),
                Triple("DSLR Camera Deposit Refund", "+ ₹2,000", "05 May 2024")
            ).forEach { tx ->
                Card(
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(tx.first, fontWeight = FontWeight.Bold)
                            Text(tx.third, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Text(
                            text = tx.second,
                            fontWeight = FontWeight.Bold,
                            color = if (tx.second.startsWith("+")) RentAnyGreen else Color.Red
                        )
                    }
                }
            }
        }
    }
}


// ================= ITEM DETAILS SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ItemDetailsScreenView(viewModel: RentViewModel, itemId: Int) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val item = items.find { it.id == itemId } ?: return
    val cartItems by viewModel.cartItemsState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Details", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.toggleBookmark(item.id, item.isBookmarked) }) {
                        Icon(
                            imageVector = if (item.isBookmarked) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                            contentDescription = "Bookmark",
                            tint = if (item.isBookmarked) Color.Red else MaterialTheme.colorScheme.onSurface
                        )
                    }
                    IconButton(onClick = { }) {
                        Icon(Icons.Default.Share, contentDescription = "Share")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
        ) {
            // Main Product Image
            AsyncImage(
                model = item.imageUrl,
                contentDescription = item.name,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(260.dp),
                contentScale = ContentScale.Crop
            )

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Name & Price row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = item.name,
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = item.category,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "₹${item.pricePerDay.toInt()}",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen
                        )
                        Text(
                            text = "/ day",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                // Ratings Block
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(Icons.Default.Star, contentDescription = null, tint = RentAnyGold)
                    Text(
                        text = "${item.rating} (120 reviews)",
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }

                Divider()

                // Security Deposit Details
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(RentAnyGreen.copy(alpha = 0.08f), RoundedCornerShape(8.dp))
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Security Deposit",
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.bodyMedium,
                            color = RentAnyGreenDark
                        )
                        Text(
                            text = "100% Refundable upon item return",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Text(
                        text = "₹${item.securityDeposit.toInt()}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = RentAnyGreenDark
                    )
                }

                // Description
                Text(
                    text = "Description",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = item.description,
                    style = MaterialTheme.typography.bodyMedium,
                    lineHeight = 20.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
                )

                Divider()

                // Owner Info Row
                Text(
                    text = "Lender Information",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = MaterialTheme.colorScheme.primary.copy(alpha = 0.12f),
                            modifier = Modifier.size(50.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = item.ownerName.first().toString(),
                                    fontWeight = FontWeight.Bold,
                                    color = RentAnyGreen
                                )
                            }
                        }

                        Column {
                            Text(
                                text = item.ownerName,
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleMedium
                            )
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Star, contentDescription = null, tint = RentAnyGold, modifier = Modifier.size(16.dp))
                                Text(
                                    text = "${item.ownerRating} (${item.ownerReviewsCount} reviews)",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }

                    OutlinedButton(
                        onClick = { viewModel.navigateTo(Screen.Chat(item.id)) },
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.MailOutline, contentDescription = "Chat", tint = RentAnyGreen)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Chat", color = RentAnyGreen)
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Dual CTA Buttons: Add to Cart & Book Now
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    val isInCart = cartItems.any { it.itemId == item.id }

                    OutlinedButton(
                        onClick = {
                            if (isInCart) {
                                viewModel.navigateTo(Screen.Cart)
                            } else {
                                viewModel.addToCart(item, days = 1, deliveryType = "Self Pickup")
                            }
                        },
                        border = BorderStroke(1.5.dp, RentAnyGreen),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (isInCart) RentAnyGreen.copy(alpha = 0.08f) else Color.Transparent
                        ),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier
                            .weight(1f)
                            .height(50.dp)
                            .testTag("add_to_cart_button")
                    ) {
                        Icon(
                            imageVector = if (isInCart) Icons.Default.CheckCircle else Icons.Default.ShoppingCart,
                            contentDescription = null,
                            tint = RentAnyGreen,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = if (isInCart) "In Cart" else "Add to Cart",
                            color = RentAnyGreen,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Button(
                        onClick = { viewModel.navigateTo(Screen.Booking(item.id)) },
                        colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier
                            .weight(1.2f)
                            .height(50.dp)
                            .testTag("book_now_button")
                    ) {
                        Text("Book Now", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

// ================= BOOKING SCREEN =================
private fun parseDateToCalendar(dateStr: String): java.util.Calendar {
    val cal = java.util.Calendar.getInstance()
    try {
        val sdf = java.text.SimpleDateFormat("MMM dd, yyyy", java.util.Locale.US)
        val date = sdf.parse(dateStr)
        if (date != null) {
            cal.time = date
        }
    } catch (e: Exception) {
        // Fallback to current date
    }
    return cal
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BookingScreenView(viewModel: RentViewModel, itemId: Int) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val item = items.find { it.id == itemId } ?: return

    val startDate by viewModel.bookingStartDate.collectAsStateWithLifecycle()
    val endDate by viewModel.bookingEndDate.collectAsStateWithLifecycle()
    val deliveryType by viewModel.bookingDeliveryType.collectAsStateWithLifecycle()

    val context = LocalContext.current
    val sdf = remember { java.text.SimpleDateFormat("MMM dd, yyyy", java.util.Locale.US) }

    val bookingDays = remember(startDate, endDate) {
        try {
            val start = sdf.parse(startDate)
            val end = sdf.parse(endDate)
            if (start != null && end != null) {
                val diff = end.time - start.time
                val days = (diff / (1000 * 60 * 60 * 24)).toInt()
                if (days < 1) 1 else days
            } else {
                3
            }
        } catch (e: Exception) {
            3
        }
    }
    val basePrice = item.pricePerDay * bookingDays
    val deliveryFee = if (deliveryType == "Delivery") 150.0 else 0.0
    val totalPrice = basePrice + deliveryFee

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Select Dates & Options", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Summary card
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    AsyncImage(
                        model = item.imageUrl,
                        contentDescription = item.name,
                        modifier = Modifier
                            .size(70.dp)
                            .clip(RoundedCornerShape(8.dp)),
                        contentScale = ContentScale.Crop
                    )
                    Column {
                        Text(text = item.name, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                        Text(text = "₹${item.pricePerDay.toInt()} / day", color = RentAnyGreen)
                    }
                }
            }

            // Dates calendar representation
            Text(
                text = "Select Dates",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // FROM date selector (clickable box)
                        Surface(
                            onClick = {
                                val cal = parseDateToCalendar(startDate)
                                android.app.DatePickerDialog(
                                    context,
                                    { _, year, month, dayOfMonth ->
                                        val selectedCal = java.util.Calendar.getInstance()
                                        selectedCal.set(year, month, dayOfMonth)
                                        val formatted = sdf.format(selectedCal.time)
                                        
                                        val endCal = parseDateToCalendar(endDate)
                                        if (selectedCal.after(endCal)) {
                                            val newEndCal = selectedCal.clone() as java.util.Calendar
                                            newEndCal.add(java.util.Calendar.DAY_OF_MONTH, 1)
                                            viewModel.bookingEndDate.value = sdf.format(newEndCal.time)
                                        }
                                        viewModel.bookingStartDate.value = formatted
                                    },
                                    cal.get(java.util.Calendar.YEAR),
                                    cal.get(java.util.Calendar.MONTH),
                                    cal.get(java.util.Calendar.DAY_OF_MONTH)
                                ).apply {
                                    datePicker.minDate = System.currentTimeMillis() - 1000
                                }.show()
                            },
                            modifier = Modifier.weight(1f).testTag("select_start_date"),
                            shape = RoundedCornerShape(12.dp),
                            color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
                        ) {
                            Column(
                                modifier = Modifier.padding(12.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.DateRange,
                                        contentDescription = null,
                                        tint = RentAnyGreen,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Text("FROM", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                }
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(startDate, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.onSurface)
                            }
                        }

                        Icon(
                            imageVector = Icons.Default.ArrowForward,
                            contentDescription = null,
                            tint = RentAnyGreen,
                            modifier = Modifier.size(24.dp)
                        )

                        // TO date selector (clickable box)
                        Surface(
                            onClick = {
                                val cal = parseDateToCalendar(endDate)
                                android.app.DatePickerDialog(
                                    context,
                                    { _, year, month, dayOfMonth ->
                                        val selectedCal = java.util.Calendar.getInstance()
                                        selectedCal.set(year, month, dayOfMonth)
                                        val formatted = sdf.format(selectedCal.time)
                                        
                                        val startCal = parseDateToCalendar(startDate)
                                        if (selectedCal.before(startCal)) {
                                            val newStartCal = selectedCal.clone() as java.util.Calendar
                                            newStartCal.add(java.util.Calendar.DAY_OF_MONTH, -1)
                                            viewModel.bookingStartDate.value = sdf.format(newStartCal.time)
                                        }
                                        viewModel.bookingEndDate.value = formatted
                                    },
                                    cal.get(java.util.Calendar.YEAR),
                                    cal.get(java.util.Calendar.MONTH),
                                    cal.get(java.util.Calendar.DAY_OF_MONTH)
                                ).apply {
                                    val startCal = parseDateToCalendar(startDate)
                                    datePicker.minDate = startCal.timeInMillis
                                }.show()
                            },
                            modifier = Modifier.weight(1f).testTag("select_end_date"),
                            shape = RoundedCornerShape(12.dp),
                            color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
                        ) {
                            Column(
                                modifier = Modifier.padding(12.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Row(
                                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.DateRange,
                                        contentDescription = null,
                                        tint = RentAnyGreen,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Text("TO", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                }
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(endDate, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.onSurface)
                            }
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Duration: $bookingDays ${if (bookingDays == 1) "day" else "days"}",
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen,
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Tap a card above to change dates",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                        )
                    }
                }
            }

            // Delivery Options
            Text(
                text = "Pickup & Delivery",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Option Self Pickup
                Surface(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { viewModel.bookingDeliveryType.value = "Self Pickup" },
                    shape = RoundedCornerShape(12.dp),
                    border = BorderStroke(
                        width = 2.dp,
                        color = if (deliveryType == "Self Pickup") RentAnyGreen else MaterialTheme.colorScheme.outlineVariant
                    ),
                    color = if (deliveryType == "Self Pickup") RentAnyGreen.copy(alpha = 0.05f) else Color.Transparent
                ) {
                    Column(modifier = Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.Person, contentDescription = null, tint = RentAnyGreen)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Self Pickup", fontWeight = FontWeight.Bold)
                        Text("Free", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }

                // Option Delivery
                Surface(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { viewModel.bookingDeliveryType.value = "Delivery" },
                    shape = RoundedCornerShape(12.dp),
                    border = BorderStroke(
                        width = 2.dp,
                        color = if (deliveryType == "Delivery") RentAnyGreen else MaterialTheme.colorScheme.outlineVariant
                    ),
                    color = if (deliveryType == "Delivery") RentAnyGreen.copy(alpha = 0.05f) else Color.Transparent
                ) {
                    Column(modifier = Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.ShoppingCart, contentDescription = null, tint = RentAnyGreen)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Delivery", fontWeight = FontWeight.Bold)
                        Text("+₹150", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }

            Divider()

            // Price Summary
            Text(
                text = "Price Details",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Rental Fee (₹${item.pricePerDay.toInt()} x $bookingDays days)")
                    Text("₹${basePrice.toInt()}")
                }
                if (deliveryType == "Delivery") {
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Delivery Fee")
                        Text("₹150")
                    }
                }
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Security Deposit (Refundable)")
                    Text("₹${item.securityDeposit.toInt()}")
                }
                Divider()
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Total Price", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleLarge)
                    Text("₹${totalPrice.toInt()}", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleLarge, color = RentAnyGreen)
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { viewModel.navigateTo(Screen.Payment(itemId, bookingDays, deliveryType)) },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("Continue to Payment", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

// ================= PAYMENT SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaymentScreenView(viewModel: RentViewModel, itemId: Int, bookingDays: Int, deliveryType: String) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val item = items.find { it.id == itemId } ?: return
    val profile by viewModel.profileState.collectAsStateWithLifecycle()

    val basePrice = item.pricePerDay * bookingDays
    val deliveryFee = if (deliveryType == "Delivery") 150.0 else 0.0
    val totalAmount = basePrice + deliveryFee
    val securityDeposit = item.securityDeposit
    val finalPayable = totalAmount + securityDeposit

    var selectedMethod by remember { mutableStateOf("Wallet") }
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Payment", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Price card
            Card(
                colors = CardDefaults.cardColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("Total Amount to Pay", color = Color.White.copy(alpha = 0.8f))
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("₹${finalPayable.toInt()}", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold, color = Color.White)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Includes ₹${securityDeposit.toInt()} refundable deposit", color = Color.White.copy(alpha = 0.8f), fontSize = 12.sp)
                }
            }

            Text(
                text = "Select Payment Method",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            // Wallet option
            Surface(
                onClick = { selectedMethod = "Wallet" },
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(
                    width = 2.dp,
                    color = if (selectedMethod == "Wallet") RentAnyGreen else MaterialTheme.colorScheme.outlineVariant
                ),
                color = if (selectedMethod == "Wallet") RentAnyGreen.copy(alpha = 0.05f) else Color.Transparent,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.AccountBox, contentDescription = null, tint = RentAnyGreen)
                        Column {
                            Text("RentAny Wallet", fontWeight = FontWeight.Bold)
                            Text("Balance: ₹${profile?.walletBalance?.toInt() ?: 2450}", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                    RadioButton(selected = selectedMethod == "Wallet", onClick = { selectedMethod = "Wallet" })
                }
            }

            // UPI Option
            Surface(
                onClick = { selectedMethod = "UPI" },
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(
                    width = 2.dp,
                    color = if (selectedMethod == "UPI") RentAnyGreen else MaterialTheme.colorScheme.outlineVariant
                ),
                color = if (selectedMethod == "UPI") RentAnyGreen.copy(alpha = 0.05f) else Color.Transparent,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Build, contentDescription = null, tint = RentAnyGreen)
                        Column {
                            Text("UPI (GPay / PhonePe)", fontWeight = FontWeight.Bold)
                            Text("rohanpatel@oksbi", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                    RadioButton(selected = selectedMethod == "UPI", onClick = { selectedMethod = "UPI" })
                }
            }

            // Cards Option
            Surface(
                onClick = { selectedMethod = "Card" },
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(
                    width = 2.dp,
                    color = if (selectedMethod == "Card") RentAnyGreen else MaterialTheme.colorScheme.outlineVariant
                ),
                color = if (selectedMethod == "Card") RentAnyGreen.copy(alpha = 0.05f) else Color.Transparent,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Lock, contentDescription = null, tint = RentAnyGreen)
                        Column {
                            Text("Debit / Credit Card", fontWeight = FontWeight.Bold)
                            Text("Visa ending in 4242", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                    RadioButton(selected = selectedMethod == "Card", onClick = { selectedMethod = "Card" })
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = {
                    viewModel.submitBooking(
                        itemId = itemId,
                        totalPrice = finalPayable,
                        itemName = item.name,
                        itemImageUrl = item.imageUrl,
                        onSuccess = {
                            Toast.makeText(context, "Booking Placed Successfully!", Toast.LENGTH_LONG).show()
                            viewModel.navigateTo(Screen.MyBookings)
                        }
                    )
                },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("Pay ₹${finalPayable.toInt()}", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

// ================= MY BOOKINGS SCREEN =================
@Composable
fun MyBookingsScreenView(viewModel: RentViewModel) {
    val bookings by viewModel.bookingsState.collectAsStateWithLifecycle()
    var selectedTab by remember { mutableStateOf("Upcoming") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Surface(
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 4.dp,
            modifier = Modifier.fillMaxWidth()
        ) {
            Column {
                Text(
                    text = "My Bookings",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(16.dp)
                )

                TabRow(
                    selectedTabIndex = when (selectedTab) {
                        "Upcoming" -> 0
                        "Ongoing" -> 1
                        else -> 2
                    }
                ) {
                    Tab(
                        selected = selectedTab == "Upcoming",
                        onClick = { selectedTab = "Upcoming" },
                        text = { Text("Upcoming") }
                    )
                    Tab(
                        selected = selectedTab == "Ongoing",
                        onClick = { selectedTab = "Ongoing" },
                        text = { Text("Ongoing") }
                    )
                    Tab(
                        selected = selectedTab == "Completed",
                        onClick = { selectedTab = "Completed" },
                        text = { Text("Completed") }
                    )
                }
            }
        }

        val filteredBookings = bookings.filter { it.status == selectedTab }

        if (filteredBookings.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = Icons.Default.DateRange,
                        contentDescription = "Empty",
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.2f),
                        modifier = Modifier.size(64.dp)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("No bookings found in this category.", style = MaterialTheme.typography.bodyMedium)
                }
            }
        } else {
            LazyColumn(
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(filteredBookings) { booking ->
                    BookingCard(booking, viewModel)
                }
            }
        }
    }
}

@Composable
fun BookingCard(booking: BookingEntity, viewModel: RentViewModel) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                AsyncImage(
                    model = booking.itemImageUrl,
                    contentDescription = booking.itemName,
                    modifier = Modifier
                        .size(60.dp)
                        .clip(RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.Crop
                )

                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = booking.itemName, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)

                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = when (booking.status) {
                                "Upcoming" -> RentAnyGreen.copy(alpha = 0.15f)
                                "Ongoing" -> RentAnyGold.copy(alpha = 0.15f)
                                else -> MaterialTheme.colorScheme.outlineVariant
                            }
                        ) {
                            Text(
                                text = booking.status,
                                color = when (booking.status) {
                                    "Upcoming" -> RentAnyGreen
                                    "Ongoing" -> RentAnyGreenDark
                                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                                },
                                fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }

                    Text(
                        text = "${booking.startDate} - ${booking.endDate}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Divider()

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Total Paid:", style = MaterialTheme.typography.bodySmall)
                    Text("₹${booking.totalPrice.toInt()}", fontWeight = FontWeight.Bold, color = RentAnyGreen)
                }

                OutlinedButton(
                    onClick = { viewModel.navigateTo(Screen.Chat(booking.itemId)) },
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.height(30.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp)
                ) {
                    Icon(Icons.Default.MailOutline, contentDescription = null, modifier = Modifier.size(14.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Lender", fontSize = 11.sp)
                }
            }
        }
    }
}

// ================= CHAT SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreenView(viewModel: RentViewModel, itemId: Int) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val item = items.find { it.id == itemId } ?: return
    val messages by viewModel.getMessagesForItem(itemId).collectAsStateWithLifecycle(initialValue = emptyList())

    var typedMessage by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()

    // Automatically scroll to the bottom of the chat list on first load or when messages change
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = RentAnyGreen.copy(alpha = 0.12f),
                            modifier = Modifier.size(36.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = item.ownerName.first().toString(),
                                    fontWeight = FontWeight.Bold,
                                    color = RentAnyGreen
                                )
                            }
                        }
                        Column {
                            Text(text = item.ownerName, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                            Text(text = "Online", style = MaterialTheme.typography.bodySmall, color = RentAnyGreen)
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Rental Context mini-card
            Surface(
                color = MaterialTheme.colorScheme.surfaceVariant,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        AsyncImage(
                            model = item.imageUrl,
                            contentDescription = item.name,
                            modifier = Modifier
                                .size(40.dp)
                                .clip(RoundedCornerShape(4.dp)),
                            contentScale = ContentScale.Crop
                        )
                        Column {
                            Text(text = item.name, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium)
                            Text(text = "₹${item.pricePerDay.toInt()} / day", style = MaterialTheme.typography.bodySmall, color = RentAnyGreen)
                        }
                    }
                    Button(
                        onClick = { viewModel.navigateTo(Screen.Booking(item.id)) },
                        colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 2.dp),
                        modifier = Modifier.height(30.dp)
                    ) {
                        Text("Book Now", fontSize = 11.sp)
                    }
                }
            }

            // Message history list
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(vertical = 16.dp)
            ) {
                items(messages) { msg ->
                    ChatBubble(message = msg)
                }
            }

            // Bottom entry message row
            Surface(
                tonalElevation = 8.dp,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .padding(12.dp)
                        .navigationBarsPadding()
                        .imePadding(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedTextField(
                        value = typedMessage,
                        onValueChange = { typedMessage = it },
                        placeholder = { Text("Type a message...") },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(24.dp),
                        maxLines = 4
                    )

                    IconButton(
                        onClick = {
                            if (typedMessage.isNotBlank()) {
                                viewModel.sendChatMessage(itemId, typedMessage)
                                typedMessage = ""
                                coroutineScope.launch {
                                    listState.animateScrollToItem(messages.size)
                                }
                            }
                        },
                        colors = IconButtonDefaults.iconButtonColors(containerColor = RentAnyGreen),
                        modifier = Modifier.size(48.dp).testTag("send_message_button")
                    ) {
                        Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send", tint = Color.White)
                    }
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessageEntity) {
    val alignment = if (message.isUserMessage) Alignment.End else Alignment.Start
    val containerColor = if (message.isUserMessage) RentAnyGreen else MaterialTheme.colorScheme.surfaceVariant
    val textColor = if (message.isUserMessage) Color.White else MaterialTheme.colorScheme.onSurface

    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = alignment) {
        Surface(
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (message.isUserMessage) 16.dp else 4.dp,
                bottomEnd = if (message.isUserMessage) 4.dp else 16.dp
            ),
            color = containerColor,
            contentColor = textColor,
            modifier = Modifier.widthIn(max = 280.dp)
        ) {
            Text(
                text = message.messageText,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

// ================= INBOX / MESSAGES SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InboxScreenView(viewModel: RentViewModel) {
    val items by viewModel.itemsState.collectAsStateWithLifecycle()
    val allMessages by viewModel.allMessagesState.collectAsStateWithLifecycle()
    var searchQuery by remember { mutableStateOf("") }

    // Group messages by itemId
    val messagesGrouped = remember(allMessages) {
        allMessages.groupBy { it.itemId }
    }

    // Map each group to a Conversation
    val conversations = remember(messagesGrouped, items) {
        messagesGrouped.mapNotNull { (itemId, msgs) ->
            val item = items.find { it.id == itemId }
            val lastMsg = msgs.maxByOrNull { it.timestamp }
            if (lastMsg != null) {
                ConversationItem(
                    itemId = itemId,
                    itemName = item?.name ?: "Rental Item #$itemId",
                    itemImageUrl = item?.imageUrl ?: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=500",
                    ownerName = item?.ownerName ?: lastMsg.senderName.ifEmpty { "Owner" },
                    lastMessage = lastMsg.messageText,
                    timestamp = lastMsg.timestamp,
                    isUserMessage = lastMsg.isUserMessage
                )
            } else {
                null
            }
        }.sortedByDescending { it.timestamp }
    }

    // Filter conversations based on search
    val filteredConversations = conversations.filter {
        it.ownerName.contains(searchQuery, ignoreCase = true) ||
        it.itemName.contains(searchQuery, ignoreCase = true) ||
        it.lastMessage.contains(searchQuery, ignoreCase = true)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Inbox / Messages", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.background)
        ) {
            // Search field
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                placeholder = { Text("Search by owner or item name...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
                    .testTag("inbox_search_bar"),
                shape = RoundedCornerShape(12.dp),
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Search") },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { searchQuery = "" }) {
                            Icon(Icons.Default.Clear, contentDescription = "Clear")
                        }
                    }
                },
                singleLine = true
            )

            if (filteredConversations.isEmpty()) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .padding(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = RentAnyGreen.copy(alpha = 0.08f),
                            modifier = Modifier.size(96.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = Icons.Default.MailOutline,
                                    contentDescription = null,
                                    tint = RentAnyGreen,
                                    modifier = Modifier.size(48.dp)
                                )
                            }
                        }

                        Text(
                            text = if (searchQuery.isEmpty()) "No chats started yet" else "No match found",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )

                        Text(
                            text = if (searchQuery.isEmpty()) {
                                "Tap 'Chat with Owner' on any item detail screen to negotiate, ask questions, or discuss pickup arrangements."
                            } else {
                                "Try searching for a different keyword or view all your conversations."
                            },
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(horizontal = 16.dp)
                        )

                        if (searchQuery.isEmpty()) {
                            Button(
                                onClick = { viewModel.navigateTo(Screen.Home) },
                                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.height(48.dp)
                            ) {
                                Text("Explore Rental Items", fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    contentPadding = PaddingValues(bottom = 16.dp)
                ) {
                    items(filteredConversations) { convo ->
                        ConversationRow(convo = convo, onClick = {
                            viewModel.navigateTo(Screen.Chat(convo.itemId))
                        })
                        HorizontalDivider(
                            modifier = Modifier.padding(horizontal = 16.dp),
                            color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
                        )
                    }
                }
            }
        }
    }
}

data class ConversationItem(
    val itemId: Int,
    val itemName: String,
    val itemImageUrl: String,
    val ownerName: String,
    val lastMessage: String,
    val timestamp: Long,
    val isUserMessage: Boolean
)

@Composable
fun ConversationRow(convo: ConversationItem, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .testTag("conversation_row_${convo.itemId}"),
        color = Color.Transparent
    ) {
        Row(
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Owner avatar / Initial with Item thumbnail badge
            Box(modifier = Modifier.size(56.dp)) {
                // Main Owner initial avatar
                Surface(
                    shape = CircleShape,
                    color = RentAnyGreen.copy(alpha = 0.12f),
                    modifier = Modifier.size(48.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            text = convo.ownerName.firstOrNull()?.toString()?.uppercase() ?: "O",
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen,
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }

                // Small thumbnail badge of item on bottom right
                AsyncImage(
                    model = convo.itemImageUrl,
                    contentDescription = convo.itemName,
                    modifier = Modifier
                        .size(24.dp)
                        .align(Alignment.BottomEnd)
                        .clip(CircleShape)
                        .border(1.5.dp, MaterialTheme.colorScheme.surface, CircleShape),
                    contentScale = ContentScale.Crop
                )
            }

            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Text(
                        text = convo.ownerName,
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.bodyLarge,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f)
                    )

                    Spacer(modifier = Modifier.width(8.dp))

                    Text(
                        text = formatChatTime(convo.timestamp),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(modifier = Modifier.height(2.dp))

                Text(
                    text = convo.itemName,
                    style = MaterialTheme.typography.bodySmall,
                    color = RentAnyGreen,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = if (convo.isUserMessage) "You: ${convo.lastMessage}" else convo.lastMessage,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            Icon(
                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

fun formatChatTime(timestamp: Long): String {
    val diff = System.currentTimeMillis() - timestamp
    val seconds = diff / 1000
    val minutes = seconds / 60
    val hours = minutes / 60
    val days = hours / 24

    return when {
        seconds < 60 -> "Just now"
        minutes < 60 -> "${minutes}m ago"
        hours < 24 -> "${hours}h ago"
        days < 7 -> "${days}d ago"
        else -> {
            val date = java.util.Date(timestamp)
            val sdf = java.text.SimpleDateFormat("dd MMM", java.util.Locale.getDefault())
            sdf.format(date)
        }
    }
}

// ================= ADD RENTAL SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddRentalScreenView(viewModel: RentViewModel) {
    val name by viewModel.addFormName.collectAsStateWithLifecycle()
    val category by viewModel.addFormCategory.collectAsStateWithLifecycle()
    val price by viewModel.addFormPrice.collectAsStateWithLifecycle()
    val deposit by viewModel.addFormSecurityDeposit.collectAsStateWithLifecycle()
    val description by viewModel.addFormDescription.collectAsStateWithLifecycle()
    val imageUrl by viewModel.addFormImageUrl.collectAsStateWithLifecycle()

    val context = LocalContext.current
    val categoriesList = listOf("Electronics", "Utensils", "Furniture", "Tools", "Party Items", "Sports", "Camping")
    var categoryExpanded by remember { mutableStateOf(false) }

    var showPhotoDialog by remember { mutableStateOf(false) }
    var customUrlInput by remember { mutableStateOf("") }

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: android.net.Uri? ->
        uri?.let {
            viewModel.addFormImageUrl.value = it.toString()
        }
    }

    val presetsForCategory = remember(category) {
        when (category) {
            "Electronics" -> listOf(
                "DSLR Camera" to "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=400",
                "Headphones" to "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=400",
                "Laptop" to "https://images.unsplash.com/photo-1496181130204-755241524eab?auto=format&fit=crop&q=80&w=400"
            )
            "Utensils" -> listOf(
                "Blender" to "https://images.unsplash.com/photo-1578643463396-0997cb5328c1?auto=format&fit=crop&q=80&w=400",
                "Cookware Set" to "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&q=80&w=400",
                "Coffee Maker" to "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&q=80&w=400"
            )
            "Furniture" -> listOf(
                "Office Chair" to "https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&q=80&w=400",
                "Lamp" to "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&q=80&w=400",
                "Study Table" to "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?auto=format&fit=crop&q=80&w=400"
            )
            "Tools" -> listOf(
                "Drill Machine" to "https://images.unsplash.com/photo-1504148455328-c376907d081c?auto=format&fit=crop&q=80&w=400",
                "Toolkit Case" to "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?auto=format&fit=crop&q=80&w=400",
                "Ladder" to "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=400"
            )
            "Party Items" -> listOf(
                "Sound Speaker" to "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&q=80&w=400",
                "Projector" to "https://images.unsplash.com/photo-1535016120720-40c646be5580?auto=format&fit=crop&q=80&w=400",
                "Karaoke Mic" to "https://images.unsplash.com/photo-1516280440614-37939bbacd6a?auto=format&fit=crop&q=80&w=400"
            )
            "Sports" -> listOf(
                "Bicycle" to "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&q=80&w=400",
                "Football" to "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&q=80&w=400",
                "Tennis Racket" to "https://images.unsplash.com/photo-1622279457486-62dcc4a4b1ca?auto=format&fit=crop&q=80&w=400"
            )
            "Camping" -> listOf(
                "Tent" to "https://images.unsplash.com/photo-1510312305653-8ed496efae75?auto=format&fit=crop&q=80&w=400",
                "Backpack" to "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&q=80&w=400",
                "Lantern" to "https://images.unsplash.com/photo-1508873535684-277a3cbcc4e8?auto=format&fit=crop&q=80&w=400"
            )
            else -> listOf(
                "Generic Item" to "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=400"
            )
        }
    }

    if (showPhotoDialog) {
        AlertDialog(
            onDismissRequest = { showPhotoDialog = false },
            title = {
                Text(
                    text = "Upload / Select Photo",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            },
            text = {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Option 1: Gallery Picker Button
                    Button(
                        onClick = {
                            launcher.launch("image/*")
                            showPhotoDialog = false
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth().height(48.dp).testTag("select_from_gallery")
                    ) {
                        Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Pick from Gallery", fontWeight = FontWeight.Bold)
                    }

                    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))

                    // Option 2: Presets for Selected Category
                    Text(
                        text = "Or choose a beautiful $category preset:",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontWeight = FontWeight.Bold
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        presetsForCategory.forEach { (label, url) ->
                            Column(
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable {
                                        viewModel.addFormImageUrl.value = url
                                        showPhotoDialog = false
                                    }
                                    .testTag("preset_image_${label.replace(" ", "_").lowercase()}"),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                AsyncImage(
                                    model = url,
                                    contentDescription = label,
                                    modifier = Modifier
                                        .size(64.dp)
                                        .clip(RoundedCornerShape(8.dp))
                                        .border(1.dp, MaterialTheme.colorScheme.outlineVariant, RoundedCornerShape(8.dp)),
                                    contentScale = ContentScale.Crop
                                )
                                Text(
                                    text = label,
                                    style = MaterialTheme.typography.labelSmall,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                    textAlign = TextAlign.Center
                                )
                            }
                        }
                    }

                    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))

                    // Option 3: Custom Web URL Textfield
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            text = "Or paste custom image URL:",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontWeight = FontWeight.Bold
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            OutlinedTextField(
                                value = customUrlInput,
                                onValueChange = { customUrlInput = it },
                                placeholder = { Text("https://example.com/image.jpg") },
                                singleLine = true,
                                modifier = Modifier.weight(1f).testTag("custom_image_url_input"),
                                textStyle = MaterialTheme.typography.bodySmall
                            )
                            Button(
                                onClick = {
                                    if (customUrlInput.isNotBlank()) {
                                        viewModel.addFormImageUrl.value = customUrlInput.trim()
                                        customUrlInput = ""
                                        showPhotoDialog = false
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                                shape = RoundedCornerShape(8.dp),
                                enabled = customUrlInput.isNotBlank(),
                                modifier = Modifier.testTag("apply_custom_image_url")
                            ) {
                                Text("Apply")
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showPhotoDialog = false }) {
                    Text("Cancel", color = RentAnyGreen)
                }
            }
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Publish New Rental", fontWeight = FontWeight.Bold) }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Photo Uploader block with preview
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
                    .background(
                        color = if (imageUrl.isEmpty()) RentAnyGreen.copy(alpha = 0.05f) else Color.Black.copy(alpha = 0.03f),
                        shape = RoundedCornerShape(12.dp)
                    )
                    .border(
                        border = BorderStroke(
                            width = 1.dp,
                            color = if (imageUrl.isEmpty()) RentAnyGreen else MaterialTheme.colorScheme.outlineVariant
                        ),
                        shape = RoundedCornerShape(12.dp)
                    )
                    .clickable { showPhotoDialog = true }
                    .testTag("photo_uploader_box"),
                contentAlignment = Alignment.Center
            ) {
                if (imageUrl.isEmpty()) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.AddCircle,
                            contentDescription = "Add Photo",
                            tint = RentAnyGreen,
                            modifier = Modifier.size(40.dp)
                        )
                        Text(
                            text = "Upload Photo of Item",
                            fontWeight = FontWeight.Bold,
                            color = RentAnyGreen,
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Tap to pick from gallery, presets, or paste a URL",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                        )
                    }
                } else {
                    Box(modifier = Modifier.fillMaxSize()) {
                        AsyncImage(
                            model = imageUrl,
                            contentDescription = "Selected Item Photo",
                            modifier = Modifier
                                .fillMaxSize()
                                .clip(RoundedCornerShape(12.dp)),
                            contentScale = ContentScale.Crop
                        )
                        
                        // Clear selection button in top-right corner
                        IconButton(
                            onClick = { viewModel.addFormImageUrl.value = "" },
                            modifier = Modifier
                                .padding(8.dp)
                                .size(32.dp)
                                .background(Color.Black.copy(alpha = 0.6f), CircleShape)
                                .align(Alignment.TopEnd)
                                .testTag("clear_photo_button")
                        ) {
                            Icon(
                                imageVector = Icons.Default.Close,
                                contentDescription = "Clear Photo",
                                tint = Color.White,
                                modifier = Modifier.size(16.dp)
                            )
                        }

                        // Change photo indicator pill at bottom center
                        Surface(
                            shape = RoundedCornerShape(50),
                            color = Color.Black.copy(alpha = 0.7f),
                            modifier = Modifier
                                .align(Alignment.BottomCenter)
                                .padding(12.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                                horizontalArrangement = Arrangement.spacedBy(6.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Edit,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(14.dp)
                                )
                                Text(
                                    text = "Tap to Change Photo",
                                    color = Color.White,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    }
                }
            }

            OutlinedTextField(
                value = name,
                onValueChange = { viewModel.addFormName.value = it },
                label = { Text("Item Name") },
                modifier = Modifier.fillMaxWidth()
            )

            // Category dropdown menu
            ExposedDropdownMenuBox(
                expanded = categoryExpanded,
                onExpandedChange = { categoryExpanded = !categoryExpanded }
            ) {
                OutlinedTextField(
                    value = category,
                    onValueChange = {},
                    readOnly = true,
                    label = { Text("Category") },
                    trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = categoryExpanded) },
                    modifier = Modifier.fillMaxWidth().menuAnchor()
                )

                ExposedDropdownMenu(
                    expanded = categoryExpanded,
                    onDismissRequest = { categoryExpanded = false }
                ) {
                    categoriesList.forEach { cat ->
                        DropdownMenuItem(
                            text = { Text(cat) },
                            onClick = {
                                viewModel.addFormCategory.value = cat
                                categoryExpanded = false
                            }
                        )
                    }
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = price,
                    onValueChange = { viewModel.addFormPrice.value = it },
                    label = { Text("Price per Day (₹)") },
                    modifier = Modifier.weight(1f),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )

                OutlinedTextField(
                    value = deposit,
                    onValueChange = { viewModel.addFormSecurityDeposit.value = it },
                    label = { Text("Refundable Deposit (₹)") },
                    modifier = Modifier.weight(1f),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
            }

            OutlinedTextField(
                value = description,
                onValueChange = { viewModel.addFormDescription.value = it },
                label = { Text("Item Description") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 3
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    if (name.isBlank() || price.isBlank()) {
                        Toast.makeText(context, "Please fill in Name and Price", Toast.LENGTH_SHORT).show()
                    } else {
                        viewModel.publishRentalItem {
                            Toast.makeText(context, "Published Successfully!", Toast.LENGTH_LONG).show()
                            viewModel.navigateTo(Screen.Home)
                        }
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
                    .testTag("publish_item_button")
            ) {
                Text("Publish Item", fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

// ================= PROFILE SCREEN =================
@Composable
fun ProfileScreenView(viewModel: RentViewModel) {
    val profile by viewModel.profileState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
    ) {
        // High contrast visual header profile box
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(RentAnyGreen)
                .padding(vertical = 32.dp, horizontal = 24.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = CircleShape,
                    color = Color.White,
                    modifier = Modifier.size(72.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            text = profile?.name?.first().toString(),
                            style = MaterialTheme.typography.displaySmall,
                            fontWeight = FontWeight.Black,
                            color = RentAnyGreen
                        )
                    }
                }

                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = profile?.name ?: "Rohan Patel",
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            style = MaterialTheme.typography.titleLarge
                        )
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Verified",
                            tint = Color.White,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                    Text(
                        text = profile?.phone ?: "+91 98765 43210",
                        color = Color.White.copy(alpha = 0.85f),
                        style = MaterialTheme.typography.bodyMedium
                    )
                    profile?.email?.let { email ->
                        if (email.isNotEmpty()) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp),
                                modifier = Modifier.padding(top = 2.dp)
                            ) {
                                if (email.contains("gmail.com") || email.contains("google")) {
                                    Surface(
                                        shape = CircleShape,
                                        color = Color.White.copy(alpha = 0.2f),
                                        modifier = Modifier.size(14.dp)
                                    ) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Text(
                                                text = "G",
                                                fontSize = 8.sp,
                                                fontWeight = FontWeight.Black,
                                                color = Color.White
                                            )
                                        }
                                    }
                                }
                                Text(
                                    text = email,
                                    color = Color.White.copy(alpha = 0.75f),
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }
                    }
                }

                IconButton(onClick = { viewModel.navigateTo(Screen.Settings) }) {
                    Icon(Icons.Default.Settings, contentDescription = "Settings", tint = Color.White)
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Profile lists / links
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("My Account", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)

            ProfileNavigationRow(Icons.Default.List, "My Listings", onClick = { })
            ProfileNavigationRow(Icons.Default.DateRange, "My Bookings", onClick = { viewModel.navigateTo(Screen.MyBookings) })
            ProfileNavigationRow(Icons.Default.MailOutline, "My Chats", onClick = { viewModel.navigateTo(Screen.Inbox) })
            ProfileNavigationRow(Icons.Default.Favorite, "Wishlist", onClick = { viewModel.navigateTo(Screen.MoreFeatures) })
            ProfileNavigationRow(Icons.Default.Star, "My Reviews", onClick = { viewModel.navigateTo(Screen.MoreFeatures) })
            ProfileNavigationRow(Icons.Default.ShoppingCart, "Payment Methods", onClick = { viewModel.navigateTo(Screen.PaymentMethods) })
            ProfileNavigationRow(Icons.Default.Settings, "Settings", onClick = { viewModel.navigateTo(Screen.Settings) })
            ProfileNavigationRow(Icons.Default.Info, "Help & Support", onClick = { viewModel.navigateTo(Screen.HelpSupport) })

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { viewModel.navigateTo(Screen.Login) },
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text("Log Out", color = Color.White, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
fun ProfileNavigationRow(icon: ImageVector, label: String, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(8.dp),
        color = MaterialTheme.colorScheme.surface,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(imageVector = icon, contentDescription = null, tint = RentAnyGreen)
                Text(text = label, fontWeight = FontWeight.SemiBold)
            }
            Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, contentDescription = null)
        }
    }
}

// ================= CATEGORIES SCREEN =================
data class CategoryDetail(
    val name: String,
    val itemCount: String,
    val icon: ImageVector,
    val imageUrl: String,
    val popularItems: String,
    val tag: String,
    val accentColor: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CategoriesScreenView(viewModel: RentViewModel) {
    val allCategories = remember {
        listOf(
            CategoryDetail(
                name = "Electronics",
                itemCount = "400+ items",
                icon = Icons.Default.ShoppingCart,
                imageUrl = "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=400",
                popularItems = "DSLR Cameras, Laptops, Audio",
                tag = "Popular",
                accentColor = Color(0xFF2563EB)
            ),
            CategoryDetail(
                name = "Utensils",
                itemCount = "650+ items",
                icon = Icons.Default.Menu,
                imageUrl = "https://images.unsplash.com/photo-1578643463396-0997cb5328c1?auto=format&fit=crop&q=80&w=400",
                popularItems = "Blenders, Coffee Makers, Sets",
                tag = "Essential",
                accentColor = Color(0xFFD97706)
            ),
            CategoryDetail(
                name = "Furniture",
                itemCount = "120+ items",
                icon = Icons.Default.Home,
                imageUrl = "https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&q=80&w=400",
                popularItems = "Office Chairs, Tables, Lamps",
                tag = "Home",
                accentColor = Color(0xFF059669)
            ),
            CategoryDetail(
                name = "Tools",
                itemCount = "900+ items",
                icon = Icons.Default.Build,
                imageUrl = "https://images.unsplash.com/photo-1504148455328-c376907d081c?auto=format&fit=crop&q=80&w=400",
                popularItems = "Power Drills, Toolkits, Ladders",
                tag = "Essential",
                accentColor = Color(0xFF4F46E5)
            ),
            CategoryDetail(
                name = "Party Items",
                itemCount = "400+ items",
                icon = Icons.Default.Star,
                imageUrl = "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&q=80&w=400",
                popularItems = "Speakers, Projectors, Mics",
                tag = "Events",
                accentColor = Color(0xFFDB2777)
            ),
            CategoryDetail(
                name = "Sports",
                itemCount = "550+ items",
                icon = Icons.Default.ThumbUp,
                imageUrl = "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&q=80&w=400",
                popularItems = "Bicycles, Racquets, Gym Sets",
                tag = "Fitness",
                accentColor = Color(0xFF0D9488)
            ),
            CategoryDetail(
                name = "Camping",
                itemCount = "300+ items",
                icon = Icons.Default.Favorite,
                imageUrl = "https://images.unsplash.com/photo-1510312305653-8ed496efae75?auto=format&fit=crop&q=80&w=400",
                popularItems = "Tents, Backpacks, Lanterns",
                tag = "Outdoor",
                accentColor = Color(0xFF7C3AED)
            )
        )
    }

    var categorySearchQuery by remember { mutableStateOf("") }
    var selectedTagFilter by remember { mutableStateOf("All") }
    var isGridView by remember { mutableStateOf(true) }

    val tags = listOf("All", "Popular", "Essential", "Home", "Events", "Fitness", "Outdoor")

    val filteredCategories = remember(categorySearchQuery, selectedTagFilter) {
        allCategories.filter { cat ->
            val matchesSearch = cat.name.contains(categorySearchQuery, ignoreCase = true) ||
                    cat.popularItems.contains(categorySearchQuery, ignoreCase = true) ||
                    cat.tag.contains(categorySearchQuery, ignoreCase = true)
            val matchesTag = selectedTagFilter == "All" || cat.tag.equals(selectedTagFilter, ignoreCase = true)
            matchesSearch && matchesTag
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Explore Categories", fontWeight = FontWeight.Bold)
                        Text(
                            text = "${allCategories.size} Categories Available",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(
                        onClick = { viewModel.navigateBack() },
                        modifier = Modifier.testTag("categories_back_button")
                    ) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(
                        onClick = { isGridView = !isGridView },
                        modifier = Modifier.testTag("toggle_view_mode_button")
                    ) {
                        Icon(
                            imageVector = if (isGridView) Icons.Default.List else Icons.Default.Menu,
                            contentDescription = "Toggle View",
                            tint = RentAnyGreen
                        )
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Search & Filters Header Container
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Search TextField
                OutlinedTextField(
                    value = categorySearchQuery,
                    onValueChange = { categorySearchQuery = it },
                    placeholder = { Text("Search category or rental item...") },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = RentAnyGreen) },
                    trailingIcon = {
                        if (categorySearchQuery.isNotEmpty()) {
                            IconButton(onClick = { categorySearchQuery = "" }) {
                                Icon(Icons.Default.Close, contentDescription = "Clear search")
                            }
                        }
                    },
                    singleLine = true,
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = RentAnyGreen,
                        unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("category_search_input")
                )

                // Category Tag Chips Row
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(bottom = 4.dp)
                ) {
                    items(tags) { tag ->
                        FilterChip(
                            selected = selectedTagFilter == tag,
                            onClick = { selectedTagFilter = tag },
                            label = { Text(tag, fontWeight = if (selectedTagFilter == tag) FontWeight.Bold else FontWeight.Normal) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = RentAnyGreen,
                                selectedLabelColor = Color.White
                            ),
                            border = FilterChipDefaults.filterChipBorder(
                                enabled = true,
                                selected = selectedTagFilter == tag,
                                borderColor = MaterialTheme.colorScheme.outlineVariant
                            ),
                            shape = RoundedCornerShape(20.dp)
                        )
                    }
                }
            }

            if (filteredCategories.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(48.dp)
                        )
                        Text(
                            text = "No categories match '$categorySearchQuery'",
                            style = MaterialTheme.typography.bodyLarge,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center
                        )
                        TextButton(onClick = {
                            categorySearchQuery = ""
                            selectedTagFilter = "All"
                        }) {
                            Text("Reset Search Filters", color = RentAnyGreen, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            } else if (isGridView) {
                // 2-Column Grid Layout
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 24.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(filteredCategories) { cat ->
                        CategoryGridCard(
                            category = cat,
                            onClick = {
                                viewModel.selectCategory(cat.name)
                                viewModel.navigateTo(Screen.Home)
                            }
                        )
                    }
                }
            } else {
                // List Layout
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 24.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(filteredCategories) { cat ->
                        CategoryListCard(
                            category = cat,
                            onClick = {
                                viewModel.selectCategory(cat.name)
                                viewModel.navigateTo(Screen.Home)
                            }
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CategoryGridCard(category: CategoryDetail, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.6f)),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        modifier = Modifier
            .fillMaxWidth()
            .testTag("category_card_${category.name.lowercase()}")
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            // Image Cover Header with Gradient Overlay & Badge
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(115.dp)
            ) {
                AsyncImage(
                    model = category.imageUrl,
                    contentDescription = category.name,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize()
                )

                // Dark Bottom Gradient
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(
                                    Color.Black.copy(alpha = 0.2f),
                                    Color.Black.copy(alpha = 0.75f)
                                )
                            )
                        )
                )

                // Tag Badge Top-Left
                Surface(
                    color = category.accentColor.copy(alpha = 0.9f),
                    shape = RoundedCornerShape(bottomEnd = 12.dp, topStart = 16.dp),
                    modifier = Modifier.align(Alignment.TopStart)
                ) {
                    Text(
                        text = category.tag,
                        color = Color.White,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }

                // Category Icon Top-Right
                Surface(
                    color = MaterialTheme.colorScheme.surface.copy(alpha = 0.85f),
                    shape = CircleShape,
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(8.dp)
                        .size(30.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = category.icon,
                            contentDescription = null,
                            tint = RentAnyGreen,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }

                // Name & Item Count Overlay
                Column(
                    modifier = Modifier
                        .align(Alignment.BottomStart)
                        .padding(10.dp)
                ) {
                    Text(
                        text = category.name,
                        color = Color.White,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        text = category.itemCount,
                        color = Color.White.copy(alpha = 0.85f),
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            // Body Content
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text(
                    text = category.popularItems,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    lineHeight = 16.sp
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Browse",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = RentAnyGreen
                    )
                    Spacer(modifier = Modifier.width(2.dp))
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = null,
                        tint = RentAnyGreen,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CategoryListCard(category: CategoryDetail, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)),
        modifier = Modifier
            .fillMaxWidth()
            .testTag("category_list_card_${category.name.lowercase()}")
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Left Image
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(10.dp))
            ) {
                AsyncImage(
                    model = category.imageUrl,
                    contentDescription = category.name,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize()
                )
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.15f))
                )
                Surface(
                    color = category.accentColor,
                    shape = RoundedCornerShape(bottomEnd = 8.dp),
                    modifier = Modifier.align(Alignment.TopStart)
                ) {
                    Text(
                        text = category.tag,
                        color = Color.White,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            // Middle Info
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Text(
                        text = category.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Surface(
                        color = RentAnyGreen.copy(alpha = 0.12f),
                        shape = RoundedCornerShape(4.dp)
                    ) {
                        Text(
                            text = category.itemCount,
                            color = RentAnyGreen,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }

                Text(
                    text = category.popularItems,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            // Right Arrow Action Icon
            Surface(
                shape = CircleShape,
                color = RentAnyGreen.copy(alpha = 0.1f),
                modifier = Modifier.size(36.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = "Explore",
                        tint = RentAnyGreen
                    )
                }
            }
        }
    }
}


// ================= SETTINGS SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreenView(viewModel: RentViewModel) {
    val profile by viewModel.profileState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Mini profile card
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Surface(shape = CircleShape, color = RentAnyGreen, modifier = Modifier.size(50.dp)) {
                        Box(contentAlignment = Alignment.Center) {
                            Text(profile?.name?.first().toString(), color = Color.White, fontWeight = FontWeight.Bold)
                        }
                    }
                    Column {
                        Text(profile?.name ?: "Rohan Patel", fontWeight = FontWeight.Bold)
                        Text(profile?.email ?: "rohanpatel@gmail.com", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            ProfileNavigationRow(Icons.Default.Person, "Account Settings", onClick = { viewModel.navigateTo(Screen.AccountSettings) })
            ProfileNavigationRow(Icons.Default.Lock, "Security", onClick = { viewModel.navigateTo(Screen.Security) })
            ProfileNavigationRow(Icons.Default.ShoppingCart, "Payment Methods", onClick = { viewModel.navigateTo(Screen.PaymentMethods) })
            ProfileNavigationRow(Icons.Default.Notifications, "Notifications", onClick = { viewModel.navigateTo(Screen.Notifications) })
            ProfileNavigationRow(Icons.Default.Lock, "Privacy", onClick = { viewModel.navigateTo(Screen.Privacy) })
            ProfileNavigationRow(Icons.Default.LocationOn, "Location", onClick = { viewModel.navigateTo(Screen.Location) })
            ProfileNavigationRow(Icons.Default.Refresh, "Backend Cloud Sync", onClick = { viewModel.navigateTo(Screen.CloudSyncSettings) })
            ProfileNavigationRow(Icons.Default.Info, "Help & Support", onClick = { viewModel.navigateTo(Screen.HelpSupport) })
            ProfileNavigationRow(Icons.Default.Info, "About RentAny", onClick = { viewModel.navigateTo(Screen.About) })

            val context = LocalContext.current
            val settingsVal by viewModel.settingsState.collectAsStateWithLifecycle()
            ProfileNavigationRow(
                icon = Icons.Default.Refresh,
                label = "Check for Updates (Download Latest APK)",
                onClick = {
                    val apkUrl = "https://github.com/abdulzubair1135/rentANY/raw/main/backend/uploads/app-debug.apk"
                    Toast.makeText(context, "Opening GitHub update link...", Toast.LENGTH_SHORT).show()
                    try {
                        val intent = Intent(Intent.ACTION_VIEW, android.net.Uri.parse(apkUrl))
                        context.startActivity(intent)
                    } catch (e: Exception) {
                        Toast.makeText(context, "Error: ${e.message}", Toast.LENGTH_LONG).show()
                    }
                }
            )
        }
    }
}

// ================= SETTINGS SUB-SCREENS =================

// Account Settings
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AccountSettingsView(viewModel: RentViewModel) {
    val profile by viewModel.profileState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    var name by remember(profile) { mutableStateOf(profile?.name ?: "") }
    var email by remember(profile) { mutableStateOf(profile?.email ?: "") }
    var phone by remember(profile) { mutableStateOf(profile?.phone ?: "") }
    var address by remember(profile) { mutableStateOf(profile?.address ?: "") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Account Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Full Name") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = email, onValueChange = { email = it }, label = { Text("Email") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = phone, onValueChange = { phone = it }, label = { Text("Phone Number") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = address, onValueChange = { address = it }, label = { Text("Address") }, modifier = Modifier.fillMaxWidth(), minLines = 2)

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    profile?.let {
                        viewModel.updateProfile(it.copy(name = name, email = email, phone = phone, address = address))
                        Toast.makeText(context, "Profile Saved Successfully!", Toast.LENGTH_SHORT).show()
                        viewModel.navigateBack()
                    }
                },
                colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth().height(50.dp)
            ) {
                Text("Save Profile", fontWeight = FontWeight.Bold)
            }
        }
    }
}

// Security
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SecuritySettingsView(viewModel: RentViewModel) {
    val settings by viewModel.settingsState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Security", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Two-factor Authentication switch
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Two-Factor Authentication", fontWeight = FontWeight.Bold)
                    Text("Add extra security to your account", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.showOnlineStatus ?: true,
                    onCheckedChange = {
                        settings?.let { s ->
                            viewModel.updateSettings(s.copy(showOnlineStatus = it))
                        }
                    }
                )
            }

            Divider()

            ProfileNavigationRow(Icons.Default.Lock, "Change Password", onClick = { })
            ProfileNavigationRow(Icons.Default.Info, "Logged-In Devices", onClick = { })
            ProfileNavigationRow(Icons.Default.List, "Active Sessions", onClick = { })
        }
    }
}

// Payment Methods (Wallet and adding money)
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaymentMethodsView(viewModel: RentViewModel) {
    val profile by viewModel.profileState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Payment Methods", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(
                colors = CardDefaults.cardColors(containerColor = RentAnyGreen.copy(alpha = 0.1f)),
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("Wallet Balance", fontWeight = FontWeight.Bold, color = RentAnyGreenDark)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("₹${profile?.walletBalance?.toInt() ?: 2450}", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold, color = RentAnyGreen)
                    Spacer(modifier = Modifier.height(12.dp))
                    Button(
                        onClick = {
                            viewModel.addWalletMoney(500.0)
                            Toast.makeText(context, "₹500 added successfully!", Toast.LENGTH_SHORT).show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen)
                    ) {
                        Text("Add Money")
                    }
                }
            }

            Text("Saved Payment Methods", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            ProfileNavigationRow(Icons.Default.Build, "UPI (rohanpatel@oksbi)", onClick = { })
            ProfileNavigationRow(Icons.Default.Lock, "Visa Ending in 4242", onClick = { })
        }
    }
}

// Notification Settings
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotificationSettingsView(viewModel: RentViewModel) {
    val settings by viewModel.settingsState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Notifications", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Booking Updates", fontWeight = FontWeight.Bold)
                    Text("Receive push notifications on booking statuses", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.bookingUpdates ?: true,
                    onCheckedChange = {
                        settings?.let { s -> viewModel.updateSettings(s.copy(bookingUpdates = it)) }
                    }
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Messages", fontWeight = FontWeight.Bold)
                    Text("Notify when you get new chat messages", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.messagesNotification ?: true,
                    onCheckedChange = {
                        settings?.let { s -> viewModel.updateSettings(s.copy(messagesNotification = it)) }
                    }
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Offers & Deals", fontWeight = FontWeight.Bold)
                    Text("Receive offers and local discounts", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.offersNotification ?: false,
                    onCheckedChange = {
                        settings?.let { s -> viewModel.updateSettings(s.copy(offersNotification = it)) }
                    }
                )
            }
        }
    }
}

// Privacy Settings
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PrivacySettingsView(viewModel: RentViewModel) {
    val settings by viewModel.settingsState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Privacy Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Show Online Status", fontWeight = FontWeight.Bold)
                    Text("Let others see when you are online", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.showOnlineStatus ?: true,
                    onCheckedChange = {
                        settings?.let { s -> viewModel.updateSettings(s.copy(showOnlineStatus = it)) }
                    }
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Show Phone Number", fontWeight = FontWeight.Bold)
                    Text("Lenders and renters can see your number", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.showPhoneNumber ?: false,
                    onCheckedChange = {
                        settings?.let { s -> viewModel.updateSettings(s.copy(showPhoneNumber = it)) }
                    }
                )
            }
        }
    }
}

// Location Settings
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LocationSettingsView(viewModel: RentViewModel) {
    val settings by viewModel.settingsState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Location Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("Search Radius: ${settings?.searchRadiusKm ?: 10} km", fontWeight = FontWeight.Bold)
            Slider(
                value = (settings?.searchRadiusKm ?: 10).toFloat(),
                onValueChange = {
                    settings?.let { s -> viewModel.updateSettings(s.copy(searchRadiusKm = it.toInt())) }
                },
                valueRange = 1f..50f
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Use Current GPS Location", fontWeight = FontWeight.Bold)
                    Text("Find rentals directly near your current position", style = MaterialTheme.typography.bodySmall)
                }
                Switch(
                    checked = settings?.useCurrentLocation ?: true,
                    onCheckedChange = {
                        settings?.let { s -> viewModel.updateSettings(s.copy(useCurrentLocation = it)) }
                    }
                )
            }
        }
    }
}

// Help & Support
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HelpSupportView(viewModel: RentViewModel) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Help & Support", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(colors = CardDefaults.cardColors(containerColor = RentAnyGreen)) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("How can we help today?", color = Color.White, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleLarge)
                    Text("Our support agents are available online 24/7.", color = Color.White.copy(alpha = 0.8f))
                }
            }

            Text("Frequently Asked Questions", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
            ProfileNavigationRow(Icons.Default.Info, "How does security deposit refund work?", onClick = { })
            ProfileNavigationRow(Icons.Default.Info, "What if an item is damaged?", onClick = { })
            ProfileNavigationRow(Icons.Default.Info, "Lender Cancellation Policy", onClick = { })
        }
    }
}

// About
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AboutRentAnyView(viewModel: RentViewModel) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("About RentAny", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Surface(shape = CircleShape, color = RentAnyGreen, modifier = Modifier.size(80.dp)) {
                Box(contentAlignment = Alignment.Center) {
                    Text("R", color = Color.White, fontWeight = FontWeight.Black, style = MaterialTheme.typography.displaySmall)
                }
            }

            Text("RentAny", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.headlineMedium)
            Text("Version 1.0.0", color = MaterialTheme.colorScheme.onSurfaceVariant)

            Divider()

            Text(
                text = "RentAny is a peer-to-peer neighborhood rental marketplace that connects local item owners with renters securely. We empower local sharing communities, saving costs, reducing wastes, and building trust in our neighborhoods.",
                textAlign = TextAlign.Center,
                lineHeight = 22.sp
            )

            Spacer(modifier = Modifier.weight(1f))

            Text("© 2026 RentAny, Inc. All rights reserved.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

// More Features
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoreFeaturesView(viewModel: RentViewModel) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("More Features", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Refer & Earn", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                    Text("Invite your friends to list items, and earn ₹100 credit on every referral.")
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Safety Center", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                    Text("Learn how we verify users and protect neighborhood transactions.")
                }
            }
        }
    }
}

// ================= BACKEND CLOUD SYNC SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CloudSyncSettingsView(viewModel: RentViewModel) {
    val settings by viewModel.settingsState.collectAsStateWithLifecycle()
    val syncStatus by viewModel.syncStatus.collectAsStateWithLifecycle()
    val context = LocalContext.current

    var backendUrlState by remember { mutableStateOf("") }
    var syncEnabledState by remember { mutableStateOf(false) }

    LaunchedEffect(settings) {
        settings?.let {
            backendUrlState = it.backendUrl
            syncEnabledState = it.syncEnabled
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Backend Cloud Sync", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Deploy your own backend server and synchronize your rental listings, bookings, and chats in real-time across devices.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Server Configuration",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = RentAnyGreen
                    )

                    OutlinedTextField(
                        value = backendUrlState,
                        onValueChange = { backendUrlState = it },
                        label = { Text("Backend Base URL") },
                        placeholder = { Text("e.g. https://my-backend.onrender.com") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Enable Cloud Syncing", fontWeight = FontWeight.SemiBold)
                            Text("Sync local data automatically", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Switch(
                            checked = syncEnabledState,
                            onCheckedChange = { syncEnabledState = it }
                        )
                    }

                    Button(
                        onClick = {
                            settings?.let { s ->
                                viewModel.updateSettings(
                                    s.copy(
                                        backendUrl = backendUrlState.trim(),
                                        syncEnabled = syncEnabledState
                                    )
                                )
                                Toast.makeText(context, "Settings saved successfully", Toast.LENGTH_SHORT).show()
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Save Configuration", color = Color.White)
                    }
                }
            }

            if (syncEnabledState && backendUrlState.isNotEmpty()) {
                Card(
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Manual Sync",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground,
                            modifier = Modifier.align(Alignment.Start)
                        )

                        Text(
                            text = "Force full background push/pull sync of listings, bookings, messages, and profile configurations with the remote server.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.align(Alignment.Start)
                        )

                        if (syncStatus != null) {
                            Text(
                                text = "Status: $syncStatus",
                                fontWeight = FontWeight.Medium,
                                color = if (syncStatus!!.contains("successful")) RentAnyGreen else MaterialTheme.colorScheme.onBackground
                            )
                        }

                        Button(
                            onClick = {
                                viewModel.triggerSync { success ->
                                    val msg = if (success) "Sync complete!" else "Sync failed. Check backend URL."
                                    Toast.makeText(context, msg, Toast.LENGTH_LONG).show()
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Icon(Icons.Default.Refresh, contentDescription = null, tint = Color.White)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Sync Now", color = Color.White)
                        }
                    }
                }
            }

            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Deployment Guide",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        text = "We have prepared a complete Node.js / Express backend with zero-config local persistence in the /backend folder of this workspace.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "You can deploy it instantly to platforms like Render, Vercel, or Heroku. Refer to the /backend/README.md file for easy instructions.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}

// ================= CART SCREEN =================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CartScreenView(viewModel: RentViewModel) {
    val cartItems by viewModel.cartItemsState.collectAsStateWithLifecycle()
    val profile by viewModel.profileState.collectAsStateWithLifecycle()
    val context = LocalContext.current

    // Calculations
    val rentSubtotal = cartItems.sumOf { it.pricePerDay * it.durationDays }
    val securityDepositTotal = cartItems.sumOf { it.securityDeposit }
    val totalPayable = rentSubtotal + securityDepositTotal

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Shopping Cart", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { viewModel.navigateBack() }) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    if (cartItems.isNotEmpty()) {
                        TextButton(onClick = { viewModel.clearCart() }) {
                            Text("Clear All", color = MaterialTheme.colorScheme.error)
                        }
                    }
                }
            )
        }
    ) { innerPadding ->
        if (cartItems.isEmpty()) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Surface(
                    shape = CircleShape,
                    color = RentAnyGreen.copy(alpha = 0.08f),
                    modifier = Modifier.size(100.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Default.ShoppingCart,
                            contentDescription = null,
                            tint = RentAnyGreen,
                            modifier = Modifier.size(48.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))
                Text(
                    text = "Your Cart is Empty",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Browse and rent high-quality local items. They will appear here for a simple, single checkout.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                    lineHeight = 20.sp
                )
                Spacer(modifier = Modifier.height(32.dp))
                Button(
                    onClick = { viewModel.navigateTo(Screen.Home) },
                    colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth(0.8f)
                        .height(48.dp)
                ) {
                    Text("Explore Listings", fontWeight = FontWeight.Bold)
                }
            }
        } else {
            Box(modifier = Modifier.fillMaxSize()) {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 16.dp, bottom = 220.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(cartItems) { cartItem ->
                        Card(
                            shape = RoundedCornerShape(12.dp),
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(12.dp),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                // Image
                                AsyncImage(
                                    model = cartItem.itemImageUrl,
                                    contentDescription = cartItem.itemName,
                                    modifier = Modifier
                                        .size(80.dp)
                                        .clip(RoundedCornerShape(8.dp)),
                                    contentScale = ContentScale.Crop
                                )

                                // Info Column
                                Column(
                                    modifier = Modifier.weight(1f),
                                    verticalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.Top
                                    ) {
                                        Text(
                                            text = cartItem.itemName,
                                            style = MaterialTheme.typography.titleMedium,
                                            fontWeight = FontWeight.Bold,
                                            maxLines = 1,
                                            overflow = TextOverflow.Ellipsis,
                                            modifier = Modifier.weight(1f)
                                        )
                                        IconButton(
                                            onClick = { viewModel.removeFromCart(cartItem.id) },
                                            modifier = Modifier.size(24.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Delete,
                                                contentDescription = "Remove",
                                                tint = MaterialTheme.colorScheme.error,
                                                modifier = Modifier.size(18.dp)
                                            )
                                        }
                                    }

                                    Text(
                                        text = "₹${cartItem.pricePerDay.toInt()}/day  •  Deposit: ₹${cartItem.securityDeposit.toInt()}",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )

                                    Spacer(modifier = Modifier.height(4.dp))

                                    // Duration Selector & Delivery Switch
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        // Days selector
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                                        ) {
                                            Text(
                                                text = "Days:",
                                                style = MaterialTheme.typography.bodySmall,
                                                color = MaterialTheme.colorScheme.onSurfaceVariant
                                            )
                                            // Minus
                                            Surface(
                                                onClick = {
                                                    if (cartItem.durationDays > 1) {
                                                        viewModel.updateCartItemDuration(cartItem.id, cartItem.durationDays - 1)
                                                    }
                                                },
                                                shape = RoundedCornerShape(4.dp),
                                                color = MaterialTheme.colorScheme.surfaceVariant,
                                                modifier = Modifier.size(24.dp)
                                            ) {
                                                Box(contentAlignment = Alignment.Center) {
                                                    Text("-", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                                                }
                                            }

                                            Text(
                                                text = "${cartItem.durationDays}",
                                                style = MaterialTheme.typography.bodyMedium,
                                                fontWeight = FontWeight.Bold
                                            )

                                            // Plus
                                            Surface(
                                                onClick = {
                                                    viewModel.updateCartItemDuration(cartItem.id, cartItem.durationDays + 1)
                                                },
                                                shape = RoundedCornerShape(4.dp),
                                                color = MaterialTheme.colorScheme.surfaceVariant,
                                                modifier = Modifier.size(24.dp)
                                            ) {
                                                Box(contentAlignment = Alignment.Center) {
                                                    Text("+", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                                                }
                                            }
                                        }

                                        // Delivery selection
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                                        ) {
                                            Text(
                                                text = if (cartItem.deliveryType == "Delivery") "Delivery" else "Pickup",
                                                style = MaterialTheme.typography.bodySmall,
                                                fontWeight = FontWeight.SemiBold,
                                                color = RentAnyGreen
                                            )
                                            Switch(
                                                checked = cartItem.deliveryType == "Delivery",
                                                onCheckedChange = { isDelivery ->
                                                    val type = if (isDelivery) "Delivery" else "Self Pickup"
                                                    viewModel.updateCartItemDeliveryType(cartItem.id, type)
                                                },
                                                modifier = Modifier.scale(0.7f)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Summary Panel
                Card(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .fillMaxWidth()
                        .shadow(12.dp),
                    shape = RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(
                        modifier = Modifier
                            .padding(16.dp)
                            .fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Rent Subtotal:", color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text("₹${rentSubtotal.toInt()}", fontWeight = FontWeight.SemiBold)
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Security Deposits (Refundable):", color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text("₹${securityDepositTotal.toInt()}", fontWeight = FontWeight.SemiBold)
                        }

                        Divider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Total Payable:",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                "₹${totalPayable.toInt()}",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = RentAnyGreen
                            )
                        }

                        Spacer(modifier = Modifier.height(4.dp))

                        Button(
                            onClick = {
                                viewModel.checkoutCart {
                                    Toast.makeText(context, "All Rental Orders Placed Successfully!", Toast.LENGTH_LONG).show()
                                    viewModel.navigateTo(Screen.MyBookings)
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = RentAnyGreen),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(50.dp)
                                .testTag("checkout_cart_button")
                        ) {
                            Text("Confirm Rental Checkout", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

