import { pgTable, text, serial, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
import { relations } from "drizzle-orm";

// === TABLE DEFINITIONS ===

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  email: text("email"),
  phone: text("phone"),
  name: text("name"),
  bio: text("bio"),
  profileEmoji: text("profile_emoji").default("🎓"),
  isPrivate: boolean("is_private").default(false),
  acceptedPrivacyPolicy: boolean("accepted_privacy_policy").default(false),
  role: text("role").default("user"), // 'user' or 'admin'
  isPremium: boolean("is_premium").default(false),
  isSuspended: boolean("is_suspended").default(false),
  suspendedReason: text("suspended_reason"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const posts = pgTable("posts", {
  id: serial("id").primaryKey(),
  type: text("type").notNull(), // 'normal', 'notes', 'confession'
  category: text("category").notNull(), // 'general', 'notes', 'events', 'memes', 'confession', 'trending'
  userId: integer("user_id").notNull(),
  isAnonymous: boolean("is_anonymous").default(false),
  caption: text("caption"),
  title: text("title"),   // For notes
  subject: text("subject"), // For notes
  fileUrl: text("file_url"),
  fileType: text("file_type"), // 'image/png', 'application/pdf', etc.
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const comments = pgTable("comments", {
  id: serial("id").primaryKey(),
  postId: integer("post_id").notNull(),
  userId: integer("user_id").notNull(),
  text: text("text").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const likes = pgTable("likes", {
  id: serial("id").primaryKey(),
  postId: integer("post_id").notNull(),
  userId: integer("user_id").notNull(),
});

export const reports = pgTable("reports", {
  id: serial("id").primaryKey(),
  postId: integer("post_id").notNull(),
  userId: integer("user_id").notNull(),
  reason: text("reason").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const events = pgTable("events", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  date: timestamp("date").notNull(),
  location: text("location"),
  imageUrl: text("image_url"),
  userId: integer("user_id").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  senderId: integer("sender_id").notNull(),
  receiverId: integer("receiver_id").notNull(),
  content: text("content").notNull(),
  type: text("type").default("message"), // 'message', 'warning', 'system'
  isRead: boolean("is_read").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

export const follows = pgTable("follows", {
  id: serial("id").primaryKey(),
  followerId: integer("follower_id").notNull(),
  followingId: integer("following_id").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const ads = pgTable("ads", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  imageUrl: text("image_url").notNull(),
  linkUrl: text("link_url"),
  isActive: boolean("is_active").default(true),
  createdBy: integer("created_by").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const communityMessages = pgTable("community_messages", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").notNull(),
  content: text("content").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// Visitor tracking for security
export const visitors = pgTable("visitors", {
  id: serial("id").primaryKey(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  path: text("path"),
  userId: integer("user_id"),
  isAuthenticated: boolean("is_authenticated").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

// System settings (emergency logout, etc.)
export const systemSettings = pgTable("system_settings", {
  id: serial("id").primaryKey(),
  key: text("key").notNull().unique(),
  value: text("value"),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Authorized college users list (admin maintains this)
export const collegeUsers = pgTable("college_users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  email: text("email"),
  name: text("name"),
  department: text("department"),
  addedBy: integer("added_by"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Pending user registrations waiting for admin approval
export const pendingUsers = pgTable("pending_users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  email: text("email"),
  phone: text("phone"),
  acceptedPrivacyPolicy: boolean("accepted_privacy_policy").default(false),
  status: text("status").default("pending"), // 'pending', 'approved', 'rejected'
  createdAt: timestamp("created_at").defaultNow(),
});

// Archive tables for storing deleted content (24hr auto-delete)
export const archivedPosts = pgTable("archived_posts", {
  id: serial("id").primaryKey(),
  originalId: integer("original_id").notNull(),
  type: text("type").notNull(),
  category: text("category").notNull(),
  userId: integer("user_id").notNull(),
  isAnonymous: boolean("is_anonymous").default(false),
  caption: text("caption"),
  title: text("title"),
  subject: text("subject"),
  fileUrl: text("file_url"),
  fileType: text("file_type"),
  originalCreatedAt: timestamp("original_created_at"),
  archivedAt: timestamp("archived_at").defaultNow(),
});

export const archivedMessages = pgTable("archived_messages", {
  id: serial("id").primaryKey(),
  originalId: integer("original_id").notNull(),
  senderId: integer("sender_id").notNull(),
  receiverId: integer("receiver_id").notNull(),
  content: text("content").notNull(),
  type: text("type").default("message"),
  originalCreatedAt: timestamp("original_created_at"),
  archivedAt: timestamp("archived_at").defaultNow(),
});

// === RELATIONS ===

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  comments: many(comments),
  likes: many(likes),
  reports: many(reports),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  user: one(users, {
    fields: [posts.userId],
    references: [users.id],
  }),
  comments: many(comments),
  likes: many(likes),
  reports: many(reports),
}));

export const commentsRelations = relations(comments, ({ one }) => ({
  post: one(posts, {
    fields: [comments.postId],
    references: [posts.id],
  }),
  user: one(users, {
    fields: [comments.userId],
    references: [users.id],
  }),
}));

export const likesRelations = relations(likes, ({ one }) => ({
  post: one(posts, {
    fields: [likes.postId],
    references: [likes.userId],
  }),
  user: one(users, {
    fields: [likes.userId],
    references: [users.id],
  }),
}));

export const reportsRelations = relations(reports, ({ one }) => ({
  post: one(posts, {
    fields: [reports.postId],
    references: [posts.id],
  }),
  user: one(users, {
    fields: [reports.userId],
    references: [users.id],
  }),
}));

export const eventsRelations = relations(events, ({ one }) => ({
  user: one(users, {
    fields: [events.userId],
    references: [users.id],
  }),
}));

export const messagesRelations = relations(messages, ({ one }) => ({
  sender: one(users, {
    fields: [messages.senderId],
    references: [users.id],
  }),
  receiver: one(users, {
    fields: [messages.receiverId],
    references: [users.id],
  }),
}));

export const followsRelations = relations(follows, ({ one }) => ({
  follower: one(users, {
    fields: [follows.followerId],
    references: [users.id],
  }),
  following: one(users, {
    fields: [follows.followingId],
    references: [users.id],
  }),
}));

export const adsRelations = relations(ads, ({ one }) => ({
  creator: one(users, {
    fields: [ads.createdBy],
    references: [users.id],
  }),
}));

export const communityMessagesRelations = relations(communityMessages, ({ one }) => ({
  user: one(users, {
    fields: [communityMessages.userId],
    references: [users.id],
  }),
}));

// === SCHEMAS ===

export const insertUserSchema = createInsertSchema(users).extend({
  email: z.string().email().optional().or(z.literal("")),
  phone: z.string().optional().or(z.literal("")),
}).omit({ id: true, createdAt: true });

export const updateUserSchema = insertUserSchema.partial();

export const insertPostSchema = createInsertSchema(posts).omit({ id: true, createdAt: true, updatedAt: true });
export const updatePostSchema = insertPostSchema.partial();

export const insertCommentSchema = createInsertSchema(comments).omit({ id: true, createdAt: true });
export const insertReportSchema = createInsertSchema(reports).omit({ id: true, createdAt: true });
export const insertEventSchema = createInsertSchema(events).omit({ id: true, createdAt: true });
export const insertMessageSchema = createInsertSchema(messages).omit({ id: true, createdAt: true });
export const insertFollowSchema = createInsertSchema(follows).omit({ id: true, createdAt: true });
export const insertAdSchema = createInsertSchema(ads).omit({ id: true, createdAt: true });
export const insertCommunityMessageSchema = createInsertSchema(communityMessages).omit({ id: true, createdAt: true });
export const insertVisitorSchema = createInsertSchema(visitors).omit({ id: true, createdAt: true });
export const insertSystemSettingSchema = createInsertSchema(systemSettings).omit({ id: true, updatedAt: true });
export const insertCollegeUserSchema = createInsertSchema(collegeUsers).omit({ id: true, createdAt: true });
export const insertPendingUserSchema = createInsertSchema(pendingUsers).omit({ id: true, createdAt: true });

// === TYPES ===

export type User = typeof users.$inferSelect;
export type Post = typeof posts.$inferSelect;
export type Comment = typeof comments.$inferSelect;
export type Like = typeof likes.$inferSelect;
export type Report = typeof reports.$inferSelect;
export type Event = typeof events.$inferSelect;
export type Message = typeof messages.$inferSelect;
export type Follow = typeof follows.$inferSelect;
export type Ad = typeof ads.$inferSelect;
export type CommunityMessage = typeof communityMessages.$inferSelect;
export type Visitor = typeof visitors.$inferSelect;
export type SystemSetting = typeof systemSettings.$inferSelect;
export type CollegeUser = typeof collegeUsers.$inferSelect;
export type PendingUser = typeof pendingUsers.$inferSelect;

export type InsertUser = z.infer<typeof insertUserSchema>;
export type UpdateUser = z.infer<typeof updateUserSchema>;
export type InsertPost = z.infer<typeof insertPostSchema>;
export type UpdatePost = z.infer<typeof updatePostSchema>;
export type InsertComment = z.infer<typeof insertCommentSchema>;
export type InsertReport = z.infer<typeof insertReportSchema>;
export type InsertEvent = z.infer<typeof insertEventSchema>;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type InsertFollow = z.infer<typeof insertFollowSchema>;
export type InsertAd = z.infer<typeof insertAdSchema>;
export type InsertCommunityMessage = z.infer<typeof insertCommunityMessageSchema>;
export type InsertVisitor = z.infer<typeof insertVisitorSchema>;
export type InsertSystemSetting = z.infer<typeof insertSystemSettingSchema>;
export type InsertCollegeUser = z.infer<typeof insertCollegeUserSchema>;
export type InsertPendingUser = z.infer<typeof insertPendingUserSchema>;

// API Types
export type PostWithDetails = Post & {
  user?: User;
  likes: Like[];
  comments: (Comment & { user: User })[];
  likeCount: number;
  hasLiked: boolean;
};

export type LoginRequest = { username: string; password: string };
export type AuthResponse = { user: User; token?: string };
