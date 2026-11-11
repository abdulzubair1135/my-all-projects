export interface SOSEvent {
  _id: string;
  eventId: string;
  userId?: string;
  userName?: string;
  userPhone?: string;
  originDeviceId: string;
  type: 'TRAPPED' | 'MEDICAL' | 'FIRE' | 'FLOOD' | 'BUILDING_COLLAPSE' | 'ACCIDENT' | 'MISSING_PERSON' | 'OTHER';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  description?: string;
  peopleCount: number;
  injuredCount: number;
  location: {
    type: 'Point';
    coordinates: [number, number]; // [lng, lat]
  };
  locationAccuracy?: number;
  addressText?: string;
  status: 'CREATED' | 'RECEIVED' | 'VERIFIED' | 'ASSIGNED' | 'ACCEPTED' | 'EN_ROUTE' | 'ARRIVED' | 'RESOLVED' | 'CANCELLED';
  source: 'ONLINE' | 'OFFLINE_BLE' | 'BLE_RELAY';
  hopCount: number;
  relayPath: string[];
  assignedTeamId?: any;
  assignedTeamName?: string;
  verifiedBy?: string;
  resolvedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SOSStats {
  totalActive: number;
  critical: number;
  highPriority: number;
  assigned: number;
  resolved: number;
  offlineRelayed: number;
  averageResponseTimeMinutes: number;
}

export interface RescueTeam {
  _id: string;
  name: string;
  contactNumber: string;
  teamType: string;
  membersCount: number;
  vehicle: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  status: 'AVAILABLE' | 'ASSIGNED' | 'EN_ROUTE' | 'ON_SCENE' | 'OFFLINE';
  currentAssignment?: any;
  lastSeen: string;
}

export interface Hospital {
  _id: string;
  name: string;
  phone: string;
  address: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  emergencyStatus: 'NORMAL' | 'HIGH_ALERT' | 'OVERWHELMED' | 'DIVERTING';
  totalBeds: number;
  availableBeds: number;
  icuBeds: number;
  availableICUBeds: number;
  ambulances: number;
  availableAmbulances: number;
  bloodAvailability: {
    aPos: number;
    aNeg: number;
    bPos: number;
    bNeg: number;
    abPos: number;
    abNeg: number;
    oPos: number;
    oNeg: number;
  };
}

export interface Shelter {
  _id: string;
  name: string;
  address: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  capacity: number;
  occupied: number;
  waterAvailable: boolean;
  foodAvailable: boolean;
  medicalAvailable: boolean;
  status: 'OPEN' | 'FULL' | 'CLOSED' | 'EVACUATING';
  managedBy?: string;
}

export interface Alert {
  _id: string;
  title: string;
  message: string;
  type: string;
  severity: 'WARNING' | 'DANGER' | 'SEVERE' | 'EXTREME';
  location?: {
    type: 'Point';
    coordinates: [number, number];
  };
  radiusKm?: number;
  source: string;
  createdAt: string;
  expiresAt: string;
  active: boolean;
}

export interface CitizenReport {
  _id: string;
  userName?: string;
  userPhone?: string;
  type: string;
  description: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  addressText?: string;
  mediaUrl?: string;
  images?: string[];
  verificationStatus: 'SUBMITTED' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED' | 'ACTION_TAKEN';
  createdAt: string;
}

export interface Resource {
  _id: string;
  organizationName: string;
  type: string;
  quantity: number;
  unit: string;
  availableQuantity: number;
  reservedQuantity: number;
}
