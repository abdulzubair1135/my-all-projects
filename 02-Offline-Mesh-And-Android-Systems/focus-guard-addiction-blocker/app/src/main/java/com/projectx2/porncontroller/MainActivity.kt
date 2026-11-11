package com.projectx2.porncontroller

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.projectx2.porncontroller.core.navigation.Screen
import com.projectx2.porncontroller.core.theme.CharcoalBackground
import com.projectx2.porncontroller.core.theme.PornControllerTheme
import com.projectx2.porncontroller.features.analytics.AnalyticsScreen
import com.projectx2.porncontroller.features.analytics.AnalyticsViewModel
import com.projectx2.porncontroller.features.dashboard.DashboardScreen
import com.projectx2.porncontroller.features.dashboard.DashboardViewModel
import com.projectx2.porncontroller.features.focus.FocusModeScreen
import com.projectx2.porncontroller.features.focus.FocusViewModel
import com.projectx2.porncontroller.features.history.DetectionHistoryScreen
import com.projectx2.porncontroller.features.keywords.KeywordManagerScreen
import com.projectx2.porncontroller.features.keywords.KeywordManagerViewModel
import com.projectx2.porncontroller.features.permissions.PermissionSetupScreen
import com.projectx2.porncontroller.features.protection.DomainManagerScreen
import com.projectx2.porncontroller.features.protection.DomainManagerViewModel
import com.projectx2.porncontroller.features.settings.AboutScreen
import com.projectx2.porncontroller.features.settings.SettingsScreen
import com.projectx2.porncontroller.features.splash.SplashScreen
import com.projectx2.porncontroller.features.tasks.TaskManagerScreen
import com.projectx2.porncontroller.features.tasks.TaskTimerScreen
import com.projectx2.porncontroller.features.tasks.TaskViewModel

class MainActivity : ComponentActivity() {

    private val dashboardViewModel: DashboardViewModel by viewModels()
    private val domainViewModel: DomainManagerViewModel by viewModels()
    private val keywordViewModel: KeywordManagerViewModel by viewModels()
    private val taskViewModel: TaskViewModel by viewModels()
    private val focusViewModel: FocusViewModel by viewModels()
    private val analyticsViewModel: AnalyticsViewModel by viewModels()

    override fun onResume() {
        super.onResume()
        dashboardViewModel.refreshServiceStates()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navigateToTarget = intent?.getStringExtra("NAVIGATE_TO")

        setContent {
            PornControllerTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = CharcoalBackground
                ) {
                    val navController = rememberNavController()

                    val startDestination = if (navigateToTarget != null) {
                        navigateToTarget
                    } else {
                        Screen.Splash.route
                    }

                    NavHost(
                        navController = navController,
                        startDestination = startDestination
                    ) {
                        composable(Screen.Splash.route) {
                            SplashScreen(
                                onSplashFinished = {
                                    navController.navigate(Screen.Dashboard.route) {
                                        popUpTo(Screen.Splash.route) { inclusive = true }
                                    }
                                }
                            )
                        }

                        composable(Screen.Dashboard.route) {
                            val localContext = androidx.compose.ui.platform.LocalContext.current
                            val lastBackPressTime = androidx.compose.runtime.remember { androidx.compose.runtime.mutableStateOf(0L) }

                            androidx.activity.compose.BackHandler {
                                val now = System.currentTimeMillis()
                                if (now - lastBackPressTime.value < 2000L) {
                                    (localContext as? android.app.Activity)?.finish()
                                } else {
                                    lastBackPressTime.value = now
                                    android.widget.Toast.makeText(
                                        localContext,
                                        "Press back again to exit",
                                        android.widget.Toast.LENGTH_SHORT
                                    ).show()
                                }
                            }

                            DashboardScreen(
                                viewModel = dashboardViewModel,
                                onNavigateToDomains = { navController.navigate(Screen.DomainManager.route) },
                                onNavigateToKeywords = { navController.navigate(Screen.KeywordManager.route) },
                                onNavigateToTasks = { navController.navigate(Screen.TaskManager.route) },
                                onNavigateToFocus = { navController.navigate(Screen.FocusMode.route) },
                                onNavigateToAnalytics = { navController.navigate(Screen.Analytics.route) },
                                onNavigateToHistory = { navController.navigate(Screen.History.route) },
                                onNavigateToPermissions = { navController.navigate(Screen.Permissions.route) },
                                onNavigateToSettings = { navController.navigate(Screen.Settings.route) }
                            )
                        }

                        composable(Screen.DomainManager.route) {
                            DomainManagerScreen(
                                viewModel = domainViewModel,
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.KeywordManager.route) {
                            KeywordManagerScreen(
                                viewModel = keywordViewModel,
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.TaskManager.route) {
                            TaskManagerScreen(
                                viewModel = taskViewModel,
                                onNavigateBack = { navController.popBackStack() },
                                onNavigateToTimer = { taskId ->
                                    navController.navigate(Screen.TaskTimer.createRoute(taskId))
                                }
                            )
                        }

                        composable(
                            route = Screen.TaskTimer.route,
                            arguments = listOf(navArgument("taskId") { type = NavType.LongType })
                        ) { backStackEntry ->
                            val taskId = backStackEntry.arguments?.getLong("taskId") ?: 0L
                            TaskTimerScreen(
                                taskId = taskId,
                                viewModel = taskViewModel,
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.FocusMode.route) {
                            FocusModeScreen(
                                viewModel = focusViewModel,
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.Analytics.route) {
                            AnalyticsScreen(
                                viewModel = analyticsViewModel,
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.History.route) {
                            DetectionHistoryScreen(
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.Permissions.route) {
                            PermissionSetupScreen(
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }

                        composable(Screen.Settings.route) {
                            SettingsScreen(
                                onNavigateBack = { navController.popBackStack() },
                                onNavigateToAbout = { navController.navigate(Screen.About.route) }
                            )
                        }

                        composable(Screen.About.route) {
                            AboutScreen(
                                onNavigateBack = { navController.popBackStack() }
                            )
                        }
                    }
                }
            }
        }
    }
}
