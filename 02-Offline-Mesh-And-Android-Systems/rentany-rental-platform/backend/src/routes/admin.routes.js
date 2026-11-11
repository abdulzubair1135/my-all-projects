import { Router } from 'express';
import { adminController } from '../controllers/admin.controller.js';
import { categoryController } from '../controllers/category.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { adminOnly } from '../middleware/admin.middleware.js';

const router = Router();

// Apply auth protection and admin restriction globally to all admin routes
router.use(protect);
router.use(adminOnly);

// Dashboard
router.get('/dashboard', adminController.getDashboard);
router.get('/users', adminController.getAllUsers);
router.get('/listings', adminController.getAllListings);
router.get('/bookings', adminController.getAllBookings);
router.get('/payments', adminController.getAllPayments);

// All remaining schema tables
router.get('/categories', adminController.getAllCategories);
router.get('/reviews', adminController.getAllReviews);
router.get('/deposits', adminController.getAllDeposits);
router.get('/refunds', adminController.getAllRefunds);
router.get('/notifications', adminController.getAllNotifications);
router.get('/wishlists', adminController.getAllWishlists);
router.get('/conversations', adminController.getAllConversations);
router.get('/messages', adminController.getAllMessages);
router.get('/banners', adminController.getAllBanners);
router.get('/listing-images', adminController.getAllListingImages);

// User moderation & CRUD
router.post('/users/:id/suspend', adminController.suspendUser);
router.post('/users/:id/activate', adminController.activateUser);
router.post('/users', adminController.createAdminUser);
router.put('/users/:id', adminController.updateAdminUser);
router.delete('/users/:id', adminController.deleteAdminUser);

// Listings moderation & CRUD
router.post('/listings/:id/approve', adminController.approveListing);
router.post('/listings/:id/reject', adminController.rejectListing);
router.post('/listings', adminController.createAdminListing);
router.put('/listings/:id', adminController.updateAdminListing);
router.delete('/listings/:id', adminController.deleteAdminListing);

// Reports moderation
router.get('/reports', adminController.getReports);
router.post('/reports/:id/resolve', adminController.resolveReport);

// Audit logs
router.get('/audit-logs', adminController.getAuditLogs);

// Categories CRUD
router.post('/categories', categoryController.createCategory);
router.put('/categories/:id', categoryController.updateCategory);
router.delete('/categories/:id', categoryController.deleteCategory);

// Banners CRUD
router.post('/banners', adminController.createBanner);
router.put('/banners/:id', adminController.updateBanner);
router.delete('/banners/:id', adminController.deleteBanner);

export default router;
