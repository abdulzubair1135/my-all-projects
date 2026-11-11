const supabase = require('../config/supabase');

const getReminders = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { data, error } = await supabase.from('reminders').select('*').eq('user_id', userId).order('created_at', { ascending: false });
    if (error) throw error;
    res.json({ success: true, reminders: data });
  } catch (err) {
    next(err);
  }
};

const createReminder = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { type, title, scheduled_time, days_before, enabled } = req.body;

    if (!type || !title) {
      return res.status(400).json({ success: false, message: 'type and title are required' });
    }

    const { data, error } = await supabase
      .from('reminders')
      .insert([{
        user_id: userId,
        type,
        title,
        scheduled_time: scheduled_time || '09:00:00',
        days_before: days_before !== undefined ? days_before : 2,
        enabled: enabled !== undefined ? enabled : true
      }])
      .select()
      .single();

    if (error) throw error;
    res.status(201).json({ success: true, message: 'Reminder created', reminder: data });
  } catch (err) {
    next(err);
  }
};

const updateReminder = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const reminderId = req.params.id;
    const { title, scheduled_time, days_before, enabled } = req.body;

    const { data, error } = await supabase
      .from('reminders')
      .update({ title, scheduled_time, days_before, enabled, updated_at: new Date() })
      .eq('id', reminderId)
      .eq('user_id', userId)
      .select()
      .single();

    if (error) throw error;
    res.json({ success: true, message: 'Reminder updated', reminder: data });
  } catch (err) {
    next(err);
  }
};

const deleteReminder = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const reminderId = req.params.id;

    const { error } = await supabase.from('reminders').delete().eq('id', reminderId).eq('user_id', userId);
    if (error) throw error;

    res.json({ success: true, message: 'Reminder deleted' });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getReminders,
  createReminder,
  updateReminder,
  deleteReminder
};
