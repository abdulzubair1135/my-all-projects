package com.projectflow.android.data.remote;

import android.content.Context;
import android.content.SharedPreferences;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.util.concurrent.TimeUnit;

public class ApiClient {
    private static volatile ApiService INSTANCE;
    private static final String PREF_NAME = "projectflow_prefs";
    private static final String KEY_BASE_URL = "api_base_url";
    private static final String KEY_TOKEN = "auth_token";
    // Live Public Production Cloud URL hosted on Render
    // Primary & Fallback Endpoints
    public static final String LOCAL_URL = "http://127.0.0.1:8082/api/v1/";
    public static final String WIFI_URL = "http://10.17.158.31:8082/api/v1/";
    public static final String CLOUD_URL = "https://projectflow-intelligence.onrender.com/api/v1/";
    public static final String DEFAULT_URL = LOCAL_URL;

    public static ApiService getService(Context context) {
        if (INSTANCE == null) {
            synchronized (ApiClient.class) {
                if (INSTANCE == null) {
                    INSTANCE = createService(context.getApplicationContext());
                }
            }
        }
        return INSTANCE;
    }

    public static void resetService() {
        INSTANCE = null;
    }

    private static ApiService createService(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        String baseUrl = prefs.getString(KEY_BASE_URL, DEFAULT_URL);
        if (baseUrl == null || baseUrl.isEmpty() || baseUrl.contains("trycloudflare.com")) {
            baseUrl = DEFAULT_URL;
            prefs.edit().putString(KEY_BASE_URL, DEFAULT_URL).apply();
        }
        if (!baseUrl.endsWith("/")) {
            baseUrl += "/";
        }

        HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
        logging.setLevel(HttpLoggingInterceptor.Level.BODY);

        Interceptor authInterceptor = chain -> {
            Request original = chain.request();
            String token = prefs.getString(KEY_TOKEN, "dev-admin-token");
            String email = prefs.getString("user_email", "admin@projectflow.io");
            String role = prefs.getString("user_role", "MEMBER");
            String userId = prefs.getString("user_id", "");
            Request.Builder builder = original.newBuilder()
                    .header("Authorization", "Bearer " + token)
                    .header("x-user-email", email)
                    .header("x-user-role", role)
                    .header("x-user-id", userId)
                    .header("x-client-platform", "android")
                    .header("Accept", "application/json");
            return chain.proceed(builder.build());
        };

        Interceptor fallbackInterceptor = chain -> {
            Request request = chain.request();
            try {
                okhttp3.Response response = chain.proceed(request);
                if (response.isSuccessful() || response.code() < 500) {
                    return response;
                }
                response.close();
            } catch (java.io.IOException ignored) {}

            okhttp3.HttpUrl originalUrl = request.url();
            String host = originalUrl.host();

            String[] candidates = new String[] { "127.0.0.1", "10.17.158.31", "projectflow-intelligence.onrender.com" };
            for (String targetHost : candidates) {
                if (targetHost.equalsIgnoreCase(host)) continue;
                try {
                    okhttp3.HttpUrl.Builder b = originalUrl.newBuilder().host(targetHost);
                    if (targetHost.contains("onrender.com")) {
                        b.scheme("https").port(443);
                    } else {
                        b.scheme("http").port(8082);
                    }
                    okhttp3.Response fbResponse = chain.proceed(request.newBuilder().url(b.build()).build());
                    if (fbResponse.isSuccessful() || fbResponse.code() < 500) {
                        return fbResponse;
                    }
                    fbResponse.close();
                } catch (java.io.IOException ignored) {}
            }

            return chain.proceed(request);
        };

        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(4, TimeUnit.SECONDS)
                .readTimeout(8, TimeUnit.SECONDS)
                .writeTimeout(8, TimeUnit.SECONDS)
                .retryOnConnectionFailure(true)
                .addInterceptor(fallbackInterceptor)
                .addInterceptor(authInterceptor)
                .addInterceptor(logging)
                .build();

        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        return retrofit.create(ApiService.class);
    }
}
