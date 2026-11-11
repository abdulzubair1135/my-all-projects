class AppConstants {
  static const String appName = "SRK Campus";
  static const String institutionName = "SRK Institute of Management & Computer Education";
  
  // Public Live Cloudflare Tunnel URL (Global HTTPS & WSS for Port 5001)
  static const String cloudflareTunnelUrl = 'https://counting-criterion-identifies-implied.trycloudflare.com';

  static String get baseUrl {
    return '$cloudflareTunnelUrl/api/v1';
  }

  static String get socketUrl {
    return cloudflareTunnelUrl;
  }

  // Pre-configured Quick Login Accounts (Real SRK MongoDB Seeded Data)
  static const Map<String, Map<String, String>> quickAccounts = {
    'principal': {
      'role': 'PRINCIPAL',
      'name': 'Dr. Nirdesh Buch',
      'title': 'Campus Principal',
      'email': 'nirdesh.buch@srk.edu',
      'password': 'Principal@123',
      'dept': 'Institutional Administration',
      'uid': 'SRK-ADM-001',
    },
    'campus_head': {
      'role': 'CAMPUS_HEAD',
      'name': 'Prof. Surbhi Ahir',
      'title': 'Campus Head',
      'email': 'surbhi.ahir@srk.edu',
      'password': 'CampusHead@123',
      'dept': 'Academic Affairs',
      'uid': 'SRK-ADM-002',
    },
    'teacher_nirali': {
      'role': 'FACULTY',
      'name': 'Prof. Nirali Thakkar',
      'title': 'Assistant Professor',
      'email': 'nirali.thakkar@srk.edu',
      'password': 'Faculty@123',
      'dept': 'Computer Applications (BCA)',
      'cabin': 'Faculty Cabin F-04',
      'uid': 'SRK-FAC-101',
    },
    'teacher_arjun': {
      'role': 'FACULTY',
      'name': 'Prof. Arjunsinh Vaghela',
      'title': 'Associate Professor',
      'email': 'arjunsinh.vaghela@srk.edu',
      'password': 'Faculty@123',
      'dept': 'Computer Applications (BCA)',
      'cabin': 'Faculty Cabin F-08',
      'uid': 'SRK-FAC-102',
    },
    'student_rahul': {
      'role': 'STUDENT',
      'name': 'Rahul Shah',
      'title': 'Student',
      'email': 'rahul.shah@srk.edu',
      'password': 'Student@123',
      'dept': 'Computer Applications (BCA)',
      'rollNo': '24BCA001',
      'uid': 'SRK-STU-201',
    },
  };

  // 30 Pre-Authorized Institutional UIDs Roster
  static const List<Map<String, String>> seedCampusUids = [
    {'uid': 'SRK-ADM-001', 'name': 'Dr. Nirdesh Buch', 'role': 'PRINCIPAL', 'title': 'Campus Principal', 'email': 'nirdesh.buch@srk.edu'},
    {'uid': 'SRK-ADM-002', 'name': 'Prof. Surbhi Ahir', 'role': 'CAMPUS_HEAD', 'title': 'Campus Head', 'email': 'surbhi.ahir@srk.edu'},
    {'uid': 'SRK-ADM-003', 'name': 'Dr. Alok Verma', 'role': 'ADMIN', 'title': 'Dean of Academics', 'email': 'alok.verma@srk.edu'},
    {'uid': 'SRK-ADM-004', 'name': 'Prof. Sunita Rao', 'role': 'ADMIN', 'title': 'Chief Registrar', 'email': 'sunita.rao@srk.edu'},
    {'uid': 'SRK-ADM-005', 'name': 'Mr. Rajesh Joshi', 'role': 'ADMIN', 'title': 'Admin Officer', 'email': 'rajesh.joshi@srk.edu'},

    {'uid': 'SRK-FAC-101', 'name': 'Prof. Nirali Thakkar', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'nirali.thakkar@srk.edu'},
    {'uid': 'SRK-FAC-102', 'name': 'Prof. Arjunsinh Vaghela', 'role': 'FACULTY', 'title': 'Associate Professor', 'email': 'arjunsinh.vaghela@srk.edu'},
    {'uid': 'SRK-FAC-103', 'name': 'Dr. Hardik Patel', 'role': 'FACULTY', 'title': 'HOD Computer Science', 'email': 'hardik.patel@srk.edu'},
    {'uid': 'SRK-FAC-104', 'name': 'Prof. Meera Desai', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'meera.desai@srk.edu'},
    {'uid': 'SRK-FAC-105', 'name': 'Prof. Rohan Shah', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'rohan.shah@srk.edu'},
    {'uid': 'SRK-FAC-106', 'name': 'Dr. Bhavna Trivedi', 'role': 'FACULTY', 'title': 'Associate Professor', 'email': 'bhavna.trivedi@srk.edu'},
    {'uid': 'SRK-FAC-107', 'name': 'Prof. Kunal Mehta', 'role': 'FACULTY', 'title': 'Lecturer', 'email': 'kunal.mehta@srk.edu'},
    {'uid': 'SRK-FAC-108', 'name': 'Prof. Pooja Dave', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'pooja.dave@srk.edu'},
    {'uid': 'SRK-FAC-109', 'name': 'Prof. Vikram Chauhan', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'vikram.chauhan@srk.edu'},
    {'uid': 'SRK-FAC-110', 'name': 'Dr. Sneha Kapadia', 'role': 'FACULTY', 'title': 'Associate Professor', 'email': 'sneha.kapadia@srk.edu'},
    {'uid': 'SRK-FAC-111', 'name': 'Prof. Jaydeep Solanki', 'role': 'FACULTY', 'title': 'Lecturer', 'email': 'jaydeep.solanki@srk.edu'},
    {'uid': 'SRK-FAC-112', 'name': 'Prof. Anjali Parekh', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'anjali.parekh@srk.edu'},
    {'uid': 'SRK-FAC-113', 'name': 'Prof. Tarun Bhatt', 'role': 'FACULTY', 'title': 'Lecturer', 'email': 'tarun.bhatt@srk.edu'},
    {'uid': 'SRK-FAC-114', 'name': 'Dr. Chetna Vyas', 'role': 'FACULTY', 'title': 'Professor', 'email': 'chetna.vyas@srk.edu'},
    {'uid': 'SRK-FAC-115', 'name': 'Prof. Divyesh Parmar', 'role': 'FACULTY', 'title': 'Assistant Professor', 'email': 'divyesh.parmar@srk.edu'},

    {'uid': 'SRK-STU-201', 'name': 'Rahul Shah', 'role': 'STUDENT', 'title': 'BCA Sem 3', 'email': 'rahul.shah@srk.edu'},
    {'uid': 'SRK-STU-202', 'name': 'Priya Patel', 'role': 'STUDENT', 'title': 'BCA Sem 3', 'email': 'priya.patel@srk.edu'},
    {'uid': 'SRK-STU-203', 'name': 'Aman Shaikh', 'role': 'STUDENT', 'title': 'BCA Sem 5', 'email': 'aman.shaikh@srk.edu'},
    {'uid': 'SRK-STU-204', 'name': 'Kavita Joshi', 'role': 'STUDENT', 'title': 'BBA Sem 3', 'email': 'kavita.joshi@srk.edu'},
    {'uid': 'SRK-STU-205', 'name': 'Harsh Vora', 'role': 'STUDENT', 'title': 'BCA Sem 1', 'email': 'harsh.vora@srk.edu'},
    {'uid': 'SRK-STU-206', 'name': 'Riya Soni', 'role': 'STUDENT', 'title': 'BCA Sem 3', 'email': 'riya.soni@srk.edu'},
    {'uid': 'SRK-STU-207', 'name': 'Devang Mehta', 'role': 'STUDENT', 'title': 'BBA Sem 5', 'email': 'devang.mehta@srk.edu'},
    {'uid': 'SRK-STU-208', 'name': 'Neha Trivedi', 'role': 'STUDENT', 'title': 'BCA Sem 5', 'email': 'neha.trivedi@srk.edu'},
    {'uid': 'SRK-STU-209', 'name': 'Sanjay Rathod', 'role': 'STUDENT', 'title': 'BCA Sem 3', 'email': 'sanjay.rathod@srk.edu'},
    {'uid': 'SRK-STU-210', 'name': 'Tanvi Dave', 'role': 'STUDENT', 'title': 'BBA Sem 1', 'email': 'tanvi.dave@srk.edu'},
  ];
}
