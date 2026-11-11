import React, { useState } from 'react';
import {
  ArrowLeft,
  MapPin,
  ChevronDown,
  Home,
  Search,
  SlidersHorizontal,
  Plus,
  Users,
  Accessibility,
  Crosshair,
  Map as MapIcon,
  Navigation,
  ArrowUpDown,
  Utensils,
  Droplets,
  AlertTriangle,
  ChevronRight,
} from 'lucide-react';
import { Shelter } from '../types';
import { sheltersList } from '../data/mockData';

interface SafeSheltersScreenProps {
  onBack: () => void;
  onOpenDirections: (shelter: Shelter) => void;
  onOpenFullMap: () => void;
}

export const SafeSheltersScreen: React.FC<SafeSheltersScreenProps> = ({
  onBack,
  onOpenDirections,
  onOpenFullMap,
}) => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'available' | 'medical' | 'family' | 'accessible'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedShelterMarker, setSelectedShelterMarker] = useState<Shelter | null>(null);

  const filteredShelters = sheltersList.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.area.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (activeFilter === 'available') return !s.isFull;
    if (activeFilter === 'medical') return s.amenities.includes('Medical');
    if (activeFilter === 'family') return s.amenities.includes('Family Friendly') || s.amenities.includes('Family');
    if (activeFilter === 'accessible') return s.amenities.includes('Accessible');
    return true;
  });

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#F7F9FC] select-none">
      {/* Top Header */}
      <div className="px-5 pt-2 pb-2 text-center relative bg-white border-b border-slate-100 shrink-0" data-purpose="app-header">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go Back"
          className="absolute left-4 top-3 p-1 text-slate-800 text-lg hover:opacity-75 focus:outline-none"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2.5]" />
        </button>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Safe Shelters</h1>
        <p className="text-xs text-slate-500 mt-0.5 font-normal">Find a safe place near you</p>
        <div className="inline-flex items-center justify-center mt-1 text-xs font-semibold text-slate-700 cursor-pointer hover:text-slate-900">
          <MapPin className="w-3.5 h-3.5 text-red-600 fill-red-600 mr-1" />
          <span>Ahmedabad, Gujarat</span>
          <ChevronDown className="w-3 h-3 text-slate-500 ml-1" />
        </div>
      </div>

      {/* Main Scrollable Content */}
      <main className="flex-1 overflow-y-auto px-4 py-3 space-y-3.5 pb-24 no-scrollbar">
        {/* Stat Cards */}
        <section className="grid grid-cols-3 gap-2.5" data-purpose="stats-overview">
          {/* Total Shelters */}
          <div className="bg-white rounded-2xl p-2.5 flex items-center space-x-2 shadow-xs border border-slate-100">
            <div className="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center text-slate-700 shrink-0">
              <Home className="w-4 h-4 fill-current" />
            </div>
            <div className="leading-tight">
              <span className="block text-base font-bold text-slate-900">24</span>
              <span className="text-[10px] text-slate-500 font-medium leading-none">Shelters Nearby</span>
            </div>
          </div>

          {/* Available Shelters */}
          <div className="bg-white rounded-2xl p-2.5 flex items-center space-x-2 shadow-xs border border-slate-100">
            <div className="w-9 h-9 rounded-full bg-green-50 flex items-center justify-center text-green-600 shrink-0">
              <Home className="w-4 h-4 fill-current" />
            </div>
            <div className="leading-tight">
              <span className="block text-base font-bold text-slate-900">18</span>
              <span className="text-[10px] text-slate-500 font-medium leading-none">Available</span>
            </div>
          </div>

          {/* Full Shelters */}
          <div className="bg-white rounded-2xl p-2.5 flex items-center space-x-2 shadow-xs border border-slate-100">
            <div className="w-9 h-9 rounded-full bg-red-50 flex items-center justify-center text-red-500 shrink-0">
              <Home className="w-4 h-4 fill-current" />
            </div>
            <div className="leading-tight">
              <span className="block text-base font-bold text-slate-900">6</span>
              <span className="text-[10px] text-slate-500 font-medium leading-none">Full</span>
            </div>
          </div>
        </section>

        {/* Search & Filters */}
        <section className="space-y-2.5" data-purpose="search-and-filters">
          <div className="relative flex items-center">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search shelters by name or area"
              className="w-full pl-10 pr-10 py-2.5 bg-white rounded-xl text-xs font-medium border border-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-red-400 focus:border-red-400 shadow-xs"
            />
            <button
              type="button"
              aria-label="Filter Options"
              className="absolute right-3 text-slate-500 hover:text-slate-700"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center space-x-2 overflow-x-auto no-scrollbar py-0.5 text-xs whitespace-nowrap">
            <button
              type="button"
              onClick={() => setActiveFilter('all')}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-2xs transition-all ${
                activeFilter === 'all'
                  ? 'border border-red-400 bg-red-50 text-red-600'
                  : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              All
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('available')}
              className={`px-3 py-1.5 rounded-full border text-xs font-medium flex items-center space-x-1.5 shadow-2xs transition-all ${
                activeFilter === 'available'
                  ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>Available</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('medical')}
              className={`px-3 py-1.5 rounded-full border text-xs font-medium flex items-center space-x-1.5 shadow-2xs transition-all ${
                activeFilter === 'medical'
                  ? 'border-red-400 bg-red-50 text-red-600'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Plus className="w-3 h-3 text-red-500 stroke-[3]" />
              <span>Medical</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('family')}
              className={`px-3 py-1.5 rounded-full border text-xs font-medium flex items-center space-x-1.5 shadow-2xs transition-all ${
                activeFilter === 'family'
                  ? 'border-red-400 bg-red-50 text-red-600'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Users className="w-3.5 h-3.5 text-slate-500" />
              <span>Family</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveFilter('accessible')}
              className={`px-3 py-1.5 rounded-full border text-xs font-medium flex items-center space-x-1.5 shadow-2xs transition-all ${
                activeFilter === 'accessible'
                  ? 'border-red-400 bg-red-50 text-red-600'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Accessibility className="w-3.5 h-3.5 text-slate-500" />
              <span>Accessible</span>
            </button>
          </div>
        </section>

        {/* Interactive Map Section */}
        <section className="bg-white rounded-2xl p-2 shadow-xs border border-slate-100 overflow-hidden" data-purpose="map-overview">
          <div className="relative h-60 w-full rounded-xl overflow-hidden bg-[#e5eef5] select-none">
            {/* SVG Graphic Map */}
            <svg className="absolute inset-0 w-full h-full object-cover" viewBox="0 0 400 240" preserveAspectRatio="none">
              <rect width="400" height="240" fill="#E8ECEF" />
              <path d="M-10,30 Q120,60 210,20 T420,50 L420,-10 L-10,-10 Z" fill="#E2E7EA" />
              <path d="M-10,200 Q150,160 300,230 L420,250 L-10,250 Z" fill="#E2E7EA" />
              <path d="M-20,90 L420,110 M-20,170 L420,140 M110,-10 L130,250 M290,-10 L270,250" fill="none" stroke="#DFE3E6" strokeWidth="6" />
              <path d="M40,20 L380,220 M360,10 L30,230" fill="none" stroke="#DFE3E6" strokeWidth="4" />
              {/* Sabarmati River */}
              <path d="M250,-10 C210,40 170,90 195,140 C215,180 165,220 150,250" fill="none" stroke="#B8D7F9" strokeWidth="36" strokeLinecap="round" />
              <path d="M250,-10 C210,40 170,90 195,140 C215,180 165,220 150,250" fill="none" stroke="#CBE2FA" strokeWidth="28" strokeLinecap="round" />
            </svg>

            {/* Area Labels */}
            <span className="absolute top-4 left-6 text-[10px] font-semibold text-slate-500">Ghatlodia</span>
            <span className="absolute top-3 left-36 text-[10px] font-semibold text-slate-500">Naranpura</span>
            <span className="absolute top-8 right-8 text-[10px] font-semibold text-slate-500">Nikol</span>
            <span className="absolute top-24 left-20 text-[10px] font-semibold text-slate-500">Navrangpura</span>
            <span className="absolute bottom-20 left-4 text-[9px] font-medium text-blue-500 leading-tight">Sabarmati<br />River</span>
            <span className="absolute bottom-16 left-24 text-[10px] font-semibold text-slate-500">Paldi</span>
            <span className="absolute bottom-18 right-24 text-[10px] font-semibold text-slate-500">Maninagar</span>
            <span className="absolute bottom-24 right-8 text-[10px] font-semibold text-slate-500">Vastral</span>

            {/* Central City Label */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none mt-2">
              <div className="relative inline-flex mb-1">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-600 border-2 border-white" />
              </div>
              <p className="text-xs font-bold text-slate-800 leading-none">Ahmedabad</p>
              <p className="text-[10px] font-medium text-slate-700 leading-tight">અમદાવાદ</p>
            </div>

            {/* Interactive Shelter Pins */}
            {/* 1. Naranpura Available (Green) */}
            <button
              type="button"
              onClick={() => setSelectedShelterMarker(sheltersList[0])}
              className="absolute top-5 left-32 transform -translate-x-1/2 hover:scale-110 transition-transform focus:outline-none"
              title="Community Relief Center"
            >
              <div className="w-6 h-6 rounded-full bg-emerald-700 border-2 border-white shadow-md flex items-center justify-center text-white text-[10px]">
                <Home className="w-3.5 h-3.5 fill-current" />
              </div>
            </button>

            {/* 2. Ghatlodia Full (Red) */}
            <button
              type="button"
              onClick={() => setSelectedShelterMarker(sheltersList[1])}
              className="absolute top-16 left-24 transform -translate-x-1/2 hover:scale-110 transition-transform focus:outline-none"
              title="City Emergency Shelter"
            >
              <div className="w-6 h-6 rounded-full bg-red-600 border-2 border-white shadow-md flex items-center justify-center text-white text-[10px]">
                <Home className="w-3.5 h-3.5 fill-current" />
              </div>
            </button>

            {/* 3. Vastral Available (Green) */}
            <button
              type="button"
              onClick={() => setSelectedShelterMarker(sheltersList[2])}
              className="absolute bottom-20 right-26 transform -translate-x-1/2 hover:scale-110 transition-transform focus:outline-none"
              title="Sardar Patel School Shelter"
            >
              <div className="w-6 h-6 rounded-full bg-emerald-700 border-2 border-white shadow-md flex items-center justify-center text-white text-[10px]">
                <Home className="w-3.5 h-3.5 fill-current" />
              </div>
            </button>

            {/* Selected Marker Callout */}
            {selectedShelterMarker && (
              <div className="absolute top-12 left-1/2 -translate-x-1/2 bg-white/95 backdrop-blur-xs px-3 py-2 rounded-xl shadow-lg border border-slate-200 text-left z-20 w-48">
                <p className="text-[11px] font-bold text-slate-900 truncate">{selectedShelterMarker.name}</p>
                <p className="text-[9px] text-slate-500">{selectedShelterMarker.area} • {selectedShelterMarker.distance}</p>
                <button
                  type="button"
                  onClick={() => onOpenDirections(selectedShelterMarker)}
                  className="mt-1 text-[10px] text-red-600 font-bold hover:underline block"
                >
                  Navigate Here →
                </button>
              </div>
            )}

            {/* Map Controls */}
            <div className="absolute right-2 top-3 flex flex-col space-y-1.5">
              <button
                type="button"
                aria-label="Recenter Map"
                className="w-7 h-7 bg-white rounded-lg shadow-sm flex items-center justify-center text-slate-700 hover:bg-slate-50 active:scale-95"
              >
                <Crosshair className="w-3.5 h-3.5" />
              </button>
              <div className="bg-white rounded-lg shadow-sm flex flex-col overflow-hidden divide-y divide-slate-100">
                <button type="button" className="w-7 h-7 flex items-center justify-center text-slate-700 hover:bg-slate-50 text-xs font-bold leading-none">+</button>
                <button type="button" className="w-7 h-7 flex items-center justify-center text-slate-700 hover:bg-slate-50 text-xs font-bold leading-none">−</button>
              </div>
            </div>

            {/* Map Floating Action Buttons */}
            <button
              type="button"
              className="absolute bottom-2.5 left-2.5 bg-white/95 backdrop-blur-xs px-3 py-1.5 rounded-xl shadow-sm border border-slate-200 flex items-center space-x-1.5 text-xs font-semibold text-blue-900 hover:bg-white active:scale-95"
            >
              <Navigation className="w-3 h-3 fill-current text-blue-800" />
              <span>My Location</span>
            </button>
            <button
              type="button"
              onClick={onOpenFullMap}
              className="absolute bottom-2.5 right-2.5 bg-white/95 backdrop-blur-xs px-3 py-1.5 rounded-xl shadow-sm border border-slate-200 flex items-center space-x-1.5 text-xs font-semibold text-blue-900 hover:bg-white active:scale-95"
            >
              <MapIcon className="w-3 h-3 text-blue-800" />
              <span>View Full Map</span>
            </button>
          </div>

          {/* Map Legend */}
          <div className="pt-2 px-1 flex items-center space-x-4 text-[11px] font-medium text-slate-600">
            <div className="flex items-center space-x-1.5">
              <div className="w-4 h-4 rounded-full bg-emerald-700 flex items-center justify-center text-white text-[8px]">
                <Home className="w-2.5 h-2.5 fill-current" />
              </div>
              <span>Available</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-4 h-4 rounded-full bg-red-600 flex items-center justify-center text-white text-[8px]">
                <Home className="w-2.5 h-2.5 fill-current" />
              </div>
              <span>Full</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-4 h-4 rounded-full bg-slate-600 flex items-center justify-center text-white text-[8px]">
                <Home className="w-2.5 h-2.5 fill-current" />
              </div>
              <span>Other</span>
            </div>
          </div>
        </section>

        {/* Shelters List Section */}
        <section className="space-y-3" data-purpose="shelters-list">
          <div className="flex items-center justify-between pt-1">
            <h2 className="text-base font-bold text-slate-900">Nearby Shelters</h2>
            <button
              type="button"
              className="inline-flex items-center text-xs font-semibold text-slate-600 bg-white px-2.5 py-1 rounded-lg border border-slate-200 hover:bg-slate-50"
            >
              <ArrowUpDown className="w-3 h-3 mr-1.5 text-slate-400" />
              Nearest First
            </button>
          </div>

          {/* Render Shelter Cards */}
          {filteredShelters.map((shelter) => (
            <article
              key={shelter.id}
              className="bg-white rounded-2xl p-3 shadow-xs border border-slate-100 flex flex-col space-y-2.5 hover:shadow-md transition-shadow"
            >
              <div className="flex space-x-3 items-start">
                <div className="relative w-24 h-20 rounded-xl overflow-hidden bg-slate-100 shrink-0">
                  <img
                    alt={shelter.name}
                    src={shelter.imageUrl}
                    className="w-full h-full object-cover"
                  />
                  <span className="absolute bottom-1 left-1 bg-black/75 backdrop-blur-xs text-white text-[9px] font-semibold px-1.5 py-0.5 rounded">
                    {shelter.distance}
                  </span>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-slate-900 text-sm truncate pr-1">{shelter.name}</h3>
                    <ChevronRight className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                  </div>
                  <p className="text-[11px] text-slate-500 truncate">{shelter.area}</p>

                  <div className="mt-1 flex items-center justify-between text-xs">
                    <span
                      className={`inline-block text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        shelter.isFull
                          ? 'bg-red-50 text-red-600'
                          : 'bg-emerald-50 text-emerald-700'
                      }`}
                    >
                      {shelter.statusText}
                    </span>
                    <span className="text-[11px] font-semibold text-slate-600">
                      <strong className="text-slate-900 font-bold">{shelter.occupied}</strong> / {shelter.capacity} people
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${shelter.isFull ? 'bg-red-500' : 'bg-emerald-500'}`}
                      style={{ width: `${(shelter.occupied / shelter.capacity) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Amenities & Direction Button */}
              <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                <div className="flex items-center space-x-2 text-[10px] text-slate-500 font-medium">
                  {shelter.amenities.map((amenity, idx) => (
                    <span key={idx} className="flex items-center">
                      {amenity === 'Food' && <Utensils className="w-3 h-3 mr-1 text-slate-400" />}
                      {amenity === 'Water' && <Droplets className="w-3 h-3 mr-1 text-slate-400" />}
                      {amenity === 'Medical' && <Plus className="w-3 h-3 mr-1 text-slate-400 stroke-[3]" />}
                      {amenity === 'Accessible' && <Accessibility className="w-3 h-3 mr-1 text-slate-400" />}
                      {amenity.includes('Family') && <Users className="w-3 h-3 mr-1 text-slate-400" />}
                      {amenity}
                    </span>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={() => onOpenDirections(shelter)}
                  className={`text-[11px] font-bold px-3 py-1.5 rounded-xl shadow-xs flex items-center space-x-1.5 transition-colors ${
                    shelter.isFull
                      ? 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                      : 'bg-red-600 hover:bg-red-700 text-white'
                  }`}
                >
                  <Navigation className="w-3 h-3" />
                  <span>GET DIRECTIONS</span>
                </button>
              </div>
            </article>
          ))}
        </section>

        {/* Warning Alert Banner */}
        <section className="bg-[#FDECEC] border border-red-100 rounded-2xl p-3.5 flex items-center space-x-3.5" data-purpose="status-disclaimer">
          <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600 shrink-0">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-red-600 leading-tight">Shelter status can change quickly.</h4>
            <p className="text-[11px] text-slate-600 mt-0.5 leading-tight">Check live availability before travelling.</p>
          </div>
        </section>
      </main>
    </div>
  );
};
