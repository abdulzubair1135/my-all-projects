package com.cyclecare.utils;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.content.res.Resources;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

public class LocaleHelper {

    private static final String PREF_NAME = "cyclecare_prefs";
    private static final String KEY_LANGUAGE = "app_language";

    private static final Map<String, Map<String, String>> TRANSLATIONS = new HashMap<>();

    static {
        // English (default)
        Map<String, String> en = new HashMap<>();
        en.put("app_title", "CycleCare");
        en.put("home_greeting", "Welcome,");
        en.put("cycle_calendar", "Cycle Calendar");
        en.put("calendar_subtitle", "Track periods, ovulation and symptom predictions");
        en.put("store_title", "CycleCare Store");
        en.put("store_subtitle", "Care essentials & discreet comfort kits");
        en.put("reminders_title", "Cycle & Care Reminders");
        en.put("reminders_subtitle", "Automatic alerts every night at 12:00 AM Midnight");
        en.put("btn_add_reminder", "➕ Add Custom Reminder");
        en.put("circle_chat_btn", "💬 Chat with Husband / Circle (Request Care)");
        en.put("ovulation_phase", "Peak Ovulation Window");
        en.put("period_phase", "Period Phase");
        en.put("luteal_phase", "Luteal Phase");
        en.put("follicular_phase", "Follicular Phase");
        TRANSLATIONS.put("en", en);

        // Hindi
        Map<String, String> hi = new HashMap<>();
        hi.put("app_title", "साइकिल केयर");
        hi.put("home_greeting", "नमस्ते,");
        hi.put("cycle_calendar", "साइकिल कैलेंडर");
        hi.put("calendar_subtitle", "पीरियड्स, ओव्यूलेशन और लक्षणों का सटीक अनुमान");
        hi.put("store_title", "साइकिल केयर स्टोर");
        hi.put("store_subtitle", "सुरक्षित आवश्यक सामान और आराम किट");
        hi.put("reminders_title", "साइकिल और केयर रिमाइंडर्स");
        hi.put("reminders_subtitle", "हर रात 12:00 बजे स्वचालित नोटिफिकेशन अलर्ट");
        hi.put("btn_add_reminder", "➕ नया रिमाइंडर सेट करें");
        hi.put("circle_chat_btn", "💬 पार्टनर / परिवार से चैट करें (सामान मंगाएं)");
        hi.put("ovulation_phase", "ओव्यूलेशन और फर्टाइल विंडो");
        hi.put("period_phase", "पीरियड का समय");
        hi.put("luteal_phase", "ल्यूटियल फेज");
        hi.put("follicular_phase", "फॉलिक्युलर फेज");
        TRANSLATIONS.put("hi", hi);

        // Hinglish
        Map<String, String> hinglish = new HashMap<>();
        hinglish.put("app_title", "CycleCare");
        hinglish.put("home_greeting", "Namaste,");
        hinglish.put("cycle_calendar", "Cycle Calendar");
        hinglish.put("calendar_subtitle", "Period, ovulation aur health tracking ek jagah");
        hinglish.put("store_title", "CycleCare Store");
        hinglish.put("store_subtitle", "Care essentials aur discreet comfort kits");
        hinglish.put("reminders_title", "Cycle & Health Reminders");
        hinglish.put("reminders_subtitle", "Har raat 12:00 baje midnight automatic phase alerts");
        hinglish.put("btn_add_reminder", "➕ Naya Reminder Add Karein");
        hinglish.put("circle_chat_btn", "💬 Husband / Circle se Chat Karein (Saman Mangwayein)");
        hinglish.put("ovulation_phase", "Peak Ovulation Window Active");
        hinglish.put("period_phase", "Period Phase");
        hinglish.put("luteal_phase", "Luteal Phase (Rest Time)");
        hinglish.put("follicular_phase", "Follicular Phase (Active Energy)");
        TRANSLATIONS.put("hinglish", hinglish);
    }

    public static String getLanguage(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        return prefs.getString(KEY_LANGUAGE, "en");
    }

    public static void setLanguage(Context context, String lang) {
        SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        prefs.edit().putString(KEY_LANGUAGE, lang).apply();

        Locale locale = "hi".equals(lang) ? new Locale("hi") : Locale.ENGLISH;
        Locale.setDefault(locale);
        Resources resources = context.getResources();
        Configuration config = new Configuration(resources.getConfiguration());
        config.setLocale(locale);
        resources.updateConfiguration(config, resources.getDisplayMetrics());
    }

    public static Context applyLocale(Context context) {
        String lang = getLanguage(context);
        Locale locale = "hi".equals(lang) ? new Locale("hi") : Locale.ENGLISH;
        Locale.setDefault(locale);

        Resources resources = context.getResources();
        Configuration config = new Configuration(resources.getConfiguration());
        config.setLocale(locale);
        resources.updateConfiguration(config, resources.getDisplayMetrics());
        return context.createConfigurationContext(config);
    }

    public static String t(Context context, String key, String defaultVal) {
        String lang = getLanguage(context);
        Map<String, String> dict = TRANSLATIONS.get(lang);
        if (dict != null && dict.containsKey(key)) {
            return dict.get(key);
        }
        return defaultVal;
    }
}
