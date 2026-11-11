const express = require('express');
const session = require('express-session');
const path = require('path');
const webRoutes = require('./routes/webRoutes');

const app = express();

// Middleware setup
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
    secret: 'gst_secret_key_secure_123',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false }
}));

// Static Frontend Routing
app.use(express.static(path.join(__dirname, 'public')));

// MVC Web Routes
app.use('/', webRoutes);

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server is running smoothly on http://localhost:${PORT}`);
});
