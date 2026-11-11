const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(cors({ origin: '*', credentials: true }));

const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
app.use('/uploads', express.static(uploadDir));

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    filename: (req, file, cb) => {
        const unique = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, unique + path.extname(file.originalname));
    }
});

const upload = multer({
    storage,
    limits: { fileSize: 5 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        const allowed = /jpeg|jpg|png|gif|webp/;
        const ext = path.extname(file.originalname).toLowerCase();
        if (allowed.test(ext) && allowed.test(file.mimetype)) cb(null, true);
        else cb(new Error('Images only'));
    }
});

const postsFile = path.join(__dirname, 'posts.json');
const studentsFile = path.join(__dirname, 'students.json');
const bansFile = path.join(__dirname, 'bans.json');

const loadJSON = (file, def = []) => {
    if (!fs.existsSync(file)) saveJSON(file, def);
    try {
        const data = fs.readFileSync(file, 'utf8').trim();
        return data ? JSON.parse(data) : def;
    } catch { return def; }
};

const saveJSON = (file, data) => {
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
};

let posts = loadJSON(postsFile);
let students = loadJSON(studentsFile);
let bans = loadJSON(bansFile);

const SUPER_ADMIN_UID = 'COL00000';

setInterval(() => {
    const now = Date.now();
    const oldCount = posts.length;
    posts = posts.filter(p => now - new Date(p.createdAt) < 24 * 60 * 60 * 1000);
    if (posts.length !== oldCount) saveJSON(postsFile, posts);
}, 3600000);

const verifyToken = (req, res, next) => {
    const header = req.headers.authorization;
    if (!header || !header.startsWith('Bearer ')) return res.status(401).json({ error: 'Token required' });

    const token = header.split(' ')[1];
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = students.find(s => s.id === decoded.id);
        if (!user) return res.status(404).json({ error: 'User not found' });
        req.user = user;
        req.isAdmin = user.uid === SUPER_ADMIN_UID || user.isAdmin === true;
        next();
    } catch {
        return res.status(401).json({ error: 'Invalid token' });
    }
};

const checkBan = (req, res, next) => {
    const ban = bans.find(b => b.userId === req.user.id && new Date(b.until) > new Date());
    if (ban) return res.status(403).json({ error: `Banned until ${new Date(b.until).toLocaleString()}` });
    next();
};

app.get('/api/test', (req, res) => res.json({ message: 'Backend LIVE', users: students.length, posts: posts.length }));

app.post('/api/register', async (req, res) => {
    const { uid, name = uid, phone, email, password } = req.body;
    if (!uid || !phone || !email || !password) return res.status(400).json({ error: 'All fields required' });
    if (students.find(s => s.uid === uid)) return res.status(400).json({ error: 'UID taken' });
    if (students.find(s => s.email === email.toLowerCase())) return res.status(400).json({ error: 'Email registered' });

    const hashed = await bcrypt.hash(password, 12);
    const newUser = {
        id: Date.now(),
        uid: uid.trim(),
        name: name.trim(),
        phone: phone.trim(),
        email: email.toLowerCase().trim(),
        password: hashed,
        isAdmin: uid === SUPER_ADMIN_UID,
        createdAt: new Date().toISOString()
    };

    students.push(newUser);
    saveJSON(studentsFile, students);
    const token = jwt.sign({ id: newUser.id }, process.env.JWT_SECRET, { expiresIn: '24h' });
    const { password: _, ...safe } = newUser;
    res.status(201).json({ message: 'Registered', token, user: safe });
});

app.post('/api/login', async (req, res) => {
    const { uid, password } = req.body;
    const user = students.find(s => s.uid === uid);
    if (!user || !(await bcrypt.compare(password, user.password))) return res.status(400).json({ error: 'Invalid UID/password' });

    const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET, { expiresIn: '24h' });
    const { password: _, ...safe } = user;
    res.json({ message: 'Login success', token, user: safe });
});

