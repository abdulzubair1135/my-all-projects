import { Router } from 'express';
import authRoutes from './auth.routes.js';
import userRoutes from './user.routes.js';
import categoryRoutes from './category.routes.js';
import listingRoutes from './listing.routes.js';
import bookingRoutes from './booking.routes.js';
import reviewRoutes from './review.routes.js';
import wishlistRoutes from './wishlist.routes.js';
import chatRoutes from './chat.routes.js';
import notificationRoutes from './notification.routes.js';
import adminRoutes from './admin.routes.js';
import compatibilityRoutes from './compatibility.routes.js';

const router = Router();

// Version 1 Routes
router.use('/v1/auth', authRoutes);
router.use('/v1/users', userRoutes);
router.use('/v1/categories', categoryRoutes);
router.use('/v1/listings', listingRoutes);
router.use('/v1/bookings', bookingRoutes);
router.use('/v1/reviews', reviewRoutes);
router.use('/v1/wishlist', wishlistRoutes);
router.use('/v1/chats', chatRoutes);
router.use('/v1/notifications', notificationRoutes);
router.use('/v1/admin', adminRoutes);

// Backwards compatibility layer directly under /api
router.use('/', compatibilityRoutes);

export default router;
