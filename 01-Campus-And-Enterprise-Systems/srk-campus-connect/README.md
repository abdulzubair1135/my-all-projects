# Campus Presence, Attendance & Faculty Coordination System

A production-grade, offline-first college campus coordination platform uniting students, faculty, and administration across 3 Flutter applications and a unified Node.js/TypeScript backend.

## System Architecture

- **Apps**:
  - `apps/student_app`: Student timetable, dynamic QR scanning, presence event signing, attendance tracking, leave requests.
  - `apps/teacher_app`: Faculty dashboard, timetable, classroom QR verification, dynamic rolling QR generation, live presence monitoring, meeting responses.
  - `apps/admin_app`: Principal & Admin master data, campus presence radar, timetable editor, analytics, meeting requests, audit logs.
- **Backend**:
  - `backend`: Node.js / TypeScript / Express / MongoDB / Socket.IO / FCM API server with Ed25519 signature validation, presence confidence engine, and offline sync processor.
- **Shared Packages**:
  - `packages/shared_types`: Cross-platform TypeScript contracts, DTOs, and schemas.
  - `packages/dart_core`: Shared Flutter/Dart models, SQLite offline queue, Dio API client, and Ed25519 crypto helpers.

## Features
- **Offline-First**: Signed presence events stored locally and synced when network resumes.
- **P2P Mesh / Peer Forwarding**: Gateway election mechanism for offline peers.
- **Dynamic Rolling QR**: 15s rotating nonce to prevent screenshot reuse and replay attacks.
- **Presence Confidence Engine**: Configurable weighted evidence scoring ($0-100\%$).
- **Strict RBAC & Audit Trails**: Role-based access control with comprehensive audit logging.
