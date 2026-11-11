import mysql from 'mysql2/promise';
import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '../../.env') });

const {
  DB_HOST = 'localhost',
  DB_PORT = 3306,
  DB_USER = 'root',
  DB_PASSWORD = '',
  DB_NAME = 'rentany'
} = process.env;

async function seed() {
  console.log('Starting Database Seeding...');
  
  let connection;
  try {
    const sslOptions = process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : null;
    connection = await mysql.createConnection({
      host: DB_HOST,
      port: Number(DB_PORT),
      user: DB_USER,
      password: DB_PASSWORD,
      database: DB_NAME,
      ssl: sslOptions
    });
    console.log('Connected to MySQL server for seeding.');
  } catch (err) {
    console.error('Database connection failed:', err.message);
    process.exit(1);
  }

  try {
    // 1. Clear existing data to prevent duplicate primary keys in dev
    console.log('Cleaning existing tables...');
    await connection.query('SET FOREIGN_KEY_CHECKS = 0');
    const tables = [
      'audit_logs', 'reports', 'user_devices', 'notifications', 'messages', 
      'conversation_participants', 'conversations', 'reviews', 'wishlists', 
      'deposits', 'refunds', 'payments', 'booking_items', 'bookings', 
      'listing_availability', 'listing_attributes', 'listing_images', 
      'listings', 'categories', 'user_addresses', 'users', 'banners'
    ];
    for (const table of tables) {
      await connection.query(`TRUNCATE TABLE \`${table}\``);
    }
    await connection.query('SET FOREIGN_KEY_CHECKS = 1');
    console.log('Cleaned existing tables successfully.');

    // 2. Seed Users
    console.log('Seeding users...');
    const passwordHash = await bcrypt.hash('password123', 10);
    const adminPasswordHash = await bcrypt.hash('danish123', 10);
    
    const users = [
      {
        uuid: crypto.randomUUID(),
        full_name: 'Rohan Patel',
        email: 'rohanpatel@gmail.com',
        phone: '+919876543210',
        password_hash: passwordHash,
        role: 'user',
        status: 'active',
        email_verified: 1,
        phone_verified: 1
      },
      {
        uuid: crypto.randomUUID(),
        full_name: 'System Admin',
        email: 'admin123@gmail.com',
        phone: '+910000000000',
        password_hash: adminPasswordHash,
        role: 'admin',
        status: 'active',
        email_verified: 1,
        phone_verified: 1
      },
      {
        uuid: crypto.randomUUID(),
        full_name: 'Amit Sharma',
        email: 'amitsharma@gmail.com',
        phone: '+919876543211',
        password_hash: passwordHash,
        role: 'user',
        status: 'active',
        email_verified: 1,
        phone_verified: 1
      },
      {
        uuid: crypto.randomUUID(),
        full_name: 'Priya Shah',
        email: 'priyashah@gmail.com',
        phone: '+919876543212',
        password_hash: passwordHash,
        role: 'user',
        status: 'active',
        email_verified: 1,
        phone_verified: 1
      },
      {
        uuid: crypto.randomUUID(),
        full_name: 'Rajesh Kumar',
        email: 'rajeshkumar@gmail.com',
        phone: '+919876543213',
        password_hash: passwordHash,
        role: 'user',
        status: 'active',
        email_verified: 1,
        phone_verified: 1
      },
      {
        uuid: crypto.randomUUID(),
        full_name: 'Karan Patel',
        email: 'karanpatel@gmail.com',
        phone: '+919876543214',
        password_hash: passwordHash,
        role: 'user',
        status: 'active',
        email_verified: 1,
        phone_verified: 1
      }
    ];

    const insertedUserIds = {};
    for (const u of users) {
      const [res] = await connection.query(
        `INSERT INTO users (uuid, full_name, email, phone, password_hash, role, status, email_verified, phone_verified)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [u.uuid, u.full_name, u.email, u.phone, u.password_hash, u.role, u.status, u.email_verified, u.phone_verified]
      );
      insertedUserIds[u.email] = res.insertId;
    }
    console.log('Seeded users successfully.');

    // 3. Seed Addresses
    console.log('Seeding user addresses...');
    const addresses = [
      {
        user_id: insertedUserIds['rohanpatel@gmail.com'],
        address_line: 'G-102, Sharnam Sky, Science City Road',
        city: 'Ahmedabad',
        state: 'Gujarat',
        country: 'India',
        postal_code: '380060',
        latitude: 23.0754,
        longitude: 72.5078,
        is_default: 1
      }
    ];
    for (const addr of addresses) {
      await connection.query(
        `INSERT INTO user_addresses (user_id, address_line, city, state, country, postal_code, latitude, longitude, is_default)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [addr.user_id, addr.address_line, addr.city, addr.state, addr.country, addr.postal_code, addr.latitude, addr.longitude, addr.is_default]
      );
    }

    // 4. Seed Categories
    console.log('Seeding categories...');
    const categories = [
      { name: 'Vehicles', slug: 'vehicles', description: 'Cars, bikes, bicycles, and scooters', icon: 'car', parent_id: null },
      { name: 'Electronics', slug: 'electronics', description: 'Mobiles, laptops, projectors, and speakers', icon: 'cpu', parent_id: null },
      { name: 'Real Estate', slug: 'real-estate', description: 'Apartments, villas, offices, and plots', icon: 'home', parent_id: null },
      { name: 'Furniture', slug: 'furniture', description: 'Sofas, tables, beds, and office furniture', icon: 'sofa', parent_id: null },
      { name: 'Tools', slug: 'tools', description: 'Drills, saws, ladders, and toolkits', icon: 'tool', parent_id: null },
      { name: 'Camping', slug: 'camping', description: 'Tents, sleeping bags, and camping gear', icon: 'tent', parent_id: null },
      { name: 'Cameras', slug: 'cameras', description: 'DSLRs, lenses, tripods, and action cams', icon: 'camera', parent_id: null },
      { name: 'Sports', slug: 'sports', description: 'Bicycles, cricket kits, tennis rackets', icon: 'trophy', parent_id: null },
      { name: 'Home & Kitchen', slug: 'home-kitchen', description: 'Dinner sets, appliances, and utensils', icon: 'chef-hat', parent_id: null },
      { name: 'Other', slug: 'other', description: 'Miscellaneous rental items', icon: 'package', parent_id: null }
    ];

    const insertedCategoryIds = {};
    for (const cat of categories) {
      const [res] = await connection.query(
        `INSERT INTO categories (name, slug, description, icon, parent_id, status)
         VALUES (?, ?, ?, ?, ?, 'active')`,
        [cat.name, cat.slug, cat.description, cat.icon, cat.parent_id]
      );
      insertedCategoryIds[cat.name] = res.insertId;
    }
    console.log('Seeded categories successfully.');

    // 5. Seed Listings
    console.log('Seeding listings...');
    const listings = [
      {
        uuid: crypto.randomUUID(),
        owner_id: insertedUserIds['amitsharma@gmail.com'],
        category_id: insertedCategoryIds['Electronics'],
        title: 'DSLR Camera',
        slug: 'dslr-camera',
        description: 'Professional Canon DSLR with 18-55mm lens. Perfect for weddings, travel photography, and video shoots.',
        price_per_day: 500.00,
        refundable_deposit: 2000.00,
        quantity: 1,
        condition: 'Like New',
        location_address: 'Satellite Road, Ahmedabad',
        city: 'Ahmedabad',
        state: 'Gujarat',
        country: 'India',
        postal_code: '380015',
        latitude: 23.0754,
        longitude: 72.5078,
        rating_average: 4.8,
        rating_count: 24,
        image_url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=500'
      },
      {
        uuid: crypto.randomUUID(),
        owner_id: insertedUserIds['priyashah@gmail.com'],
        category_id: insertedCategoryIds['Home & Kitchen'],
        title: 'Luxury Dinner Set',
        slug: 'luxury-dinner-set',
        description: '44-piece premium bone china dinner set. Perfect for family gatherings, house warming parties, and grand dinners.',
        price_per_day: 300.00,
        refundable_deposit: 1000.00,
        quantity: 1,
        condition: 'Good',
        location_address: 'Bodakdev, Ahmedabad',
        city: 'Ahmedabad',
        state: 'Gujarat',
        country: 'India',
        postal_code: '380054',
        latitude: 23.0782,
        longitude: 72.5112,
        rating_average: 4.5,
        rating_count: 12,
        image_url: 'https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&q=80&w=500'
      },
      {
        uuid: crypto.randomUUID(),
        owner_id: insertedUserIds['rajeshkumar@gmail.com'],
        category_id: insertedCategoryIds['Electronics'],
        title: '4K Home Projector',
        slug: '4k-home-projector',
        description: 'Ultra HD portable home theater projector. Includes HDMI cable, remote, and 100-inch portable screen.',
        price_per_day: 800.00,
        refundable_deposit: 3000.00,
        quantity: 1,
        condition: 'Like New',
        location_address: 'Ghatlodia, Ahmedabad',
        city: 'Ahmedabad',
        state: 'Gujarat',
        country: 'India',
        postal_code: '380061',
        latitude: 23.0721,
        longitude: 72.5045,
        rating_average: 4.9,
        rating_count: 38,
        image_url: 'https://images.unsplash.com/photo-1535016120720-40c646be5580?auto=format&fit=crop&q=80&w=500'
      },
      {
        uuid: crypto.randomUUID(),
        owner_id: insertedUserIds['karanpatel@gmail.com'],
        category_id: insertedCategoryIds['Electronics'],
        title: 'Party Sound System',
        slug: 'party-sound-system',
        description: 'High-bass party speakers with dual wireless mics. Ideal for birthdays, terrace events, and karaoke nights.',
        price_per_day: 1200.00,
        refundable_deposit: 4000.00,
        quantity: 1,
        condition: 'Good',
        location_address: 'Vastrapur, Ahmedabad',
        city: 'Ahmedabad',
        state: 'Gujarat',
        country: 'India',
        postal_code: '380015',
        latitude: 23.0799,
        longitude: 72.5065,
        rating_average: 4.7,
        rating_count: 19,
        image_url: 'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&q=80&w=500'
      }
    ];

    for (const item of listings) {
      const [res] = await connection.query(
        `INSERT INTO listings (uuid, owner_id, category_id, title, slug, description, price_per_day, refundable_deposit, quantity, \`condition\`, location_address, city, state, country, postal_code, latitude, longitude, rating_average, rating_count, status)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'published')`,
        [item.uuid, item.owner_id, item.category_id, item.title, item.slug, item.description, item.price_per_day, item.refundable_deposit, item.quantity, item.condition, item.location_address, item.city, item.state, item.country, item.postal_code, item.latitude, item.longitude, item.rating_average, item.rating_count]
      );
      
      // Seed listing image
      await connection.query(
        `INSERT INTO listing_images (listing_id, image_url, sort_order, is_primary)
         VALUES (?, ?, ?, ?)`,
        [res.insertId, item.image_url, 0, 1]
      );
    }
    console.log('Seeded listings successfully.');

    // 6. Seed Banners
    console.log('Seeding promotional banners...');
    const banners = [
      { title: 'Rent Top Electronics', subtitle: 'Get up to 30% off on projectors & sound systems this weekend!', image_url: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&q=80&w=500', action_type: 'category', action_value: 'electronics', priority: 1 },
      { title: 'Professional DSLR Kits', subtitle: 'Capture your memories with our top cameras.', image_url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=500', action_type: 'category', action_value: 'cameras', priority: 2 }
    ];
    for (const b of banners) {
      await connection.query(
        `INSERT INTO banners (title, subtitle, image_url, action_type, action_value, priority, status)
         VALUES (?, ?, ?, ?, ?, ?, 'active')`,
        [b.title, b.subtitle, b.image_url, b.action_type, b.action_value, b.priority]
      );
    }
    console.log('Seeded banners successfully.');

  } catch (err) {
    console.error('Error seeding database:', err.message);
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
      console.log('Seeding connection closed.');
    }
  }
}

seed();
