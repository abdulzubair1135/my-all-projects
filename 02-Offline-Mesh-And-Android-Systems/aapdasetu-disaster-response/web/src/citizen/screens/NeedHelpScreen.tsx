import React, { useState } from 'react';
import {
  ArrowLeft,
  MapPin,
  Waves,
  Flame,
  CloudLightning,
  Mountain,
  MoreHorizontal,
  Plus,
  Utensils,
  Home,
  Droplets,
  Pill,
  Users,
  Phone,
  Crosshair,
  MessageSquare,
  Camera,
  Video,
  Send,
  CheckCircle2,
} from 'lucide-react';
import { ActivityItem } from '../types';
import { api } from '../../services/api';

interface NeedHelpScreenProps {
  onBack: () => void;
  onSubmitHelpRequest: (newActivity: ActivityItem) => void;
}

export const NeedHelpScreen: React.FC<NeedHelpScreenProps> = ({ onBack, onSubmitHelpRequest }) => {
  const [selectedDisaster, setSelectedDisaster] = useState<string>('Flood');
  const [selectedHelp, setSelectedHelp] = useState<string[]>(['Medical Help']);
  const [locationText, setLocationText] = useState('Sarkhej - Gandhinagar Hwy, Ahmedabad, Gujarat 380015');
  const [details, setDetails] = useState('');
  const [photosCount, setPhotosCount] = useState(0);
  const [videosCount, setVideosCount] = useState(0);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const toggleHelp = (item: string) => {
    if (selectedHelp.includes(item)) {
      setSelectedHelp(selectedHelp.filter((h) => h !== item));
    } else {
      setSelectedHelp([...selectedHelp, item]);
    }
  };

  const handleUpdateLocation = () => {
    // Simulate high precision GPS update
    setLocationText('SG Highway, Bodakdev, Ahmedabad, Gujarat 380054 (GPS Lat 23.039, Long 72.508)');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newActivity: ActivityItem = {
      id: `help-${Date.now()}`,
      type: 'help-request',
      title: `${selectedDisaster} Assistance Request`,
      subtitle: selectedHelp.join(', ') || 'General Relief',
      description: details || 'Urgent assistance requested for disaster affected location.',
      status: 'In Review',
      date: 'Just now',
      location: locationText.split(',')[0] + ', Ahmedabad',
    };
    onSubmitHelpRequest(newActivity);
    setIsSubmitted(true);

    api.createSOS({
      originDeviceId: 'WEB_NEED_HELP_' + Math.floor(1000 + Math.random() * 9000),
      userName: 'Citizen (Aid Request)',
      userPhone: '9876543210',
      type: 'TRAPPED',
      severity: 'HIGH',
      description: `[NGO & RESCUE] ${selectedDisaster} Request: ${selectedHelp.join(', ')} - ${details || 'Urgent aid required'}`,
      peopleCount: 1,
      injuredCount: 0,
      latitude: 23.0395,
      longitude: 72.5082,
      accuracy: 10,
      addressText: locationText,
      source: 'ONLINE',
    }).catch((err) => console.error('Error dispatching help request:', err));
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-white select-none">
      {/* Top Navigation Header */}
      <header className="px-5 pt-2 pb-2 bg-white flex items-center justify-between z-20 shrink-0">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go back"
          className="w-9 h-9 flex items-center justify-start text-gray-900 text-xl active:scale-95 transition-transform"
        >
          <ArrowLeft className="w-6 h-6 stroke-[2.5]" />
        </button>
        <div className="text-center flex-1 px-2">
          <h1 className="text-xl font-extrabold text-gray-900 leading-tight">I Need Help</h1>
        </div>
        <div className="w-9 h-9 flex items-center justify-end">
          <div className="w-9 h-9 rounded-full bg-red-50 flex items-center justify-center text-red-600 text-base shadow-xs">
            <MapPin className="w-4 h-4 fill-red-600" />
          </div>
        </div>
      </header>

      {/* Subtitle Description */}
      <div className="px-7 pb-2.5 text-center bg-white border-b border-gray-50 shrink-0">
        <p className="text-xs text-gray-500 leading-relaxed font-normal">
          Tell us about the disaster and the help you need.
          <br />
          We'll alert the nearest rescue teams.
        </p>
      </div>

      {/* Scrollable Form Content */}
      <main className="flex-1 overflow-y-auto px-5 py-3 space-y-4 no-scrollbar pb-24">
        {/* Section 1: Type of Disaster */}
        <section data-purpose="disaster-type-selector">
          <div className="mb-2">
            <h2 className="text-sm font-bold text-gray-900">Type of Disaster</h2>
            <p className="text-[11px] text-gray-500">Select the current situation in your area</p>
          </div>
          <div className="grid grid-cols-5 gap-2">
            {/* Flood */}
            <button
              type="button"
              onClick={() => setSelectedDisaster('Flood')}
              className={`flex flex-col items-center justify-center h-20 rounded-xl border transition-all p-1 text-center ${
                selectedDisaster === 'Flood'
                  ? 'border-red-600 bg-red-50 text-red-600 shadow-xs'
                  : 'border-gray-100 bg-gray-50/50 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <Waves className={`w-5 h-5 mb-1 ${selectedDisaster === 'Flood' ? 'text-red-600' : 'text-slate-700'}`} />
              <span className="text-[11px] font-semibold leading-tight">Flood</span>
            </button>

            {/* Fire */}
            <button
              type="button"
              onClick={() => setSelectedDisaster('Fire')}
              className={`flex flex-col items-center justify-center h-20 rounded-xl border transition-all p-1 text-center ${
                selectedDisaster === 'Fire'
                  ? 'border-red-600 bg-red-50 text-red-600 shadow-xs'
                  : 'border-gray-100 bg-gray-50/50 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <Flame className={`w-5 h-5 mb-1 ${selectedDisaster === 'Fire' ? 'text-red-600' : 'text-slate-700'}`} />
              <span className="text-[11px] font-semibold leading-tight">Fire</span>
            </button>

            {/* Storm / Cyclone */}
            <button
              type="button"
              onClick={() => setSelectedDisaster('Storm')}
              className={`flex flex-col items-center justify-center h-20 rounded-xl border transition-all p-1 text-center ${
                selectedDisaster === 'Storm'
                  ? 'border-red-600 bg-red-50 text-red-600 shadow-xs'
                  : 'border-gray-100 bg-gray-50/50 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <CloudLightning className={`w-5 h-5 mb-1 ${selectedDisaster === 'Storm' ? 'text-red-600' : 'text-slate-700'}`} />
              <span className="text-[10px] font-semibold leading-tight">Storm /<br />Cyclone</span>
            </button>

            {/* Landslide */}
            <button
              type="button"
              onClick={() => setSelectedDisaster('Landslide')}
              className={`flex flex-col items-center justify-center h-20 rounded-xl border transition-all p-1 text-center ${
                selectedDisaster === 'Landslide'
                  ? 'border-red-600 bg-red-50 text-red-600 shadow-xs'
                  : 'border-gray-100 bg-gray-50/50 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <Mountain className={`w-5 h-5 mb-1 ${selectedDisaster === 'Landslide' ? 'text-red-600' : 'text-amber-800'}`} />
              <span className="text-[11px] font-semibold leading-tight">Landslide</span>
            </button>

            {/* Other */}
            <button
              type="button"
              onClick={() => setSelectedDisaster('Other')}
              className={`flex flex-col items-center justify-center h-20 rounded-xl border transition-all p-1 text-center ${
                selectedDisaster === 'Other'
                  ? 'border-red-600 bg-red-50 text-red-600 shadow-xs'
                  : 'border-gray-100 bg-gray-50/50 hover:bg-gray-50 text-gray-700'
              }`}
            >
              <MoreHorizontal className={`w-5 h-5 mb-1 ${selectedDisaster === 'Other' ? 'text-red-600' : 'text-slate-600'}`} />
              <span className="text-[11px] font-semibold leading-tight">Other</span>
            </button>
          </div>
        </section>

        {/* Section 2: What kind of help do you need? */}
        <section data-purpose="help-type-selector">
          <div className="mb-2">
            <h2 className="text-sm font-bold text-gray-900">What kind of help do you need?</h2>
            <p className="text-[11px] text-gray-500">Select all that apply</p>
          </div>
          <div className="grid grid-cols-4 gap-2">
            {[
              { id: 'Medical Help', label: 'Medical Help', icon: Plus, iconColor: 'text-red-600' },
              { id: 'Food', label: 'Food', icon: Utensils, iconColor: 'text-slate-700' },
              { id: 'Shelter', label: 'Shelter', icon: Home, iconColor: 'text-slate-700' },
              { id: 'Drinking Water', label: 'Drinking Water', icon: Droplets, iconColor: 'text-slate-700' },
              { id: 'Medicine', label: 'Medicine', icon: Pill, iconColor: 'text-slate-700' },
              { id: 'Rescue / Evacuation', label: 'Rescue /\nEvacuation', icon: Users, iconColor: 'text-slate-700' },
              { id: 'Communication Support', label: 'Communication\nSupport', icon: Phone, iconColor: 'text-slate-700' },
              { id: 'Other', label: 'Other', icon: MoreHorizontal, iconColor: 'text-slate-700' },
            ].map((item) => {
              const IconComp = item.icon;
              const isSelected = selectedHelp.includes(item.id);
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => toggleHelp(item.id)}
                  className={`flex flex-col items-center justify-center h-[76px] rounded-xl border p-1 text-center transition-all ${
                    isSelected
                      ? 'border-red-600 bg-red-50 text-red-600 shadow-xs'
                      : 'border-gray-100 bg-gray-50/50 hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <IconComp className={`w-5 h-5 mb-1 ${isSelected ? 'text-red-600 stroke-[2.5]' : item.iconColor}`} />
                  <span className="text-[10px] font-semibold leading-tight whitespace-pre-line">{item.label}</span>
                </button>
              );
            })}
          </div>
        </section>

        {/* Section 3: Your Current Location */}
        <section data-purpose="current-location-banner">
          <h2 className="text-sm font-bold text-gray-900 mb-1.5">Your Current Location</h2>
          <div className="flex items-center justify-between p-3 rounded-xl border border-gray-200 bg-white shadow-xs">
            <div className="flex items-center space-x-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-full bg-red-100/70 shrink-0 flex items-center justify-center text-red-600 text-sm">
                <MapPin className="w-4 h-4 fill-red-600" />
              </div>
              <div className="text-left leading-snug">
                <p className="text-xs font-semibold text-gray-800 truncate max-w-[170px]">
                  {locationText.split(',')[0]}
                </p>
                <p className="text-[11px] text-gray-500 truncate max-w-[170px]">
                  {locationText.split(',').slice(1).join(',')}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleUpdateLocation}
              className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-red-50 text-red-600 text-[11px] font-semibold border border-red-100 active:scale-95 transition-transform shrink-0"
            >
              <Crosshair className="w-3.5 h-3.5" />
              <span>Update Location</span>
            </button>
          </div>
        </section>

        {/* Section 4: Additional Details (Optional) */}
        <section data-purpose="additional-details-form">
          <h2 className="text-sm font-bold text-gray-900 mb-1.5">
            Additional Details <span className="text-gray-400 font-normal text-xs">(Optional)</span>
          </h2>
          <div className="relative rounded-xl border border-gray-200 p-3 bg-white focus-within:border-red-500 focus-within:ring-1 focus-within:ring-red-500">
            <div className="flex items-start space-x-2.5">
              <MessageSquare className="w-4 h-4 text-gray-400 mt-1 shrink-0" />
              <textarea
                value={details}
                onChange={(e) => setDetails(e.target.value.slice(0, 300))}
                className="w-full border-0 p-0 text-xs text-gray-800 placeholder-gray-400 focus:ring-0 focus:outline-none resize-none font-normal leading-relaxed"
                placeholder="Share any additional information (e.g. number of people, special requirements, nearby landmarks)"
                rows={3}
              />
            </div>
            <div className="text-right text-[11px] text-gray-400 mt-1 select-none">
              {details.length}/300
            </div>
          </div>

          {/* Attachment Buttons */}
          <div className="grid grid-cols-2 gap-3 mt-2.5">
            <button
              type="button"
              onClick={() => setPhotosCount((c) => c + 1)}
              className="flex items-center justify-center space-x-2 h-11 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 active:scale-[0.98] transition"
            >
              <Camera className="w-4 h-4 text-slate-500" />
              <span className="text-xs font-medium text-gray-700">
                {photosCount > 0 ? `${photosCount} Photo(s) Attached` : 'Add Photo (Optional)'}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setVideosCount((c) => c + 1)}
              className="flex items-center justify-center space-x-2 h-11 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 active:scale-[0.98] transition"
            >
              <Video className="w-4 h-4 text-slate-500" />
              <span className="text-xs font-medium text-gray-700">
                {videosCount > 0 ? `${videosCount} Video(s) Attached` : 'Add Video (Optional)'}
              </span>
            </button>
          </div>
        </section>

        {/* Submit CTA */}
        <section className="pt-2 pb-1" data-purpose="submit-action">
          <button
            type="button"
            onClick={handleSubmit}
            className="w-full bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold py-3.5 px-4 rounded-xl shadow-md shadow-red-200 flex items-center justify-center space-x-2.5 transition active:scale-[0.99]"
          >
            <Send className="w-4 h-4" />
            <span className="tracking-wide text-xs uppercase font-extrabold">Send Help Request</span>
          </button>
        </section>
      </main>

      {/* Confirmation Modal */}
      {isSubmitted && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-xs w-full text-center shadow-2xl border border-slate-100">
            <div className="w-14 h-14 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Help Request Dispatched</h3>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Your SOS alert for <strong>{selectedDisaster}</strong> has been transmitted to Gujarat State Disaster Management & nearby emergency squads.
            </p>
            <div className="bg-slate-50 p-3 rounded-xl my-3 text-[11px] text-slate-600 text-left border border-slate-100 space-y-1">
              <div><strong>Ticket ID:</strong> SOS-AHM-{Math.floor(100000 + Math.random() * 900000)}</div>
              <div><strong>ETA:</strong> 8 - 14 minutes</div>
              <div><strong>Dispatched Unit:</strong> Team Alpha-3 (Memnagar Station)</div>
            </div>
            <button
              type="button"
              onClick={() => {
                setIsSubmitted(false);
                onBack();
              }}
              className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-md"
            >
              View in Activity History
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
