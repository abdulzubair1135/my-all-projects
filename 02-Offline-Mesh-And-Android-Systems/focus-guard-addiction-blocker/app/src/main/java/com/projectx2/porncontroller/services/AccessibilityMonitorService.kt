package com.projectx2.porncontroller.services

import android.accessibilityservice.AccessibilityService
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.provider.Settings
import android.text.TextUtils
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.projectx2.porncontroller.PornControllerApp
import com.projectx2.porncontroller.domain.rules.DomainDetectionEngine
import com.projectx2.porncontroller.domain.rules.KeywordDetectionEngine
import com.projectx2.porncontroller.domain.rules.RepetitionDetectionEngine
import com.projectx2.porncontroller.features.intervention.InterventionActivity
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AccessibilityMonitorService : AccessibilityService() {

    companion object {
        const val TAG = "AccessibilityMonitor"
        @Volatile
        var isRunning: Boolean = false
            private set

        @Volatile
        var instance: AccessibilityMonitorService? = null
            private set

        private val _isRunningFlow = MutableStateFlow(false)
        val isRunningFlow: StateFlow<Boolean> = _isRunningFlow.asStateFlow()

        fun isAccessibilityEnabledInSystem(context: Context): Boolean {
            val expectedComponentName = ComponentName(context, AccessibilityMonitorService::class.java)
            val enabledServices = Settings.Secure.getString(
                context.contentResolver,
                Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
            ) ?: return false
            val colonSplitter = TextUtils.SimpleStringSplitter(':')
            colonSplitter.setString(enabledServices)
            while (colonSplitter.hasNext()) {
                val componentNameString = colonSplitter.next()
                val enabledComponent = ComponentName.unflattenFromString(componentNameString)
                if (enabledComponent != null && enabledComponent == expectedComponentName) {
                    return true
                }
            }
            return false
        }
    }

    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Default + serviceJob)
    private val keywordEngine = KeywordDetectionEngine()
    private val repetitionEngine = RepetitionDetectionEngine()
    private val domainEngine = DomainDetectionEngine()
    @Volatile
    private var lastInterventionTimestamp: Long = 0L

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        isRunning = true
        _isRunningFlow.value = true
        Log.d(TAG, "AccessibilityMonitorService connected")

        // Load adult domains into engine
        val app = application as? PornControllerApp
        if (app != null) {
            serviceScope.launch {
                val domains = app.repository.getEnabledDomains()
                domainEngine.updateDomainList(domains)
                Log.d(TAG, "Loaded ${domains.size} adult domains into Accessibility monitor")
            }
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return

        val eventType = event.eventType
        if (eventType == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED ||
            eventType == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED ||
            eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ||
            eventType == AccessibilityEvent.TYPE_VIEW_FOCUSED
        ) {
            val rootNode = rootInActiveWindow ?: return
            inspectNodeHierarchy(rootNode, event.packageName?.toString())
        }
    }

    private fun inspectNodeHierarchy(node: AccessibilityNodeInfo, packageName: String?) {
        // Strict Privacy: Never inspect password or masked fields
        if (node.isPassword) {
            return
        }

        // Check text
        val text = node.text?.toString()
        if (!text.isNullOrBlank() && text.length > 2) {
            evaluateText(text, packageName)
        }

        // Also check contentDescription (browsers often put URL / page title here)
        val contentDesc = node.contentDescription?.toString()
        if (!contentDesc.isNullOrBlank() && contentDesc.length > 2 && contentDesc != text) {
            evaluateText(contentDesc, packageName)
        }

        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                inspectNodeHierarchy(child, packageName)
                child.recycle()
            }
        }
    }

    private fun evaluateText(text: String, packageName: String?) {
        val app = application as? PornControllerApp ?: return

        serviceScope.launch {
            val settings = app.repository.getSettings() ?: return@launch

            // ============================================================
            // 1. ADULT DOMAIN INTERCEPTION (Zero-Tolerance, 0-Second Delay)
            // ============================================================
            if (settings.isDomainProtectionEnabled) {
                val blockedDomain = domainEngine.findBlockedDomainInText(text)
                if (blockedDomain != null) {
                    val now = System.currentTimeMillis()
                    if (now - lastInterventionTimestamp < 2500L) {
                        return@launch
                    }
                    lastInterventionTimestamp = now

                    Log.i(TAG, "BLOCKED ADULT DOMAIN DETECTED: $blockedDomain in app $packageName (Text: $text)")

                    // 1. Record event in database
                    app.repository.recordDomainBlocked(blockedDomain)

                    // 2. Haptic alert
                    if (settings.hapticAlertsEnabled) {
                        triggerHaptic()
                    }

                    // 3. Immediately kick out the browser / offending app to Android Home Screen!
                    try {
                        performGlobalAction(GLOBAL_ACTION_HOME)
                    } catch (e: Exception) {
                        Log.e(TAG, "Error executing GLOBAL_ACTION_HOME", e)
                    }

                    // 4. Launch Intervention Screen with adult domain alert
                    launchIntervention(
                        triggerKeyword = blockedDomain,
                        category = "STRICT",
                        customMsg = "Adult content is blocked. Access to '$blockedDomain' has been terminated."
                    )
                    return@launch
                }
            }

            // ============================================================
            // 2. KEYWORD & OBSESSIVE SEARCH INTERCEPTION (Repetition Rules)
            // ============================================================
            if (!settings.isKeywordMonitoringEnabled) return@launch

            val keywords = app.repository.getEnabledKeywords()
            val matchedKeyword = keywordEngine.findMatchingKeyword(
                inputText = text,
                configuredKeywords = keywords,
                sensitivity = settings.detectionSensitivity
            )

            if (matchedKeyword != null) {
                val shouldTrigger = repetitionEngine.recordAndCheckRepetition(
                    keyword = matchedKeyword.keyword,
                    fullQuery = text,
                    threshold = matchedKeyword.repetitionThreshold,
                    windowMinutes = 10,
                    cooldownMinutes = settings.cooldownPeriodMinutes
                )

                if (shouldTrigger) {
                    val now = System.currentTimeMillis()
                    if (now - lastInterventionTimestamp < 2500L) {
                        return@launch
                    }
                    lastInterventionTimestamp = now

                    Log.d(TAG, "Triggered intervention for keyword: ${matchedKeyword.keyword}")

                    // 1. Record event in database
                    app.repository.recordKeywordDetected(
                        id = matchedKeyword.id,
                        keyword = matchedKeyword.keyword,
                        appPackage = packageName
                    )

                    // 2. Haptic feedback
                    if (settings.hapticAlertsEnabled) {
                        triggerHaptic()
                    }

                    // 3. Immediately kick out offending app/browser to Android Home screen!
                    try {
                        performGlobalAction(GLOBAL_ACTION_HOME)
                    } catch (e: Exception) {
                        Log.e(TAG, "Error executing GLOBAL_ACTION_HOME", e)
                    }

                    // 4. Launch Intervention Screen on top
                    launchIntervention(
                        triggerKeyword = matchedKeyword.keyword,
                        category = settings.interventionCategory,
                        customMsg = settings.customInterventionMessage
                    )
                }
            }
        }
    }

    private fun launchIntervention(triggerKeyword: String, category: String, customMsg: String) {
        val intent = Intent(this, InterventionActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                    Intent.FLAG_ACTIVITY_CLEAR_TOP or
                    Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra(InterventionActivity.EXTRA_TRIGGER_SOURCE, triggerKeyword)
            putExtra(InterventionActivity.EXTRA_CATEGORY, category)
            putExtra(InterventionActivity.EXTRA_CUSTOM_MSG, customMsg)
        }
        startActivity(intent)
    }

    private fun triggerHaptic() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vibratorManager = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                vibratorManager.defaultVibrator.vibrate(
                    VibrationEffect.createWaveform(longArrayOf(0, 150, 100, 150), -1)
                )
            } else {
                @Suppress("DEPRECATION")
                val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                @Suppress("DEPRECATION")
                vibrator.vibrate(250)
            }
        } catch (_: Exception) {}
    }

    override fun onInterrupt() {
        Log.w(TAG, "AccessibilityMonitorService interrupted")
    }

    override fun onDestroy() {
        if (instance == this) {
            instance = null
        }
        isRunning = false
        _isRunningFlow.value = false
        serviceJob.cancel()
        repetitionEngine.clearAll()
        super.onDestroy()
    }
}
