package com.cyclecare.api;

import android.content.Context;
import android.content.SharedPreferences;

import java.io.IOException;
import okhttp3.Interceptor;
import okhttp3.Request;
import okhttp3.Response;

public class AuthInterceptor implements Interceptor {
    private Context context;

    public AuthInterceptor(Context context) {
        this.context = context.getApplicationContext();
    }

    @Override
    public Response intercept(Chain chain) throws IOException {
        SharedPreferences prefs = context.getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
        String token = prefs.getString("jwt_token", null);

        Request.Builder builder = chain.request().newBuilder();
        if (token != null && !token.isEmpty()) {
            builder.addHeader("Authorization", "Bearer " + token);
        }

        return chain.proceed(builder.build());
    }
}
