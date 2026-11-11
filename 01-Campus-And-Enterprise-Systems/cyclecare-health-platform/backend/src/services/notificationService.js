const supabase = require('../config/supabase');
const { exec } = require('child_process');
const fs = require('fs');

async function sendProductCampaignNotification({
  productId,
  title,
  body,
  imageUrl,
  targetAudience = 'ALL'
}) {
  const deepLink = `cyclecare://product/${productId}`;

  // 1. Record campaign in Supabase database
  let campaign = null;
  try {
    const { data, error } = await supabase
      .from('notification_campaigns')
      .insert([{
        product_id: productId,
        title: title || 'New care essential available',
        body: body || 'Check out the latest addition to CycleCare Store.',
        image_url: imageUrl || null,
        deep_link: deepLink,
        target_audience: targetAudience,
        status: 'SENT',
        sent_at: new Date(),
        sent_count: 1
      }])
      .select()
      .single();

    if (!error) campaign = data;
  } catch (err) {
    console.error('Failed to save notification campaign:', err.message);
  }

  // 2. Insert into user notifications list
  try {
    await supabase.from('notifications').insert([{
      title: title || 'New care essential available',
      body: body || 'Check out the latest addition to CycleCare Store.',
      type: 'PRODUCT_ANNOUNCEMENT',
      metadata: {
        product_id: productId,
        deep_link: deepLink,
        image_url: imageUrl
      }
    }]);
  } catch (err) {
    console.error('Failed to insert user notification:', err.message);
  }

  // 3. Dispatch to connected device via ADB broadcast for real-time mobile push
  try {
    const adbPath = process.env.ADB_PATH || 'C:\\Users\\abdul\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe';
    if (fs.existsSync(adbPath)) {
      const cleanTitle = (title || 'New care essential available').replace(/"/g, '\\"');
      const cleanBody = (body || 'Check out the latest addition to CycleCare Store.').replace(/"/g, '\\"');
      const cleanImg = imageUrl ? imageUrl.replace(/"/g, '\\"') : '';
      const cmd = `"${adbPath}" shell am broadcast -a com.cyclecare.ACTION_STORE_PRODUCT_ADDED -p com.cyclecare --es name "${cleanTitle}" --es price "199" --es product_id "${productId}" --es image_url "${cleanImg}" --es deep_link "${deepLink}"`;
      exec(cmd, (err) => {
        if (!err) console.log('Dispatched local notification broadcast to phone');
      });
    }
  } catch (_) {}

  return {
    success: true,
    campaignId: campaign ? campaign.id : null,
    deepLink,
    title,
    body
  };
}

async function sendChatPushNotification({
  senderId,
  senderName,
  receiverId,
  messageText,
  connectionId,
  messageType = 'TEXT'
}) {
  try {
    const cleanSender = senderName || 'CycleCare Circle';
    const cleanText = messageText || 'Sent a new message';

    // 1. Record in notifications table
    if (receiverId) {
      await supabase.from('notifications').insert([{
        user_id: receiverId,
        title: cleanSender,
        body: cleanText,
        type: 'CHAT_MESSAGE',
        metadata: {
          connection_id: connectionId,
          sender_id: senderId,
          message_type: messageType
        }
      }]).catch(() => {});
    }

    // 2. Query device tokens
    const pool = require('../config/db');
    const { rows: tokens } = await pool.query(
      `SELECT token FROM device_tokens WHERE user_id = $1 AND is_active = true`,
      [receiverId]
    ).catch(() => ({ rows: [] }));

    // 3. Dispatch via ADB broadcast for connected phone/emulator
    try {
      const adbPath = process.env.ADB_PATH || 'C:\\Users\\abdul\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe';
      if (fs.existsSync(adbPath)) {
        const safeName = cleanSender.replace(/"/g, '\\"');
        const safeText = cleanText.replace(/"/g, '\\"');
        const cmd = `"${adbPath}" shell am broadcast -a com.cyclecare.ACTION_CHAT_MESSAGE_RECEIVED -p com.cyclecare --es sender_name "${safeName}" --es message_text "${safeText}" --es connection_id "${connectionId || ''}" --es sender_id "${senderId || ''}"`;
        exec(cmd, (err) => {
          if (!err) console.log('Dispatched chat notification broadcast to phone');
        });
      }
    } catch (_) {}

    return {
      success: true,
      tokenCount: tokens.length
    };
  } catch (err) {
    console.error('Failed to send chat push notification:', err.message);
    return { success: false, error: err.message };
  }
}

module.exports = {
  sendProductCampaignNotification,
  sendChatPushNotification
};
