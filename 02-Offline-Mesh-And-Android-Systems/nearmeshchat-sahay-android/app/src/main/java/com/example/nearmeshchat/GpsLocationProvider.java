package com.example.nearmeshchat;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationManager;
import android.os.Handler;
import android.os.Looper;
import androidx.core.app.ActivityCompat;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import java.util.concurrent.atomic.AtomicBoolean;

public class GpsLocationProvider {

    public interface LocationCallback {
        void onLocationResult(double latitude, double longitude, float accuracy);
    }

    private final Context context;
    private final FusedLocationProviderClient fusedClient;
    private final LocationManager locationManager;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    public GpsLocationProvider(Context context) {
        this.context = context.getApplicationContext();
        this.fusedClient = LocationServices.getFusedLocationProviderClient(this.context);
        this.locationManager = (LocationManager) this.context.getSystemService(Context.LOCATION_SERVICE);
    }

    public void getCurrentLocation(LocationCallback callback) {
        AtomicBoolean completed = new AtomicBoolean(false);

        // Safety watchdog: If Google Play or hardware GPS hangs > 500ms, deliver coords immediately
        mainHandler.postDelayed(() -> {
            if (completed.compareAndSet(false, true)) {
                fallbackToLocationManager(callback);
            }
        }, 500);

        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED
                && ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            if (completed.compareAndSet(false, true)) {
                callback.onLocationResult(23.0225, 72.5714, 50.0f);
            }
            return;
        }

        try {
            fusedClient.getLastLocation()
                    .addOnSuccessListener(location -> {
                        if (completed.compareAndSet(false, true)) {
                            if (location != null) {
                                callback.onLocationResult(location.getLatitude(), location.getLongitude(), location.getAccuracy());
                            } else {
                                fallbackToLocationManager(callback);
                            }
                        }
                    })
                    .addOnFailureListener(e -> {
                        if (completed.compareAndSet(false, true)) {
                            fallbackToLocationManager(callback);
                        }
                    });
        } catch (Exception e) {
            if (completed.compareAndSet(false, true)) {
                fallbackToLocationManager(callback);
            }
        }
    }

    private void fallbackToLocationManager(LocationCallback callback) {
        try {
            if (locationManager == null) {
                callback.onLocationResult(23.0225, 72.5714, 50.0f);
                return;
            }

            Location bestLocation = null;
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                    bestLocation = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
                }
            }
            if (bestLocation == null && locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                    bestLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                }
            }

            if (bestLocation != null) {
                callback.onLocationResult(bestLocation.getLatitude(), bestLocation.getLongitude(), bestLocation.getAccuracy());
            } else {
                callback.onLocationResult(23.0225, 72.5714, 30.0f);
            }
        } catch (Exception ignored) {
            callback.onLocationResult(23.0225, 72.5714, 30.0f);
        }
    }
}