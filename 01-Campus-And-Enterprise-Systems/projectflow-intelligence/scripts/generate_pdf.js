// scripts/generate_pdf.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { marked } = require('marked');

console.log('Generating master PDF report...');

const mdPath = path.join(__dirname, '..', 'PROJECTFLOW_MASTER_ARCHITECTURE_AND_CODE_BIBLE.md');
const htmlTempPath = path.join(__dirname, '..', 'report_temp.html');
const pdfOutputPath = path.join(__dirname, '..', 'PROJECTFLOW_MASTER_ARCHITECTURE_AND_CODE_BIBLE.pdf');
const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

if (!fs.existsSync(mdPath)) {
  console.error(`Markdown file not found: ${mdPath}`);
  process.exit(1);
}

const markdownContent = fs.readFileSync(mdPath, 'utf8');
const htmlBody = marked.parse(markdownContent);

const completeHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ProjectFlow Intelligence — Master Architecture & Code Bible</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    @page {
      size: A4;
      margin: 20mm 18mm 20mm 18mm;
      @bottom-right {
        content: counter(page);
      }
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.65;
      color: #292D28;
      background-color: #FFFFFF;
      margin: 0;
      padding: 0;
    }

    h1, h2, h3, h4, h5, h6 {
      color: #1C1917;
      font-weight: 700;
      page-break-after: avoid;
    }

    h1 {
      font-size: 22pt;
      border-bottom: 2px solid #56664C;
      padding-bottom: 8px;
      margin-top: 36px;
      margin-bottom: 16px;
      page-break-before: always;
    }

    h1:first-of-type {
      page-break-before: avoid;
      margin-top: 0;
    }

    h2 {
      font-size: 16pt;
      border-bottom: 1px solid #E2E0D8;
      padding-bottom: 6px;
      margin-top: 26px;
      margin-bottom: 12px;
    }

    h3 {
      font-size: 13pt;
      margin-top: 20px;
      margin-bottom: 8px;
      color: #56664C;
    }

    h4 {
      font-size: 11pt;
      margin-top: 16px;
      margin-bottom: 6px;
    }

    p, li {
      color: #3B3F38;
      text-align: justify;
    }

    ul, ol {
      padding-left: 24px;
      margin-top: 6px;
      margin-bottom: 12px;
    }

    li {
      margin-bottom: 5px;
    }

    pre {
      background-color: #F8F7F2;
      border: 1px solid #E2E0D8;
      border-radius: 6px;
      padding: 12px 14px;
      overflow-x: auto;
      font-family: 'JetBrains Mono', Consolas, "Courier New", monospace;
      font-size: 8.5pt;
      line-height: 1.45;
      page-break-inside: avoid;
      color: #1F241D;
    }

    code {
      font-family: 'JetBrains Mono', Consolas, "Courier New", monospace;
      font-size: 9pt;
      background-color: #F4F2E9;
      color: #56664C;
      padding: 2px 5px;
      border-radius: 4px;
      border: 1px solid #E2E0D8;
    }

    pre code {
      background-color: transparent;
      padding: 0;
      border: none;
      color: inherit;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      margin-bottom: 18px;
      font-size: 9pt;
      page-break-inside: avoid;
    }

    th, td {
      border: 1px solid #DCD9CF;
      padding: 7px 10px;
      text-align: left;
    }

    th {
      background-color: #F4F2E9;
      color: #292D28;
      font-weight: 700;
    }

    tr:nth-child(even) {
      background-color: #FAFAF7;
    }

    blockquote {
      border-left: 4px solid #56664C;
      background-color: #F4F2E9;
      margin: 14px 0;
      padding: 10px 16px;
      border-radius: 0 6px 6px 0;
      font-style: italic;
    }

    hr {
      border: 0;
      height: 1px;
      background-color: #E2E0D8;
      margin: 24px 0;
    }

    a {
      color: #56664C;
      text-decoration: none;
      font-weight: 600;
    }

    .badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 8pt;
      font-weight: 700;
      text-transform: uppercase;
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
console.log('Temporary HTML file created at: ' + htmlTempPath);

console.log('Rendering PDF via Headless Edge...');
const edgeCmd = `"${edgePath}" --headless --disable-gpu --print-to-pdf-no-header --print-to-pdf="${pdfOutputPath}" "${htmlTempPath}"`;

try {
  execSync(edgeCmd, { stdio: 'inherit' });
  console.log('SUCCESS! PDF generated successfully at:');
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
