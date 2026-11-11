package com.example.nearmeshchat;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class WebActivity extends AppCompatActivity {
    public static String htmlPayload = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());

        if (htmlPayload != null && !htmlPayload.isEmpty()) {
            webView.loadDataWithBaseURL("http://www.abdul.dream", htmlPayload, "text/html", "UTF-8", null);
        } else {
            webView.loadData("<h3>Connecting to Mesh Node Gateway...</h3>", "text/html", "UTF-8");
        }
    }
}