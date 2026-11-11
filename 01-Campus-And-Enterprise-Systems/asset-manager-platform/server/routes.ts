import type { Express } from "express";
import type { Server } from "http";
import { setupAuth } from "./auth";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import multer from "multer";
import path from "path";
import fs from "fs";
import express from "express";
import rateLimit from "express-rate-limit";
import bcrypt from "bcryptjs";

// Ensure uploads directory exists
const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Configure Multer
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => {
      cb(null, "uploads/");
    },
    filename: (req, file, cb) => {
      const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
      cb(null, uniqueSuffix + path.extname(file.originalname));
    }
  }),
  limits: { fileSize: 25 * 1024 * 1024 }, // 25MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith("image/") || file.mimetype === "application/pdf") {
      cb(null, true);
    } else {
      cb(new Error("Only images and PDFs are allowed"));
    }
  }
});

// Rate limiters for security
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: { message: "Too many requests, please try again later." }
});

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10, // limit login/register attempts
  message: { message: "Too many authentication attempts, please try again later." }
});

// Middleware to check if user is suspended
function checkSuspended(req: any, res: any, next: any) {
  if (req.user?.isSuspended) {
    return res.status(403).json({ message: "Your account has been suspended: " + (req.user.suspendedReason || "Contact admin for details") });
  }
  next();
}

// Middleware to check if user is admin
function requireAdmin(req: any, res: any, next: any) {
  if (!req.isAuthenticated()) return res.sendStatus(401);
  if (req.user.role !== 'admin') return res.sendStatus(403);
  next();
}

// Auto-cleanup scheduler - runs every hour with instance protection
let cleanupRunning = false;

