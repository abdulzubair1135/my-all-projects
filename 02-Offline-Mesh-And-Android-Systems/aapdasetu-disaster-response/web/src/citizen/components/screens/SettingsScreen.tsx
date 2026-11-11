import React, { useState, useRef } from 'react';
import {
  User,
  Phone,
  Droplets,
  Plus,
  Bell,
  Volume2,
  MapPin,
  WifiOff,
  Map,
  Share2,
  Globe,
  HelpCircle,
  BookOpen,
  Shield,
  FileText,
  LogOut,
  ChevronRight,
  Edit2,
  Check,
  Camera,
  Upload,
  Trash2,
  X,
  Image as ImageIcon,
} from 'lucide-react';
import { UserProfile } from '../../types';

interface SettingsScreenProps {
  userProfile: UserProfile;
  onUpdateProfile: (updated: Partial<UserProfile>) => void;
  onSignOut: () => void;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({
  userProfile,
  onUpdateProfile,
  onSignOut,
}) => {
  const [emergencyAlerts, setEmergencyAlerts] = useState(true);
  const [soundVibration, setSoundVibration] = useState(true);
  const [locationAlerts, setLocationAlerts] = useState(true);
  const [offlineMode, setOfflineMode] = useState(true);
  const [offlineMapsDownloaded, setOfflineMapsDownloaded] = useState(true);
  const [meshNetworking, setMeshNetworking] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState(userProfile.language || 'English');
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [showAddContactModal, setShowAddContactModal] = useState(false);
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [newContactName, setNewContactName] = useState('');
  const [newContactPhone, setNewContactPhone] = useState('');
  const [newContactRelation, setNewContactRelation] = useState('');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editName, setEditName] = useState(userProfile.name);
  const [editPhone, setEditPhone] = useState(userProfile.phone);
  const [editBloodGroup, setEditBloodGroup] = useState(userProfile.bloodGroup);

