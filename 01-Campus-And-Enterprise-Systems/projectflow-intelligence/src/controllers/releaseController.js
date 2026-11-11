const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { store } = require('../supabase');
const { recordAuditLog } = require('../middleware/auditLogger');

function getLatestRelease(req, res) {
  const appId = req.query.applicationId || 'com.projectflow.android';
  const published = (store.releases || [])
    .filter(r => r.applicationId === appId && r.status === 'PUBLISHED')
    .sort((a, b) => b.versionCode - a.versionCode);

  if (published.length === 0) {
    return res.status(404).json({ error: 'No published releases available' });
  }

  const latest = published[0];
  res.json({
    ...latest,
    downloadUrl: `/api/v1/releases/${latest.id}/download`
  });
}

function downloadRelease(req, res) {
  const rel = (store.releases || []).find(r => r.id === req.params.id);
  if (!rel) {
    return res.status(404).json({ error: 'Release artifact not found' });
  }

  // Base directory is project root
  const rootDir = path.resolve(__dirname, '../../');
  const filePath = path.join(rootDir, rel.storagePath);
  res.setHeader('Content-Type', rel.mimeType || 'application/vnd.android.package-archive');
  res.setHeader('Content-Disposition', `attachment; filename="${rel.artifactFilename}"`);
  res.setHeader('x-sha256-checksum', rel.sha256Checksum);

  res.sendFile(filePath, (err) => {
    if (err) {
      console.error('[RELEASE DOWNLOAD ERROR]', err.message);
      if (!res.headersSent) {
        res.status(500).json({ error: 'Failed streaming APK release artifact' });
      }
    }
  });
}

function listAdminReleases(req, res) {
  const normalized = (store.releases || []).map(r => ({
    ...r,
    channel: r.channel || r.releaseChannel || 'STABLE',
    artifactSize: r.artifactSize || r.fileSizeBytes || 8114674,
    artifactUrl: r.artifactUrl || (r.storagePath ? `/${r.storagePath}` : '/releases/android/ProjectFlow-Intelligence-v2.0.0.apk')
  }));
  res.json(normalized);
}

function createRelease(req, res) {
  const { versionName, versionCode, artifactFilename, storagePath, releaseNotes, releaseChannel, channel, artifactSize, fileSizeBytes } = req.body;
  const newRelease = {
    id: uuidv4(),
    applicationId: req.body.applicationId || 'com.projectflow.android',
    versionName: versionName || '2.0.0',
    versionCode: versionCode || 200,
    artifactFilename: artifactFilename || 'ProjectFlow-Intelligence-v2.0.0.apk',
    storagePath: storagePath || 'releases/android/ProjectFlow-Intelligence-v2.0.0.apk',
    mimeType: 'application/vnd.android.package-archive',
    fileSizeBytes: fileSizeBytes || artifactSize || 8114674,
    artifactSize: artifactSize || fileSizeBytes || 8114674,
    sha256Checksum: req.body.sha256Checksum || '8c20000160064c7bb80af8765f912ed1d9bb20ef6bffbb4d35ed2b3729030409',
    releaseChannel: releaseChannel || channel || 'STABLE',
    channel: channel || releaseChannel || 'STABLE',
    releaseNotes: releaseNotes || 'Official release',
    minimumSupportedVersionCode: 1,
    status: 'PUBLISHED',
    createdAt: new Date().toISOString(),
    publishedAt: new Date().toISOString()
  };
  (store.releases = store.releases || []).unshift(newRelease);
  recordAuditLog('RELEASE_CREATED', 'RELEASE', newRelease.id, req.headers['x-user-email'] || 'admin@projectflow.io', { versionName: newRelease.versionName, channel: newRelease.channel });
  res.status(201).json(newRelease);
}

function publishRelease(req, res) {
  const rel = (store.releases || []).find(r => r.id === req.params.id);
  if (!rel) return res.status(404).json({ error: 'Release not found' });
  rel.status = 'PUBLISHED';
  rel.publishedAt = new Date().toISOString();
  recordAuditLog('RELEASE_PUBLISHED', 'RELEASE', rel.id, req.headers['x-user-email'] || 'admin@projectflow.io', { versionName: rel.versionName });
  res.json(rel);
}

function unpublishRelease(req, res) {
  const rel = (store.releases || []).find(r => r.id === req.params.id);
  if (!rel) return res.status(404).json({ error: 'Release not found' });
  rel.status = 'DRAFT';
  recordAuditLog('RELEASE_UNPUBLISHED', 'RELEASE', rel.id, req.headers['x-user-email'] || 'admin@projectflow.io', { versionName: rel.versionName });
  res.json(rel);
}

module.exports = {
  getLatestRelease,
  downloadRelease,
  listAdminReleases,
  createRelease,
  publishRelease,
  unpublishRelease
};
