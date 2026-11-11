export type ScreenType =
  | 'signin'
  | 'home'
  | 'alerts'
  | 'need-help'
  | 'safe-shelters'
  | 'medical-help'
  | 'disaster-map'
  | 'report-incident'
  | 'history'
  | 'settings'
  | 'emergency-chat'
  | 'offline-network';

export type NavTab = 'home' | 'alerts' | 'shelters' | 'map' | 'history' | 'settings';
export type TabType = 'home' | 'alerts' | 'shelters' | 'map' | 'history' | 'settings';

export interface EmergencyContact {
  id: string;
  name: string;
  relation: string;
  phone: string;
}

export interface UserProfile {
  name: string;
  fullName?: string;
  email: string;
  phone: string;
  avatarUrl: string;
  bloodGroup: string;
  address: string;
  city: string;
  state: string;
  emergencyContacts: EmergencyContact[];
  language?: string;
  verified?: boolean;
  locationAccess?: boolean;
  privateIdentity?: boolean;
  showLocationToNearby?: boolean;
  emergencyMessages?: boolean;
  communityUpdates?: boolean;
  chatMessages?: boolean;
  darkMode?: boolean;
  textSize?: string;
}

export interface ActivityItem {
  id: string;
  type: 'medical-help' | 'report' | 'shelter' | 'chat' | 'help-request';
  title: string;
  subtitle: string;
  description: string;
  status: 'Resolved' | 'In Review' | 'Completed' | 'Cancelled';
  date: string;
  location: string;
  images?: string[];
}

export interface Shelter {
  id: string;
  name: string;
  area: string;
  distance: string;
  statusText: string;
  availablePercent: number;
  occupied: number;
  capacity: number;
  isFull: boolean;
  amenities: string[];
  imageUrl: string;
  lat: number;
  lng: number;
}

export interface Hospital {
  id: string;
  name: string;
  area: string;
  distance: string;
  tags: string;
  isOperational: boolean;
  crowdLevel: 'Low Crowd' | 'Moderate Crowd' | 'High Crowd';
  phone: string;
  imageUrl: string;
  lat: number;
  lng: number;
}

export interface DisasterAlert {
  id: string;
  type: 'flood' | 'fire' | 'storm' | 'landslide';
  title: string;
  description: string;
  riskLevel: 'High Risk' | 'Moderate Risk' | 'Low Risk';
  distance: string;
  timeAgo: string;
}

export interface ChatMessage {
  id: string;
  sender: string;
  senderRole: 'rescue' | 'user' | 'volunteer' | 'citizen' | 'responder';
  message?: string;
  text?: string;
  timestamp?: string;
  time?: string;
  isMe?: boolean;
}
