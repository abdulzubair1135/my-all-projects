const express = require('express');
const router = express.Router();
const { authenticateDevice } = require('../middleware/auth');
const { dateQuerySchema, dateRangeQuerySchema } = require('../utils/validation');
const { getVaultByDate, getVaultByRange, getStorageStats } = require('../services/vaultService');

/**
 * GET /api/vault?date=YYYY-MM-DD
 * Exact date search across all vaulted categories.
 */
router.get('/', authenticateDevice, (req, res) => {
  const parseResult = dateQuerySchema.safeParse(req.query);
  if (!parseResult.success) {
    return res.status(400).json({
      success: false,
      error: 'Invalid date parameter. Required format: YYYY-MM-DD',
      details: parseResult.error.errors.map(e => e.message)
    });
  }

  try {
    const results = getVaultByDate(parseResult.data.date);
    res.json({
      success: true,
      ...results
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: `Error querying vault date: ${error.message}`
    });
  }
});

/**
 * GET /api/vault/range?from=YYYY-MM-DD&to=YYYY-MM-DD
 * Date range search.
 */
router.get('/range', authenticateDevice, (req, res) => {
  const parseResult = dateRangeQuerySchema.safeParse(req.query);
  if (!parseResult.success) {
    return res.status(400).json({
      success: false,
      error: 'Invalid date range parameters. Required format: YYYY-MM-DD',
      details: parseResult.error.errors.map(e => e.message)
    });
  }

  try {
    const results = getVaultByRange(parseResult.data.from, parseResult.data.to);
    res.json({
      success: true,
      ...results
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: `Error querying vault date range: ${error.message}`
    });
  }
});

/**
 * GET /api/storage
 * Disk and media storage statistics.
 */
router.get('/storage', authenticateDevice, (req, res) => {
  try {
    const stats = getStorageStats();
    res.json({
      success: true,
      ...stats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: `Failed to retrieve storage statistics: ${error.message}`
    });
  }
});

module.exports = router;
