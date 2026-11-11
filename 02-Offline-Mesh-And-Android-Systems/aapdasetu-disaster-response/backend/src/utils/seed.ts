import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
import { User } from '../models/User.js';
import { Hospital } from '../models/Hospital.js';
import { Shelter } from '../models/Shelter.js';
import { RescueTeam } from '../models/RescueTeam.js';
import { NGO } from '../models/NGO.js';
import { Resource } from '../models/Resource.js';
import { Alert } from '../models/Alert.js';
import { Directive } from '../models/Directive.js';

dotenv.config();

const seed = async () => {
  if (mongoose.connection.readyState === 0) {
    const uri = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/aapdasetu';
    await mongoose.connect(uri);
    console.log('[Seed] Connected to MongoDB');
  } else {
    console.log('[Seed] Reusing active MongoDB connection');
  }

  const passwordHash = await bcrypt.hash('admin123', 10);

  // 1. Initial Users
  const users = [
    { name: 'DDMA Command Officer', phone: '9876543210', email: 'gov@aapdasetu.gov.in', passwordHash, role: 'GOVERNMENT', verified: true },
    { name: 'NDRF Unit Commander', phone: '9876543211', email: 'rescue@aapdasetu.gov.in', passwordHash, role: 'RESCUE', verified: true },
    { name: 'Civil Hospital Emergency Desk', phone: '9876543212', email: 'hospital@civil.gov.in', passwordHash, role: 'HOSPITAL', verified: true },
    { name: 'Red Cross Relief Manager', phone: '9876543213', email: 'ngo@redcross.org', passwordHash, role: 'NGO', verified: true },
    { name: 'AapdaSetu System Admin', phone: '9876543214', email: 'admin@aapdasetu.gov.in', passwordHash, role: 'SUPER_ADMIN', verified: true },
    { name: 'Rahul Sharma (Citizen)', phone: '9999999999', address: 'B-402 Shivalik Residency, Satellite', city: 'Ahmedabad', state: 'Gujarat', role: 'CITIZEN', verified: true }
  ];

  for (const u of users) {
    const exists = await User.findOne({ $or: [{ email: u.email }, { phone: u.phone }] });
    if (!exists) {
      await User.create(u);
      console.log(`[Seed] Created user: ${u.name} (${u.role})`);
    }
  }

  // 2. Real Hospitals in Ahmedabad
  const hospitals = [
    {
      name: 'Ahmedabad Civil Hospital & Trauma Centre',
      phone: '079-22680074',
      address: 'Asarwa, Ahmedabad, Gujarat 380016',
      location: { type: 'Point', coordinates: [72.5873, 23.0525] },
      emergencyStatus: 'NORMAL',
      totalBeds: 1200,
      availableBeds: 340,
      icuBeds: 150,
      availableICUBeds: 28,
      ambulances: 15,
      availableAmbulances: 6,
      bloodAvailability: { aPos: 45, aNeg: 12, bPos: 60, bNeg: 15, abPos: 20, abNeg: 8, oPos: 80, oNeg: 25 }
    },
    {
      name: 'Sardar Vallabhbhai Patel (SVP) Hospital',
      phone: '079-26577621',
      address: 'Ellisbridge, Ahmedabad, Gujarat 380006',
      location: { type: 'Point', coordinates: [72.5714, 23.0185] },
      emergencyStatus: 'NORMAL',
      totalBeds: 800,
      availableBeds: 210,
      icuBeds: 100,
      availableICUBeds: 18,
      ambulances: 10,
      availableAmbulances: 4,
      bloodAvailability: { aPos: 30, aNeg: 8, bPos: 40, bNeg: 10, abPos: 15, abNeg: 5, oPos: 55, oNeg: 18 }
    },
    {
      name: 'Apollo Hospital International',
      phone: '079-66701800',
      address: 'Plot 1A, GIDC Bhat, Gandhinagar / Ahmedabad 382428',
      location: { type: 'Point', coordinates: [72.6041, 23.1098] },
      emergencyStatus: 'NORMAL',
      totalBeds: 400,
      availableBeds: 95,
      icuBeds: 60,
      availableICUBeds: 12,
      ambulances: 8,
      availableAmbulances: 3,
      bloodAvailability: { aPos: 20, aNeg: 6, bPos: 25, bNeg: 7, abPos: 10, abNeg: 3, oPos: 35, oNeg: 10 }
    }
  ];

  for (const h of hospitals) {
    const exists = await Hospital.findOne({ name: h.name });
    if (!exists) {
      await Hospital.create(h);
      console.log(`[Seed] Created hospital: ${h.name}`);
    }
  }

  // 3. Real Shelters
  const shelters = [
    {
      name: 'Sardar Patel Indoor Complex Evacuation Center',
      address: 'Navrangpura, Ahmedabad, Gujarat 380009',
      location: { type: 'Point', coordinates: [72.5630, 23.0375] },
      capacity: 1500,
      occupied: 120,
      waterAvailable: true,
      foodAvailable: true,
      medicalAvailable: true,
      status: 'OPEN',
      managedBy: 'Ahmedabad Municipal Corporation (AMC)'
    },
    {
      name: 'Gujarat University Convention Shelter',
      address: 'Near Helmet Cross Roads, Memnagar, Ahmedabad 380052',
      location: { type: 'Point', coordinates: [72.5448, 23.0360] },
      capacity: 2500,
      occupied: 0,
      waterAvailable: true,
      foodAvailable: true,
      medicalAvailable: true,
      status: 'OPEN',
      managedBy: 'District Disaster Management Authority'
    },
    {
      name: 'Riverfront Emergency Assembly Relief Zone',
      address: 'Sabarmati Riverfront West, Ahmedabad 380001',
      location: { type: 'Point', coordinates: [72.5750, 23.0280] },
      capacity: 3000,
      occupied: 50,
      waterAvailable: true,
      foodAvailable: true,
      medicalAvailable: true,
      status: 'OPEN',
      managedBy: 'AMC Disaster Relief Wing'
    }
  ];

  for (const s of shelters) {
    const exists = await Shelter.findOne({ name: s.name });
    if (!exists) {
      await Shelter.create(s);
      console.log(`[Seed] Created shelter: ${s.name}`);
    }
  }

  // 4. Rescue Teams
  const teams = [
    {
      name: 'NDRF 6th Battalion Alpha Unit',
      contactNumber: '079-23240001',
      teamType: 'NDRF',
      membersCount: 12,
      vehicle: 'Heavy Rescue All-Terrain Vehicle',
      location: { type: 'Point', coordinates: [72.5800, 23.0400] },
      status: 'AVAILABLE'
    },
    {
      name: 'SDRF Gujarat Quick Response Bravo',
      contactNumber: '079-23250002',
      teamType: 'SDRF',
      membersCount: 8,
      vehicle: 'Flood Inflatable Boat & Van',
      location: { type: 'Point', coordinates: [72.5650, 23.0250] },
      status: 'AVAILABLE'
    },
    {
      name: 'Ahmedabad Fire & Emergency Rescue Squad',
      contactNumber: '101',
      teamType: 'FIRE_RESCUE',
      membersCount: 6,
      vehicle: 'Hydraulic Platform Rescue Tender',
      location: { type: 'Point', coordinates: [72.5700, 23.0200] },
      status: 'AVAILABLE'
    }
  ];

  for (const t of teams) {
    const exists = await RescueTeam.findOne({ name: t.name });
    if (!exists) {
      await RescueTeam.create(t);
      console.log(`[Seed] Created rescue team: ${t.name}`);
    }
  }

  // 5. Official Alert (Active status)
  const alertExists = await Alert.findOne({ title: /Preparedness Advisory/ });
  if (!alertExists) {
    await Alert.create({
      title: 'State Monsoon Preparedness & Safe Zone Advisory',
      message: 'All regional response teams on standby. Citizen networks and local shelters are fully operational.',
      type: 'EXTREME_WEATHER',
      severity: 'WARNING',
      location: { type: 'Point', coordinates: [72.5714, 23.0225] },
      radiusKm: 30,
      source: 'GOVERNMENT',
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      active: true
    });
    console.log('[Seed] Created default official preparedness alert');
  }

  // 6. Tactical Directives (Gov -> NGO Supply Mobilization)
  const dirExists = await Directive.findOne({});
  if (!dirExists) {
    await Directive.create({
      directiveId: 'DIR-88129A',
      title: 'Deploy 500 Ration Food Kits & 1000L Potable Water',
      category: 'FOOD_SUPPLY',
      quantity: 500,
      unit: 'Packets',
      targetZone: 'Paldi Relief Camp (Ward 7)',
      assignedNgoName: 'Red Cross Gujarat',
      priority: 'HIGH',
      status: 'PENDING',
      instructions: 'Urgent distribution required for riverside families relocated due to flood alerts.',
      issuedAt: new Date()
    });
    await Directive.create({
      directiveId: 'DIR-44912B',
      title: 'Dispatch 200 Emergency Medical & Trauma Kits',
      category: 'MEDICAL_KITS',
      quantity: 200,
      unit: 'Kits',
      targetZone: 'Riverfront Emergency Assembly Relief Zone',
      assignedNgoName: 'Goonj Disaster Relief',
      priority: 'URGENT',
      status: 'CRITICAL_STOCK_SHORTAGE',
      instructions: 'First aid kits for minor injuries and waterborne infection prevention.',
      stockShortageDetails: {
        reportedAt: new Date(),
        missingItems: 'Sterile bandages, antiseptic solution, ORS packets',
        requestedQuantity: 150,
        notes: 'Depot stock exhausted. Immediate supply convoy needed from Govt Central Depot.'
      },
      issuedAt: new Date(Date.now() - 3600000)
    });
    console.log('[Seed] Created default tactical relief directives');
  }

  console.log('[Seed] Database initialization completed successfully.');
};

export const seedDatabase = seed;

if (process.argv[1] && process.argv[1].includes('seed')) {
  seed().then(() => process.exit(0)).catch((err) => {
    console.error('[Seed] Error during seeding:', err);
    process.exit(1);
  });
}

