import { User } from '../models/User';
import { Faculty } from '../models/Faculty';
import { Student } from '../models/Student';
import { Room } from '../models/Room';
import { Subject } from '../models/Subject';
import { Department } from '../models/Department';
import { ClassSession } from '../models/ClassSession';
import { FacultyStatus, ClassSessionStatus } from '../constants/enums';

export class AdminService {
  /**
   * Unified search across students, faculty, rooms, and subjects
   */
  static async searchCampus(query: string): Promise<{
    faculty: any[];
    students: any[];
    rooms: any[];
    subjects: any[];
  }> {
    const regex = new RegExp(query, 'i');

    const [facultyUsers, studentUsers, rooms, subjects] = await Promise.all([
      User.find({ name: regex, role: 'FACULTY' }).select('_id'),
      User.find({ name: regex, role: 'STUDENT' }).select('_id'),
      Room.find({ $or: [{ roomNumber: regex }, { building: regex }] }).populate('departmentId', 'name code'),
      Subject.find({ $or: [{ name: regex }, { code: regex }] }).populate('departmentId', 'name code')
    ]);

    const facultyUserIds = facultyUsers.map(u => u._id);
    const studentUserIds = studentUsers.map(u => u._id);

    const [faculty, students] = await Promise.all([
      Faculty.find({
        $or: [{ userId: { $in: facultyUserIds } }, { employeeId: regex }]
      })
        .populate('userId', 'name email phone')
        .populate('departmentId', 'name code')
        .populate('currentLocation.roomId', 'roomNumber building'),
      Student.find({
        $or: [{ userId: { $in: studentUserIds } }, { enrollmentNo: regex }]
      })
        .populate('userId', 'name email phone')
        .populate('departmentId', 'name code')
    ]);

    return { faculty, students, rooms, subjects };
  }

  /**
   * Campus overview dashboard metrics
   */
  static async getCampusOverview(): Promise<{
    faculty: { inClass: number; available: number; busy: number; offline: number; total: number };
    classes: { running: number; upcoming: number; completed: number; total: number };
    students: { total: number; active: number };
    rooms: { occupied: number; available: number; total: number };
  }> {
    const [
      facultyInClass,
      facultyAvailable,
      facultyBusy,
      facultyOffline,
      totalFaculty,
      runningClasses,
      completedClasses,
      totalClasses,
      totalStudents,
      activeStudents,
      occupiedRooms,
      totalRooms
    ] = await Promise.all([
      Faculty.countDocuments({ currentStatus: FacultyStatus.IN_CLASS }),
      Faculty.countDocuments({ currentStatus: FacultyStatus.AVAILABLE }),
      Faculty.countDocuments({ currentStatus: { $in: [FacultyStatus.BUSY, FacultyStatus.MEETING] } }),
      Faculty.countDocuments({ currentStatus: FacultyStatus.OFFLINE }),
      Faculty.countDocuments(),
      ClassSession.countDocuments({ status: ClassSessionStatus.ACTIVE }),
      ClassSession.countDocuments({ status: ClassSessionStatus.ENDED }),
      ClassSession.countDocuments(),
      Student.countDocuments(),
      Student.countDocuments({ status: 'ACTIVE' }),
      Room.countDocuments({ status: 'OCCUPIED' }),
      Room.countDocuments()
    ]);

    return {
      faculty: {
        inClass: facultyInClass,
        available: facultyAvailable,
        busy: facultyBusy,
        offline: facultyOffline,
        total: totalFaculty
      },
      classes: {
        running: runningClasses,
        upcoming: Math.max(0, totalClasses - runningClasses - completedClasses),
        completed: completedClasses,
        total: totalClasses
      },
      students: {
        total: totalStudents,
        active: activeStudents
      },
      rooms: {
        occupied: occupiedRooms,
        available: Math.max(0, totalRooms - occupiedRooms),
        total: totalRooms
      }
    };
  }
}
