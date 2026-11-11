from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="College Website", version="1.0.0")

# ==================== DATA MODELS ====================
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    course: str
    year: int
    enrollment_date: str

class Faculty(BaseModel):
    id: Optional[int] = None
    name: str
    department: str
    email: str
    designation: str

class Course(BaseModel):
    id: Optional[int] = None
    code: str
    name: str
    credits: int
    department: str

# ==================== IN-MEMORY DATABASE ====================
students_db = []
faculty_db = []
courses_db = []

student_counter = 1
faculty_counter = 1
course_counter = 1

# Seed some initial data
def seed_data():
    global student_counter, faculty_counter, course_counter
    
    students_db.append(Student(id=1, name="Aarav Sharma", email="aarav@college.edu", course="Computer Science", year=3, enrollment_date="2023-08-15"))
    students_db.append(Student(id=2, name="Priya Patel", email="priya@college.edu", course="Mathematics", year=2, enrollment_date="2024-01-10"))
    students_db.append(Student(id=3, name="Rahul Singh", email="rahul@college.edu", course="Physics", year=1, enrollment_date="2024-08-20"))
    students_db.append(Student(id=4, name="Sneha Reddy", email="sneha@college.edu", course="Computer Science", year=4, enrollment_date="2022-08-15"))
    students_db.append(Student(id=5, name="Vikram Kumar", email="vikram@college.edu", course="Electronics", year=2, enrollment_date="2023-08-15"))
    student_counter = 6
    
    faculty_db.append(Faculty(id=1, name="Dr. Ananya Rao", department="Computer Science", email="ananya.rao@college.edu", designation="Professor"))
    faculty_db.append(Faculty(id=2, name="Dr. Suresh Menon", department="Mathematics", email="suresh.menon@college.edu", designation="Associate Professor"))
    faculty_db.append(Faculty(id=3, name="Prof. Meera Nair", department="Physics", email="meera.nair@college.edu", designation="Assistant Professor"))
    faculty_counter = 4
    
    courses_db.append(Course(id=1, code="CS101", name="Introduction to Programming", credits=4, department="Computer Science"))
    courses_db.append(Course(id=2, code="CS201", name="Data Structures", credits=4, department="Computer Science"))
    courses_db.append(Course(id=3, code="MA101", name="Calculus I", credits=3, department="Mathematics"))
    courses_db.append(Course(id=4, code="PH101", name="Mechanics", credits=3, department="Physics"))
    courses_db.append(Course(id=5, code="EL101", name="Basic Electronics", credits=3, department="Electronics"))
    course_counter = 6

seed_data()

# ==================== API ENDPOINTS ====================
# Students
@app.get("/api/students", response_model=List[Student])
async def get_students():
    return students_db

@app.post("/api/students", response_model=Student)
async def create_student(student: Student):
    global student_counter
    student.id = student_counter
    student_counter += 1
    students_db.append(student)
    return student

@app.put("/api/students/{student_id}", response_model=Student)
async def update_student(student_id: int, student: Student):
    for i, s in enumerate(students_db):
        if s.id == student_id:
            student.id = student_id
            students_db[i] = student
            return student
    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    for i, s in enumerate(students_db):
        if s.id == student_id:
            del students_db[i]
            return {"message": "Student deleted successfully"}
    raise HTTPException(status_code=404, detail="Student not found")

# Faculty
@app.get("/api/faculty", response_model=List[Faculty])
async def get_faculty():
    return faculty_db

@app.post("/api/faculty", response_model=Faculty)
async def create_faculty(faculty: Faculty):
    global faculty_counter
    faculty.id = faculty_counter
    faculty_counter += 1
    faculty_db.append(faculty)
    return faculty

@app.put("/api/faculty/{faculty_id}", response_model=Faculty)
async def update_faculty(faculty_id: int, faculty: Faculty):
    for i, f in enumerate(faculty_db):
        if f.id == faculty_id:
            faculty.id = faculty_id
            faculty_db[i] = faculty
            return faculty
    raise HTTPException(status_code=404, detail="Faculty not found")

