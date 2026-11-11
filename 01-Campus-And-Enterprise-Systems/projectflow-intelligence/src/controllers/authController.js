const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const { store, supabase } = require('../supabase');
const { JWT_SECRET } = require('../middleware/authMiddleware');
const { recordAuditLog } = require('../middleware/auditLogger');

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const CREDENTIALS_FILE = path.join(__dirname, '../../database/user_credentials.json');

const defaultCredentials = {
  'admin@projectflow.io': 'ProjectFlow@2026',
  'manager@projectflow.io': 'ProjectFlow@2026',
  'abdulzubair221@gmail.com': 'ProjectFlow@2026',
  'vipra@projectflow.io': 'ProjectFlow@2026',
  'boyundertheaim@gmail.com': 'ProjectFlow@2026',
  'lalwanipuneet91@gmail.com': 'ProjectFlow@2026'
};

function loadCredentials() {
  try {
    if (fs.existsSync(CREDENTIALS_FILE)) {
      const data = fs.readFileSync(CREDENTIALS_FILE, 'utf8');
      return { ...defaultCredentials, ...JSON.parse(data) };
    }
  } catch (e) {
    console.warn('[AUTH] Error reading user_credentials.json:', e.message);
  }
  return { ...defaultCredentials };
}

function saveCredentials(credentials) {
  try {
    const dir = path.dirname(CREDENTIALS_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CREDENTIALS_FILE, JSON.stringify(credentials, null, 2), 'utf8');
  } catch (e) {
    console.warn('[AUTH] Error writing user_credentials.json:', e.message);
  }
}

store.userPasswords = loadCredentials();

function verifyPassword(email, inputPassword) {
  if (!inputPassword) return false;
  const normalizedEmail = (email || '').trim().toLowerCase();

  // 1. Check in persistent store.userPasswords
  const registeredPassword = store.userPasswords[normalizedEmail];
  if (registeredPassword) {
    if (Array.isArray(registeredPassword)) {
      return registeredPassword.includes(inputPassword);
    }
    return registeredPassword === inputPassword;
  }

  // 2. Check if user object in store has password
  const user = store.users.find(u => u.email.toLowerCase() === normalizedEmail);
  if (user && user.password) {
    return user.password === inputPassword;
  }

  // Strict: DO NOT allow unverified accounts to log in
  return false;
}

async function login(req, res) {
  const email = (req.body && req.body.email) ? req.body.email.trim().toLowerCase() : '';
  const password = req.body && req.body.password ? req.body.password : '';

  if (!email) {
    return res.status(400).json({ error: 'Email address is required' });
  }

  if (!password) {
    return res.status(400).json({ error: 'Password is required' });
  }

  // Always reload credentials to catch recent signups
  store.userPasswords = loadCredentials();

  const existingUser = store.users.find(u => u.email.toLowerCase() === email);
  const hasRegisteredPassword = Boolean(store.userPasswords && store.userPasswords[email]);

  // 1. Attempt Supabase Auth if connected
  let authSuccess = false;
  let authUser = null;
  if (supabase && password) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (!error && data && data.user) {
        authUser = data.user;
        authSuccess = true;
      }
    } catch (e) {
      console.warn('[AUTH] Supabase signIn fallback:', e.message);
    }
  }

  // USER DIRECTIVE: Agar email ne sign up nahi kiya hai to login bilkul nahi karne dena
  if (!existingUser && !hasRegisteredPassword && !authSuccess) {
    return res.status(404).json({ error: 'No account found with this email. Please sign up first.' });
  }

  // USER DIRECTIVE: Jo password signup me dala hai wahi password verify karna hai
  if (!authSuccess) {
    const isPasswordValid = verifyPassword(email, password);
    if (!isPasswordValid) {
      return res.status(401).json({ error: 'Incorrect password. Please enter the password you created during sign-up.' });
    }
  }

  // 3. User is authorized
  let user = existingUser;
  if (!user && authUser) {
    const role = email.includes('admin') ? 'ADMINISTRATOR' : (email.includes('manager') ? 'MANAGER' : 'MEMBER');
    const defaultName = email.split('@')[0];
    const formattedName = defaultName.charAt(0).toUpperCase() + defaultName.slice(1);
    user = {
      id: authUser.id,
      email,
      fullName: (authUser.user_metadata && authUser.user_metadata.full_name) || formattedName,
      role,
      active: true,
      createdAt: new Date().toISOString()
    };
    store.users.push(user);
  }

  if (!user) {
    const role = email.includes('admin') ? 'ADMINISTRATOR' : (email.includes('manager') ? 'MANAGER' : 'MEMBER');
    const defaultName = email.split('@')[0];
    const formattedName = defaultName.charAt(0).toUpperCase() + defaultName.slice(1);
    user = {
      id: uuidv4(),
      email,
      fullName: formattedName,
      role,
      active: true,
      createdAt: new Date().toISOString()
    };
    store.users.push(user);
  }

  // 4. Mark active session
  store.activeSessions[email] = Date.now();

  // 5. Generate JWT
  const token = jwt.sign(
    { userId: user.id, email: user.email, role: user.role, fullName: user.fullName },
    JWT_SECRET,
    { expiresIn: '30d' }
  );

  recordAuditLog('USER_LOGGED_IN', 'USER', user.id, user.email, { ip: req.ip, role: user.role });
  res.json({ token, user, message: 'Authentication successful' });
}

