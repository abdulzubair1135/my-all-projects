package com.example.lifevault.security

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.util.UUID

class TokenStore(context: Context) {

    private val prefs: SharedPreferences

    init {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        prefs = EncryptedSharedPreferences.create(
            context,
            "life_vault_secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        // Ensure unique device ID exists
        if (getDeviceId().isEmpty()) {
            val generated = "android_" + UUID.randomUUID().toString().replace("-", "").take(16)
            prefs.edit().putString(KEY_DEVICE_ID, generated).apply()
        }
    }

    fun getServerUrl(): String {
        val saved = prefs.getString(KEY_SERVER_URL, null)
        // If no URL saved, or saved URL is an old local/tunnel URL, use permanent Render cloud server
        if (saved.isNullOrEmpty()
            || saved.contains("127.0.0.1")
            || saved.contains("10.0.2.2")
            || saved.contains("loca.lt")
            || saved.contains("trycloudflare.com")
            || saved.contains("ngrok-free.dev")
        ) {
            // PRIMARY = Permanent Render Cloud Server
            return "https://safe-vault-xx5c.onrender.com"
        }
        return saved
    }

    fun setServerUrl(url: String) {
        val clean = url.trim().removeSuffix("/")
        prefs.edit().putString(KEY_SERVER_URL, clean).apply()
    }

    fun getDeviceId(): String {
        return prefs.getString(KEY_DEVICE_ID, "") ?: ""
    }

    fun getDeviceName(): String {
        return prefs.getString(KEY_DEVICE_NAME, android.os.Build.MODEL ?: "Personal Android") ?: "Personal Android"
    }

    fun setDeviceName(name: String) {
        prefs.edit().putString(KEY_DEVICE_NAME, name.trim()).apply()
    }

    fun getAuthToken(): String? {
        return prefs.getString(KEY_AUTH_TOKEN, null)
    }

    fun setAuthToken(token: String?) {
        prefs.edit().putString(KEY_AUTH_TOKEN, token).apply()
    }

    fun getAdminKey(): String {
        return prefs.getString(KEY_ADMIN_KEY, "ChangeThisMasterKeyBeforeProductionSync123!") ?: "ChangeThisMasterKeyBeforeProductionSync123!"
    }

    fun setAdminKey(key: String) {
        prefs.edit().putString(KEY_ADMIN_KEY, key.trim()).apply()
    }

    fun isAutoSyncEnabled(): Boolean = true
    fun setAutoSyncEnabled(enabled: Boolean) = prefs.edit().putBoolean(KEY_AUTO_SYNC, true).apply()

    fun isWifiOnly(): Boolean = prefs.getBoolean(KEY_WIFI_ONLY, false)
    fun setWifiOnly(enabled: Boolean) = prefs.edit().putBoolean(KEY_WIFI_ONLY, enabled).apply()

    fun isChargingOnly(): Boolean = prefs.getBoolean(KEY_CHARGING_ONLY, false)
    fun setChargingOnly(enabled: Boolean) = prefs.edit().putBoolean(KEY_CHARGING_ONLY, enabled).apply()

    fun getLastSyncTimestamp(): Long = prefs.getLong(KEY_LAST_SYNC, 0L)
    fun setLastSyncTimestamp(ts: Long) = prefs.edit().putLong(KEY_LAST_SYNC, ts).apply()

    companion object {
        private const val KEY_SERVER_URL = "vault_server_url"
        private const val KEY_DEVICE_ID = "vault_device_id"
        private const val KEY_DEVICE_NAME = "vault_device_name"
        private const val KEY_AUTH_TOKEN = "vault_auth_token"
        private const val KEY_ADMIN_KEY = "vault_admin_key"
        private const val KEY_AUTO_SYNC = "vault_auto_sync"
        private const val KEY_WIFI_ONLY = "vault_wifi_only"
        private const val KEY_CHARGING_ONLY = "vault_charging_only"
        private const val KEY_LAST_SYNC = "vault_last_sync_timestamp"
    }
}
