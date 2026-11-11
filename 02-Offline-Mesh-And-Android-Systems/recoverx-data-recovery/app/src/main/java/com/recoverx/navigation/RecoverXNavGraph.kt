package com.recoverx.navigation

import android.net.Uri
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.recoverx.app.AppContainer
import com.recoverx.data.entities.FileCategory
import com.recoverx.ui.diagnostics.StorageDiagnosticsScreen
import com.recoverx.ui.home.HomeDashboardScreen
import com.recoverx.ui.onboarding.*
import com.recoverx.ui.preview.FileDetailsScreen
import com.recoverx.ui.preview.ImagePreviewScreen
import com.recoverx.ui.preview.VideoPreviewScreen
import com.recoverx.ui.recovery.*
import com.recoverx.ui.scanning.*
import com.recoverx.ui.settings.*
import com.recoverx.ui.storage.CategoryBrowserScreen
import com.recoverx.ui.storage.FolderBrowserScreen
import com.recoverx.ui.storage.StorageExplorerScreen

@Composable
fun RecoverXNavGraph(
    navController: NavHostController,
    container: AppContainer
) {
    val scope = rememberCoroutineScope()

    NavHost(
        navController = navController,
        startDestination = Screen.Splash.route
    ) {
        // 1. Splash
        composable(Screen.Splash.route) {
            SplashScreen(
                onNavigateNext = {
                    navController.navigate(Screen.Welcome.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                }
            )
        }

        // 2. Welcome
        composable(Screen.Welcome.route) {
            WelcomeScreen(
                onNavigateNext = { navController.navigate(Screen.PrivacyIntro.route) }
            )
        }

        // 3. Privacy Intro
        composable(Screen.PrivacyIntro.route) {
            PrivacyIntroScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateNext = { navController.navigate(Screen.PermissionSetup.route) }
            )
        }

        // 4. Permission Setup
        composable(Screen.PermissionSetup.route) {
            PermissionSetupScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateNext = { navController.navigate(Screen.StorageAssessment.route) }
            )
        }

        // 5. Storage Assessment
        composable(Screen.StorageAssessment.route) {
            StorageAssessmentScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateNext = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Welcome.route) { inclusive = true }
                    }
                }
            )
        }

        // 6. Home Dashboard
        composable(Screen.Home.route) {
            HomeDashboardScreen(
                dbHelper = container.dbHelper,
                onNavigateQuickScan = { navController.navigate(Screen.QuickScan.route) },
                onNavigateAdvancedScan = { navController.navigate(Screen.AdvancedScan.route) },
                onNavigateStorageExplorer = { navController.navigate(Screen.StorageExplorer.route) },
                onNavigateRecoveryCenter = { navController.navigate(Screen.RecoveryCenter.route) },
                onNavigateCategory = { cat -> navController.navigate(Screen.CategoryBrowser.createRoute(cat)) },
                onNavigateDiagnostics = { navController.navigate(Screen.StorageDiagnostics.route) },
                onNavigateSettings = { navController.navigate(Screen.Settings.route) }
            )
        }

        // 7. Storage Explorer
        composable(Screen.StorageExplorer.route) {
            StorageExplorerScreen(
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateImagePreview = { id -> navController.navigate(Screen.ImagePreview.createRoute(id)) },
                onNavigateVideoPreview = { id -> navController.navigate(Screen.VideoPreview.createRoute(id)) },
                onNavigateItemDetails = { id -> navController.navigate(Screen.FileDetails.createRoute(id)) }
            )
        }

        // 8. Folder Browser
        composable(Screen.FolderBrowser.route) {
            FolderBrowserScreen(
                onNavigateBack = { navController.popBackStack() },
                onStartTreeScan = { treeUri ->
                    container.scanCoordinator.startAdvancedScan(scope, treeUri)
                    navController.navigate(Screen.ScanProgress.route)
                }
            )
        }

        // 9. Category Browser
        composable(
            route = Screen.CategoryBrowser.route,
            arguments = listOf(navArgument("category") { type = NavType.StringType })
        ) { backStackEntry ->
            val cat = backStackEntry.arguments?.getString("category") ?: "Other"
            CategoryBrowserScreen(
                categoryName = cat,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateImagePreview = { id -> navController.navigate(Screen.ImagePreview.createRoute(id)) },
                onNavigateVideoPreview = { id -> navController.navigate(Screen.VideoPreview.createRoute(id)) },
                onNavigateItemDetails = { id -> navController.navigate(Screen.FileDetails.createRoute(id)) }
            )
        }

        // 10. Quick Scan
        composable(Screen.QuickScan.route) {
            QuickScanScreen(
                onNavigateBack = { navController.popBackStack() },
                onStartScan = {
                    container.scanCoordinator.startQuickScan(scope)
                    navController.navigate(Screen.ScanProgress.route)
                }
            )
        }

        // 11. Advanced Scan
        composable(Screen.AdvancedScan.route) {
            AdvancedScanScreen(
                onNavigateBack = { navController.popBackStack() },
                onStartScan = {
                    container.scanCoordinator.startAdvancedScan(scope, null)
                    navController.navigate(Screen.ScanProgress.route)
                },
                onPickFolder = { navController.navigate(Screen.FolderBrowser.route) }
            )
        }

        // 12. Scan Progress
        composable(Screen.ScanProgress.route) {
            ScanProgressScreen(
                scanCoordinator = container.scanCoordinator,
                onNavigateBack = { navController.popBackStack() },
                onScanFinished = {
                    navController.navigate(Screen.ScanResults.route) {
                        popUpTo(Screen.ScanProgress.route) { inclusive = true }
                    }
                }
            )
        }

        // 13. Scan Results
        composable(Screen.ScanResults.route) {
            ScanResultsScreen(
                scanCoordinator = container.scanCoordinator,
                onNavigateBack = { navController.navigate(Screen.Home.route) },
                onNavigateImagePreview = { id -> navController.navigate(Screen.ImagePreview.createRoute(id)) },
                onNavigateVideoPreview = { id -> navController.navigate(Screen.VideoPreview.createRoute(id)) },
                onNavigateItemDetails = { id -> navController.navigate(Screen.FileDetails.createRoute(id)) },
                onNavigateRecoveryCenter = { navController.navigate(Screen.RecoveryCenter.route) }
            )
        }

        // 14. Filtered Result List
        composable(
            route = Screen.FilteredResults.route,
            arguments = listOf(navArgument("filter") { type = NavType.StringType })
        ) { backStackEntry ->
            val filter = backStackEntry.arguments?.getString("filter") ?: ""
            FilteredResultListScreen(
                filter = filter,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateImagePreview = { id -> navController.navigate(Screen.ImagePreview.createRoute(id)) },
                onNavigateVideoPreview = { id -> navController.navigate(Screen.VideoPreview.createRoute(id)) },
                onNavigateItemDetails = { id -> navController.navigate(Screen.FileDetails.createRoute(id)) }
            )
        }

        // 15. Image Preview
        composable(
            route = Screen.ImagePreview.route,
            arguments = listOf(navArgument("itemId") { type = NavType.LongType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong("itemId") ?: 0L
            ImagePreviewScreen(
                itemId = id,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateRestore = { itemId -> navController.navigate(Screen.RecoveryDestinationPicker.createRoute(itemId)) }
            )
        }

        // 16. Video Preview
        composable(
            route = Screen.VideoPreview.route,
            arguments = listOf(navArgument("itemId") { type = NavType.LongType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong("itemId") ?: 0L
            VideoPreviewScreen(
                itemId = id,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateRestore = { itemId -> navController.navigate(Screen.RecoveryDestinationPicker.createRoute(itemId)) }
            )
        }

        // 17. File Details
        composable(
            route = Screen.FileDetails.route,
            arguments = listOf(navArgument("itemId") { type = NavType.LongType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong("itemId") ?: 0L
            FileDetailsScreen(
                itemId = id,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigatePreview = { item ->
                    if (item.category == FileCategory.IMAGES) {
                        navController.navigate(Screen.ImagePreview.createRoute(item.id))
                    } else if (item.category == FileCategory.VIDEOS) {
                        navController.navigate(Screen.VideoPreview.createRoute(item.id))
                    }
                },
                onNavigateRestore = { itemId -> navController.navigate(Screen.RecoveryDestinationPicker.createRoute(itemId)) }
            )
        }

        // 18. Recovery Center
        composable(Screen.RecoveryCenter.route) {
            RecoveryCenterScreen(
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateImagePreview = { id -> navController.navigate(Screen.ImagePreview.createRoute(id)) },
                onNavigateVideoPreview = { id -> navController.navigate(Screen.VideoPreview.createRoute(id)) },
                onNavigateItemDetails = { id -> navController.navigate(Screen.FileDetails.createRoute(id)) },
                onNavigateHistory = { navController.navigate(Screen.RecoveryHistory.route) }
            )
        }

        // 19. Recovery Destination Picker
        composable(
            route = Screen.RecoveryDestinationPicker.route,
            arguments = listOf(navArgument("itemId") { type = NavType.LongType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong("itemId") ?: 0L
            RecoveryDestinationPickerScreen(
                itemId = id,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onStartRestoration = { itemId, uri ->
                    navController.navigate(Screen.RecoveryProgress.createRoute(itemId))
                }
            )
        }

        // 20. Recovery Progress
        composable(
            route = Screen.RecoveryProgress.route,
            arguments = listOf(navArgument("itemId") { type = NavType.LongType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong("itemId") ?: 0L
            RecoveryProgressScreen(
                itemId = id,
                dbHelper = container.dbHelper,
                recoveryManager = container.recoveryManager,
                destinationTreeUri = null,
                onNavigateBack = { navController.popBackStack() },
                onRestorationComplete = { recordId ->
                    navController.navigate(Screen.RecoveryReport.createRoute(recordId)) {
                        popUpTo(Screen.RecoveryProgress.createRoute(id)) { inclusive = true }
                    }
                }
            )
        }

        // 21. Recovery Report
        composable(
            route = Screen.RecoveryReport.route,
            arguments = listOf(navArgument("recordId") { type = NavType.LongType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getLong("recordId") ?: 0L
            RecoveryReportScreen(
                recordId = id,
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigateHome = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) { inclusive = true }
                    }
                }
            )
        }

        // 22. Recovery History
        composable(Screen.RecoveryHistory.route) {
            RecoveryHistoryScreen(
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 23. Storage Diagnostics
        composable(Screen.StorageDiagnostics.route) {
            StorageDiagnosticsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 24. Settings
        composable(Screen.Settings.route) {
            SettingsScreen(
                dbHelper = container.dbHelper,
                onNavigateBack = { navController.popBackStack() },
                onNavigatePrivacyCenter = { navController.navigate(Screen.PrivacyCenter.route) },
                onNavigateHelp = { navController.navigate(Screen.HelpLimitations.route) },
                onNavigateKnownIssues = { navController.navigate(Screen.KnownIssues.route) }
            )
        }

        // 25. Privacy Center
        composable(Screen.PrivacyCenter.route) {
            PrivacyCenterScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 26. Help & Limitations
        composable(Screen.HelpLimitations.route) {
            HelpLimitationsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 27. Known Issues
        composable(Screen.KnownIssues.route) {
            KnownIssuesScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