async function signup(req, res) {
  const email = (req.body && req.body.email) ? req.body.email.trim().toLowerCase() : '';
  const password = req.body && req.body.password ? req.body.password : '';
  const fullName = (req.body && req.body.fullName) ? req.body.fullName.trim() : (email ? email.split('@')[0] : 'Team Member');

  if (!email) {
    return res.status(400).json({ error: 'Email address is required' });
  }

  if (!password || password.length < 6) {
    return res.status(400).json({ error: 'Password must be at least 6 characters long' });
  }

  // Check if account already exists
  store.userPasswords = loadCredentials();
  const existingUser = store.users.find(u => u.email.toLowerCase() === email);
  if (existingUser && store.userPasswords[email]) {
    return res.status(409).json({ error: 'An account with this email already exists. Please log in.' });
  }

  // Register password in persistent credential store
  store.userPasswords[email] = password;
  saveCredentials(store.userPasswords);

  let userId = uuidv4();

  // 1. Create in Supabase Auth if connected
  if (supabase && password) {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { full_name: fullName } }
      });
      if (!error && data && data.user) {
        userId = data.user.id;
      }
    } catch (e) {
      console.warn('[AUTH] Supabase signUp warning:', e.message);
    }
  }

  const role = email.includes('admin') ? 'ADMINISTRATOR' : 'MEMBER';
  const user = {
    id: userId,
    email,
    fullName,
    role,
    password,
    active: true,
    createdAt: new Date().toISOString()
  };

  const existingIdx = store.users.findIndex(u => u.email.toLowerCase() === email);
  if (existingIdx >= 0) {
    store.users[existingIdx] = user;
  } else {
    store.users.push(user);
  }

  // 2. Persist to Supabase profiles
  if (supabase) {
    try {
      await supabase.from('profiles').upsert({
        id: user.id,
        email: user.email,
        full_name: user.fullName,
        role: user.role,
        active: true,
        created_at: user.createdAt
      });
    } catch (e) {
      console.warn('[AUTH] Supabase profile upsert warning:', e.message);
    }
  }

  store.activeSessions[email] = Date.now();

  const token = jwt.sign(
    { userId: user.id, email: user.email, role: user.role, fullName: user.fullName },
    JWT_SECRET,
    { expiresIn: '30d' }
  );

  res.status(201).json({ token, user, message: 'Account created successfully' });
}

function devLogin(req, res) {
  const email = (req.body && req.body.email) ? req.body.email.trim().toLowerCase() : 'admin@projectflow.io';
  let role = 'MEMBER';
  let fullName = 'Team Member';
  let token = 'dev-member-token';

  if (email.includes('admin')) {
    role = 'ADMINISTRATOR';
    fullName = 'System Administrator';
    token = 'dev-admin-token';
  } else if (email.includes('manager')) {
    role = 'MANAGER';
    fullName = 'Project Manager';
    token = 'dev-manager-token';
  }

  let user = store.users.find(u => u.email.toLowerCase() === email);
  if (!user) {
    user = {
      id: uuidv4(),
      email,
      fullName,
      role,
      active: true,
      createdAt: new Date().toISOString()
    };
    store.users.push(user);
  }

  res.json({ token, user });
}

