document.addEventListener('DOMContentLoaded', () => {
  // Tab Switching
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');

      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      document.getElementById(targetTab).classList.add('active');

      if (targetTab === 'devices-tab') loadDevices();
      if (targetTab === 'timeline-tab') { loadTimeline(); loadStoragePanelBackedFiles(); loadAppUsageTrackerPanel(); }
      if (targetTab === 'phone-explorer-tab') loadRemoteDevicesDropdown();
      if (targetTab === 'files-tab') loadFiles('');
    });
  });


  // Initial Load
  loadDevices();
  loadStats();
  loadRemoteDevicesDropdown();
  loadAppUsageTrackerPanel();

  // Auto Refresh Devices Status & Dropdown every 4s
  setInterval(() => {
    loadDevices();
    loadRemoteDevicesDropdown();
  }, 4000);

  // Refresh Button
  document.getElementById('refresh-devices-btn').addEventListener('click', loadDevices);

  // Timeline Filters
  document.getElementById('timeline-filter-btn').addEventListener('click', loadTimeline);

  // File Explorer & Phone Explorer State
  let currentSubpath = '';
  let selectedFiles = new Set();
  let lastExploredPhoneData = null;

  // Save Phone Storage Directory Structure JSON
  document.getElementById('export-phone-structure-btn').addEventListener('click', () => {
    if (!lastExploredPhoneData || !lastExploredPhoneData.files) {
      alert('Explore a phone directory first to export its structure!');
      return;
    }
    const phoneSelect = document.getElementById('remote-device-select');
    const deviceId = phoneSelect ? phoneSelect.value : 'phone';
    const jsonStr = JSON.stringify(lastExploredPhoneData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Phone_Storage_Structure_${deviceId}_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  });

  // Load Registered Devices & Status
  async function loadDevices() {
    try {
      const res = await fetch('/api/web/devices');
      const data = await res.json();

      if (!data || !data.success || !Array.isArray(data.devices)) return;

      const tbody = document.getElementById('devices-list-body');
      if (!tbody) return;
      tbody.innerHTML = '';

      let onlineCount = 0;

      if (data.devices.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No devices registered yet. Open Android app to sync.</td></tr>`;
        return;
      }

      data.devices.forEach(dev => {
        if (dev.is_online) onlineCount++;

        const tr = document.createElement('tr');
        const notifCnt = dev.counts ? (dev.counts.notifications || 0) : 0;
        const telecomCnt = dev.counts ? (dev.counts.telecom || 0) : 0;
        const mediaCnt = dev.counts ? (dev.counts.media || 0) : 0;
        const lastSeenStr = dev.last_seen_formatted || (dev.last_seen ? new Date(dev.last_seen).toLocaleString() : 'Never');

        tr.innerHTML = `
          <td>
            <span class="badge ${dev.is_online ? 'badge-online' : 'badge-offline'}">
              ${dev.is_online ? '● ONLINE' : '○ OFFLINE'}
            </span>
          </td>
          <td>
            <strong>${escapeHtml(dev.device_name || 'Phone')}</strong>
            <button class="btn btn-outline btn-sm rename-dev-btn" data-id="${escapeHtml(dev.device_id || '')}" data-name="${escapeHtml(dev.device_name || '')}" style="margin-left: 8px; font-size: 10px; padding: 2px 6px; border-radius: 4px;" title="Rename Device">✏️ Rename</button>
          </td>
          <td><code style="font-size: 11px;">${escapeHtml(dev.device_id || '')}</code></td>
          <td>${escapeHtml(lastSeenStr)}</td>
          <td>
            <span style="font-family: var(--font-mono); font-size: 12px;">
              Notifs: ${notifCnt} | Telecom: ${telecomCnt} | Media: ${mediaCnt}
            </span>
          </td>
          <td>
            <button class="btn btn-outline btn-sm inspect-dev-btn" data-id="${escapeHtml(dev.device_id || '')}">Inspect Logs</button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      const totalElem = document.getElementById('stat-total-devices');
      const onlineElem = document.getElementById('stat-online-devices');
      if (totalElem) totalElem.innerText = data.devices.length;
      if (onlineElem) onlineElem.innerText = onlineCount;

      // Bind inspect buttons
      document.querySelectorAll('.inspect-dev-btn').forEach(b => {
        b.addEventListener('click', () => {
          const devId = b.getAttribute('data-id');
          document.querySelector('[data-tab="timeline-tab"]')?.click();
          setTimeout(() => loadTimeline(devId), 200);
        });
      });

      // Bind rename buttons
      document.querySelectorAll('.rename-dev-btn').forEach(b => {
        b.addEventListener('click', async () => {
          const devId = b.getAttribute('data-id');
          const oldName = b.getAttribute('data-name');
          const newName = prompt('Enter new name for this device:', oldName);
          if (newName !== null && newName.trim() !== '') {
            try {
              const response = await fetch('/api/web/device/rename', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device_id: devId, new_name: newName.trim() })
              });
              const result = await response.json();
              if (result.success) {
                loadDevices(); // Refresh the table
                loadRemoteDevicesDropdown(); // Refresh the dropdown in Storage Explorer
              } else {
                alert('Failed to rename device: ' + (result.error || 'Unknown error'));
              }
            } catch (err) {
              console.error('Rename error:', err);
              alert('Network error while renaming device.');
            }
          }
        });
      });

    } catch (err) {
      console.error('Error loading devices:', err);
    }
  }

  // Load Overview Stats
  async function loadStats() {
    try {
      const res = await fetch('/api/web/stats');
      const data = await res.json();
      if (!data.success) return;

      document.getElementById('stat-total-notifs').innerText = data.stats.notifications;
      document.getElementById('stat-storage-size').innerText = data.stats.storage_formatted;
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }

  // Timeline Selection State
  let loadedTimelineItems = [];
  let selectedTimelineItems = new Map();

  // ────────────────────────────────────────────────────────
  //  STORAGE PANEL — Backed-Up Files from Phone (time-sorted)
  // ────────────────────────────────────────────────────────
  async function loadStoragePanelBackedFiles() {
    try {
      const res = await fetch('/api/web/timeline?category=media&limit=200');
      const data = await res.json();
      if (!data.success) return;

      const container = document.getElementById('backed-files-panel');
      if (!container) return;

      const items = data.items;
      if (items.length === 0) {
        container.innerHTML = `
          <div style="text-align:center;padding:40px;color:var(--text-muted);">
            <div style="font-size:48px;margin-bottom:12px;">📭</div>
            <div style="font-size:14px;">No files backed up yet from phone.</div>
            <div style="font-size:12px;margin-top:6px;">Go to <strong>PHONE STORAGE BROWSER</strong> and click <strong>☁️ Backup to Laptop</strong></div>
          </div>`;
        return;
      }

      // Group by date
      const grouped = {};
      items.forEach(item => {
        const d = new Date(item.timestamp);
        const dateKey = d.toLocaleDateString('en-IN', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
        if (!grouped[dateKey]) grouped[dateKey] = { date: d, items: [] };
        grouped[dateKey].items.push(item);
      });

      const sortedDates = Object.keys(grouped).sort((a, b) => grouped[b].date - grouped[a].date);

      let totalBytes = 0;
      items.forEach(i => totalBytes += (i.file_size || 0));

      let html = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding:16px 20px;background:#1a1d2e;border-radius:12px;border:1px solid #2a2d3e;">
          <div style="display:flex;gap:32px;">
            <div><div style="color:#7c6ce0;font-size:10px;font-weight:700;letter-spacing:2px;">TOTAL FILES</div><div style="color:#fff;font-size:24px;font-weight:700;">${items.length}</div></div>
            <div><div style="color:#7c6ce0;font-size:10px;font-weight:700;letter-spacing:2px;">TOTAL SIZE</div><div style="color:#f0b429;font-size:24px;font-weight:700;">${fmtBytes(totalBytes)}</div></div>
            <div><div style="color:#7c6ce0;font-size:10px;font-weight:700;letter-spacing:2px;">DATE RANGE</div><div style="color:#50fa7b;font-size:14px;font-weight:600;margin-top:4px;">${sortedDates[sortedDates.length-1]} – ${sortedDates[0]}</div></div>
          </div>
          <button onclick="loadStoragePanelBackedFiles()" style="padding:8px 16px;background:#7c6ce0;border:none;border-radius:8px;color:#fff;cursor:pointer;font-size:12px;">&#x21BB; Refresh</button>
        </div>`;

      sortedDates.forEach(dateKey => {
        const group = grouped[dateKey];
        const groupBytes = group.items.reduce((s, i) => s + (i.file_size || 0), 0);
        html += `
          <div style="margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:12px;padding:8px 16px;background:#12142a;border-radius:8px;margin-bottom:4px;">
              <span style="color:#7c6ce0;font-weight:700;font-size:12px;">📅 ${dateKey}</span>
              <span style="color:#a0a0c0;font-size:11px;">${group.items.length} file(s)</span>
              <span style="color:#f0b429;font-size:11px;margin-left:auto;">${fmtBytes(groupBytes)}</span>
            </div>
            <table style="width:100%;border-collapse:collapse;">
              <thead><tr style="background:#1a1d2e;">
                <th style="padding:8px 12px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">TYPE</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">FILE NAME</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">ORIGINAL PATH ON PHONE</th>
                <th style="padding:8px 12px;text-align:right;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">SIZE</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">TIME</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">DEVICE</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">ACTION</th>
              </tr></thead>
              <tbody>`;

        group.items.forEach(item => {
          const t = new Date(item.timestamp);
          const timeStr = t.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          const mime = item.source || '';
          let icon = '📄', typeBadge = mime || 'file', badgeColor = '#4a4a6a';
          if (mime.startsWith('image/')) { icon = '📷'; badgeColor = '#1e6b3c'; }
          else if (mime.startsWith('video/')) { icon = '🎥'; badgeColor = '#6b1e1e'; }
          else if (mime.startsWith('audio/')) { icon = '🎧'; badgeColor = '#1e4a6b'; }
          else if (mime.includes('pdf')) { icon = '📎'; badgeColor = '#6b3a1e'; }
          else if (mime.includes('docx') || mime.includes('word')) { icon = '📝'; badgeColor = '#1e3a6b'; }
          else if (mime.includes('zip') || mime.includes('archive')) { icon = '🗄️'; badgeColor = '#5a3a1e'; }

          const localPath = item.body || '';
          const downloadUrl = localPath ? `/api/web/download?file=${encodeURIComponent(localPath.replace('C:\\Vault\\', '').replace('C:/Vault/', '').replace(/\\/g, '/'))}` : '#';

          html += `<tr style="border-bottom:1px solid #1a1d2e;transition:background 0.15s;" onmouseover="this.style.background='#1a2040'" onmouseout="this.style.background=''">
            <td style="padding:8px 12px;">
              <span style="font-size:16px;">${icon}</span>
              <span style="background:${badgeColor};color:#fff;font-size:9px;padding:2px 6px;border-radius:4px;margin-left:4px;vertical-align:middle;">${escapeHtml(typeBadge.split('/').pop())}</span>
            </td>
            <td style="padding:8px 12px;"><strong style="font-size:12px;color:#e0e0ff;">${escapeHtml(item.title || 'Unknown')}</strong></td>
            <td style="padding:8px 12px;"><code style="font-size:10px;color:#a0a0c0;word-break:break-all;">${escapeHtml(localPath)}</code></td>
            <td style="padding:8px 12px;text-align:right;"><span style="font-family:monospace;font-size:12px;color:#f0b429;font-weight:600;">${fmtBytes(item.file_size || 0)}</span></td>
            <td style="padding:8px 12px;"><span style="font-family:monospace;font-size:11px;color:#50fa7b;">${timeStr}</span></td>
            <td style="padding:8px 12px;"><span style="font-size:11px;color:#a0a0c0;">${escapeHtml(item.device_name || item.device_id || 'Phone')}</span></td>
            <td style="padding:8px 12px;display:flex;gap:6px;">
              ${localPath ? `
                <button onclick="window.showFilePreview('${escapeHtml(item.title||'').replace(/'/g, "\\'")}', '${escapeHtml(localPath).replace(/'/g, "\\'")}', '${escapeHtml(mime||'').replace(/'/g, "\\'")}', ${item.file_size||0})" class="btn btn-silver btn-sm" style="font-size:10px;padding:3px 8px;">👁️ Preview</button>
                <a href="${downloadUrl}" class="btn btn-outline btn-sm" style="font-size:10px;padding:3px 8px;" target="_blank">💾 Download</a>
              ` : '<span style="color:#555;font-size:10px;">--</span>'}
            </td>
          </tr>`;
        });

        html += `</tbody></table></div>`;
      });

      container.innerHTML = html;
    } catch(err) {
      console.error('Storage Panel backed files error:', err);
    }
  }

  function fmtBytes(b) {
    if (!b || b <= 0) return '0 B';
    if (b >= 1073741824) return (b/1073741824).toFixed(2) + ' GB';
    if (b >= 1048576) return (b/1048576).toFixed(2) + ' MB';
    if (b >= 1024) return (b/1024).toFixed(1) + ' KB';
    return b + ' B';
  }

  // ─── Load Timeline (Activity Logs: Notifications / SMS / Calls) ───────
  async function loadTimeline(deviceIdFilter = null) {
    try {
      const category = document.getElementById('timeline-category-select').value;
      const search = document.getElementById('timeline-search-input').value;

      let url = `/api/web/timeline?category=${category}&search=${encodeURIComponent(search)}&limit=100`;
      if (deviceIdFilter) url += `&device_id=${encodeURIComponent(deviceIdFilter)}`;

      const res = await fetch(url);
      const data = await res.json();
      if (!data.success) return;

      loadedTimelineItems = data.items;
      selectedTimelineItems.clear();
      updateTimelineSelectedCount();

      const tbody = document.getElementById('timeline-list-body');
      tbody.innerHTML = '';

      if (data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No activity logs found matching criteria.</td></tr>`;
        return;
      }

      data.items.forEach((item, idx) => {
        let catBadge = 'badge-notif';
        let badgeLabel = (item.category || '').toUpperCase();
        const srcLower = (item.source || '').toLowerCase();

        if (srcLower.includes('whatsapp')) { catBadge = 'badge-online'; badgeLabel = '🟢 WHATSAPP'; }
        else if (srcLower.includes('sms') || srcLower.includes('messaging')) { catBadge = 'badge-telecom'; badgeLabel = '📱 SMS'; }
        else if (srcLower.includes('call') || srcLower.includes('dialer')) { catBadge = 'badge-telecom'; badgeLabel = '📞 CALL'; }
        else if (item.category === 'media') { catBadge = 'badge-media'; badgeLabel = '📷 MEDIA'; }
        else if (item.category === 'telecom') { catBadge = 'badge-telecom'; badgeLabel = '📱 TELECOM'; }

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><input type="checkbox" class="timeline-select-cb" data-idx="${idx}"></td>
          <td><span class="badge ${catBadge}">${badgeLabel}</span></td>
          <td><code style="font-size:11px;">${escapeHtml(item.source || 'N/A')}</code></td>
          <td><strong>${escapeHtml(item.title || 'Untitled')}</strong></td>
          <td><span style="font-size:12px;color:var(--text-muted);">${escapeHtml(item.body || item.file_size ? (item.body || '') + (item.file_size ? ' (' + fmtBytes(item.file_size) + ')' : '') : '')}</span></td>
          <td style="font-family:var(--font-mono);font-size:11px;">${item.date_formatted}</td>
          <td>
            <strong>${escapeHtml(item.device_name || item.device_id || 'Unknown')}</strong>
            <br/><code style="font-size:10px;color:var(--text-muted);">${escapeHtml(item.device_id || '')}</code>
          </td>
        `;
        tbody.appendChild(tr);
      });

      tbody.querySelectorAll('.timeline-select-cb').forEach(cb => {
        cb.addEventListener('change', (e) => {
          const idx = parseInt(e.target.getAttribute('data-idx'));
          if (e.target.checked) selectedTimelineItems.set(idx, loadedTimelineItems[idx]);
          else selectedTimelineItems.delete(idx);
          updateTimelineSelectedCount();
        });
      });

    } catch (err) {
      console.error('Error loading activity logs:', err);
    }
  }

  // Timeline Select All

  document.getElementById('select-all-timeline-cb').addEventListener('change', (e) => {
    const cbs = document.querySelectorAll('.timeline-select-cb');
    cbs.forEach(cb => {
      cb.checked = e.target.checked;
      const idx = parseInt(cb.getAttribute('data-idx'));
      if (e.target.checked) selectedTimelineItems.set(idx, loadedTimelineItems[idx]);
      else selectedTimelineItems.delete(idx);
    });
    updateTimelineSelectedCount();
  });

  function updateTimelineSelectedCount() {
    const count = selectedTimelineItems.size;
    document.getElementById('timeline-selected-count').innerText = count;
    document.getElementById('export-selected-csv-btn').disabled = count === 0;
    document.getElementById('export-selected-json-btn').disabled = count === 0;
  }

  // Export Selected CSV Handler
  document.getElementById('export-selected-csv-btn').addEventListener('click', () => exportSelectedLogs('csv'));
  document.getElementById('export-selected-json-btn').addEventListener('click', () => exportSelectedLogs('json'));

  async function exportSelectedLogs(format) {
    if (selectedTimelineItems.size === 0) return;

    try {
      const itemsToExport = Array.from(selectedTimelineItems.values());
      const res = await fetch('/api/web/export-selected', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: itemsToExport, format })
      });

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Vault_Selected_Export_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert('Error exporting selected logs: ' + err.message);
    }
  }

  // Laptop Database Backup Handler
  document.getElementById('create-db-backup-btn').addEventListener('click', async () => {
    try {
      const btn = document.getElementById('create-db-backup-btn');
      btn.innerText = '⌛ Creating Backup...';
      btn.disabled = true;

      const res = await fetch('/api/web/backup-db', { method: 'POST' });
      const data = await res.json();

      btn.innerText = '💾 Backup Laptop Database';
      btn.disabled = false;

      if (data.success) {
        alert(`🎉 Database Backup Created Successfully!\n\nArchive Name: ${data.file_name}\nLocation: ${data.file_path}\nSize: ${(data.size_bytes / 1024).toFixed(1)} KB`);
      } else {
        alert('Error creating database backup: ' + data.error);
      }
    } catch (err) {
      alert('Error creating backup: ' + err.message);
    }
  });


  // Load File Explorer
  async function loadFiles(subpath = '') {
    try {
      currentSubpath = subpath;
      const res = await fetch(`/api/web/files?subpath=${encodeURIComponent(subpath)}`);
      const data = await res.json();

      if (!data.success) return;

      // Update Breadcrumbs
      const breadcrumb = document.getElementById('file-breadcrumb');
      let breadHtml = `<span class="breadcrumb-root breadcrumb-link" data-path="">C:\\Vault</span>`;
      if (data.current_subpath) {
        const parts = data.current_subpath.split('/');
        let accum = '';
        parts.forEach((p, idx) => {
          accum += (accum ? '/' : '') + p;
          breadHtml += `<span class="breadcrumb-sep">/</span>`;
          if (idx === parts.length - 1) {
            breadHtml += `<span class="breadcrumb-current">${escapeHtml(p)}</span>`;
          } else {
            breadHtml += `<span class="breadcrumb-link" data-path="${accum}">${escapeHtml(p)}</span>`;
          }
        });
      }
      breadcrumb.innerHTML = breadHtml;

      // Bind breadcrumb clicks
      breadcrumb.querySelectorAll('.breadcrumb-link').forEach(link => {
        link.addEventListener('click', () => {
          loadFiles(link.getAttribute('data-path'));
        });
      });

      const tbody = document.getElementById('files-list-body');
      tbody.innerHTML = '';
      selectedFiles.clear();
      updateSelectedCount();

      if (data.files.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">This directory is empty.</td></tr>`;
        return;
      }

      data.files.forEach(file => {
        const tr = document.createElement('tr');
        const icon = file.is_directory ? '📁' : '📄';

        tr.innerHTML = `
          <td><input type="checkbox" class="file-select-cb" data-path="${file.relative_path}"></td>
          <td>${icon}</td>
          <td>
            ${file.is_directory ? 
              `<a class="file-link dir-link" data-path="${file.relative_path}"><strong>${escapeHtml(file.name)}/</strong></a>` :
              `<a class="file-link" href="/api/web/download?file=${encodeURIComponent(file.relative_path)}" target="_blank">${escapeHtml(file.name)}</a>`
            }
          </td>
          <td><code style="font-size: 11px;">${file.relative_path}</code></td>
          <td style="font-family: var(--font-mono); font-size: 11px;">${file.size_formatted}</td>
          <td style="font-family: var(--font-mono); font-size: 11px;">${file.modified}</td>
          <td>
            ${file.is_directory ? '--' : 
              `<a href="/api/web/download?file=${encodeURIComponent(file.relative_path)}" class="btn btn-outline btn-sm">💾 Download</a>`
            }
          </td>
        `;
        tbody.appendChild(tr);
      });

      // Bind directory clicks
      tbody.querySelectorAll('.dir-link').forEach(link => {
        link.addEventListener('click', () => {
          loadFiles(link.getAttribute('data-path'));
        });
      });

      // Checkbox Select Handler
      tbody.querySelectorAll('.file-select-cb').forEach(cb => {
        cb.addEventListener('change', (e) => {
          const path = e.target.getAttribute('data-path');
          if (e.target.checked) selectedFiles.add(path);
          else selectedFiles.delete(path);
          updateSelectedCount();
        });
      });

    } catch (err) {
      console.error('Error loading files:', err);
    }
  }

  // Select All Checkbox
  document.getElementById('select-all-files-cb').addEventListener('change', (e) => {
    const checkboxes = document.querySelectorAll('.file-select-cb');
    checkboxes.forEach(cb => {
      cb.checked = e.target.checked;
      const path = cb.getAttribute('data-path');
      if (e.target.checked) selectedFiles.add(path);
      else selectedFiles.delete(path);
    });
    updateSelectedCount();
  });

  function updateSelectedCount() {
    const countSpan = document.getElementById('selected-count');
    const batchBtn = document.getElementById('batch-download-btn');
    countSpan.innerText = selectedFiles.size;
    batchBtn.disabled = selectedFiles.size === 0;
  }

  // Batch ZIP Download
  document.getElementById('batch-download-btn').addEventListener('click', async () => {
    if (selectedFiles.size === 0) return;

    try {
      const res = await fetch('/api/web/download-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files: Array.from(selectedFiles) })
      });

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Vault_Batch_${Date.now()}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert('Error downloading ZIP batch: ' + err.message);
    }
  });

  // Remote Phone Storage Explorer Implementation
  const phoneSelect = document.getElementById('remote-device-select');
  const refreshPhoneBtn = document.getElementById('refresh-phone-explorer-btn');
  let currentPhonePath = '/storage/emulated/0';
  const phoneSelectedFiles = new Map(); // key: path, val: { path, name, size }

  refreshPhoneBtn?.addEventListener('click', () => {
    explorePhoneDirectory(currentPhonePath);
  });

  document.querySelectorAll('.quick-path-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = btn.getAttribute('data-path');
      explorePhoneDirectory(p);
    });
  });

  async function loadRemoteDevicesDropdown() {
    try {
      const res = await fetch('/api/web/devices');
      const data = await res.json();
      if (!data.success) return;

      phoneSelect.innerHTML = '';
      if (data.devices.length === 0) {
        phoneSelect.innerHTML = `<option value="">No registered phones found</option>`;
        return;
      }

      data.devices.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.device_id;
        const hasCached = !!localStorage.getItem('cached_schema_' + d.device_id);
        opt.innerText = `${d.device_name || 'Phone'} (${d.is_online ? '🟢 ONLINE' : '🔴 OFFLINE'}) ${hasCached ? '⚡[CACHED]' : ''} - ID: ${d.device_id}`;
        phoneSelect.appendChild(opt);
      });
    } catch (err) {
      console.error('Error loading devices dropdown:', err);
    }
  }

  // Scan Full Storage Schema Button
  document.getElementById('scan-full-schema-btn')?.addEventListener('click', async () => {
    const deviceId = phoneSelect ? phoneSelect.value : null;
    if (!deviceId) {
      alert('Please select an online phone device first.');
      return;
    }

    const btn = document.getElementById('scan-full-schema-btn');
    btn.innerText = '⌛ Scanning Phone Storage Schema... (10-15s)';
    btn.disabled = true;

    try {
      const cmdRes = await fetch('/api/device/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: deviceId,
          command_type: 'SCAN_FULL_STORAGE',
          payload: { path: '/storage/emulated/0' }
        })
      });
      const cmdData = await cmdRes.json();
      if (!cmdData.success) {
        alert('Failed to start storage scan: ' + cmdData.error);
        btn.innerText = '⚡ Download Storage Schema (Instant Offline Mode)';
        btn.disabled = false;
        return;
      }

      const cmdId = cmdData.command_id;
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        if (attempts > 30) {
          clearInterval(pollInterval);
          alert('⚠️ Storage scan timed out. Ensure the phone is online and active.');
          btn.innerText = '⚡ Download Storage Schema (Instant Offline Mode)';
          btn.disabled = false;
          return;
        }

        try {
          const checkRes = await fetch(`/api/device/command/${cmdId}`);
          const checkData = await checkRes.json();

          if (checkData.success && checkData.command.status === 'COMPLETED') {
            clearInterval(pollInterval);
            const schema = checkData.command.result;
            localStorage.setItem('cached_schema_' + deviceId, JSON.stringify(schema));
            btn.innerText = '⚡ Storage Schema Cached (Instant Mode)';
            btn.disabled = false;
            alert(`🎉 Storage Schema Downloaded Successfully!\n\nTotal Files & Folders Indexed: ${schema.total_items || schema.files?.length || 0}\n\nYou can now browse all folders INSTANTLY without waiting or internet!`);
            explorePhoneDirectory('/storage/emulated/0');
          } else if (checkData.command.status === 'FAILED') {
            clearInterval(pollInterval);
            alert('❌ Storage scan failed on phone.');
            btn.innerText = '⚡ Download Storage Schema (Instant Offline Mode)';
            btn.disabled = false;
          }
        } catch (e) {
          console.error(e);
        }
      }, 1500);
    } catch (err) {
      alert('Error initiating scan: ' + err.message);
      btn.innerText = '⚡ Download Storage Schema (Instant Offline Mode)';
      btn.disabled = false;
    }
  });

  async function explorePhoneDirectory(targetPath) {
    const deviceId = phoneSelect ? phoneSelect.value : null;
    if (!deviceId) {
      alert('Please select a phone device first.');
      return;
    }

    currentPhonePath = targetPath.replace(/\\/g, '/').replace(/\/+$/, '') || '/storage/emulated/0';
    const tbody = document.getElementById('phone-files-list-body');

    // ⚡ INSTANT OFFLINE CACHED SCHEMA LOOKUP
    const cachedStr = localStorage.getItem('cached_schema_' + deviceId);
    if (cachedStr) {
      try {
        const cachedData = JSON.parse(cachedStr);
        if (cachedData && Array.isArray(cachedData.files)) {
          const normTarget = currentPhonePath.toLowerCase();
          const matchedFiles = cachedData.files.filter(f => {
            const fParent = (f.parent_path || '').replace(/\\/g, '/').replace(/\/+$/, '').toLowerCase();
            return fParent === normTarget;
          });

          renderPhoneDirectoryResult({
            current_path: currentPhonePath,
            parent_path: currentPhonePath === '/storage/emulated/0' ? null : currentPhonePath.substring(0, currentPhonePath.lastIndexOf('/')),
            files: matchedFiles
          });
          return;
        }
      } catch (e) { console.error('Cache read error:', e); }
    }

    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">⏳ Communicating with phone at path: <code>${escapeHtml(targetPath)}</code>...</td></tr>`;

    try {
      // Send EXPLORE_DIR command
      const cmdRes = await fetch('/api/device/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: deviceId,
          command_type: 'EXPLORE_DIR',
          payload: { path: targetPath }
        })
      });
      const cmdData = await cmdRes.json();
      if (!cmdData.success) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-offline">Failed to send command to phone: ${escapeHtml(cmdData.error)}</td></tr>`;
        return;
      }

      const cmdId = cmdData.command_id;
      // Poll command result
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        if (attempts > 15) {
          clearInterval(pollInterval);
          tbody.innerHTML = `<tr><td colspan="6" class="text-center text-offline">⚠️ Request timed out. Ensure the Android app is open/online on phone.</td></tr>`;
          return;
        }

        try {
          const checkRes = await fetch(`/api/device/command/${cmdId}`);
          const checkData = await checkRes.json();

          if (checkData.success && checkData.command.status === 'COMPLETED') {
            clearInterval(pollInterval);
            renderPhoneDirectoryResult(checkData.command.result);
          } else if (checkData.command.status === 'FAILED') {
            clearInterval(pollInterval);
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-offline">❌ Phone failed to read directory: ${escapeHtml(checkData.command.result?.error || 'Unknown error')}</td></tr>`;
          }
        } catch (e) {
          console.error(e);
        }
      }, 1000);

    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center text-offline">Error communicating with server: ${escapeHtml(err.message)}</td></tr>`;
    }
  }

  let currentPhoneSort = 'recent';

  // Bind Phone Folder Sort Toolbar buttons
  document.querySelectorAll('.phone-sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.phone-sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentPhoneSort = btn.getAttribute('data-sort') || 'recent';
      if (lastExploredPhoneData) {
        renderPhoneDirectoryResult(lastExploredPhoneData);
      }
    });
  });

  function renderPhoneDirectoryResult(resultData) {
    lastExploredPhoneData = resultData;
    const tbody = document.getElementById('phone-files-list-body');
    tbody.innerHTML = '';

    if (!resultData || !resultData.files) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No files or empty directory response.</td></tr>`;
      return;
    }

    // Render breadcrumbs
    const breadcrumb = document.getElementById('phone-breadcrumb');
    const curPath = resultData.current_path || '/storage/emulated/0';
    let breadHtml = `<span class="breadcrumb-root phone-bread-link" data-path="/storage/emulated/0">/storage/emulated/0</span>`;

    if (curPath !== '/storage/emulated/0') {
      const parts = curPath.replace('/storage/emulated/0', '').split('/').filter(Boolean);
      let accum = '/storage/emulated/0';
      parts.forEach((p, idx) => {
        accum += '/' + p;
        breadHtml += `<span class="breadcrumb-sep">/</span>`;
        if (idx === parts.length - 1) {
          breadHtml += `<span class="breadcrumb-current">${escapeHtml(p)}</span>`;
        } else {
          breadHtml += `<span class="breadcrumb-link phone-bread-link" data-path="${accum}">${escapeHtml(p)}</span>`;
        }
      });
    }
    breadcrumb.innerHTML = breadHtml;

    breadcrumb.querySelectorAll('.phone-bread-link').forEach(link => {
      link.addEventListener('click', () => {
        explorePhoneDirectory(link.getAttribute('data-path'));
      });
    });

    if (resultData.files.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">This phone directory is empty.</td></tr>`;
      return;
    }

    // Sort files based on user-selected option
    let files = [...resultData.files];
    const dirs = files.filter(f => f.is_directory);
    let nonDirs = files.filter(f => !f.is_directory);

    if (currentPhoneSort === 'high_size') {
      nonDirs.sort((a, b) => (b.size_bytes || 0) - (a.size_bytes || 0));
    } else if (currentPhoneSort === 'low_size') {
      nonDirs.sort((a, b) => (a.size_bytes || 0) - (b.size_bytes || 0));
    } else if (currentPhoneSort === 'name') {
      nonDirs.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      dirs.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    } else if (currentPhoneSort === 'old') {
      nonDirs.sort((a, b) => (a.modified || a.last_modified || a.date_modified || 0) - (b.modified || b.last_modified || b.date_modified || 0));
    } else {
      // 'recent' / default
      nonDirs.sort((a, b) => (b.modified || b.last_modified || b.date_modified || 0) - (a.modified || a.last_modified || a.date_modified || 0));
    }

    const sortedFiles = [...dirs, ...nonDirs];

    // Update stats badge
    const statsElem = document.getElementById('phone-folder-stats');
    if (statsElem) {
      const totalBytes = nonDirs.reduce((acc, f) => acc + (f.size_bytes || 0), 0);
      statsElem.textContent = `${dirs.length} folder(s), ${nonDirs.length} file(s) (${formatBytes(totalBytes)})`;
    }

    sortedFiles.forEach(f => {
      const tr = document.createElement('tr');
      let icon = '📄';
      if (f.is_directory) icon = '📁';
      else if (f.mime_type && f.mime_type.startsWith('image/')) icon = '📷';
      else if (f.mime_type && f.mime_type.startsWith('video/')) icon = '🎥';
      else if (f.mime_type && f.mime_type.startsWith('audio/')) icon = '🎙️';

      const sizeBytes = f.size_bytes || 0;
      const formattedSize = f.is_directory ? '<span style="color:var(--text-muted);font-size:10px;">folder</span>' :
        sizeBytes > 1048576 ? (sizeBytes / 1048576).toFixed(2) + ' MB' :
        sizeBytes > 1024 ? (sizeBytes / 1024).toFixed(1) + ' KB' :
        sizeBytes + ' B';

      const actionHtml = f.is_directory
        ? `<button class="btn btn-outline btn-sm remote-backup-btn" style="font-size:10px;" data-path="${escapeHtml(f.absolute_path)}" data-name="${escapeHtml(f.name)}" data-isdir="true" data-size="0">📁 Backup Folder</button>`
        : `<button class="btn btn-silver btn-sm remote-backup-btn" data-path="${escapeHtml(f.absolute_path)}" data-name="${escapeHtml(f.name)}" data-isdir="false" data-size="${sizeBytes}">☁️ Backup to Laptop</button>`;

      const isChecked = phoneSelectedFiles.has(f.absolute_path);
      const cbHtml = f.is_directory
        ? `<span style="color:#444;">--</span>`
        : `<input type="checkbox" class="phone-file-cb" data-path="${escapeHtml(f.absolute_path)}" data-name="${escapeHtml(f.name)}" data-size="${sizeBytes}" ${isChecked ? 'checked' : ''}>`;

      tr.innerHTML = `
        <td style="text-align:center;">${cbHtml}</td>
        <td>${icon}</td>
        <td>
          ${f.is_directory
            ? `<a class="file-link phone-dir-click" data-path="${escapeHtml(f.absolute_path)}"><strong>${escapeHtml(f.name)}/</strong></a>`
            : `<strong>${escapeHtml(f.name)}</strong>`
          }
        </td>
        <td><code style="font-size: 11px; word-break:break-all;">${escapeHtml(f.absolute_path)}</code></td>
        <td style="font-family: var(--font-mono); font-size: 11px;">${formattedSize}</td>
        <td><span class="badge badge-notif" style="font-size: 10px;">${escapeHtml(f.mime_type || (f.is_directory ? 'folder' : 'file'))}</span></td>
        <td>${actionHtml}</td>
      `;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll('.phone-dir-click').forEach(link => {
      link.addEventListener('click', () => {
        explorePhoneDirectory(link.getAttribute('data-path'));
      });
    });

    tbody.querySelectorAll('.remote-backup-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const bt = e.target.closest('.remote-backup-btn');
        const filePath = bt.getAttribute('data-path');
        const fileName = bt.getAttribute('data-name');
        const isDir = bt.getAttribute('data-isdir') === 'true';
        const fileSize = parseInt(bt.getAttribute('data-size') || '0', 10);
        if (isDir) {
          triggerRemoteFolderBackup(filePath, fileName, bt);
        } else {
          triggerRemoteFileBackup(filePath, fileName, bt, fileSize);
        }
      });
    });

    // Checkbox Listeners
    tbody.querySelectorAll('.phone-file-cb').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const path = e.target.getAttribute('data-path');
        const name = e.target.getAttribute('data-name');
        const size = parseInt(e.target.getAttribute('data-size') || '0', 10);
        if (e.target.checked) {
          phoneSelectedFiles.set(path, { path, name, size });
        } else {
          phoneSelectedFiles.delete(path);
        }
        updatePhoneSelectedCount();
      });
    });

    updatePhoneSelectedCount();
  }

  // Update selected counter & batch button state
  function updatePhoneSelectedCount() {
    const countSpan = document.getElementById('phone-selected-count');
    const batchBtn = document.getElementById('batch-phone-backup-btn');
    const count = phoneSelectedFiles.size;
    if (countSpan) countSpan.innerText = count;
    if (batchBtn) batchBtn.disabled = count === 0;

    const selectAllCb = document.getElementById('phone-select-all-cb');
    const cbs = document.querySelectorAll('.phone-file-cb');
    if (selectAllCb && cbs.length > 0) {
      selectAllCb.checked = Array.from(cbs).every(cb => cb.checked);
    }
  }

  // Phone Select All Checkbox Handler
  document.getElementById('phone-select-all-cb')?.addEventListener('change', (e) => {
    const isChecked = e.target.checked;
    const cbs = document.querySelectorAll('.phone-file-cb');
    cbs.forEach(cb => {
      cb.checked = isChecked;
      const path = cb.getAttribute('data-path');
      const name = cb.getAttribute('data-name');
      const size = parseInt(cb.getAttribute('data-size') || '0', 10);
      if (isChecked) {
        phoneSelectedFiles.set(path, { path, name, size });
      } else {
        phoneSelectedFiles.delete(path);
      }
    });
    updatePhoneSelectedCount();
  });

  // Batch Phone Backup Button Handler
  document.getElementById('batch-phone-backup-btn')?.addEventListener('click', () => {
    triggerBatchPhoneBackup();
  });

  // ── Multi-File Batch Phone Backup ───────────────────────────────────────
  async function triggerBatchPhoneBackup() {
    const deviceId = phoneSelect ? phoneSelect.value : null;
    if (!deviceId) {
      alert('Please select an online phone device first.');
      return;
    }

    const items = Array.from(phoneSelectedFiles.values());
    if (items.length === 0) return;

    const batchBtn = document.getElementById('batch-phone-backup-btn');
    const originalText = batchBtn.innerHTML;
    batchBtn.disabled = true;

    const totalFiles = items.length;
    showProgressModal(`Starting batch... (0/${totalFiles})`, 0, `⚡ BATCH BACKUP (${totalFiles} FILES)`);

    let done = 0;
    let failed = 0;
    let totalBytesTransferred = 0;
    const batchStartTime = Date.now();

    for (let i = 0; i < totalFiles; i++) {
      const item = items[i];
      const curIndex = i + 1;

      // Update progress drawer
      const headerTitle = `⚡ BATCH BACKUP (${curIndex}/${totalFiles})`;
      const hTitleElem = document.getElementById('bp-header-title');
      if (hTitleElem) hTitleElem.textContent = headerTitle;
      document.getElementById('bp-filename').textContent = item.name;
      batchBtn.innerHTML = `<span>⌛</span> Backing up ${curIndex}/${totalFiles}...`;

      const pct = Math.round(((curIndex - 1) / totalFiles) * 100);
      updateProgress(
        pct,
        totalBytesTransferred,
        0,
        Math.floor((Date.now() - batchStartTime) / 1000),
        `[${curIndex}/${totalFiles}] Uploading ${item.name}...`,
        `[${new Date().toLocaleTimeString()}] 🚀 File ${curIndex}/${totalFiles}: ${item.name}`
      );

      // Find row in table and update button if visible
      const rowBtn = Array.from(document.querySelectorAll('.remote-backup-btn')).find(b => b.getAttribute('data-path') === item.path);
      if (rowBtn) {
        rowBtn.disabled = true;
        rowBtn.innerText = '⌛ Backing up...';
      }

      const res = await triggerRemoteFileBackupSilent(item.path, item.name, deviceId);
      if (res) {
        done++;
        const savedSize = (typeof res === 'object' && res.file_size) ? res.file_size : (item.size || 0);
        totalBytesTransferred += savedSize;
        if (rowBtn) {
          rowBtn.innerText = '✅ Saved!';
          rowBtn.style.background = '#28a745';
          rowBtn.style.color = '#fff';
        }
        updateProgress(
          Math.round((curIndex / totalFiles) * 100),
          totalBytesTransferred,
          0,
          Math.floor((Date.now() - batchStartTime) / 1000),
          `✅ Saved: ${item.name}`,
          `[${new Date().toLocaleTimeString()}] ✅ [${curIndex}/${totalFiles}] Saved: ${item.name} (${formatBytes(savedSize)})`
        );

        saveTransferRecord({
          fileName: item.name,
          filePath: item.path,
          localPath: (typeof res === 'object' && res.local_path) ? res.local_path : 'C:\\Vault',
          mimeType: (typeof res === 'object' && res.mime_type) ? res.mime_type : '',
          fileSize: savedSize,
          durationSec: Math.max(1, Math.round((Date.now() - batchStartTime) / 1000)),
          speedBps: 0,
          timestamp: Date.now(),
          status: 'COMPLETED'
        });
      } else {
        failed++;
        if (rowBtn) {
          rowBtn.disabled = false;
          rowBtn.innerText = '❌ Failed';
        }
        updateProgress(
          Math.round((curIndex / totalFiles) * 100),
          totalBytesTransferred,
          0,
          Math.floor((Date.now() - batchStartTime) / 1000),
          `❌ Failed: ${item.name}`,
          `[${new Date().toLocaleTimeString()}] ❌ Failed: ${item.name}`
        );
      }
    }

    // Finished Batch
    batchBtn.disabled = false;
    batchBtn.innerHTML = `<span>✅</span> Done (${done}/${totalFiles})`;
    setTimeout(() => {
      batchBtn.innerHTML = originalText;
      updatePhoneSelectedCount();
    }, 4000);

    phoneSelectedFiles.clear();
    document.querySelectorAll('.phone-file-cb').forEach(cb => cb.checked = false);
    const selectAllCb = document.getElementById('phone-select-all-cb');
    if (selectAllCb) selectAllCb.checked = false;
    updatePhoneSelectedCount();

    hideProgressModal(failed === 0, failed > 0 ? `${failed} files failed to backup` : null);
    loadStats();
    loadStoragePanelBackedFiles();
  }

  async function triggerRemoteFolderBackup(folderPath, folderName, btnElem) {
    const deviceId = phoneSelect ? phoneSelect.value : null;
    if (!deviceId) return;

    const originalText = btnElem.innerText;
    btnElem.disabled = true;
    btnElem.innerText = '⌛ Scanning Folder...';

    try {
      // Send EXPLORE_DIR to get files inside this folder
      const cmdRes = await fetch('/api/device/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: deviceId,
          command_type: 'EXPLORE_DIR',
          payload: { path: folderPath }
        })
      });
      const cmdData = await cmdRes.json();
      if (!cmdData.success) {
        alert('Failed: ' + cmdData.error);
        btnElem.disabled = false;
        btnElem.innerText = originalText;
        return;
      }

      const cmdId = cmdData.command_id;
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        if (attempts > 20) {
          clearInterval(pollInterval);
          btnElem.disabled = false;
          btnElem.innerText = '⚠️ Timed Out';
          return;
        }
        try {
          const checkRes = await fetch(`/api/device/command/${cmdId}`);
          const checkData = await checkRes.json();
          if (checkData.success && checkData.command.status === 'COMPLETED') {
            clearInterval(pollInterval);
            const files = (checkData.command.result?.files || []).filter(f => !f.is_directory);
            if (files.length === 0) {
              alert(`Folder "${folderName}" has no files to backup. (Only sub-folders found)\n\nOpen the folder and go deeper to find files.`);
              btnElem.disabled = false;
              btnElem.innerText = originalText;
              return;
            }
            btnElem.innerText = `⌛ Backing up ${files.length} files...`;
            let done = 0;
            for (const f of files) {
              await triggerRemoteFileBackupSilent(f.absolute_path, f.name, deviceId);
              done++;
              btnElem.innerText = `⌛ ${done}/${files.length} done...`;
            }
            btnElem.innerText = `✅ ${done} files backed up!`;
            btnElem.style.background = '#28a745';
            btnElem.style.color = '#fff';
            alert(`✅ Folder backup complete!\n\nFolder: ${folderName}\nFiles backed up: ${done}`);
            loadStats();
          }
        } catch(e) { console.error(e); }
      }, 1000);
    } catch(err) {
      btnElem.disabled = false;
      btnElem.innerText = originalText;
      alert('Error: ' + err.message);
    }
  }

  async function triggerRemoteFileBackupSilent(filePath, fileName, deviceId) {
    try {
      const cmdRes = await fetch('/api/device/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: deviceId, command_type: 'BACKUP_FILE', payload: { path: filePath } })
      });
      const cmdData = await cmdRes.json();
      if (!cmdData.success) return false;
      const cmdId = cmdData.command_id;
      for (let i = 0; i < 120; i++) {
        await new Promise(r => setTimeout(r, 1000));
        const checkRes = await fetch(`/api/device/command/${cmdId}`);
        const checkData = await checkRes.json();
        if (checkData.command && checkData.command.status === 'COMPLETED') {
          return checkData.command.result || true;
        }
        if (checkData.command && checkData.command.status === 'FAILED') return false;
      }
    } catch(e) { return false; }
    return false;
  }

  // ── Floating Progress Drawer Helpers (Non-Blocking) ───────────────────────
  function showProgressModal(fileName, fileSize, headerTitle = 'BACKING UP FROM PHONE') {
    const overlay = document.getElementById('backup-progress-overlay');
    if (!overlay) return;
    overlay.style.display = 'block';

    const drawerBody = document.getElementById('bp-drawer-body');
    if (drawerBody) drawerBody.style.display = 'block';

    const minBtn = document.getElementById('bp-minimize-btn');
    if (minBtn) minBtn.textContent = '—';

    const hTitle = document.getElementById('bp-header-title');
    if (hTitle) hTitle.textContent = headerTitle;

    document.getElementById('bp-filename').textContent = fileName;
    const bar = document.getElementById('bp-bar');
    if (bar) {
      bar.style.width = '0%';
      bar.style.background = 'linear-gradient(90deg, #7c6ce0, #a855f7)';
    }
    document.getElementById('bp-transferred').textContent = '0 B';
    document.getElementById('bp-total-size').textContent = fileSize > 0 ? formatBytes(fileSize) : '--';
    document.getElementById('bp-elapsed').textContent = '0s';
    document.getElementById('bp-status').textContent = 'Sending command to phone...';
    document.getElementById('bp-log').innerHTML = '';
  }

  function updateProgress(pct, transferred, totalSize, elapsed, status, logLine) {
    const bar = document.getElementById('bp-bar');
    if (bar) bar.style.width = Math.min(pct, 100) + '%';
    const trans = document.getElementById('bp-transferred');
    if (trans) trans.textContent = formatBytes(transferred);
    if (totalSize > 0) {
      const tot = document.getElementById('bp-total-size');
      if (tot) tot.textContent = formatBytes(totalSize);
    }
    const el = document.getElementById('bp-elapsed');
    if (el) el.textContent = elapsed + 's';
    if (status) {
      const st = document.getElementById('bp-status');
      if (st) st.textContent = status;
    }
    if (logLine) {
      const log = document.getElementById('bp-log');
      if (log) {
        log.innerHTML += `<div>${logLine}</div>`;
        log.scrollTop = log.scrollHeight;
      }
    }
  }

  function hideProgressModal(success, errorMsg) {
    const overlay = document.getElementById('backup-progress-overlay');
    if (!overlay) return;
    if (success) {
      document.getElementById('bp-status').textContent = '✅ Backup Complete!';
      const bar = document.getElementById('bp-bar');
      if (bar) {
        bar.style.width = '100%';
        bar.style.background = '#28a745';
      }
      setTimeout(() => {
        if (overlay) overlay.style.display = 'none';
        if (bar) bar.style.background = 'linear-gradient(90deg, #7c6ce0, #a855f7)';
      }, 3500);
    } else {
      document.getElementById('bp-status').textContent = '❌ ' + (errorMsg || 'Failed');
      const bar = document.getElementById('bp-bar');
      if (bar) bar.style.background = '#dc3545';
    }
  }

  // Floating Drawer Close & Minimize buttons
  const bpCancelBtn = document.getElementById('bp-cancel-btn');
  const bpDismissBtn = document.getElementById('bp-dismiss-btn');
  const bpMinBtn = document.getElementById('bp-minimize-btn');

  const hideDrawer = () => {
    const ov = document.getElementById('backup-progress-overlay');
    if (ov) ov.style.display = 'none';
  };

  bpCancelBtn?.addEventListener('click', hideDrawer);
  bpDismissBtn?.addEventListener('click', hideDrawer);

  bpMinBtn?.addEventListener('click', () => {
    const body = document.getElementById('bp-drawer-body');
    if (!body) return;
    if (body.style.display === 'none') {
      body.style.display = 'block';
      bpMinBtn.textContent = '—';
    } else {
      body.style.display = 'none';
      bpMinBtn.textContent = '+';
    }
  });

  function formatBytes(b) {
    if (!b || b <= 0) return '0 B';
    if (b >= 1073741824) return (b/1073741824).toFixed(2) + ' GB';
    if (b >= 1048576) return (b/1048576).toFixed(2) + ' MB';
    if (b >= 1024) return (b/1024).toFixed(1) + ' KB';
    return b + ' B';
  }

  // ── Main backup function — real progress from server, 1GB support ────────
  async function triggerRemoteFileBackup(filePath, fileName, btnElem, knownSize) {
    const deviceId = phoneSelect ? phoneSelect.value : null;
    if (!deviceId) return;

    const originalText = btnElem ? btnElem.innerText : '';
    if (btnElem) { btnElem.disabled = true; btnElem.innerText = '⌛ Uploading...'; }

    showProgressModal(fileName, knownSize || 0);
    const startTime = Date.now();
    let sessionId = null; // will be filled once phone starts upload
    let lastRealPct = 0;
    let lastSpeed = 0;
    let lastUploadedBytes = 0;
    let lastSpeedTime = startTime;

    let elapsedTimer = setInterval(() => {
      document.getElementById('bp-elapsed').textContent = Math.floor((Date.now() - startTime) / 1000) + 's';
    }, 500);

    try {
      updateProgress(3, 0, knownSize || 0, 0, 'Sending command to phone...', `[${new Date().toLocaleTimeString()}] 📤 BACKUP_FILE → ${fileName}`);

      const cmdRes = await fetch('/api/device/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: deviceId, command_type: 'BACKUP_FILE', payload: { path: filePath } })
      });
      const cmdData = await cmdRes.json();
      if (!cmdData.success) {
        clearInterval(elapsedTimer);
        hideProgressModal(false, 'Failed to send: ' + cmdData.error);
        if (btnElem) { btnElem.disabled = false; btnElem.innerText = originalText; }
        return;
      }

      updateProgress(5, 0, knownSize || 0, 1, 'Command sent — phone is preparing file...', `[${new Date().toLocaleTimeString()}] ✅ Command ${cmdData.command_id} sent. Waiting for phone...`);

      const cmdId = cmdData.command_id;
      let attempts = 0;

      const pollInterval = setInterval(async () => {
        attempts++;
        const elapsed = Math.floor((Date.now() - startTime) / 1000);

        if (attempts > 3600) { // 1 hour max
          clearInterval(pollInterval);
          clearInterval(elapsedTimer);
          hideProgressModal(false, 'Timed out after 1 hour.');
          if (btnElem) { btnElem.disabled = false; btnElem.innerText = '⚠️ Timed Out'; }
          return;
        }

        try {
          // Try to get real progress from server (Android reports every 1MB)
          if (sessionId) {
            const progRes = await fetch(`/api/device/upload-progress/${sessionId}`);
            const progData = await progRes.json();
            if (progData.progress) {
              const p = progData.progress;
              const now = Date.now();
              const speedBps = (p.uploaded_bytes - lastUploadedBytes) / ((now - lastSpeedTime) / 1000);
              lastSpeed = speedBps > 0 ? speedBps : lastSpeed;
              lastSpeedTime = now;
              lastUploadedBytes = p.uploaded_bytes;
              lastRealPct = p.percent;
              const eta = lastSpeed > 0 ? Math.round((p.total_bytes - p.uploaded_bytes) / lastSpeed) : '?';
              const speedStr = formatBytes(Math.round(lastSpeed)) + '/s';
              updateProgress(
                p.percent,
                p.uploaded_bytes,
                p.total_bytes,
                elapsed,
                `📡 Uploading: ${p.percent}% | ${formatBytes(p.uploaded_bytes)} / ${formatBytes(p.total_bytes)} | Speed: ${speedStr} | ETA: ${eta}s`,
                null
              );
            }
          } else {
            // No session yet — animate slowly up to 15%
            const animPct = Math.min(5 + attempts * 0.15, 15);
            updateProgress(animPct, 0, knownSize || 0, elapsed, `Waiting for phone to start upload... (${elapsed}s)`, null);
          }

          // Check command completion
          const checkRes = await fetch(`/api/device/command/${cmdId}`);
          const checkData = await checkRes.json();

          if (checkData.success && checkData.command.status === 'COMPLETED') {
            clearInterval(pollInterval);
            clearInterval(elapsedTimer);
            const resData = checkData.command.result || {};
            sessionId = resData.session_id || sessionId;
            const savedSize = resData.file_size || knownSize || 0;
            const localPath = resData.local_path || 'C:\\Vault';
            const mimeType = resData.mime_type || '';
            const isDup = resData.duplicate ? ' (deduplication — file already existed)' : '';
            updateProgress(100, savedSize, savedSize, elapsed, '✅ Backup complete!',
              `[${new Date().toLocaleTimeString()}] ✅ DONE${isDup} → ${localPath} (${formatBytes(savedSize)})`);
            hideProgressModal(true);
            if (btnElem) { btnElem.innerText = '✅ Saved!'; btnElem.style.background = '#28a745'; btnElem.style.color = '#fff'; }
            
            // Record transfer history ("Etne der mai aa gaya")
            const durationSec = Math.max(1, Math.round((Date.now() - startTime) / 1000));
            saveTransferRecord({
              fileName,
              filePath,
              localPath,
              mimeType,
              fileSize: savedSize,
              durationSec,
              speedBps: lastSpeed || (savedSize / durationSec),
              timestamp: Date.now(),
              status: 'COMPLETED'
            });

            // Show preview after backup
            setTimeout(() => showFilePreview(fileName, localPath, mimeType, savedSize), 1800);
            setTimeout(() => loadStoragePanelBackedFiles(), 1500);
            loadStats();

          } else if (checkData.command.status === 'FAILED') {
            clearInterval(pollInterval);
            clearInterval(elapsedTimer);
            const errMsg = checkData.command.result?.error || 'Phone reported failure';
            hideProgressModal(false, errMsg);
            if (btnElem) { btnElem.disabled = false; btnElem.innerText = '❌ Failed'; }
            updateProgress(0, 0, 0, elapsed, null, `[${new Date().toLocaleTimeString()}] ❌ ERROR: ${errMsg}`);

            saveTransferRecord({
              fileName,
              filePath,
              localPath: '',
              mimeType: '',
              fileSize: knownSize || 0,
              durationSec: Math.max(1, Math.round((Date.now() - startTime) / 1000)),
              speedBps: 0,
              timestamp: Date.now(),
              status: 'FAILED',
              errorMsg: errMsg
            });
          }
        } catch (e) {
          console.error(e);
        }
      }, 1000);

      // Also poll upload-progress-all to discover session_id when phone starts
      const discoverInterval = setInterval(async () => {
        if (sessionId) { clearInterval(discoverInterval); return; }
        try {
          const allRes = await fetch('/api/device/upload-progress-all');
          const allData = await allRes.json();
          if (allData.sessions && allData.sessions.length > 0) {
            const s = allData.sessions[0];
            if (s.file_name && fileName.includes(s.file_name.substring(0, 10))) {
              sessionId = s.session_id;
              updateProgress(10, 0, s.total_bytes || knownSize || 0, 0, 'Phone started upload!', `[${new Date().toLocaleTimeString()}] 🟢 Upload started — Session: ${sessionId}`);
              clearInterval(discoverInterval);
            }
          }
        } catch(e) {}
      }, 2000);

    } catch (err) {
      clearInterval(elapsedTimer);
      hideProgressModal(false, err.message);
      if (btnElem) { btnElem.disabled = false; btnElem.innerText = originalText; }
    }
  }

  // ── File Preview Modal after backup ────────────────────────────────────
  function showFilePreview(fileName, localPath, mimeType, fileSize) {
    // Build download URL from local path
    const relPath = (localPath || '').replace(/\\/g, '/').replace('C:/Vault/', '').replace('C:\\Vault\\', '');
    const downloadUrl = `/api/web/download?file=${encodeURIComponent(relPath)}`;

    let previewHtml = '';
    const mt = (mimeType || '').toLowerCase();
    if (mt.startsWith('image/')) {
      previewHtml = `<img src="${downloadUrl}" style="max-width:100%;max-height:320px;border-radius:8px;object-fit:contain;" onerror="this.style.display='none'">`;
    } else if (mt.startsWith('video/')) {
      previewHtml = `<video src="${downloadUrl}" controls style="max-width:100%;max-height:280px;border-radius:8px;"></video>`;
    } else if (mt.startsWith('audio/')) {
      previewHtml = `<div style="font-size:48px;text-align:center;padding:20px;">🎧</div><audio src="${downloadUrl}" controls style="width:100%;margin-top:8px;"></audio>`;
    } else if (mt.includes('pdf')) {
      previewHtml = `<div style="font-size:48px;text-align:center;padding:10px;">📎</div><p style="text-align:center;color:#a0a0c0;font-size:13px;">PDF file — click Download to open</p>`;
    } else {
      const ext = fileName.split('.').pop().toUpperCase();
      previewHtml = `<div style="font-size:64px;text-align:center;padding:20px;">📄</div><p style="text-align:center;color:#a0a0c0;">No preview available for .${ext} files</p>`;
    }

    // Remove existing preview modal if any
    const existing = document.getElementById('file-preview-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'file-preview-modal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:10000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px);';
    modal.innerHTML = `
      <div style="background:#1a1d2e;border:1px solid #7c6ce0;border-radius:16px;padding:28px;max-width:600px;width:90%;max-height:90vh;overflow-y:auto;box-shadow:0 20px 80px rgba(124,108,224,0.5);position:relative;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:16px;">
          <div>
            <div style="color:#7c6ce0;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">✅ BACKED UP SUCCESSFULLY</div>
            <div style="color:#fff;font-size:14px;font-weight:600;margin-top:4px;word-break:break-all;">${escapeHtml(fileName)}</div>
            <div style="color:#f0b429;font-size:12px;margin-top:4px;">${formatBytes(fileSize)}</div>
          </div>
          <button id="pm-cross-btn" onclick="window.closePreviewModal()" style="background:#2a2d3e;border:1px solid #7c6ce0;border-radius:50%;color:#fff;cursor:pointer;width:36px;height:36px;font-size:18px;display:flex;align-items:center;justify-content:center;transition:background 0.2s;" onmouseover="this.style.background='#7c6ce0'" onmouseout="this.style.background='#2a2d3e'" title="Close Preview">✕</button>
        </div>
        <div style="background:#0d0f1a;border-radius:12px;padding:16px;margin-bottom:16px;min-height:80px;display:flex;align-items:center;justify-content:center;">
          ${previewHtml}
        </div>
        <div style="display:flex;gap:10px;">
          <a href="${downloadUrl}" target="_blank" download style="flex:1;padding:10px;background:#7c6ce0;color:#fff;border:none;border-radius:8px;text-align:center;text-decoration:none;font-size:13px;font-weight:600;">💾 Download to PC</a>
          <button id="pm-close-btn" onclick="window.closePreviewModal()" style="flex:1;padding:10px;background:transparent;border:1px solid #444;border-radius:8px;color:#aaa;cursor:pointer;font-size:13px;">Close</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const closeSelf = () => {
      modal.remove();
      const leftOver = document.getElementById('file-preview-modal');
      if (leftOver) leftOver.remove();
    };

    modal.querySelector('#pm-cross-btn')?.addEventListener('click', closeSelf);
    modal.querySelector('#pm-close-btn')?.addEventListener('click', closeSelf);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeSelf(); });

    const escHandler = (e) => {
      if (e.key === 'Escape') {
        closeSelf();
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
  }

  // ── Transfer Activity Store ("Etne Der Mai Aa Gaya") ─────────
  let transferHistoryStore = JSON.parse(localStorage.getItem('vault_transfer_history') || '[]');

  function saveTransferRecord(record) {
    transferHistoryStore.unshift(record);
    if (transferHistoryStore.length > 50) transferHistoryStore.pop();
    localStorage.setItem('vault_transfer_history', JSON.stringify(transferHistoryStore));
    renderTransferActivityPanel();
  }

  function renderTransferActivityPanel() {
    const container = document.getElementById('transfer-activity-panel');
    if (!container) return;

    if (transferHistoryStore.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:24px;color:var(--text-muted);font-size:12px;background:#141726;border-radius:10px;border:1px solid #2a2d3e;">No active or recent transfers yet.</div>`;
      return;
    }

    let html = `
      <div style="background:#141726;border:1px solid #2a2d3e;border-radius:12px;overflow:hidden;">
        <table style="width:100%;border-collapse:collapse;">
          <thead>
            <tr style="background:#1a1d2e;">
              <th style="padding:10px 14px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">FILE NAME & PATH</th>
              <th style="padding:10px 14px;text-align:right;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">SIZE</th>
              <th style="padding:10px 14px;text-align:center;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">TIME TAKEN ("ETNE DER MAI AA GAYA")</th>
              <th style="padding:10px 14px;text-align:right;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">AVG SPEED</th>
              <th style="padding:10px 14px;text-align:center;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">STATUS</th>
              <th style="padding:10px 14px;text-align:left;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">DATE & TIME</th>
              <th style="padding:10px 14px;text-align:center;font-size:10px;color:#7c6ce0;font-weight:700;letter-spacing:1px;">ACTION</th>
            </tr>
          </thead>
          <tbody>`;

    transferHistoryStore.forEach((rec) => {
      const durSec = rec.durationSec || 0;
      const durFormatted = durSec >= 60 ? `${Math.floor(durSec/60)}m ${durSec%60}s` : `${durSec}s`;
      const timeStr = rec.timestamp ? new Date(rec.timestamp).toLocaleString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', day: '2-digit', month: 'short' }) : 'Just now';
      
      const isSuccess = rec.status === 'COMPLETED';
      const statusBadge = isSuccess ? '<span style="background:#1e6b3c;color:#fff;font-size:10px;padding:3px 8px;border-radius:6px;font-weight:600;">✅ COMPLETED</span>' : '<span style="background:#6b1e1e;color:#fff;font-size:10px;padding:3px 8px;border-radius:6px;font-weight:600;">❌ FAILED</span>';
      
      const speedFormatted = rec.speedBps ? formatBytes(Math.round(rec.speedBps)) + '/s' : '--';
      const downloadUrl = rec.localPath ? `/api/web/download?file=${encodeURIComponent(rec.localPath.replace(/\\/g, '/').replace('C:/Vault/', '').replace('C:\\Vault\\', ''))}` : '#';

      html += `
        <tr style="border-bottom:1px solid #1a1d2e;">
          <td style="padding:10px 14px;">
            <strong style="color:#fff;font-size:12px;">${escapeHtml(rec.fileName)}</strong>
            <br/><code style="font-size:10px;color:#888;">${escapeHtml(rec.filePath)}</code>
          </td>
          <td style="padding:10px 14px;text-align:right;"><span style="font-family:monospace;font-size:12px;color:#f0b429;font-weight:700;">${formatBytes(rec.fileSize)}</span></td>
          <td style="padding:10px 14px;text-align:center;">
            <span style="background:#23273e;border:1px solid #3b4268;color:#50fa7b;font-family:monospace;font-size:11px;padding:4px 10px;border-radius:8px;font-weight:700;">
              ⚡ ${durFormatted} (${durSec}s me aa gaya)
            </span>
          </td>
          <td style="padding:10px 14px;text-align:right;"><span style="font-family:monospace;font-size:11px;color:#7c6ce0;">${speedFormatted}</span></td>
          <td style="padding:10px 14px;text-align:center;">${statusBadge}</td>
          <td style="padding:10px 14px;"><span style="font-size:11px;color:#a0a0c0;">${timeStr}</span></td>
          <td style="padding:10px 14px;text-align:center;">
            ${isSuccess ? `
              <button onclick="window.showFilePreview('${escapeHtml(rec.fileName).replace(/'/g, "\\'")}', '${escapeHtml(rec.localPath).replace(/'/g, "\\'")}', '${escapeHtml(rec.mimeType||'').replace(/'/g, "\\'")}', ${rec.fileSize})" class="btn btn-silver btn-sm" style="font-size:10px;padding:3px 8px;margin-right:4px;">👁️ Preview</button>
              <a href="${downloadUrl}" class="btn btn-outline btn-sm" style="font-size:10px;padding:3px 8px;" target="_blank">💾 Download</a>
            ` : '<span style="color:#666;font-size:10px;">--</span>'}
          </td>
        </tr>`;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
  }

  document.getElementById('clear-transfer-log-btn')?.addEventListener('click', () => {
    transferHistoryStore = [];
    localStorage.removeItem('vault_transfer_history');
    renderTransferActivityPanel();
  });

  // ── App Usage Tracker Panel ("Konsa App Kitne Baje Chala") ─────────────
  async function loadAppUsageTrackerPanel() {
    try {
      const container = document.getElementById('app-usage-tracker-panel');
      if (!container) return;

      const res = await fetch('/api/web/app-usage?limit=100');
      const data = await res.json();
      if (!data || !data.success || !Array.isArray(data.items)) return;

      const items = data.items;
      if (items.length === 0) {
        container.innerHTML = `<div style="text-align:center;padding:24px;color:var(--text-muted);font-size:12px;background:#141726;border-radius:10px;border:1px solid #2a2d3e;">No app activity captured yet.</div>`;
        return;
      }

      let html = `
        <div style="background:#141726;border:1px solid #2a2d3e;border-radius:12px;overflow:hidden;">
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr style="background:#1a1d2e;">
                <th style="padding:10px 14px;text-align:left;font-size:10px;color:#50fa7b;font-weight:700;letter-spacing:1px;">APP NAME</th>
                <th style="padding:10px 14px;text-align:left;font-size:10px;color:#50fa7b;font-weight:700;letter-spacing:1px;">EXACT DATE & TIME ("KITNE BAJE CHALA")</th>
                <th style="padding:10px 14px;text-align:left;font-size:10px;color:#50fa7b;font-weight:700;letter-spacing:1px;">DEVICE NAME / USER</th>
                <th style="padding:10px 14px;text-align:center;font-size:10px;color:#50fa7b;font-weight:700;letter-spacing:1px;">ACTIVITY STATE</th>
              </tr>
            </thead>
            <tbody>`;

      items.forEach(item => {
        let appIcon = '📱';
        const name = (item.app_name || '').toLowerCase();
        if (name.includes('whatsapp')) appIcon = '💬';
        else if (name.includes('youtube')) appIcon = '🎥';
        else if (name.includes('instagram') || name.includes('facebook')) appIcon = '📷';
        else if (name.includes('chrome') || name.includes('browser')) appIcon = '🌐';
        else if (name.includes('call') || name.includes('phone') || name.includes('dialer')) appIcon = '📞';
        else if (name.includes('message') || name.includes('sms')) appIcon = '✉️';
        else if (name.includes('setting')) appIcon = '⚙️';
        else if (name.includes('gallery') || name.includes('photo')) appIcon = '🖼️';

        html += `
          <tr style="border-bottom:1px solid #1a1d2e;transition:background 0.15s;" onmouseover="this.style.background='#1a243a'" onmouseout="this.style.background=''">
            <td style="padding:10px 14px;">
              <span style="font-size:16px;vertical-align:middle;margin-right:6px;">${appIcon}</span>
              <strong style="color:#fff;font-size:13px;vertical-align:middle;">${escapeHtml(item.app_name)}</strong>
              ${item.package_name ? `<span style="font-size:10px;color:#888;margin-left:6px;font-family:monospace;">(${escapeHtml(item.package_name)})</span>` : ''}
            </td>
            <td style="padding:10px 14px;">
              <span style="background:#122b1e;border:1px solid #1e6b3c;color:#50fa7b;font-family:monospace;font-size:12px;padding:4px 10px;border-radius:6px;font-weight:700;">
                🕒 ${escapeHtml(item.date_formatted)}
              </span>
            </td>
            <td style="padding:10px 14px;">
              <span style="color:#e0e0ff;font-size:12px;">📱 ${escapeHtml(item.device_name)}</span>
            </td>
            <td style="padding:10px 14px;text-align:center;">
              <span style="background:#2a2d3e;color:#7c6ce0;font-size:10px;padding:3px 8px;border-radius:4px;font-weight:700;">
                ${escapeHtml(item.event)}
              </span>
            </td>
          </tr>`;
      });

      html += `</tbody></table></div>`;
      container.innerHTML = html;
    } catch(err) {
      console.error('Error loading app usage tracker:', err);
    }
  }

  // Render initial activity panel
  renderTransferActivityPanel();

  // Expose global methods for inline HTML onclick handlers
  window.showFilePreview = showFilePreview;
  window.loadStoragePanelBackedFiles = loadStoragePanelBackedFiles;
  window.loadAppUsageTrackerPanel = loadAppUsageTrackerPanel;

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
});

// Top-level global close handler accessible from anywhere
window.closePreviewModal = function() {
  const modals = document.querySelectorAll('#file-preview-modal');
  modals.forEach(m => {
    m.style.display = 'none';
    m.remove();
  });
};


