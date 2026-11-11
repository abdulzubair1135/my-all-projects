package com.cyclecare.home;

import android.animation.ObjectAnimator;
import android.animation.PropertyValuesHolder;
import android.animation.ValueAnimator;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.AccelerateDecelerateInterpolator;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.cyclecare.R;
import com.cyclecare.cycle.PeriodLogActivity;
import com.cyclecare.database.AppDatabase;
import com.cyclecare.database.entity.PeriodLogEntity;
import com.cyclecare.store.CartActivity;
import com.cyclecare.store.CheckoutActivity;
import com.cyclecare.wellness.AskAIAssistantActivity;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

public class HomeFragment extends Fragment {

    private Button btnQuickLog, btnPrepareNow, btnViewCareKit, btnEmergencyMode, btnAskAi;
    private TextView tvGreeting, tvDialDaysCount, tvDialStatusSub, tvDialPhaseTag, tvCycleDay;
    private TextView tvTempValue, tvChartSubtitle, tvBreakdownSubtitle;
    private TextView tvBreakdownPeriod, tvBreakdownFollicular, tvBreakdownOvulation, tvBreakdownLuteal;
    private TextView[] tvDaysOfWeek;
    private LinearLayout llDialCore;
    private FrameLayout btnToggleActive, btnToggleSymptoms, btnToggleOvulation, btnToggleInsights;
    private ObjectAnimator pulseAnimator;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_home, container, false);

        tvGreeting = view.findViewById(R.id.tv_greeting);
        tvDialDaysCount = view.findViewById(R.id.tv_dial_days_count);
        tvDialStatusSub = view.findViewById(R.id.tv_dial_status_sub);
        tvDialPhaseTag = view.findViewById(R.id.tv_dial_phase_tag);
        tvCycleDay = view.findViewById(R.id.tv_cycle_day);
        llDialCore = view.findViewById(R.id.ll_dial_core);

        tvTempValue = view.findViewById(R.id.tv_temp_value);
        tvChartSubtitle = view.findViewById(R.id.tv_chart_subtitle);
        tvBreakdownSubtitle = view.findViewById(R.id.tv_breakdown_subtitle);
        tvBreakdownPeriod = view.findViewById(R.id.tv_breakdown_period);
        tvBreakdownFollicular = view.findViewById(R.id.tv_breakdown_follicular);
        tvBreakdownOvulation = view.findViewById(R.id.tv_breakdown_ovulation);
        tvBreakdownLuteal = view.findViewById(R.id.tv_breakdown_luteal);

        tvDaysOfWeek = new TextView[]{
                view.findViewById(R.id.tv_day_sun),
                view.findViewById(R.id.tv_day_mon),
                view.findViewById(R.id.tv_day_tue),
                view.findViewById(R.id.tv_day_wed),
                view.findViewById(R.id.tv_day_thu),
                view.findViewById(R.id.tv_day_fri),
                view.findViewById(R.id.tv_day_sat)
        };
        updateDayOfWeekHighlight();

        btnToggleActive = view.findViewById(R.id.btn_toggle_active);
        btnToggleSymptoms = view.findViewById(R.id.btn_toggle_symptoms);
        btnToggleOvulation = view.findViewById(R.id.btn_toggle_ovulation);
        btnToggleInsights = view.findViewById(R.id.btn_toggle_insights);

        btnQuickLog = view.findViewById(R.id.btn_quick_log);
        btnPrepareNow = view.findViewById(R.id.btn_prepare_now);
        btnViewCareKit = view.findViewById(R.id.btn_view_care_kit);
        btnEmergencyMode = view.findViewById(R.id.btn_emergency_mode);
        btnAskAi = view.findViewById(R.id.btn_ask_ai);

        // Load greeting
        if (getActivity() != null) {
            SharedPreferences prefs = getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
            String userName = prefs.getString("user_name", "User");
            tvGreeting.setText("Welcome, " + userName);
        }

        // Start pulse animation on the thermostat cycle dial core
        startDialPulseAnimation();

        // 📊 Compute Real Cycle Estimation from Room Database
        computeRealCycleEstimation();

        // Dial Core Click Action
        llDialCore.setOnClickListener(v -> {
            v.animate().scaleX(0.94f).scaleY(0.94f).setDuration(100).withEndAction(() -> {
                v.animate().scaleX(1.0f).scaleY(1.0f).setDuration(120).start();
                startActivity(new Intent(getActivity(), PeriodLogActivity.class));
            }).start();
        });

        // Quick Row Toggles
        btnToggleActive.setOnClickListener(v -> startActivity(new Intent(getActivity(), PeriodLogActivity.class)));
        btnToggleSymptoms.setOnClickListener(v -> startActivity(new Intent(getActivity(), PeriodLogActivity.class)));
        btnToggleOvulation.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).selectNavigationTab(R.id.nav_calendar);
            }
        });
        btnToggleInsights.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).selectNavigationTab(R.id.nav_profile);
            }
        });

        btnQuickLog.setOnClickListener(v -> startActivity(new Intent(getActivity(), PeriodLogActivity.class)));

        btnPrepareNow.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).selectNavigationTab(R.id.nav_store);
            }
        });

        btnViewCareKit.setOnClickListener(v -> {
            Intent cartIntent = new Intent(getActivity(), CartActivity.class);
            startActivity(cartIntent);
        });

        btnEmergencyMode.setOnClickListener(v -> {
            if (getActivity() == null) return;
            SharedPreferences prefs = getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
            String emergencyPhone = prefs.getString("emergency_phone", "");
            String emergencyRel = prefs.getString("emergency_rel", "Husband");

            android.widget.LinearLayout layout = new android.widget.LinearLayout(getActivity());
            layout.setOrientation(android.widget.LinearLayout.VERTICAL);
            layout.setPadding(40, 30, 40, 20);

            TextView tvDesc = new TextView(getActivity());
            tvDesc.setText("🚨 CycleCare Emergency SOS Care Kit includes:\n• 4x Heavy Flow Overnight Organic Cotton Pads\n• 2x Air-Activated Heat Cramp Patches\n• 1x Soothing Chamomile Relief Tea Sachet\n• 1x Intimate Antiseptic Care Wipe\n• Fast 15-20 min priority dispatch to your address.");
            tvDesc.setTextColor(0xFF334155);
            tvDesc.setTextSize(13);
            tvDesc.setLineSpacing(4, 1.1f);
            layout.addView(tvDesc);

            androidx.appcompat.app.AlertDialog.Builder builder = new androidx.appcompat.app.AlertDialog.Builder(getActivity())
                    .setTitle("🚨 Emergency Care & SOS Dispatch")
                    .setView(layout)
                    .setPositiveButton("📦 Dispatch SOS Kit (₹149)", (dialog, which) -> {
                        Intent emergencyIntent = new Intent(getActivity(), CheckoutActivity.class);
                        emergencyIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_PRODUCT_ID, "a1111111-1111-1111-1111-111111111111");
                        emergencyIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_PRODUCT_NAME, "CycleCare Emergency SOS Kit");
                        emergencyIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_PRICE, 149.0);
                        emergencyIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_QTY, 1);
                        emergencyIntent.putExtra(CheckoutActivity.EXTRA_BUY_NOW_IMAGE, "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80");
                        startActivity(emergencyIntent);
                    });

            if (!emergencyPhone.isEmpty()) {
                builder.setNeutralButton("📞 Call " + emergencyRel + " (" + emergencyPhone + ")", (dialog, which) -> {
                    Intent callIntent = new Intent(Intent.ACTION_DIAL);
                    callIntent.setData(Uri.parse("tel:" + emergencyPhone));
                    startActivity(callIntent);
                });
            } else {
                builder.setNeutralButton("📞 Call Relative / Husband", (dialog, which) -> {
                    Toast.makeText(getContext(), "Set your emergency phone in Profile -> Emergency Phone", Toast.LENGTH_LONG).show();
                    if (getActivity() instanceof MainActivity) {
                        ((MainActivity) getActivity()).selectNavigationTab(R.id.nav_profile);
                    }
                });
            }

            builder.setNegativeButton("Cancel", null).show();
        });

        btnAskAi.setOnClickListener(v -> startActivity(new Intent(getActivity(), AskAIAssistantActivity.class)));

        View btnHomeChat = view.findViewById(R.id.btn_home_chat);
        if (btnHomeChat != null) {
            btnHomeChat.setOnClickListener(v -> {
                Intent chatIntent = new Intent(getActivity(), com.cyclecare.chat.CircleConversationsActivity.class);
                startActivity(chatIntent);
            });
        }

        View btnHomeProfile = view.findViewById(R.id.btn_home_profile);
        if (btnHomeProfile != null) {
            btnHomeProfile.setOnClickListener(v -> {
                if (getActivity() instanceof MainActivity) {
                    ((MainActivity) getActivity()).selectNavigationTab(R.id.nav_profile);
                }
            });
        }

        View btnHomeCircleChat = view.findViewById(R.id.btn_home_circle_chat);
        if (btnHomeCircleChat != null) {
            btnHomeCircleChat.setOnClickListener(v -> {
                // Smart auto-routing: check circle contacts for Husband, Father, BF, Mother
                com.cyclecare.api.ApiClient.getApiService(getContext()).getCircleContacts().enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
                    @Override
                    public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            Object contactsObj = response.body().get("contacts");
                            if (contactsObj instanceof java.util.List) {
                                java.util.List<?> list = (java.util.List<?>) contactsObj;
                                for (Object item : list) {
                                    if (item instanceof java.util.Map) {
                                        java.util.Map<?, ?> m = (java.util.Map<?, ?>) item;
                                        String rel = String.valueOf(m.get("relationship")).toLowerCase();
                                        if (rel.contains("husband") || rel.contains("partner") || rel.contains("father") || rel.contains("mom")) {
                                            Intent intent = new Intent(getActivity(), com.cyclecare.chat.CircleChatActivity.class);
                                            intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONNECTION_ID, String.valueOf(m.get("connection_id")));
                                            intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_CONTACT_NAME, String.valueOf(m.get("display_name")));
                                            intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_RELATIONSHIP, String.valueOf(m.get("relationship")));
                                            intent.putExtra(com.cyclecare.chat.CircleChatActivity.EXTRA_PARTNER_USER_ID, String.valueOf(m.get("user_id")));
                                            startActivity(intent);
                                            return;
                                        }
                                    }
                                }
                            }
                        }
                        // Fallback to conversation list
                        Intent chatIntent = new Intent(getActivity(), com.cyclecare.chat.CircleConversationsActivity.class);
                        startActivity(chatIntent);
                    }

                    @Override
                    public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {
                        Intent chatIntent = new Intent(getActivity(), com.cyclecare.chat.CircleConversationsActivity.class);
                        startActivity(chatIntent);
                    }
                });
            });
        }

        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        if (getActivity() != null) {
            SharedPreferences prefs = getActivity().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
            String userName = prefs.getString("user_name", "User");
            if (tvGreeting != null) tvGreeting.setText("Welcome, " + userName);
        }
        syncRemotePeriodLogs();
    }

    private void updateDayOfWeekHighlight() {
        if (tvDaysOfWeek == null || !isAdded()) return;
        java.util.Calendar cal = java.util.Calendar.getInstance();
        int dayOfWeek = cal.get(java.util.Calendar.DAY_OF_WEEK); // 1 = Sun, 2 = Mon, ... 7 = Sat
        for (int i = 0; i < 7; i++) {
            if (tvDaysOfWeek[i] != null) {
                if ((i + 1) == dayOfWeek) {
                    tvDaysOfWeek[i].setTextColor(getResources().getColor(R.color.colorPrimary));
                    tvDaysOfWeek[i].setTypeface(null, android.graphics.Typeface.BOLD);
                } else {
                    tvDaysOfWeek[i].setTextColor(getResources().getColor(R.color.textHint));
                    tvDaysOfWeek[i].setTypeface(null, android.graphics.Typeface.NORMAL);
                }
            }
        }
    }

    /**
     * Calculates real cycle progress and days remaining from the local database.
     */
    private void computeRealCycleEstimation() {
        if (getContext() == null) return;

        AppDatabase.getInstance(requireContext())
                .periodLogDao()
                .getAllPeriodLogs()
                .observe(getViewLifecycleOwner(), logs -> {
                    updateDayOfWeekHighlight();
                    int cycleLength = 28;

                    if (logs != null && !logs.isEmpty()) {
                        PeriodLogEntity latestLog = logs.get(0);
                        try {
                            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
                            Date startDate = sdf.parse(latestLog.getStartDate());
                            if (startDate != null) {
                                long diffMs = Math.abs(System.currentTimeMillis() - startDate.getTime());
                                long diffDays = TimeUnit.MILLISECONDS.toDays(diffMs);
                                int cycleDay = (int) (diffDays % cycleLength) + 1;
                                int daysRemaining = cycleLength - cycleDay;
                                if (daysRemaining <= 0) daysRemaining = 1;

                                String phase;
                                if (cycleDay <= 5) {
                                    phase = "Menstrual Phase";
                                    if (tvChartSubtitle != null) tvChartSubtitle.setText("Estrogen & Progesterone low • Day " + cycleDay + " flow rhythm");
                                    if (tvTempValue != null) tvTempValue.setText("36.4°C • Baseline Normal");
                                    if (tvBreakdownPeriod != null) tvBreakdownPeriod.setText("Period: 5 days (18%) • CURRENT ACTIVE");
                                    if (tvBreakdownFollicular != null) tvBreakdownFollicular.setText("Follicular: 6 days (22%)");
                                    if (tvBreakdownOvulation != null) tvBreakdownOvulation.setText("Ovulation: 5 days (18%)");
                                    if (tvBreakdownLuteal != null) tvBreakdownLuteal.setText("Luteal: 12 days (42%)");
                                } else if (cycleDay <= 11) {
                                    phase = "Follicular Phase";
                                    if (tvChartSubtitle != null) tvChartSubtitle.setText("Estrogen rising • Energy & follicle developing");
                                    if (tvTempValue != null) tvTempValue.setText("36.3°C • Pre-Ovulatory Normal");
                                    if (tvBreakdownPeriod != null) tvBreakdownPeriod.setText("Period: 5 days (18%)");
                                    if (tvBreakdownFollicular != null) tvBreakdownFollicular.setText("Follicular: 6 days (22%) • CURRENT ACTIVE");
                                    if (tvBreakdownOvulation != null) tvBreakdownOvulation.setText("Ovulation: 5 days (18%)");
                                    if (tvBreakdownLuteal != null) tvBreakdownLuteal.setText("Luteal: 12 days (42%)");
                                } else if (cycleDay <= 16) {
                                    phase = "Ovulation Window";
                                    if (tvChartSubtitle != null) tvChartSubtitle.setText("LH surge peak • High fertility & energy rhythm");
                                    if (tvTempValue != null) tvTempValue.setText("36.6°C • Slight Temp Dip & Rise");
                                    if (tvBreakdownPeriod != null) tvBreakdownPeriod.setText("Period: 5 days (18%)");
                                    if (tvBreakdownFollicular != null) tvBreakdownFollicular.setText("Follicular: 6 days (22%)");
                                    if (tvBreakdownOvulation != null) tvBreakdownOvulation.setText("Ovulation: 5 days (18%) • CURRENT ACTIVE");
                                    if (tvBreakdownLuteal != null) tvBreakdownLuteal.setText("Luteal: 12 days (42%)");
                                } else {
                                    phase = "Luteal Phase";
                                    if (tvChartSubtitle != null) tvChartSubtitle.setText("Progesterone elevated • Body temperature peaking");
                                    if (tvTempValue != null) tvTempValue.setText("36.9°C • Luteal Elevated Normal");
                                    if (tvBreakdownPeriod != null) tvBreakdownPeriod.setText("Period: 5 days (18%)");
                                    if (tvBreakdownFollicular != null) tvBreakdownFollicular.setText("Follicular: 6 days (22%)");
                                    if (tvBreakdownOvulation != null) tvBreakdownOvulation.setText("Ovulation: 5 days (18%)");
                                    if (tvBreakdownLuteal != null) tvBreakdownLuteal.setText("Luteal: 12 days (42%) • CURRENT ACTIVE");
                                }

                                int percent = (int) (((float) cycleDay / cycleLength) * 100);
                                tvDialDaysCount.setText(String.valueOf(daysRemaining));
                                tvDialStatusSub.setText("days left");
                                tvDialPhaseTag.setText(phase);
                                tvCycleDay.setText("Day " + cycleDay + " of " + cycleLength + " (" + percent + "%)");
                                return;
                            }
                        } catch (Exception ignored) {
                        }
                    }

                    // Empty State: No logs recorded yet
                    tvDialDaysCount.setText("+");
                    tvDialStatusSub.setText("Log Period");
                    tvDialPhaseTag.setText("No Logs Recorded");
                    tvCycleDay.setText("Tap dial to log your cycle start date");
                    if (tvChartSubtitle != null) tvChartSubtitle.setText("Log your period to view active hormone curve");
                    if (tvTempValue != null) tvTempValue.setText("-- • Awaiting Period Log");
                    if (tvBreakdownPeriod != null) tvBreakdownPeriod.setText("Period: 5 days (18%)");
                    if (tvBreakdownFollicular != null) tvBreakdownFollicular.setText("Follicular: 6 days (22%)");
                    if (tvBreakdownOvulation != null) tvBreakdownOvulation.setText("Ovulation: 5 days (18%)");
                    if (tvBreakdownLuteal != null) tvBreakdownLuteal.setText("Luteal: 12 days (42%)");
                });
    }

    private void syncRemotePeriodLogs() {
        if (getContext() == null) return;
        com.cyclecare.api.ApiClient.getApiService(getContext()).getCycleData().enqueue(new retrofit2.Callback<java.util.Map<String, Object>>() {
            @Override
            public void onResponse(retrofit2.Call<java.util.Map<String, Object>> call, retrofit2.Response<java.util.Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Object pLogs = response.body().get("periodLogs");
                    if (pLogs instanceof java.util.List && !((java.util.List<?>) pLogs).isEmpty()) {
                        java.util.concurrent.Executors.newSingleThreadExecutor().execute(() -> {
                            try {
                                com.google.gson.Gson gson = new com.google.gson.Gson();
                                String json = gson.toJson(pLogs);
                                java.lang.reflect.Type listType = new com.google.gson.reflect.TypeToken<java.util.List<com.cyclecare.models.PeriodLog>>() {}.getType();
                                java.util.List<com.cyclecare.models.PeriodLog> list = gson.fromJson(json, listType);
                                if (list != null && getContext() != null) {
                                    for (com.cyclecare.models.PeriodLog pl : list) {
                                        String id = pl.getId() != null ? pl.getId() : java.util.UUID.randomUUID().toString();
                                        PeriodLogEntity entity = new PeriodLogEntity(id, pl.getStartDate(), pl.getEndDate(), pl.getFlow(), pl.getNotes(), true);
                                        AppDatabase.getInstance(requireContext()).periodLogDao().insertPeriodLog(entity);
                                    }
                                }
                            } catch (Exception ignored) {}
                        });
                    }
                }
            }

            @Override
            public void onFailure(retrofit2.Call<java.util.Map<String, Object>> call, Throwable t) {}
        });
    }

    private void startDialPulseAnimation() {
        if (llDialCore != null) {
            PropertyValuesHolder scaleX = PropertyValuesHolder.ofFloat(View.SCALE_X, 1.0f, 1.035f, 1.0f);
            PropertyValuesHolder scaleY = PropertyValuesHolder.ofFloat(View.SCALE_Y, 1.0f, 1.035f, 1.0f);
            pulseAnimator = ObjectAnimator.ofPropertyValuesHolder(llDialCore, scaleX, scaleY);
            pulseAnimator.setDuration(2200);
            pulseAnimator.setRepeatCount(ValueAnimator.INFINITE);
            pulseAnimator.setRepeatMode(ValueAnimator.RESTART);
            pulseAnimator.setInterpolator(new AccelerateDecelerateInterpolator());
            pulseAnimator.start();
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        if (pulseAnimator != null) {
            pulseAnimator.cancel();
        }
    }
}
