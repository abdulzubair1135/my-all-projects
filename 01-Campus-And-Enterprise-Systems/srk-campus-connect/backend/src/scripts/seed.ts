import mongoose from 'mongoose';
import { connectDatabase, disconnectDatabase } from '../config/database';
import { User } from '../models/User';
import { Student } from '../models/Student';
import { Faculty } from '../models/Faculty';
import { Department } from '../models/Department';
import { Subject } from '../models/Subject';
import { Room } from '../models/Room';
import { Timetable } from '../models/Timetable';
import { UserRole, FacultyStatus, RoomStatus } from '../constants/enums';
import { logger } from '../utils/logger';

export const seedDatabase = async (): Promise<void> => {
  logger.info('Resetting SRK Institute database with full real students roster...');
  await Promise.all([
    User.deleteMany({}),
    Student.deleteMany({}),
    Faculty.deleteMany({}),
    Department.deleteMany({}),
    Subject.deleteMany({}),
    Room.deleteMany({}),
    Timetable.deleteMany({})
  ]);

  logger.info('Creating SRK Departments...');
  const bbaDept = await Department.create({ name: 'Bachelor of Business Administration', code: 'BBA' });
  const bcaDept = await Department.create({ name: 'Bachelor of Computer Applications', code: 'BCA' });
  const mbaDept = await Department.create({ name: 'Master of Business Administration', code: 'MBA' });

  logger.info('Creating SRK Lecture Halls (1 to 10) & Computer Labs...');
  const rooms = {
    lh1: await Room.create({ roomNumber: 'Lecture Hall 1', building: 'Academic Wing', capacity: 70, departmentId: bbaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-1', status: RoomStatus.OCCUPIED }),
    lh2: await Room.create({ roomNumber: 'Lecture Hall 2', building: 'Academic Wing', capacity: 70, departmentId: bbaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-2', status: RoomStatus.OCCUPIED }),
    lh3: await Room.create({ roomNumber: 'Lecture Hall 3', building: 'Academic Wing', capacity: 70, departmentId: bcaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-3', status: RoomStatus.OCCUPIED }),
    lh4: await Room.create({ roomNumber: 'Lecture Hall 4', building: 'Academic Wing', capacity: 70, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-4', status: RoomStatus.AVAILABLE }),
    lh5: await Room.create({ roomNumber: 'Lecture Hall 5', building: 'Academic Wing', capacity: 70, departmentId: bcaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-5', status: RoomStatus.OCCUPIED }),
    lh6: await Room.create({ roomNumber: 'Lecture Hall 6', building: 'Academic Wing', capacity: 70, departmentId: bbaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-6', status: RoomStatus.OCCUPIED }),
    lh7: await Room.create({ roomNumber: 'Lecture Hall 7', building: 'Academic Wing', capacity: 70, departmentId: bbaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-7', status: RoomStatus.OCCUPIED }),
    lh8: await Room.create({ roomNumber: 'Lecture Hall 8', building: 'Academic Wing', capacity: 70, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-8', status: RoomStatus.AVAILABLE }),
    lh9: await Room.create({ roomNumber: 'Lecture Hall 9', building: 'Academic Wing', capacity: 70, departmentId: bcaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-9', status: RoomStatus.OCCUPIED }),
    lh10: await Room.create({ roomNumber: 'Lecture Hall 10', building: 'Academic Wing', capacity: 70, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LH-10', status: RoomStatus.AVAILABLE }),
    
    labWeb: await Room.create({ roomNumber: 'Web & Cyber Lab', building: 'IT Wing', capacity: 45, departmentId: bcaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LAB-WEB', status: RoomStatus.AVAILABLE }),
    labPython: await Room.create({ roomNumber: 'Python & App Lab', building: 'IT Wing', capacity: 45, departmentId: bcaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LAB-PY', status: RoomStatus.AVAILABLE }),
    labDbms: await Room.create({ roomNumber: 'DBMS & C Lab', building: 'IT Wing', capacity: 45, departmentId: bcaDept._id, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-LAB-DBMS', status: RoomStatus.AVAILABLE }),
    principalCabin: await Room.create({ roomNumber: 'Principal Office', building: 'Admin Block', capacity: 15, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-ADMIN-PRINCIPAL', status: RoomStatus.OCCUPIED }),
    campusHeadCabin: await Room.create({ roomNumber: 'Campus Head Office', building: 'Admin Block', capacity: 15, permanentQrCode: 'CAMPUS_ROOM_V1:SRK-ADMIN-HEAD', status: RoomStatus.OCCUPIED })
  };

  logger.info('Creating Real Authorities: Dr. Nirdesh Buch (Principal) & Prof. Surbhi Ahir (Campus Head)...');
  await User.create({
    name: 'Dr. Nirdesh Buch (NB)',
    email: 'nirdesh.buch@srk.edu',
    phone: '+919800000001',
    passwordHash: 'Principal@123',
    role: UserRole.PRINCIPAL,
    isActive: true
  });

  await User.create({
    name: 'Prof. Surbhi Ahir (SA)',
    email: 'surbhi.ahir@srk.edu',
    phone: '+919800000002',
    passwordHash: 'CampusHead@123',
    role: UserRole.SUPER_ADMIN,
    isActive: true
  });

  logger.info('Creating 15 Real SRK Faculty Members...');
  const realFacultyList = [
    { code: 'NB', name: 'Dr. Nirdesh Buch', email: 'nirdesh.buch@srk.edu', desig: 'Principal & Professor', deptId: bbaDept._id },
    { code: 'SA', name: 'Prof. Surbhi Ahir', email: 'surbhi.ahir@srk.edu', desig: 'Campus Head & Assistant Professor', deptId: mbaDept._id },
    { code: 'RS', name: 'Prof. Rishi Sonpar', email: 'rishi.sonpar@srk.edu', desig: 'Professor & HOD BBA', deptId: bbaDept._id },
    { code: 'RJ', name: 'Prof. Rishi Joshi', email: 'rishi.joshi@srk.edu', desig: 'Assistant Professor', deptId: bbaDept._id },
    { code: 'AA', name: 'Prof. Abhishek Abhani', email: 'abhishek.abhani@srk.edu', desig: 'Associate Professor', deptId: bbaDept._id },
    { code: 'CT', name: 'Prof. Chandni Thacker', email: 'chandni.thacker@srk.edu', desig: 'Professor', deptId: bbaDept._id },
    { code: 'JS', name: 'Prof. Jinal Sorathiya', email: 'jinal.sorathiya@srk.edu', desig: 'Associate Professor', deptId: bcaDept._id },
    { code: 'SS', name: 'Prof. Stephen Sober', email: 'stephen.sober@srk.edu', desig: 'Associate Professor', deptId: mbaDept._id },
    { code: 'MM', name: 'Prof. Mayur Meghani', email: 'mayur.meghani@srk.edu', desig: 'Associate Professor', deptId: bbaDept._id },
    { code: 'AG', name: 'Prof. Ankit Gandhi', email: 'ankit.gandhi@srk.edu', desig: 'Assistant Professor', deptId: mbaDept._id },
    { code: 'PL', name: 'Prof. Prakash Lambha', email: 'prakash.lambha@srk.edu', desig: 'Professor & HOD BCA', deptId: bcaDept._id },
    { code: 'PJ', name: 'Prof. Prayag Joshi', email: 'prayag.joshi@srk.edu', desig: 'Assistant Professor', deptId: bcaDept._id },
    { code: 'NT', name: 'Prof. Nirali Thakkar', email: 'nirali.thakkar@srk.edu', desig: 'Associate Professor', deptId: bcaDept._id },
    { code: 'AV', name: 'Prof. Arjunsinh Vaghela', email: 'arjunsinh.vaghela@srk.edu', desig: 'Professor', deptId: bcaDept._id },
    { code: 'KP', name: 'Prof. Krupa Patel', email: 'krupa.patel@srk.edu', desig: 'Professor & HOD MBA', deptId: mbaDept._id },
  ];

  const facultyMap: Record<string, any> = {};

  for (const fac of realFacultyList) {
    let user = await User.findOne({ email: fac.email });
    if (!user) {
      user = await User.create({
        name: `${fac.name} (${fac.code})`,
        email: fac.email,
        phone: '+9198765432' + (fac.code.charCodeAt(0) % 90),
        passwordHash: 'Faculty@123',
        role: UserRole.FACULTY,
        departmentId: fac.deptId,
        isActive: true
      });
    }

    const facultyDoc = await Faculty.create({
      userId: user._id,
      employeeId: `SRK_${fac.code}`,
      departmentId: fac.deptId,
      designation: fac.desig,
      subjects: [],
      currentStatus: FacultyStatus.AVAILABLE,
      currentLocation: {
        roomId: rooms.lh3._id,
        confidence: 90,
        lastVerified: new Date()
      }
    });

    facultyMap[fac.code] = facultyDoc;
  }

  // Initial Presence Radar States:
  await Faculty.findByIdAndUpdate(facultyMap['NT']._id, {
    currentStatus: FacultyStatus.IN_CLASS,
    currentLocation: { roomId: rooms.lh3._id, confidence: 96, lastVerified: new Date() }
  });
  await Faculty.findByIdAndUpdate(facultyMap['AV']._id, {
    currentStatus: FacultyStatus.IN_CLASS,
    currentLocation: { roomId: rooms.lh9._id, confidence: 95, lastVerified: new Date() }
  });
  await Faculty.findByIdAndUpdate(facultyMap['NB']._id, {
    currentStatus: FacultyStatus.IN_CLASS,
    currentLocation: { roomId: rooms.lh6._id, confidence: 98, lastVerified: new Date() }
  });
  await Faculty.findByIdAndUpdate(facultyMap['RS']._id, {
    currentStatus: FacultyStatus.WITH_PRINCIPAL,
    currentLocation: { roomId: rooms.principalCabin._id, confidence: 98, lastVerified: new Date() }
  });
  await Faculty.findByIdAndUpdate(facultyMap['JS']._id, {
    currentStatus: FacultyStatus.NOT_IN_CLASS_PENDING_SCAN,
    currentLocation: { roomId: rooms.lh3._id, confidence: 35, lastVerified: new Date(Date.now() - 15 * 60000) }
  });
  await Faculty.findByIdAndUpdate(facultyMap['PL']._id, {
    currentStatus: FacultyStatus.MOBILE_DATA_OFF_BLE_ONLY,
    currentLocation: { roomId: rooms.labPython._id, confidence: 85, lastVerified: new Date() }
  });

  logger.info('Creating 20+ Real SRK Students across BCA, BBA & MBA...');
  const studentSeedData = [
    // BCA Sem 3 (Lecture Hall 3)
    { name: 'Rahul Shah', enroll: 'SRK2026BCA001', email: 'rahul.shah@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Priya Sharma', enroll: 'SRK2026BCA002', email: 'priya.sharma@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Meet Vaghela', enroll: 'SRK2026BCA003', email: 'meet.vaghela@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Dev Patel', enroll: 'SRK2026BCA004', email: 'dev.patel@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Yash Joshi', enroll: 'SRK2026BCA005', email: 'yash.joshi@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Anjali Mehta', enroll: 'SRK2026BCA006', email: 'anjali.mehta@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Harsh Trivedi', enroll: 'SRK2026BCA007', email: 'harsh.trivedi@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Riya Solanki', enroll: 'SRK2026BCA008', email: 'riya.solanki@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Aman Khan', enroll: 'SRK2026BCA009', email: 'aman.khan@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },
    { name: 'Sneha Dave', enroll: 'SRK2026BCA010', email: 'sneha.dave@srk.edu', deptId: bcaDept._id, sem: 3, div: 'A' },

    // BCA Sem 1 (Lecture Hall 5)
    { name: 'Jay Soni', enroll: 'SRK2026BCA101', email: 'jay.soni@srk.edu', deptId: bcaDept._id, sem: 1, div: 'A' },
    { name: 'Diya Parekh', enroll: 'SRK2026BCA102', email: 'diya.parekh@srk.edu', deptId: bcaDept._id, sem: 1, div: 'A' },

    // BCA Sem 5 (Lecture Hall 9)
    { name: 'Parth Solanki', enroll: 'SRK2026BCA501', email: 'parth.solanki@srk.edu', deptId: bcaDept._id, sem: 5, div: 'A' },
    { name: 'Riya Rathod', enroll: 'SRK2026BCA502', email: 'riya.rathod@srk.edu', deptId: bcaDept._id, sem: 5, div: 'A' },

    // BBA Sem 1 Class I (Lecture Hall 6)
    { name: 'Rohan Merchant', enroll: 'SRK2026BBA101', email: 'rohan.merchant@srk.edu', deptId: bbaDept._id, sem: 1, div: 'Class I' },
    { name: 'Pooja Zala', enroll: 'SRK2026BBA102', email: 'pooja.zala@srk.edu', deptId: bbaDept._id, sem: 1, div: 'Class I' },

    // BBA Sem 1 Class II (Lecture Hall 7)
    { name: 'Mihir Bhatt', enroll: 'SRK2026BBA201', email: 'mihir.bhatt@srk.edu', deptId: bbaDept._id, sem: 1, div: 'Class II' },
    { name: 'Kruti Dave', enroll: 'SRK2026BBA202', email: 'kruti.dave@srk.edu', deptId: bbaDept._id, sem: 1, div: 'Class II' },

    // BBA Sem 3 (Lecture Hall 1)
    { name: 'Smit Sonpar', enroll: 'SRK2026BBA301', email: 'smit.sonpar@srk.edu', deptId: bbaDept._id, sem: 3, div: 'A' },
    { name: 'Tanvi Shukla', enroll: 'SRK2026BBA302', email: 'tanvi.shukla@srk.edu', deptId: bbaDept._id, sem: 3, div: 'A' },

    // BBA Sem 5 (Lecture Hall 2)
    { name: 'Karan Mehta', enroll: 'SRK2026BBA501', email: 'karan.mehta@srk.edu', deptId: bbaDept._id, sem: 5, div: 'A' },
    { name: 'Jhanvi Thakkar', enroll: 'SRK2026BBA502', email: 'jhanvi.thakkar@srk.edu', deptId: bbaDept._id, sem: 5, div: 'A' },

    // MBA Sem 3
    { name: 'Hardik Gandhi', enroll: 'SRK2026MBA301', email: 'hardik.gandhi@srk.edu', deptId: mbaDept._id, sem: 3, div: 'A' },
    { name: 'Saloni Ansari', enroll: 'SRK2026MBA302', email: 'saloni.ansari@srk.edu', deptId: mbaDept._id, sem: 3, div: 'A' },
  ];

  for (const s of studentSeedData) {
    let user = await User.findOne({ email: s.email });
    if (!user) {
      user = await User.create({
        name: s.name,
        email: s.email,
        passwordHash: 'Student@123',
        role: UserRole.STUDENT,
        departmentId: s.deptId,
        isActive: true
      });
    }

    let stu = await Student.findOne({ enrollmentNo: s.enroll });
    if (!stu) {
      await Student.create({
        userId: user._id,
        enrollmentNo: s.enroll,
        departmentId: s.deptId,
        semester: s.sem,
        division: s.div,
        academicYear: '2026-2027',
        status: 'ACTIVE'
      });
    }
  }

  logger.info('Seeding Timetable with Exact Lecture Halls (LH 1 to 10)...');
  const addSlot = async (day: number, start: string, end: string, deptId: any, sem: number, div: string, subName: string, subCode: string, facCode: string, roomId: any) => {
    let subject = await Subject.findOne({ code: subCode });
    if (!subject) {
      subject = await Subject.create({ name: subName, code: subCode, departmentId: deptId, semester: sem, credits: 4 });
    }
    const faculty = facultyMap[facCode] || facultyMap['AV'];
    await Timetable.create({
      departmentId: deptId,
      semester: sem,
      division: div,
      subjectId: subject._id,
      facultyId: faculty._id,
      roomId: roomId,
      dayOfWeek: day,
      startTime: start,
      endTime: end,
      academicYear: '2026-2027',
      isActive: true
    });
  };

  // Lecture Hall 3: BCA Sem 3
  await addSlot(1, '08:40', '09:40', bcaDept._id, 3, 'A', 'DBMS - I', 'BCA301', 'NT', rooms.lh3._id);
  await addSlot(1, '09:45', '10:40', bcaDept._id, 3, 'A', 'Lab: Data Structure using C', 'BCA302L', 'AV', rooms.labDbms._id);
  await addSlot(1, '11:30', '12:25', bcaDept._id, 3, 'A', 'Indian Thinkers', 'BCA303', 'RJ', rooms.lh3._id);
  await addSlot(1, '12:30', '13:25', bcaDept._id, 3, 'A', 'Understanding OOP with Python', 'BCA304', 'PL', rooms.lh3._id);

  // Lecture Hall 5: BCA Sem 1
  await addSlot(1, '08:40', '09:40', bcaDept._id, 1, 'A', 'Statistics', 'BCA101', 'JS', rooms.lh5._id);
  await addSlot(1, '09:45', '10:40', bcaDept._id, 1, 'A', 'Web Designing using HTML/CSS/JS', 'BCA102', 'NT', rooms.lh5._id);
  await addSlot(1, '11:30', '12:25', bcaDept._id, 1, 'A', 'Digital Electronics', 'BCA103', 'PL', rooms.lh5._id);
  await addSlot(1, '12:30', '13:25', bcaDept._id, 1, 'A', 'Bhagavad Gita & Life Management', 'BCA104', 'NB', rooms.lh5._id);

  // Lecture Hall 9: BCA Sem 5
  await addSlot(1, '08:40', '09:40', bcaDept._id, 5, 'A', 'Advanced DBMS', 'BCA501', 'AV', rooms.lh9._id);
  await addSlot(1, '09:45', '10:40', bcaDept._id, 5, 'A', 'Operational Research', 'BCA502', 'JS', rooms.lh9._id);
  await addSlot(1, '11:30', '12:25', bcaDept._id, 5, 'A', 'Software Engineering', 'BCA503', 'NT', rooms.lh9._id);
  await addSlot(1, '12:30', '13:25', bcaDept._id, 5, 'A', 'Understanding Operating Systems', 'BCA504', 'AV', rooms.lh9._id);

  // Lecture Hall 6: BBA Sem 1 - Class I (A)
  await addSlot(1, '08:40', '09:40', bbaDept._id, 1, 'Class I', 'Introduction to Bhagwad Gita', 'BBA101', 'NB', rooms.lh6._id);
  await addSlot(1, '09:45', '10:40', bbaDept._id, 1, 'Class I', 'Fundamentals of Management', 'BBA102', 'RS', rooms.lh6._id);
  await addSlot(1, '11:30', '12:25', bbaDept._id, 1, 'Class I', 'E-Commerce & Digital Solutions', 'BBA103', 'MM', rooms.lh6._id);
  await addSlot(1, '12:30', '13:25', bbaDept._id, 1, 'Class I', 'Economics-1', 'BBA104', 'CT', rooms.lh6._id);

  // Lecture Hall 7: BBA Sem 1 - Class II (B)
  await addSlot(1, '08:40', '09:40', bbaDept._id, 1, 'Class II', 'Business Organization & Structure', 'BBA105', 'AA', rooms.lh7._id);
  await addSlot(1, '09:45', '10:40', bbaDept._id, 1, 'Class II', 'E-Commerce & Digital Solutions', 'BBA103', 'MM', rooms.lh7._id);
  await addSlot(1, '11:30', '12:25', bbaDept._id, 1, 'Class II', 'Business Statistics/Ecology', 'BBA106', 'JS', rooms.lh7._id);
  await addSlot(1, '12:30', '13:25', bbaDept._id, 1, 'Class II', 'Fundamentals of Management', 'BBA102', 'RS', rooms.lh7._id);

  // Lecture Hall 1: BBA Sem 3
  await addSlot(1, '08:40', '09:40', bbaDept._id, 3, 'A', 'Consumer Behaviour', 'BBA301', 'SS', rooms.lh1._id);
  await addSlot(1, '09:45', '10:40', bbaDept._id, 3, 'A', 'Humanities', 'BBA302', 'AA', rooms.lh1._id);
  await addSlot(1, '11:30', '12:25', bbaDept._id, 3, 'A', 'HRM-1', 'BBA303', 'RS', rooms.lh1._id);
  await addSlot(1, '12:30', '13:25', bbaDept._id, 3, 'A', 'Practical English - III', 'BBA304', 'RJ', rooms.lh1._id);

  // Lecture Hall 2: BBA Sem 5
  await addSlot(1, '08:40', '09:40', bbaDept._id, 5, 'A', 'Mercantile Law', 'BBA501', 'RS', rooms.lh2._id);
  await addSlot(1, '09:45', '10:40', bbaDept._id, 5, 'A', 'Direct Tax', 'BBA502', 'CT', rooms.lh2._id);
  await addSlot(1, '11:30', '12:25', bbaDept._id, 5, 'A', 'Business Environment - 2', 'BBA503', 'NB', rooms.lh2._id);
  await addSlot(1, '12:30', '13:25', bbaDept._id, 5, 'A', 'CM & OD', 'BBA504', 'SS', rooms.lh2._id);

  logger.info('SRK Institute database completely populated with real students and timetable!');
};

if (require.main === module) {
  (async () => {
    try {
      await connectDatabase();
      await seedDatabase();
      await disconnectDatabase();
      process.exit(0);
    } catch (err) {
      logger.error('Database seeding failed', { err });
      process.exit(1);
    }
  })();
}
