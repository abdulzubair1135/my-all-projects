package com.cyclecare.cycle;

import android.app.DatePickerDialog;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.repository.CycleRepository;
import com.google.android.material.textfield.TextInputLayout;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class PeriodLogActivity extends AppCompatActivity {

    private EditText etStartDate, etEndDate, etNotes;
    private TextInputLayout tilStartDate, tilEndDate;
    private RadioGroup rgFlow;
    private Button btnSaveLog, btnDeleteLog;
    private CycleRepository cycleRepository;
    private String existingLogId = null;
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_period_log);

        etStartDate = findViewById(R.id.et_start_date);
        etEndDate = findViewById(R.id.et_end_date);
        tilStartDate = findViewById(R.id.til_start_date);
        tilEndDate = findViewById(R.id.til_end_date);
        etNotes = findViewById(R.id.et_notes);
        rgFlow = findViewById(R.id.rg_flow);
        btnSaveLog = findViewById(R.id.btn_save_log);
        btnDeleteLog = findViewById(R.id.btn_delete_log);

        cycleRepository = new CycleRepository(this);

        String today = dateFormat.format(new Date());
        etStartDate.setText(today);

        // Click listeners to open DatePickerDialog
        View.OnClickListener startPickerListener = v -> showDatePicker(etStartDate);
        etStartDate.setOnClickListener(startPickerListener);
        if (tilStartDate != null) tilStartDate.setOnClickListener(startPickerListener);

        View.OnClickListener endPickerListener = v -> showDatePicker(etEndDate);
        etEndDate.setOnClickListener(endPickerListener);
        if (tilEndDate != null) tilEndDate.setOnClickListener(endPickerListener);

        btnSaveLog.setOnClickListener(v -> savePeriodLog());

        if (btnDeleteLog != null) {
            btnDeleteLog.setOnClickListener(v -> {
                new androidx.appcompat.app.AlertDialog.Builder(this)
                        .setTitle("🗑️ Delete Period Log")
                        .setMessage("Are you sure you want to delete this period log?")
                        .setPositiveButton("Delete", (d, w) -> {
                            if (existingLogId != null) {
                                cycleRepository.deletePeriodLog(existingLogId);
                                Toast.makeText(this, "✓ Period log deleted. Cycle reset to empty.", Toast.LENGTH_SHORT).show();
                                finish();
                            }
                        })
                        .setNegativeButton("Cancel", null)
                        .show();
            });
        }

        // Check if an existing log exists to support updating/editing
        new Thread(() -> {
            java.util.List<com.cyclecare.database.entity.PeriodLogEntity> logs = 
                    com.cyclecare.database.AppDatabase.getInstance(this).periodLogDao().getAllPeriodLogsSync();
            if (logs != null && !logs.isEmpty()) {
                com.cyclecare.database.entity.PeriodLogEntity latest = logs.get(0);
                existingLogId = latest.getId();
                runOnUiThread(() -> {
                    if (latest.getStartDate() != null) etStartDate.setText(latest.getStartDate());
                    if (latest.getEndDate() != null && !latest.getEndDate().isEmpty()) {
                        etEndDate.setText(latest.getEndDate());
                    }
                    if ("LIGHT".equalsIgnoreCase(latest.getFlow())) {
                        rgFlow.check(R.id.rb_flow_light);
                    } else if ("HEAVY".equalsIgnoreCase(latest.getFlow())) {
                        rgFlow.check(R.id.rb_flow_heavy);
                    } else {
                        rgFlow.check(R.id.rb_flow_medium);
                    }
                    if (latest.getNotes() != null) etNotes.setText(latest.getNotes());
                    btnSaveLog.setText("UPDATE PERIOD LOG");
                    if (btnDeleteLog != null) btnDeleteLog.setVisibility(View.VISIBLE);
                });
            }
        }).start();
    }

    private void showDatePicker(EditText targetEditText) {
        Calendar calendar = Calendar.getInstance();
        String currentText = targetEditText.getText().toString().trim();
        if (!currentText.isEmpty()) {
            try {
                Date parsed = dateFormat.parse(currentText);
                if (parsed != null) calendar.setTime(parsed);
            } catch (Exception ignored) {}
        }

        DatePickerDialog dialog = new DatePickerDialog(
                this,
                (view, year, month, dayOfMonth) -> {
                    Calendar selected = Calendar.getInstance();
                    selected.set(year, month, dayOfMonth);
                    targetEditText.setText(dateFormat.format(selected.getTime()));
                },
                calendar.get(Calendar.YEAR),
                calendar.get(Calendar.MONTH),
                calendar.get(Calendar.DAY_OF_MONTH)
        );

        dialog.show();
    }

    private void savePeriodLog() {
        String start = etStartDate.getText().toString().trim();
        String end = etEndDate.getText().toString().trim();
        String notes = etNotes.getText().toString().trim();

        if (start.isEmpty()) {
            Toast.makeText(this, "Start date is required", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!end.isEmpty()) {
            try {
                Date startDate = dateFormat.parse(start);
                Date endDate = dateFormat.parse(end);
                if (startDate != null && endDate != null && endDate.before(startDate)) {
                    Toast.makeText(this, "End date cannot be earlier than start date", Toast.LENGTH_SHORT).show();
                    return;
                }
            } catch (Exception ignored) {}
        }

        int selectedId = rgFlow.getCheckedRadioButtonId();
        String flow = "MEDIUM";
        if (selectedId == R.id.rb_flow_light) flow = "LIGHT";
        else if (selectedId == R.id.rb_flow_heavy) flow = "HEAVY";

        if (existingLogId != null) {
            cycleRepository.updatePeriodLog(existingLogId, start, end, flow, notes);
            Toast.makeText(this, "✓ Period log updated! New dates applied.", Toast.LENGTH_SHORT).show();
        } else {
            cycleRepository.addPeriodLog(start, end, flow, notes);
            Toast.makeText(this, "✓ Period log saved! Updated cycle estimation.", Toast.LENGTH_SHORT).show();
        }
        finish();
    }
}
