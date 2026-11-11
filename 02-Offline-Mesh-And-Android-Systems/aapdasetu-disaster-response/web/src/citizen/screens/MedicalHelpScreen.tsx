import React, { useState } from 'react';
import {
  ArrowLeft,
  PhoneCall,
  Search,
  SlidersHorizontal,
  Plus,
  Stethoscope,
  Droplets,
  Truck,
  Pill,
  Crosshair,
  Navigation,
  Building2,
  Store,
  ArrowUpDown,
  Phone,
  AlertTriangle,
  ChevronDown,
} from 'lucide-react';
import { Hospital } from '../types';
import { hospitalsList } from '../data/mockData';

interface MedicalHelpScreenProps {
  onBack: () => void;
  onOpenDirections: (hospital: Hospital) => void;
}

export const MedicalHelpScreen: React.FC<MedicalHelpScreenProps> = ({
  onBack,
  onOpenDirections,
}) => {
  const [activeTab, setActiveTab] = useState<'hospitals' | 'clinics' | 'blood-banks' | 'ambulance' | 'pharmacies'>('hospitals');
  const [searchQuery, setSearchQuery] = useState('');
  const [callNotice, setCallNotice] = useState<string | null>(null);

  const filteredHospitals = hospitalsList.filter((h) =>
    h.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    h.area.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCall = (name: string, phone: string) => {
    setCallNotice(`Connecting direct emergency line to ${name} (${phone})...`);
    setTimeout(() => setCallNotice(null), 4000);
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-white select-none">
      {/* Top Bar */}
      <header className="px-4 pt-2 pb-1 flex items-center justify-between border-b border-gray-50 shrink-0">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go Back"
          className="p-1 -ml-1 text-gray-800 active:opacity-60"
        >
          <ArrowLeft className="w-6 h-6 stroke-[2.2]" />
        </button>

        <div className="text-center flex-1 px-1">
          <h1 className="text-base font-bold text-gray-900 leading-tight">Medical Help</h1>
          <p className="text-[10px] text-gray-500 font-medium truncate">
            Find nearby hospitals, clinics and medical support
          </p>
        </div>

        {/* Emergency 108 Call Button */}
        <button
          type="button"
          onClick={() => handleCall('National Emergency Medical Service', '108')}
          className="flex items-center gap-1.5 bg-red-50 hover:bg-red-100 border border-red-100 px-2.5 py-1 rounded-full text-right shrink-0"
        >
          <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center text-red-600">
            <PhoneCall className="w-3.5 h-3.5 fill-current" />
          </div>
          <div className="leading-none text-left">
            <span className="block text-[9px] text-red-600 font-semibold uppercase tracking-tight">Emergency Call</span>
            <span className="block text-xs text-red-600 font-bold">108</span>
          </div>
        </button>
      </header>

      {/* Call notification banner if triggered */}
      {callNotice && (
        <div className="bg-red-600 text-white text-xs px-4 py-2 text-center animate-in fade-in flex items-center justify-center gap-2">
          <PhoneCall className="w-4 h-4 animate-bounce" />
          <span>{callNotice}</span>
        </div>
      )}

      {/* Category Tabs */}
      <nav className="px-4 py-2 border-b border-gray-100 shrink-0">
        <div className="flex space-x-2 overflow-x-auto no-scrollbar py-0.5">
          {/* Hospitals */}
          <button
            type="button"
            onClick={() => setActiveTab('hospitals')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-xs shrink-0 transition-all ${
              activeTab === 'hospitals'
                ? 'border border-red-600 bg-red-50 text-red-600'
                : 'border border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Plus className="w-3.5 h-3.5 stroke-[3]" />
            <span>Hospitals</span>
          </button>

          {/* Clinics */}
          <button
            type="button"
            onClick={() => setActiveTab('clinics')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-xs shrink-0 transition-all ${
              activeTab === 'clinics'
                ? 'border border-red-600 bg-red-50 text-red-600'
                : 'border border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Stethoscope className="w-3.5 h-3.5" />
            <span>Clinics</span>
          </button>

          {/* Blood Banks */}
          <button
            type="button"
            onClick={() => setActiveTab('blood-banks')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-xs shrink-0 transition-all ${
              activeTab === 'blood-banks'
                ? 'border border-red-600 bg-red-50 text-red-600'
                : 'border border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Droplets className="w-3.5 h-3.5 text-red-600 fill-red-600" />
            <span>Blood Banks</span>
          </button>

          {/* Ambulance */}
          <button
            type="button"
            onClick={() => setActiveTab('ambulance')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-xs shrink-0 transition-all ${
              activeTab === 'ambulance'
                ? 'border border-red-600 bg-red-50 text-red-600'
                : 'border border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Truck className="w-3.5 h-3.5 text-red-600" />
            <span>Ambulance</span>
          </button>

          {/* Pharmacies */}
          <button
            type="button"
            onClick={() => setActiveTab('pharmacies')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-xs shrink-0 transition-all ${
              activeTab === 'pharmacies'
                ? 'border border-red-600 bg-red-50 text-red-600'
                : 'border border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Pill className="w-3.5 h-3.5 text-gray-500" />
            <span>Pharmacies</span>
          </button>
        </div>
      </nav>

      {/* Main Scrollable Content */}
      <main className="flex-1 overflow-y-auto px-4 py-2 space-y-3 pb-24 no-scrollbar">
        {/* Search and Filters */}
        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-400">
              <Search className="w-4 h-4" />
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name or area"
              className="w-full bg-white border border-gray-200 rounded-xl py-2 pl-9 pr-3 text-xs text-gray-800 placeholder-gray-400 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600 shadow-2xs"
            />
          </div>
          <button
            type="button"
            className="flex items-center space-x-1 px-3 py-2 rounded-xl bg-red-50/80 border border-red-100 text-red-600 text-xs font-medium hover:bg-red-100 shrink-0"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Filters</span>
          </button>
        </div>

        {/* Interactive Map View */}
        <section aria-label="Map View">
          <div className="relative w-full h-48 rounded-2xl overflow-hidden border border-gray-200 shadow-inner bg-[#e5ecef]">
            {/* Map Roads & River Graphic */}
            <svg className="absolute inset-0 w-full h-full object-cover" viewBox="0 0 400 200" preserveAspectRatio="none">
              <rect width="400" height="200" fill="#E8ECEF" />
              {/* Secondary roads */}
              <line x1="0" y1="60" x2="400" y2="70" stroke="#DFE3E6" strokeWidth="4" />
              <line x1="0" y1="130" x2="400" y2="120" stroke="#DFE3E6" strokeWidth="4" />
              <line x1="100" y1="0" x2="110" y2="200" stroke="#DFE3E6" strokeWidth="4" />
              <line x1="280" y1="0" x2="270" y2="200" stroke="#DFE3E6" strokeWidth="4" />
              {/* Sabarmati river */}
              <path d="M220,0 C190,40 170,90 190,140 C205,170 170,200 160,200" fill="none" stroke="#CBE2FA" strokeWidth="32" strokeLinecap="round" />
            </svg>

            {/* City Label */}
            <div className="absolute top-[36%] left-[45%] -translate-x-1/2 text-center pointer-events-none">
              <span className="block text-xs font-bold text-gray-800 tracking-tight">Ahmedabad</span>
              <span className="block text-[10px] text-gray-600 font-medium">અમદાવાદ</span>
            </div>

            {/* Locality labels */}
            <span className="absolute top-4 left-24 text-[9px] font-semibold text-gray-600">Navrangpura</span>
            <span className="absolute top-24 left-16 text-[9px] font-semibold text-gray-600">Paldi</span>
            <span className="absolute bottom-4 left-40 text-[9px] font-semibold text-gray-600">Ellisbridge</span>
            <span className="absolute bottom-4 right-16 text-[9px] font-semibold text-gray-600">Maninagar</span>
            <span className="absolute top-24 right-6 text-[9px] font-semibold text-gray-600">Vastral</span>

            {/* Medical Pins (Red crosses) */}
            <div className="absolute top-5 left-16 bg-red-600 text-white p-1 rounded-full shadow-md">
              <Plus className="w-3 h-3 stroke-[3]" />
            </div>
            <div className="absolute top-14 left-28 bg-red-600 text-white p-1 rounded-full shadow-md">
              <Plus className="w-3 h-3 stroke-[3]" />
            </div>
            <div className="absolute top-8 right-28 bg-red-600 text-white p-1 rounded-full shadow-md">
              <Plus className="w-3 h-3 stroke-[3]" />
            </div>
            <div className="absolute bottom-10 right-20 bg-red-600 text-white p-1 rounded-full shadow-md">
              <Plus className="w-3 h-3 stroke-[3]" />
            </div>

            {/* Current Location Beacon */}
            <div className="absolute top-[34%] left-[49%] -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
              <div className="w-10 h-10 bg-blue-400/30 rounded-full animate-ping absolute" />
              <div className="w-6 h-6 bg-blue-400/40 rounded-full absolute" />
              <div className="w-3.5 h-3.5 bg-blue-600 border-2 border-white rounded-full shadow-xs z-10" />
            </div>

            {/* Floating Actions */}
            <div className="absolute bottom-2.5 left-2.5">
              <button
                type="button"
                className="bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded-full shadow-xs border border-gray-200 text-gray-800 text-[10px] font-semibold flex items-center space-x-1"
              >
                <Navigation className="w-2.5 h-2.5 fill-current text-gray-700" />
                <span>My Location</span>
              </button>
            </div>
            <button
              type="button"
              aria-label="Center on Location"
              className="absolute bottom-2.5 right-2.5 bg-white/95 backdrop-blur-xs p-1.5 rounded-full shadow-xs border border-gray-200 text-gray-800"
            >
              <Crosshair className="w-3.5 h-3.5 text-gray-700" />
            </button>
          </div>
        </section>

        {/* Quick Counts Overview */}
        <section aria-label="Facilities Overview" className="py-2 border-y border-gray-100">
          <div className="grid grid-cols-5 gap-1 text-center">
            <div className="flex flex-col items-center justify-center p-0.5">
              <div className="flex items-center space-x-0.5">
                <Building2 className="w-3.5 h-3.5 text-red-600" />
                <span className="text-xs font-bold text-gray-900 leading-none">12</span>
              </div>
              <span className="text-[8.5px] text-gray-500 font-medium leading-tight mt-0.5">Hospitals</span>
            </div>

            <div className="flex flex-col items-center justify-center p-0.5 border-l border-gray-100">
              <div className="flex items-center space-x-0.5">
                <Stethoscope className="w-3.5 h-3.5 text-red-600" />
                <span className="text-xs font-bold text-gray-900 leading-none">8</span>
              </div>
              <span className="text-[8.5px] text-gray-500 font-medium leading-tight mt-0.5">Clinics</span>
            </div>

            <div className="flex flex-col items-center justify-center p-0.5 border-l border-gray-100">
              <div className="flex items-center space-x-0.5">
                <Droplets className="w-3.5 h-3.5 text-red-600 fill-red-600" />
                <span className="text-xs font-bold text-gray-900 leading-none">6</span>
              </div>
              <span className="text-[8.5px] text-gray-500 font-medium leading-tight mt-0.5">Blood Banks</span>
            </div>

            <div className="flex flex-col items-center justify-center p-0.5 border-l border-gray-100">
              <div className="flex items-center space-x-0.5">
                <Truck className="w-3.5 h-3.5 text-red-600" />
                <span className="text-xs font-bold text-gray-900 leading-none">14</span>
              </div>
              <span className="text-[8.5px] text-gray-500 font-medium leading-tight mt-0.5">Ambulances</span>
            </div>

            <div className="flex flex-col items-center justify-center p-0.5 border-l border-gray-100">
              <div className="flex items-center space-x-0.5">
                <Store className="w-3.5 h-3.5 text-red-600" />
                <span className="text-xs font-bold text-gray-900 leading-none">20</span>
              </div>
              <span className="text-[8.5px] text-gray-500 font-medium leading-tight mt-0.5">Pharmacies</span>
            </div>
          </div>
        </section>

        {/* Section Header */}
        <div className="pt-1 pb-0.5 flex justify-between items-center">
          <h2 className="text-sm font-bold text-gray-900">Nearby Hospitals</h2>
          <button
            type="button"
            className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 text-xs font-medium"
          >
            <ArrowUpDown className="w-3.5 h-3.5 text-gray-500" />
            <span>Nearest First</span>
            <ChevronDown className="w-3 h-3 text-gray-500" />
          </button>
        </div>

        {/* Hospitals List */}
        <div className="space-y-3">
          {filteredHospitals.map((hospital) => (
            <article
              key={hospital.id}
              className="bg-white rounded-2xl border border-gray-100 shadow-xs p-3 hover:shadow-md transition-shadow"
            >
              <div className="flex space-x-3">
                <img
                  alt={hospital.name}
                  src={hospital.imageUrl}
                  className="w-20 h-20 rounded-xl object-cover shrink-0 border border-gray-100"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <h3 className="text-xs font-bold text-gray-900 truncate">{hospital.name}</h3>
                    <span className="text-xs font-bold text-gray-800 shrink-0 ml-1">{hospital.distance}</span>
                  </div>
                  <p className="text-[10px] text-gray-500 font-normal truncate mt-0.5">{hospital.area}</p>
                  <p className="text-[9px] text-gray-400 font-medium mt-0.5 truncate">{hospital.tags}</p>

                  <div className="flex items-center space-x-1.5 mt-2">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-medium bg-emerald-50 text-emerald-700">
                      <span className="w-1.5 h-1.5 bg-emerald-600 rounded-full mr-1" />
                      Operational
                    </span>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-medium ${
                        hospital.crowdLevel === 'Low Crowd'
                          ? 'bg-green-50 text-green-700'
                          : 'bg-amber-50 text-amber-700'
                      }`}
                    >
                      {hospital.crowdLevel}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 mt-3 pt-2.5 border-t border-gray-50">
                <button
                  type="button"
                  onClick={() => handleCall(hospital.name, hospital.phone)}
                  className="flex-1 py-1.5 px-3 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 text-xs font-medium flex items-center justify-center space-x-1.5 border border-red-100 transition-colors"
                >
                  <Phone className="w-3.5 h-3.5 fill-current" />
                  <span>Call</span>
                </button>
                <button
                  type="button"
                  onClick={() => onOpenDirections(hospital)}
                  className="w-2/3 py-1.5 px-3 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-medium flex items-center justify-center space-x-1.5 shadow-xs transition-colors"
                >
                  <Navigation className="w-3.5 h-3.5 fill-current" />
                  <span>Get Directions</span>
                </button>
              </div>
            </article>
          ))}
        </div>

        {/* Emergency Notice Banner */}
        <footer className="mt-2">
          <div className="bg-red-50/70 border border-red-100/90 rounded-2xl p-3 flex items-start space-x-3">
            <div className="bg-red-600 text-white p-2 rounded-xl shrink-0">
              <AlertTriangle className="w-4 h-4 fill-white text-red-600" />
            </div>
            <div className="text-[11px] leading-snug">
              <p className="font-bold text-red-600">In a life-threatening situation, call 108 immediately.</p>
              <p className="text-gray-600 text-[10px] mt-0.5">
                This app helps you find nearby medical facilities, but is not a substitute for emergency services.
              </p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
};
