package com.couplecanvas.app.data.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.util.UUID

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_preferences")

class UserPreferencesRepository(private val context: Context) {

    companion object {
        private val KEY_USER_ID = stringPreferencesKey("user_id")
        private val KEY_DISPLAY_NAME = stringPreferencesKey("display_name")
        private val KEY_PHONE_NUMBER = stringPreferencesKey("phone_number")
        private val KEY_PARTNER_PHONE = stringPreferencesKey("partner_phone")
        private val KEY_PARTNER_NAME = stringPreferencesKey("partner_name")
        private val KEY_SIGNALING_SERVER_URL = stringPreferencesKey("signaling_server_url")
        private val KEY_DARK_MODE = booleanPreferencesKey("dark_mode")
        private val KEY_HAPTIC_FEEDBACK = booleanPreferencesKey("haptic_feedback")

        // Cloudflare Public WSS Signaling Endpoint
        const val DEFAULT_SIGNALING_URL = "wss://psychological-streams-centres-fell.trycloudflare.com"
    }

    val userId: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[KEY_USER_ID] ?: "CC-" + UUID.randomUUID().toString().take(6).uppercase()
    }

    val displayName: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[KEY_DISPLAY_NAME] ?: "Artist"
    }

    val phoneNumber: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[KEY_PHONE_NUMBER] ?: ""
    }

    val partnerPhone: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[KEY_PARTNER_PHONE] ?: ""
    }

    val partnerName: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[KEY_PARTNER_NAME] ?: ""
    }

    val signalingServerUrl: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[KEY_SIGNALING_SERVER_URL] ?: DEFAULT_SIGNALING_URL
    }

    val isDarkMode: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[KEY_DARK_MODE] ?: false
    }

    val isHapticEnabled: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[KEY_HAPTIC_FEEDBACK] ?: true
    }

    suspend fun saveUserId(userId: String) {
        context.dataStore.edit { prefs ->
            prefs[KEY_USER_ID] = userId
        }
    }

    suspend fun saveDisplayName(name: String) {
        context.dataStore.edit { prefs ->
            prefs[KEY_DISPLAY_NAME] = name
        }
    }

    suspend fun savePhoneNumber(phone: String) {
        context.dataStore.edit { prefs ->
            prefs[KEY_PHONE_NUMBER] = phone
        }
    }

    suspend fun savePartnerInfo(partnerPhone: String, partnerName: String) {
        context.dataStore.edit { prefs ->
            prefs[KEY_PARTNER_PHONE] = partnerPhone
            prefs[KEY_PARTNER_NAME] = partnerName
        }
    }

    suspend fun saveSignalingServerUrl(url: String) {
        context.dataStore.edit { prefs ->
            prefs[KEY_SIGNALING_SERVER_URL] = url
        }
    }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[KEY_DARK_MODE] = enabled
        }
    }

    suspend fun setHapticFeedback(enabled: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[KEY_HAPTIC_FEEDBACK] = enabled
        }
    }

    suspend fun clearAllData() {
        context.dataStore.edit { prefs ->
            prefs.clear()
        }
    }
}
