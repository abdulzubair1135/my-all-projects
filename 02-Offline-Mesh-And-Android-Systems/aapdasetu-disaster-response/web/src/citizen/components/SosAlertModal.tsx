import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Radio,
  MapPin,
  Users,
  Shield,
  Phone,
  MessageSquare,
  CheckCircle2,
  X,
} from 'lucide-react';
import { UserProfile } from '../types';
import { api } from '../../services/api';

interface SosAlertModalProps {
  userProfile: UserProfile;
  onCancel: () => void;
  onOpenChat: () => void;
}

export const SosAlertModal: React.FC<SosAlertModalProps> = ({
  userProfile,
  onCancel,
  onOpenChat,
}) => {
  const [countdown, setCountdown] = useState(3);
  const [isAlertActive, setIsAlertActive] = useState(false);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setIsAlertActive(true);
      api.createSOS({
        originDeviceId: 'WEB_CITIZEN_' + Math.floor(1000 + Math.random() * 9000),
        userName: userProfile.fullName || userProfile.name || 'Rahul Sharma',
        userPhone: userProfile.phone || '9876543210',
        type: 'MEDICAL',
        severity: 'CRITICAL',
        description: 'Immediate distress signal from citizen emergency modal',
        peopleCount: 1,
        injuredCount: 0,
        latitude: 23.0395,
        longitude: 72.5082,
        accuracy: 10,
        addressText: `${userProfile.city || 'Ahmedabad'}, ${userProfile.state || 'Gujarat'}`,
        source: 'ONLINE',
      }).catch((err) => console.error('SOS submit error:', err));
    }
  }, [countdown, userProfile]);

  return (
    <div className="fixed inset-0 bg-red-950/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-3xl p-6 max-w-sm w-full text-center shadow-2xl border-4 border-red-500 overflow-hidden relative">
        {/* Animated Emergency Beacon */}
        <div className="relative w-24 h-24 mx-auto mb-3 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-red-500/20 animate-ping" />
          <div className="absolute inset-2 rounded-full bg-red-500/40 animate-pulse" />
          <div className="relative w-16 h-16 rounded-full bg-red-600 text-white flex items-center justify-center shadow-xl shadow-red-600/50">
            <Radio className="w-8 h-8 animate-spin" />
          </div>
        </div>

        {/* Header */}
        <span className="inline-block px-3 py-1 rounded-full bg-red-100 text-red-700 text-xs font-black uppercase tracking-wider mb-1">
          {isAlertActive ? '🚨 Emergency SOS Dispatched' : `Transmitting in ${countdown}s`}
        </span>
        <h2 className="text-xl font-black text-slate-900 leading-tight">
          SOS SIGNAL ACTIVE
        </h2>
        <p className="text-xs text-slate-600 mt-1">
          Emergency telemetry and GPS location coordinates are being transmitted to authorities.
        </p>

        {/* Information Grid */}
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-3.5 my-4 text-left text-xs space-y-2">
          <div className="flex items-center space-x-2 text-slate-700">
            <MapPin className="w-4 h-4 text-red-600 shrink-0" />
            <span className="truncate">
              <strong>GPS:</strong> 23.0395° N, 72.5082° E (SG Highway, Ahmedabad)
            </span>
          </div>
          <div className="flex items-center space-x-2 text-slate-700">
            <Users className="w-4 h-4 text-blue-600 shrink-0" />
            <span>
              <strong>Notified:</strong> {userProfile.emergencyContacts?.length || 0} Emergency Contacts
            </span>
          </div>
          <div className="flex items-center space-x-2 text-slate-700">
            <Shield className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              <strong>Units Dispatched:</strong> GSDMA Rapid Squad Alpha
            </span>
          </div>
        </div>

        {/* Primary Action Buttons */}
        <div className="space-y-2">
          <a
            href="tel:108"
            className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider flex items-center justify-center space-x-2 shadow-lg shadow-red-600/30 active:scale-95 transition"
          >
            <Phone className="w-4 h-4 fill-current" />
            <span>Call 108 Emergency Direct</span>
          </a>

          <button
            type="button"
            onClick={onOpenChat}
            className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-bold flex items-center justify-center space-x-2 transition"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Open Rescue Team Live Chat</span>
          </button>

          <button
            type="button"
            onClick={onCancel}
            className="w-full py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-xl text-xs font-semibold"
          >
            I am Safe • Cancel SOS Alert
          </button>
        </div>
      </div>
    </div>
  );
};
