package com.cyclecare.cycle;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CalendarView;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.widget.SwitchCompat;
import androidx.fragment.app.Fragment;

import com.cyclecare.R;
import com.cyclecare.notifications.CycleNotificationScheduler;
import com.cyclecare.utils.LocaleHelper;
import com.google.android.material.bottomsheet.BottomSheetDialog;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

public class CalendarFragment extends Fragment {

    private CalendarView calendarView;
    private TextView tvCalendarHeaderTitle, tvCalendarHeaderSubtitle;
    private TextView tvSelectedDate, tvPhaseBadge, tvDateStatus, tvLoggedNotes;
    private Button btnLogForDate, btnAddReminder;
    private SwitchCompat swRemOvulation, swRemPeriod, swRemPill, swRemHydration;
    private SharedPreferences prefs;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_calendar, container, false);

        if (getContext() != null) {
            prefs = getContext().getSharedPreferences("cyclecare_prefs", Context.MODE_PRIVATE);
        }

        calendarView = view.findViewById(R.id.calendar_view);
        tvCalendarHeaderTitle = view.findViewById(R.id.tv_calendar_header_title);
        tvCalendarHeaderSubtitle = view.findViewById(R.id.tv_calendar_header_subtitle);
        tvSelectedDate = view.findViewById(R.id.tv_selected_date);
        tvPhaseBadge = view.findViewById(R.id.tv_phase_badge);
        tvDateStatus = view.findViewById(R.id.tv_date_status);
        tvLoggedNotes = view.findViewById(R.id.tv_logged_notes);
        btnLogForDate = view.findViewById(R.id.btn_log_for_date);
        btnAddReminder = view.findViewById(R.id.btn_add_reminder);

        swRemOvulation = view.findViewById(R.id.sw_rem_ovulation);
        swRemPeriod = view.findViewById(R.id.sw_rem_period);
        swRemPill = view.findViewById(R.id.sw_rem_pill);
        swRemHydration = view.findViewById(R.id.sw_rem_hydration);

        applyLocalization();
        setupCalendarView();
        setupReminders();

        btnLogForDate.setOnClickListener(v -> {
            Intent intent = new Intent(getActivity(), PeriodLogActivity.class);
            startActivity(intent);
        });

        btnAddReminder.setOnClickListener(v -> showAddReminderDialog());

        return view;
    }

    private void applyLocalization() {
        if (getContext() == null) return;
        tvCalendarHeaderTitle.setText(LocaleHelper.t(getContext(), "cycle_calendar", "Cycle Calendar"));
        tvCalendarHeaderSubtitle.setText(LocaleHelper.t(getContext(), "calendar_subtitle", "Track periods, ovulation and symptom predictions"));
    }

    private void setupCalendarView() {
        Calendar today = Calendar.getInstance();
        SimpleDateFormat sdf = new SimpleDateFormat("EEEE, MMM dd, yyyy", Locale.getDefault());
        tvSelectedDate.setText(sdf.format(today.getTime()));

        calendarView.setOnDateChangeListener((view1, year, month, dayOfMonth) -> {
            Calendar sel = Calendar.getInstance();
            sel.set(year, month, dayOfMonth);
            String formattedDate = sdf.format(sel.getTime());
            tvSelectedDate.setText(formattedDate);

            // Dynamic phase calculation simulation based on day of month
            int dayMod = dayOfMonth % 28;
            if (dayMod >= 1 && dayMod <= 5) {
                tvPhaseBadge.setText("Period Phase");
                tvPhaseBadge.setBackgroundResource(R.drawable.bg_badge_period);
                tvPhaseBadge.setTextColor(getResources().getColor(R.color.colorPrimary));
                tvDateStatus.setText("Cycle Day " + dayMod + " • Heavy Flow Window");
                tvLoggedNotes.setText("Period active. Logged symptoms: Moderate cramps, low energy.");
            } else if (dayMod >= 12 && dayMod <= 16) {
                tvPhaseBadge.setText("Fertile Window");
                tvPhaseBadge.setBackgroundResource(R.drawable.bg_badge_ovulation);
                tvPhaseBadge.setTextColor(getResources().getColor(R.color.colorSkyBlueDark));
                tvDateStatus.setText("Cycle Day " + dayMod + " • Peak Ovulation Window");
                tvLoggedNotes.setText("High fertility window. Peak energy & calm mood.");
            } else {
                tvPhaseBadge.setText("Follicular / Luteal");
                tvPhaseBadge.setBackgroundResource(R.drawable.bg_badge_today);
                tvPhaseBadge.setTextColor(getResources().getColor(R.color.textSecondary));
                tvDateStatus.setText("Cycle Day " + (dayMod == 0 ? 28 : dayMod) + " • Regular Phase");
                tvLoggedNotes.setText("No severe symptoms recorded for this date.");
            }
        });
    }

    private void setupReminders() {
        if (prefs == null) return;

        swRemOvulation.setChecked(prefs.getBoolean("rem_ovulation_enabled", true));
        swRemPeriod.setChecked(prefs.getBoolean("rem_period_enabled", true));
        swRemPill.setChecked(prefs.getBoolean("rem_pill_enabled", true));
        swRemHydration.setChecked(prefs.getBoolean("rem_hydration_enabled", true));

        swRemOvulation.setOnCheckedChangeListener((btn, isChecked) -> {
            prefs.edit().putBoolean("rem_ovulation_enabled", isChecked).apply();
            if (isChecked && getContext() != null) {
                CycleNotificationScheduler.scheduleMidnightAlarm(getContext());
                Toast.makeText(getContext(), "✓ 12:00 AM Ovulation Alert Enabled", Toast.LENGTH_SHORT).show();
            }
        });

        swRemPeriod.setOnCheckedChangeListener((btn, isChecked) -> {
            prefs.edit().putBoolean("rem_period_enabled", isChecked).apply();
            if (isChecked && getContext() != null) {
                CycleNotificationScheduler.scheduleMidnightAlarm(getContext());
                Toast.makeText(getContext(), "✓ 12:00 AM Period Warning Enabled", Toast.LENGTH_SHORT).show();
            }
        });

        swRemPill.setOnCheckedChangeListener((btn, isChecked) -> {
            prefs.edit().putBoolean("rem_pill_enabled", isChecked).apply();
            Toast.makeText(getContext(), isChecked ? "✓ Evening 9:00 PM Supplement Reminder Set" : "Supplement Reminder Off", Toast.LENGTH_SHORT).show();
        });

        swRemHydration.setOnCheckedChangeListener((btn, isChecked) -> {
            prefs.edit().putBoolean("rem_hydration_enabled", isChecked).apply();
            Toast.makeText(getContext(), isChecked ? "✓ Afternoon 4:00 PM Hydration Alert Set" : "Hydration Alert Off", Toast.LENGTH_SHORT).show();
        });
    }

    private void showAddReminderDialog() {
        if (getContext() == null) return;

        BottomSheetDialog dialog = new BottomSheetDialog(getContext());
        View sheet = getLayoutInflater().inflate(R.layout.dialog_add_reminder, null);
        dialog.setContentView(sheet);

        EditText etTitle = sheet.findViewById(R.id.et_reminder_title);
        Button btnMidnight = sheet.findViewById(R.id.btn_time_midnight);
        Button btnMorning = sheet.findViewById(R.id.btn_time_morning);
        Button btnNight = sheet.findViewById(R.id.btn_time_night);
        Button btnCustom = sheet.findViewById(R.id.btn_time_custom);
        Button btnSave = sheet.findViewById(R.id.btn_save_reminder);

        final String[] selectedTime = {"12:00 AM Midnight"};
        final int[] selectedHour = {0};
        final int[] selectedMin = {0};

        int primaryColor = getResources().getColor(R.color.textPrimary);
        int onPrimaryColor = getResources().getColor(R.color.textOnPrimary);

        btnMidnight.setOnClickListener(v -> {
            selectedTime[0] = "12:00 AM Midnight";
            selectedHour[0] = 0;
            selectedMin[0] = 0;
            btnMidnight.setBackgroundResource(R.drawable.bg_m3_button);
            btnMidnight.setTextColor(onPrimaryColor);
            btnMorning.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnMorning.setTextColor(primaryColor);
            btnNight.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnNight.setTextColor(primaryColor);
            if (btnCustom != null) {
                btnCustom.setBackgroundResource(R.drawable.bg_neu_card_raised);
                btnCustom.setTextColor(getResources().getColor(R.color.colorPrimary));
                btnCustom.setText("⏰ Choose Custom Time (Pick Any Time)");
            }
        });

        btnMorning.setOnClickListener(v -> {
            selectedTime[0] = "9:00 AM Morning";
            selectedHour[0] = 9;
            selectedMin[0] = 0;
            btnMorning.setBackgroundResource(R.drawable.bg_m3_button);
            btnMorning.setTextColor(onPrimaryColor);
            btnMidnight.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnMidnight.setTextColor(primaryColor);
            btnNight.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnNight.setTextColor(primaryColor);
            if (btnCustom != null) {
                btnCustom.setBackgroundResource(R.drawable.bg_neu_card_raised);
                btnCustom.setTextColor(getResources().getColor(R.color.colorPrimary));
                btnCustom.setText("⏰ Choose Custom Time (Pick Any Time)");
            }
        });

        btnNight.setOnClickListener(v -> {
            selectedTime[0] = "9:00 PM Evening";
            selectedHour[0] = 21;
            selectedMin[0] = 0;
            btnNight.setBackgroundResource(R.drawable.bg_m3_button);
            btnNight.setTextColor(onPrimaryColor);
            btnMidnight.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnMidnight.setTextColor(primaryColor);
            btnMorning.setBackgroundResource(R.drawable.bg_neu_card_raised);
            btnMorning.setTextColor(primaryColor);
            if (btnCustom != null) {
                btnCustom.setBackgroundResource(R.drawable.bg_neu_card_raised);
                btnCustom.setTextColor(getResources().getColor(R.color.colorPrimary));
                btnCustom.setText("⏰ Choose Custom Time (Pick Any Time)");
            }
        });

        if (btnCustom != null) {
            btnCustom.setOnClickListener(v -> {
                java.util.Calendar now = java.util.Calendar.getInstance();
                new android.app.TimePickerDialog(getContext(), (view, hourOfDay, minute) -> {
                    selectedHour[0] = hourOfDay;
                    selectedMin[0] = minute;
                    String amPm = hourOfDay >= 12 ? "PM" : "AM";
                    int displayHour = hourOfDay % 12;
                    if (displayHour == 0) displayHour = 12;
                    String timeStr = String.format(java.util.Locale.getDefault(), "%02d:%02d %s", displayHour, minute, amPm);
                    selectedTime[0] = timeStr;
                    btnCustom.setText("⏰ Selected: " + timeStr + " ✓");
                    btnCustom.setBackgroundResource(R.drawable.bg_m3_button);
                    btnCustom.setTextColor(onPrimaryColor);

                    btnMidnight.setBackgroundResource(R.drawable.bg_neu_card_raised);
                    btnMidnight.setTextColor(primaryColor);
                    btnMorning.setBackgroundResource(R.drawable.bg_neu_card_raised);
                    btnMorning.setTextColor(primaryColor);
                    btnNight.setBackgroundResource(R.drawable.bg_neu_card_raised);
                    btnNight.setTextColor(primaryColor);
                }, now.get(java.util.Calendar.HOUR_OF_DAY), now.get(java.util.Calendar.MINUTE), false).show();
            });
        }

        btnSave.setOnClickListener(v -> {
            String title = etTitle.getText().toString().trim();
            if (TextUtils.isEmpty(title)) {
                title = "Cycle & Health Reminder";
            }

            dialog.dismiss();
            CycleNotificationScheduler.scheduleCustomReminder(requireContext(), title, selectedHour[0], selectedMin[0]);
            Toast.makeText(getContext(), "✓ Reminder '" + title + "' scheduled for " + selectedTime[0] + "!", Toast.LENGTH_LONG).show();
        });

        dialog.show();
    }
}
