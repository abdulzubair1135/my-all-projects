package com.projectflow.android.ui.fragment;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.projectflow.android.R;
import com.projectflow.android.data.local.AppDatabase;
import com.projectflow.android.data.local.TaskEntity;
import com.projectflow.android.ui.CreateTaskActivity;
import com.projectflow.android.ui.TaskDetailsActivity;
import com.projectflow.android.ui.adapter.TaskAdapter;

import java.text.SimpleDateFormat;
import java.util.*;

public class CalendarFragment extends Fragment {

    private TextView btnPrevMonth, btnNextMonth, tvCurrentMonthYear, btnToday;
    private GridView gvCalendar;
    private TextView tvSelectedDateHeader, tvDayTaskCount, tvEmptyDay;
    private RecyclerView rvDayTasks;
    private FloatingActionButton fabAddEvent;
    private TaskAdapter taskAdapter;

    private Calendar currentDisplayMonth;
    private Calendar selectedDate;
    private final Calendar today = Calendar.getInstance();

    private final SimpleDateFormat monthYearFormat = new SimpleDateFormat("MMMM yyyy", Locale.getDefault());
    private final SimpleDateFormat isoDateFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
    private final SimpleDateFormat displayDateFormat = new SimpleDateFormat("EEEE, MMM d", Locale.getDefault());

    private List<TaskEntity> allTasks = new ArrayList<>();
    private final Set<String> datesWithTasks = new HashSet<>();

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_calendar, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        currentDisplayMonth = Calendar.getInstance();
        selectedDate = Calendar.getInstance();

        btnPrevMonth = view.findViewById(R.id.btnPrevMonth);
        btnNextMonth = view.findViewById(R.id.btnNextMonth);
        tvCurrentMonthYear = view.findViewById(R.id.tvCurrentMonthYear);
        btnToday = view.findViewById(R.id.btnToday);
        gvCalendar = view.findViewById(R.id.gvCalendar);

        tvSelectedDateHeader = view.findViewById(R.id.tvSelectedDateHeader);
        tvDayTaskCount = view.findViewById(R.id.tvDayTaskCount);
        tvEmptyDay = view.findViewById(R.id.tvEmptyDay);
        rvDayTasks = view.findViewById(R.id.rvDayTasks);
        fabAddEvent = view.findViewById(R.id.fabAddEvent);

        taskAdapter = new TaskAdapter(task -> {
            Intent intent = new Intent(requireContext(), TaskDetailsActivity.class);
            intent.putExtra("task_id", task.id);
            intent.putExtra("task_title", task.title);
            intent.putExtra("task_desc", task.description);
            intent.putExtra("task_priority", task.priority);
            intent.putExtra("task_status", task.statusCategory);
            intent.putExtra("task_due", task.dueDate);
            intent.putExtra("task_progress", task.progressPercent);
            intent.putExtra("task_project_id", task.projectId);
            startActivity(intent);
        });
        rvDayTasks.setLayoutManager(new LinearLayoutManager(requireContext()));
        rvDayTasks.setAdapter(taskAdapter);

        // Prev Month
        btnPrevMonth.setOnClickListener(v -> {
            currentDisplayMonth.add(Calendar.MONTH, -1);
            updateCalendarGrid();
        });

        // Next Month
        btnNextMonth.setOnClickListener(v -> {
            currentDisplayMonth.add(Calendar.MONTH, 1);
            updateCalendarGrid();
        });

        // Today Shortcut
        btnToday.setOnClickListener(v -> {
            currentDisplayMonth = Calendar.getInstance();
            selectedDate = Calendar.getInstance();
            updateCalendarGrid();
            filterTasksForSelectedDate();
        });

        fabAddEvent.setOnClickListener(v -> {
            Intent intent = new Intent(requireContext(), CreateTaskActivity.class);
            intent.putExtra("default_due_date", isoDateFormat.format(selectedDate.getTime()));
            startActivity(intent);
        });

        // Observe Tasks
        AppDatabase db = AppDatabase.getInstance(requireContext());
        db.taskDao().getAllLive().observe(getViewLifecycleOwner(), list -> {
            allTasks = (list != null) ? list : new ArrayList<>();
            datesWithTasks.clear();
            for (TaskEntity t : allTasks) {
                if (t.dueDate != null && !t.dueDate.isEmpty()) {
                    datesWithTasks.add(t.dueDate);
                }
            }
            updateCalendarGrid();
            filterTasksForSelectedDate();
        });

