import { Router } from 'express';
import pool from '../config/database.js';
import { userRepository } from '../repositories/user.repository.js';
import { listingRepository } from '../repositories/listing.repository.js';
import { bookingRepository } from '../repositories/booking.repository.js';
import { chatRepository } from '../repositories/chat.repository.js';
import { bookingService } from '../services/booking.service.js';
import fs from 'fs';
import path from 'path';

const router = Router();

const DEFAULT_USER_ID = 1; // Rohan Patel
const SETTINGS_FILE = path.resolve('uploads/compatibility_settings.json');

// Middleware to track online status for compatibility routes
router.use(async (req, res, next) => {
  try {
    await pool.query('UPDATE users SET last_active_at = NOW() WHERE id = ?', [DEFAULT_USER_ID]);
  } catch (err) {
    console.error('Failed to update compatibility active status:', err.message);
  }
  next();
});

// Helper to initialize and load app settings
function loadSettings() {
  if (fs.existsSync(SETTINGS_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(SETTINGS_FILE, 'utf8'));
    } catch (e) {
      console.error('Error reading compatibility settings file:', e.message);
    }
  }
  return {
    id: 1,
    bookingUpdates: true,
    messagesNotification: true,
    offersNotification: false,
    systemUpdates: true,
    showOnlineStatus: true,
    showPhoneNumber: false,
    profileVisibilityPublic: true,
    isDarkMode: false,
    searchRadiusKm: 10,
    useCurrentLocation: true,
    backendUrl: "",
    syncEnabled: true
  };
}

function saveSettings(settings) {
  try {
    fs.writeFileSync(SETTINGS_FILE, JSON.stringify(settings, null, 2), 'utf8');
  } catch (e) {
    console.error('Error writing compatibility settings file:', e.message);
  }
}

// 1. Profile Compatibility
router.get('/profile', async (req, res, next) => {
  try {
    const user = await userRepository.findById(DEFAULT_USER_ID);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    // Map to UserProfileEntity structure
    res.json({
      id: user.id,
      name: user.full_name,
      email: user.email,
      phone: user.phone,
      dob: '15 May 1997', // Mock profile details not stored in users table
      gender: 'Male',
      address: 'G-102, Sharnam Sky, Science City Road, Ahmedabad, Gujarat - 380060',
      kycVerified: user.email_verified === 1,
      walletBalance: 2450.0
    });
  } catch (err) {
    next(err);
  }
});

router.post('/profile', async (req, res, next) => {
  try {
    const { name, email, phone } = req.body;
    await userRepository.update(DEFAULT_USER_ID, {
      full_name: name,
      email,
      phone
    });
    const user = await userRepository.findById(DEFAULT_USER_ID);
    res.json({
      id: user.id,
      name: user.full_name,
      email: user.email,
      phone: user.phone,
      dob: req.body.dob || '15 May 1997',
      gender: req.body.gender || 'Male',
      address: req.body.address || 'G-102, Sharnam Sky, Science City Road, Ahmedabad, Gujarat - 380060',
      kycVerified: user.email_verified === 1,
      walletBalance: req.body.walletBalance || 2450.0
    });
  } catch (err) {
    next(err);
  }
});

// 2. Items Compatibility
router.get('/items', async (req, res, next) => {
  try {
    const [rows] = await pool.query(
      `SELECT l.*, c.name as category_name, 
              (SELECT image_url FROM listing_images WHERE listing_id = l.id AND is_primary = 1 LIMIT 1) as primary_image,
              owner.full_name as owner_name, owner.rating_average as owner_rating, 
              (SELECT COUNT(*) FROM reviews WHERE owner_id = owner.id) as owner_reviews
       FROM listings l
       JOIN categories c ON l.category_id = c.id
       JOIN users owner ON l.owner_id = owner.id
       WHERE l.status = 'published' AND l.deleted_at IS NULL
       ORDER BY l.id DESC`
    );

    // Map to RentalItemEntity list
    const mapped = rows.map(item => ({
      id: item.id,
      name: item.title,
      category: item.category_name,
      pricePerDay: Number(item.price_per_day),
      securityDeposit: Number(item.refundable_deposit),
      description: item.description,
      imageUrl: item.primary_image || 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=500',
      rating: Number(item.rating_average),
      reviewsCount: item.rating_count,
      ownerName: item.owner_name,
      ownerRating: Number(item.rating_average), // Default to listing rating if owner doesn't have separate rating
      ownerReviewsCount: item.rating_count,
      latitude: Number(item.latitude),
      longitude: Number(item.longitude),
      isBookmarked: false // Handled in client app or simple cookie
    }));

    res.json(mapped);
  } catch (err) {
    next(err);
  }
});