app.get('/api/profile', verifyToken, (req, res) => {
    const { password, ...safe } = req.user;
    res.json({ ...safe, isAdmin: req.isAdmin });
});

app.get('/api/posts', verifyToken, checkBan, (req, res) => {
    const sorted = [...posts].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    res.json(sorted);
});

app.post('/api/posts', verifyToken, checkBan, upload.single('image'), (req, res) => {
    const { content = '', category = 'all' } = req.body;
    const image = req.file ? `/uploads/${req.file.filename}` : null;

    const newPost = {
        id: Date.now(),
        uid: req.user.uid,
        userDisplayName: req.user.name,
        content: content.substring(0, 1000),
        image,
        category,
        likes: 0,
        likedBy: [],
        comments: [],
        createdAt: new Date().toISOString()
    };

    posts.unshift(newPost);
    saveJSON(postsFile, posts);
    res.status(201).json({ message: 'Posted', post: newPost });
});

app.put('/api/posts/:id/like', verifyToken, checkBan, (req, res) => {
    const post = posts.find(p => p.id === parseInt(req.params.id));
    if (!post) return res.status(404).json({ error: 'Post not found' });

    const idx = post.likedBy.indexOf(req.user.id);
    if (idx > -1) {
        post.likedBy.splice(idx, 1);
        post.likes--;
    } else {
        post.likedBy.push(req.user.id);
        post.likes++;
    }
    saveJSON(postsFile, posts);
    res.json({ likes: post.likes });
});

app.post('/api/posts/:id/comment', verifyToken, checkBan, (req, res) => {
    const post = posts.find(p => p.id === parseInt(req.params.id));
    if (!post) return res.status(404).json({ error: 'Post not found' });
    const { text } = req.body;
    if (!text?.trim()) return res.status(400).json({ error: 'Comment required' });

    const comment = {
        id: Date.now(),
        uid: req.user.uid,
        userDisplayName: req.user.name,
        text: text.substring(0, 300),
        date: new Date().toISOString()
    };
    post.comments.unshift(comment);
    saveJSON(postsFile, posts);
    res.json({ comment });
});

app.delete('/api/posts/:id', verifyToken, (req, res) => {
    const idx = posts.findIndex(p => p.id === parseInt(req.params.id));
    if (idx === -1) return res.status(404).json({ error: 'Post not found' });

    const post = posts[idx];
    const isOwner = post.uid === req.user.uid;
    if (!isOwner && !req.isAdmin) return res.status(403).json({ error: 'Not authorized' });

    if (post.image) {
        const filePath = path.join(__dirname, post.image);
        if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    }

    posts.splice(idx, 1);
    saveJSON(postsFile, posts);
    res.json({ message: 'Deleted' });
});

app.post('/api/ban', verifyToken, (req, res) => {
    if (!req.isAdmin) return res.status(403).json({ error: 'Admin only' });
    const { userId, duration = '1d' } = req.body;
    const hours = duration === '2h' ? 2 : duration === '3h' ? 3 : duration === '1d' ? 24 : 720;
    const until = new Date(Date.now() + hours * 3600000);

    bans = bans.filter(b => b.userId !== parseInt(userId));
    bans.push({ userId: parseInt(userId), until: until.toISOString() });
    saveJSON(bansFile, bans);
    res.json({ message: 'Banned' });
});

app.get('/api/search', verifyToken, (req, res) => {
    const q = (req.query.q || '').toLowerCase().trim();
    if (q.length < 2) return res.json({ users: [], posts: [] });

    const userResults = students.filter(s => s.uid.toLowerCase().includes(q) || s.name.toLowerCase().includes(q));
    const postResults = posts.filter(p => p.content.toLowerCase().includes(q) || p.uid.toLowerCase().includes(q));

    res.json({ users: userResults.map(({ password, ...u }) => u), posts: postResults });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`COLLEGE FACE BACKEND RUNNING ON http://localhost:${PORT}`);
    console.log(`Super Admin UID: ${SUPER_ADMIN_UID}`);
});