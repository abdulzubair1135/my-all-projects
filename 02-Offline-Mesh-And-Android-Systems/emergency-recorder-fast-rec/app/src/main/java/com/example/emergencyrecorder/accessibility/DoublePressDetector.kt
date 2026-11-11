package com.example.emergencyrecorder.accessibility

/**
 * Detects double-press patterns using a monotonic time provider.
 * Protects against key bounce, rapid key spam, and duplicate triggers.
 */
class DoublePressDetector(
    private var windowMs: Long = 650L,
    private val debounceThresholdMs: Long = 40L,
    private val postTriggerCooldownMs: Long = 400L,
    private val timeProvider: () -> Long = { android.os.SystemClock.elapsedRealtime() }
) {

    private var firstPressTimestamp: Long = 0L
    private var lastTriggerTimestamp: Long = 0L

    fun updateWindow(newWindowMs: Long) {
        this.windowMs = newWindowMs
    }

    /**
     * Called whenever a KEYCODE_VOLUME_DOWN ACTION_DOWN event is received.
     * @return true if this press completes a valid double-press trigger, false otherwise.
     */
    @Synchronized
    fun onKeyDown(eventTimeMs: Long = timeProvider()): Boolean {
        val now = eventTimeMs

        // 1. Post-trigger cooldown: ignore key spam immediately following a trigger
        if (now - lastTriggerTimestamp < postTriggerCooldownMs) {
            return false
        }

        // 2. Hardware key bounce protection: ignore presses faster than physical debounce
        if (firstPressTimestamp > 0 && (now - firstPressTimestamp < debounceThresholdMs)) {
            return false
        }

        // 3. Evaluate double-press window
        val elapsedSinceFirst = now - firstPressTimestamp
        if (firstPressTimestamp > 0 && elapsedSinceFirst <= windowMs) {
            // Valid second press inside the active window!
            firstPressTimestamp = 0L
            lastTriggerTimestamp = now
            return true
        }

        // 4. First press in the detection cycle: open the window
        firstPressTimestamp = now
        return false
    }

    @Synchronized
    fun reset() {
        firstPressTimestamp = 0L
        lastTriggerTimestamp = 0L
    }
}
