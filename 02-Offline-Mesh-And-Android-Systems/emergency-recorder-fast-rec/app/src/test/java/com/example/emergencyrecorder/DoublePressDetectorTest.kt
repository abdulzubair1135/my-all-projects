package com.example.emergencyrecorder

import com.example.emergencyrecorder.accessibility.DoublePressDetector
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class DoublePressDetectorTest {

    private var simulatedTime: Long = 1000L
    private lateinit var detector: DoublePressDetector

    @Before
    fun setUp() {
        simulatedTime = 1000L
        detector = DoublePressDetector(
            windowMs = 650L,
            debounceThresholdMs = 40L,
            postTriggerCooldownMs = 400L,
            timeProvider = { simulatedTime }
        )
    }

    @Test
    fun singlePress_doesNotTrigger() {
        val result = detector.onKeyDown(simulatedTime)
        assertFalse("First press must not trigger recording", result)
    }

    @Test
    fun validDoublePress_withinWindow_triggers() {
        // First press at t=1000
        assertFalse(detector.onKeyDown(1000L))

        // Second press at t=1400 (400ms later, within 650ms window)
        val result = detector.onKeyDown(1400L)
        assertTrue("Second press within window must trigger recording", result)
    }

    @Test
    fun slowDoublePress_outsideWindow_resetsAndDoesNotTrigger() {
        // First press at t=1000
        assertFalse(detector.onKeyDown(1000L))

        // Second press at t=1750 (750ms later, exceeds 650ms window)
        val result = detector.onKeyDown(1750L)
        assertFalse("Second press after window expiry must become a new first press and NOT trigger", result)
    }

    @Test
    fun rapidBounce_underDebounceThreshold_isIgnored() {
        // First press at t=1000
        assertFalse(detector.onKeyDown(1000L))

        // Bounce at t=1020 (20ms later, < 40ms threshold)
        assertFalse(detector.onKeyDown(1020L))

        // Real second press at t=1300 (300ms from original)
        assertTrue("Valid second press after debounce must trigger", detector.onKeyDown(1300L))
    }

    @Test
    fun postTriggerCooldown_preventsKeySpam() {
        // Trigger sequence
        detector.onKeyDown(1000L)
        assertTrue(detector.onKeyDown(1300L)) // Triggered!

        // Immediate subsequent spam presses (e.g. at 1400ms, 1500ms) within 400ms cooldown
        assertFalse("Spam press during cooldown must be ignored", detector.onKeyDown(1400L))
        assertFalse("Spam press during cooldown must be ignored", detector.onKeyDown(1500L))

        // After cooldown passes (1300 + 400 = 1700ms) -> t=1800 starts a fresh cycle
        assertFalse("Fresh first press after cooldown", detector.onKeyDown(1800L))
        assertTrue("Fresh second press triggers again", detector.onKeyDown(2100L))
    }
}
