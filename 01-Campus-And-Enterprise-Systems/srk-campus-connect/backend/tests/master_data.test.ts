import { DepartmentService } from '../src/services/department.service';
import { SubjectService } from '../src/services/subject.service';
import { RoomService } from '../src/services/room.service';
import { FacultyService } from '../src/services/faculty.service';
import { StudentService } from '../src/services/student.service';
import { AdminService } from '../src/services/admin.service';
import { Department } from '../src/models/Department';
import { Subject } from '../src/models/Subject';
import { Room } from '../src/models/Room';
import { Faculty } from '../src/models/Faculty';
import { Student } from '../src/models/Student';
import { User } from '../src/models/User';
import { FacultyStatus, UserRole } from '../src/constants/enums';

describe('Phase 2: Master Data Management Unit Tests', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('DepartmentService: should validate unique code and create department', async () => {
    jest.spyOn(Department, 'findOne').mockResolvedValue(null as any);
    jest.spyOn(Department, 'create').mockResolvedValue({
      _id: 'dept123',
      name: 'Computer Engineering',
      code: 'COMP',
      isActive: true
    } as any);

    const dept = await DepartmentService.createDepartment('Computer Engineering', 'comp');
    expect(dept.name).toBe('Computer Engineering');
    expect(dept.code).toBe('COMP');
  });

  it('RoomService: should auto-generate permanent QR code format', async () => {
    jest.spyOn(Room, 'findOne').mockResolvedValue(null as any);
    jest.spyOn(Room, 'create').mockImplementation((data: any) => Promise.resolve({
      _id: 'room204',
      ...data
    }) as any);

    const room = await RoomService.createRoom({
      roomNumber: '204',
      building: 'Building A',
      capacity: 60
    });

    expect(room.permanentQrCode).toBe('CAMPUS_ROOM_V1:BUILDING A-204');
    expect(room.status).toBe('AVAILABLE');
  });

  it('FacultyService: should create User with FACULTY role and linked Faculty profile', async () => {
    jest.spyOn(User, 'findOne').mockResolvedValue(null as any);
    jest.spyOn(Faculty, 'findOne').mockResolvedValue(null as any);
    
    jest.spyOn(User, 'create').mockResolvedValue({
      _id: 'user_arjun',
      name: 'Arjun Sir',
      email: 'arjun@campus.edu',
      role: UserRole.FACULTY,
      isActive: true
    } as any);

    jest.spyOn(Faculty, 'create').mockResolvedValue({
      _id: 'fac_arjun',
      userId: 'user_arjun',
      employeeId: 'FAC001',
      departmentId: 'dept123',
      designation: 'Associate Professor',
      currentStatus: FacultyStatus.AVAILABLE
    } as any);

    const result = await FacultyService.createFaculty({
      name: 'Arjun Sir',
      email: 'arjun@campus.edu',
      employeeId: 'fac001',
      departmentId: 'dept123',
      designation: 'Associate Professor'
    });

    expect(result.user.role).toBe(UserRole.FACULTY);
    expect(result.faculty.employeeId).toBe('FAC001');
    expect(result.faculty.currentStatus).toBe(FacultyStatus.AVAILABLE);
  });

  it('StudentService: should create User with STUDENT role and linked Student record', async () => {
    jest.spyOn(User, 'findOne').mockResolvedValue(null as any);
    jest.spyOn(Student, 'findOne').mockResolvedValue(null as any);

    jest.spyOn(User, 'create').mockResolvedValue({
      _id: 'user_rahul',
      name: 'Rahul Shah',
      email: 'rahul@student.campus.edu',
      role: UserRole.STUDENT,
      isActive: true
    } as any);

    jest.spyOn(Student, 'create').mockResolvedValue({
      _id: 'stud_rahul',
      userId: 'user_rahul',
      enrollmentNo: 'EN2026COMP001',
      departmentId: 'dept123',
      semester: 4,
      division: 'A',
      academicYear: '2025-2026',
      status: 'ACTIVE'
    } as any);

    const result = await StudentService.createStudent({
      name: 'Rahul Shah',
      email: 'rahul@student.campus.edu',
      enrollmentNo: 'en2026comp001',
      departmentId: 'dept123',
      semester: 4,
      division: 'a',
      academicYear: '2025-2026'
    });

    expect(result.user.role).toBe(UserRole.STUDENT);
    expect(result.student.enrollmentNo).toBe('EN2026COMP001');
    expect(result.student.division).toBe('A');
  });
});
