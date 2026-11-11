package com.example.meshlink.browser;

import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.meshlink.R;

public class BrowserFragment extends Fragment {

    private WebView wvOfflineBrowser;
    private EditText etBrowserUrl;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_browser, container, false);

        wvOfflineBrowser = v.findViewById(R.id.wvOfflineBrowser);
        etBrowserUrl = v.findViewById(R.id.etBrowserUrl);

        setupWebView();

        v.findViewById(R.id.btnBrowserBack).setOnClickListener(view -> {
            if (wvOfflineBrowser.canGoBack()) wvOfflineBrowser.goBack();
        });

        v.findViewById(R.id.btnBrowserForward).setOnClickListener(view -> {
            if (wvOfflineBrowser.canGoForward()) wvOfflineBrowser.goForward();
        });

        v.findViewById(R.id.btnBrowserGo).setOnClickListener(view -> loadEnteredUrl());

        v.findViewById(R.id.btnDefaultServer).setOnClickListener(view -> {
            etBrowserUrl.setText("http://127.0.0.1:8888");
            loadEnteredUrl();
        });

        etBrowserUrl.setOnEditorActionListener((textView, actionId, keyEvent) -> {
            if (actionId == EditorInfo.IME_ACTION_GO) {
                loadEnteredUrl();
                return true;
            }
            return false;
        });

        // Smart Auto-Connect to Offline Laptop Server
        autoConnectServer();
        return v;
    }

    private void autoConnectServer() {
        // Show landing page first
        loadDefaultLandingPage();

        // Background probe to see if server is active and auto-load if reachable
        new Thread(() -> {
            String[] candidateIps = new String[]{"127.0.0.1", "10.221.131.3", "192.168.137.1", "10.0.2.2"};
            String workingUrl = null;

            for (String ip : candidateIps) {
                try {
                    java.net.URL url = new java.net.URL("http://" + ip + ":8888/api/status");
                    java.net.HttpURLConnection conn = (java.net.HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(800);
                    conn.setReadTimeout(800);
                    conn.setRequestMethod("GET");
                    int code = conn.getResponseCode();
                    if (code == 200) {
                        workingUrl = "http://" + ip + ":8888";
                        conn.disconnect();
                        break;
                    }
                    conn.disconnect();
                } catch (Exception ignored) {}
            }

            if (workingUrl != null) {
                final String target = workingUrl;
                if (getActivity() != null) {
                    getActivity().runOnUiThread(() -> {
                        if (etBrowserUrl != null) etBrowserUrl.setText(target);
                        if (wvOfflineBrowser != null) {
                            Toast.makeText(getContext(), "⚡ Auto-connected to Laptop Server!", Toast.LENGTH_SHORT).show();
                            wvOfflineBrowser.loadUrl(target);
                        }
                    });
                }
            }
        }).start();
    }

    private void setupWebView() {
        WebSettings settings = wvOfflineBrowser.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);

        wvOfflineBrowser.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                if (etBrowserUrl != null && !etBrowserUrl.hasFocus() && url != null && url.startsWith("http")) {
                    etBrowserUrl.setText(url);
                }
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                loadErrorPage(failingUrl);
            }
        });
    }

    private void loadEnteredUrl() {
        String url = etBrowserUrl.getText().toString().trim();
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "http://" + url;
        }
        Toast.makeText(getContext(), "Connecting to " + url, Toast.LENGTH_SHORT).show();
        wvOfflineBrowser.loadUrl(url);
    }

    private void loadDefaultLandingPage() {
        String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>" +
                "<style>" +
                "body { font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F8F9FA; color: #111827; padding: 20px; text-align: center; margin: 0; }" +
                ".container { max-width: 480px; margin: 0 auto; }" +
                ".badge { background: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; padding: 5px 14px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; margin-bottom: 12px; }" +
                "h1 { color: #111827; font-size: 20px; margin: 6px 0; font-weight: 700; }" +
                ".card { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 18px; margin: 14px 0; text-align: left; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }" +
                "h2 { color: #16A34A; font-size: 15px; margin-top: 0; margin-bottom: 6px; font-weight: 600; }" +
                "p { color: #6B7280; font-size: 13px; line-height: 1.45; margin: 4px 0 14px 0; }" +
                ".btn { display: inline-block; background: #16A34A; color: #FFFFFF; font-weight: 600; font-size: 13px; padding: 10px 16px; border-radius: 8px; text-decoration: none; text-align: center; width: calc(100% - 32px); box-sizing: border-box; }" +
                ".btn-outline { background: #F3F4F6; color: #374151; border: 1px solid #E5E7EB; }" +
                ".steps { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 16px; margin-top: 16px; text-align: left; font-size: 13px; color: #4B5563; line-height: 1.6; }" +
                ".steps b { color: #16A34A; }" +
                "</style></head><body><div class='container'>" +
                "<div class='badge'>Offline Local Server</div>" +
                "<h1>Knowledge &amp; File Portal</h1>" +
                "<p style='color: #6B7280; font-size: 13px;'>Direct connection to your Laptop (Port 8888)</p>" +
                "<div class='card'>" +
                "<h2>📁 Shared File Hub</h2>" +
                "<p>Access emergency documentation, manuals, and files hosted on your laptop.</p>" +
                "<a class='btn' href='http://127.0.0.1:8888'>Open Laptop Portal ➔</a>" +
                "</div>" +
                "<div class='card'>" +
                "<h2>📡 Server Status &amp; Telemetry</h2>" +
                "<p>Inspect connected mesh peers and real-time server sockets.</p>" +
                "<a class='btn btn-outline' href='http://127.0.0.1:8888/api/status'>View Telemetry ➔</a>" +
                "</div>" +
                "<div class='steps'>" +
                "<div style='font-weight: 600; color: #111827; margin-bottom: 6px;'>💡 Kaise Connect Karein:</div>" +
                "1. Laptop mein <b>Mobile Hotspot</b> ON karein.<br/>" +
                "2. Phone ko laptop ke Wi-Fi se connect karein.<br/>" +
                "3. Upar <b>CONNECT</b> button par tap karein." +
                "</div>" +
                "</div></body></html>";
        wvOfflineBrowser.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null);
    }

    private void loadErrorPage(String url) {
        String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>" +
                "<style>body { font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F8F9FA; color: #111827; padding: 24px; text-align: center; }" +
                "h2 { color: #EF4444; font-size: 18px; font-weight: 600; }" +
                "p { color: #6B7280; font-size: 13px; line-height: 1.5; }" +
                "code { background: #E5E7EB; padding: 3px 6px; border-radius: 4px; color: #111827; font-family: monospace; font-size: 12px; }" +
                ".card { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 18px; margin: 18px auto; max-width: 440px; text-align: left; }" +
                "</style></head><body>" +
                "<h2>Server Not Reachable</h2>" +
                "<p>Could not connect to <code>" + url + "</code></p>" +
                "<div class='card'>" +
                "<b style='color: #111827;'>Connection Steps:</b><br/><br/>" +
                "1. Laptop par <b>Mobile Hotspot</b> ON karein.<br/>" +
                "2. Mobile ko Laptop Wi-Fi se connect karein.<br/>" +
                "3. Laptop par server chal raha hai port <b>8888</b> par.<br/>" +
                "4. Upar address bar mein <code>http://127.0.0.1:8888</code> daal kar reload karein." +
                "</div>" +
                "</body></html>";
        wvOfflineBrowser.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null);
    }
}
