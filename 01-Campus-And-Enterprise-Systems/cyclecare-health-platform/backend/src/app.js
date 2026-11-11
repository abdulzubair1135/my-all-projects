const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const path = require('path');

const authRoutes = require('./routes/authRoutes');
const cycleRoutes = require('./routes/cycleRoutes');
const symptomsRoutes = require('./routes/symptomsRoutes');
const moodsRoutes = require('./routes/moodsRoutes');
const remindersRoutes = require('./routes/remindersRoutes');
const storeRoutes = require('./routes/storeRoutes');
const ordersRoutes = require('./routes/ordersRoutes');
const paymentsRoutes = require('./routes/paymentsRoutes');
const careKitRoutes = require('./routes/careKitRoutes');
const wellnessRoutes = require('./routes/wellnessRoutes');
const aiRoutes = require('./routes/aiRoutes');
const adminRoutes = require('./routes/adminRoutes');
const productRoutes = require('./routes/productRoutes');
const partnerRoutes = require('./routes/partnerRoutes');
const deliveryRoutes = require('./routes/deliveryRoutes');
const addressesRoutes = require('./routes/addressesRoutes');
const chatRoutes = require('./routes/chatRoutes');
const monitoringRoutes = require('./routes/monitoringRoutes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Security Middlewares
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      scriptSrcAttr: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https:"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https:", "http:"],
    }
  }
}));
app.use(cors());

// Rate Limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200, // Limit each IP to 200 requests per windowMs
  message: { success: false, message: 'Too many requests, please try again later.', code: 'RATE_LIMIT_EXCEEDED' }
});
app.use('/api/', limiter);

// Body Parsers & Logging
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

// Static Admin Web Panel & Routes
app.use('/admin-panel', express.static(path.join(__dirname, 'views')));
app.get(['/admin', '/admin-panel'], (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'admin.html'));
});

// API Routes (v1)
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/cycle', cycleRoutes);
app.use('/api/v1/symptoms', symptomsRoutes);
app.use('/api/v1/moods', moodsRoutes);
app.use('/api/v1/reminders', remindersRoutes);
app.use('/api/v1/store', storeRoutes);
app.use('/api/v1/orders', ordersRoutes);
app.use('/api/v1/payments', paymentsRoutes);
app.use('/api/v1/care-kits', careKitRoutes);
app.use('/api/v1/wellness', wellnessRoutes);
app.use('/api/v1/ai', aiRoutes);
app.use('/api/v1/admin', adminRoutes);
app.use('/api/v1/products', productRoutes);
app.use('/api/v1/partners', partnerRoutes);
app.use('/api/v1/partner', partnerRoutes);
app.use('/api/v1/deliveries', deliveryRoutes);
app.use('/api/v1/delivery', deliveryRoutes);
app.use('/api/v1/addresses', addressesRoutes);
app.use('/api/v1/chat', chatRoutes);
app.use('/api/v1/monitoring', monitoringRoutes);
app.use('/api/v1/notifications', monitoringRoutes);

// Healthcheck Endpoint
app.get('/api/v1/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'CycleCare API',
    version: '1.0.0'
  });
});

// Root Healthcheck
app.get('/', (req, res) => {
  res.json({
    name: 'CycleCare API Server',
    status: 'ONLINE',
    tagline: 'Track • Understand • Prepare • Care',
    version: '1.0.0',
    adminPanel: '/admin-panel/admin.html'
  });
});

// Centralized Error Handler
app.use(errorHandler);

module.exports = app;
