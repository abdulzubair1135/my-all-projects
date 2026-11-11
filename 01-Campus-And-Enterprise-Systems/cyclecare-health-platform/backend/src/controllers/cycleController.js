const supabase = require('../config/supabase');
const { calculateCycleMetrics, generateInsights } = require('../services/cycleService');

const getCycleData = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: settings } = await supabase.from('cycle_settings').select('*').eq('user_id', userId).single();
    const { data: logs } = await supabase.from('period_logs').select('*').eq('user_id', userId).order('start_date', { ascending: false });

    const metrics = calculateCycleMetrics(logs || [], settings);

    res.json({
      success: true,
      settings: settings || { average_cycle_length: 28, average_period_length: 5 },
      periodLogs: logs || [],
      metrics
    });
  } catch (err) {
    next(err);
  }
};

const addPeriodLog = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { start_date, end_date, flow, notes } = req.body;

    if (!start_date) {
      return res.status(400).json({ success: false, message: 'Start date is required' });
    }

    if (end_date && new Date(end_date) < new Date(start_date)) {
      return res.status(400).json({ success: false, message: 'End date cannot be before start date' });
    }

    const { data, error } = await supabase
      .from('period_logs')
      .insert([{ user_id: userId, start_date, end_date, flow: flow || 'MEDIUM', notes }])
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ success: true, message: 'Period log added successfully', periodLog: data });
  } catch (err) {
    next(err);
  }
};

const updatePeriodLog = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const logId = req.params.id;
    const { start_date, end_date, flow, notes } = req.body;

    if (end_date && new Date(end_date) < new Date(start_date)) {
      return res.status(400).json({ success: false, message: 'End date cannot be before start date' });
    }

    const { data, error } = await supabase
      .from('period_logs')
      .update({ start_date, end_date, flow, notes, updated_at: new Date() })
      .eq('id', logId)
      .eq('user_id', userId)
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, message: 'Period log updated successfully', periodLog: data });
  } catch (err) {
    next(err);
  }
};

const deletePeriodLog = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const logId = req.params.id;

    const { error } = await supabase.from('period_logs').delete().eq('id', logId).eq('user_id', userId);
    if (error) throw error;

    res.json({ success: true, message: 'Period log deleted successfully' });
  } catch (err) {
    next(err);
  }
};

const getPrediction = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: settings } = await supabase.from('cycle_settings').select('*').eq('user_id', userId).single();
    const { data: logs } = await supabase.from('period_logs').select('*').eq('user_id', userId).order('start_date', { ascending: false });

    const metrics = calculateCycleMetrics(logs || [], settings);
    res.json({ success: true, prediction: metrics });
  } catch (err) {
    next(err);
  }
};

const getInsights = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: settings } = await supabase.from('cycle_settings').select('*').eq('user_id', userId).single();
    const { data: logs } = await supabase.from('period_logs').select('*').eq('user_id', userId).order('start_date', { ascending: false });
    const { data: symptoms } = await supabase.from('symptom_logs').select('*, symptoms(name)').eq('user_id', userId);
    const { data: moods } = await supabase.from('mood_logs').select('*').eq('user_id', userId);

    const metrics = calculateCycleMetrics(logs || [], settings);
    const insights = generateInsights(metrics, symptoms || [], moods || []);

    res.json({ success: true, insights });
  } catch (err) {
    next(err);
  }
};

const getCycleHistory = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data: logs, error } = await supabase
      .from('period_logs')
      .select('*')
      .eq('user_id', userId)
      .order('start_date', { ascending: false });

    if (error) throw error;
    res.json({ success: true, history: logs || [] });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getCycleData,
  addPeriodLog,
  updatePeriodLog,
  deletePeriodLog,
  getCycleHistory,
  getPrediction,
  getInsights
};
