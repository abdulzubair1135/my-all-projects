import { Router } from 'express';
import { DepartmentController } from '../controllers/department.controller';
import { authenticateJwt } from '../middleware/auth.middleware';
import { requireRoles } from '../middleware/rbac.middleware';
import { logAudit } from '../middleware/audit.middleware';
import { UserRole } from '../constants/enums';

const router = Router();

router.use(authenticateJwt);

router.get('/', DepartmentController.getAllDepartments);
router.get('/:id', DepartmentController.getDepartmentById);

// Admin & Super Admin write actions
router.post(
  '/',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('CREATE_DEPARTMENT', 'Department'),
  DepartmentController.createDepartment
);

router.put(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN, UserRole.PRINCIPAL),
  logAudit('UPDATE_DEPARTMENT', 'Department'),
  DepartmentController.updateDepartment
);

router.delete(
  '/:id',
  requireRoles(UserRole.SUPER_ADMIN),
  logAudit('DELETE_DEPARTMENT', 'Department'),
  DepartmentController.deleteDepartment
);

export const departmentRoutes = router;
