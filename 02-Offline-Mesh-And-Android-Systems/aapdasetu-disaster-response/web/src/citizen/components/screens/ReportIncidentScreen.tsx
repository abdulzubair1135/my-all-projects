import React, { useState } from 'react';
import {
  ArrowLeft,
  Camera,
  Waves,
  Flame,
  Mountain,
  CloudLightning,
  Plus,
  Construction,
  Building,
  MoreHorizontal,
  X,
  MapPin,
  Crosshair,
  Send,
  CheckCircle2,
} from 'lucide-react';
import { ActivityItem } from '../../types';
import { sampleIncidentPhotos } from '../../data/mockData';

interface ReportIncidentScreenProps {
  onBack: () => void;
  onSubmitReport: (newReport: ActivityItem) => void;
}

export const ReportIncidentScreen: React.FC<ReportIncidentScreenProps> = ({
  onBack,
  onSubmitReport,
}) => {
  const [incidentType, setIncidentType] = useState<string>('Flood');
  const [photos, setPhotos] = useState<string[]>([...sampleIncidentPhotos]);
  const [details, setDetails] = useState('');
  const [locationName, setLocationName] = useState('Vastral, Ahmedabad, Gujarat');
  const [shareCommunity, setShareCommunity] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);

  const removePhoto = (index: number) => {
    setPhotos(photos.filter((_, i) => i !== index));
  };

  const addDemoPhoto = () => {
    if (photos.length < 5) {
      setPhotos([
        ...photos,
        'https://lh3.googleusercontent.com/aida-public/AB6AXuCtZDgBeS0209kc5UesAadMslV-aHHWL25Ac4ceWzs9qoEmKfd2EVkO5QuoGRI7fiBZ1Jw2bWJjDqEPdlzi5BHeRiVp1CcBoqRRM8B7XyjBlJmE8IDnJtkk2fVW_WWMzKGFd3hiXymlAkx2zDH_0MyqLZ-K1bqcKNF5uzBdwK7Y6LOb5_6sZrAyReYOxA3uSbmApqQF7caK4Z-MfxxcclQuSxU8c6J1woAbXZ-DfgVKoP5p9f0wLU56Kw',
      ]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newActivity: ActivityItem = {
      id: `report-${Date.now()}`,
      type: 'report',
      title: 'Reported Incident',
      subtitle: incidentType,
      description: details || `Reported ${incidentType.toLowerCase()} hazard in community area.`,
      status: 'In Review',
      date: 'Just now',
      location: locationName,
      images: photos.length > 0 ? photos : undefined,
    };
    onSubmitReport(newActivity);
    setIsSuccess(true);
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-white select-none">
      {/* Top Navigation */}
      <div className="relative px-4 py-2 flex items-center justify-center border-b border-gray-100 shrink-0">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go Back"
          className="absolute left-4 p-2 text-neutral-800 hover:text-neutral-500 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2.5]" />
        </button>
        <div className="text-center">
          <h1 className="text-base font-bold text-slate-900">Report Incident</h1>
          <p className="text-xs text-slate-500 font-medium">Help others by sharing real-time information</p>
        </div>
      </div>

      {/* Scrollable Content */}
      <main className="flex-1 px-4 py-3 space-y-4 overflow-y-auto pb-24 no-scrollbar">
        {/* Notice Banner */}
        <section className="bg-red-50 border border-red-100/70 rounded-xl p-3 flex items-start space-x-3" data-purpose="awareness-banner">
          <div className="shrink-0 w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center text-white text-xs mt-0.5 shadow-xs">
            <Camera className="w-4 h-4" />
          </div>
          <div className="flex-1 text-left">
            <h2 className="text-xs font-bold text-red-600">Your report can save lives.</h2>
            <p className="text-[11px] text-slate-600 leading-tight mt-0.5">
              Share accurate information and help people in your community.
            </p>
          </div>
        </section>

        {/* 1. Select Incident Type */}
        <section className="space-y-2" data-purpose="incident-type-selection">
          <h2 className="text-xs font-bold text-slate-900">1. Select Incident Type</h2>
          <div className="grid grid-cols-4 gap-2">
            {[
              { id: 'Flood', label: 'Flood', icon: Waves, color: 'text-slate-800' },
              { id: 'Fire', label: 'Fire', icon: Flame, color: 'text-red-600' },
              { id: 'Landslide', label: 'Landslide', icon: Mountain, color: 'text-slate-700' },
              { id: 'Storm', label: 'Storm', icon: CloudLightning, color: 'text-slate-700' },
              { id: 'Medical Emergency', label: 'Medical Emergency', icon: Plus, color: 'text-red-600', isPlus: true },
              { id: 'Blocked Road', label: 'Blocked Road', icon: Construction, color: 'text-slate-700' },
              { id: 'Infrastructure Damage', label: 'Infrastructure Damage', icon: Building, color: 'text-slate-700' },
              { id: 'Other', label: 'Other', icon: MoreHorizontal, color: 'text-slate-700' },
            ].map((item) => {
              const IconComp = item.icon;
              const isSelected = incidentType === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setIncidentType(item.id)}
                  className={`flex flex-col items-center justify-center p-2.5 rounded-xl border transition-all text-center ${
                    isSelected
                      ? 'border-red-500 bg-red-50/50 shadow-xs'
                      : 'border-slate-100 bg-slate-50/70 hover:bg-slate-50'
                  }`}
                >
                  <IconComp className={`w-5 h-5 mb-1.5 ${isSelected ? 'text-red-600 stroke-[2.5]' : item.color}`} />
                  <span
                    className={`text-[10.5px] leading-tight ${
                      isSelected ? 'font-semibold text-red-600' : 'font-medium text-slate-700'
                    }`}
                  >
                    {item.label}
                  </span>
                </button>
              );
            })}
          </div>
        </section>

        {/* 2. Add Photos */}
        <section className="space-y-2" data-purpose="photo-uploader">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xs font-bold text-slate-900">
                2. Add Photos <span className="font-normal text-slate-500">(Optional)</span>
              </h2>
              <p className="text-[11px] text-slate-500">Share clear photos to help others understand the situation.</p>
            </div>
            <span className="text-[10px] text-slate-400 self-start pt-0.5">Add up to 5 photos</span>
          </div>

          <div className="flex items-center space-x-2.5 pt-1 overflow-x-auto no-scrollbar">
            {photos.map((src, idx) => (
              <div key={idx} className="relative w-24 h-20 rounded-xl overflow-hidden shadow-xs shrink-0 group">
                <img alt={`Incident proof ${idx + 1}`} src={src} className="w-full h-full object-cover" />
                <button
                  type="button"
                  onClick={() => removePhoto(idx)}
                  aria-label="Remove image"
                  className="absolute top-1 right-1 w-5 h-5 bg-slate-900/80 rounded-full flex items-center justify-center text-white text-[10px] hover:bg-slate-950 transition"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}

            {photos.length < 5 && (
              <button
                type="button"
                onClick={addDemoPhoto}
                className="w-24 h-20 border border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center text-slate-500 bg-slate-50/50 hover:bg-slate-50 transition-colors shrink-0"
              >
                <Camera className="w-4 h-4 mb-1 text-slate-600" />
                <span className="text-[10px] font-medium">Add Photo</span>
              </button>
            )}
          </div>
        </section>

        {/* 3. Add Details */}
        <section className="space-y-1.5" data-purpose="incident-details">
          <h2 className="text-xs font-bold text-slate-900">3. Add Details</h2>
          <div className="relative">
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value.slice(0, 500))}
              className="w-full rounded-xl border border-slate-200 p-3 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-red-500 focus:border-red-500 resize-none font-normal"
              rows={3}
              placeholder="Describe what's happening..."
            />
            <span className="absolute bottom-2.5 right-3 text-[10px] text-slate-400 select-none">
              {details.length}/500
            </span>
          </div>
        </section>

        {/* 4. Set Location */}
        <section className="space-y-2" data-purpose="location-details">
          <h2 className="text-xs font-bold text-slate-900">4. Set Location</h2>
          <div className="p-3 bg-white border border-slate-100 shadow-xs rounded-xl flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <MapPin className="w-5 h-5 text-red-600 fill-red-600" />
              <div className="text-left">
                <div className="text-xs font-semibold text-slate-900">Current Location</div>
                <div className="text-[11px] text-slate-500">{locationName}</div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setLocationName('Memnagar Underpass, Ahmedabad, Gujarat')}
              className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-[11px] font-medium flex items-center space-x-1 transition-colors"
            >
              <Crosshair className="w-3 h-3" />
              <span>Change Location</span>
            </button>
          </div>
        </section>

        {/* Community Consent */}
        <section className="bg-red-50/60 border border-red-100 rounded-xl p-3 flex items-start space-x-2.5" data-purpose="privacy-options">
          <div className="flex items-center h-5">
            <input
              id="share-report"
              type="checkbox"
              checked={shareCommunity}
              onChange={(e) => setShareCommunity(e.target.checked)}
              className="w-4 h-4 rounded text-red-600 border-red-300 focus:ring-red-500 cursor-pointer accent-red-600"
            />
          </div>
          <div className="text-left">
            <label htmlFor="share-report" className="text-xs font-semibold text-slate-800 cursor-pointer block leading-tight">
              Share my report with nearby users and rescue teams
            </label>
            <p className="text-[10px] text-slate-500 mt-0.5">Your identity will remain private.</p>
          </div>
        </section>

        {/* Submit Action */}
        <div className="pt-1 pb-2">
          <button
            type="button"
            onClick={handleSubmit}
            className="w-full py-3 bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-semibold text-xs rounded-xl shadow-md shadow-red-200 flex items-center justify-center space-x-2 transition-all"
          >
            <Send className="w-4 h-4" />
            <span>Submit Report</span>
          </button>
        </div>
      </main>

      {/* Confirmation Modal */}
      {isSuccess && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-xs w-full text-center shadow-2xl border border-slate-100">
            <div className="w-14 h-14 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Incident Reported</h3>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Thank you! Your report on <strong>{incidentType}</strong> has been shared with regional rescue teams and nearby citizens.
            </p>
            <button
              type="button"
              onClick={() => {
                setIsSuccess(false);
                onBack();
              }}
              className="w-full py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider shadow-md mt-4"
            >
              View in Activity History
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
