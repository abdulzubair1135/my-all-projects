import { Router } from 'express';
import { MeetingController } from '../controllers/meeting.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.post('/test-summon-push', async (req, res) => {
  const { FCMService } = await import('../services/fcm.service');
  const { SocketManager } = await import('../sockets/socket.manager');

  const payload = {
    id: `urgent_${Date.now()}`,
    type: 'URGENT_CABIN_CALL',
    callerName: 'Dr. Nirdesh Buch (Principal)',
    location: 'Principal Cabin P-01',
    reason: 'Emergency Academic Coordination & Committee Review',
    timestamp: new Date().toLocaleTimeString(),
    priority: 'URGENT'
  };

  // Broadcast via Socket.IO
  SocketManager.broadcastAll('meeting.new', payload);
  SocketManager.broadcastAll('radar.updated', { event: 'URGENT_SUMMON_DISPATCHED', payload });

  // Broadcast via FCM
  await FCMService.sendUrgentSummonNotification({
    facultyName: 'Prof. Nirali Thakkar',
    callerName: 'Dr. Nirdesh Buch (Principal)',
    location: 'Principal Cabin P-01',
    meetingId: payload.id,
    reason: payload.reason,
  });

  res.json({
    success: true,
    message: '🚨 Principal Urgent Summon push notification successfully dispatched!',
    data: payload
  });
});

router.use(authenticateJwt);

router.get('/', MeetingController.getMeetings);

// Principal creates meeting / urgent call request
router.post(
  '/request',
  requireRoles(UserRole.PRINCIPAL, UserRole.SUPER_ADMIN),
  logAudit('REQUEST_FACULTY_MEETING', 'MeetingRequest'),
  MeetingController.requestMeeting
);

router.post(
  '/urgent-call',
  requireRoles(UserRole.PRINCIPAL, UserRole.SUPER_ADMIN),
  logAudit('DISPATCH_URGENT_CALL', 'MeetingRequest'),
  MeetingController.requestMeeting
);

// Faculty quick responds (1-tap BUSY or ARRIVING)
router.post(
  '/:id/quick-respond',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN),
  logAudit('QUICK_RESPOND_MEETING', 'MeetingRequest'),
  MeetingController.quickRespondMeeting
);

// Faculty standard responds
router.patch(
  '/:id/respond',
  requireRoles(UserRole.FACULTY, UserRole.SUPER_ADMIN),
  logAudit('RESPOND_FACULTY_MEETING', 'MeetingRequest'),
  MeetingController.respondMeeting
);

export const meetingRoutes = router;