function startCleanupScheduler() {
  const runCleanup = async () => {
    // Prevent concurrent runs
    if (cleanupRunning) {
      console.log("[Cleanup] Already running, skipping...");
      return;
    }
    
    cleanupRunning = true;
    try {
      const deletedPosts = await storage.archiveAndDeleteOldPosts();
      const deletedMessages = await storage.archiveAndDeleteOldMessages();
      if (deletedPosts > 0 || deletedMessages > 0) {
        console.log(`[Cleanup] Archived and deleted ${deletedPosts} posts and ${deletedMessages} messages`);
      }
    } catch (err) {
      console.error("[Cleanup] Error during cleanup:", err);
    } finally {
      cleanupRunning = false;
    }
  };
  
  // Run after a delay on startup
  setTimeout(runCleanup, 30000);
  
  // Then run every hour
  setInterval(runCleanup, 60 * 60 * 1000);
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Start auto-cleanup scheduler
  startCleanupScheduler();
  
  // Security headers
  app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:;");
    next();
  });

  // Apply rate limiting
  app.use('/api/', generalLimiter);
  app.use('/api/login', authLimiter);
  app.use('/api/register', authLimiter);

  // Static uploads serving
  app.use('/uploads', express.static('uploads'));

  // Setup Auth (Passport)
  setupAuth(app);

  // Visitor tracking middleware (after auth setup so isAuthenticated works)
  app.use(async (req, res, next) => {
    try {
      const ipAddress = req.headers['x-forwarded-for'] as string || req.socket.remoteAddress || 'unknown';
      const userAgent = req.headers['user-agent'] || 'unknown';
      const path = req.path;
      
      // Only track API and page requests, skip static files
      if (!path.startsWith('/uploads') && !path.includes('.')) {
        await storage.createVisitor({
          ipAddress: ipAddress.split(',')[0].trim(),
          userAgent,
          path,
          userId: req.isAuthenticated() ? (req.user as any).id : null,
          isAuthenticated: req.isAuthenticated()
        });
      }
    } catch (e) {
      // Silently fail visitor tracking
    }
    next();
  });

  // Emergency logout check middleware
  app.use(async (req, res, next) => {
    if (req.isAuthenticated() && (req.user as any).role !== 'admin') {
      const logoutTime = await storage.getEmergencyLogoutTime();
      if (logoutTime) {
        req.logout((err) => {});
        return res.status(503).json({ 
          message: "Server Crashed - Please try again later",
          emergencyLogout: true,
          serverCrashed: true
        });
      }
    }
    next();
  });

  // === POSTS ROUTES ===
  
  app.get(api.posts.list.path, async (req, res) => {
    // Require authentication to view posts
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const filters = {
        category: req.query.category as string | undefined,
        search: req.query.search as string | undefined,
        sort: req.query.sort as 'latest' | 'top' | undefined,
        trending: req.query.trending === 'true',
      };
      // @ts-ignore
      const currentUserId = req.user.id;
      const posts = await storage.getPosts(filters, currentUserId);
      res.json(posts);
    } catch (e) {
      res.status(500).json({ message: "Internal Server Error" });
    }
  });

  app.get(api.posts.get.path, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    const id = parseInt(req.params.id);
    if (isNaN(id)) return res.status(404).json({ message: "Invalid ID" });
    
    // @ts-ignore
    const currentUserId = req.user.id;
    const post = await storage.getPost(id, currentUserId);
    if (!post) return res.status(404).json({ message: "Post not found" });
    res.json(post);
  });

  app.patch("/api/posts/:id", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const id = parseInt(req.params.id);
    const post = await storage.getPost(id);
    if (!post) return res.sendStatus(404);
    
    // @ts-ignore
    if (post.userId !== req.user.id && req.user.role !== 'admin') return res.sendStatus(403);

    const updated = await storage.updatePost(id, req.body);
    res.json(updated);
  });

  app.patch("/api/user", checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    // @ts-ignore
    const updated = await storage.updateUser(req.user.id, req.body);
    res.json(updated);
  });

  // Password change
  app.post("/api/user/change-password", checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    const { currentPassword, newPassword } = req.body;
    if (!currentPassword || !newPassword) {
      return res.status(400).json({ message: "Current and new password required" });
    }
    if (newPassword.length < 6) {
      return res.status(400).json({ message: "New password must be at least 6 characters" });
    }
    
    // @ts-ignore
    const user = await storage.getUser(req.user.id);
    if (!user) return res.sendStatus(404);
    
    const isValid = await bcrypt.compare(currentPassword, user.password);
    if (!isValid) {
      return res.status(400).json({ message: "Current password is incorrect" });
    }
    
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    // @ts-ignore
    await storage.updateUser(req.user.id, { password: hashedPassword });
    res.json({ message: "Password changed successfully" });
  });

  // Unread messages count
  app.get("/api/messages/unread-count", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    // @ts-ignore
    const count = await storage.getUnreadMessageCount(req.user.id);
    res.json({ count });
  });

  app.post(api.posts.create.path, checkSuspended, upload.single("file"), async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);

    try {
      const body = {
        ...req.body,
        isAnonymous: req.body.isAnonymous === "true" || req.body.isAnonymous === true,
      };
      const input = api.posts.create.input.parse(body);
      
      const fileUrl = req.file ? `/uploads/${req.file.filename}` : undefined;
      const fileType = req.file ? req.file.mimetype : undefined;

      const post = await storage.createPost({
        ...input,
        // @ts-ignore
        userId: req.user.id,
        fileUrl,
        fileType,
      });
      res.status(201).json(post);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      console.error(err);
      res.status(500).json({ message: "Failed to create post" });
    }
  });

  app.delete(api.posts.delete.path, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    const id = parseInt(req.params.id);
    const post = await storage.getPost(id);
    
    if (!post) return res.sendStatus(404);
    
    // @ts-ignore
    if (post.userId !== req.user.id && req.user.role !== 'admin') {
      return res.sendStatus(403);
    }

    await storage.deletePost(id);
    res.sendStatus(200);
  });

  app.post(api.posts.like.path, checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    const id = parseInt(req.params.id);
    // @ts-ignore
    const result = await storage.toggleLike(id, req.user.id);
    res.json(result);
  });

  // === COMMENTS ===

  app.post(api.comments.create.path, checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);

    try {
      const input = api.comments.create.input.parse(req.body);
      const postId = parseInt(req.params.postId);
      
      const comment = await storage.createComment({
        ...input,
        postId,
        // @ts-ignore
        userId: req.user.id,
      });
      res.status(201).json(comment);
    } catch (err) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  // === REPORTS ===

  app.post(api.reports.create.path, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    
    try {
      const input = api.reports.create.input.parse(req.body);
      const postId = parseInt(req.params.postId);
      
      const report = await storage.createReport({
        ...input,
        postId,
        // @ts-ignore
        userId: req.user.id,
      });
      res.status(201).json(report);
    } catch (err) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  app.get(api.reports.list.path, requireAdmin, async (req, res) => {
    const reports = await storage.getReports();
    res.json(reports);
  });

  app.delete("/api/reports/:id", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deleteReport(id);
    res.sendStatus(200);
  });

  // === USER SEARCH ===
  app.get("/api/users/search", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    try {
      const query = (req.query.q as string) || "";
      const users = await storage.searchUsers(query);
      res.json(users);
    } catch (e) {
      res.status(500).json({ message: "Internal Server Error" });
    }
  });

  // === ADMIN USER MANAGEMENT ===
  app.get("/api/admin/users", requireAdmin, async (req, res) => {
    const users = await storage.getAllUsers();
    res.json(users);
  });

  app.post("/api/admin/users/:id/suspend", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    const { reason } = req.body;
    const user = await storage.suspendUser(id, reason || "Violation of community guidelines");
    res.json(user);
  });

  app.post("/api/admin/users/:id/unsuspend", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    const user = await storage.unsuspendUser(id);
    res.json(user);
  });

  app.delete("/api/admin/users/:id", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deleteUser(id);
    res.sendStatus(200);
  });

  app.post("/api/admin/users/:id/warn", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    const { message } = req.body;
    // @ts-ignore
    const warning = await storage.createMessage({
      senderId: req.user.id,
      receiverId: id,
      content: message,
      type: "warning"
    });
    res.status(201).json(warning);
  });

  // Premium subscription toggle
  app.post("/api/admin/users/:id/premium", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    const { isPremium } = req.body;
    const user = await storage.toggleUserPremium(id, isPremium);
    res.json(user);
  });

  // Visitor tracking for admin alerts
  app.get("/api/admin/visitors", requireAdmin, async (req, res) => {
    const visitors = await storage.getVisitors(100);
    res.json(visitors);
  });

  app.get("/api/admin/unknown-visitors", requireAdmin, async (req, res) => {
    const visitors = await storage.getRecentUnknownVisitors(50);
    res.json(visitors);
  });

  // Emergency logout controls
  app.post("/api/admin/emergency-logout", requireAdmin, async (req, res) => {
    await storage.triggerEmergencyLogout();
    res.json({ success: true, message: "Emergency logout triggered - all non-admin users will be logged out" });
  });

  app.delete("/api/admin/emergency-logout", requireAdmin, async (req, res) => {
    await storage.clearEmergencyLogout();
    res.json({ success: true, message: "Emergency logout cleared" });
  });

  app.get("/api/admin/emergency-status", requireAdmin, async (req, res) => {
    const logoutTime = await storage.getEmergencyLogoutTime();
    res.json({ active: !!logoutTime, triggeredAt: logoutTime });
  });

  // === EVENTS ===
  app.get("/api/events", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    try {
      const events = await storage.getEvents();
      res.json(events);
    } catch (e) {
      res.status(500).json({ message: "Internal Server Error" });
    }
  });

  app.post("/api/events", requireAdmin, upload.single('image'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "Image is required for events" });
      }
      const imageUrl = `/uploads/${req.file.filename}`;
      const event = await storage.createEvent({
        title: req.body.title,
        description: req.body.description,
        date: new Date(req.body.date),
        location: req.body.location,
        imageUrl,
        // @ts-ignore
        userId: req.user.id,
      });
      res.status(201).json(event);
    } catch (e) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  app.delete("/api/events/:id", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deleteEvent(id);
    res.sendStatus(200);
  });

  // === MESSAGES ===
  app.get("/api/messages", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    // @ts-ignore
    const messages = await storage.getMessages(req.user.id);
    res.json(messages);
  });

  app.get("/api/messages/:userId", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const otherUserId = parseInt(req.params.userId);
    // @ts-ignore
    const messages = await storage.getConversation(req.user.id, otherUserId);
    // Mark messages from the other user as read
    // @ts-ignore
    await storage.markConversationRead(req.user.id, otherUserId);
    res.json(messages);
  });

  app.post("/api/messages", checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    try {
      const { receiverId, content } = req.body;
      const message = await storage.createMessage({
        // @ts-ignore
        senderId: req.user.id,
        receiverId: parseInt(receiverId),
        content,
        type: "message"
      });
      res.status(201).json(message);
    } catch (e) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  app.patch("/api/messages/:id/read", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const id = parseInt(req.params.id);
    await storage.markMessageRead(id);
    res.sendStatus(200);
  });

  // === FOLLOWS ===
  app.post("/api/users/:id/follow", checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const followingId = parseInt(req.params.id);
    // @ts-ignore
    if (followingId === req.user.id) {
      return res.status(400).json({ message: "Cannot follow yourself" });
    }
    // @ts-ignore
    const result = await storage.toggleFollow(req.user.id, followingId);
    res.json(result);
  });

  app.get("/api/users/:id/followers", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const userId = parseInt(req.params.id);
    const followers = await storage.getFollowers(userId);
    res.json(followers);
  });

  app.get("/api/users/:id/following", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const userId = parseInt(req.params.id);
    const following = await storage.getFollowing(userId);
    res.json(following);
  });

  app.get("/api/users/:id/follow-counts", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const userId = parseInt(req.params.id);
    const counts = await storage.getFollowCounts(userId);
    res.json(counts);
  });

  app.get("/api/users/:id/is-following", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const followingId = parseInt(req.params.id);
    // @ts-ignore
    const isFollowing = await storage.isFollowing(req.user.id, followingId);
    res.json({ isFollowing });
  });

  // === ADS ===
  app.get("/api/ads", async (req, res) => {
    const ads = await storage.getActiveAds();
    res.json(ads);
  });

  app.post("/api/ads", requireAdmin, upload.single("image"), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "Image is required for ads" });
      }
      const imageUrl = `/uploads/${req.file.filename}`;
      const ad = await storage.createAd({
        title: req.body.title,
        imageUrl,
        linkUrl: req.body.linkUrl,
        // @ts-ignore
        createdBy: req.user.id
      });
      res.status(201).json(ad);
    } catch (e) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  app.delete("/api/ads/:id", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deleteAd(id);
    res.sendStatus(200);
  });

  app.patch("/api/ads/:id/toggle", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    const ad = await storage.toggleAdActive(id);
    res.json(ad);
  });

  // === COMMUNITY CHAT ===
  app.get("/api/community", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const messages = await storage.getCommunityMessages(100);
    res.json(messages);
  });

  app.post("/api/community", checkSuspended, async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    try {
      const { content } = req.body;
      const message = await storage.createCommunityMessage({
        // @ts-ignore
        userId: req.user.id,
        content
      });
      res.status(201).json(message);
    } catch (e) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  // === USER PROFILE BY USERNAME ===
  app.get("/api/users/:username", async (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    const user = await storage.getUserByUsername(req.params.username);
    if (!user) return res.status(404).json({ message: "User not found" });
    // Don't expose password
    const { password, ...safeUser } = user;
    res.json(safeUser);
  });

  // === COLLEGE USERS MANAGEMENT ===
  app.get("/api/admin/college-users", requireAdmin, async (req, res) => {
    const users = await storage.getCollegeUsers();
    res.json(users);
  });

  app.post("/api/admin/college-users", requireAdmin, async (req, res) => {
    try {
      const { username, email, name, department } = req.body;
      
      // Check if already exists
      const existing = await storage.getCollegeUserByUsername(username);
      if (existing) {
        return res.status(400).json({ message: "Username already in college list" });
      }

      const user = await storage.createCollegeUser({
        username,
        email: email || null,
        name: name || null,
        department: department || null,
        addedBy: (req.user as any).id
      });
      res.status(201).json(user);
    } catch (e) {
      res.status(400).json({ message: "Invalid input" });
    }
  });

  app.delete("/api/admin/college-users/:id", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deleteCollegeUser(id);
    res.sendStatus(200);
  });

  // === PENDING REGISTRATIONS ===
  app.get("/api/admin/pending-users", requireAdmin, async (req, res) => {
    const users = await storage.getPendingUsers();
    res.json(users);
  });

  app.post("/api/admin/pending-users/:id/approve", requireAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const user = await storage.approvePendingUser(id);
      res.json(user);
    } catch (e: any) {
      res.status(400).json({ message: e.message || "Failed to approve user" });
    }
  });

  app.post("/api/admin/pending-users/:id/reject", requireAdmin, async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      await storage.rejectPendingUser(id);
      res.sendStatus(200);
    } catch (e) {
      res.status(400).json({ message: "Failed to reject user" });
    }
  });

  app.delete("/api/admin/pending-users/:id", requireAdmin, async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deletePendingUser(id);
    res.sendStatus(200);
  });

  return httpServer;
}
