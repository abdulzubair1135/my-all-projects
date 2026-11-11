const supabase = require('../config/supabase');

const getSymptoms = async (req, res, next) => {
  try {
    const { data, error } = await supabase.from('symptoms').select('*').order('name');
    if (error) throw error;
    res.json({ success: true, symptoms: data });
  } catch (err) {
    next(err);
  }
};

const logSymptom = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { symptom_id, log_date, intensity, notes } = req.body;

    if (!symptom_id || !log_date) {
      return res.status(400).json({ success: false, message: 'symptom_id and log_date are required' });
    }

    const { data, error } = await supabase
      .from('symptom_logs')
      .insert([{ user_id: userId, symptom_id, log_date, intensity: intensity || 'MEDIUM', notes }])
      .select('*, symptoms(name, category)')
      .single();

    if (error) throw error;
    res.status(201).json({ success: true, message: 'Symptom logged successfully', symptomLog: data });
  } catch (err) {
    next(err);
  }
};

const getSymptomHistory = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data, error } = await supabase
      .from('symptom_logs')
      .select('*, symptoms(name, category)')
      .eq('user_id', userId)
      .order('log_date', { ascending: false });

    if (error) throw error;
    res.json({ success: true, history: data });
  } catch (err) {
    next(err);
  }
};

const deleteSymptomLog = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const logId = req.params.id;

    const { error } = await supabase.from('symptom_logs').delete().eq('id', logId).eq('user_id', userId);
    if (error) throw error;

    res.json({ success: true, message: 'Symptom log deleted successfully' });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getSymptoms,
  logSymptom,
  getSymptomHistory,
  deleteSymptomLog
};
