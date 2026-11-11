const express = require('express');
const router = express.Router();
const partnerController = require('../controllers/partnerController');
const authenticateToken = require('../middleware/auth');

// Public invite validation
router.get('/invite/:token', partnerController.validateInvite);

// All other partner routes require authentication
router.use(authenticateToken);

// Search & Invites
router.get('/search', partnerController.searchPartner);
router.post('/invite', partnerController.createInvite);

// Connections Lifecycle
router.post('/request', partnerController.sendConnectionRequest);
router.get('/requests', partnerController.listRequests);
router.get('/connections', partnerController.listRequests);
router.post('/requests/:id/accept', partnerController.acceptRequest);
router.post('/requests/:id/decline', partnerController.declineRequest);
router.delete('/:connectionId', partnerController.revokeConnection);
router.delete('/connections/:connectionId', partnerController.revokeConnection);
router.post('/:connectionId/block', partnerController.blockPartner);
router.post('/connections/:connectionId/block', partnerController.blockPartner);
router.patch('/:connectionId/relationship', partnerController.updateRelationship);
router.put('/:connectionId/relationship', partnerController.updateRelationship);
router.patch('/connections/:connectionId/relationship', partnerController.updateRelationship);
router.put('/connections/:connectionId/relationship', partnerController.updateRelationship);
router.get('/:connectionId/audit-trail', partnerController.getAuditTrail);
router.get('/connections/:connectionId/audit-trail', partnerController.getAuditTrail);

// Granular Permissions Management
router.get('/:connectionId/permissions', partnerController.getPermissions);
router.put('/:connectionId/permissions', partnerController.updatePermissions);
router.get('/connections/:connectionId/permissions', partnerController.getPermissions);
router.put('/connections/:connectionId/permissions', partnerController.updatePermissions);

// Permitted Data Access (Server-side enforced)
router.get('/:connectionId/member-status', partnerController.getMemberStatus);
router.get('/connections/:connectionId/member-status', partnerController.getMemberStatus);
router.get('/:connectionId/shared-cycle', partnerController.getSharedCycle);
router.get('/connections/:connectionId/shared-cycle', partnerController.getSharedCycle);
router.get('/:connectionId/care-kit', partnerController.getSharedCareKit);
router.get('/:connectionId/wishlist', partnerController.getSharedWishlist);
router.get('/:connectionId/shared-address', partnerController.getSharedAddress);

// Care Package Order
router.post('/:connectionId/care-package', partnerController.createCarePackage);

module.exports = router;
