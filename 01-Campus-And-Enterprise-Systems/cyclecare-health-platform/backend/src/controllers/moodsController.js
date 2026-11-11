const supabase = require('../config/supabase');

const getMoods = async (req, res, next) => {
  try {
    const { data, error } = await supabase.from('moods').select('*').order('name');
    if (error) throw error;
    res.json({ success: true, moods: data });
  } catch (err) {
    next(err);
  }
};

const logMood = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { mood_id, log_date, intensity, notes } = req.body;

    if (!mood_id || !log_date) {
      return res.status(400).json({ success: false, message: 'mood_id and log_date are required' });
    }

    const { data, error } = await supabase
      .from('mood_logs')
      .insert([{ user_id: userId, mood_id, log_date, intensity: intensity || 'MEDIUM', notes }])
      .select('*, moods(name, icon_name)')
      .single();

    if (error) throw error;
    res.status(201).json({ success: true, message: 'Mood logged successfully', moodLog: data });
  } catch (err) {
    next(err);
  }
};

const getMoodHistory = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data, error } = await supabase
      .from('mood_logs')
      .select('*, moods(name, icon_name)')
      .eq('user_id', userId)
      .order('log_date', { ascending: false });

    if (error) throw error;
    res.json({ success: true, history: data });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getMoods,
  logMood,
  getMoodHistory
};
