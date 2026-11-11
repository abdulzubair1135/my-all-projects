import passport from "passport";
import { Strategy as LocalStrategy } from "passport-local";
import { Express } from "express";
import session from "express-session";
import { scrypt, randomBytes, timingSafeEqual } from "crypto";
import { promisify } from "util";
import { storage } from "./storage";
import { User } from "@shared/schema";
import bcrypt from "bcryptjs"; // User specifically asked for bcrypt

export function setupAuth(app: Express) {
  const sessionSettings: session.SessionOptions = {
    secret: process.env.SESSION_SECRET || "college_face_super_secret",
    resave: false,
    saveUninitialized: false,
    store: session.MemoryStore(),
    cookie: {
      secure: app.get("env") === "production",
    }
  };

  app.set("trust proxy", 1);
  app.use(session(sessionSettings));
  app.use(passport.initialize());
  app.use(passport.session());

  passport.use(
    new LocalStrategy(async (username, password, done) => {
      try {
        const user = await storage.getUserByUsername(username);
        if (!user) {
          return done(null, false, { message: "Incorrect username." });
        }

        const isValid = await bcrypt.compare(password, user.password);
        if (!isValid) {
          return done(null, false, { message: "Incorrect password." });
        }

        return done(null, user);
      } catch (err) {
        return done(err);
      }
    }),
  );

  passport.serializeUser((user, done) => {
    done(null, (user as User).id);
  });

  passport.deserializeUser(async (id: number, done) => {
    try {
      const user = await storage.getUser(id);
      done(null, user);
    } catch (err) {
      done(err);
    }
  });

  app.post("/api/auth/register", async (req, res, next) => {
    try {
      const { username, password, name, bio, email, phone, acceptedPrivacyPolicy } = req.body;
      
      // Check if user already exists
      const existingUser = await storage.getUserByUsername(username);
      if (existingUser) {
        return res.status(400).json({ message: "Username already exists" });
      }

      // Check if username is in authorized college users list
      const collegeUser = await storage.getCollegeUserByUsername(username);
      if (!collegeUser) {
        return res.status(403).json({ 
          message: "Not authorized - check your account. Your username is not in our college database.",
          code: "NOT_COLLEGE_USER"
        });
      }

      // Check if already has pending registration
      const pendingUser = await storage.getPendingUserByUsername(username);
      if (pendingUser) {
        if (pendingUser.status === "pending") {
          return res.status(400).json({ 
            message: "Your registration is pending admin approval. Please wait.",
            code: "PENDING_APPROVAL"
          });
        } else if (pendingUser.status === "rejected") {
          return res.status(403).json({ 
            message: "Your registration was rejected. Please contact admin.",
            code: "REGISTRATION_REJECTED"
          });
        }
      }

      // Create pending user for admin approval
      const hashedPassword = await bcrypt.hash(password, 10);
      await storage.createPendingUser({
        username,
        password: hashedPassword,
        email: email || null,
        phone: phone || null,
        acceptedPrivacyPolicy: acceptedPrivacyPolicy || false,
        status: "pending"
      });

      return res.status(202).json({ 
        message: "Registration submitted! Please wait for admin approval.",
        code: "PENDING_APPROVAL"
      });
    } catch (err) {
      next(err);
    }
  });

  app.post("/api/auth/login", (req, res, next) => {
    passport.authenticate("local", (err, user, info) => {
      if (err) return next(err);
      if (!user) return res.status(401).send(info?.message || "Login failed");
      
      req.login(user, (err) => {
        if (err) return next(err);
        return res.status(200).json({ id: user.id, username: user.username });
      });
    })(req, res, next);
  });

  app.post("/api/auth/logout", (req, res, next) => {
    req.logout((err) => {
      if (err) return next(err);
      res.sendStatus(200);
    });
  });

  app.get("/api/user", (req, res) => {
    if (!req.isAuthenticated()) return res.sendStatus(401);
    res.json(req.user);
  });
}
