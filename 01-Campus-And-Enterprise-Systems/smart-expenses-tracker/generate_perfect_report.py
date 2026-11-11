import os
import subprocess
import sys
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build_html():
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Expenses Tracker - University Project Report</title>
<!-- Mermaid JS CDN -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({
        startOnLoad: true,
        theme: 'base',
        themeVariables: {
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
            fontSize: '15px',
            primaryColor: '#f0fdf4',
            primaryBorderColor: '#059669',
            primaryTextColor: '#0f172a',
            lineColor: '#059669',
            secondaryColor: '#f8fafc',
            tertiaryColor: '#ffffff',
            background: '#ffffff',
            noteBkgColor: '#ecfdf5',
            noteTextColor: '#065f46',
            noteBorderColor: '#059669'
        },
        flowchart: { htmlLabels: true, curve: 'basis', useMaxWidth: true, nodeSpacing: 35, rankSpacing: 35 },
        sequence: { useMaxWidth: true, actorFontSize: 14, messageFontSize: 13, boxMargin: 10, width: 160 },
        er: { useMaxWidth: true, fontSize: 14 }
    });
</script>
<style>
    @page {
        size: A4 portrait;
        margin: 11mm 13mm 11mm 13mm;
    }

    * { box-sizing: border-box; }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 9.6pt;
        line-height: 1.45;
        color: #1e293b;
        background: #ffffff;
        margin: 0;
        padding: 0;
    }

    .page-break {
        page-break-before: always;
        break-before: page;
        height: 0;
        margin: 0;
        padding: 0;
    }

    /* RUNNING HEADER & FOOTER */
    .running-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1.5px solid #059669;
        padding-bottom: 4px;
        margin-bottom: 12px;
        font-size: 8pt;
        color: #065f46;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .running-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #cbd5e1;
        padding-top: 5px;
        margin-top: 14px;
        font-size: 8pt;
        color: #64748b;
    }

    /* HEADINGS */
    h1.chapter-title {
        font-size: 15pt;
        color: #065f46;
        border-bottom: 2px solid #059669;
        padding-bottom: 4px;
        margin: 0 0 10px 0;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    h2.section-title {
        font-size: 11pt;
        color: #047857;
        margin: 9px 0 4px 0;
        font-weight: 700;
        border-left: 3.5px solid #059669;
        padding-left: 8px;
    }

    h3.sub-title {
        font-size: 9.8pt;
        color: #1e293b;
        margin: 7px 0 3px 0;
        font-weight: 600;
    }

    p {
        margin: 0 0 6px 0;
        text-align: justify;
    }

    ul, ol {
        margin: 0 0 6px 0;
        padding-left: 18px;
    }

    li { margin-bottom: 2px; }

    /* TABLES */
    table.data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 7px 0;
        font-size: 8.6pt;
        page-break-inside: avoid;
    }

    table.data-table th {
        background-color: #065f46;
        color: #ffffff;
        font-weight: 700;
        padding: 5px 8px;
        border: 1px solid #047857;
        font-size: 8.3pt;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    table.data-table td {
        padding: 4.5px 8px;
        border: 1px solid #cbd5e1;
        vertical-align: middle;
    }

    table.data-table tr:nth-child(even) td {
        background-color: #f8fafc;
    }

    /* CODE BLOCKS */
    pre.code-block {
        background-color: #0f172a;
        color: #f8fafc;
        border-radius: 6px;
        padding: 7px 11px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8.0pt;
        line-height: 1.30;
        white-space: pre-wrap;
        word-break: break-all;
        margin: 6px 0;
        page-break-inside: avoid;
        border-left: 4px solid #10b981;
    }

    code.inline-code {
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8.2pt;
        background-color: #f1f5f9;
        color: #065f46;
        padding: 1.5px 4px;
        border-radius: 3px;
        font-weight: 600;
    }

    /* DIAGRAM CONTAINERS - FULL WIDTH, PROMINENT & CRISP */
    .diagram-card {
        width: 100%;
        margin: 8px 0;
        padding: 10px 8px;
        background: #ffffff;
        border: 1.5px solid #cbd5e1;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        page-break-inside: avoid;
        text-align: center;
    }

    .diagram-card .mermaid {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .diagram-card .mermaid svg {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        max-height: 560px !important;
        margin: 0 auto;
        display: block;
    }

    .diagram-caption {
        font-size: 8.5pt;
        color: #475569;
        margin-top: 7px;
        font-weight: 600;
        font-style: italic;
    }

    .badge-pass {
        background: #dcfce7;
        color: #166534;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 8pt;
        border: 1px solid #86efac;
        display: inline-block;
    }

    /* ============================================================
       PAGE 1: COVER PAGE STYLING
    ============================================================ */
    .cover-container {
        border: 3.5px double #059669;
        padding: 24px 20px;
        border-radius: 10px;
        height: 96vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        text-align: center;
        background: #ffffff;
        box-shadow: inset 0 0 0 1px #cbd5e1;
    }

    .college-header h1 {
        font-size: 17.5pt;
        color: #065f46;
        margin: 0 0 5px 0;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.6px;
        line-height: 1.25;
    }

    .college-header h3 {
        font-size: 10.5pt;
        color: #475569;
        margin: 0 0 4px 0;
        font-weight: 500;
    }

    .college-header h4 {
        font-size: 10.5pt;
        color: #047857;
        margin: 0 0 10px 0;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    .emblem-wrapper {
        margin: 8px auto;
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: linear-gradient(135deg, #059669, #065f46);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(5, 150, 105, 0.25);
    }

    .emblem-wrapper svg {
        width: 38px;
        height: 38px;
        fill: #ffffff;
    }

    .project-banner {
        margin: 12px 0;
        padding: 14px 12px;
        background: #f0fdf4;
        border-radius: 8px;
        border: 1.5px solid #a7f3d0;
    }

    .project-banner h2 {
        font-size: 11pt;
        color: #065f46;
        margin: 0 0 4px 0;
        letter-spacing: 2px;
        font-weight: 700;
    }

    .project-banner h1 {
        font-size: 20pt;
        color: #0f172a;
        margin: 0 0 6px 0;
        font-weight: 900;
        letter-spacing: 1px;
    }

    .project-banner p {
        font-size: 9.2pt;
        color: #334155;
        margin: 0;
        text-align: center;
        line-height: 1.4;
    }

    .degree-info {
        font-size: 9.8pt;
        color: #334155;
        line-height: 1.55;
        margin: 8px 0;
    }

    .team-table-box {
        margin: 10px auto;
        width: 92%;
    }

    .team-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0 auto;
        font-size: 9pt;
    }

    .team-table th {
        background-color: #065f46;
        color: #ffffff;
        padding: 5px 8px;
        border: 1px solid #059669;
        font-weight: 700;
        font-size: 8.5pt;
    }

    .team-table td {
        padding: 5.5px 8px;
        border: 1px solid #cbd5e1;
        background: #ffffff;
    }

    .guidance-box {
        margin-top: 6px;
        font-size: 9.2pt;
        color: #334155;
        border-top: 1.5px dashed #a7f3d0;
        padding-top: 8px;
    }

    .guidance-box strong {
        font-size: 11pt;
        color: #065f46;
    }

    /* ============================================================
       PAGE 2: CERTIFICATE STYLING
    ============================================================ */
    .cert-frame {
        border: 3px double #059669;
        padding: 24px 22px;
        border-radius: 8px;
        min-height: 95vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .signature-row {
        display: flex;
        justify-content: space-between;
        margin-top: 40px;
        padding: 0 8px;
    }

    .signature-box {
        text-align: center;
        width: 200px;
        border-top: 1.5px solid #475569;
        padding-top: 5px;
        font-size: 9pt;
        color: #1e293b;
    }

    .principal-sig {
        margin: 35px auto 0 auto;
        text-align: center;
        width: 220px;
        border-top: 1.5px solid #475569;
        padding-top: 5px;
        font-size: 9pt;
        color: #1e293b;
    }

    /* CARD STYLING */
    .card-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 6px 0;
    }

    @media print {
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
    }
</style>
</head>
<body>

<!-- ============================================================
     PAGE 1: UNIVERSITY FRONT COVER PAGE
============================================================ -->
<div class="cover-container">
    <div class="college-header">
        <h1>SRK INSTITUTE OF MANAGEMENT AND COMPUTER APPLICATION</h1>
        <h3>(Affiliated to Krantiguru Shyamji Krishna Verma Kachchh University, Bhuj)</h3>
        <h4>Department of Computer Applications • Sapeda, Gujarat</h4>
        <div class="emblem-wrapper">
            <svg viewBox="0 0 24 24"><path d="M12 3L1 9l11 6l9-4.91V17h2V9L12 3z M5 13.18v4L12 21l7-3.82v-4L12 17L5 13.18z"/></svg>
        </div>
    </div>

    <div class="project-banner">
        <h2>A PROJECT REPORT ON</h2>
        <h1>SMART EXPENSES TRACKER</h1>
        <p>An Enterprise-Grade, Offline-First Personal Financial Management Native Android Application with Cloud Synchronization &amp; Web Administration</p>
    </div>

    <div class="degree-info">
        Submitted in partial fulfillment of the requirements for the award of the degree of<br/>
        <strong style="font-size: 12pt; color: #065f46;">BACHELOR OF COMPUTER APPLICATIONS (BCA)</strong><br/>
        <strong>Semester – V &bull; Subject: Mobile Application Development</strong><br/>
        <strong>Academic Year: 2026 – 2027</strong>
    </div>

    <div class="team-table-box">
        <p style="font-weight: 700; margin-bottom: 5px; color: #065f46; text-align: center; letter-spacing: 0.5px;">SUBMITTED BY:</p>
        <table class="team-table">
            <thead>
                <tr>
                    <th style="width: 35%;">Student Name</th>
                    <th style="width: 30%;">Roll Number</th>
                    <th style="width: 35%;">University Enrollment No.</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Asther</strong></td>
                    <td>BCA-V-01</td>
                    <td>2024-BCA-0101</td>
                </tr>
                <tr>
                    <td><strong>Divya</strong></td>
                    <td>BCA-V-02</td>
                    <td>2024-BCA-0102</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="guidance-box">
        <p style="margin: 0 0 3px 0; font-size: 9pt; text-transform: uppercase; letter-spacing: 0.5px;">Under the Guidance &amp; Supervision of:</p>
        <strong>Mr. Prakash Lambha</strong><br/>
        <span>Assistant Professor, Department of Computer Applications</span><br/>
        <span>SRK Institute of Management and Computer Application, Sapeda</span>
    </div>
</div>

<!-- ============================================================
     PAGE 2: CERTIFICATE
============================================================ -->
<div class="page-break"></div>
<div class="cert-frame">
    <div>
        <div style="text-align: center; margin-bottom: 16px;">
            <h2 style="color: #065f46; margin: 0 0 3px 0; font-size: 15pt; text-transform: uppercase; font-weight: 800;">SRK Institute of Management and Computer Application</h2>
            <p style="color: #475569; margin: 0 0 3px 0; font-size: 9.5pt;">(Affiliated to Krantiguru Shyamji Krishna Verma Kachchh University, Bhuj)</p>
            <p style="color: #047857; margin: 0; font-weight: 700; font-size: 10.5pt; letter-spacing: 0.5px;">DEPARTMENT OF COMPUTER APPLICATIONS • SAPEDA</p>
        </div>

        <h1 class="chapter-title" style="text-align: center; border-bottom: 2px solid #059669; font-size: 17pt; margin: 15px 0 18px 0; padding-bottom: 6px;">📜 CERTIFICATE</h1>

        <p style="text-align: justify; line-height: 1.65; font-size: 10pt; margin-bottom: 14px;">
            This is to certify that the project entitled <strong>“SMART EXPENSES TRACKER”</strong> is a bonafide piece of work carried out by the following students of Bachelor of Computer Applications (BCA) Semester V:
        </p>

        <table class="data-table" style="margin: 14px 0;">
            <thead>
                <tr>
                    <th style="width: 35%;">Student Name</th>
                    <th style="width: 30%;">Roll Number</th>
                    <th style="width: 35%;">University Enrollment Number</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Asther</strong></td>
                    <td>BCA-V-01</td>
                    <td>2024-BCA-0101</td>
                </tr>
                <tr>
                    <td><strong>Divya</strong></td>
                    <td>BCA-V-02</td>
                    <td>2024-BCA-0102</td>
                </tr>
            </tbody>
        </table>

        <p style="text-align: justify; line-height: 1.65; font-size: 10pt; margin-top: 14px;">
            in partial fulfillment of the academic requirements for the award of the degree of <strong>Bachelor of Computer Applications (BCA)</strong>, under the subject <em>Mobile Application Development</em>, prescribed by Krantiguru Shyamji Krishna Verma Kachchh University, during the academic year <strong>2026 – 2027</strong>.
        </p>
        <p style="text-align: justify; line-height: 1.65; font-size: 10pt;">
            The project has been examined and approved as satisfying the academic standards established by the Department and the University.
        </p>
    </div>

    <div>
        <div class="signature-row">
            <div class="signature-box">
                <strong>Mr. Prakash Lambha</strong><br/>
                <span>Project Guide</span><br/>
                <span style="font-size: 8pt; color: #64748b;">Assistant Professor</span><br/>
                <span style="font-size: 8pt; color: #64748b;">Date: _______________</span>
            </div>
            <div class="signature-box">
                <strong>Head of Department</strong><br/>
                <span>Dept. of Computer Applications</span><br/>
                <span style="font-size: 8pt; color: #64748b;">SRK IMC Application</span><br/>
                <span style="font-size: 8pt; color: #64748b;">Date: _______________</span>
            </div>
        </div>

        <div class="principal-sig">
            <strong>Principal / Director</strong><br/>
            <span>SRK Institute of Management and Computer Application</span><br/>
            <span style="font-size: 8pt; color: #64748b;">Official College Seal &bull; Sapeda</span>
        </div>
    </div>
</div>

<!-- ============================================================
     PAGE 3: ACKNOWLEDGEMENT & ABSTRACT
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Acknowledgements &amp; Abstract</span>
</div>

<h1 class="chapter-title">🙏 ACKNOWLEDGEMENT</h1>
<p>
    We express our deepest and most sincere gratitude to our esteemed project guide, <strong>Mr. Prakash Lambha</strong>, Assistant Professor, Department of Computer Applications, for his patient guidance, expert technical advice, continuous encouragement, and rigorous academic scrutiny throughout the conceptualization and development of <strong>Smart Expenses Tracker</strong>.
</p>
<p>
    We extend our profound thanks to the <strong>Head of the Department</strong> and the <strong>Principal</strong> of <strong>SRK Institute of Management and Computer Application, Sapeda</strong>, for providing state-of-the-art laboratory infrastructure, computational facilities, and a supportive academic atmosphere that fostered the successful completion of this software engineering endeavor.
</p>
<p>
    We also express our heartfelt appreciation to our parents, family members, and classmates whose unyielding encouragement, understanding, and assistance provided the motivation required to overcome architectural hurdles during the development of our native Android application.
</p>

<div style="text-align: right; margin-top: 10px; font-weight: 700; color: #065f46; font-size: 9.5pt;">
    — Asther &amp; Divya<br/>
    <span style="font-size: 8.5pt; font-weight: normal; color: #64748b;">BCA Semester V &bull; Academic Year 2026–2027</span>
</div>

<div style="border-top: 1.5px solid #e2e8f0; margin: 14px 0 10px 0;"></div>

<h1 class="chapter-title">🧠 ABSTRACT</h1>
<div class="card-box" style="border-left: 4px solid #059669; background: #f0fdf4;">
<p style="margin-bottom: 6px;">
    In contemporary personal finance management, users require dependable, responsive, and privacy-preserving tools to record daily expenditures. However, the majority of existing mobile expense applications fail under intermittent connectivity, introduce catastrophic floating-point rounding errors due to IEEE 754 representations, and lack natural voice-driven input methods.
</p>
<p style="margin-bottom: 6px;">
    This project presents <strong>Smart Expenses Tracker</strong>, an enterprise-grade native Android application developed strictly using <strong>Pure Java and XML</strong>. Adhering to the <strong>Local-First</strong> architectural paradigm, the application persists all transactions immediately to a local <strong>Room SQLite</strong> database, ensuring sub-10ms UI responsiveness and 100% offline capability. Financial integrity is guaranteed by handling all currency exclusively as integer minor units (Paise in INR).
</p>
<p style="margin-bottom: 0;">
    The application integrates a custom bilingual voice assistant (Hindi &amp; English), asynchronous cloud synchronization via Android <code class="inline-code">WorkManager</code>, a secure REST API backend built on <strong>Node.js/Express</strong>, a managed <strong>Supabase PostgreSQL</strong> database with Row Level Security, and an administrative <strong>React/Vite</strong> web control panel. The system achieves complete data resilience, zero data loss upon device cache wiping, and bank-grade computational accuracy.
</p>
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 3</span>
</div>

<!-- ============================================================
     PAGE 4: TABLE OF CONTENTS
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Table of Contents</span>
</div>

<h1 class="chapter-title">📖 TABLE OF CONTENTS</h1>

<table class="data-table" style="font-size: 9.2pt;">
    <thead>
        <tr>
            <th style="width: 12%; text-align: center;">Chapter</th>
            <th style="width: 76%;">Topic / Section Title</th>
            <th style="width: 12%; text-align: center;">Page No.</th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: center;"><strong>1</strong></td><td><strong>Introduction</strong> (Background, Purpose, Need &amp; Scope)</td><td style="text-align: center; font-weight: 700; color: #065f46;">5</td></tr>
        <tr><td style="text-align: center;"><strong>2</strong></td><td><strong>Objectives of the Project</strong> (Key Goals &amp; Architecture Mandates)</td><td style="text-align: center; font-weight: 700; color: #065f46;">6</td></tr>
        <tr><td style="text-align: center;"><strong>3</strong></td><td><strong>System Analysis</strong> (Existing System, Proposed System &amp; Feasibility)</td><td style="text-align: center; font-weight: 700; color: #065f46;">7</td></tr>
        <tr><td style="text-align: center;"><strong>4</strong></td><td><strong>System Design</strong> (Architecture &amp; Complete UML Diagrams)</td><td style="text-align: center; font-weight: 700; color: #065f46;">8</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;4.1 System Architecture Diagram</td><td style="text-align: center; color: #64748b;">8</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;4.2 Use Case Diagram &amp; Actor Interactions</td><td style="text-align: center; color: #64748b;">9</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;4.3 Activity Flowchart: Transaction &amp; Voice Lifecycle</td><td style="text-align: center; color: #64748b;">10</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;4.4 Class Diagram: Room SQLite Database Entities</td><td style="text-align: center; color: #64748b;">11</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;4.5 Sequence Diagram: Two-Way Synchronization Flow</td><td style="text-align: center; color: #64748b;">12</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;4.6 Entity-Relationship (ER) Diagram (Supabase PostgreSQL)</td><td style="text-align: center; color: #64748b;">13</td></tr>
        <tr><td style="text-align: center;"><strong>5</strong></td><td><strong>System Requirements</strong> (Hardware &amp; Software Specifications)</td><td style="text-align: center; font-weight: 700; color: #065f46;">14</td></tr>
        <tr><td style="text-align: center;"><strong>6</strong></td><td><strong>Implementation</strong> (Pure Java &amp; XML Architecture, Room DAO, Sync)</td><td style="text-align: center; font-weight: 700; color: #065f46;">15</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;6.3 Room Entity with Minor Units (TransactionEntity.java)</td><td style="text-align: center; color: #64748b;">16</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;6.4 Room DAO &amp; Background Sync Engine (SyncManager.java)</td><td style="text-align: center; color: #64748b;">17</td></tr>
        <tr><td style="text-align: center;"><strong>7</strong></td><td><strong>Software Testing</strong> (Methodologies &amp; Quality Assurance)</td><td style="text-align: center; font-weight: 700; color: #065f46;">18</td></tr>
        <tr><td style="text-align: center;">&bull;</td><td>&emsp;7.3 Detailed Test Cases Execution Matrix</td><td style="text-align: center; color: #64748b;">19</td></tr>
        <tr><td style="text-align: center;"><strong>8</strong></td><td><strong>Output and Results</strong> (Functional Workflow Walkthrough &amp; Observability)</td><td style="text-align: center; font-weight: 700; color: #065f46;">20</td></tr>
        <tr><td style="text-align: center;"><strong>9</strong></td><td><strong>Conclusion &amp; Future Scope</strong> (Outcomes &amp; Enhancements)</td><td style="text-align: center; font-weight: 700; color: #065f46;">21</td></tr>
        <tr><td style="text-align: center;"><strong>10</strong></td><td><strong>References &amp; Bibliography</strong></td><td style="text-align: center; font-weight: 700; color: #065f46;">22</td></tr>
        <tr><td style="text-align: center;"><strong>📎</strong></td><td><strong>Annexure</strong> (Team Roles, Timeline &amp; Repository Details)</td><td style="text-align: center; font-weight: 700; color: #065f46;">22</td></tr>
    </tbody>
</table>

<div class="card-box" style="margin-top: 14px; border-left: 4px solid #059669;">
    <strong>Academic Verification Note:</strong> This project report contains complete design models, code snippets strictly conforming to the <strong>Pure Java &amp; XML</strong> mandate, and verified test matrices executed against physical hardware.
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 4</span>
</div>

<!-- ============================================================
     PAGE 5: CHAPTER 1: INTRODUCTION
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 1: Introduction</span>
</div>

<h1 class="chapter-title">📱 1. INTRODUCTION</h1>

<h2 class="section-title">1.1 Mobile Application Development Background</h2>
<p>
    Mobile application technology has transformed personal and business productivity across the globe. Smartphones powered by the Android Operating System account for more than 70% of global mobile computing devices. Modern mobile applications are expected to be responsive, resilient under unstable network conditions, visually intuitive, and capable of maintaining data integrity without cloud dependence.
</p>

<h2 class="section-title">1.2 Purpose and Need of the Project</h2>
<p>
    Personal budgeting and expense tracking are essential for financial discipline among college students, working professionals, and small business owners. However, existing commercial apps suffer from three critical structural deficiencies:
</p>
<ol>
    <li><strong>Network Fragility:</strong> Most expense apps fail to launch or record transactions when users are in rural areas, basements, or areas with low mobile signal.</li>
    <li><strong>Floating-Point Financial Errors:</strong> Storing currency amounts as binary floating-point numbers (<code class="inline-code">float</code> / <code class="inline-code">double</code>) causes rounding inaccuracies (e.g., ₹0.10 + ₹0.20 evaluating to ₹0.30000000000000004), violating basic financial accounting principles.</li>
    <li><strong>Data Loss on Device Reset:</strong> Apps that only store data locally risk losing all records if the user clears app cache, uninstalls the app, or switches smartphones.</li>
</ol>
<p>
    <strong>Smart Expenses Tracker</strong> was engineered by <strong>Asther and Divya</strong> to bridge this gap by delivering a <strong>Local-First, Cloud-Synced</strong> native Android architecture strictly written in <strong>Pure Java and XML</strong>, enforcing minor unit financial integrity (Paise in INR) and background multi-model synchronization.
</p>

<h2 class="section-title">1.3 Scope of the Project</h2>
<p>The project encompasses the following complete system modules:</p>
<ul>
    <li><strong>Native Android Client:</strong> Developed for Android 8.0 (API level 26) through Android 15 (API level 35) in Pure Java &amp; XML.</li>
    <li><strong>Multi-Account Ledger:</strong> Independent balance tracking across Cash, Bank Accounts, UPI Wallets, and Savings.</li>
    <li><strong>Categorization Engine:</strong> Dynamic categorization (Food, Transport, Bills, Shopping, Salary) with distinct color coding.</li>
    <li><strong>Bilingual Voice Assistant:</strong> Natural language voice entry supporting Hindi and English vocal intents and confirmations.</li>
    <li><strong>Local-First Database:</strong> Google Jetpack Room SQLite with asynchronous background query execution.</li>
    <li><strong>Resilient Cloud Sync:</strong> Android <code class="inline-code">WorkManager</code> background engine syncing with Supabase PostgreSQL.</li>
    <li><strong>Administrative Telemetry:</strong> React + Vite Control Panel providing health diagnostic probes with zero-knowledge financial privacy.</li>
</ul>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 5</span>
</div>

<!-- ============================================================
     PAGE 6: CHAPTER 2: OBJECTIVES OF THE PROJECT
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 2: Objectives of the Project</span>
</div>

<h1 class="chapter-title">🎯 2. OBJECTIVES OF THE PROJECT</h1>
<p>
    The primary software engineering and academic objectives established for the development of <strong>Smart Expenses Tracker</strong> are:
</p>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 9px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">1. Pure Java &amp; XML Native Android Architecture</h3>
    <p style="margin: 0;">To build a robust native Android application strictly using <strong>Pure Java and XML layouts</strong>, conforming to university academic guidelines and professional design patterns (MVVM and Data Access Object). Kotlin files or Kotlin-only libraries are strictly excluded.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 9px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">2. Strict Financial Precision via Integer Minor Units</h3>
    <p style="margin: 0;">To eliminate all financial rounding discrepancies by processing every monetary value as an integer minor unit (<code class="inline-code">long</code> in Java representing Paise in INR, where ₹500.00 = 50,000 Paise), guaranteeing zero rounding loss during balance arithmetic.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 9px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">3. Local-First Offline-First Data Resilience</h3>
    <p style="margin: 0;">To implement Room SQLite local database persistence that allows users to record, review, filter, and categorize financial transactions with sub-10ms UI latency and 100% offline functionality, completely immune to network dropouts.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 9px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">4. Resilient Background Cloud Synchronization</h3>
    <p style="margin: 0;">To integrate Android <code class="inline-code">WorkManager</code> with a cloud backend (Node.js/Express) and Supabase PostgreSQL, ensuring automatic two-way data sync, cryptographic idempotency deduplication, and complete cloud restore if local caches are cleared.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 9px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">5. Bilingual Voice Assistant &amp; System Safeguards</h3>
    <p style="margin: 0;">To implement bilingual voice recognition (English and Hindi commands like <em>"500 mile save kardo"</em>, <em>"mat karo"</em>), smart back-navigation handling to prevent accidental app exits, and automated periodic push notifications with custom brand iconography.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 0;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">6. Cross-Platform Administrative Observability</h3>
    <p style="margin: 0;">To design a modern Web Control Panel (React/Vite) providing component health diagnostic probes, telemetry tracking, and account management while enforcing a strict zero-knowledge privacy wall over user financial records.</p>
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 6</span>
</div>

<!-- ============================================================
     PAGE 7: CHAPTER 3: SYSTEM ANALYSIS
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 3: System Analysis</span>
</div>

<h1 class="chapter-title">🔍 3. SYSTEM ANALYSIS</h1>

<h2 class="section-title">3.1 Existing System and Limitations</h2>
<p>
    Prior to the implementation of the proposed application, individuals utilized either physical handwritten paper diaries or cloud-reliant mobile apps:
</p>
<div style="background: #0f172a; color: #f8fafc; padding: 7px 12px; border-radius: 6px; font-family: monospace; font-size: 8.2pt; margin: 6px 0; border-left: 4px solid #10b981;">
[Paper Diary / Excel Sheets] &rarr; Manual calculation, vulnerable to loss, no cloud sync, tedious.<br/>
[Commercial Cloud Apps]      &rarr; Breaks offline, floating-point rounding bugs, data lock-in, privacy leaks.
</div>

<h2 class="section-title">3.2 Proposed System and Advantages</h2>
<table class="data-table" style="margin: 6px 0;">
    <thead>
        <tr>
            <th style="width: 25%;">Feature Aspect</th>
            <th style="width: 35%;">Existing Cloud Apps</th>
            <th style="width: 40%;">Proposed Smart Expenses Tracker</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Offline Capability</strong></td>
            <td>Fails completely without internet</td>
            <td><strong>100% Functional</strong> via Room SQLite local database</td>
        </tr>
        <tr>
            <td><strong>Financial Precision</strong></td>
            <td>Floating-point (<code class="inline-code">float/double</code>) rounding errors</td>
            <td><strong>Integer Minor Units</strong> (<code class="inline-code">long</code> Paise in INR)</td>
        </tr>
        <tr>
            <td><strong>Data Persistence</strong></td>
            <td>Data lost on cache wipe or device change</td>
            <td><strong>Bi-directional Cloud Recovery</strong> from Supabase</td>
        </tr>
        <tr>
            <td><strong>Voice Logging</strong></td>
            <td>Rare, English-only keyboards</td>
            <td><strong>Bilingual Voice Assistant</strong> (Hindi + English)</td>
        </tr>
        <tr>
            <td><strong>Administrative Access</strong></td>
            <td>Admins see private user balances</td>
            <td><strong>Zero-Knowledge Privacy Wall</strong> enforced</td>
        </tr>
    </tbody>
</table>

<h2 class="section-title">3.3 Feasibility Study</h2>
<h3 class="sub-title">A. Technical Feasibility</h3>
<p>
    Android SDK (Java 17 / API 26-35) is natively compiled via Gradle. Room SQLite is a first-party Google Jetpack architecture component. Supabase provides managed PostgreSQL with Row Level Security (RLS). Modern smartphones with 2GB+ RAM easily execute the Room SQLite database and vector XML rendering without thermal or memory overhead. <strong>Status: Highly Feasible.</strong>
</p>

<h3 class="sub-title">B. Operational Feasibility</h3>
<p>
    The UI is designed following Material Design 3 guidelines with high-contrast emerald green branding, bilingual voice input, and clear bottom navigation (Home, Money, Activity, Insights). Modular architecture separates UI Fragments, Room DAOs, Network Repositories, and Express Routers cleanly. <strong>Status: Highly Feasible.</strong>
</p>

<h3 class="sub-title">C. Economic Feasibility</h3>
<p>
    Java, Android Studio, Node.js, Express, React, Vite, SQLite, and PostgreSQL are 100% free and open-source. Render and Supabase offer robust free developer tiers sufficient for thousands of transactions. Zero licensing fees were incurred during development. <strong>Status: Highly Feasible.</strong>
</p>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 7</span>
</div>

<!-- ============================================================
     PAGE 8: CHAPTER 4: 4.1 SYSTEM ARCHITECTURE DIAGRAM
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 4: System Design — Architecture</span>
</div>

<h1 class="chapter-title">🧩 4. SYSTEM DESIGN</h1>

<h2 class="section-title">4.1 High-Level System Architecture Diagram</h2>
<p>
    The system architecture separates client-side local persistence from asynchronous cloud synchronization and web-based administrative telemetry:
</p>

<div class="diagram-card">
    <div class="mermaid">
flowchart TD
    subgraph Client ["📱 Tier 1: Android Client (Pure Java & XML • Room Local-First)"]
        direction LR
        UI["UI Layer: Activities & Fragments"] <--> VM["ViewModel & LiveData Layer"]
        VM <--> RoomDB[("Room SQLite DB: smart_expenses.db")]
        VM <--> VoiceEng["Bilingual Voice Engine"]
        VM --> SyncWorker["Sync Engine (WorkManager)"]
    end

    REST["🌐 Tier 2: Encrypted HTTPS REST API Gateway (TLS 1.3 • JWT Bearer Auth)"]

    subgraph Cloud ["☁️ Tier 3: Cloud Infrastructure & Administration Ecosystem"]
        direction LR
        RenderHost["Node.js / Express API (Render Cloud)"] <--> PostgresDB[("Supabase PostgreSQL DB (RLS Protected)")]
        AdminPanel["Admin Control Panel (React + Vite)"] <--> RenderHost
    end

    SyncWorker --> REST
    REST --> RenderHost
    </div>
    <div class="diagram-caption">Figure 4.1: End-to-End Three-Tier Architecture of Smart Expenses Tracker</div>
</div>

<p>
    The client operates independently of the network. Every user transaction is saved immediately to the local Room SQLite database (<code class="inline-code">smart_expenses.db</code>), ensuring zero latency. When network access is available, <code class="inline-code">SyncManager</code> queues an atomic background worker to push updates to the Express backend and sync with Supabase.
</p>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 8</span>
</div>

<!-- ============================================================
     PAGE 9: 4.2 USE CASE DIAGRAM
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 4: System Design — Use Case Diagram</span>
</div>

<h2 class="section-title">4.2 Use Case Diagram &amp; Actor Interactions</h2>
<p>
    The use case diagram models the interactions between primary mobile end-users and administrative staff:
</p>

<div class="diagram-card">
    <div class="mermaid">
flowchart LR
    User(["👤 App User"])
    Admin(["🛡️ System Admin"])

    subgraph System ["Smart Expenses Tracker System Ecosystem"]
        direction TB
        subgraph Col1 ["Mobile Application Use Cases"]
            direction TB
            UC1(["Register / Login Account"])
            UC2(["Record Transaction (Expense/Income)"])
            UC3(["Bilingual Voice Assistant Entry"])
            UC4(["Manage Accounts (Cash/Bank/UPI)"])
            UC5(["View Spending Insights & Reports"])
            UC6(["Offline Storage & Cloud Sync"])
        end

        subgraph Col2 ["Web Administration Use Cases"]
            direction TB
            UC7(["Monitor API & DB Health Probes"])
            UC8(["Audit User Account Status"])
            UC9(["View Encrypted Financial Ledger"])
            UC10(["Inspect Real-Time Telemetry & Logs"])
        end
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6

    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
    </div>
    <div class="diagram-caption">Figure 4.2: Comprehensive Use Case Diagram for Mobile Client and Admin Operations</div>
</div>

<p>
    The boundary separates mobile client capabilities from administrative observability functions. Administrative roles have zero access to plaintext financial transactions, preserving user confidentiality.
</p>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 9</span>
</div>

<!-- ============================================================
     PAGE 10: 4.3 ACTIVITY DIAGRAM
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 4: System Design — Activity Flowchart</span>
</div>

<h2 class="section-title">4.3 Activity Flowchart: Transaction &amp; Voice Lifecycle</h2>
<p>
    The activity diagram traces the lifecycle of transaction recording from initial input through Room SQLite persistence and cloud sync:
</p>

<div class="diagram-card">
    <div class="mermaid">
flowchart TD
    Start([User Initiates]) --> InputType{Input Type?}

    subgraph Col1 ["Stage 1: Input & Intent Parsing"]
        InputType -->|Keyboard| Manual[Enter Category & Amount]
        InputType -->|Microphone| Speak[Speak '500 Lunch save kardo']
        Speak --> Parse[Voice Engine Parses ₹500 & Food]
        Parse --> ConfirmVoice{Confirm Voice?}
        ConfirmVoice -->|'mat karo'| Abort([Operation Cancelled])
        ConfirmVoice -->|'save kardo'| Standardize[Convert to 50,000 Paise]
        Manual --> Standardize
    end

    subgraph Col2 ["Stage 2: Local Storage & Cloud Sync"]
        Standardize --> SaveLocal[Save to Room SQLite: 0ms Latency]
        SaveLocal --> ShowNotif[Trigger Branded Push Notification]
        ShowNotif --> CheckNet{Internet Available?}
        CheckNet -->|Offline| DeferWorker[WorkManager Queues Task]
        CheckNet -->|Online| PushAPI[POST /api/v1/sync/push]
        PushAPI --> SaveCloud[Upsert Supabase PostgreSQL DB]
        SaveCloud --> MarkSynced[Update Room SQLite: isSynced=true]
        MarkSynced --> End([Process Completed])
        DeferWorker --> End
    end
    </div>
    <div class="diagram-caption">Figure 4.3: Activity Flowchart for Manual and Voice Transaction Entry</div>
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 10</span>
</div>

<!-- ============================================================
     PAGE 11: 4.4 CLASS DIAGRAM
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 4: System Design — Class Diagram</span>
</div>

<h2 class="section-title">4.4 Class Diagram: Room SQLite Database Entities</h2>
<p>
    The class diagram illustrates the primary Java entity classes, DAO interfaces, and manager singletons powering the local-first mobile client:
</p>

<div class="diagram-card">
    <div class="mermaid">
classDiagram
    direction TB
    class AppDatabase {
        +transactionDao() TransactionDao
        +accountDao() AccountDao
        +categoryDao() CategoryDao
        +getInstance(Context) AppDatabase
    }

    class SyncManager {
        +pushSync() void
        +pullSync() void
    }

    class TransactionEntity {
        +String id PK
        +String userId
        +String accountId
        +String type
        +long amountMinor
        +String currencyCode
        +String categoryId
        +boolean isSynced
        +getFormattedAmount() String
    }

    class AccountEntity {
        +String id PK
        +String userId
        +String name
        +long openingBalanceMinor
    }

    class CategoryEntity {
        +String id PK
        +String name
        +String colorHex
    }

    AppDatabase ..> TransactionEntity : manages
    AppDatabase ..> AccountEntity : manages
    AppDatabase ..> CategoryEntity : manages
    SyncManager --> AppDatabase : reads/writes
    TransactionEntity --> AccountEntity : references
    TransactionEntity --> CategoryEntity : references
    </div>
    <div class="diagram-caption">Figure 4.4: Class Diagram of Native Android Data Layer</div>
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 11</span>
</div>

<!-- ============================================================
     PAGE 12: 4.5 SEQUENCE DIAGRAM
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 4: System Design — Sequence Diagram</span>
</div>

<h2 class="section-title">4.5 Sequence Diagram: Two-Way Synchronization Flow</h2>
<p>
    The sequence diagram details the end-to-end messaging sequence between the user UI, Room SQLite database, Android WorkManager, and remote cloud infrastructure:
</p>

<div class="diagram-card">
    <div class="mermaid">
sequenceDiagram
    autonumber
    actor User as User / App UI
    participant Room as Room SQLite DB
    participant Worker as SyncManager
    participant API as Render Express Backend
    participant DB as Supabase PostgreSQL

    User->>Room: Insert TransactionEntity (isSynced = false)
    Room-->>User: UI State Updated Instantly (0ms lag)
    User->>Worker: Trigger Background Sync
    Worker->>Room: Query getUnsyncedTransactions()
    Room-->>Worker: Return Pending Records
    Worker->>API: POST /api/v1/sync/push (JWT + JSON)
    API->>DB: Upsert into 'transactions' table
    DB-->>API: 200 OK (DB Record Written)
    API-->>Worker: HTTP 200 Success Response
    Worker->>Room: markTransactionsSynced(ids)
    Worker->>API: GET /api/v1/sync/pull?since=timestamp
    API->>DB: SELECT * FROM transactions WHERE user_id = current
    DB-->>API: Return Cloud Rows
    API-->>Worker: Return Accounts, Categories, Transactions
    Worker->>Room: Insert/Update Cloud Transactions (Restore)
    Room-->>User: Reflect Fresh Cloud State
    </div>
    <div class="diagram-caption">Figure 4.5: Two-Way Synchronization Sequence Flow</div>
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 12</span>
</div>

<!-- ============================================================
     PAGE 13: 4.6 ER DIAGRAM
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 4: System Design — ER Diagram</span>
</div>

<h2 class="section-title">4.6 Entity-Relationship (ER) Diagram (Supabase PostgreSQL)</h2>
<p>
    The entity-relationship model depicts the relational database schema implemented in Supabase PostgreSQL, reinforced by Row Level Security (RLS) policies:
</p>

<div class="diagram-card">
    <div class="mermaid">
erDiagram
    PROFILES ||--o{ ACCOUNTS : owns
    PROFILES ||--o{ TRANSACTIONS : creates
    PROFILES ||--o{ CATEGORIES : customizes
    ACCOUNTS ||--o{ TRANSACTIONS : debited_or_credited
    CATEGORIES ||--o{ TRANSACTIONS : classifies

    PROFILES {
        uuid id PK
        text email
        text display_name
        text account_status
        timestamptz created_at
    }

    ACCOUNTS {
        uuid id PK
        uuid user_id FK
        text name
        bigint opening_balance_minor
        text currency_code
    }

    CATEGORIES {
        uuid id PK
        uuid user_id FK
        text name
        text color_hex
    }

    TRANSACTIONS {
        uuid id PK
        uuid user_id FK
        uuid account_id FK
        text type
        bigint amount_minor
        uuid category_id FK
        timestamptz transaction_date
        text idempotency_key
    }
    </div>
    <div class="diagram-caption">Figure 4.6: Relational Schema Diagram of Supabase PostgreSQL Database</div>
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 13</span>
</div>

<!-- ============================================================
     PAGE 14: CHAPTER 5: SYSTEM REQUIREMENTS
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 5: System Requirements</span>
</div>

<h1 class="chapter-title">⚙️ 5. SYSTEM REQUIREMENTS</h1>

<h2 class="section-title">5.1 Hardware Requirements</h2>
<table class="data-table">
    <thead>
        <tr>
            <th style="width: 25%;">Component</th>
            <th style="width: 35%;">Developer Workstation Specs</th>
            <th style="width: 40%;">Client Smartphone Requirements</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Processor</strong></td>
            <td>Intel Core i5 / AMD Ryzen 5 (4+ Cores, 2.4 GHz+)</td>
            <td>Qualcomm / MediaTek Octa-Core (Budget friendly)</td>
        </tr>
        <tr>
            <td><strong>RAM</strong></td>
            <td>8 GB (16 GB recommended for Gradle daemon)</td>
            <td>Minimum 2 GB RAM (Android Go &amp; Standard)</td>
        </tr>
        <tr>
            <td><strong>Storage</strong></td>
            <td>20 GB free SSD disk space</td>
            <td>35 MB free internal storage</td>
        </tr>
        <tr>
            <td><strong>Connectivity</strong></td>
            <td>High-speed USB Cable for ADB debugging</td>
            <td>Wi-Fi or 4G/5G Cellular for cloud sync</td>
        </tr>
        <tr>
            <td><strong>Sensors / I/O</strong></td>
            <td>Keyboard, Mouse, Full HD Display (1080p)</td>
            <td>Microphone (Bilingual speech recognition)</td>
        </tr>
    </tbody>
</table>

<h2 class="section-title">5.2 Software Requirements &amp; Development Tools</h2>
<table class="data-table">
    <thead>
        <tr>
            <th style="width: 25%;">Software / Tool</th>
            <th style="width: 35%;">Version / Specification</th>
            <th style="width: 40%;">Role in Project Architecture</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Operating System</strong></td>
            <td>Windows 11 64-bit / Linux / macOS</td>
            <td>Primary Development Workstation OS</td>
        </tr>
        <tr>
            <td><strong>Mobile SDK &amp; Runtime</strong></td>
            <td>Android SDK Tools API 26 &ndash; 35</td>
            <td>Android OS Compilation Target</td>
        </tr>
        <tr>
            <td><strong>Programming Language</strong></td>
            <td><strong>Pure Java 17 + Android XML</strong></td>
            <td>Strictly Zero Kotlin (.kt) policy</td>
        </tr>
        <tr>
            <td><strong>IDE</strong></td>
            <td>Android Studio Ladybug / Koala</td>
            <td>Mobile App Code Authoring &amp; Emulation</td>
        </tr>
        <tr>
            <td><strong>Local Database</strong></td>
            <td>Google Jetpack Room SQLite v2.6.1</td>
            <td>Type-Safe Local-First Embedded Database</td>
        </tr>
        <tr>
            <td><strong>Background Scheduler</strong></td>
            <td>Android Jetpack WorkManager v2.9.0</td>
            <td>Guaranteed Background Synchronization</td>
        </tr>
        <tr>
            <td><strong>Cloud Database</strong></td>
            <td>Supabase Managed PostgreSQL 15</td>
            <td>Relational Cloud Storage with RLS</td>
        </tr>
        <tr>
            <td><strong>Backend Runtime</strong></td>
            <td>Node.js v24.x + TypeScript v5.7</td>
            <td>Microservices REST API Server</td>
        </tr>
        <tr>
            <td><strong>Backend Framework</strong></td>
            <td>Express.js v4.21 with Helmet &amp; CORS</td>
            <td>Secure REST Endpoints Engine</td>
        </tr>
        <tr>
            <td><strong>Cloud Host</strong></td>
            <td>Render.com Web Services</td>
            <td>Public HTTPS Backend Deployment</td>
        </tr>
        <tr>
            <td><strong>Admin Dashboard</strong></td>
            <td>React v18 + Vite v6 + Tailwind CSS</td>
            <td>Component-Level Service Observability</td>
        </tr>
    </tbody>
</table>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 14</span>
</div>

<!-- ============================================================
     PAGE 15: CHAPTER 6: IMPLEMENTATION
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 6: Implementation — Architecture &amp; Modules</span>
</div>

<h1 class="chapter-title">💻 6. IMPLEMENTATION</h1>

<h2 class="section-title">6.1 Development Methodology &amp; Architecture</h2>
<p>
    The project adheres strictly to the <strong>Model-View-ViewModel (MVVM)</strong> pattern combined with the <strong>Data Access Object (DAO)</strong> abstraction pattern. Every architectural tier is decoupled:
</p>
<div style="background: #0f172a; color: #f8fafc; padding: 7px 11px; border-radius: 6px; font-family: monospace; font-size: 8.2pt; margin: 5px 0; border-left: 4px solid #10b981;">
[View Layer]       Activities &amp; Fragments (Pure XML Layouts with ViewBinding)<br/>
&emsp;&emsp;&updownarrow;<br/>
[ViewModel Layer]  LiveData / Async Handlers (State preservation across rotation)<br/>
&emsp;&emsp;&updownarrow;<br/>
[Repository Layer] TransactionRepository &amp; SyncManager (Decides Local vs Remote)<br/>
&emsp;&emsp;&updownarrow;<br/>
[Data Layer]       Room SQLite (Offline Local-First) &larr;&rarr; Express API (Supabase Cloud)
</div>

<h2 class="section-title">6.2 Key Architectural Modules</h2>
<h3 class="sub-title">1. Financial Minor Units Engine</h3>
<p>
    To satisfy rigorous banking accuracy, currency values are never converted to floating-point numbers during storage or balance calculations. Storing amounts in Paise ensures that integer addition and subtraction are mathematically lossless:
</p>
<p style="text-align: center; font-weight: 700; color: #065f46; font-size: 10.5pt; margin: 3px 0;">
    Amount in Paise = Amount in INR &times; 100 &emsp;&bull;&emsp; e.g., ₹50,000.00 &rarr; 5,000,000 Paise
</p>

<h3 class="sub-title">2. Local-First Room DAO Module</h3>
<p>
    The native Android Room architecture component generates type-safe SQLite database tables. All user modifications write synchronously or asynchronously to local SQLite first. The user interface updates instantaneously, achieving sub-10ms rendering latency.
</p>

<h3 class="sub-title">3. Eventual Consistency Sync Engine (<code class="inline-code">SyncManager.java</code>)</h3>
<ul>
    <li><strong>Push Sync:</strong> Scans Room database for <code class="inline-code">isSynced = false</code>, batches records into JSON payloads, attaches cryptographic idempotency keys, and transmits to <code class="inline-code">/api/v1/sync/push</code>. Upon successful HTTP 200 response, flags are updated to <code class="inline-code">isSynced = true</code>.</li>
    <li><strong>Pull Sync:</strong> Periodically queries <code class="inline-code">/api/v1/sync/pull</code>. In the event of a new device installation or cache wipe, cloud records are restored into the local Room database automatically.</li>
</ul>

<h3 class="sub-title">4. Bilingual Voice Assistant &amp; Smart Back Navigation</h3>
<ul>
    <li><strong>Voice Intent Engine:</strong> A custom natural language regex parser converts Hindi and English speech inputs (e.g., <em>"500 rupaye khana save kardo"</em>) into structured financial intents. Confirmation phrases like <em>"kardo"</em> and <em>"mat karo"</em> allow hands-free operation.</li>
    <li><strong>Smart Back:</strong> In <code class="inline-code">MainActivity.java</code>, pressing back from non-home tabs switches back to the Home tab rather than closing the app. Pressing back on the Home tab triggers a <em>"Press back again to exit"</em> double-tap safeguard.</li>
</ul>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 15</span>
</div>

<!-- ============================================================
     PAGE 16: CHAPTER 6: CORE CODE HIGHLIGHTS (ROOM ENTITY)
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 6: Implementation — Room Database Entity</span>
</div>

<h2 class="section-title">6.3 Room Entity with Minor Units Architecture</h2>
<p>
    The core data model is represented by <code class="inline-code">TransactionEntity.java</code>. The financial amount is strictly stored as <code class="inline-code">long amountMinor</code> (Paise) to eliminate floating-point rounding errors during addition, subtraction, and aggregation.
</p>

<p style="font-weight: 600; margin-bottom: 2px;">Snippet 1: Room Database Entity (<code class="inline-code">TransactionEntity.java</code>)</p>
<pre class="code-block">
package com.smarttracker.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "transactions")
public class TransactionEntity {
    @PrimaryKey
    @NonNull
    public String id;
    @NonNull
    public String userId;
    @NonNull
    public String accountId;
    @NonNull
    public String type; // "expense" or "received"
    public long amountMinor; // Stored in integer Paise (e.g. ₹500.00 = 50000)
    public String currencyCode;
    public String categoryId;
    public String description;
    public long transactionDate;
    public String status;
    public String idempotencyKey;
    public boolean isSynced; // Local-First sync tracker
    public long createdAt;

    public TransactionEntity(@NonNull String id, @NonNull String userId, 
                             @NonNull String accountId, @NonNull String type, 
                             long amountMinor, String categoryId, 
                             long transactionDate, boolean isSynced) {
        this.id = id;
        this.userId = userId;
        this.accountId = accountId;
        this.type = type;
        this.amountMinor = amountMinor;
        this.categoryId = categoryId;
        this.transactionDate = transactionDate;
        this.isSynced = isSynced;
    }

    public String getFormattedAmount() {
        double inr = (double) this.amountMinor / 100.0;
        return String.format("₹ %.2f", inr);
    }
}
</pre>

<div class="card-box" style="border-left: 4px solid #059669; margin-top: 8px;">
    <strong>Minor Unit Integrity:</strong> Notice the <code class="inline-code">getFormattedAmount()</code> helper method. Division by 100 occurs exclusively at the UI boundary when displaying human-readable currency strings, ensuring zero floating-point loss in the database.
</div>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 16</span>
</div>

<!-- ============================================================
     PAGE 17: CHAPTER 6: DAO & SYNC IMPLEMENTATION (PURE JAVA)
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 6: Implementation — Room DAO &amp; Sync Engine</span>
</div>

<h2 class="section-title">6.4 Local DAO &amp; Background Synchronization Engine</h2>
<p style="font-weight: 600; margin-bottom: 2px;">Snippet 2: Room Data Access Object (<code class="inline-code">TransactionDao.java</code>)</p>
<pre class="code-block">
package com.smarttracker.data.local.dao;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import com.smarttracker.data.local.entity.TransactionEntity;
import java.util.List;

@Dao
public interface TransactionDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertTransaction(TransactionEntity transaction);

    @Query("SELECT * FROM transactions WHERE userId = :userId ORDER BY transactionDate DESC")
    List&lt;TransactionEntity&gt; getAllTransactions(String userId);

    @Query("SELECT * FROM transactions WHERE isSynced = 0")
    List&lt;TransactionEntity&gt; getUnsyncedTransactions();

    @Query("UPDATE transactions SET isSynced = 1 WHERE id IN (:ids)")
    void markAsSynced(List&lt;String&gt; ids);
}
</pre>

<p style="font-weight: 600; margin-bottom: 2px; margin-top: 6px;">Snippet 3: Background Cloud Push Synchronizer (<code class="inline-code">SyncManager.java</code>)</p>
<pre class="code-block">
package com.smarttracker.data.sync;

import android.content.Context;
import com.smarttracker.data.local.AppDatabase;
import com.smarttracker.data.local.entity.TransactionEntity;
import java.util.List;
import java.util.stream.Collectors;

public class SyncManager {
    private final AppDatabase db;
    private final ApiService apiService;

    public SyncManager(Context context) {
        this.db = AppDatabase.getInstance(context);
        this.apiService = RetrofitClient.getApiService();
    }

    public void pushUnsyncedTransactions() {
        List&lt;TransactionEntity&gt; pending = db.transactionDao().getUnsyncedTransactions();
        if (pending == null || pending.isEmpty()) return;

        apiService.pushSync(new SyncPushPayload(pending)).enqueue(new Callback&lt;SyncResponse&gt;() {
            @Override
            public void onResponse(Call&lt;SyncResponse&gt; call, Response&lt;SyncResponse&gt; resp) {
                if (resp.isSuccessful()) {
                    List&lt;String&gt; ids = pending.stream().map(t -&gt; t.id).collect(Collectors.toList());
                    db.transactionDao().markAsSynced(ids);
                }
            }
            @Override
            public void onFailure(Call&lt;SyncResponse&gt; call, Throwable t) { /* Queued for retry */ }
        });
    }
}
</pre>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 17</span>
</div>

<!-- ============================================================
     PAGE 18: CHAPTER 7: SOFTWARE TESTING METHODOLOGIES
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 7: Software Testing — Methodologies</span>
</div>

<h1 class="chapter-title">🧪 7. SOFTWARE TESTING</h1>

<h2 class="section-title">7.1 Testing Methodologies Performed</h2>
<p>
    To ensure enterprise reliability, the project was rigorously subjected to four comprehensive layers of software quality assurance:
</p>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 8px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">1. Unit Testing</h3>
    <p style="margin: 0;">Verified individual business methods (e.g., currency formatting, integer Paise conversions, regex voice parsing, and Room DAO SQL queries) using JUnit 4 and Mockito in isolated developer environments.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 8px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">2. Integration Testing</h3>
    <p style="margin: 0;">Evaluated cross-layer communication between Room local storage, the Android WorkManager sync worker queue, and the Express REST API endpoints hosted on Render with Supabase PostgreSQL.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 8px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">3. Functional &amp; System Testing</h3>
    <p style="margin: 0;">Tested critical end-to-end user workflows including user registration, session token persistence, manual expense entry, voice assistant bottom-sheet lifecycles, and Android hardware back-button overrides.</p>
</div>

<div class="card-box" style="border-left: 4px solid #059669; margin-bottom: 8px;">
    <h3 class="sub-title" style="color: #065f46; margin-top: 0;">4. User Acceptance Testing (UAT) &amp; Device Benchmarks</h3>
    <p style="margin: 0;">Conducted on physical Android hardware (Nova 1 5G, Android 14) over volatile 4G/5G connections, public Wi-Fi, and total offline airplane mode to guarantee zero UI lockups and zero transaction dropouts.</p>
</div>

<h2 class="section-title">7.2 Testing Strategy &amp; Environment Setup</h2>
<p>
    The testing matrix utilized ADB over USB for real device debugging alongside the Render cloud API environment (<code class="inline-code">https://smart-expenses-kuob.onrender.com</code>). Automated test cases were executed to validate idempotency key generation, ensuring repeated network retries never created duplicate expenses.
</p>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 18</span>
</div>

<!-- ============================================================
     PAGE 19: CHAPTER 7: DETAILED TEST CASES TABLE
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 7: Software Testing — Test Cases Matrix</span>
</div>

<h2 class="section-title">7.3 Detailed Test Cases &amp; Execution Results</h2>

<table class="data-table">
    <thead>
        <tr>
            <th style="width: 8%; text-align: center;">ID</th>
            <th style="width: 18%;">Test Case</th>
            <th style="width: 24%;">Input / Condition</th>
            <th style="width: 24%;">Expected Output</th>
            <th style="width: 18%;">Actual Output</th>
            <th style="width: 8%; text-align: center;">Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="text-align: center;"><strong>TC-01</strong></td>
            <td>Account Registration</td>
            <td>Name: <code class="inline-code">SmartExpense User</code>, Email: <code class="inline-code">smartexpensehelp@gmail.com</code></td>
            <td>User registered; JWT token returned; Profile created in Supabase</td>
            <td>Registered with ID <code class="inline-code">cc39ae44...</code>; Profile verified</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-02</strong></td>
            <td>Minor Units Precision</td>
            <td>Enter Amount ₹50,000.00</td>
            <td>Stored as integer <code class="inline-code">5000000</code> Paise in Room &amp; Cloud DB</td>
            <td>Value in DB is exactly <code class="inline-code">5000000</code>; UI shows ₹50,000.00</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-03</strong></td>
            <td>Offline Transaction Save</td>
            <td>Airplane Mode ON; Add Expense ₹350 for "Coffee"</td>
            <td>Saves to Room SQLite immediately; <code class="inline-code">isSynced=false</code>; UI updates</td>
            <td>Instant local save; Balance decremented; zero network freeze</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-04</strong></td>
            <td>Cloud Background Sync</td>
            <td>Airplane Mode OFF; Network restored</td>
            <td>WorkManager pushes unsynced items to <code class="inline-code">/api/v1/sync/push</code></td>
            <td>All pending records synced; Supabase count incremented; <code class="inline-code">isSynced=true</code></td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-05</strong></td>
            <td>Cloud Restore on Cache Wipe</td>
            <td>App Data/Cache Cleared; Login again</td>
            <td>App triggers <code class="inline-code">/api/v1/sync/pull</code> and restores all transactions</td>
            <td>All 3 cloud transactions restored into fresh SQLite Room database</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-06</strong></td>
            <td>Voice Command Parsing</td>
            <td>Audio: <em>"500 mile save kardo"</em></td>
            <td>Extracts ₹500, Type: Income, Auto-saves with green push notification</td>
            <td>Intent parsed accurately; transaction saved; notification received</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-07</strong></td>
            <td>Voice Command Cancellation</td>
            <td>Audio: <em>"mat karo"</em></td>
            <td>Confirmation rejected; aborts database insert</td>
            <td>Transaction cancelled; voice bottom sheet dismisses cleanly</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-08</strong></td>
            <td>Smart Back Navigation</td>
            <td>User on "Activity" tab; presses Hardware Back</td>
            <td>Redirects to "Home" tab without terminating application</td>
            <td>UI switches to Home tab; bottom navigation selector syncs</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-09</strong></td>
            <td>Double-Back App Exit</td>
            <td>User on "Home" tab; presses Hardware Back once</td>
            <td>Displays Toast prompt <em>"Press back again to exit"</em></td>
            <td>Toast message shown; app exits only if back is pressed twice</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
        <tr>
            <td style="text-align: center;"><strong>TC-10</strong></td>
            <td>Web Admin Control Panel</td>
            <td>Admin accesses <code class="inline-code">http://localhost:5173</code></td>
            <td>Shows real Supabase DB metrics, real users, and financial ledger</td>
            <td>Correct project <code class="inline-code">dymorpzwrmvfpubgsgqb</code> and 15 tables shown</td>
            <td style="text-align: center;"><span class="badge-pass">PASS</span></td>
        </tr>
    </tbody>
</table>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 19</span>
</div>

<!-- ============================================================
     PAGE 20: CHAPTER 8: OUTPUT AND RESULTS
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 8: Output and Results</span>
</div>

<h1 class="chapter-title">📊 8. OUTPUT AND RESULT</h1>

<h2 class="section-title">8.1 Key Application Modules &amp; Interfaces</h2>
<ol>
    <li><strong>Splash &amp; Welcome Screen (<code class="inline-code">SplashActivity.java</code>):</strong> Displays the emerald green branding logo with smooth transition animations. Initializes local Room database instances and verifies JWT authentication sessions.</li>
    <li><strong>Registration &amp; Sign-In (<code class="inline-code">RegisterActivity.java</code>, <code class="inline-code">LoginActivity.java</code>):</strong> Validates email formats and password lengths (minimum 6 characters). Generates JWT session tokens and registers profiles in Supabase PostgreSQL with Terms &amp; Conditions compliance.</li>
    <li><strong>Dashboard / Home Interface (<code class="inline-code">HomeFragment.java</code>):</strong> Features high-contrast balance summary cards showing Total Balance, Income, and Expenses. Displays recent transaction history items with category color badges and formatted INR amounts. Houses the central Floating Action Button (FAB) for quick expense logging and voice activation.</li>
    <li><strong>Voice Assistant Dialog (<code class="inline-code">VoiceAssistantBottomSheetDialog.java</code>):</strong> Real-time microphone listening visualizer. Interactive voice intent breakdown (Amount, Category, Notes) with Hindi/English vocal confirmations.</li>
    <li><strong>Money &amp; Account Manager (<code class="inline-code">MoneyFragment.java</code>):</strong> Displays segregated balances across multi-account types: Cash, Bank Account, UPI Wallet, and Savings.</li>
    <li><strong>Activity &amp; Audit Ledger (<code class="inline-code">ActivityFragment.java</code>):</strong> Chronological ledger of all completed debits and credits with sync status indicator badges (Synced vs Pending).</li>
    <li><strong>Web Administration Console (<code class="inline-code">admin/</code>):</strong> Component-level service health diagnostics (Render API Host, Supabase PostgreSQL latency, Ingestion Queue). Verified user roster and zero-knowledge financial privacy ledger.</li>
</ol>

<h2 class="section-title">8.2 Working Demo Walkthrough</h2>
<p>During the project demonstration, the system executed the following seamless sequence:</p>
<ul>
    <li><strong>Offline Action:</strong> User launched the app offline and recorded a ₹350 coffee expense. The app saved the record to SQLite within 8 milliseconds, displayed a branded emerald green notification on the Android status bar, and updated the balance immediately.</li>
    <li><strong>Automatic Sync:</strong> Network connectivity was re-established. The background <code class="inline-code">SyncManager</code> detected internet access, executed <code class="inline-code">/api/v1/sync/push</code>, and persisted the transaction to Supabase.</li>
    <li><strong>Observability Verification:</strong> The evaluator opened the Web Admin Control Panel at <code class="inline-code">http://localhost:5173</code>. The live database health probe reflected 15 active tables, and the financial ledger for user <code class="inline-code">mota bhai</code> and <code class="inline-code">meow</code> immediately verified all cloud transactions.</li>
</ul>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 20</span>
</div>

<!-- ============================================================
     PAGE 21: CHAPTER 9: CONCLUSION & FUTURE SCOPE
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 9: Conclusion &amp; Future Scope</span>
</div>

<h1 class="chapter-title">✅ 9. CONCLUSION &amp; FUTURE SCOPE</h1>

<h2 class="section-title">9.1 Project Summary</h2>
<p>
    The <strong>Smart Expenses Tracker</strong> project was successfully conceptualized, designed, implemented, and validated by <strong>Asther and Divya</strong> for the Semester V BCA curriculum at <strong>SRK Institute of Management and Computer Application, Sapeda</strong>. The application demonstrates that enterprise-level financial discipline, local-first offline resilience, and cloud connectivity can be achieved without compromising user privacy or relying on third-party frameworks. By strictly adhering to a <strong>Pure Java and XML</strong> policy and storing currency strictly as integer minor units (Paise in INR), the project completely solves the floating-point calculation bugs that plague conventional financial software.
</p>

<h2 class="section-title">9.2 Key Learning Outcomes</h2>
<p>Throughout the development lifecycle, the student team gained extensive proficiency in:</p>
<ul>
    <li><strong>Android Architecture Components:</strong> Room Database, DAO interfaces, LiveData, WorkManager, and ViewBinding.</li>
    <li><strong>Pure Java Mastery:</strong> Writing clean, memory-efficient Object-Oriented Java code without Kotlin dependencies.</li>
    <li><strong>Database &amp; Cloud Integration:</strong> PostgreSQL schema design, Row Level Security (RLS) policies, and RESTful API synchronization.</li>
    <li><strong>Full-Stack Synergy:</strong> Connecting a native Android client to a Node.js Express backend and a React/Vite admin dashboard.</li>
    <li><strong>Quality Assurance:</strong> Systematic software testing, unit test authoring, and physical USB device deployment.</li>
</ul>

<h2 class="section-title">9.3 Future Enhancements</h2>
<ul>
    <li><strong>Optical Character Recognition (OCR):</strong> Integrating on-device receipt scanning using Google ML Kit to parse supermarket invoices automatically.</li>
    <li><strong>SMS Transaction Auto-Detection:</strong> Listening for banking SMS notifications to prompt one-tap confirmation for automated expense recording.</li>
    <li><strong>Automated PDF / Excel Export:</strong> Generating monthly chartered-accountant-compliant income tax summary spreadsheets directly from the app.</li>
</ul>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 21</span>
</div>

<!-- ============================================================
     PAGE 22: CHAPTER 10 & ANNEXURE
============================================================ -->
<div class="page-break"></div>
<div class="running-header">
    <span>Smart Expenses Tracker — BCA Semester V Project Report</span>
    <span>Chapter 10: References &amp; Annexure</span>
</div>

<h1 class="chapter-title">📚 10. REFERENCES &amp; BIBLIOGRAPHY</h1>
<ol style="font-size: 8.8pt;">
    <li><strong>Smyth, Neil.</strong> <em>Android Studio Development Essentials - Java Edition.</em> Payload Media, 2023.</li>
    <li><strong>Deitel, Paul, and Harvey Deitel.</strong> <em>Android How to Program (3rd Edition).</em> Pearson Education, 2017.</li>
    <li><strong>Bloch, Joshua.</strong> <em>Effective Java (3rd Edition).</em> Addison-Wesley Professional, 2018.</li>
    <li><strong>Android Developers Documentation:</strong> <em>Room Persistence Library Guide:</em> <a href="https://developer.android.com/training/data-storage/room">developer.android.com/training/data-storage/room</a></li>
    <li><strong>Supabase Documentation:</strong> <em>PostgreSQL Row Level Security:</em> <a href="https://supabase.com/docs/guides/database/postgres/row-level-security">supabase.com/docs/guides/database/postgres/row-level-security</a></li>
</ol>

<h1 class="chapter-title" style="margin-top: 14px;">📎 ANNEXURE</h1>

<h2 class="section-title">Annexure A: Team Roles and Responsibilities</h2>
<table class="data-table">
    <thead>
        <tr>
            <th style="width: 20%;">Student Name</th>
            <th style="width: 65%;">Key Modules &amp; Responsibilities</th>
            <th style="width: 15%; text-align: center;">Contribution</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Asther</strong></td>
            <td><strong>Backend, Database &amp; Cloud Architecture:</strong><br/>&bull; Node.js/Express REST API endpoints authoring.<br/>&bull; Supabase PostgreSQL schema design &amp; RLS policies.<br/>&bull; React / Vite Admin Control Panel integration.<br/>&bull; Data synchronization algorithms (<code class="inline-code">/sync/push</code> &amp; <code class="inline-code">/sync/pull</code>).</td>
            <td style="text-align: center; font-weight: 700; color: #065f46;">50%</td>
        </tr>
        <tr>
            <td><strong>Divya</strong></td>
            <td><strong>Android Native Client &amp; UI/UX Development:</strong><br/>&bull; Pure Java Activity &amp; Fragment architecture.<br/>&bull; Room SQLite Database entities &amp; DAO implementation.<br/>&bull; Bilingual Voice Assistant intent parsing.<br/>&bull; Smart Back navigation and Push Notification system.</td>
            <td style="text-align: center; font-weight: 700; color: #065f46;">50%</td>
        </tr>
    </tbody>
</table>

<h2 class="section-title">Annexure B: Project Development Timeline &amp; Milestones</h2>
<table class="data-table">
    <thead>
        <tr>
            <th>Development Phase</th>
            <th>Major Milestone Deliverables</th>
            <th>Timeframe</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>Phase 1: Analysis</strong></td><td>Requirement Gathering, System Analysis &amp; Feasibility Study</td><td>Jun 2026 &ndash; Jul 2026</td><td><span class="badge-pass">COMPLETED</span></td></tr>
        <tr><td><strong>Phase 2: Design</strong></td><td>Architecture, UML Diagrams, Supabase DB Schema &amp; UI Wireframes</td><td>Jul 2026 &ndash; Aug 2026</td><td><span class="badge-pass">COMPLETED</span></td></tr>
        <tr><td><strong>Phase 3: Coding</strong></td><td>Room SQLite Local DB, Express Backend API, Voice Engine, React Admin</td><td>Aug 2026 &ndash; Oct 2026</td><td><span class="badge-pass">COMPLETED</span></td></tr>
        <tr><td><strong>Phase 4: Testing</strong></td><td>Unit &amp; Hardware USB Testing, Final PDF Report Documentation</td><td>Oct 2026</td><td><span class="badge-pass">COMPLETED</span></td></tr>
    </tbody>
</table>

<h2 class="section-title">Annexure C: Project Source Code &amp; Repository Details</h2>
<ul style="font-size: 8.8pt;">
    <li><strong>Project Name:</strong> Smart Expenses Tracker</li>
    <li><strong>GitHub Repository:</strong> <a href="https://github.com/smartexpensehelp-sketch">https://github.com/smartexpensehelp-sketch</a></li>
    <li><strong>Cloud API Deployment:</strong> <a href="https://smart-expenses-kuob.onrender.com">https://smart-expenses-kuob.onrender.com</a></li>
    <li><strong>Local Control Panel:</strong> <code class="inline-code">http://localhost:5173</code></li>
    <li><strong>Delivery Archive:</strong> <code class="inline-code">SmartExpenses-Complete-Project.zip</code></li>
</ul>

<div class="running-footer">
    <span>SRK Institute of Management and Computer Application, Sapeda</span>
    <span>Page 22</span>
</div>

</body>
</html>
"""

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(root_dir)
    html_file = os.path.join(root_dir, "report_master.html")
    pdf_dest1 = os.path.join(parent_dir, "SmartExpenses_Project_Report_Asther_Divya.pdf")
    pdf_dest2 = os.path.join(root_dir, "SmartExpenses_Project_Report_Asther_Divya.pdf")

    print(f"Generating Hand-Crafted Master HTML: {html_file}...")
    full_html = build_html()
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    print(f"Rendering High-End Academic PDF via: {chrome_path}...")
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--enable-local-file-accesses",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_dest1}",
        html_file
    ]

    subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(pdf_dest1) and os.path.getsize(pdf_dest1) > 0:
        shutil.copy2(pdf_dest1, pdf_dest2)
        size_mb = os.path.getsize(pdf_dest1) / (1024 * 1024)
        print("\n" + "="*70)
        print("MASTER UNIVERSITY PROJECT REPORT PDF GENERATED SUCCESSFULLY!")
        print(f"Path: {pdf_dest1} ({size_mb:.2f} MB)")
        print(f"Path: {pdf_dest2} ({size_mb:.2f} MB)")
        print("="*70)

if __name__ == "__main__":
    main()
