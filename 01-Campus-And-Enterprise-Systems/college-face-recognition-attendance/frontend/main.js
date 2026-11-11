const API_BASE = 'http://localhost:5000/api';
let currentUser = null;
let currentUserId = null;
let isAdmin = false;
let posts = [];
let currentCategory = 'all';

// DOM Cache
const elements = {
    authScreen: document.getElementById('auth-screen'),
    mainScreen: document.getElementById('main-screen'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    loginUid: document.getElementById('login-uid'),
    loginPassword: document.getElementById('login-password'),
    regUid: document.getElementById('reg-uid'),
    regName: document.getElementById('reg-name'),
    regPhone: document.getElementById('reg-phone'),
    regEmail: document.getElementById('reg-email'),
    regPassword: document.getElementById('reg-password'),
    regConfirm: document.getElementById('reg-confirm'),
    termsCheck: document.getElementById('terms-check'),
    userAvatar: document.getElementById('user-avatar'),
    sidebar: document.getElementById('sidebar'),
    sidebarToggle: document.getElementById('sidebar-toggle'),
    postsList: document.getElementById('posts-list'),
    quickPostInput: document.getElementById('quick-post-input'),
    quickImage: document.getElementById('quick-image'),
    fab: document.getElementById('fab'),
    searchInput: document.getElementById('search-input'),
    logoutBtn: document.getElementById('logout-btn'),
    themeToggle: document.querySelector('.theme-toggle')
};

// Toast Notification System
const toast = (message, type = 'info', duration = 4000) => {
    const container = document.getElementById('toast-container') || document.createElement('div');
    if (!document.getElementById('toast-container')) {
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    `;
    container.appendChild(toast);
    toast.querySelector('.toast-close').onclick = () => toast.remove();
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
};

// Password Toggle
document.querySelectorAll('.toggle-password').forEach(toggle => {
    toggle.addEventListener('click', () => {
        const input = toggle.previousElementSibling;
        const icon = toggle.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('fa-eye-slash', 'fa-eye');
        } else {
            input.type = 'password';
            icon.classList.replace('fa-eye', 'fa-eye-slash');
        }
    });
});

// Auth Tab Switching
document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab + '-form').classList.add('active');
    });
});

// Register Handler
elements.registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const uid = elements.regUid.value.trim();
    const name = elements.regName.value.trim();
    const phone = elements.regPhone.value.trim();
    const email = elements.regEmail.value.trim();
    const password = elements.regPassword.value;
    const confirm = elements.regConfirm.value;

    if (!uid || !name || !phone || !email || !password) return toast('All fields are required', 'error');
    if (password !== confirm) return toast('Passwords do not match', 'error');
    if (password.length < 6) return toast('Password must be 6+ characters', 'error');
    if (!elements.termsCheck.checked) return toast('Please accept terms', 'error');

    try {
        const res = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid, name, phone, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.token);
            toast('Account created successfully! 🎉', 'success');
            setTimeout(initApp, 1500);
        } else {
            toast(data.error || 'Registration failed', 'error');
        }
    } catch (err) {
        toast('Server is offline. Start backend!', 'error');
    }
});

// Login Handler
elements.loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const uid = elements.loginUid.value.trim();
    const password = elements.loginPassword.value;

    if (!uid || !password) return toast('Fill all fields', 'error');

    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.token);
            toast('Welcome back! 🚀', 'success');
            setTimeout(initApp, 1500);
        } else {
            toast(data.error || 'Invalid credentials', 'error');
        }
    } catch (err) {
        toast('Backend not running!', 'error');
    }
});

// Initialize App
const initApp = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const res = await fetch(`${API_BASE}/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('Invalid token');

        const user = await res.json();
        currentUser = user;
        currentUserId = user.id;
        isAdmin = user.isAdmin || user.uid === 'COL00000';

        elements.authScreen.classList.add('hidden');
        elements.mainScreen.classList.remove('hidden');
        elements.userAvatar.textContent = user.name.charAt(0).toUpperCase();

        loadPosts();
        setupEventListeners();
    } catch (err) {
        localStorage.removeItem('token');
        toast('Session expired. Login again', 'error');
    }
};

// Load Posts
const loadPosts = async () => {
    try {
        const res = await fetch(`${API_BASE}/posts`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (res.status === 403) {
            const err = await res.json();
            toast(err.error || 'You are banned!', 'error');
            logout();
            return;
        }

        posts = await res.json();
        renderPosts();
    } catch (err) {
        toast('Failed to load posts', 'error');
    }
};

// Render Posts
const renderPosts = () => {
    elements.postsList.innerHTML = '';
    const filtered = currentCategory === 'all' ? posts : posts.filter(p => p.category === currentCategory);

    if (filtered.length === 0) {
        elements.postsList.innerHTML = '<div class="empty-state"><p>No posts yet in this category</p></div>';
        return;
    }

    filtered.forEach(post => {
        const postEl = document.createElement('div');
        postEl.className = 'post-card';
        const time = timeAgo(post.createdAt);
        const isOwner = post.uid === currentUser.uid;
        const canDelete = isOwner || isAdmin;
        const liked = post.likedBy?.includes(currentUserId);

        postEl.innerHTML = `
            <div class="post-header">
                <div class="post-user">
                    <div class="user-avatar small">${post.userDisplayName[0].toUpperCase()}</div>
                    <div>
                        <h4>${escapeHtml(post.userDisplayName)}</h4>
                        <small>@${post.uid} • ${time}</small>
                    </div>
                </div>
                ${canDelete ? `<button class="delete-btn" onclick="deletePost(${post.id})"><i class="fas fa-trash"></i></button>` : ''}
            </div>
            <div class="post-content">
                ${post.content ? `<p>${escapeHtml(post.content)}</p>` : ''}
                ${post.image ? `<img src="http://localhost:5000${post.image}" class="post-img" onclick="openImage(this.src)">` : ''}
                <div class="post-category-tag">${post.category}</div>
            </div>
            <div class="post-actions">
                <button class="action-btn ${liked ? 'liked' : ''}" onclick="toggleLike(${post.id}, this)">
                    <i class="fas fa-heart"></i>
                    <span>${post.likes || 0}</span>
                </button>
                <button class="action-btn"><i class="fas fa-comment"></i> ${post.comments?.length || 0}</button>
                <button class="action-btn"><i class="fas fa-share"></i></button>
            </div>
        `;
        elements.postsList.appendChild(postEl);
    });
};

// Utility Functions
const escapeHtml = (text) => text.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]);
const timeAgo = (date) => {
    const seconds = Math.floor((Date.now() - new Date(date)) / 1000);
    const intervals = {year:31536000, month:2592000, day:86400, hour:3600, minute:60};
    for (const [unit, secs] of Object.entries(intervals)) {
        const count = Math.floor(seconds / secs);
        if (count > 0) return `${count}${unit.charAt(0)} ago`;
    }
    return 'just now';
};

