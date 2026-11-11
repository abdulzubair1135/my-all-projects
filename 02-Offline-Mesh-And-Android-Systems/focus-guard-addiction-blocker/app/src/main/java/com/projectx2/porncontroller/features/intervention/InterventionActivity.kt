package com.projectx2.porncontroller.features.intervention

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.addCallback
import androidx.activity.compose.setContent
import com.projectx2.porncontroller.MainActivity
import com.projectx2.porncontroller.core.navigation.Screen
import com.projectx2.porncontroller.core.theme.PornControllerTheme
import com.projectx2.porncontroller.domain.rules.InterventionEngine
import com.projectx2.porncontroller.services.AccessibilityMonitorService

class InterventionActivity : ComponentActivity() {

    companion object {
        const val EXTRA_TRIGGER_SOURCE = "extra_trigger_source"
        const val EXTRA_CATEGORY = "extra_category"
        const val EXTRA_CUSTOM_MSG = "extra_custom_msg"
    }

    private fun kickUserToHomeScreenAndFinish() {
        // 1. Send system HOME action via Accessibility service to minimize offensive browser/app
        try {
            AccessibilityMonitorService.instance?.performGlobalAction(AccessibilityService.GLOBAL_ACTION_HOME)
        } catch (_: Exception) {}

        // 2. Start Home intent to guarantee landing directly on device launcher
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        startActivity(homeIntent)
        finish()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Ensure back gesture / button always boots to Home screen, never back to bad app
        onBackPressedDispatcher.addCallback(this) {
            kickUserToHomeScreenAndFinish()
        }

        val triggerSource = intent.getStringExtra(EXTRA_TRIGGER_SOURCE) ?: ""
        val category = intent.getStringExtra(EXTRA_CATEGORY) ?: "MOTIVATIONAL"
        val customMsg = intent.getStringExtra(EXTRA_CUSTOM_MSG) ?: ""

        val displayMessage = InterventionEngine.getInterventionMessage(category, customMsg)

        setContent {
            PornControllerTheme {
                InterventionScreen(
                    triggerSource = triggerSource,
                    message = displayMessage,
                    category = category,
                    onReturnToWork = {
                        kickUserToHomeScreenAndFinish()
                    },
                    onTakeBreak = {
                        // Open app directly to Focus Mode with 5 min break
                        val mainIntent = Intent(this, MainActivity::class.java).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                            putExtra("NAVIGATE_TO", Screen.FocusMode.route)
                        }
                        startActivity(mainIntent)
                        finish()
                    },
                    onCompleteTask = {
                        // Open app to Task Manager
                        val mainIntent = Intent(this, MainActivity::class.java).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                            putExtra("NAVIGATE_TO", Screen.TaskManager.route)
                        }
                        startActivity(mainIntent)
                        finish()
                    },
                    onDismiss = {
                        kickUserToHomeScreenAndFinish()
                    }
                )
            }
        }
    }
}
