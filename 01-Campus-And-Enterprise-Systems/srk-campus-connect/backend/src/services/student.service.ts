import { Student, IStudent } from '../models/Student';
import { User, IUser } from '../models/User';
import { UserRole } from '../constants/enums';

export class StudentService {
  static async createStudent(data: {
    name: string;
    email: string;
    phone?: string;
    password?: string;
    enrollmentNo: string;
    departmentId: string;
    semester: number;
    division: string;
    academicYear: string;
  }): Promise<{ user: IUser; student: IStudent }> {
    const existingUser = await User.findOne({ email: data.email.toLowerCase() });
    if (existingUser) {
      throw new Error(`User with email ${data.email} already exists`);
    }

    const existingStudent = await Student.findOne({ enrollmentNo: data.enrollmentNo.toUpperCase() });
    if (existingStudent) {
      throw new Error(`Student with enrollment number ${data.enrollmentNo} already exists`);
    }

    const defaultPassword = data.password || 'Student@123';

    const user = await User.create({
      name: data.name,
      email: data.email.toLowerCase(),
      phone: data.phone,
      passwordHash: defaultPassword,
      role: UserRole.STUDENT,
      departmentId: data.departmentId,
      isActive: true
    });

    const student = await Student.create({
      userId: user._id,
      enrollmentNo: data.enrollmentNo.toUpperCase(),
      departmentId: data.departmentId,
      semester: data.semester,
      division: data.division.toUpperCase(),
      academicYear: data.academicYear,
      status: 'ACTIVE'
    });

    return { user, student };
  }

  static async getStudents(filter: {
    departmentId?: string;
    semester?: number;
    division?: string;
    academicYear?: string;
  } = {}): Promise<IStudent[]> {
    const query: any = { status: 'ACTIVE' };
    if (filter.departmentId) query.departmentId = filter.departmentId;
    if (filter.semester) query.semester = filter.semester;
    if (filter.division) query.division = filter.division.toUpperCase();
    if (filter.academicYear) query.academicYear = filter.academicYear;

    return await Student.find(query)
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code');
  }

  static async getStudentById(id: string): Promise<IStudent | null> {
    return await Student.findById(id)
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code');
  }

  static async getStudentByUserId(userId: string): Promise<IStudent | null> {
    return await Student.findOne({ userId })
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code');
  }

  static async getStudentByEnrollmentNo(enrollmentNo: string): Promise<IStudent | null> {
    return await Student.findOne({ enrollmentNo: enrollmentNo.toUpperCase() })
      .populate('userId', 'name email phone avatarUrl isActive')
      .populate('departmentId', 'name code');
  }
}
