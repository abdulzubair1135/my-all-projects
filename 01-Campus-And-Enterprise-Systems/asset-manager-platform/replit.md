# College Face

## Overview

College Face is a campus-focused social media platform designed for college communities. It combines three distinct content types: Normal Posts (photo/text sharing), Notes (study materials with PDF/image uploads), and Anonymous Confessions. The platform features a modern dark-themed UI with glassmorphism effects, targeting a unique campus community experience rather than a generic social media clone.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (January 2026)

### Admin Dashboard
- Full admin panel at `/admin` for user/content management
- User suspension and unsuspension capabilities
- Post deletion from admin interface
- Warning message system (sends DMs to users)
- Ads management: create/delete promotional ads with images/GIFs
- Report review and resolution

### Social Features
- Follow/unfollow users on profile pages
- Follower/following counts displayed
- Private messaging system at `/messages`
- Community group chat at `/community`

### Security Enhancements
- Rate limiting: 100 requests per 15 minutes per IP
- Security headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP, Referrer-Policy
- Suspended user middleware blocking access
- Authentication required to view posts and content
- Password change feature in Settings (validates current password, min 6 chars)
- Visitor tracking: Records IP address, browser info, and path for all visitors
- Emergency logout button: Admin can force logout all non-admin users instantly with "Server Crashed" message
- Unknown visitors alert panel in admin Security tab

### Message Notifications
- Unread message count badge displayed in navigation sidebar
- Red notification badge shows on Messages link when new messages arrive
- Auto-polls every 30 seconds for new messages
- Messages automatically marked as read when conversation is opened

### Navigation Updates
- Admin Panel link in sidebar (admin users only)
- Community, Messages, Help links in navigation
- Events page: admin-only posting, back button added

### Ads System
- Right-side panel displays ads on desktop (hidden on mobile)
- Admins create ads via `/admin` with title, image file upload (required), optional link
- Ads stored in database with createdBy tracking
- Images displayed at max 1080px width

### Premium Subscription
- Admin can grant/revoke premium status for users via toggle switch in Users tab
- Premium users have crown badge displayed next to their username

### Image Display
- All images (posts, events, ads) displayed at max 1080px width
- Events require image upload by admin
- Posts show images inline instead of download links

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight React router)
- **State Management**: TanStack React Query for server state, React hooks for local state
- **Styling**: Tailwind CSS with custom design tokens, shadcn/ui component library (New York style)
- **Build Tool**: Vite with path aliases (@/, @shared/, @assets/)
- **Theme System**: Dark/light mode with multiple color theme options (indigo, emerald, rose, amber)

The frontend follows a component-based architecture with clear separation:
- Pages in `client/src/pages/`
- Reusable components in `client/src/components/`
- Custom hooks in `client/src/hooks/`
- UI primitives from shadcn/ui in `client/src/components/ui/`

### Backend Architecture
- **Runtime**: Node.js with Express
- **Language**: TypeScript with ES Modules
- **API Design**: RESTful endpoints defined in `shared/routes.ts` with Zod schema validation
- **File Uploads**: Multer middleware storing files in `/uploads` directory (25MB limit, images and PDFs only)
- **Session Management**: Express sessions with Passport.js
- **Rate Limiting**: express-rate-limit with 100 req/15min limit

### Data Storage
- **Database**: PostgreSQL via Drizzle ORM
- **Schema Location**: `shared/schema.ts` - defines users, posts, comments, likes, reports, events, messages, follows, communityMessages, and ads tables
- **Migrations**: Drizzle Kit with migrations output to `/migrations`
- **Connection**: Uses DATABASE_URL environment variable

### Database Tables
- `users`: User accounts with roles (user/admin), suspension status, premium status
- `posts`: All content types (posts, notes, confessions)
- `comments`: Post comments
- `likes`: Post likes
- `reports`: Content reports for moderation
- `events`: Campus events with images
- `messages`: Private DMs and warning messages
- `follows`: User follow relationships
- `communityMessages`: Group chat messages
- `ads`: Promotional advertisements
- `visitors`: Visitor tracking for security (IP, browser, path)
- `systemSettings`: System settings (emergency logout state)
- `collegeUsers`: Authorized college users list (admin maintained)
- `pendingUsers`: Pending user registrations waiting for admin approval

### Authentication & Authorization
- **Strategy**: Session-based authentication using Passport.js with Local Strategy
- **Password Hashing**: bcryptjs for secure password storage
- **User Roles**: Supports 'user' and 'admin' roles
- **Session Store**: Memory store (development) with secure cookies in production
- **Admin Features**: Suspend users, delete content, manage ads, send warnings, manage college users, approve registrations

### User Registration Flow
1. Admin adds authorized students to the College Users list
2. When a new user registers, system checks if their username is in the college list
3. If not authorized: Shows "Not authorized - check your account" message
4. If authorized: Creates a pending registration request
5. Admin approves or rejects the pending registration in Admin > Pending tab
6. Once approved, user can log in with their credentials

### Shared Code
The `shared/` directory contains code used by both frontend and backend:
- `schema.ts`: Database table definitions and Zod validation schemas
- `routes.ts`: API endpoint definitions with request/response schemas

### Build System
- **Development**: tsx for running TypeScript directly, Vite dev server with HMR
- **Production**: Custom build script using esbuild for server bundling, Vite for client
- **Output**: Compiled to `dist/` with server as `index.cjs` and client in `dist/public/`

## External Dependencies

### Database
- PostgreSQL (required, connection via DATABASE_URL environment variable)
- Drizzle ORM for database operations

### Key NPM Packages
- **UI**: Radix UI primitives, Lucide React icons, class-variance-authority
- **Forms**: React Hook Form with Zod resolvers
- **Date Handling**: date-fns
- **File Upload**: Multer
- **Security**: express-rate-limit

### Environment Variables Required
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret for session encryption (defaults to fallback in development)
- `SUPER_ADMIN_PASSWORD`: Optional admin password for seeding
- `RESEND_API_KEY`: (Optional, for future OTP) Resend API key for email verification

## Future Enhancements

### OTP Email Verification (Not Yet Implemented)
- Email OTP verification for signup is planned but not yet implemented
- Requires Resend integration with API key stored as `RESEND_API_KEY` secret
- When ready, set up the Resend connector in Replit integrations or provide the API key manually

### Replit-Specific Integrations
- `@replit/vite-plugin-runtime-error-modal`: Error overlay in development
- `@replit/vite-plugin-cartographer`: Development tooling
- `@replit/vite-plugin-dev-banner`: Development banner
