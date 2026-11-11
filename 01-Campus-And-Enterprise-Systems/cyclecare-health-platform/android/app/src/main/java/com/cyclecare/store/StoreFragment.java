package com.cyclecare.store;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.models.Product;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class StoreFragment extends Fragment {

    private RecyclerView rvProducts;
    private ProductAdapter adapter;
    private final List<Product> allProducts = new ArrayList<>();
    private final List<Product> displayedProducts = new ArrayList<>();
    private String currentCategoryFilter = "All";
    private String currentSearchQuery = "";

    private Button chipAll, chipPeriodCare, chipComfort, chipHygiene, chipCareKits, chipTeas, chipWellness;
    private List<Button> allChips = new ArrayList<>();

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_store, container, false);

        rvProducts = view.findViewById(R.id.rv_products);
        rvProducts.setLayoutManager(new GridLayoutManager(getContext(), 2));

        EditText etSearch = view.findViewById(R.id.et_store_search);
        chipAll = view.findViewById(R.id.chip_all);
        chipPeriodCare = view.findViewById(R.id.chip_period_care);
        chipComfort = view.findViewById(R.id.chip_comfort);
        chipHygiene = view.findViewById(R.id.chip_hygiene);
        chipCareKits = view.findViewById(R.id.chip_care_kits);
        chipTeas = view.findViewById(R.id.chip_teas);
        chipWellness = view.findViewById(R.id.chip_wellness);

        allChips.add(chipAll);
        allChips.add(chipPeriodCare);
        allChips.add(chipComfort);
        allChips.add(chipHygiene);
        allChips.add(chipCareKits);
        allChips.add(chipTeas);
        allChips.add(chipWellness);

        adapter = new ProductAdapter(getContext(), displayedProducts);
        adapter.setOnCartUpdatedListener(this::updateCartBadge);
        rvProducts.setAdapter(adapter);

        loadSampleProducts();
        applyFilter();

        // Fetch live catalog from server
        fetchLiveProducts();

        // Chip Clicks
        chipAll.setOnClickListener(v -> selectCategory("All", chipAll));
        chipPeriodCare.setOnClickListener(v -> selectCategory("Period Care", chipPeriodCare));
        chipComfort.setOnClickListener(v -> selectCategory("Comfort", chipComfort));
        chipHygiene.setOnClickListener(v -> selectCategory("Hygiene", chipHygiene));
        chipCareKits.setOnClickListener(v -> selectCategory("Care Kits", chipCareKits));
        chipTeas.setOnClickListener(v -> selectCategory("Teas", chipTeas));
        chipWellness.setOnClickListener(v -> selectCategory("Wellness", chipWellness));

        // Search TextWatcher
        etSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                currentSearchQuery = s.toString().trim().toLowerCase();
                applyFilter();
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        // Header Action Listeners
        View btnOrders = view.findViewById(R.id.btn_store_orders);
        if (btnOrders != null) {
            btnOrders.setOnClickListener(v -> {
                Intent intent = new Intent(getContext(), OrdersActivity.class);
                startActivity(intent);
            });
        }

        View btnCart = view.findViewById(R.id.btn_store_cart);
        if (btnCart != null) {
            btnCart.setOnClickListener(v -> {
                Intent intent = new Intent(getContext(), CartActivity.class);
                startActivity(intent);
            });
        }

        return view;
    }

    private void selectCategory(String category, Button selectedChip) {
        currentCategoryFilter = category;
        for (Button chip : allChips) {
            if (chip == null) continue;
            if (chip == selectedChip) {
                chip.setBackgroundResource(R.drawable.bg_m3_button);
                chip.setTextColor(getResources().getColor(R.color.textOnPrimary));
            } else {
                chip.setBackgroundResource(R.drawable.bg_neu_card_raised);
                chip.setTextColor(0xFF000000);
            }
        }
        applyFilter();
    }

    @Override
    public void onResume() {
        super.onResume();
        updateCartBadge();
    }

    private void updateCartBadge() {
        if (getView() == null || getContext() == null) return;
        TextView tvBadge = getView().findViewById(R.id.tv_store_cart_badge);
        if (tvBadge == null) return;

        ApiClient.getApiService(getContext()).getCart().enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object itemsObj = body.get("items");
                    if (itemsObj instanceof List) {
                        int count = ((List<?>) itemsObj).size();
                        if (count > 0) {
                            tvBadge.setVisibility(View.VISIBLE);
                            tvBadge.setText(String.valueOf(count));
                        } else {
                            tvBadge.setVisibility(View.GONE);
                        }
                    }
                }
            }
            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {}
        });
    }

    private void fetchLiveProducts() {
        if (getContext() == null) return;
        ApiClient.getApiService(getContext()).getProducts(null, null).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Map<String, Object> body = response.body();
                    Object productsObj = body.get("products");
                    if (productsObj != null) {
                        Gson gson = new Gson();
                        String json = gson.toJson(productsObj);
                        Type listType = new TypeToken<List<Product>>() {}.getType();
                        List<Product> fetched = gson.fromJson(json, listType);
                        if (fetched != null && !fetched.isEmpty()) {
                            allProducts.clear();
                            allProducts.addAll(fetched);
                            applyFilter();
                        }
                    }
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                // Keep sample products visible
            }
        });
    }

    private void loadSampleProducts() {
        allProducts.clear();
        allProducts.add(new Product("a1111111-1111-1111-1111-111111111111", "CycleCare Organic Cotton Pads (Night)", "Soft, ultra-absorbent organic cotton pads with heavy flow leak guards (10x)", 149, "Period Care", 100, "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("a2222222-2222-2222-2222-222222222222", "CycleCare Ultra-Thin Daily Pantyliners", "Breathable daily pantyliners for all-day fresh comfort (20x)", 99, "Period Care", 150, "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("b1111111-1111-1111-1111-111111111111", "Instant Warmth Heat Patch (Pack of 3)", "Air-activated heating patches soothing cramps for up to 8 hours", 199, "Comfort", 80, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("b2222222-2222-2222-2222-222222222222", "Soothing Electric Heating Water Bag", "Rechargeable electric hot water bag for abdominal & back relief", 399, "Comfort", 40, "https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("c1111111-1111-1111-1111-111111111111", "Gentle pH-Balanced Intimate Wipes", "Biodegradable wipes with soothing aloe vera and chamomile (15x)", 85, "Hygiene", 120, "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("d1111111-1111-1111-1111-111111111111", "CycleCare Period Comfort Dark Chocolate (70%)", "Rich Belgian dark chocolate infused with magnesium for cramp ease", 120, "Comfort", 200, "https://images.unsplash.com/photo-1549007994-cb92caebd54b?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("d2222222-2222-2222-2222-222222222222", "Chamomile & Ginger Soothing Herbal Tea", "Caffeine-free herbal blend relieving bloating & body tension (15 Bags)", 180, "Teas", 90, "https://images.unsplash.com/photo-1597481499750-3e6b22637e12?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("009f4b12-2efa-4e28-8c1a-4f872e955fb7", "CycleCare Herbal Cramp Relief Roll-On", "Ayurvedic botanical essential oils for fast abdominal cramp relief", 249, "Wellness", 65, "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("1f970168-18c4-4b4a-81bd-3aed6fcf3587", "CycleCare Magnesium Sleep & Cramp Gummies", "Berry flavored chewable gummies supporting muscle relaxation & deep sleep", 349, "Wellness", 55, "https://images.unsplash.com/photo-1577401239170-897942555fb3?auto=format&fit=crop&w=600&q=80"));
        allProducts.add(new Product("carekit-premium-01", "CycleCare Emergency Period & Cramp Care Kit", "Complete discreet emergency kit with pads, heating patch, wipes, & chamomile tea", 499, "Care Kits", 45, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80"));
    }

    private void applyFilter() {
        displayedProducts.clear();
        for (Product p : allProducts) {
            boolean matchesCat = currentCategoryFilter.equals("All");
            if (!matchesCat && p.getCategory() != null) {
                matchesCat = p.getCategory().toLowerCase().contains(currentCategoryFilter.toLowerCase())
                        || currentCategoryFilter.toLowerCase().contains(p.getCategory().toLowerCase());
            }

            boolean matchesSearch = currentSearchQuery.isEmpty();
            if (!matchesSearch) {
                String name = p.getName() != null ? p.getName().toLowerCase() : "";
                String desc = p.getDescription() != null ? p.getDescription().toLowerCase() : "";
                String cat = p.getCategory() != null ? p.getCategory().toLowerCase() : "";
                matchesSearch = name.contains(currentSearchQuery) || desc.contains(currentSearchQuery) || cat.contains(currentSearchQuery);
            }

            if (matchesCat && matchesSearch) {
                displayedProducts.add(p);
            }
        }
        if (adapter != null) {
            adapter.notifyDataSetChanged();
        }
    }
}