        updateCalendarGrid();
        filterTasksForSelectedDate();
    }

    private void updateCalendarGrid() {
        tvCurrentMonthYear.setText(monthYearFormat.format(currentDisplayMonth.getTime()));

        Calendar cal = (Calendar) currentDisplayMonth.clone();
        cal.set(Calendar.DAY_OF_MONTH, 1);

        int firstDayOfWeek = cal.get(Calendar.DAY_OF_WEEK) - 1; // 0 for Sunday
        int maxDaysInMonth = cal.getActualMaximum(Calendar.DAY_OF_MONTH);

        List<DayItem> daysList = new ArrayList<>();
        // Padding for previous month
        for (int i = 0; i < firstDayOfWeek; i++) {
            daysList.add(new DayItem(0, null, false, false, false));
        }
        // Current month days
        for (int day = 1; day <= maxDaysInMonth; day++) {
            Calendar dayCal = (Calendar) currentDisplayMonth.clone();
            dayCal.set(Calendar.DAY_OF_MONTH, day);
            String iso = isoDateFormat.format(dayCal.getTime());

            boolean isToday = isSameDay(dayCal, today);
            boolean isSelected = isSameDay(dayCal, selectedDate);
            boolean hasTasks = datesWithTasks.contains(iso);

            daysList.add(new DayItem(day, iso, isToday, isSelected, hasTasks));
        }

        gvCalendar.setAdapter(new CalendarGridAdapter(requireContext(), daysList, dayItem -> {
            if (dayItem.dayNumber > 0) {
                selectedDate = (Calendar) currentDisplayMonth.clone();
                selectedDate.set(Calendar.DAY_OF_MONTH, dayItem.dayNumber);
                updateCalendarGrid();
                filterTasksForSelectedDate();
            }
        }));
    }

    private void filterTasksForSelectedDate() {
        String selectedIso = isoDateFormat.format(selectedDate.getTime());
        tvSelectedDateHeader.setText("Tasks on " + displayDateFormat.format(selectedDate.getTime()));

        List<TaskEntity> dayTasks = new ArrayList<>();
        for (TaskEntity t : allTasks) {
            if (selectedIso.equals(t.dueDate)) {
                dayTasks.add(t);
            }
        }

        tvDayTaskCount.setText(dayTasks.size() + (dayTasks.size() == 1 ? " Task" : " Tasks"));
        taskAdapter.setTasks(dayTasks);

        if (dayTasks.isEmpty()) {
            rvDayTasks.setVisibility(View.GONE);
            tvEmptyDay.setVisibility(View.VISIBLE);
        } else {
            tvEmptyDay.setVisibility(View.GONE);
            rvDayTasks.setVisibility(View.VISIBLE);
        }
    }

    private boolean isSameDay(Calendar c1, Calendar c2) {
        return c1.get(Calendar.YEAR) == c2.get(Calendar.YEAR) &&
               c1.get(Calendar.DAY_OF_YEAR) == c2.get(Calendar.DAY_OF_YEAR);
    }

    private static class DayItem {
        int dayNumber;
        String isoDate;
        boolean isToday;
        boolean isSelected;
        boolean hasTasks;

        DayItem(int dayNumber, String isoDate, boolean isToday, boolean isSelected, boolean hasTasks) {
            this.dayNumber = dayNumber;
            this.isoDate = isoDate;
            this.isToday = isToday;
            this.isSelected = isSelected;
            this.hasTasks = hasTasks;
        }
    }

    private interface OnDayClickListener {
        void onDayClick(DayItem day);
    }

    private static class CalendarGridAdapter extends BaseAdapter {
        private final Context context;
        private final List<DayItem> days;
        private final OnDayClickListener listener;

        CalendarGridAdapter(Context context, List<DayItem> days, OnDayClickListener listener) {
            this.context = context;
            this.days = days;
            this.listener = listener;
        }

        @Override public int getCount() { return days.size(); }
        @Override public Object getItem(int position) { return days.get(position); }
        @Override public long getItemId(int position) { return position; }

        @NonNull
        @Override
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            if (convertView == null) {
                convertView = LayoutInflater.from(context).inflate(R.layout.item_calendar_day, parent, false);
            }

            DayItem item = days.get(position);
            TextView tvDay = convertView.findViewById(R.id.tvDayNumber);
            View dot = convertView.findViewById(R.id.dotEvent);

            if (item.dayNumber == 0) {
                tvDay.setText("");
                dot.setVisibility(View.INVISIBLE);
                convertView.setOnClickListener(null);
            } else {
                tvDay.setText(String.valueOf(item.dayNumber));
                dot.setVisibility(item.hasTasks ? View.VISIBLE : View.INVISIBLE);

                if (item.isSelected) {
                    tvDay.setBackgroundResource(R.drawable.bg_chip_selected);
                    tvDay.setTextColor(Color.WHITE);
                } else if (item.isToday) {
                    tvDay.setBackgroundResource(R.drawable.bg_badge_info);
                    tvDay.setTextColor(ContextCompat.getColor(context, R.color.earth_info));
                } else {
                    tvDay.setBackground(null);
                    tvDay.setTextColor(ContextCompat.getColor(context, R.color.text_main));
                }

                convertView.setOnClickListener(v -> listener.onDayClick(item));
            }

            return convertView;
        }
    }
}