  const presetAvatars = [
    { id: '1', label: 'Default', url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80' },
    { id: '2', label: 'Citizen (Male)', url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80' },
    { id: '3', label: 'Citizen (Female)', url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&auto=format&fit=crop&q=80' },
    { id: '4', label: 'Volunteer', url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80' },
    { id: '5', label: 'Emergency Officer', url: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&auto=format&fit=crop&q=80' },
    { id: '6', label: 'Paramedic', url: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80' },
  ];

  const handleImageFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file');
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      if (base64) {
        onUpdateProfile({ avatarUrl: base64 });
        setShowPhotoModal(false);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleSelectPresetAvatar = (url: string) => {
    onUpdateProfile({ avatarUrl: url });
    setShowPhotoModal(false);
  };

  const handleRemovePhoto = () => {
    onUpdateProfile({ avatarUrl: '' });
    setShowPhotoModal(false);
  };

  const handleSaveProfile = () => {
    onUpdateProfile({
      name: editName,
      phone: editPhone,
      bloodGroup: editBloodGroup,
    });
    setIsEditingProfile(false);
  };

  const handleAddContact = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContactName || !newContactPhone) return;
    const newContact = {
      id: `contact-${Date.now()}`,
      name: newContactName,
      relation: newContactRelation || 'Emergency Contact',
      phone: newContactPhone,
    };
    onUpdateProfile({
      emergencyContacts: [...(userProfile.emergencyContacts || []), newContact],
    });
    setNewContactName('');
    setNewContactPhone('');
    setNewContactRelation('');
    setShowAddContactModal(false);
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#F8FAFC] select-none">
      {/* Top Header */}
      <div className="px-5 pt-3 pb-3 bg-white border-b border-slate-100 text-center shrink-0">
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Settings</h1>
        <p className="text-xs text-slate-500 mt-0.5 font-normal">
          Manage preferences, notifications and emergency setup
        </p>
      </div>

      {/* Scrollable Content */}
      <main className="flex-1 px-4 py-3 space-y-4 overflow-y-auto pb-24 no-scrollbar text-left">
        {/* Profile Card */}
        <section className="bg-white rounded-2xl p-4 shadow-xs border border-slate-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3.5">
              {/* Profile Picture with Camera Icon Overlay */}
              <div className="relative group shrink-0">
                <button
                  type="button"
                  onClick={() => setShowPhotoModal(true)}
                  className="w-16 h-16 rounded-full overflow-hidden border-2 border-slate-100 shadow-sm bg-slate-100 flex items-center justify-center hover:opacity-95 transition-all cursor-pointer relative"
                  title="Profile picture badle (Change photo)"
                  aria-label="Profile picture badle"
                >
                  {userProfile.avatarUrl ? (
                    <img
                      alt={userProfile.name}
                      src={userProfile.avatarUrl}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="w-8 h-8 text-slate-400" />
                  )}
                  {/* Subtle hover shade with camera icon */}
                  <div className="absolute inset-0 bg-black/25 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white">
                    <Camera className="w-5 h-5 drop-shadow" />
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setShowPhotoModal(true)}
                  className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center shadow-md border-2 border-white transition-transform active:scale-95 cursor-pointer"
                  title="Add/Change Profile Picture"
                  aria-label="Add/Change Profile Picture"
                >
                  <Camera className="w-3.5 h-3.5" />
                </button>
              </div>

              <div>
                <h2 className="text-sm font-bold text-slate-900">{userProfile.name}</h2>
                <p className="text-xs text-slate-500">{userProfile.phone}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-red-50 text-red-600 text-[10px] font-semibold">
                    <Droplets className="w-3 h-3 fill-current" />
                    <span>Blood Group: {userProfile.bloodGroup}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowPhotoModal(true)}
                    className="text-[10px] font-bold text-red-600 hover:text-red-700 hover:underline flex items-center gap-0.5 cursor-pointer"
                  >
                    <span>Change Photo</span>
                  </button>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setIsEditingProfile(true)}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-xl cursor-pointer"
              title="Edit Profile"
              aria-label="Edit Profile"
            >
              <Edit2 className="w-4 h-4" />
            </button>
          </div>
        </section>

        {/* Emergency Contacts Section */}
        <section className="space-y-2">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Emergency Contacts</h3>
            <span className="text-[11px] text-slate-400">{(userProfile.emergencyContacts || []).length} Contacts</span>
          </div>

          <div className="space-y-2">
            {(userProfile.emergencyContacts || []).map((contact) => (
              <div
                key={contact.id}
                className="bg-white rounded-2xl p-3 shadow-xs border border-slate-100 flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{contact.name}</h4>
                    <p className="text-[11px] text-slate-500">{contact.phone} • {contact.relation}</p>
                  </div>
                </div>

                <a
                  href={`tel:${contact.phone}`}
                  className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center hover:bg-emerald-100"
                >
                  <Phone className="w-4 h-4 fill-current" />
                </a>
              </div>
            ))}

            <button
              type="button"
              onClick={() => setShowAddContactModal(true)}
              className="w-full py-2.5 rounded-2xl border border-dashed border-red-300 bg-red-50/50 text-red-600 text-xs font-bold flex items-center justify-center space-x-1.5 hover:bg-red-50 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Emergency Contact</span>
            </button>
          </div>
        </section>

        {/* Notifications & Alerts */}
        <section className="space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider px-1">Notifications & Alerts</h3>
          <div className="bg-white rounded-2xl p-3 shadow-xs border border-slate-100 divide-y divide-slate-100">
            {/* Emergency Alerts */}
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Bell className="w-4 h-4 text-slate-600" />
                <div>
                  <div className="text-xs font-semibold text-slate-900">Government Emergency Alerts</div>
                  <div className="text-[10px] text-slate-500">Receive critical life safety broadcasts</div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEmergencyAlerts(!emergencyAlerts)}
                className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                  emergencyAlerts ? 'bg-red-600 justify-end' : 'bg-slate-200 justify-start'
                }`}
              >
                <div className="bg-white w-4 h-4 rounded-full shadow-md" />
              </button>
            </div>

            {/* Sound & Vibration */}
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Volume2 className="w-4 h-4 text-slate-600" />
                <div>
                  <div className="text-xs font-semibold text-slate-900">Sound & Loud Siren</div>
                  <div className="text-[10px] text-slate-500">Override silent mode on high alert</div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSoundVibration(!soundVibration)}
                className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                  soundVibration ? 'bg-red-600 justify-end' : 'bg-slate-200 justify-start'
                }`}
              >
                <div className="bg-white w-4 h-4 rounded-full shadow-md" />
              </button>
            </div>

