package com.recoverx.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Welcome : Screen("welcome")
    object PrivacyIntro : Screen("privacy_intro")
    object PermissionSetup : Screen("permission_setup")
    object StorageAssessment : Screen("storage_assessment")
    object Home : Screen("home")
    object StorageExplorer : Screen("storage_explorer")
    object FolderBrowser : Screen("folder_browser")
    object CategoryBrowser : Screen("category_browser/{category}") {
        fun createRoute(category: String) = "category_browser/$category"
    }
    object QuickScan : Screen("quick_scan")
    object AdvancedScan : Screen("advanced_scan")
    object ScanProgress : Screen("scan_progress")
    object ScanResults : Screen("scan_results")
    object FilteredResults : Screen("filtered_results/{filter}") {
        fun createRoute(filter: String) = "filtered_results/$filter"
    }
    object ImagePreview : Screen("image_preview/{itemId}") {
        fun createRoute(itemId: Long) = "image_preview/$itemId"
    }
    object VideoPreview : Screen("video_preview/{itemId}") {
        fun createRoute(itemId: Long) = "video_preview/$itemId"
    }
    object FileDetails : Screen("file_details/{itemId}") {
        fun createRoute(itemId: Long) = "file_details/$itemId"
    }
    object RecoveryCenter : Screen("recovery_center")
    object RecoveryDestinationPicker : Screen("recovery_dest_picker/{itemId}") {
        fun createRoute(itemId: Long) = "recovery_dest_picker/$itemId"
    }
    object RecoveryProgress : Screen("recovery_progress/{itemId}") {
        fun createRoute(itemId: Long) = "recovery_progress/$itemId"
    }
    object RecoveryReport : Screen("recovery_report/{recordId}") {
        fun createRoute(recordId: Long) = "recovery_report/$recordId"
    }
    object RecoveryHistory : Screen("recovery_history")
    object StorageDiagnostics : Screen("storage_diagnostics")
    object Settings : Screen("settings")
    object PrivacyCenter : Screen("privacy_center")
    object HelpLimitations : Screen("help_limitations")
    object KnownIssues : Screen("known_issues")
}