function getMe(req, res) {
  const auth = req.headers.authorization || '';
  let email = req.userEmail || (req.user && req.user.email) || req.headers['x-user-email'];
  if (!email && auth.startsWith('Bearer ')) {
    try {
      const decoded = jwt.decode(auth.substring(7));
      if (decoded && decoded.email) email = decoded.email;
    } catch (e) {}
  }
  if (!email) email = 'admin@projectflow.io';

  const normalized = email.trim().toLowerCase();
  let user = store.users.find(u => u.email.toLowerCase() === normalized);
  if (!user) {
    const isAdm = normalized.includes('admin');
    const isMgr = normalized.includes('manager');
    const defaultName = normalized.split('@')[0];
    user = {
      id: req.user ? req.user.userId : uuidv4(),
      email: normalized,
      fullName: isAdm ? 'System Administrator' : (isMgr ? 'Project Manager' : defaultName.charAt(0).toUpperCase() + defaultName.slice(1)),
      role: isAdm ? 'ADMINISTRATOR' : (isMgr ? 'MANAGER' : 'MEMBER'),
      active: true
    };
    store.users.push(user);
  }
  res.json(user);
}

function updateProfile(req, res) {
  const email = req.userEmail || (req.user && req.user.email) || req.headers['x-user-email'] || 'admin@projectflow.io';
  const user = store.users.find(u => u.email.toLowerCase() === email.toLowerCase()) || store.users[0];
  if (req.body.fullName) user.fullName = req.body.fullName.trim();
  res.json(user);
}

function heartbeat(req, res) {
  const email = req.body.email || req.userEmail || req.headers['x-user-email'] || (req.user && req.user.email);
  if (email) {
    store.activeSessions[email.trim().toLowerCase()] = Date.now();
  }
  res.json({
    success: true,
    online: true,
    status: 'ALIVE',
    timestamp: Date.now(),
    activeCount: Object.keys(store.activeSessions).length
  });
}

async function forgotPassword(req, res) {
  const email = (req.body && req.body.email) ? req.body.email.trim().toLowerCase() : '';
  if (!email) {
    return res.status(400).json({ error: 'Email address is required' });
  }

  store.userPasswords = loadCredentials();
  const existingUser = store.users.find(u => u.email.toLowerCase() === email);
  const hasPassword = Boolean(store.userPasswords[email]);

  if (!existingUser && !hasPassword) {
    return res.status(404).json({ error: 'No account found with this email. Please sign up first.' });
  }

  // Dummy OTP 1234 as required
  console.log(`[AUTH] Forgot password requested for ${email}. OTP generated: 1234`);
  return res.json({
    success: true,
    message: 'Verification code sent. Use OTP: 1234',
    otp: '1234',
    email
  });
}

async function resetPassword(req, res) {
  const email = (req.body && req.body.email) ? req.body.email.trim().toLowerCase() : '';
  const otp = (req.body && (req.body.otp || req.body.code)) ? String(req.body.otp || req.body.code).trim() : '';
  const newPassword = (req.body && (req.body.newPassword || req.body.password)) ? String(req.body.newPassword || req.body.password) : '';

  if (!email) {
    return res.status(400).json({ error: 'Email address is required' });
  }

  if (otp !== '1234') {
    return res.status(400).json({ error: 'Invalid verification code. Please enter OTP 1234.' });
  }

  if (!newPassword || newPassword.length < 6) {
    return res.status(400).json({ error: 'New password must be at least 6 characters long.' });
  }

  store.userPasswords = loadCredentials();
  store.userPasswords[email] = newPassword;
  saveCredentials(store.userPasswords);

  const user = store.users.find(u => u.email.toLowerCase() === email);
  if (user) {
    user.password = newPassword;
  }

  recordAuditLog('PASSWORD_RESET', 'USER', user ? user.id : 'unknown', email, { ip: req.ip });
  console.log(`[AUTH] Password reset successful for ${email}`);

  return res.json({
    success: true,
    message: 'Password has been reset successfully! Please log in with your new password.'
  });
}

module.exports = {
  login,
  signup,
  devLogin,
  getMe,
  updateProfile,
  heartbeat,
  forgotPassword,
  resetPassword
};

