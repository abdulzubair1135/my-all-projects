import { storage } from "./storage";
import bcrypt from "bcryptjs";

async function seed() {
  console.log("Seeding database...");

  // Check if data exists
  const existingUser = await storage.getUserByUsername("admin");
  if (existingUser) {
    console.log("Database already seeded.");
    return;
  }

  // Create Users
  const password = await bcrypt.hash("password123", 10);
  const adminPassword = await bcrypt.hash(process.env.SUPER_ADMIN_PASSWORD || "admin123", 10);

  const admin = await storage.createUser({
    username: "admin",
    password: adminPassword,
    name: "Admin User",
    bio: "Campus Administrator",
    email: "admin@college.edu",
    phone: "1234567890",
    role: "admin"
  });

  const alice = await storage.createUser({
    username: "alice",
    password,
    name: "Alice Student",
    bio: "CS Major | 2026",
    email: "alice@college.edu",
    phone: "0987654321",
    role: "user"
  });

  const bob = await storage.createUser({
    username: "bob",
    password,
    name: "Bob Builder",
    bio: "Architecture | 2025",
    email: "bob@college.edu",
    phone: "1122334455",
    role: "user"
  });

  console.log("Users created");

  // Create Posts
  
  // 1. Normal Post
  await storage.createPost({
    type: "normal",
    category: "general",
    userId: alice.id,
    caption: "Just finished my final project! #cs #life",
    isAnonymous: false,
  });

  // 2. Notes
  await storage.createPost({
    type: "notes",
    category: "notes",
    userId: alice.id,
    title: "Data Structures Cheatsheet",
    subject: "CS 201",
    caption: "Here is a quick summary of Trees and Graphs.",
    isAnonymous: false,
    fileType: "application/pdf"
  });

  // 3. Confession (Anonymous)
  await storage.createPost({
    type: "confession",
    category: "confession",
    userId: bob.id,
    caption: "I have a crush on the girl who sits in the front row of Calc II. Should I talk to her?",
    isAnonymous: true,
  });

  // 4. Trending Meme
  const meme = await storage.createPost({
    type: "normal",
    category: "memes",
    userId: bob.id,
    caption: "When the professor says 'it's trivial'...",
    isAnonymous: false,
  });

  // Add interactions
  await storage.toggleLike(meme.id, alice.id);
  await storage.toggleLike(meme.id, admin.id);
  
  await storage.createComment({
    postId: meme.id,
    userId: alice.id,
    text: "So true! 😂"
  });

  console.log("Seeding complete!");
  process.exit(0);
}

seed().catch((err) => {
  console.error("Seeding failed:", err);
  process.exit(1);
});
