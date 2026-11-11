package com.example.nearmeshchat;

import android.content.res.ColorStateList;
import android.graphics.Color;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.floatingactionbutton.FloatingActionButton;

public class DisasterMapActivity extends AppCompatActivity {

    private WebView wvDisasterMap;
    private double currentLat = 23.0225;
    private double currentLng = 72.5714;
    private float currentAcc = 10f;
    private String currentFilter = "all";

    private Button btnFilterAll, btnFilterShelters, btnFilterHospitals, btnFilterHazards;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_disaster_map);

        currentLat = getIntent().getDoubleExtra("LATITUDE", 23.0225);
        currentLng = getIntent().getDoubleExtra("LONGITUDE", 72.5714);
        currentAcc = getIntent().getFloatExtra("ACCURACY", 10f);

        TextView tvMapSubtitle = findViewById(R.id.tvMapSubtitle);
        tvMapSubtitle.setText(String.format("GPS: %.4f° N, %.4f° E (±%.0fm)", currentLat, currentLng, currentAcc));

        findViewById(R.id.btnMapBack).setOnClickListener(v -> finish());

        btnFilterAll = findViewById(R.id.btnFilterAll);
        btnFilterShelters = findViewById(R.id.btnFilterShelters);
        btnFilterHospitals = findViewById(R.id.btnFilterHospitals);
        btnFilterHazards = findViewById(R.id.btnFilterHazards);

        setupFilterButtons();

        wvDisasterMap = findViewById(R.id.wvDisasterMap);
        WebSettings settings = wvDisasterMap.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);

        wvDisasterMap.setWebViewClient(new WebViewClient());

        String mapHtml = generateMapHtml(currentLat, currentLng, currentAcc);
        wvDisasterMap.loadDataWithBaseURL("https://aapdasetu.gov.in", mapHtml, "text/html", "UTF-8", null);

        FloatingActionButton fabRecenter = findViewById(R.id.fabRecenter);
        fabRecenter.setOnClickListener(v -> {
            wvDisasterMap.evaluateJavascript("recenterMap(" + currentLat + ", " + currentLng + ");", null);
        });
    }

    private void setupFilterButtons() {
        btnFilterAll.setOnClickListener(v -> updateFilter("all"));
        btnFilterShelters.setOnClickListener(v -> updateFilter("shelters"));
        btnFilterHospitals.setOnClickListener(v -> updateFilter("hospitals"));
        btnFilterHazards.setOnClickListener(v -> updateFilter("hazards"));
    }

    private void updateFilter(String filter) {
        currentFilter = filter;

        btnFilterAll.setBackgroundTintList(ColorStateList.valueOf(filter.equals("all") ? Color.parseColor("#E53935") : Color.parseColor("#F1F5F9")));
        btnFilterAll.setTextColor(filter.equals("all") ? Color.WHITE : Color.parseColor("#0F172A"));

        btnFilterShelters.setBackgroundTintList(ColorStateList.valueOf(filter.equals("shelters") ? Color.parseColor("#16A34A") : Color.parseColor("#F1F5F9")));
        btnFilterShelters.setTextColor(filter.equals("shelters") ? Color.WHITE : Color.parseColor("#0F172A"));

        btnFilterHospitals.setBackgroundTintList(ColorStateList.valueOf(filter.equals("hospitals") ? Color.parseColor("#2563EB") : Color.parseColor("#F1F5F9")));
        btnFilterHospitals.setTextColor(filter.equals("hospitals") ? Color.WHITE : Color.parseColor("#0F172A"));

        btnFilterHazards.setBackgroundTintList(ColorStateList.valueOf(filter.equals("hazards") ? Color.parseColor("#D97706") : Color.parseColor("#F1F5F9")));
        btnFilterHazards.setTextColor(filter.equals("hazards") ? Color.WHITE : Color.parseColor("#0F172A"));

        wvDisasterMap.evaluateJavascript("filterMarkers('" + filter + "');", null);
    }

    private String generateMapHtml(double lat, double lng, float acc) {
        return "<!DOCTYPE html>\n" +
                "<html>\n" +
                "<head>\n" +
                "  <meta charset='utf-8' />\n" +
                "  <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />\n" +
                "  <link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' />\n" +
                "  <script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>\n" +
                "  <style>\n" +
                "    html, body, #map { width: 100%; height: 100%; margin: 0; padding: 0; background: #e2e8f0; font-family: sans-serif; }\n" +
                "    .pulse-ring { width: 34px; height: 34px; border-radius: 50%; background: rgba(220, 38, 38, 0.35); border: 3px solid #dc2626; box-shadow: 0 0 12px rgba(220,38,38,0.8); animation: pulse 1.6s infinite ease-out; }\n" +
                "    @keyframes pulse { 0% { transform: scale(0.6); opacity: 1; } 100% { transform: scale(1.6); opacity: 0; } }\n" +
                "    .badge { padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; color: #fff; display: inline-block; }\n" +
                "    .popup-title { font-size: 14px; font-weight: bold; color: #0f172a; margin-bottom: 4px; }\n" +
                "    .popup-sub { font-size: 12px; color: #475569; line-height: 1.4; }\n" +
                "  </style>\n" +
                "</head>\n" +
                "<body>\n" +
                "  <div id='map'></div>\n" +
                "  <script>\n" +
                "    var myLat = " + lat + ";\n" +
                "    var myLng = " + lng + ";\n" +
                "    var map = L.map('map', { zoomControl: false }).setView([myLat, myLng], 14);\n" +
                "\n" +
                "    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {\n" +
                "      attribution: 'AapdaSetu Disaster Command • OpenStreetMap',\n" +
                "      maxZoom: 19\n" +
                "    }).addTo(map);\n" +
                "\n" +
                "    var sheltersLayer = L.layerGroup().addTo(map);\n" +
                "    var hospitalsLayer = L.layerGroup().addTo(map);\n" +
                "    var hazardsLayer = L.layerGroup().addTo(map);\n" +
                "\n" +
                "    // Current User Pulse Beacon\n" +
                "    var pulseIcon = L.divIcon({\n" +
                "      className: 'pulse-container',\n" +
                "      html: '<div class=\"pulse-ring\"></div><div style=\"position:absolute; top:9px; left:9px; width:16px; height:16px; background:#dc2626; border-radius:50%; border:2px solid #fff;\"></div>',\n" +
                "      iconSize: [34, 34],\n" +
                "      iconAnchor: [17, 17]\n" +
                "    });\n" +
                "    var userMarker = L.marker([myLat, myLng], { icon: pulseIcon }).addTo(map);\n" +
                "    userMarker.bindPopup('<div class=\"popup-title\">📍 You Are Here</div><div class=\"popup-sub\">GPS Accuracy: ±" + acc + "m<br/>Status: <strong>Monitored in Safety Zone</strong></div>').openPopup();\n" +
                "\n" +
                "    // Safe Shelters\n" +
                "    L.marker([23.0425, 72.5620]).addTo(sheltersLayer).bindPopup('<div class=\"popup-title\">🏕️ Sardar Patel Indoor Evacuation Center</div><div class=\"popup-sub\"><span class=\"badge\" style=\"background:#16a34a;\">OPEN</span><br/>Capacity: 1500 (Occupied: 120)<br/>Supplies: Water, Rations, First Aid Ready</div>');\n" +
                "    L.marker([23.0360, 72.5480]).addTo(sheltersLayer).bindPopup('<div class=\"popup-title\">🏕️ Gujarat University Convention Relief Zone</div><div class=\"popup-sub\"><span class=\"badge\" style=\"background:#16a34a;\">OPEN</span><br/>Capacity: 2500<br/>Rations & Temporary Tents Available</div>');\n" +
                "    L.marker([23.0300, 72.5770]).addTo(sheltersLayer).bindPopup('<div class=\"popup-title\">🏕️ Sabarmati Riverfront Relief Wing</div><div class=\"popup-sub\"><span class=\"badge\" style=\"background:#16a34a;\">ACTIVE</span><br/>AMC Disaster Relief Base Camp</div>');\n" +
                "\n" +
                "    // Hospitals\n" +
                "    L.marker([23.0525, 72.5873]).addTo(hospitalsLayer).bindPopup('<div class=\"popup-title\">🏥 Ahmedabad Civil Hospital & Trauma Centre</div><div class=\"popup-sub\"><span class=\"badge\" style=\"background:#2563eb;\">TRAUMA READY</span><br/>Available Beds: <strong>340</strong> / 1200<br/>ICU Beds: <strong>28</strong> | Ambulances: <strong>6</strong><br/>Phone: 079-22680074</div>');\n" +
                "    L.marker([23.0185, 72.5714]).addTo(hospitalsLayer).bindPopup('<div class=\"popup-title\">🏥 SVP Hospital (Ellisbridge)</div><div class=\"popup-sub\"><span class=\"badge\" style=\"background:#2563eb;\">EMERGENCY ACTIVE</span><br/>Available Beds: <strong>210</strong> / 800<br/>ICU Beds: <strong>18</strong> | Ambulances: <strong>4</strong><br/>Phone: 079-26577621</div>');\n" +
                "    L.marker([23.1020, 72.5950]).addTo(hospitalsLayer).bindPopup('<div class=\"popup-title\">🏥 Apollo Hospitals Gandhinagar/Ahmedabad</div><div class=\"popup-sub\"><span class=\"badge\" style=\"background:#2563eb;\">READY</span><br/>Available Beds: <strong>85</strong> / 350<br/>ICU Beds: <strong>12</strong><br/>Phone: 079-66701800</div>');\n" +
                "\n" +
                "    // Hazard Zones\n" +
                "    L.circle([23.0280, 72.5120], { color: '#dc2626', fillColor: '#ef4444', fillOpacity: 0.35, radius: 450 }).addTo(hazardsLayer).bindPopup('<div class=\"popup-title\">⚠️ Flash Waterlogging Alert</div><div class=\"popup-sub\">Satellite Crossroads Underpass<br/>Avoid low-lying roadways. NDRF pumps deployed.</div>');\n" +
                "    L.circle([23.0640, 72.5640], { color: '#d97706', fillColor: '#f59e0b', fillOpacity: 0.35, radius: 350 }).addTo(hazardsLayer).bindPopup('<div class=\"popup-title\">⚠️ Road Blockage Notice</div><div class=\"popup-sub\">Tree uprooting cleared by AMC Fire Squad. Normal traffic restoring.</div>');\n" +
                "\n" +
                "    // Dynamic Official Hazard Danger Zones & Citizen Reports\n" +
                "    function loadDynamicHazards() {\n" +
                "      var alertEndpoints = ['http://127.0.0.1:5000/api/alerts', 'https://sahay-2tvh.onrender.com/api/alerts'];\n" +
                "      function fetchAlerts(idx) {\n" +
                "        if (idx >= alertEndpoints.length) return;\n" +
                "        fetch(alertEndpoints[idx])\n" +
                "          .then(function(res){ return res.json(); })\n" +
                "          .then(function(data){\n" +
                "            if (data && data.data && data.data.length > 0) {\n" +
                "              data.data.forEach(function(alert){\n" +
                "                if (alert.active !== false && alert.latitude && alert.longitude) {\n" +
                "                  var r = (alert.radiusKm || 5) * 1000;\n" +
                "                  L.circle([alert.latitude, alert.longitude], {\n" +
                "                    color: '#dc2626',\n" +
                "                    weight: 2,\n" +
                "                    dashArray: '6, 6',\n" +
                "                    fillColor: '#ef4444',\n" +
                "                    fillOpacity: 0.25,\n" +
                "                    radius: r\n" +
                "                  }).addTo(hazardsLayer);\n" +
                "                  var hIcon = L.divIcon({\n" +
                "                    className: 'danger-pin',\n" +
                "                    html: '<div style=\"background:#dc2626; color:#fff; font-size:14px; font-weight:bold; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; border:2px solid #fff; box-shadow:0 0 10px rgba(220,38,38,0.8);\">⚠️</div>',\n" +
                "                    iconSize: [28, 28],\n" +
                "                    iconAnchor: [14, 14]\n" +
                "                  });\n" +
                "                  L.marker([alert.latitude, alert.longitude], { icon: hIcon })\n" +
                "                    .addTo(hazardsLayer)\n" +
                "                    .bindPopup('<div class=\"popup-title\" style=\"color:#dc2626;\">⚠️ ' + (alert.title || 'Official Danger Zone') + '</div>' +\n" +
                "                               '<div class=\"popup-sub\"><strong>Severity:</strong> ' + (alert.severity || 'CRITICAL') + '<br/>' +\n" +
                "                               '<strong>Danger Radius:</strong> ' + (alert.radiusKm || 5) + ' km<br/>' +\n" +
                "                               '<strong>Advisory:</strong> ' + (alert.message || 'Evacuate or avoid this danger area') + '</div>');\n" +
                "                }\n" +
                "              });\n" +
                "            }\n" +
                "          }).catch(function(){ fetchAlerts(idx + 1); });\n" +
                "      }\n" +
                "      fetchAlerts(0);\n" +
                "\n" +
                "      var reportEndpoints = ['http://127.0.0.1:5000/api/reports', 'https://sahay-2tvh.onrender.com/api/reports'];\n" +
                "      function fetchReports(idx) {\n" +
                "        if (idx >= reportEndpoints.length) return;\n" +
                "        fetch(reportEndpoints[idx])\n" +
                "          .then(function(res){ return res.json(); })\n" +
                "          .then(function(data){\n" +
                "            if (data && data.data && data.data.length > 0) {\n" +
                "              data.data.forEach(function(rep){\n" +
                "                if (rep.latitude && rep.longitude) {\n" +
                "                  var repIcon = L.divIcon({\n" +
                "                    className: 'rep-pin',\n" +
                "                    html: '<div style=\"background:#d97706; color:#fff; font-size:12px; font-weight:bold; border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center; border:2px solid #fff;\">📢</div>',\n" +
                "                    iconSize: [26, 26],\n" +
                "                    iconAnchor: [13, 13]\n" +
                "                  });\n" +
                "                  var imgHtml = '';\n" +
                "                  var imgUrl = rep.mediaUrl || (rep.images && rep.images[0]);\n" +
                "                  if (imgUrl) {\n" +
                "                    imgHtml = '<div style=\"margin-top:6px;\"><img src=\"' + imgUrl + '\" style=\"width:100%; max-height:120px; object-fit:cover; border-radius:6px;\" /></div>';\n" +
                "                  }\n" +
                "                  L.marker([rep.latitude, rep.longitude], { icon: repIcon })\n" +
                "                    .addTo(hazardsLayer)\n" +
                "                    .bindPopup('<div class=\"popup-title\" style=\"color:#b45309;\">📢 ' + (rep.type || 'Citizen Report') + '</div>' +\n" +
                "                               '<div class=\"popup-sub\">' + (rep.description || '') + '<br/>' +\n" +
                "                               '<small style=\"color:#64748b;\">Reported by: ' + (rep.userName || 'Citizen') + '</small></div>' + imgHtml);\n" +
                "                }\n" +
                "              });\n" +
                "            }\n" +
                "          }).catch(function(){ fetchReports(idx + 1); });\n" +
                "      }\n" +
                "      fetchReports(0);\n" +
                "    }\n" +
                "    loadDynamicHazards();\n" +
                "\n" +
                "    function filterMarkers(type) {\n" +
                "      if (type === 'all') {\n" +
                "        map.addLayer(sheltersLayer);\n" +
                "        map.addLayer(hospitalsLayer);\n" +
                "        map.addLayer(hazardsLayer);\n" +
                "      } else if (type === 'shelters') {\n" +
                "        map.addLayer(sheltersLayer);\n" +
                "        map.removeLayer(hospitalsLayer);\n" +
                "        map.removeLayer(hazardsLayer);\n" +
                "      } else if (type === 'hospitals') {\n" +
                "        map.removeLayer(sheltersLayer);\n" +
                "        map.addLayer(hospitalsLayer);\n" +
                "        map.removeLayer(hazardsLayer);\n" +
                "      } else if (type === 'hazards') {\n" +
                "        map.removeLayer(sheltersLayer);\n" +
                "        map.removeLayer(hospitalsLayer);\n" +
                "        map.addLayer(hazardsLayer);\n" +
                "      }\n" +
                "    }\n" +
                "\n" +
                "    function recenterMap(lat, lng) {\n" +
                "      map.setView([lat, lng], 15, { animate: true });\n" +
                "      userMarker.openPopup();\n" +
                "    }\n" +
                "  </script>\n" +
                "</body>\n" +
                "</html>";
    }
}
