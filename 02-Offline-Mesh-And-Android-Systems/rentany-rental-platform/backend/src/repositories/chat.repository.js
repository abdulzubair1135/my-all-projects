import pool from '../config/database.js';
import crypto from 'crypto';

export const chatRepository = {
  async isParticipant(conversationId, userId) {
    const [rows] = await pool.query(
      'SELECT 1 FROM conversation_participants WHERE conversation_id = ? AND user_id = ?',
      [conversationId, userId]
    );
    return rows.length > 0;
  },

  async findUserConversations(userId) {
    // Fetches conversations where user participates, with other participant's name and last message
    const [rows] = await pool.query(
      `SELECT c.id as conversation_id, c.uuid as conversation_uuid, c.created_at, c.updated_at,
              l.id as listing_id, l.title as listing_title,
              other_user.id as other_user_id, other_user.full_name as other_user_name, other_user.profile_image as other_user_image,
              last_msg.message as last_message_text, last_msg.created_at as last_message_time, last_msg.sender_id as last_message_sender_id
       FROM conversations c
       JOIN conversation_participants cp ON c.id = cp.conversation_id AND cp.user_id = ?
       LEFT JOIN listings l ON c.listing_id = l.id
       -- Join other participant
       JOIN conversation_participants cp_other ON c.id = cp_other.conversation_id AND cp_other.user_id != ?
       JOIN users other_user ON cp_other.user_id = other_user.id
       -- Subquery to fetch last message
       LEFT JOIN (
         SELECT m1.* FROM messages m1
         INNER JOIN (
           SELECT conversation_id, MAX(id) as max_id FROM messages WHERE deleted_at IS NULL GROUP BY conversation_id
         ) m2 ON m1.id = m2.max_id
       ) last_msg ON c.id = last_msg.conversation_id
       ORDER BY c.updated_at DESC`,
      [userId, userId]
    );
    return rows;
  },

  async getConversationMessages(conversationId) {
    const [rows] = await pool.query(
      `SELECT m.id, m.conversation_id, m.sender_id, u.full_name as sender_name, m.message, m.message_type, m.attachment_url, m.is_read, m.created_at
       FROM messages m
       JOIN users u ON m.sender_id = u.id
       WHERE m.conversation_id = ? AND m.deleted_at IS NULL
       ORDER BY m.id ASC`,
      [conversationId]
    );
    return rows;
  },

  async createMessage(conversationId, senderId, message, messageType = 'text', attachmentUrl = null) {
    const [res] = await pool.query(
      `INSERT INTO messages (conversation_id, sender_id, message, message_type, attachment_url, is_read)
       VALUES (?, ?, ?, ?, ?, 0)`,
      [conversationId, senderId, message, messageType, attachmentUrl]
    );
    
    // Update the conversation's updated_at timestamp to bring it to the top of list
    await pool.query('UPDATE conversations SET updated_at = NOW() WHERE id = ?', [conversationId]);
    
    return res.insertId;
  },

  async markMessagesAsRead(conversationId, userId) {
    // Mark messages sent by others in this conversation as read
    await pool.query(
      'UPDATE messages SET is_read = 1 WHERE conversation_id = ? AND sender_id != ? AND is_read = 0',
      [conversationId, userId]
    );
    
    // Update participant's last_read_at timestamp
    await pool.query(
      'UPDATE conversation_participants SET last_read_at = NOW() WHERE conversation_id = ? AND user_id = ?',
      [conversationId, userId]
    );
  },

  async getOrCreateConversation(listingId, renterId, ownerId) {
    // Verify if conversation already exists for this listing between these two users
    const [existing] = await pool.query(
      `SELECT c.id FROM conversations c
       JOIN conversation_participants cp1 ON c.id = cp1.conversation_id AND cp1.user_id = ?
       JOIN conversation_participants cp2 ON c.id = cp2.conversation_id AND cp2.user_id = ?
       WHERE c.listing_id = ?`,
      [renterId, ownerId, listingId]
    );

    if (existing.length > 0) {
      return existing[0].id;
    }

    // Create a new conversation using transactions
    const connection = await pool.getConnection();
    try {
      await connection.beginTransaction();
      
      const uuid = crypto.randomUUID();
      const [convoRes] = await connection.query(
        'INSERT INTO conversations (uuid, listing_id) VALUES (?, ?)',
        [uuid, listingId]
      );
      
      const convoId = convoRes.insertId;
      
      // Add participants
      await connection.query(
        'INSERT INTO conversation_participants (conversation_id, user_id) VALUES (?, ?), (?, ?)',
        [convoId, renterId, convoId, ownerId]
      );
      
      await connection.commit();
      return convoId;
    } catch (err) {
      await connection.rollback();
      throw err;
    } finally {
      connection.release();
    }
  }
};
