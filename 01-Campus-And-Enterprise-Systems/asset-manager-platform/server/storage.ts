import { db } from "./db";
import { eq, desc, and, ilike, or, ne, lt, sql, inArray } from "drizzle-orm";
import { 
  users, posts, comments, likes, reports, events, messages, follows, ads, communityMessages,
  archivedPosts, archivedMessages, visitors, systemSettings, collegeUsers, pendingUsers,
  type User, type InsertUser, type UpdateUser,
  type Post, type InsertPost, type UpdatePost, type PostWithDetails,
  type Comment, type InsertComment,
  type Report, type InsertReport,
  type Event, type InsertEvent,
  type Message, type InsertMessage,
  type Follow, type InsertFollow,
  type Ad, type InsertAd,
  type CommunityMessage, type InsertCommunityMessage,
  type Visitor, type InsertVisitor,
  type SystemSetting,
  type CollegeUser, type InsertCollegeUser,
  type PendingUser, type InsertPendingUser
} from "@shared/schema";

export interface IStorage {
  // User
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: number, user: Partial<UpdateUser>): Promise<User>;
  getAllUsers(): Promise<User[]>;
  suspendUser(id: number, reason: string): Promise<User>;
  unsuspendUser(id: number): Promise<User>;
  deleteUser(id: number): Promise<void>;

  // Posts
  createPost(post: InsertPost): Promise<Post>;
  updatePost(id: number, post: UpdatePost): Promise<Post>;
  getPosts(filters?: { 
    category?: string; 
    search?: string; 
    sort?: 'latest' | 'top'; 
    trending?: boolean 
  }, currentUserId?: number): Promise<PostWithDetails[]>;
  getPost(id: number, currentUserId?: number): Promise<PostWithDetails | undefined>;
  deletePost(id: number): Promise<void>;

  // Interactions
  createComment(comment: InsertComment): Promise<Comment>;
  toggleLike(postId: number, userId: number): Promise<{ likes: number; hasLiked: boolean }>;
  
  // Reports
  createReport(report: InsertReport): Promise<Report>;
  getReports(): Promise<(Report & { post: Post; user: User })[]>;
  deleteReport(id: number): Promise<void>;

  // Events
  createEvent(event: InsertEvent): Promise<Event>;
  getEvents(): Promise<Event[]>;
  deleteEvent(id: number): Promise<void>;

  // Search
  searchUsers(query: string): Promise<User[]>;

  // Messages
  createMessage(message: InsertMessage): Promise<Message>;
  getMessages(userId: number): Promise<(Message & { sender: User })[]>;
  getConversation(userId1: number, userId2: number): Promise<Message[]>;
  markMessageRead(id: number): Promise<void>;
  markConversationRead(userId: number, senderId: number): Promise<void>;
  getUnreadMessageCount(userId: number): Promise<number>;

  // Follows
  toggleFollow(followerId: number, followingId: number): Promise<{ isFollowing: boolean }>;
  getFollowers(userId: number): Promise<User[]>;
  getFollowing(userId: number): Promise<User[]>;
  isFollowing(followerId: number, followingId: number): Promise<boolean>;
  getFollowCounts(userId: number): Promise<{ followers: number; following: number }>;

  // Ads
  createAd(ad: InsertAd): Promise<Ad>;
  getActiveAds(): Promise<Ad[]>;
  deleteAd(id: number): Promise<void>;
  toggleAdActive(id: number): Promise<Ad>;

  // Community Chat
  createCommunityMessage(message: InsertCommunityMessage): Promise<CommunityMessage>;
  getCommunityMessages(limit?: number): Promise<(CommunityMessage & { user: User })[]>;

  // Auto-cleanup (24hr)
  archiveAndDeleteOldPosts(): Promise<number>;
  archiveAndDeleteOldMessages(): Promise<number>;
}

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(user: InsertUser): Promise<User> {
    const [newUser] = await db.insert(users).values(user).returning();
    return newUser;
  }

  async updateUser(id: number, user: Partial<UpdateUser>): Promise<User> {
    const [updatedUser] = await db.update(users).set(user).where(eq(users.id, id)).returning();
    return updatedUser;
  }

  async getAllUsers(): Promise<User[]> {
    return await db.select().from(users).orderBy(desc(users.createdAt));
  }

  async suspendUser(id: number, reason: string): Promise<User> {
    const [user] = await db.update(users).set({ isSuspended: true, suspendedReason: reason }).where(eq(users.id, id)).returning();
    return user;
  }

  async unsuspendUser(id: number): Promise<User> {
    const [user] = await db.update(users).set({ isSuspended: false, suspendedReason: null }).where(eq(users.id, id)).returning();
    return user;
  }

  async deleteUser(id: number): Promise<void> {
    await db.delete(users).where(eq(users.id, id));
  }

  async createPost(post: InsertPost): Promise<Post> {
    const [newPost] = await db.insert(posts).values(post).returning();
    return newPost;
  }

  async updatePost(id: number, post: UpdatePost): Promise<Post> {
    const [updatedPost] = await db.update(posts).set({ ...post, updatedAt: new Date() }).where(eq(posts.id, id)).returning();
    return updatedPost;
  }

  async getPosts(filters?: { 
    category?: string; 
    search?: string; 
    sort?: 'latest' | 'top'; 
    trending?: boolean 
  }, currentUserId?: number): Promise<PostWithDetails[]> {
    const whereConditions = [];
    if (filters?.category) {
      whereConditions.push(eq(posts.category, filters.category));
    }
    if (filters?.search) {
      const search = `%${filters.search}%`;
      whereConditions.push(or(
        ilike(posts.caption, search),
        ilike(posts.title, search),
        ilike(posts.subject, search)
      ));
    }

    const results = await db.query.posts.findMany({
      where: whereConditions.length > 0 ? and(...whereConditions) : undefined,
      with: {
        user: true,
        likes: true,
        comments: {
          with: { user: true },
          orderBy: desc(comments.createdAt),
          limit: 3
        }
      },
      orderBy: desc(posts.createdAt),
    });

    let processed = results.map(post => {
      return {
        ...post,
        user: post.isAnonymous ? undefined : post.user,
        likeCount: post.likes.length,
        hasLiked: currentUserId ? post.likes.some(l => l.userId === currentUserId) : false,
      };
    });

    if (filters?.sort === 'top' || filters?.trending) {
      processed.sort((a, b) => b.likeCount - a.likeCount);
    }

    if (filters?.trending) {
      return processed.slice(0, 20) as PostWithDetails[];
    }

    return processed as PostWithDetails[];
  }

  async getPost(id: number, currentUserId?: number): Promise<PostWithDetails | undefined> {
    const post = await db.query.posts.findFirst({
      where: eq(posts.id, id),
      with: {
        user: true,
        likes: true,
        comments: {
          with: { user: true },
          orderBy: desc(comments.createdAt)
        }
      }
    });

    if (!post) return undefined;

    return {
      ...post,
      user: post.isAnonymous ? undefined : post.user,
      likeCount: post.likes.length,
      hasLiked: currentUserId ? post.likes.some(l => l.userId === currentUserId) : false,
    };
  }

  async deletePost(id: number): Promise<void> {
    await db.delete(likes).where(eq(likes.postId, id));
    await db.delete(comments).where(eq(comments.postId, id));
    await db.delete(reports).where(eq(reports.postId, id));
    await db.delete(posts).where(eq(posts.id, id));
  }

  async createComment(comment: InsertComment): Promise<Comment> {
    const [newComment] = await db.insert(comments).values(comment).returning();
    return newComment;
  }

  async toggleLike(postId: number, userId: number): Promise<{ likes: number; hasLiked: boolean }> {
    const existingLike = await db.select().from(likes).where(
      and(eq(likes.postId, postId), eq(likes.userId, userId))
    );

    if (existingLike.length > 0) {
      await db.delete(likes).where(
        and(eq(likes.postId, postId), eq(likes.userId, userId))
      );
    } else {
      await db.insert(likes).values({ postId, userId });
    }

    const allLikes = await db.select().from(likes).where(eq(likes.postId, postId));
    return {
      likes: allLikes.length,
      hasLiked: existingLike.length === 0
    };
  }

  async createReport(report: InsertReport): Promise<Report> {
    const [newReport] = await db.insert(reports).values(report).returning();
    return newReport;
  }

  async getReports(): Promise<(Report & { post: Post; user: User })[]> {
    return await db.query.reports.findMany({
      with: {
        post: true,
        user: true
      }
    });
  }

  async deleteReport(id: number): Promise<void> {
    await db.delete(reports).where(eq(reports.id, id));
  }

  async createEvent(event: InsertEvent): Promise<Event> {
    const [newEvent] = await db.insert(events).values(event).returning();
    return newEvent;
  }

  async getEvents(): Promise<Event[]> {
    return await db.select().from(events).orderBy(desc(events.date));
  }

  async deleteEvent(id: number): Promise<void> {
    await db.delete(events).where(eq(events.id, id));
  }

  async searchUsers(query: string): Promise<User[]> {
    if (!query.trim()) return [];
    const search = `%${query}%`;
    return await db.select({
      id: users.id,
      username: users.username,
      name: users.name,
      bio: users.bio,
      profileEmoji: users.profileEmoji,
    }).from(users).where(
      or(
        ilike(users.username, search),
        ilike(users.name, search)
      )
    ).limit(10) as User[];
  }

  // Messages
  async createMessage(message: InsertMessage): Promise<Message> {
    const [newMessage] = await db.insert(messages).values(message).returning();
    
    // Cleanup: Keep only latest 100 messages per conversation
    await this.cleanupConversationMessages(message.senderId, message.receiverId, 100);
    
    return newMessage;
  }

  async cleanupConversationMessages(userId1: number, userId2: number, maxCount: number = 100): Promise<number> {
    // Get only messages beyond the limit (offset by maxCount)
    const oldMessages = await db.select({ id: messages.id })
      .from(messages)
      .where(
        or(
          and(eq(messages.senderId, userId1), eq(messages.receiverId, userId2)),
          and(eq(messages.senderId, userId2), eq(messages.receiverId, userId1))
        )
      )
      .orderBy(desc(messages.createdAt))
      .offset(maxCount);
    
    if (oldMessages.length === 0) return 0;
    
    // Batch delete using inArray
    const idsToDelete = oldMessages.map(m => m.id);
    await db.delete(messages).where(inArray(messages.id, idsToDelete));
    return idsToDelete.length;
  }

  async getMessages(userId: number): Promise<(Message & { sender: User })[]> {
    return await db.query.messages.findMany({
      where: eq(messages.receiverId, userId),
      with: { sender: true },
      orderBy: desc(messages.createdAt)
    }) as (Message & { sender: User })[];
  }

  async getConversation(userId1: number, userId2: number): Promise<Message[]> {
    return await db.select().from(messages).where(
      or(
        and(eq(messages.senderId, userId1), eq(messages.receiverId, userId2)),
        and(eq(messages.senderId, userId2), eq(messages.receiverId, userId1))
      )
    ).orderBy(messages.createdAt);
  }

  async markMessageRead(id: number): Promise<void> {
    await db.update(messages).set({ isRead: true }).where(eq(messages.id, id));
  }

  async markConversationRead(userId: number, senderId: number): Promise<void> {
    await db.update(messages).set({ isRead: true }).where(
      and(
        eq(messages.senderId, senderId),
        eq(messages.receiverId, userId),
        eq(messages.isRead, false)
      )
    );
  }

  async getUnreadMessageCount(userId: number): Promise<number> {
    const unread = await db.select().from(messages).where(
      and(
        eq(messages.receiverId, userId),
        eq(messages.isRead, false)
      )
    );
    return unread.length;
  }

  // Follows
  async toggleFollow(followerId: number, followingId: number): Promise<{ isFollowing: boolean }> {
    const existing = await db.select().from(follows).where(
      and(eq(follows.followerId, followerId), eq(follows.followingId, followingId))
    );

    if (existing.length > 0) {
      await db.delete(follows).where(
        and(eq(follows.followerId, followerId), eq(follows.followingId, followingId))
      );
      return { isFollowing: false };
    } else {
      await db.insert(follows).values({ followerId, followingId });
      return { isFollowing: true };
    }
  }

  async getFollowers(userId: number): Promise<User[]> {
    const result = await db.query.follows.findMany({
      where: eq(follows.followingId, userId),
      with: { follower: true }
    });
    return result.map(f => f.follower);
  }

  async getFollowing(userId: number): Promise<User[]> {
    const result = await db.query.follows.findMany({
      where: eq(follows.followerId, userId),
      with: { following: true }
    });
    return result.map(f => f.following);
  }

  async isFollowing(followerId: number, followingId: number): Promise<boolean> {
    const result = await db.select().from(follows).where(
      and(eq(follows.followerId, followerId), eq(follows.followingId, followingId))
    );
    return result.length > 0;
  }

  async getFollowCounts(userId: number): Promise<{ followers: number; following: number }> {
    const followers = await db.select().from(follows).where(eq(follows.followingId, userId));
    const following = await db.select().from(follows).where(eq(follows.followerId, userId));
    return { followers: followers.length, following: following.length };
  }

  // Ads
  async createAd(ad: InsertAd): Promise<Ad> {
    const [newAd] = await db.insert(ads).values(ad).returning();
    return newAd;
  }

  async getActiveAds(): Promise<Ad[]> {
    return await db.select().from(ads).where(eq(ads.isActive, true));
  }

  async deleteAd(id: number): Promise<void> {
    await db.delete(ads).where(eq(ads.id, id));
  }

  async toggleAdActive(id: number): Promise<Ad> {
    const [ad] = await db.select().from(ads).where(eq(ads.id, id));
    const [updated] = await db.update(ads).set({ isActive: !ad.isActive }).where(eq(ads.id, id)).returning();
    return updated;
  }

  // Community Chat
  async createCommunityMessage(message: InsertCommunityMessage): Promise<CommunityMessage> {
    const [newMessage] = await db.insert(communityMessages).values(message).returning();
    
    // Cleanup: Keep only latest 150 messages
    await this.cleanupCommunityMessages(150);
    
    return newMessage;
  }

  async getCommunityMessages(limit: number = 100): Promise<(CommunityMessage & { user: User })[]> {
    return await db.query.communityMessages.findMany({
      with: { user: true },
      orderBy: desc(communityMessages.createdAt),
      limit
    }) as (CommunityMessage & { user: User })[];
  }

  async cleanupCommunityMessages(maxCount: number = 150): Promise<number> {
    // Get only messages beyond the limit (offset by maxCount)
    const oldMessages = await db.select({ id: communityMessages.id })
      .from(communityMessages)
      .orderBy(desc(communityMessages.createdAt))
      .offset(maxCount);
    
    if (oldMessages.length === 0) return 0;
    
    // Batch delete using inArray
    const idsToDelete = oldMessages.map(m => m.id);
    await db.delete(communityMessages).where(inArray(communityMessages.id, idsToDelete));
    return idsToDelete.length;
  }

  // Auto-cleanup: Archive and delete posts older than 24 hours (batch operation)
  async archiveAndDeleteOldPosts(): Promise<number> {
    const cutoffTime = new Date(Date.now() - 24 * 60 * 60 * 1000);
    
    // Get old posts
    const oldPosts = await db.select().from(posts).where(lt(posts.createdAt, cutoffTime));
    
    if (oldPosts.length === 0) return 0;
    
    // Get post IDs for batch operations
    const postIds = oldPosts.map(p => p.id);
    
    // Batch archive all posts
    await db.insert(archivedPosts).values(
      oldPosts.map(post => ({
        originalId: post.id,
        type: post.type,
        category: post.category,
        userId: post.userId,
        isAnonymous: post.isAnonymous,
        caption: post.caption,
        title: post.title,
        subject: post.subject,
        fileUrl: post.fileUrl,
        fileType: post.fileType,
        originalCreatedAt: post.createdAt,
      }))
    );
    
    // Batch delete associated data
    for (const postId of postIds) {
      await db.delete(likes).where(eq(likes.postId, postId));
      await db.delete(comments).where(eq(comments.postId, postId));
      await db.delete(reports).where(eq(reports.postId, postId));
    }
    
    // Delete old posts in batch
    await db.delete(posts).where(lt(posts.createdAt, cutoffTime));
    
    return oldPosts.length;
  }

  // Auto-cleanup: Archive and delete messages older than 24 hours (batch operation)
  async archiveAndDeleteOldMessages(): Promise<number> {
    const cutoffTime = new Date(Date.now() - 24 * 60 * 60 * 1000);
    
    // Get old messages (excluding warnings which should persist)
    const oldMessages = await db.select().from(messages).where(
      and(
        lt(messages.createdAt, cutoffTime),
        ne(messages.type, "warning")
      )
    );
    
    if (oldMessages.length === 0) return 0;
    
    // Batch archive all messages
    await db.insert(archivedMessages).values(
      oldMessages.map(msg => ({
        originalId: msg.id,
        senderId: msg.senderId,
        receiverId: msg.receiverId,
        content: msg.content,
        type: msg.type,
        originalCreatedAt: msg.createdAt,
      }))
    );
    
    // Delete old messages in batch (except warnings)
    await db.delete(messages).where(
      and(
        lt(messages.createdAt, cutoffTime),
        ne(messages.type, "warning")
      )
    );
    
    return oldMessages.length;
  }

  // Visitor tracking
  async createVisitor(visitor: InsertVisitor): Promise<Visitor> {
    const [newVisitor] = await db.insert(visitors).values(visitor).returning();
    return newVisitor;
  }

  async getVisitors(limit: number = 100): Promise<Visitor[]> {
    return await db.select().from(visitors)
      .orderBy(desc(visitors.createdAt))
      .limit(limit) as Visitor[];
  }

  async getRecentUnknownVisitors(limit: number = 50): Promise<Visitor[]> {
    return await db.select().from(visitors)
      .where(eq(visitors.isAuthenticated, false))
      .orderBy(desc(visitors.createdAt))
      .limit(limit) as Visitor[];
  }

  // Premium subscription
  async toggleUserPremium(userId: number, isPremium: boolean): Promise<User | undefined> {
    const [updated] = await db.update(users)
      .set({ isPremium })
      .where(eq(users.id, userId))
      .returning();
    return updated;
  }

  // System settings
  async getSystemSetting(key: string): Promise<string | null> {
    const setting = await db.select().from(systemSettings)
      .where(eq(systemSettings.key, key))
      .limit(1);
    return setting[0]?.value || null;
  }

  async setSystemSetting(key: string, value: string): Promise<SystemSetting> {
    const existing = await this.getSystemSetting(key);
    if (existing !== null) {
      const [updated] = await db.update(systemSettings)
        .set({ value, updatedAt: new Date() })
        .where(eq(systemSettings.key, key))
        .returning();
      return updated;
    } else {
      const [created] = await db.insert(systemSettings)
        .values({ key, value })
        .returning();
      return created;
    }
  }

  // Emergency logout
  async triggerEmergencyLogout(): Promise<void> {
    await this.setSystemSetting('emergency_logout', new Date().toISOString());
  }

  async getEmergencyLogoutTime(): Promise<Date | null> {
    const value = await this.getSystemSetting('emergency_logout');
    return value ? new Date(value) : null;
  }

  async clearEmergencyLogout(): Promise<void> {
    await db.delete(systemSettings).where(eq(systemSettings.key, 'emergency_logout'));
  }

  // College users management
  async getCollegeUsers(): Promise<CollegeUser[]> {
    return await db.select().from(collegeUsers).orderBy(desc(collegeUsers.createdAt)) as CollegeUser[];
  }

  async getCollegeUserByUsername(username: string): Promise<CollegeUser | undefined> {
    const [user] = await db.select().from(collegeUsers)
      .where(eq(collegeUsers.username, username));
    return user;
  }

  async createCollegeUser(user: InsertCollegeUser): Promise<CollegeUser> {
    const [created] = await db.insert(collegeUsers).values(user).returning();
    return created;
  }

  async deleteCollegeUser(id: number): Promise<void> {
    await db.delete(collegeUsers).where(eq(collegeUsers.id, id));
  }

  // Pending user registrations
  async getPendingUsers(): Promise<PendingUser[]> {
    return await db.select().from(pendingUsers)
      .where(eq(pendingUsers.status, "pending"))
      .orderBy(desc(pendingUsers.createdAt)) as PendingUser[];
  }

  async getPendingUserByUsername(username: string): Promise<PendingUser | undefined> {
    const [user] = await db.select().from(pendingUsers)
      .where(eq(pendingUsers.username, username));
    return user;
  }

  async createPendingUser(user: InsertPendingUser): Promise<PendingUser> {
    const [created] = await db.insert(pendingUsers).values(user).returning();
    return created;
  }

  async approvePendingUser(id: number): Promise<User> {
    const [pending] = await db.select().from(pendingUsers)
      .where(eq(pendingUsers.id, id));
    
    if (!pending) throw new Error("Pending user not found");

    // Create actual user
    const [user] = await db.insert(users).values({
      username: pending.username,
      password: pending.password,
      email: pending.email,
      phone: pending.phone,
      acceptedPrivacyPolicy: pending.acceptedPrivacyPolicy,
    }).returning();

    // Update pending status
    await db.update(pendingUsers)
      .set({ status: "approved" })
      .where(eq(pendingUsers.id, id));

    return user;
  }

  async rejectPendingUser(id: number): Promise<void> {
    await db.update(pendingUsers)
      .set({ status: "rejected" })
      .where(eq(pendingUsers.id, id));
  }

  async deletePendingUser(id: number): Promise<void> {
    await db.delete(pendingUsers).where(eq(pendingUsers.id, id));
  }
}

export const storage = new DatabaseStorage();