            {/* Location Alerts */}
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <MapPin className="w-4 h-4 text-slate-600" />
                <div>
                  <div className="text-xs font-semibold text-slate-900">Location-Based Warnings</div>
                  <div className="text-[10px] text-slate-500">Auto-filter alerts for your immediate radius</div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setLocationAlerts(!locationAlerts)}
                className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                  locationAlerts ? 'bg-red-600 justify-end' : 'bg-slate-200 justify-start'
                }`}
              >
                <div className="bg-white w-4 h-4 rounded-full shadow-md" />
              </button>
            </div>
          </div>
        </section>

        {/* Offline & Connectivity */}
        <section className="space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider px-1">Offline & Connectivity</h3>
          <div className="bg-white rounded-2xl p-3 shadow-xs border border-slate-100 divide-y divide-slate-100">
            {/* Offline Mode */}
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <WifiOff className="w-4 h-4 text-slate-600" />
                <div>
                  <div className="text-xs font-semibold text-slate-900">Offline Standby Cache</div>
                  <div className="text-[10px] text-slate-500">Store crucial emergency contacts & guides locally</div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setOfflineMode(!offlineMode)}
                className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                  offlineMode ? 'bg-red-600 justify-end' : 'bg-slate-200 justify-start'
                }`}
              >
                <div className="bg-white w-4 h-4 rounded-full shadow-md" />
              </button>
            </div>

            {/* Offline Maps */}
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Map className="w-4 h-4 text-slate-600" />
                <div>
                  <div className="text-xs font-semibold text-slate-900">Offline Ahmedabad Map</div>
                  <div className="text-[10px] text-slate-500">
                    {offlineMapsDownloaded ? 'Downloaded (240 MB)' : 'Download for offline use'}
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setOfflineMapsDownloaded(!offlineMapsDownloaded)}
                className={`px-3 py-1 rounded-lg text-[11px] font-bold ${
                  offlineMapsDownloaded ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700'
                }`}
              >
                {offlineMapsDownloaded ? 'Saved' : 'Download'}
              </button>
            </div>

            {/* Mesh Networking */}
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <Share2 className="w-4 h-4 text-slate-600" />
                <div>
                  <div className="text-xs font-semibold text-slate-900">Bluetooth Mesh Relay</div>
                  <div className="text-[10px] text-slate-500">Relay SOS alerts peer-to-peer without towers</div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setMeshNetworking(!meshNetworking)}
                className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                  meshNetworking ? 'bg-red-600 justify-end' : 'bg-slate-200 justify-start'
                }`}
              >
                <div className="bg-white w-4 h-4 rounded-full shadow-md" />
              </button>
            </div>
          </div>
        </section>

        {/* Language & Region */}
        <section className="space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider px-1">Language & Region</h3>
          <div className="bg-white rounded-2xl p-3 shadow-xs border border-slate-100 divide-y divide-slate-100">
            <button
              type="button"
              onClick={() => setShowLanguageModal(true)}
              className="w-full flex items-center justify-between py-2 hover:bg-slate-50"
            >
              <div className="flex items-center space-x-3">
                <Globe className="w-4 h-4 text-slate-600" />
                <div className="text-left">
                  <div className="text-xs font-semibold text-slate-900">Display Language</div>
                  <div className="text-[10px] text-slate-500">{selectedLanguage}</div>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </button>

            <div className="flex items-center justify-between py-2">
              <div className="flex items-center space-x-3">
                <MapPin className="w-4 h-4 text-slate-600" />
                <div className="text-left">
                  <div className="text-xs font-semibold text-slate-900">Current Disaster Region</div>
                  <div className="text-[10px] text-slate-500">Ahmedabad, Gujarat (GSDMA Node)</div>
                </div>
              </div>
              <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">
                Active
              </span>
            </div>
          </div>
        </section>

        {/* Support & Legal */}
        <section className="space-y-2">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider px-1">Support & Legal</h3>
          <div className="bg-white rounded-2xl p-3 shadow-xs border border-slate-100 divide-y divide-slate-100">
            <div className="flex items-center justify-between py-2 cursor-pointer hover:bg-slate-50">
              <div className="flex items-center space-x-3">
                <HelpCircle className="w-4 h-4 text-slate-600" />
                <span className="text-xs font-semibold text-slate-900">Help & FAQs</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </div>

            <div className="flex items-center justify-between py-2 cursor-pointer hover:bg-slate-50">
              <div className="flex items-center space-x-3">
                <BookOpen className="w-4 h-4 text-slate-600" />
                <span className="text-xs font-semibold text-slate-900">Disaster Survival Guidelines</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </div>

            <div className="flex items-center justify-between py-2 cursor-pointer hover:bg-slate-50">
              <div className="flex items-center space-x-3">
                <Shield className="w-4 h-4 text-slate-600" />
                <span className="text-xs font-semibold text-slate-900">Privacy & Data Protection</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </div>

            <div className="flex items-center justify-between py-2 cursor-pointer hover:bg-slate-50">
              <div className="flex items-center space-x-3">
                <FileText className="w-4 h-4 text-slate-600" />
                <span className="text-xs font-semibold text-slate-900">Terms of Emergency Service</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </div>
          </div>
        </section>

        {/* Sign Out Button */}
        <div className="pt-2">
          <button
            type="button"
            onClick={onSignOut}
            className="w-full py-3 rounded-2xl border border-red-200 bg-white hover:bg-red-50 text-red-600 text-xs font-bold flex items-center justify-center space-x-2 transition-colors shadow-xs"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>

        {/* App Version Info */}
        <div className="text-center text-[10px] text-slate-400 py-2">
          Disaster Response & Emergency SOS • v2.4.1 (Build 890)
          <br />
          Integrated with Gujarat State Disaster Management Authority
        </div>
      </main>

      {/* Language Selector Modal */}
      {showLanguageModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-xs w-full text-left shadow-2xl border border-slate-100">
            <h3 className="text-base font-bold text-slate-900 mb-3">Choose Language</h3>
            <div className="space-y-1.5">
              {[
                { name: 'English', native: 'English' },
                { name: 'Gujarati', native: 'ગુજરાતી' },
                { name: 'Hindi', native: 'हिन्दी' },
              ].map((lang) => (
                <button
                  key={lang.name}
                  type="button"
                  onClick={() => {
                    setSelectedLanguage(lang.name);
                    onUpdateProfile({ language: lang.name });
                    setShowLanguageModal(false);
                  }}
                  className={`w-full flex items-center justify-between p-3 rounded-xl border text-xs font-semibold ${
                    selectedLanguage === lang.name
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <span>{lang.name} ({lang.native})</span>
                  {selectedLanguage === lang.name && <Check className="w-4 h-4 text-red-600" />}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setShowLanguageModal(false)}
              className="mt-4 w-full py-2.5 bg-slate-100 text-slate-700 font-semibold text-xs rounded-xl"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Add Emergency Contact Modal */}
      {showAddContactModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full text-left shadow-2xl border border-slate-100">
            <h3 className="text-base font-bold text-slate-900">Add Emergency Contact</h3>
            <p className="text-xs text-slate-500 mt-0.5 mb-4">
              This person will receive immediate SOS alerts with your GPS location.
            </p>

            <form onSubmit={handleAddContact} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={newContactName}
                  onChange={(e) => setNewContactName(e.target.value)}
                  placeholder="e.g. Ramesh Patel"
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-red-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Phone Number</label>
                <input
                  type="tel"
                  required
                  value={newContactPhone}
                  onChange={(e) => setNewContactPhone(e.target.value)}
                  placeholder="+91 98765 00000"
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-red-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Relationship</label>
                <input
                  type="text"
                  value={newContactRelation}
                  onChange={(e) => setNewContactRelation(e.target.value)}
                  placeholder="e.g. Father, Neighbor, Doctor"
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-red-500"
                />
              </div>

              <div className="flex space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddContactModal(false)}
                  className="flex-1 py-2.5 bg-slate-100 text-slate-700 font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-red-600 text-white font-bold rounded-xl shadow-md"
                >
                  Save Contact
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Profile Modal */}
      {isEditingProfile && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full text-left shadow-2xl border border-slate-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-base font-bold text-slate-900">Edit Profile</h3>
              <button
                type="button"
                onClick={() => setIsEditingProfile(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Profile Avatar Quick Change */}
            <div className="flex items-center space-x-3 p-3 mb-3 bg-slate-50 rounded-2xl border border-slate-100">
              <div className="w-12 h-12 rounded-full overflow-hidden bg-slate-200 shrink-0 border border-slate-200">
                {userProfile.avatarUrl ? (
                  <img
                    src={userProfile.avatarUrl}
                    alt={userProfile.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-400">
                    <User className="w-6 h-6" />
                  </div>
                )}
              </div>
              <div className="flex-1">
                <span className="text-xs font-semibold text-slate-700 block">Profile Picture</span>
                <button
                  type="button"
                  onClick={() => setShowPhotoModal(true)}
                  className="text-xs font-bold text-red-600 hover:text-red-700 flex items-center gap-1 mt-0.5 cursor-pointer"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Change Photo</span>
                </button>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-red-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={editPhone}
                  onChange={(e) => setEditPhone(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-red-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Blood Group</label>
                <select
                  value={editBloodGroup}
                  onChange={(e) => setEditBloodGroup(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-red-500 bg-white"
                >
                  {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map((bg) => (
                    <option key={bg} value={bg}>{bg}</option>
                  ))}
                </select>
              </div>

              <div className="flex space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsEditingProfile(false)}
                  className="flex-1 py-2.5 bg-slate-100 text-slate-700 font-semibold rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveProfile}
                  className="flex-1 py-2.5 bg-red-600 text-white font-bold rounded-xl shadow-md cursor-pointer"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Change Profile Picture Modal */}
      {showPhotoModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-3xl p-5 max-w-sm w-full text-left shadow-2xl border border-slate-100">
            {/* Hidden native file input */}
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="hidden"
              onChange={handleImageFileUpload}
            />

            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-red-50 text-red-600 flex items-center justify-center">
                  <Camera className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Profile Picture</h3>
                  <p className="text-[11px] text-slate-500">Add or choose your profile photo</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowPhotoModal(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Current Avatar Large Preview */}
            <div className="my-4 flex flex-col items-center">
              <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-slate-100 shadow-md bg-slate-100 relative group flex items-center justify-center">
                {userProfile.avatarUrl ? (
                  <img
                    src={userProfile.avatarUrl}
                    alt={userProfile.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-12 h-12 text-slate-400" />
                )}
              </div>
              <p className="text-xs font-semibold text-slate-700 mt-2">{userProfile.name}</p>
            </div>

            {/* Upload Button */}
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full py-2.5 px-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs flex items-center justify-center space-x-2 shadow-sm transition active:scale-98 cursor-pointer"
              >
                <Upload className="w-4 h-4" />
                <span>Upload from Device / Camera</span>
              </button>
            </div>

            {/* Preset Avatars Choice */}
            <div className="mt-4 pt-3 border-t border-slate-100">
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-2">
                Or Select Preset Avatar
              </span>
              <div className="grid grid-cols-3 gap-2">
                {presetAvatars.map((avatar) => {
                  const isSelected = userProfile.avatarUrl === avatar.url;
                  return (
                    <button
                      key={avatar.id}
                      type="button"
                      onClick={() => handleSelectPresetAvatar(avatar.url)}
                      className={`p-1 rounded-2xl flex flex-col items-center border transition-all cursor-pointer ${
                        isSelected
                          ? 'border-red-600 bg-red-50/50 ring-2 ring-red-500/20'
                          : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      <div className="w-11 h-11 rounded-full overflow-hidden mb-1 relative">
                        <img
                          src={avatar.url}
                          alt={avatar.label}
                          className="w-full h-full object-cover"
                        />
                        {isSelected && (
                          <div className="absolute inset-0 bg-red-600/30 flex items-center justify-center">
                            <Check className="w-4 h-4 text-white" />
                          </div>
                        )}
                      </div>
                      <span className="text-[10px] font-medium text-slate-600 truncate w-full text-center">
                        {avatar.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Footer actions: Remove / Cancel */}
            <div className="flex items-center justify-between pt-4 mt-3 border-t border-slate-100">
              {userProfile.avatarUrl ? (
                <button
                  type="button"
                  onClick={handleRemovePhoto}
                  className="text-xs font-semibold text-rose-600 hover:text-rose-700 flex items-center space-x-1 cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Remove Photo</span>
                </button>
              ) : (
                <div />
              )}
              <button
                type="button"
                onClick={() => setShowPhotoModal(false)}
                className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
