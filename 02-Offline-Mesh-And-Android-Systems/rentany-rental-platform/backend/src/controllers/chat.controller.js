import { chatRepository } from '../repositories/chat.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { AppError } from '../middleware/error.middleware.js';

export const chatController = {
  async getConversations(req, res, next) {
    try {
      const conversations = await chatRepository.findUserConversations(req.user.id);
      res.status(200).json({
        success: true,
        data: conversations
      });
    } catch (err) {
      next(err);
    }
  },

  async getMessages(req, res, next) {
    try {
      const conversationId = Number(req.params.conversationId);

      // Verify participant
      const isPart = await chatRepository.isParticipant(conversationId, req.user.id);
      if (!isPart) {
        throw new AppError('You are not authorized to view this conversation.', 403);
      }

      // Mark messages as read
      await chatRepository.markMessagesAsRead(conversationId, req.user.id);

      const messages = await chatRepository.getConversationMessages(conversationId);

      res.status(200).json({
        success: true,
        data: messages
      });
    } catch (err) {
      next(err);
    }
  },

  async sendMessage(req, res, next) {
    try {
      const { conversationId, listingId, messageText, messageType = 'text' } = req.body;
      const senderId = req.user.id;
      
      let finalConvoId = conversationId;
      let attachmentUrl = null;

      // Handle file attachments from multer upload to Cloudinary
      if (req.file) {
        const { uploadToCloudinary } = await import('../middleware/upload.middleware.js');
        const uploadResult = await uploadToCloudinary(req.file.buffer);
        attachmentUrl = uploadResult.secure_url;
      }

      // 1. If starting a new chat via a listing
      if (!finalConvoId && listingId) {
        const listing = await listingRepository.findById(listingId);
        if (!listing) {
          throw new AppError('Listing not found.', 404);
        }
        
        if (listing.owner_id === senderId) {
          throw new AppError('You cannot start a conversation with yourself.', 400);
        }

        finalConvoId = await chatRepository.getOrCreateConversation(listingId, senderId, listing.owner_id);
      }

      if (!finalConvoId) {
        throw new AppError('Conversation ID or Listing ID is required.', 400);
      }

      // 2. Validate participant
      const isPart = await chatRepository.isParticipant(finalConvoId, senderId);
      if (!isPart) {
        throw new AppError('You are not a participant in this conversation.', 403);
      }

      // 3. Create message
      const messageId = await chatRepository.createMessage(
        finalConvoId,
        senderId,
        messageText || '',
        messageType,
        attachmentUrl
      );

      res.status(201).json({
        success: true,
        message: 'Message sent successfully',
        data: {
          messageId,
          conversationId: finalConvoId,
          attachmentUrl
        }
      });
    } catch (err) {
      next(err);
    }
  }
};
