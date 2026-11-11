import { notificationRepository } from '../repositories/notification.repository.js';
import { AppError } from '../middleware/error.middleware.js';

export const notificationController = {
  async getNotifications(req, res, next) {
    try {
      const list = await notificationRepository.getUserNotifications(req.user.id);
      res.status(200).json({
        success: true,
        data: list
      });
    } catch (err) {
      next(err);
    }
  },

  async markAsRead(req, res, next) {
    try {
      const id = Number(req.params.id);
      const success = await notificationRepository.markAsRead(id, req.user.id);
      
      if (!success) {
        throw new AppError('Notification not found.', 404);
      }

      res.status(200).json({
        success: true,
        message: 'Notification marked as read.'
      });
    } catch (err) {
      next(err);
    }
  },

  async markAllAsRead(req, res, next) {
    try {
      await notificationRepository.markAllAsRead(req.user.id);
      res.status(200).json({
        success: true,
        message: 'All notifications marked as read.'
      });
    } catch (err) {
      next(err);
    }
  }
};
