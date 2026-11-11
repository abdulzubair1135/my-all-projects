const User = require('../models/userModel');

const authController = {
    loginPage: (req, res) => {
        res.sendFile('login.html', { root: './public' });
    },

    login: async (req, res) => {
        try {
            const { email, password } = req.body;
            const user = await User.findByEmail(email);

            if (!user || user.password !== password) {
                return res.status(401).json({ success: false, message: 'Invalid email or password' });
            }

            req.session.userId = user.id;
            req.session.userName = user.name;
            req.session.userState = user.state;

            res.json({ success: true, message: 'Login successful' });
        } catch (err) {
            res.status(500).json({ success: false, message: err.message });
        }
    },

    logout: (req, res) => {
        req.session.destroy(() => {
            res.redirect('/login.html');
        });
    },

    getSessionUser: (req, res) => {
        if (!req.session.userId) {
            return res.status(401).json({ loggedIn: false });
        }
        res.json({ loggedIn: true, name: req.session.userName, state: req.session.userState });
    }
};

module.exports = authController;
