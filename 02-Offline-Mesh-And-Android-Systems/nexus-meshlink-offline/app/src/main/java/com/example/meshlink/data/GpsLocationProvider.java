package com.example.meshlink.data;

import android.annotation.SuppressLint;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;

import androidx.annotation.NonNull;

public class GpsLocationProvider {

    public interface LocationCallback {
        void onLocationUpdated(double latitude, double longitude, float accuracy);
    }

    private final Context context;
    private final LocationManager locationManager;
    private LocationCallback callback;
    private Location lastLocation;

    private final LocationListener locationListener = new LocationListener() {
        @Override
        public void onLocationChanged(@NonNull Location location) {
            lastLocation = location;
            if (callback != null) {
                callback.onLocationUpdated(location.getLatitude(), location.getLongitude(), location.getAccuracy());
            }
        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {}

        @Override
        public void onProviderEnabled(@NonNull String provider) {}

        @Override
        public void onProviderDisabled(@NonNull String provider) {}
    };

    public GpsLocationProvider(Context context) {
        this.context = context;
        this.locationManager = (LocationManager) context.getSystemService(Context.LOCATION_SERVICE);
    }

    @SuppressLint("MissingPermission")
    public void startListening(LocationCallback callback) {
        this.callback = callback;
        try {
            if (locationManager != null) {
                if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                    locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 3000, 5, locationListener);
                }
                if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                    locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 3000, 5, locationListener);
                }
                Location gps = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
                Location net = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
                Location best = gps != null ? gps : net;
                if (best != null) {
                    lastLocation = best;
                    if (callback != null) {
                        callback.onLocationUpdated(best.getLatitude(), best.getLongitude(), best.getAccuracy());
                    }
                }
            }
        } catch (Exception ignored) {}
    }

    public void stopListening() {
        if (locationManager != null) {
            locationManager.removeUpdates(locationListener);
        }
    }

    public Location getLastLocation() {
        return lastLocation;
    }
}