@app.delete("/api/faculty/{faculty_id}")
async def delete_faculty(faculty_id: int):
    for i, f in enumerate(faculty_db):
        if f.id == faculty_id:
            del faculty_db[i]
            return {"message": "Faculty deleted successfully"}
    raise HTTPException(status_code=404, detail="Faculty not found")

# Courses
@app.get("/api/courses", response_model=List[Course])
async def get_courses():
    return courses_db

@app.post("/api/courses", response_model=Course)
async def create_course(course: Course):
    global course_counter
    course.id = course_counter
    course_counter += 1
    courses_db.append(course)
    return course

@app.put("/api/courses/{course_id}", response_model=Course)
async def update_course(course_id: int, course: Course):
    for i, c in enumerate(courses_db):
        if c.id == course_id:
            course.id = course_id
            courses_db[i] = course
            return course
    raise HTTPException(status_code=404, detail="Course not found")

@app.delete("/api/courses/{course_id}")
async def delete_course(course_id: int):
    for i, c in enumerate(courses_db):
        if c.id == course_id:
            del courses_db[i]
            return {"message": "Course deleted successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

# Dashboard Stats
@app.get("/api/stats")
async def get_stats():
    return {
        "students": len(students_db),
        "faculty": len(faculty_db),
        "courses": len(courses_db),
        "departments": len(set(c.department for c in courses_db))
    }

# ==================== FRONTEND ====================
@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Management System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { transition: all 0.2s ease; }
        .tab-active { border-bottom: 3px solid #3b82f6; color: #1e40af; font-weight: 600; }
        .modal-overlay { background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 12px 24px -8px rgba(0,0,0,0.15); }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .stat-card:nth-child(2) { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .stat-card:nth-child(3) { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .stat-card:nth-child(4) { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .fade-in { animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .table-row:hover { background-color: #f8fafc; }
        .badge { padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
        .badge-cs { background: #dbeafe; color: #1e40af; }
        .badge-math { background: #d1fae5; color: #065f46; }
        .badge-phy { background: #fef3c7; color: #92400e; }
        .badge-el { background: #fce4ec; color: #b71c1c; }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">

    <div class="container mx-auto px-4 py-8 max-w-7xl">
        <!-- Header -->
        <header class="bg-white rounded-2xl shadow-xl p-6 mb-8 flex flex-col md:flex-row justify-between items-center">
            <div class="flex items-center gap-4 mb-4 md:mb-0">
                <div class="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <div>
                    <h1 class="text-2xl font-bold text-gray-800">College Management</h1>
                    <p class="text-sm text-gray-500">St. Xavier's Institute of Technology</p>
                </div>
            </div>
            <div class="flex gap-3">
                <span class="text-sm text-gray-600"><i class="far fa-calendar-alt mr-1"></i> Fall 2026</span>
                <span class="text-sm text-gray-600"><i class="far fa-clock mr-1"></i> <span id="liveTime">--:--:--</span></span>
            </div>
        </header>

        <!-- Stats Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div class="stat-card rounded-xl p-6 text-white shadow-lg card-hover">
                <div class="flex items-center justify-between">
                    <div><p class="text-sm opacity-90">Total Students</p><p class="text-3xl font-bold" id="totalStudents">0</p></div>
                    <i class="fas fa-user-graduate text-4xl opacity-30"></i>
                </div>
            </div>
            <div class="stat-card rounded-xl p-6 text-white shadow-lg card-hover">
                <div class="flex items-center justify-between">
                    <div><p class="text-sm opacity-90">Faculty Members</p><p class="text-3xl font-bold" id="totalFaculty">0</p></div>
                    <i class="fas fa-chalkboard-teacher text-4xl opacity-30"></i>
                </div>
            </div>
            <div class="stat-card rounded-xl p-6 text-white shadow-lg card-hover">
                <div class="flex items-center justify-between">
                    <div><p class="text-sm opacity-90">Courses</p><p class="text-3xl font-bold" id="totalCourses">0</p></div>
                    <i class="fas fa-book-open text-4xl opacity-30"></i>
                </div>
            </div>
            <div class="stat-card rounded-xl p-6 text-white shadow-lg card-hover">
                <div class="flex items-center justify-between">
                    <div><p class="text-sm opacity-90">Departments</p><p class="text-3xl font-bold" id="totalDepartments">0</p></div>
                    <i class="fas fa-building text-4xl opacity-30"></i>
                </div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
            <div class="border-b border-gray-200 px-6">
                <nav class="flex gap-8 -mb-px">
                    <button class="tab-btn py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent tab-active" data-tab="students">
                        <i class="fas fa-users mr-2"></i>Students
                    </button>
                    <button class="tab-btn py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent" data-tab="faculty">
                        <i class="fas fa-user-tie mr-2"></i>Faculty
                    </button>
                    <button class="tab-btn py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent" data-tab="courses">
                        <i class="fas fa-book mr-2"></i>Courses
                    </button>
                </nav>
            </div>

            <div class="p-6">
                <!-- Students Tab -->
                <div id="tab-students" class="tab-content fade-in">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                        <div class="relative flex-1 max-w-sm">
                            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
                            <input type="text" id="studentSearch" placeholder="Search students by name or course..." 
                                   class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                        <button onclick="openModal('student')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-md hover:shadow-lg">
                            <i class="fas fa-plus"></i> Add Student
                        </button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="bg-gray-50 text-left text-sm text-gray-600">
                                    <th class="px-4 py-3 font-semibold">ID</th>
                                    <th class="px-4 py-3 font-semibold">Name</th>
                                    <th class="px-4 py-3 font-semibold">Email</th>
                                    <th class="px-4 py-3 font-semibold">Course</th>
                                    <th class="px-4 py-3 font-semibold">Year</th>
                                    <th class="px-4 py-3 font-semibold">Enrolled</th>
                                    <th class="px-4 py-3 font-semibold text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="studentsTableBody" class="divide-y divide-gray-100"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Faculty Tab -->
                <div id="tab-faculty" class="tab-content fade-in hidden">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                        <div class="relative flex-1 max-w-sm">
                            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
                            <input type="text" id="facultySearch" placeholder="Search faculty by name or department..." 
                                   class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                        <button onclick="openModal('faculty')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-md hover:shadow-lg">
                            <i class="fas fa-plus"></i> Add Faculty
                        </button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="bg-gray-50 text-left text-sm text-gray-600">
                                    <th class="px-4 py-3 font-semibold">ID</th>
                                    <th class="px-4 py-3 font-semibold">Name</th>
                                    <th class="px-4 py-3 font-semibold">Email</th>
                                    <th class="px-4 py-3 font-semibold">Department</th>
                                    <th class="px-4 py-3 font-semibold">Designation</th>
                                    <th class="px-4 py-3 font-semibold text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="facultyTableBody" class="divide-y divide-gray-100"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Courses Tab -->
                <div id="tab-courses" class="tab-content fade-in hidden">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                        <div class="relative flex-1 max-w-sm">
                            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
                            <input type="text" id="courseSearch" placeholder="Search courses by code or name..." 
                                   class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
                        </div>
                        <button onclick="openModal('course')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-md hover:shadow-lg">
                            <i class="fas fa-plus"></i> Add Course
                        </button>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="bg-gray-50 text-left text-sm text-gray-600">
                                    <th class="px-4 py-3 font-semibold">ID</th>
                                    <th class="px-4 py-3 font-semibold">Code</th>
                                    <th class="px-4 py-3 font-semibold">Name</th>
                                    <th class="px-4 py-3 font-semibold">Credits</th>
                                    <th class="px-4 py-3 font-semibold">Department</th>
                                    <th class="px-4 py-3 font-semibold text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="coursesTableBody" class="divide-y divide-gray-100"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="mt-8 text-center text-sm text-gray-500">
            <p>&copy; 2026 St. Xavier's Institute of Technology. All rights reserved.</p>
        </footer>
    </div>

    <!-- Modal -->
    <div id="modal" class="fixed inset-0 modal-overlay hidden items-center justify-center z-50">
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 fade-in">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-gray-800" id="modalTitle">Add New</h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <form id="modalForm" class="space-y-4">
                <div id="modalFields"></div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg shadow-md hover:shadow-lg transition">
                    <i class="fas fa-save mr-2"></i> Save
                </button>
            </form>
        </div>
    </div>

    <script>
        // ==================== STATE ====================
        let currentTab = 'students';
        let editId = null;
        let editType = null;

        // ==================== UTILITY ====================
        function getDeptBadge(dept) {
            const map = {
                'Computer Science': 'badge-cs',
                'Mathematics': 'badge-math',
                'Physics': 'badge-phy',
                'Electronics': 'badge-el'
            };
            return map[dept] || 'badge-cs';
        }

        // ==================== API CALLS ====================
        async function api(method, url, data = null) {
            const opts = { method, headers: { 'Content-Type': 'application/json' } };
            if (data) opts.body = JSON.stringify(data);
            const res = await fetch(url, opts);
            if (!res.ok) throw new Error(await res.text());
            return res.json();
        }

        // ==================== LOAD DATA ====================
        async function loadStats() {
            try {
                const stats = await api('GET', '/api/stats');
                document.getElementById('totalStudents').textContent = stats.students;
                document.getElementById('totalFaculty').textContent = stats.faculty;
                document.getElementById('totalCourses').textContent = stats.courses;
                document.getElementById('totalDepartments').textContent = stats.departments;
            } catch (e) { console.error(e); }
        }

        async function loadStudents(filter = '') {
            try {
                const data = await api('GET', '/api/students');
                const filtered = data.filter(s => 
                    s.name.toLowerCase().includes(filter) || 
                    s.course.toLowerCase().includes(filter)
                );
                const tbody = document.getElementById('studentsTableBody');
                tbody.innerHTML = filtered.map(s => `
                    <tr class="table-row">
                        <td class="px-4 py-3 text-sm">${s.id}</td>
                        <td class="px-4 py-3 font-medium text-gray-800">${s.name}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">${s.email}</td>
                        <td class="px-4 py-3"><span class="badge ${getDeptBadge(s.course)}">${s.course}</span></td>
                        <td class="px-4 py-3 text-sm">Year ${s.year}</td>
                        <td class="px-4 py-3 text-sm text-gray-500">${s.enrollment_date}</td>
                        <td class="px-4 py-3 text-center">
                            <button onclick="editItem('student', ${s.id})" class="text-blue-600 hover:text-blue-800 mx-1"><i class="fas fa-edit"></i></button>
                            <button onclick="deleteItem('students', ${s.id})" class="text-red-600 hover:text-red-800 mx-1"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `).join('');
            } catch (e) { console.error(e); }
        }

        async function loadFaculty(filter = '') {
            try {
                const data = await api('GET', '/api/faculty');
                const filtered = data.filter(f => 
                    f.name.toLowerCase().includes(filter) || 
                    f.department.toLowerCase().includes(filter)
                );
                const tbody = document.getElementById('facultyTableBody');
                tbody.innerHTML = filtered.map(f => `
                    <tr class="table-row">
                        <td class="px-4 py-3 text-sm">${f.id}</td>
                        <td class="px-4 py-3 font-medium text-gray-800">${f.name}</td>
                        <td class="px-4 py-3 text-sm text-gray-600">${f.email}</td>
                        <td class="px-4 py-3"><span class="badge ${getDeptBadge(f.department)}">${f.department}</span></td>
                        <td class="px-4 py-3 text-sm">${f.designation}</td>
                        <td class="px-4 py-3 text-center">
                            <button onclick="editItem('faculty', ${f.id})" class="text-blue-600 hover:text-blue-800 mx-1"><i class="fas fa-edit"></i></button>
                            <button onclick="deleteItem('faculty', ${f.id})" class="text-red-600 hover:text-red-800 mx-1"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `).join('');
            } catch (e) { console.error(e); }
        }

        async function loadCourses(filter = '') {
            try {
                const data = await api('GET', '/api/courses');
                const filtered = data.filter(c => 
                    c.code.toLowerCase().includes(filter) || 
                    c.name.toLowerCase().includes(filter)
                );
                const tbody = document.getElementById('coursesTableBody');
                tbody.innerHTML = filtered.map(c => `
                    <tr class="table-row">
                        <td class="px-4 py-3 text-sm">${c.id}</td>
                        <td class="px-4 py-3 font-mono text-sm font-semibold text-blue-700">${c.code}</td>
                        <td class="px-4 py-3 font-medium text-gray-800">${c.name}</td>
                        <td class="px-4 py-3 text-sm">${c.credits}</td>
                        <td class="px-4 py-3"><span class="badge ${getDeptBadge(c.department)}">${c.department}</span></td>
                        <td class="px-4 py-3 text-center">
                            <button onclick="editItem('course', ${c.id})" class="text-blue-600 hover:text-blue-800 mx-1"><i class="fas fa-edit"></i></button>
                            <button onclick="deleteItem('courses', ${c.id})" class="text-red-600 hover:text-red-800 mx-1"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `).join('');
            } catch (e) { console.error(e); }
        }

        async function refreshAll() {
            await loadStats();
            const searchVal = {
                students: document.getElementById('studentSearch').value.toLowerCase(),
                faculty: document.getElementById('facultySearch').value.toLowerCase(),
                courses: document.getElementById('courseSearch').value.toLowerCase()
            };
            await loadStudents(searchVal.students);
            await loadFaculty(searchVal.faculty);
            await loadCourses(searchVal.courses);
        }

        // ==================== DELETE ====================
        async function deleteItem(endpoint, id) {
            if (!confirm('Are you sure you want to delete this item?')) return;
            try {
                await api('DELETE', `/api/${endpoint}/${id}`);
                await refreshAll();
            } catch (e) { alert('Error deleting: ' + e.message); }
        }

        // ==================== MODAL ====================
        function openModal(type, data = null) {
            editType = type;
            editId = data?.id || null;
            const modal = document.getElementById('modal');
            const title = document.getElementById('modalTitle');
            const fields = document.getElementById('modalFields');
            
            const isEdit = !!editId;
            title.textContent = isEdit ? `Edit ${type.charAt(0).toUpperCase() + type.slice(1)}` : `Add New ${type.charAt(0).toUpperCase() + type.slice(1)}`;
            
            let html = '';
            if (type === 'student') {
                html = `
                    <input type="text" name="name" placeholder="Full Name" value="${data?.name || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="email" name="email" placeholder="Email" value="${data?.email || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <select name="course" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                        <option value="">Select Course</option>
                        <option value="Computer Science" ${data?.course === 'Computer Science' ? 'selected' : ''}>Computer Science</option>
                        <option value="Mathematics" ${data?.course === 'Mathematics' ? 'selected' : ''}>Mathematics</option>
                        <option value="Physics" ${data?.course === 'Physics' ? 'selected' : ''}>Physics</option>
                        <option value="Electronics" ${data?.course === 'Electronics' ? 'selected' : ''}>Electronics</option>
                    </select>
                    <input type="number" name="year" placeholder="Year (1-4)" value="${data?.year || ''}" min="1" max="4" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="date" name="enrollment_date" value="${data?.enrollment_date || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                `;
            } else if (type === 'faculty') {
                html = `
                    <input type="text" name="name" placeholder="Full Name" value="${data?.name || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="email" name="email" placeholder="Email" value="${data?.email || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <select name="department" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                        <option value="">Select Department</option>
                        <option value="Computer Science" ${data?.department === 'Computer Science' ? 'selected' : ''}>Computer Science</option>
                        <option value="Mathematics" ${data?.department === 'Mathematics' ? 'selected' : ''}>Mathematics</option>
                        <option value="Physics" ${data?.department === 'Physics' ? 'selected' : ''}>Physics</option>
                        <option value="Electronics" ${data?.department === 'Electronics' ? 'selected' : ''}>Electronics</option>
                    </select>
                    <input type="text" name="designation" placeholder="Designation (e.g., Professor, Associate Professor)" value="${data?.designation || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                `;
            } else if (type === 'course') {
                html = `
                    <input type="text" name="code" placeholder="Course Code (e.g., CS101)" value="${data?.code || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="text" name="name" placeholder="Course Name" value="${data?.name || ''}" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <input type="number" name="credits" placeholder="Credits" value="${data?.credits || ''}" min="1" max="6" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    <select name="department" required class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                        <option value="">Select Department</option>
                        <option value="Computer Science" ${data?.department === 'Computer Science' ? 'selected' : ''}>Computer Science</option>
                        <option value="Mathematics" ${data?.department === 'Mathematics' ? 'selected' : ''}>Mathematics</option>
                        <option value="Physics" ${data?.department === 'Physics' ? 'selected' : ''}>Physics</option>
                        <option value="Electronics" ${data?.department === 'Electronics' ? 'selected' : ''}>Electronics</option>
                    </select>
                `;
            }
            fields.innerHTML = html;
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }

        function closeModal() {
            document.getElementById('modal').classList.add('hidden');
            document.getElementById('modal').classList.remove('flex');
            editId = null;
            editType = null;
        }

        async function editItem(type, id) {
            try {
                const data = await api('GET', `/api/${type}s`);
                const item = data.find(d => d.id === id);
                if (item) openModal(type, item);
            } catch (e) { alert('Error loading item: ' + e.message); }
        }

        // Modal form submit
        document.getElementById('modalForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const data = {};
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(inp => { data[inp.name] = inp.value; });
            
            try {
                const endpoint = editType === 'student' ? 'students' : editType === 'faculty' ? 'faculty' : 'courses';
                const method = editId ? 'PUT' : 'POST';
                const url = editId ? `/api/${endpoint}/${editId}` : `/api/${endpoint}`;
                await api(method, url, data);
                closeModal();
                await refreshAll();
            } catch (err) {
                alert('Error saving: ' + err.message);
            }
        });

        // ==================== TAB SWITCHING ====================
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('tab-active'));
                this.classList.add('tab-active');
                const tab = this.dataset.tab;
                currentTab = tab;
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                document.getElementById(`tab-${tab}`).classList.remove('hidden');
            });
        });

        // ==================== SEARCH ====================
        document.getElementById('studentSearch').addEventListener('input', (e) => {
            loadStudents(e.target.value.toLowerCase());
        });
        document.getElementById('facultySearch').addEventListener('input', (e) => {
            loadFaculty(e.target.value.toLowerCase());
        });
        document.getElementById('courseSearch').addEventListener('input', (e) => {
            loadCourses(e.target.value.toLowerCase());
        });

        // ==================== CLOCK ====================
        function updateClock() {
            document.getElementById('liveTime').textContent = new Date().toLocaleTimeString('en-US', { hour12: false });
        }
        setInterval(updateClock, 1000);
        updateClock();

        // ==================== INIT ====================
        refreshAll();

        // Click outside modal to close
        document.getElementById('modal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) closeModal();
        });
    </script>
</body>
</html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)