package com.cyclecare.notifications;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import com.cyclecare.database.AppDatabase;
import com.cyclecare.database.entity.PeriodLogEntity;

import java.util.List;

public class MidnightCycleReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent != null && intent.hasExtra("reminder_title")) {
            String title = intent.getStringExtra("reminder_title");
            DiscreetNotificationManager manager = new DiscreetNotificationManager(context);
            manager.showReminderNotification("⏰ " + title, "Time for your scheduled reminder: " + title);
            return;
        }

        // Reschedule for next midnight
        CycleNotificationScheduler.scheduleMidnightAlarm(context);

        // Fetch user preferences
        SharedPreferences prefs = context.getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
        boolean enabled = prefs.getBoolean("midnight_notifications_enabled", true);
        if (!enabled) return;

        String lang = prefs.getString("app_language", "en");

        // Compute cycle day from local database in background thread
        new Thread(() -> {
            try {
                List<PeriodLogEntity> logs = AppDatabase.getInstance(context).periodLogDao().getAllPeriodLogsSync();
                int cycleDay = 14; // Default sensible fallback (Ovulation)
                if (logs != null && !logs.isEmpty()) {
                    PeriodLogEntity latest = logs.get(0);
                    if (latest.getStartDate() != null && !latest.getStartDate().isEmpty()) {
                        try {
                            java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.US);
                            java.util.Date parsedDate = sdf.parse(latest.getStartDate());
                            if (parsedDate != null) {
                                long startMs = parsedDate.getTime();
                                long nowMs = System.currentTimeMillis();
                                int diffDays = (int) ((nowMs - startMs) / (1000 * 60 * 60 * 24));
                                cycleDay = (diffDays % 28) + 1;
                            }
                        } catch (Exception ignored) {}
                    }
                }

                String title;
                String body;

                if (cycleDay == 14) {
                    if ("hi".equals(lang)) {
                        title = "🌸 ओव्यूलेशन विंडो शुरू हो गई है";
                        body = "आज आपका ओव्यूलेशन विंडो शुरू हो गया है। आराम करें और खूब पानी पिएं!";
                    } else if ("hinglish".equals(lang)) {
                        title = "🌸 Aapka Ovulation Window Start Ho Gaya Hai!";
                        body = "Aaj se peak ovulation window shuru ho gaya hai. Healthy rahein aur hydration maintain karein!";
                    } else {
                        title = "🌸 Ovulation Window Started!";
                        body = "Your peak ovulation window has started today. Track symptoms & stay hydrated!";
                    }
                } else if (cycleDay >= 26) {
                    if ("hi".equals(lang)) {
                        title = "🩸 पीरियड्स 2 दिन में आने वाले हैं";
                        body = "तैयारी का समय! अपने पैड्स और हीटिंग पैच तैयार रखें।";
                    } else if ("hinglish".equals(lang)) {
                        title = "🩸 Period Aane Wala Hai (2 Din Baaki)";
                        body = "Care kit prepare kar lijiye! Pads aur heat patch ready rakhein.";
                    } else {
                        title = "🩸 Period Approaching in ~2 Days";
                        body = "Preparation window active. Keep your pads, heat patch, and care kit ready!";
                    }
                } else if (cycleDay == 1) {
                    if ("hi".equals(lang)) {
                        title = "🌺 पीरियड का पहला दिन";
                        body = "साइकिल का पहला दिन। आराम करें, गर्म रहें और हीटिंग पैच का उपयोग करें।";
                    } else if ("hinglish".equals(lang)) {
                        title = "🌺 Period Day 1 Shuru Hua!";
                        body = "Aapke cycle ka pehla din hai. Proper rest karein aur warm water bag use karein ❤️";
                    } else {
                        title = "🌺 Period Day 1 Has Arrived";
                        body = "Cycle Day 1. Rest well, stay warm, and remember your heating patch!";
                    }
                } else {
                    if ("hi".equals(lang)) {
                        title = "✨ आज का साइकिल केयर टिप";
                        body = "साइकिल दिन " + cycleDay + "। पर्याप्त नींद लें और हल्का व्यायाम करें।";
                    } else if ("hinglish".equals(lang)) {
                        title = "✨ Cycle Care Update: Day " + cycleDay;
                        body = "Cycle Day " + cycleDay + " chal raha hai. Herbal tea piyein aur stress-free rahein!";
                    } else {
                        title = "✨ Cycle Care: Day " + cycleDay;
                        body = "Active cycle care window. Chamomile tea and good sleep help muscle comfort.";
                    }
                }

                DiscreetNotificationManager manager = new DiscreetNotificationManager(context);
                manager.showReminderNotification(title, body);

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }
}
