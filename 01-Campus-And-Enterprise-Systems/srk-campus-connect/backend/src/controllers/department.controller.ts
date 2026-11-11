import { Request, Response, NextFunction } from 'express';
import { DepartmentService } from '../services/department.service';
import { ResponseUtil } from '../utils/response';

export class DepartmentController {
  static async createDepartment(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { name, code, hodId } = req.body;
      if (!name || !code) {
        ResponseUtil.error(res, 'Department name and code are required', 400);
        return;
      }
      const department = await DepartmentService.createDepartment(name, code, hodId);
      ResponseUtil.success(res, department, 'Department created successfully', 201);
    } catch (error: any) {
      next(error);
    }
  }

  static async getAllDepartments(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const departments = await DepartmentService.getAllDepartments();
      ResponseUtil.success(res, departments, 'Departments retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async getDepartmentById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const department = await DepartmentService.getDepartmentById(req.params.id);
      if (!department) {
        ResponseUtil.error(res, 'Department not found', 404);
        return;
      }
      ResponseUtil.success(res, department, 'Department retrieved successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async updateDepartment(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const department = await DepartmentService.updateDepartment(req.params.id, req.body);
      if (!department) {
        ResponseUtil.error(res, 'Department not found', 404);
        return;
      }
      ResponseUtil.success(res, department, 'Department updated successfully');
    } catch (error: any) {
      next(error);
    }
  }

  static async deleteDepartment(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const department = await DepartmentService.deleteDepartment(req.params.id);
      if (!department) {
        ResponseUtil.error(res, 'Department not found', 404);
        return;
      }
      ResponseUtil.success(res, { id: req.params.id }, 'Department deactivated successfully');
    } catch (error: any) {
      next(error);
    }
  }
}
