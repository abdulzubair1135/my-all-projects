import { Department, IDepartment } from '../models/Department';

export class DepartmentService {
  static async createDepartment(name: string, code: string, hodId?: string): Promise<IDepartment> {
    const existing = await Department.findOne({ $or: [{ name }, { code: code.toUpperCase() }] });
    if (existing) {
      throw new Error('Department with same name or code already exists');
    }
    return await Department.create({
      name,
      code: code.toUpperCase(),
      hodId
    });
  }

  static async getAllDepartments(): Promise<IDepartment[]> {
    return await Department.find({ isActive: true }).populate('hodId', 'userId designation');
  }

  static async getDepartmentById(id: string): Promise<IDepartment | null> {
    return await Department.findById(id).populate('hodId');
  }

  static async updateDepartment(id: string, updateData: Partial<IDepartment>): Promise<IDepartment | null> {
    if (updateData.code) {
      updateData.code = updateData.code.toUpperCase();
    }
    return await Department.findByIdAndUpdate(id, updateData, { new: true, runValidators: true });
  }

  static async deleteDepartment(id: string): Promise<IDepartment | null> {
    return await Department.findByIdAndUpdate(id, { isActive: false }, { new: true });
  }
}
