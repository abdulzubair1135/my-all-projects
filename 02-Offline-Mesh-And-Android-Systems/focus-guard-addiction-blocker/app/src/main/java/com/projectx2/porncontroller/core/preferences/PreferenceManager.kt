package com.projectx2.porncontroller.core.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_preferences")

class PreferenceManager(private val context: Context) {
    companion object {
        val KEY_VPN_ACTIVE = booleanPreferencesKey("vpn_active")
        val KEY_ACCESSIBILITY_ACTIVE = booleanPreferencesKey("accessibility_active")
        val KEY_FOCUS_MODE_ACTIVE = booleanPreferencesKey("focus_mode_active")
        val KEY_LAST_INTERVENTION_TIME = longPreferencesKey("last_intervention_time")
        val KEY_SOUND_INTRO_ENABLED = booleanPreferencesKey("sound_intro_enabled")
    }

    val isVpnActive: Flow<Boolean> = context.dataStore.data.map { it[KEY_VPN_ACTIVE] ?: false }
    val isAccessibilityActive: Flow<Boolean> = context.dataStore.data.map { it[KEY_ACCESSIBILITY_ACTIVE] ?: false }
    val isFocusModeActive: Flow<Boolean> = context.dataStore.data.map { it[KEY_FOCUS_MODE_ACTIVE] ?: false }
    val isSoundIntroEnabled: Flow<Boolean> = context.dataStore.data.map { it[KEY_SOUND_INTRO_ENABLED] ?: true }

    suspend fun setVpnActive(active: Boolean) {
        context.dataStore.edit { it[KEY_VPN_ACTIVE] = active }
    }

    suspend fun setAccessibilityActive(active: Boolean) {
        context.dataStore.edit { it[KEY_ACCESSIBILITY_ACTIVE] = active }
    }

    suspend fun setFocusModeActive(active: Boolean) {
        context.dataStore.edit { it[KEY_FOCUS_MODE_ACTIVE] = active }
    }

    suspend fun setLastInterventionTime(time: Long) {
        context.dataStore.edit { it[KEY_LAST_INTERVENTION_TIME] = time }
    }

    suspend fun setSoundIntroEnabled(enabled: Boolean) {
        context.dataStore.edit { it[KEY_SOUND_INTRO_ENABLED] = enabled }
    }
}
