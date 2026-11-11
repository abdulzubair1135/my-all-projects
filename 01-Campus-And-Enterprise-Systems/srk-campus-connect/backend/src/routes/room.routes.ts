import { Router } from 'express';
import { RoomController } from '../controllers/room.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

router.get('/', RoomController.getAllRooms);
router.get('/verify-qr', RoomController.getRoomByQr);
router.get('/:id', RoomController.getRoomById);

router.post(
  '/',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('CREATE_ROOM', 'Room'),
  RoomController.createRoom
);

router.put(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('UPDATE_ROOM', 'Room'),
  RoomController.updateRoom
);

router.patch(
  '/:id/status',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL, UserRole.FACULTY),
  logAudit('UPDATE_ROOM_STATUS', 'Room'),
  RoomController.updateRoomStatus
);

export const roomRoutes = router;
