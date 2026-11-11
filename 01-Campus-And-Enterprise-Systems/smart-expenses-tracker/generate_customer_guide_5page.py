# -*- coding: utf-8 -*-
"""
Smart Expenses Tracker - 5-Page Customer QuickStart Guide Generator
Generates:
1. customer_guide_5page.html (Pixel-Perfect 5-Page HTML)
2. SmartExpenses_Customer_QuickStart_Guide_5Pages.pdf (Rendered via Headless Chrome)
"""

import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def build_html():
    html = """<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<title>Smart Expenses Tracker - Customer QuickStart Guide (5 Pages)</title>
<style>
    @page {
        size: A4 portrait;
        margin: 14mm 14mm 14mm 14mm;
    }
    *, *::before, *::after {
        box-sizing: border-box;
    }
    body {
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        font-size: 8.9pt;
        line-height: 1.44;
    }
    
    .page {
        page-break-after: always;
        height: 268mm;
        max-height: 268mm;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .page:last-child {
        page-break-after: avoid;
    }

    .page-content {
        flex-grow: 1;
    }

    /* Running Header & Footer */
    .running-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #059669;
        padding-bottom: 5px;
        margin-bottom: 12px;
        font-size: 8pt;
        color: #475569;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .running-header .tag {
        background: #ecfdf5;
        color: #047857;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 7.5pt;
        font-weight: 700;
        border: 1px solid #a7f3d0;
    }

    .running-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1.5px solid #cbd5e1;
        padding-top: 5px;
        margin-top: 8px;
        font-size: 7.8pt;
        color: #64748b;
        font-weight: 500;
    }
    .running-footer .page-number {
        font-weight: 800;
        color: #0f172a;
        background: #f1f5f9;
        padding: 2px 10px;
        border-radius: 4px;
        border: 1px solid #cbd5e1;
    }

    /* Headings */
    h1.chapter-title {
        font-size: 16pt;
        color: #065f46;
        margin: 0 0 8px 0;
        font-weight: 800;
        border-left: 5px solid #10b981;
        padding-left: 10px;
        line-height: 1.25;
    }
    h2.sub-title {
        font-size: 11pt;
        color: #0f172a;
        margin: 10px 0 5px 0;
        font-weight: 700;
        border-bottom: 1.5px solid #e2e8f0;
        padding-bottom: 3px;
    }
    h3.sub-sub-title {
        font-size: 9.8pt;
        color: #1e3a8a;
        margin: 7px 0 3px 0;
        font-weight: 700;
    }
    p {
        margin: 0 0 7px 0;
        text-align: justify;
    }

    /* Badges */
    .badge {
        display: inline-block;
        font-size: 7.5pt;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 4px;
    }
    .badge-step { background: #065f46; color: #ffffff; }
    .badge-app { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
    .badge-server { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-db { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }

    /* Cards */
    .card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 11px;
        margin: 7px 0;
    }
    .card-highlight {
        background: #f0fdf4;
        border: 1.5px solid #86efac;
        border-left: 5px solid #10b981;
    }
    .card-warning {
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 4px solid #f59e0b;
    }

    /* Grid */
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin: 7px 0;
    }
    .grid-card {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 8px 10px;
    }
    .grid-card h4 {
        margin: 0 0 5px 0;
        color: #065f46;
        font-size: 9.5pt;
        font-weight: 700;
        border-bottom: 1.5px solid #10b981;
        padding-bottom: 2px;
    }

    /* Code & Terminal */
    pre.code-block {
        background: #0f172a;
        color: #f8fafc;
        padding: 8px 11px;
        border-radius: 6px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8pt;
        line-height: 1.36;
        margin: 6px 0;
        overflow: hidden;
        border: 1px solid #334155;
    }
    code.inline-code {
        background: #f1f5f9;
        color: #0f172a;
        font-family: 'Consolas', monospace;
        font-size: 8.2pt;
        padding: 1px 5px;
        border-radius: 3px;
        border: 1px solid #cbd5e1;
        font-weight: 600;
    }

    /* Tables */
    table.data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 7px 0;
        font-size: 8.2pt;
    }
    table.data-table th, table.data-table td {
        border: 1px solid #cbd5e1;
        padding: 5px 8px;
        text-align: left;
        vertical-align: top;
    }
    table.data-table th {
        background: #065f46;
        color: #ffffff;
        font-weight: 700;
    }
    table.data-table tr:nth-child(even) {
        background: #f8fafc;
    }
</style>
</head>
<body>
"""
    return html