// Like Toggle
window.toggleLike = async (postId, btn) => {
    try {
        const res = await fetch(`${API_BASE}/posts/${postId}/like`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (res.ok) {
            const data = await res.json();
            const post = posts.find(p => p.id === postId);
            post.likes = data.likes;
            post.likedBy = post.likedBy || [];
            const index = post.likedBy.indexOf(currentUserId);
            if (index > -1) post.likedBy.splice(index, 1);
            else post.likedBy.push(currentUserId);
            btn.classList.toggle('liked');
            btn.querySelector('span').textContent = post.likes;
        }
    } catch (err) { }
};

// Delete Post
window.deletePost = async (postId) => {
    if (!confirm('Delete this post permanently?')) return;
    try {
        const res = await fetch(`${API_BASE}/posts/${postId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (res.ok) {
            posts = posts.filter(p => p.id !== postId);
            renderPosts();
            toast('Post deleted', 'success');
        } else {
            toast('Cannot delete this post', 'error');
        }
    } catch (err) {
        toast('Error deleting post', 'error');
    }
};

// Quick Post
elements.quickPostInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        createQuickPost();
    }
});

const createQuickPost = async () => {
    const content = elements.quickPostInput.value.trim();
    if (!content) return;
    const image = elements.quickImage.files[0];

    const formData = new FormData();
    formData.append('content', content);
    formData.append('category', currentCategory);
    if (image) formData.append('image', image);

    try {
        const res = await fetch(`${API_BASE}/posts`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        });
        if (res.ok) {
            const data = await res.json();
            posts.unshift(data.post);
            renderPosts();
            elements.quickPostInput.value = '';
            elements.quickImage.value = '';
            toast('Posted!', 'success');
        }
    } catch (err) {
        toast('Post failed', 'error');
    }
};

// Event Listeners
const setupEventListeners = () => {
    // Category Filter
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            currentCategory = link.dataset.category === 'all' ? 'all' : link.dataset.category;
            renderPosts();
        });
    });

    // Search
    elements.searchInput.addEventListener('input', () => {
        const query = elements.searchInput.value.toLowerCase();
        const filtered = posts.filter(p => 
            p.content.toLowerCase().includes(query) || 
            p.userDisplayName.toLowerCase().includes(query) ||
            p.uid.toLowerCase().includes(query)
        );
        elements.postsList.innerHTML = '';
        filtered.forEach(post => elements.postsList.appendChild(createPostElement(post)));
    });

    // Theme Toggle
    elements.themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    });

    // Sidebar Toggle
    elements.sidebarToggle.addEventListener('click', () => {
        elements.sidebar.classList.toggle('active');
    });

    // Logout
    elements.logoutBtn.addEventListener('click', logout);

    // FAB
    elements.fab.addEventListener('click', () => {
        elements.quickPostInput.focus();
    });
};

// Logout
function logout() {
    localStorage.removeItem('token');
    location.reload();
}

// Load Theme
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark');
}

// Auto Init
window.addEventListener('load', initApp);