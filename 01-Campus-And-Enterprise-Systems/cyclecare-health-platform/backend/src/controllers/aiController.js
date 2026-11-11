const supabase = require('../config/supabase');

const chatWithAI = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { message, include_user_cycle_data } = req.body;

    if (!message) return res.status(400).json({ success: false, message: 'Message prompt is required' });

    let userContextSummary = "";
    if (include_user_cycle_data) {
      const { data: settings } = await supabase.from('cycle_settings').select('*').eq('user_id', userId).single();
      userContextSummary = `[User Context Provided with Consent: Baseline Average Cycle Length = ${settings?.average_cycle_length || 28} days]. `;
    }

    // Safety filter to prevent diagnostic claims
    const lowerMessage = message.toLowerCase();
    let replyText = "";

    const disclaimer = "\n\n*Note: I am an educational wellness assistant, not a doctor. Please consult a qualified healthcare provider for medical advice or diagnosis.*";

    if (lowerMessage.includes('diagnose') || lowerMessage.includes('prescribe') || lowerMessage.includes('medicine for severe')) {
      replyText = "I cannot provide medical diagnoses or prescribe medications. If you are experiencing severe pain, abnormal bleeding, or medical concerns, please consult a qualified healthcare professional right away." + disclaimer;
    } else if (lowerMessage.includes('pms') || lowerMessage.includes('premenstrual')) {
      replyText = `${userContextSummary}PMS (Premenstrual Syndrome) refers to emotional and physical symptoms that many individuals experience 1-2 weeks before their period, such as mild cramps, mood shifts, bloating, and fatigue. Balanced nutrition, hydration, light exercise, and warm compresses can help ease comfort.` + disclaimer;
    } else if (lowerMessage.includes('cramp') || lowerMessage.includes('pain')) {
      replyText = `${userContextSummary}Menstrual cramps (dysmenorrhea) occur when the uterine muscles contract to shed its lining. Natural comfort techniques include applying heat patches or hot water bags to the abdomen, sipping chamomile tea, and doing gentle yoga stretches.` + disclaimer;
    } else if (lowerMessage.includes('cycle') || lowerMessage.includes('what is period')) {
      replyText = `${userContextSummary}A menstrual cycle is the monthly series of changes a woman's body goes through in preparation for the possibility of pregnancy. A typical cycle ranges from 21 to 35 days, averaging around 28 days.` + disclaimer;
    } else {
      replyText = `${userContextSummary}CycleCare Educational Wellness Assistant: Thank you for your question about menstrual health ("${message}"). For optimal cycle wellness, track your cycle regularly, prioritize sleep, stay hydrated, and maintain balanced nutrition.` + disclaimer;
    }

    res.json({
      success: true,
      role: 'assistant',
      content: replyText,
      dataUsed: !!include_user_cycle_data
    });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  chatWithAI
};
