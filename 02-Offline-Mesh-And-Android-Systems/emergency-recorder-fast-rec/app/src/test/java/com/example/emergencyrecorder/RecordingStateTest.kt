package com.example.emergencyrecorder

import com.example.emergencyrecorder.recording.RecordingState
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RecordingStateTest {

    @Test
    fun idleState_flags() {
        val state: RecordingState = RecordingState.Idle
        assertFalse(state.isRecording)
        assertTrue(state.canStart)
        assertFalse(state.canStop)
    }

    @Test
    fun startingState_flags() {
        val state: RecordingState = RecordingState.Starting
        assertFalse(state.isRecording)
        assertFalse(state.canStart)
        assertTrue(state.canStop)
    }

    @Test
    fun stoppingState_flags() {
        val state: RecordingState = RecordingState.Stopping
        assertFalse(state.isRecording)
        assertFalse(state.canStart)
        assertFalse(state.canStop)
    }

    @Test
    fun errorState_allowsRecovery() {
        val state: RecordingState = RecordingState.Error("Simulated error")
        assertFalse(state.isRecording)
        assertTrue(state.canStart)
        assertFalse(state.canStop)
    }
}
