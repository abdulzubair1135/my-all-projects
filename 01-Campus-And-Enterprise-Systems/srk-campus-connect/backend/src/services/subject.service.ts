import { Subject, ISubject } from '../models/Subject';

export class SubjectService {
  static async createSubject(data: {
    name: string;
    code: string;
    departmentId: string;
    semester: number;
    credits?: number;
  }): Promise<ISubject> {
    const existing = await Subject.findOne({ code: data.code.toUpperCase() });
    if (existing) {
      throw new Error(`Subject with code ${data.code} already exists`);
    }

    return await Subject.create({
      name: data.name,
      code: data.code.toUpperCase(),
      departmentId: data.departmentId,
      semester: data.semester,
      credits: data.credits || 3
    });
  }

  static async getSubjects(filter: { departmentId?: string; semester?: number } = {}): Promise<ISubject[]> {
    const query: any = { isActive: true };
    if (filter.departmentId) query.departmentId = filter.departmentId;
    if (filter.semester) query.semester = filter.semester;
    return await Subject.find(query).populate('departmentId', 'name code');
  }

  static async getSubjectById(id: string): Promise<ISubject | null> {
    return await Subject.findById(id).populate('departmentId');
  }

  static async updateSubject(id: string, updateData: Partial<ISubject>): Promise<ISubject | null> {
    if (updateData.code) {
      updateData.code = updateData.code.toUpperCase();
    }
    return await Subject.findByIdAndUpdate(id, updateData, { new: true, runValidators: true });
  }

  static async deleteSubject(id: string): Promise<ISubject | null> {
    return await Subject.findByIdAndUpdate(id, { isActive: false }, { new: true });
  }
}
