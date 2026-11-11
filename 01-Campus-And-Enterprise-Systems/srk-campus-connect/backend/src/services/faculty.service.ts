import mongoose from 'mongoose';
import { Faculty, IFaculty } from '../models/Faculty';
import { User, IUser } from '../models/User';
import { UserRole, FacultyStatus } from '../constants/enums';

export class FacultyService {
  static async createFaculty(data: {
    name: string;
    email: string;
    phone?: string;
    password?: string;
    employeeId: string;
    departmentId: string;
    designation: string;
    subjects?: string[];
  }): Promise<{ user: IUser; faculty: IFaculty }> {
    const existingUser = await User.findOne({ email: data.email.toLowerCase() });
    if (existingUser) {
      throw new Error(`User with email ${data.email} already exists`);
    }

    const existingFaculty = await Faculty.findOne({ employeeId: data.employeeId.toUpperCase() });
    if (existingFaculty) {
      throw new Error(`Faculty with employee ID ${data.employeeId} already exists`);
    }

    const defaultPassword = data.password || 'Faculty@123';

    const user = await User.create({
      name: data.name,
      email: data.email.toLowerCase(),
      phone: data.phone,
      passwordHash: defaultPassword,
      role: UserRole.FACULTY,
      departmentId: data.departmentId,
      isActive: true
    });

    const faculty = await Faculty.create({
      userId: user._id,
      employeeId: data.employeeId.toUpperCase(),
      departmentId: data.departmentId,
      designation: data.designation,
      subjects: data.subjects || [],
      currentStatus: FacultyStatus.AVAILABLE,
      statusUpdatedAt: new Date()
    });

    return { user, faculty };
  }

  static async getAllFaculty(departmentId?: string): Promise<IFaculty[]> {
    const query: any = {};
    if (departmentId) query.departmentId = departmentId;
    return await Faculty.find(query)
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code')
      .populate('subjects', 'name code')
      .populate('currentLocation.roomId', 'roomNumber building');
  }

  static async getFacultyById(id: string): Promise<IFaculty | null> {
    return await Faculty.findById(id)
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code')
      .populate('subjects', 'name code')
      .populate('currentLocation.roomId', 'roomNumber building');
  }

  static async getFacultyByUserId(userId: string): Promise<IFaculty | null> {
    return await Faculty.findOne({ userId })
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code')
      .populate('subjects', 'name code')
      .populate('currentLocation.roomId', 'roomNumber building');
  }

  static async updateStatus(facultyId: string, status: FacultyStatus): Promise<IFaculty | null> {
    return await Faculty.findByIdAndUpdate(
      facultyId,
      {
        currentStatus: status,
        statusUpdatedAt: new Date()
      },
      { new: true }
    );
  }

  static async updatePresence(facultyId: string, roomId: string, confidence: number): Promise<IFaculty | null> {
    return await Faculty.findByIdAndUpdate(
      facultyId,
      {
        currentLocation: {
          roomId: new mongoose.Types.ObjectId(roomId),
          confidence,
          lastVerified: new Date()
        }
      },
      { new: true }
    );
  }
}