router.post('/items', async (req, res, next) => {
  try {
    const { name, category, pricePerDay, securityDeposit, description, imageUrl, latitude, longitude } = req.body;
    
    // Find category ID matching name or default to 1 (Electronics)
    const [catRows] = await pool.query('SELECT id FROM categories WHERE name = ?', [category]);
    const categoryId = catRows.length > 0 ? catRows[0].id : 2; // Electronics

    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const [insertRes] = await pool.query(
      `INSERT INTO listings (uuid, owner_id, category_id, title, slug, description, price_per_day, refundable_deposit,
        location_address, city, state, country, postal_code, latitude, longitude, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'published')`,
      [
        crypto.randomUUID(),
        DEFAULT_USER_ID,
        categoryId,
        name,
        slug,
        description,
        pricePerDay,
        securityDeposit,
        'Ahmedabad, India', 'Ahmedabad', 'Gujarat', 'India', '380001',
        latitude || 23.0754, longitude || 72.5078
      ]
    );

    const listingId = insertRes.insertId;

    // Add image url
    if (imageUrl) {
      await pool.query(
        'INSERT INTO listing_images (listing_id, image_url, is_primary) VALUES (?, ?, 1)',
        [listingId, imageUrl]
      );
    }

    res.json({
      id: listingId,
      name,
      category,
      pricePerDay,
      securityDeposit,
      description,
      imageUrl,
      rating: 5.0,
      reviewsCount: 1,
      ownerName: 'Rohan Patel',
      ownerRating: 4.8,
      ownerReviewsCount: 12,
      latitude: latitude || 23.0754,
      longitude: longitude || 72.5078,
      isBookmarked: false
    });
  } catch (err) {
    next(err);
  }
});

// 3. Bookings Compatibility
router.get('/bookings', async (req, res, next) => {
  try {
    const [rows] = await pool.query(
      `SELECT b.*, l.title as listing_name,
              (SELECT image_url FROM listing_images WHERE listing_id = l.id AND is_primary = 1 LIMIT 1) as primary_image
       FROM bookings b
       JOIN listings l ON b.listing_id = l.id
       WHERE b.renter_id = ?
       ORDER BY b.id DESC`,
      [DEFAULT_USER_ID]
    );

    // Map to BookingEntity
    const mapped = rows.map(b => ({
      id: b.id,
      itemId: b.listing_id,
      itemName: b.listing_name,
      itemImageUrl: b.primary_image || 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=500',
      startDate: b.start_date,
      endDate: b.end_date,
      deliveryType: b.delivery_fee > 0 ? 'Delivery' : 'Self Pickup',
      totalPrice: Number(b.total_amount),
      status: b.booking_status === 'active' ? 'Ongoing' : (b.booking_status === 'completed' ? 'Completed' : 'Upcoming'),
      timestamp: new Date(b.created_at).getTime()
    }));

    res.json(mapped);
  } catch (err) {
    next(err);
  }
});

router.post('/bookings', async (req, res, next) => {
  try {
    const { itemId, startDate, endDate, deliveryType, totalPrice } = req.body;
    
    // Call transactional booking creation helper directly mapped for DEFAULT_USER_ID
    const booking = await bookingService.createBooking(DEFAULT_USER_ID, {
      listingId: itemId,
      startDate,
      endDate,
      deliveryType: deliveryType || 'Self Pickup',
      quantity: 1
    });

    res.json({
      id: booking.id,
      itemId: booking.listing_id,
      itemName: booking.listing_title,
      itemImageUrl: booking.listing_primary_image,
      startDate: booking.start_date,
      endDate: booking.end_date,
      deliveryType: booking.delivery_fee > 0 ? 'Delivery' : 'Self Pickup',
      totalPrice: Number(booking.total_amount),
      status: 'Upcoming',
      timestamp: new Date(booking.created_at).getTime()
    });
  } catch (err) {
    next(err);
  }
});

// 4. Chats Compatibility
router.get('/chats/:itemId', async (req, res, next) => {
  try {
    const itemId = Number(req.params.itemId);
    
    // Find listing to get owner id
    const listing = await listingRepository.findById(itemId);
    if (!listing) return res.json([]);

    // Find if a conversation already exists
    const [convo] = await pool.query(
      `SELECT c.id FROM conversations c
       JOIN conversation_participants cp1 ON c.id = cp1.conversation_id AND cp1.user_id = ?
       JOIN conversation_participants cp2 ON c.id = cp2.conversation_id AND cp2.user_id = ?
       WHERE c.listing_id = ?`,
      [DEFAULT_USER_ID, listing.owner_id, itemId]
    );

    if (convo.length === 0) return res.json([]);

    const messages = await chatRepository.getConversationMessages(convo[0].id);
    
    // Map to ChatMessageEntity
    const mapped = messages.map(m => ({
      id: m.id,
      itemId,
      senderName: m.sender_name,
      messageText: m.message,
      timestamp: new Date(m.created_at).getTime(),
      isUserMessage: m.sender_id === DEFAULT_USER_ID
    }));

    res.json(mapped);
  } catch (err) {
    next(err);
  }
});

router.post('/chats', async (req, res, next) => {
  try {
    const { itemId, messageText } = req.body;
    
    const listing = await listingRepository.findById(itemId);
    if (!listing) {
      return res.status(404).json({ message: 'Listing not found' });
    }

    // Get or create convo
    const convoId = await chatRepository.getOrCreateConversation(itemId, DEFAULT_USER_ID, listing.owner_id);
    
    const messageId = await chatRepository.createMessage(convoId, DEFAULT_USER_ID, messageText, 'text');

    res.json({
      id: messageId,
      itemId,
      senderName: 'Rohan Patel',
      messageText,
      timestamp: Date.now(),
      isUserMessage: true
    });
  } catch (err) {
    next(err);
  }
});

// 5. Settings Compatibility
router.get('/settings', (req, res) => {
  res.json(loadSettings());
});

router.post('/settings', (req, res) => {
  const settings = { ...loadSettings(), ...req.body, id: 1 };
  saveSettings(settings);
  res.json(settings);
});

export default router;
