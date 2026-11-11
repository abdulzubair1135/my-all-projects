package com.example.lifevault.network

import com.example.lifevault.security.TokenStore
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

class ApiClient(private val tokenStore: TokenStore) {

    private var currentBaseUrl: String = ""
    private var cachedApi: VaultApi? = null

    @Synchronized
    fun getApi(): VaultApi {
        var url = tokenStore.getServerUrl().trim()
        if (!url.endsWith("/")) {
            url += "/"
        }

        if (cachedApi != null && currentBaseUrl == url) {
            return cachedApi!!
        }

        val authInterceptor = Interceptor { chain ->
            val original = chain.request()
            val builder = original.newBuilder()

            // Attach Bearer token if registered
            tokenStore.getAuthToken()?.let { token ->
                if (token.isNotEmpty()) {
                    builder.header("Authorization", "Bearer $token")
                }
            }

            builder.header("User-Agent", "LifeVault-Android/1.0")
            builder.header("Bypass-Tunnel-Reminder", "true")
            builder.header("bypass-tunnel-reminder", "1")
            builder.header("ngrok-skip-browser-warning", "true")
            chain.proceed(builder.build())
        }

        val failoverInterceptor = Interceptor { chain ->
            val request = chain.request()
            try {
                return@Interceptor chain.proceed(request)
            } catch (e: Exception) {
                // If primary URL fails, try fallbacks!
                val fallbacks = listOf(
                    "https://safe-vault-xx5c.onrender.com",               // Permanent Render Cloud Server
                    "https://illusion-roundish-configure.ngrok-free.dev", // Ngrok tunnel
                    "http://10.221.241.31:8088",                           // LAN fallback (same WiFi)
                    "http://127.0.0.1:8088"                                // USB ADB reverse tunnel fallback
                )
                for (fallbackBase in fallbacks) {
                    try {
                        val fallbackUri = fallbackBase.toHttpUrlOrNull() ?: continue
                        val newUrl = request.url.newBuilder()
                            .scheme(fallbackUri.scheme)
                            .host(fallbackUri.host)
                            .port(fallbackUri.port)
                            .build()
                        val newRequest = request.newBuilder().url(newUrl).build()
                        val response = chain.proceed(newRequest)
                        if (response.isSuccessful) {
                            tokenStore.setServerUrl(fallbackBase)
                            return@Interceptor response
                        }
                    } catch (_: Exception) {}
                }
                throw e
            }
        }

        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.HEADERS
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(failoverInterceptor)
            .addInterceptor(logging)
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.MINUTES)   // 60 min for 1GB+ file uploads
            .writeTimeout(60, TimeUnit.MINUTES)  // 60 min for 1GB+ file uploads
            .callTimeout(60, TimeUnit.MINUTES)   // overall call timeout
            .retryOnConnectionFailure(true)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(url)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        currentBaseUrl = url
        val api = retrofit.create(VaultApi::class.java)
        cachedApi = api
        return api
    }
}
