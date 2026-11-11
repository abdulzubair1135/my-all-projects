package com.cyclecare.partner;

import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapView;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.Polyline;
import com.google.android.gms.maps.model.PolylineOptions;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class OrderTrackingActivity extends AppCompatActivity implements OnMapReadyCallback {

    private static final String MAPVIEW_BUNDLE_KEY = "MapViewBundleKey";

    private TextView tvOrderTitle;
    private TextView tvEtaBadge;
    private TextView tvOtpDisplay;
    private TextView tvStatusStep3;
    private TextView tvStatusStep4;
    private TextView tvStatusStep5;
    private TextView tvMapDistanceEta;
    private MapView mapView;
    private GoogleMap googleMap;
    private Marker courierMarker;
    private Marker destinationMarker;
    private Polyline routePolyline;

    private ApiService apiService;
    private Handler handler;
    private int animationStep = 0;

    // Delivery path points (e.g. urban route)
    private final List<LatLng> routePoints = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_order_tracking);

        apiService = ApiClient.getApiService(this);
        handler = new Handler(Looper.getMainLooper());

        tvOrderTitle = findViewById(R.id.tv_order_title);
        tvEtaBadge = findViewById(R.id.tv_eta_badge);
        tvOtpDisplay = findViewById(R.id.tv_otp_display);
        tvStatusStep3 = findViewById(R.id.tv_status_step3);
        tvStatusStep4 = findViewById(R.id.tv_status_step4);
        tvStatusStep5 = findViewById(R.id.tv_status_step5);
        tvMapDistanceEta = findViewById(R.id.tv_map_distance_eta);
        mapView = findViewById(R.id.map_view);

        // Initialize realistic delivery route coordinates (Connaught Place to Destination)
        routePoints.add(new LatLng(28.6328, 77.2197)); // Start: Hub / Store
        routePoints.add(new LatLng(28.6315, 77.2215));
        routePoints.add(new LatLng(28.6290, 77.2230));
        routePoints.add(new LatLng(28.6265, 77.2245));
        routePoints.add(new LatLng(28.6240, 77.2260));
        routePoints.add(new LatLng(28.6215, 77.2272)); // Destination: Customer Home

        // MapView lifecycle
        Bundle mapViewBundle = null;
        if (savedInstanceState != null) {
            mapViewBundle = savedInstanceState.getBundle(MAPVIEW_BUNDLE_KEY);
        }
        if (mapView != null) {
            mapView.onCreate(mapViewBundle);
            mapView.getMapAsync(this);
        }

        fetchOrderTracking();
        startPeriodicUpdates();
    }

    @Override
    public void onMapReady(@NonNull GoogleMap map) {
        this.googleMap = map;
        try {
            googleMap.getUiSettings().setZoomControlsEnabled(true);
            googleMap.getUiSettings().setCompassEnabled(true);
            googleMap.getUiSettings().setMyLocationButtonEnabled(false);

            // Customer Destination Marker
            LatLng dest = routePoints.get(routePoints.size() - 1);
            destinationMarker = googleMap.addMarker(new MarkerOptions()
                    .position(dest)
                    .title("Customer Delivery Address")
                    .snippet("Tamper-evident CycleCare parcel")
                    .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_ROSE)));

            // Courier Marker
            LatLng initialCourier = routePoints.get(0);
            courierMarker = googleMap.addMarker(new MarkerOptions()
                    .position(initialCourier)
                    .title("CycleCare Courier")
                    .snippet("Arriving soon • Verified Agent")
                    .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE)));

            // Route Polyline
            PolylineOptions polylineOptions = new PolylineOptions()
                    .addAll(routePoints)
                    .color(Color.parseColor("#E91E63"))
                    .width(10f);
            routePolyline = googleMap.addPolyline(polylineOptions);

            // Fit bounds with padding
            LatLngBounds.Builder builder = new LatLngBounds.Builder();
            for (LatLng p : routePoints) {
                builder.include(p);
            }
            LatLngBounds bounds = builder.build();
            googleMap.moveCamera(CameraUpdateFactory.newLatLngBounds(bounds, 120));
        } catch (Exception e) {
            // Map fallback
        }
    }

    private void fetchOrderTracking() {
        String orderId = getIntent().getStringExtra("order_id");
        if (orderId == null || orderId.isEmpty()) {
            orderId = "cc-demo-1001";
        }

        apiService.getOrderTracking(orderId).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    if (body.containsKey("order")) {
                        Map<String, Object> order = (Map<String, Object>) body.get("order");
                        if (order.containsKey("order_number")) {
                            tvOrderTitle.setText("Order " + order.get("order_number"));
                        }
                        if (order.containsKey("delivery_otp")) {
                            String otp = String.valueOf(order.get("delivery_otp"));
                            tvOtpDisplay.setText(otp.replace("", " ").trim());
                        }
                    }
                    if (body.containsKey("delivery")) {
                        Map<String, Object> del = (Map<String, Object>) body.get("delivery");
                        String status = String.valueOf(del.get("status"));
                        applyDeliveryStatus(status);
                    }
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                // Keep default simulated fallback state
            }
        });
    }

    private void applyDeliveryStatus(String status) {
        if ("ARRIVED".equalsIgnoreCase(status)) {
            tvEtaBadge.setText("Arrived at Door");
            tvStatusStep4.setText("Arrived");
            tvStatusStep4.setTextColor(Color.parseColor("#D97706"));
            if (tvMapDistanceEta != null) {
                tvMapDistanceEta.setText("Arrived • Share OTP 4821");
            }
        } else if ("DELIVERED".equalsIgnoreCase(status)) {
            tvEtaBadge.setText("Delivered");
            tvStatusStep5.setText("Delivered");
            tvStatusStep5.setTextColor(Color.parseColor("#16A34A"));
            if (tvMapDistanceEta != null) {
                tvMapDistanceEta.setText("Delivered successfully");
            }
        } else {
            tvEtaBadge.setText("ETA: 12–18 min");
            tvStatusStep3.setText("In Transit");
        }
    }

    private void startPeriodicUpdates() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                animationStep = (animationStep + 1) % routePoints.size();
                LatLng currentPos = routePoints.get(animationStep);

                if (courierMarker != null) {
                    courierMarker.setPosition(currentPos);
                }

                if (googleMap != null && animationStep == 0) {
                    googleMap.animateCamera(CameraUpdateFactory.newLatLng(currentPos));
                }

                if (tvMapDistanceEta != null) {
                    int remainingPoints = routePoints.size() - 1 - animationStep;
                    if (remainingPoints <= 0) {
                        tvMapDistanceEta.setText("Arriving right now • 50 m");
                        tvEtaBadge.setText("Arriving Now");
                    } else {
                        double kmRemaining = Math.max(0.2, remainingPoints * 0.35);
                        int minsRemaining = Math.max(2, remainingPoints * 3);
                        tvMapDistanceEta.setText(String.format("🚴 %.1f km away • %d mins", kmRemaining, minsRemaining));
                        tvEtaBadge.setText(String.format("ETA: %d min", minsRemaining));
                    }
                }

                handler.postDelayed(this, 3500);
            }
        }, 1500);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (mapView != null) mapView.onResume();
    }

    @Override
    protected void onStart() {
        super.onStart();
        if (mapView != null) mapView.onStart();
    }

    @Override
    protected void onStop() {
        super.onStop();
        if (mapView != null) mapView.onStop();
    }

    @Override
    protected void onPause() {
        if (mapView != null) mapView.onPause();
        super.onPause();
    }

    @Override
    protected void onDestroy() {
        if (mapView != null) mapView.onDestroy();
        if (handler != null) {
            handler.removeCallbacksAndMessages(null);
        }
        super.onDestroy();
    }

    @Override
    public void onLowMemory() {
        super.onLowMemory();
        if (mapView != null) mapView.onLowMemory();
    }

    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        Bundle mapViewBundle = outState.getBundle(MAPVIEW_BUNDLE_KEY);
        if (mapViewBundle == null) {
            mapViewBundle = new Bundle();
            outState.putBundle(MAPVIEW_BUNDLE_KEY, mapViewBundle);
        }
        if (mapView != null) {
            mapView.onSaveInstanceState(mapViewBundle);
        }
    }
}