def get_pages_content():
    pages = []

    # PAGE 1: SYSTEM OVERVIEW & 1-CLICK FAST START (.BAT)
    pages.append("""
<div class="page">
    <div class="running-header">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="tag">Page 1: 1-Click Fast Start</span>
    </div>
    <div class="page-content">
        <h1 class="chapter-title">🚀 1-Click Fast Start: Pura App &amp; Server Kaise Chalu Karein</h1>
        
        <div class="card card-highlight">
            <strong>👋 Welcome Customer! Yeh Guide Kiske Liye Hai?</strong><br/>
            Agar aapke paas poora project package aa gaya hai aur aap bina kisi technical jhanjhat ke turant <strong>App, Server aur Admin Website</strong> ko test karna chahte hain, toh yeh 5-page ki simple guide aapke liye hai.
        </div>

        <h2 class="sub-title">1. Sabse Aasan Tarika: Batch (.bat) Files Se 1-Click Me Run Karna</h2>
        <p>
            Aapko koi command yaad rakhne ki zaroorat nahi hai. Project folder ke andar ready-made automation scripts hain:
        </p>

        <div class="grid-2">
            <div class="grid-card">
                <h4>🟢 Step 1: Server &amp; Admin Website Chalu Karein</h4>
                <p style="font-size: 8.2pt; margin-bottom: 4px;">Folder me ja kar is file par <strong>Double Click</strong> karein:</p>
                <div style="background: #0f172a; color: #38bdf8; padding: 6px 9px; border-radius: 4px; font-weight: 700; font-family: Consolas; font-size: 8.8pt;">
                    START_ALL.bat
                </div>
                <p style="font-size: 7.8pt; margin-top: 5px;">
                    Yeh do windows open karega:<br/>
                    1. <strong>Backend Relay API:</strong> Port 4000 par start ho jayegi.<br/>
                    2. <strong>Admin Web Panel:</strong> Port 5173 par start ho jayega.
                </p>
            </div>

            <div class="grid-card">
                <h4>📱 Step 2: Phone Me App Install Karein</h4>
                <p style="font-size: 8.2pt; margin-bottom: 4px;">Phone ko USB cable se jodein aur double click karein:</p>
                <div style="background: #0f172a; color: #34d399; padding: 6px 9px; border-radius: 4px; font-weight: 700; font-family: Consolas; font-size: 8.8pt;">
                    INSTALL_ANDROID_USB.bat
                </div>
                <p style="font-size: 7.8pt; margin-top: 5px;">
                    Yeh script connected phone ko automatically detect karke ready APK install karegi aur phone screen par app turant open kar degi!
                </p>
            </div>
        </div>

        <h2 class="sub-title">2. Browser Me Kaunsa URL Kholna Hai?</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 25%;">Service</th>
                    <th style="width: 35%;">URL Link</th>
                    <th style="width: 40%;">Screen Par Kya Dikhega?</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Admin Web Portal</strong></td>
                    <td><code class="inline-code">http://localhost:5173</code></td>
                    <td>Real-time Diagnostic Dashboard, Server Health &amp; Logs.</td>
                </tr>
                <tr>
                    <td><strong>Backend Health Check</strong></td>
                    <td><code class="inline-code">http://localhost:4000/health</code></td>
                    <td>Green JSON status: <code class="inline-code">{"status":"UP"}</code> dikhega.</td>
                </tr>
                <tr>
                    <td><strong>Live Cloud Backup</strong></td>
                    <td><code class="inline-code">https://smart-expenses-kuob.onrender.com</code></td>
                    <td>Cloud deployed API endpoint status.</td>
                </tr>
            </tbody>
        </table>

        <h2 class="sub-title">3. Kaam Khatam Hone Par Server Band Kaise Karein?</h2>
        <div class="card card-warning">
            <strong>🛑 Hamesha STOP_ALL.bat Use Karein:</strong><br/>
            Direct window cross (X) mat karein. Folder me di gayi <strong><code class="inline-code">STOP_ALL.bat</code></strong> par double-click karein. Yeh background ports (4000 aur 5173) ko smoothly band kar deta hai taaki agli baar <em>"Port in use"</em> ka koi error na aaye.
        </div>
    </div>
    <div class="running-footer">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="page-number">Page 1 of 5</span>
    </div>
</div>
""")

    # PAGE 2: GITHUB & FOLDER STRUCTURE BREAKDOWN
    pages.append("""
<div class="page">
    <div class="running-header">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="tag">Page 2: GitHub &amp; Folders</span>
    </div>
    <div class="page-content">
        <h1 class="chapter-title">📂 GitHub &amp; Folder Structure: Kidar Kya Hai?</h1>

        <div class="card card-highlight">
            <strong>🌐 Official GitHub Repository:</strong><br/>
            Project ka official source code link: <strong><a href="https://github.com/smartexpensehelp-sketch" style="color: #047857; text-decoration: underline;">https://github.com/smartexpensehelp-sketch</a></strong><br/>
            Customer delivery archive zip: <code class="inline-code">SmartExpenses-Complete-Project.zip</code>
        </div>

        <h2 class="sub-title">1. Project Folder Ka Map (Har Folder Ka Kaam)</h2>
        <p>Jab aap ZIP file extract karte hain, toh aapko yeh 4 main folders aur automation files milti hain:</p>

        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 25%;">Folder / File Name</th>
                    <th style="width: 20%;">Category</th>
                    <th style="width: 55%;">Iske Andar Kya Hai Aur Iska Use Kya Hai?</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code class="inline-code">android/</code></td>
                    <td><span class="badge badge-app">Mobile App</span></td>
                    <td>Pure Java 17 aur XML layouts ka complete Android Studio project. Room SQLite local database, voice engine aur UI screens isi ke andar hain.</td>
                </tr>
                <tr>
                    <td><code class="inline-code">backend/</code></td>
                    <td><span class="badge badge-server">Relay Server</span></td>
                    <td>Node.js, Express aur TypeScript ka backend API server. Mobile app aur Supabase database ke beech bridge ka kaam karta hai (Port 4000).</td>
                </tr>
                <tr>
                    <td><code class="inline-code">admin/</code></td>
                    <td><span class="badge badge-server">Web Portal</span></td>
                    <td>React 18 aur Vite ka Admin Dashboard source code. Isme system diagnostics, database connection status aur network telemetry monitor hoti hai.</td>
                </tr>
                <tr>
                    <td><code class="inline-code">APK/</code></td>
                    <td><span class="badge badge-app">Ready Binary</span></td>
                    <td>Pre-compiled <code class="inline-code">SmartExpenses-v1.0.apk</code> file. Agar aapko Android Studio open nahi karna hai, toh aap is APK ko direct phone me install kar sakte hain.</td>
                </tr>
                <tr>
                    <td><code class="inline-code">*.bat files</code></td>
                    <td><span class="badge badge-step">Automation</span></td>
                    <td><code class="inline-code">START_ALL.bat</code>, <code class="inline-code">STOP_ALL.bat</code>, <code class="inline-code">INSTALL_ANDROID_USB.bat</code> aur <code class="inline-code">RUN_AND_INSTALL.bat</code>.</td>
                </tr>
            </tbody>
        </table>

        <h2 class="sub-title">2. GitHub Par Important Files Kidar Hain?</h2>
        <div class="grid-2">
            <div class="grid-card">
                <h4>Android Ke Main Java Codes</h4>
                <p style="font-size: 7.8pt;">
                    &bull; <strong>Room DB Model:</strong> <code class="inline-code">android/app/src/main/java/.../entity/TransactionEntity.java</code><br/>
                    &bull; <strong>Database Queries:</strong> <code class="inline-code">.../dao/TransactionDao.java</code><br/>
                    &bull; <strong>Voice AI Sheet:</strong> <code class="inline-code">.../ui/voice/VoiceBottomSheet.java</code><br/>
                    &bull; <strong>Background Sync:</strong> <code class="inline-code">.../worker/SyncWorker.java</code>
                </p>
            </div>
            <div class="grid-card">
                <h4>Backend &amp; Server Files</h4>
                <p style="font-size: 7.8pt;">
                    &bull; <strong>Main Server:</strong> <code class="inline-code">backend/src/server.ts</code><br/>
                    &bull; <strong>Sync Push/Pull:</strong> <code class="inline-code">backend/src/routes/sync.ts</code><br/>
                    &bull; <strong>Admin Telemetry:</strong> <code class="inline-code">backend/src/routes/monitoring.ts</code><br/>
                    &bull; <strong>Environment Keys:</strong> <code class="inline-code">backend/.env</code>
                </p>
            </div>
        </div>

        <div class="card card-warning" style="margin-top: 6px;">
            <strong>📌 Rule Jo Yaad Rakhna Hai:</strong> Android project me ek bhi Kotlin file (`.kt`) nahi hai! Poora code <strong>Pure Java &amp; XML</strong> me likha gaya hai.
        </div>
    </div>
    <div class="running-footer">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="page-number">Page 2 of 5</span>
    </div>
</div>
""")

    # PAGE 3: SUPABASE CLOUD DATABASE & BACKEND SETUP
    pages.append("""
<div class="page">
    <div class="running-header">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="tag">Page 3: Supabase &amp; Cloud</span>
    </div>
    <div class="page-content">
        <h1 class="chapter-title">☁️ Supabase Cloud Database &amp; Backend Setup</h1>

        <h2 class="sub-title">1. Supabase Kya Hai Aur Yeh Kyu Use Kiya Hai?</h2>
        <p>
            Supabase ek secure cloud platform hai jo background me authentic <strong>Enterprise PostgreSQL 15 Database</strong> run karta hai. Jab phone me internet hota hai, toh app ka sara financial data encrypt hokar Supabase me permanently safe ho jata hai.
        </p>

        <div class="grid-2">
            <div class="grid-card">
                <h4>Row Level Security (RLS)</h4>
                <p style="font-size: 7.8pt;">Har user ka data doosre user se 100% isolated rehta hai. User A kabhi User B ka transaction na padh sakta hai na badal sakta hai.</p>
            </div>
            <div class="grid-card">
                <h4>Paise Integer Precision</h4>
                <p style="font-size: 7.8pt;">Supabase table me amount <code class="inline-code">amount_minor BIGINT</code> (Paise) me store hota hai, jisse ₹1 paise ka bhi rounding error nahi aata.</p>
            </div>
        </div>

        <h2 class="sub-title">2. Supabase Dashboard Me Live Data Kaise Check Karein?</h2>
        <ol style="font-size: 8.2pt; margin: 4px 0 6px 18px; padding: 0; line-height: 1.45;">
            <li>Apne browser me <strong><a href="https://supabase.com/dashboard" target="_blank" style="color: #059669; font-weight: 700;">https://supabase.com/dashboard</a></strong> par jayein aur account login karein.</li>
            <li>Apna Project select karein (Project Ref ID: <code class="inline-code">dymorpzwrmvfpubgsgqb</code>).</li>
            <li>Left side menu me <strong>Table Editor</strong> par click karein.</li>
            <li>Aapko tables dikhayi dengi:
                <ul style="margin: 3px 0; padding-left: 14px;">
                    <li><strong><code class="inline-code">transactions</code>:</strong> Phone se sync hue kharche aur aamadni ki live rows.</li>
                    <li><strong><code class="inline-code">profiles</code>:</strong> Registered users ki email aur details.</li>
                    <li><strong><code class="inline-code">accounts</code>:</strong> Wallets (Cash, Bank Account, Savings) aur unka minor balance.</li>
                </ul>
            </li>
        </ol>

        <h2 class="sub-title">3. Backend .env File (Keys Kaha Hoti Hain?)</h2>
        <p>Backend folder me <code class="inline-code">backend/.env</code> file hoti hai jisme cloud keys pre-configured hain:</p>
        <pre class="code-block">
PORT=4000
NODE_ENV=development
SUPABASE_URL=https://dymorpzwrmvfpubgsgqb.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=super_secret_jwt_hs256_key_for_smart_tracker
ADMIN_API_KEY=admin_secret_key_2026
        </pre>

        <div class="card card-highlight">
            <strong>✅ Customer Advantage:</strong> Aapko yeh keys manually bharne ki koi zaroorat nahi hai. Humne sab kuch pehle se link aur test karke package kiya hai. Sirf <code class="inline-code">START_ALL.bat</code> dabate hi backend automatically database se connect ho jata hai!
        </div>
    </div>
    <div class="running-footer">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="page-number">Page 3 of 5</span>
    </div>
</div>
""")

    # PAGE 4: ANDROID STUDIO ME PROJECT KAISE OPEN KAREIN
    pages.append("""
<div class="page">
    <div class="running-header">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="tag">Page 4: Android Studio Setup</span>
    </div>
    <div class="page-content">
        <h1 class="chapter-title">🛠️ Android Studio Me Project Kaise Open Karein</h1>

        <div class="card card-warning">
            <strong>⚠️ Sabse Badi Common Galati Jo Beginners Karte Hain:</strong><br/>
            Android Studio me poora root folder open nahi karna hota! Agar aap root folder select karenge toh Gradle detect nahi hoga. Hamesha sirf <strong><code class="inline-code">android</code></strong> folder ko select karein!
        </div>

        <h2 class="sub-title">1. Step-by-Step Android Studio Open Karne Ka Tarika</h2>
        
        <p><strong><span class="badge badge-step">STEP 1</span> Android Studio Launch Karein</strong><br/>
        Apne PC me Android Studio open karein. Welcome screen par <strong>"Open"</strong> (ya <strong>File &rarr; Open</strong>) par click karein.</p>

        <p><strong><span class="badge badge-step">STEP 2</span> Sahi Folder Select Karein</strong><br/>
        Folder browse karke yaha jayein: <br/>
        <code class="inline-code">...\\divya\\android</code> &larr; <em>(Sirf is 'android' folder par click karke OK dabayein)</em>.</p>

        <p><strong><span class="badge badge-step">STEP 3</span> Gradle Sync Hone Dein (1-2 Minute)</strong><br/>
        Project khulte hi bottom right me <em>"Gradle build running..."</em> dikhega. Internet on rakhein taaki libraries verify ho sakein. Jab neeche <strong>"Gradle sync finished"</strong> green tick aa jaye, tab project compile ke liye ready hai.</p>

        <h2 class="sub-title">2. JDK 17 Configuration Check Karein</h2>
        <p>Agar kabhi Java version error aaye toh yeh 10-second setting check karein:</p>
        <ol style="font-size: 8.2pt; margin: 3px 0 6px 18px; padding: 0;">
            <li>Android Studio me <strong>File &rarr; Settings</strong> (Mac par Preferences) open karein.</li>
            <li><strong>Build, Execution, Deployment &rarr; Build Tools &rarr; Gradle</strong> par jayein.</li>
            <li><strong>Gradle JDK</strong> me select karein: <strong>"Embedded JDK 17"</strong> ya <strong>"Android Studio java runtime (jbr)"</strong>.</li>
            <li>Apply aur OK dabayein.</li>
        </ol>

        <h2 class="sub-title">3. App Run (Compile) Kaise Karein?</h2>
        <div class="grid-2">
            <div class="grid-card">
                <h4>Phone / Emulator Select Karein</h4>
                <p style="font-size: 7.8pt;">Top toolbar me device dropdown dekhein. Apna connected real phone (jaise <strong>Nova 1 5G</strong>) ya Android Emulator select karein.</p>
            </div>
            <div class="grid-card">
                <h4>Green Play Button Dabayein</h4>
                <p style="font-size: 7.8pt;">Toolbar me green color ke <strong>Play Button (Run 'app')</strong> &rarr; <code class="inline-code">Shift + F10</code> par click karein. App compile hokar phone par khul jayega!</p>
            </div>
        </div>
    </div>
    <div class="running-footer">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="page-number">Page 4 of 5</span>
    </div>
</div>
""")

    # PAGE 5: REAL PHONE USB SETUP & LOCAL NETWORK ACCESS
    pages.append("""
<div class="page">
    <div class="running-header">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="tag">Page 5: USB &amp; Real Phone</span>
    </div>
    <div class="page-content">
        <h1 class="chapter-title">📱 Real Phone Me USB Debugging &amp; Network Setup</h1>

        <p>
            Customer ya teacher ke samne physical phone par app run karke dikhana sabse convincing hota hai. Kisi bhi Android phone (jaise <strong>Nova 1 5G</strong>) ko connect karne ka full step-by-step method:
        </p>

        <h2 class="sub-title">1. Phone Me Developer Mode &amp; USB Debugging On Karna</h2>
        
        <p><strong><span class="badge badge-step">STEP A</span> Developer Options Unlock Karein</strong><br/>
        Phone ki <strong>Settings &rarr; About Phone</strong> me jayein. <strong>Build Number</strong> (kuch phones me Version) par lagataar <strong>7 baar tap karein</strong>. Message aayega: <em>"You are now a developer!"</em>.</p>

        <p><strong><span class="badge badge-step">STEP B</span> USB Debugging On Karein</strong><br/>
        Settings me wapas ja kar <strong>Additional Settings &rarr; Developer Options</strong> me jayein. Waha <strong>"USB Debugging"</strong> ka toggle ON karein.</p>

        <p><strong><span class="badge badge-step">STEP C</span> Computer Ko Authorize Karein</strong><br/>
        Phone ko USB cable se PC se connect karein. Phone screen par ek prompt aayega: <em>"Allow USB Debugging from this computer?"</em><br/>
        <strong>"Always allow from this computer"</strong> par tick mark lagayein aur <strong>OK</strong> dabayein.</p>

        <h2 class="sub-title">2. 1-Click Phone Me Install Karna (Script)</h2>
        <p>
            Developer Mode on karne ke baad aapko kisi command ki zaroorat nahi hai. Simply double-click karein:
        </p>
        <div style="background: #0f172a; color: #34d399; padding: 7px 10px; border-radius: 5px; font-weight: 700; font-family: Consolas; font-size: 8.8pt;">
            INSTALL_ANDROID_USB.bat
        </div>
        <p style="font-size: 7.8pt; margin-top: 4px;">
            Yeh script ADB ke through aapke phone me direct APK push karegi aur screen par automatic welcome splash screen khol degi!
        </p>

        <h2 class="sub-title">3. USB Tethering / Wi-Fi Par Local Server Connect Karna</h2>
        <div class="card card-highlight">
            <strong>🌐 Agar Phone Aur PC Dono Ek Hi Wi-Fi Par Hain:</strong><br/>
            PC ka Local IP address dekhein (CMD me <code class="inline-code">ipconfig</code> type karein, e.g. <code class="inline-code">192.168.1.15</code>).<br/>
            Phone me app chalate waqt backend URL automatically Render Cloud API (<code class="inline-code">https://smart-expenses-kuob.onrender.com</code>) par sync hota hai, isliye agar aap local IP configure na bhi karein tab bhi cloud sync 100% seamlessly kaam karta hai!
        </div>

        <div class="card card-warning" style="margin-top: 6px;">
            <strong>🎉 Badhai Ho! Customer Setup Poora Ho Gaya:</strong><br/>
            Aapka Smart Expenses Tracker ab physical phone par live chal raha hai. Aap offline transactions add kar sakte hain, voice se bolkar kharcha save kar sakte hain, aur website dashboard par live health monitor kar sakte hain!
        </div>
    </div>
    <div class="running-footer">
        <span>Smart Expenses Tracker &bull; Customer QuickStart Guide</span>
        <span class="page-number">Page 5 of 5</span>
    </div>
</div>
""")

    return pages

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(root_dir)
    
    html_file = os.path.join(root_dir, "customer_guide_5page.html")
    pdf_file_divya = os.path.join(root_dir, "SmartExpenses_Customer_QuickStart_Guide_5Pages.pdf")
    pdf_file_parent = os.path.join(parent_dir, "SmartExpenses_Customer_QuickStart_Guide_5Pages.pdf")
    
    print("1. Generating 5-Page Master HTML...")
    html_header = build_html()
    pages = get_pages_content()
    full_html = html_header + "".join(pages) + "\n</body>\n</html>"
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"HTML generated at: {html_file}")
    
    print("2. Rendering 5-Page PDF via Headless Chrome...")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={pdf_file_divya}",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]
    
    subprocess.run(cmd, check=True)
    
    if os.path.exists(pdf_file_divya):
        import shutil
        shutil.copy2(pdf_file_divya, pdf_file_parent)
        print(f"Copied PDF to: {pdf_file_parent}")
        
    try:
        import pymupdf
        doc = pymupdf.open(pdf_file_divya)
        print("======================================================================")
        print(f"SUCCESS! Rendered PDF Page Count: {len(doc)} Pages")
        print(f"File Size: {os.path.getsize(pdf_file_divya) / (1024*1024):.2f} MB")
        print(f"Has abdulzubair: {any('abdulzubair' in p.get_text().lower() for p in doc)}")
        print(f"Has smartexpensehelp-sketch: {any('smartexpensehelp-sketch' in p.get_text() for p in doc)}")
        print(f"Path: {pdf_file_parent}")
        print("======================================================================")
    except Exception as e:
        print("Pymupdf check error:", e)

if __name__ == "__main__":
    main()
