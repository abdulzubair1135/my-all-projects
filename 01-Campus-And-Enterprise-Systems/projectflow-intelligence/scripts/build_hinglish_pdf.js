// scripts/build_hinglish_pdf.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { marked } = require('marked');

console.log('Building Hinglish Architecture & Code Bible Report in PDF...');

const mdPath = path.join(__dirname, '..', 'PROJECTFLOW_MASTER_HINGLISH_ARCHITECTURE_REPORT.md');
const htmlTempPath = path.join(__dirname, '..', 'reports', 'hinglish_report_temp.html');
const pdfOutputPath = path.join(__dirname, '..', 'reports', 'ProjectFlow_Master_Architecture_Report_Hinglish.pdf');
const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

if (!fs.existsSync(mdPath)) {
  console.error(`Markdown source file not found: ${mdPath}`);
  process.exit(1);
}

const markdownContent = fs.readFileSync(mdPath, 'utf8');
const htmlBody = marked.parse(markdownContent);

const completeHtml = `<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <title>ProjectFlow Intelligence — Master Architecture & Engineering Report (Hinglish)</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    @page {
      size: A4;
      margin: 18mm 16mm 18mm 16mm;
      @bottom-right {
        content: counter(page);
      }
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.6;
      color: #292D28;
      background-color: #FFFFFF;
      margin: 0;
      padding: 0;
    }

    .cover-page {
      page-break-after: always;
      display: flex;
      flex-direction: column;
      justify-content: center;
      min-height: 85vh;
      padding: 40px;
      background: linear-gradient(145deg, #F9F8F5 0%, #EFECE4 100%);
      border: 3px solid #56664C;
      border-radius: 12px;
      margin-bottom: 30px;
    }

    .cover-title {
      font-size: 28pt;
      font-weight: 800;
      color: #292D28;
      margin-bottom: 8px;
      line-height: 1.2;
    }

    .cover-subtitle {
      font-size: 15pt;
      font-weight: 600;
      color: #56664C;
      margin-bottom: 24px;
    }

    .cover-meta {
      font-size: 10pt;
      color: #5A6258;
      line-height: 1.8;
      margin-top: 30px;
      border-top: 2px dashed #C2BEB0;
      padding-top: 20px;
    }

    h1, h2, h3, h4, h5, h6 {
      color: #1C1917;
      font-weight: 700;
      page-break-after: avoid;
    }

    h1 {
      font-size: 20pt;
      color: #292D28;
      border-bottom: 2.5px solid #56664C;
      padding-bottom: 8px;
      margin-top: 36px;
      margin-bottom: 16px;
      page-break-before: always;
    }

    h2 {
      font-size: 15pt;
      color: #485640;
      border-left: 4px solid #56664C;
      padding-left: 10px;
      margin-top: 28px;
      margin-bottom: 12px;
    }

    h3 {
      font-size: 12.5pt;
      color: #292D28;
      margin-top: 20px;
      margin-bottom: 8px;
    }

    p, li {
      color: #374151;
      font-size: 10pt;
    }

    strong {
      color: #111827;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      font-size: 9pt;
      page-break-inside: auto;
    }

    tr {
      page-break-inside: avoid;
      page-break-after: auto;
    }

    th, td {
      border: 1px solid #D1D5DB;
      padding: 7px 10px;
      text-align: left;
      vertical-align: top;
    }

    th {
      background-color: #56664C;
      color: #FFFFFF;
      font-weight: 600;
    }

    tr:nth-child(even) {
      background-color: #F9FAFB;
    }

    pre, code {
      font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
      font-size: 8.5pt;
    }

    pre {
      background-color: #1F2937;
      color: #F3F4F6;
      padding: 12px 14px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 14px 0;
      border: 1px solid #374151;
      page-break-inside: avoid;
    }

    code {
      background-color: #F3F4F6;
      color: #B91C1C;
      padding: 1.5px 4px;
      border-radius: 3px;
    }

    pre code {
      background-color: transparent;
      color: #E5E7EB;
      padding: 0;
    }

    blockquote {
      border-left: 4px solid #56664C;
      background-color: #F4F6F2;
      padding: 10px 14px;
      margin: 14px 0;
      border-radius: 0 6px 6px 0;
    }

    .badge {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 8pt;
      font-weight: 700;
    }

    .badge-green { background: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; }
    .badge-amber { background: #FFF8E1; color: #F57F17; border: 1px solid #FFECB3; }
    .badge-red { background: #FFEBEE; color: #C62828; border: 1px solid #FFCDD2; }
  </style>
</head>
<body>
  ${htmlBody}
</body>
</html>`;

fs.writeFileSync(htmlTempPath, completeHtml, 'utf8');
console.log('Temporary HTML file generated at:', htmlTempPath);

console.log('Rendering PDF via Headless Edge engine...');
const edgeCmd = `"${edgePath}" --headless=new --disable-gpu --run-all-compositor-stages-before-draw --print-to-pdf-no-header --print-to-pdf="${pdfOutputPath}" "${htmlTempPath}"`;

try {
  execSync(edgeCmd, { stdio: 'inherit' });
  console.log('SUCCESS! Master PDF generated successfully at:');
  console.log(pdfOutputPath);

  if (fs.existsSync(htmlTempPath)) {
    fs.unlinkSync(htmlTempPath);
  }

  const stats = fs.statSync(pdfOutputPath);
  console.log(`PDF File Size: ${(stats.size / (1024 * 1024)).toFixed(2)} MB (${stats.size} bytes)`);
} catch (err) {
  console.error('Failed to generate PDF:', err.message);
  process.exit(1);
}
