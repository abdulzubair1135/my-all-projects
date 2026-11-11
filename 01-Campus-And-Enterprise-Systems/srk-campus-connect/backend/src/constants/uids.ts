export interface CampusUIDRecord {
  uid: string;
  name: string;
  role: 'PRINCIPAL' | 'CAMPUS_HEAD' | 'ADMIN' | 'FACULTY' | 'STUDENT';
  department: string;
  designation?: string;
  cabinNumber?: string;
  rollNumber?: string;
  defaultEmail: string;
}

export const CAMPUS_AUTHORIZED_UIDS: CampusUIDRecord[] = [
  // 1-5: Administration & Principal
  {
    uid: 'SRK-ADM-001',
    name: 'Dr. Nirdesh Buch',
    role: 'PRINCIPAL',
    department: 'Institutional Administration',
    designation: 'Campus Principal',
    cabinNumber: 'Principal Cabin P-01',
    defaultEmail: 'nirdesh.buch@srk.edu'
  },
  {
    uid: 'SRK-ADM-002',
    name: 'Prof. Surbhi Ahir',
    role: 'CAMPUS_HEAD',
    department: 'Academic Affairs',
    designation: 'Campus Head',
    cabinNumber: 'Cabin A-01',
    defaultEmail: 'surbhi.ahir@srk.edu'
  },
  {
    uid: 'SRK-ADM-003',
    name: 'Dr. Rajesh Sharma',
    role: 'ADMIN',
    department: 'Academic Dean Office',
    designation: 'Dean of Academics',
    cabinNumber: 'Cabin A-02',
    defaultEmail: 'rajesh.sharma@srk.edu'
  },
  {
    uid: 'SRK-ADM-004',
    name: 'Prof. Meena Vyas',
    role: 'ADMIN',
    department: 'Registrar Office',
    designation: 'Registrar',
    cabinNumber: 'Cabin A-03',
    defaultEmail: 'meena.vyas@srk.edu'
  },
  {
    uid: 'SRK-ADM-005',
    name: 'Mr. Sanjay Patel',
    role: 'ADMIN',
    department: 'Examination Cell',
    designation: 'Controller of Examinations',
    cabinNumber: 'Cabin A-04',
    defaultEmail: 'sanjay.patel@srk.edu'
  },

  // 6-20: Faculty (15 Professors)
  {
    uid: 'SRK-FAC-101',
    name: 'Prof. Nirali Thakkar',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-04',
    defaultEmail: 'nirali.thakkar@srk.edu'
  },
  {
    uid: 'SRK-FAC-102',
    name: 'Prof. Arjunsinh Vaghela',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Associate Professor',
    cabinNumber: 'Faculty Cabin F-08',
    defaultEmail: 'arjunsinh.vaghela@srk.edu'
  },
  {
    uid: 'SRK-FAC-103',
    name: 'Prof. Kinjal Patel',
    role: 'FACULTY',
    department: 'Management Studies (BBA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-02',
    defaultEmail: 'kinjal.patel@srk.edu'
  },
  {
    uid: 'SRK-FAC-104',
    name: 'Prof. Hardik Joshi',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-05',
    defaultEmail: 'hardik.joshi@srk.edu'
  },
  {
    uid: 'SRK-FAC-105',
    name: 'Prof. Priya Trivedi',
    role: 'FACULTY',
    department: 'Computer Applications (MCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-06',
    defaultEmail: 'priya.trivedi@srk.edu'
  },
  {
    uid: 'SRK-FAC-106',
    name: 'Prof. Dharmendra Shah',
    role: 'FACULTY',
    department: 'Management Studies (MBA)',
    designation: 'Associate Professor',
    cabinNumber: 'Faculty Cabin F-01',
    defaultEmail: 'dharmendra.shah@srk.edu'
  },
  {
    uid: 'SRK-FAC-107',
    name: 'Prof. Sneha Mehta',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-07',
    defaultEmail: 'sneha.mehta@srk.edu'
  },
  {
    uid: 'SRK-FAC-108',
    name: 'Prof. Chetan Dave',
    role: 'FACULTY',
    department: 'Computer Applications (MCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-09',
    defaultEmail: 'chetan.dave@srk.edu'
  },
  {
    uid: 'SRK-FAC-109',
    name: 'Prof. Bhavna Raval',
    role: 'FACULTY',
    department: 'Management Studies (BBA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-03',
    defaultEmail: 'bhavna.raval@srk.edu'
  },
  {
    uid: 'SRK-FAC-110',
    name: 'Prof. Ankit Patel',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-10',
    defaultEmail: 'ankit.patel@srk.edu'
  },
  {
    uid: 'SRK-FAC-111',
    name: 'Prof. Riddhi Solanki',
    role: 'FACULTY',
    department: 'Management Studies (MBA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-11',
    defaultEmail: 'riddhi.solanki@srk.edu'
  },
  {
    uid: 'SRK-FAC-112',
    name: 'Prof. Manish Varma',
    role: 'FACULTY',
    department: 'Computer Applications (MCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-12',
    defaultEmail: 'manish.varma@srk.edu'
  },
  {
    uid: 'SRK-FAC-113',
    name: 'Prof. Pooja Shukla',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-14',
    defaultEmail: 'pooja.shukla@srk.edu'
  },
  {
    uid: 'SRK-FAC-114',
    name: 'Prof. Vishal Pandya',
    role: 'FACULTY',
    department: 'Computer Applications (BCA)',
    designation: 'Associate Professor',
    cabinNumber: 'Faculty Cabin F-15',
    defaultEmail: 'vishal.pandya@srk.edu'
  },
  {
    uid: 'SRK-FAC-115',
    name: 'Prof. Jagruti Parmar',
    role: 'FACULTY',
    department: 'Management Studies (BBA)',
    designation: 'Assistant Professor',
    cabinNumber: 'Faculty Cabin F-16',
    defaultEmail: 'jagruti.parmar@srk.edu'
  },

  // 21-30: Students (10 Students)
  {
    uid: 'SRK-STU-201',
    name: 'Rahul Shah',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '24BCA001',
    defaultEmail: 'rahul.shah@srk.edu'
  },
  {
    uid: 'SRK-STU-202',
    name: 'Priya Mehta',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '24BCA002',
    defaultEmail: 'priya.mehta@srk.edu'
  },
  {
    uid: 'SRK-STU-203',
    name: 'Ananya Joshi',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '24BCA003',
    defaultEmail: 'ananya.joshi@srk.edu'
  },
  {
    uid: 'SRK-STU-204',
    name: 'Dev Patel',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '24BCA004',
    defaultEmail: 'dev.patel@srk.edu'
  },
  {
    uid: 'SRK-STU-205',
    name: 'Karan Sharma',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '23BCA015',
    defaultEmail: 'karan.sharma@srk.edu'
  },
  {
    uid: 'SRK-STU-206',
    name: 'Neha Trivedi',
    role: 'STUDENT',
    department: 'Management Studies (BBA)',
    rollNumber: '24BBA008',
    defaultEmail: 'neha.trivedi@srk.edu'
  },
  {
    uid: 'SRK-STU-207',
    name: 'Parth Vaghela',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '25BCA042',
    defaultEmail: 'parth.vaghela@srk.edu'
  },
  {
    uid: 'SRK-STU-208',
    name: 'Riya Shah',
    role: 'STUDENT',
    department: 'Computer Applications (MCA)',
    rollNumber: '25MCA012',
    defaultEmail: 'riya.shah@srk.edu'
  },
  {
    uid: 'SRK-STU-209',
    name: 'Aman Sheikh',
    role: 'STUDENT',
    department: 'Management Studies (MBA)',
    rollNumber: '24MBA020',
    defaultEmail: 'aman.sheikh@srk.edu'
  },
  {
    uid: 'SRK-STU-210',
    name: 'Sneha Rathod',
    role: 'STUDENT',
    department: 'Computer Applications (BCA)',
    rollNumber: '24BCA025',
    defaultEmail: 'sneha.rathod@srk.edu'
  }
];
