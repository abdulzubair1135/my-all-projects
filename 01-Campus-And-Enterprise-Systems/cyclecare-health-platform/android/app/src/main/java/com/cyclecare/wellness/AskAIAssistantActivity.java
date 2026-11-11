package com.cyclecare.wellness;

import android.os.Bundle;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.cyclecare.R;
import com.cyclecare.api.ApiClient;
import com.cyclecare.api.ApiService;

import java.util.HashMap;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AskAIAssistantActivity extends AppCompatActivity {

    private CheckBox chkIncludeCycleData;
    private TextView tvResponse;
    private EditText etPrompt;
    private Button btnSend;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ask_ai);

        chkIncludeCycleData = findViewById(R.id.chk_include_cycle_data);
        tvResponse = findViewById(R.id.tv_ai_response);
        etPrompt = findViewById(R.id.et_prompt);
        btnSend = findViewById(R.id.btn_send_prompt);

        btnSend.setOnClickListener(v -> sendPrompt());
    }

    private void sendPrompt() {
        String prompt = etPrompt.getText().toString().trim();
        if (prompt.isEmpty()) return;

        boolean includeData = chkIncludeCycleData.isChecked();
        tvResponse.setText("Asking Ask CycleCare AI...");

        Map<String, Object> body = new HashMap<>();
        body.put("message", prompt);
        body.put("include_user_cycle_data", includeData);

        ApiService api = ApiClient.getApiService(this);
        api.askAI(body).enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(Call<Map<String, Object>> call, Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    String content = (String) response.body().get("content");
                    tvResponse.setText(content);
                } else {
                    tvResponse.setText("Error receiving AI response.");
                }
            }

            @Override
            public void onFailure(Call<Map<String, Object>> call, Throwable t) {
                tvResponse.setText("Unable to connect to CycleCare AI service.");
            }
        });
    }
}
