package com.projectx2.porncontroller.core.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Dashboard : Screen("dashboard")
    object DomainManager : Screen("domain_manager")
    object KeywordManager : Screen("keyword_manager")
    object TaskManager : Screen("task_manager")
    object TaskTimer : Screen("task_timer/{taskId}") {
        fun createRoute(taskId: Long) = "task_timer/$taskId"
    }
    object FocusMode : Screen("focus_mode")
    object Analytics : Screen("analytics")
    object History : Screen("history")
    object Permissions : Screen("permissions")
    object Settings : Screen("settings")
    object About : Screen("about")
}
