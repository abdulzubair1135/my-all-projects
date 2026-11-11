import React, { useState } from 'react';
import {
  ArrowLeft,
  Info,
  Radio,
  ChevronRight,
  Waves,
  Flame,
  Mountain,
  Home,
  Plus,
  Package,
  Navigation,
  Crosshair,
  List,
  AlertTriangle,
  Layers,
} from 'lucide-react';

interface DisasterMapScreenProps {
  onBack: () => void;
  onNavigateToShelters: () => void;
  onNavigateToMedical: () => void;
}

export const DisasterMapScreen: React.FC<DisasterMapScreenProps> = ({
  onBack,
  onNavigateToShelters,
  onNavigateToMedical,
}) => {
  const [activeFilter, setActiveFilter] = useState<'All' | 'Flood' | 'Fire' | 'Landslide' | 'Shelter' | 'Medical' | 'Relief'>('All');
  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showAffectedAreasModal, setShowAffectedAreasModal] = useState(false);
  const [safeRouteActive, setSafeRouteActive] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedPinInfo, setSelectedPinInfo] = useState<string | null>(null);

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#f8f9fa] relative select-none">
      {/* App Header */}
      <div className="px-5 pt-3 pb-2 flex items-center justify-between z-30 shrink-0 bg-white border-b border-gray-100">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go back"
          className="w-9 h-9 flex items-center justify-center -ml-1 text-gray-800 hover:opacity-75 transition-opacity"
        >
          <ArrowLeft className="w-6 h-6 stroke-[2.5]" />
        </button>

        <div className="text-center flex-1 px-1">
          <h1 className="text-lg font-bold tracking-tight text-gray-900 leading-tight">Disaster Map</h1>
          <p className="text-[11px] text-gray-500 font-normal truncate mt-0.5">
            Live updates from authorities and on-ground teams
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowAboutModal(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs font-semibold text-gray-800 shadow-2xs hover:bg-gray-50 active:scale-95 transition-all"
        >
          <div className="w-4 h-4 rounded-full bg-gray-800 flex items-center justify-center text-[10px] text-white font-serif font-bold italic">
            i
          </div>
          <span>About</span>
        </button>
      </div>

      {/* Real-time Alert Banner */}
      <div className="px-4 py-2 z-30 shrink-0 bg-white">
        <div className="bg-[#FFF1F1] border border-[#FEE2E2] rounded-2xl p-3 flex items-center justify-between shadow-2xs">
          <div className="flex items-center space-x-3">
            <div className="text-red-600 flex items-center justify-center pl-1">
              <Radio className="w-5 h-5 animate-pulse" />
            </div>
            <div className="text-left">
              <h2 className="text-xs font-bold text-red-600 tracking-tight leading-tight">
                Stay informed. Stay safe.
              </h2>
              <p className="text-[11px] text-gray-600 leading-tight mt-0.5 font-normal">
                This map shows real-time information from verified sources.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowAffectedAreasModal(true)}
            className="text-gray-400 pl-2 pr-1 hover:text-gray-600"
          >
            <ChevronRight className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </div>

      {/* Disaster Category Filters */}
      <nav className="py-2 px-4 z-30 shrink-0 bg-white border-b border-gray-100">
        <div className="flex items-center space-x-2.5 overflow-x-auto no-scrollbar scroll-smooth pb-0.5">
          {[
            { id: 'All', label: 'All' },
            { id: 'Flood', label: 'Flood', icon: Waves, color: 'text-blue-500' },
            { id: 'Fire', label: 'Fire', icon: Flame, color: 'text-red-500' },
            { id: 'Landslide', label: 'Landslide', icon: Mountain, color: 'text-amber-800' },
            { id: 'Shelter', label: 'Shelter', icon: Home, color: 'text-emerald-700' },
            { id: 'Medical', label: 'Medical', icon: Plus, color: 'text-red-600' },
            { id: 'Relief', label: 'Relief', icon: Package, color: 'text-indigo-600' },
          ].map((item) => {
            const isSelected = activeFilter === item.id;
            const IconComp = item.icon;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveFilter(item.id as any)}
                className={`flex flex-col items-center justify-center min-w-[54px] h-[58px] rounded-xl shadow-2xs transition-transform active:scale-95 ${
                  isSelected
                    ? 'bg-red-50 border-2 border-red-500'
                    : 'bg-white border border-gray-200/90'
                }`}
              >
                {IconComp && (
                  <IconComp className={`w-5 h-5 mt-1 ${item.color}`} />
                )}
                <span
                  className={`text-[10px] font-semibold mt-1 ${
                    isSelected ? 'text-gray-900 font-bold' : 'text-gray-700'
                  }`}
                >
                  {item.label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Interactive Map Canvas Viewport */}
      <main className="relative flex-1 w-full bg-[#EBF2F7] overflow-hidden min-h-[360px]">
        <div
          className="absolute inset-0 transition-transform duration-300 origin-center"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          {/* SVG Map Layer */}
          <svg
            className="absolute inset-0 w-full h-full"
            fill="none"
            viewBox="0 0 428 500"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="floodGrad" x1="0%" x2="100%" y1="0%" y2="100%">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.32" />
                <stop offset="100%" stopColor="#60A5FA" stopOpacity="0.22" />
              </linearGradient>
              <linearGradient id="riskGrad" x1="0%" x2="100%" y1="0%" y2="100%">
                <stop offset="0%" stopColor="#EF4444" stopOpacity="0.32" />
                <stop offset="100%" stopColor="#F87171" stopOpacity="0.20" />
              </linearGradient>
              <linearGradient id="warningGrad" x1="0%" x2="100%" y1="0%" y2="100%">
                <stop offset="0%" stopColor="#F97316" stopOpacity="0.28" />
                <stop offset="100%" stopColor="#FB923C" stopOpacity="0.18" />
              </linearGradient>
            </defs>

            {/* Base Landmass */}
            <rect width="428" height="500" fill="#E8F0F3" />

            {/* Green Parks */}
            <path d="M 40,20 C 70,10 110,35 90,80 C 75,115 10,95 20,45 Z" fill="#D1E8D5" opacity="0.6" />
            <path d="M 330,60 C 370,50 410,80 395,120 C 365,150 310,130 330,60 Z" fill="#D1E8D5" opacity="0.6" />
            <path d="M 230,270 C 260,250 300,280 280,320 C 250,350 210,330 230,270 Z" fill="#D1E8D5" opacity="0.6" />

            {/* Road Grid */}
            <g opacity="0.85" stroke="#FFFFFF" strokeWidth="1.6">
              <path d="M-10,90 L440,70" />
              <path d="M-10,160 L440,150" />
              <path d="M-10,240 L440,250" />
              <path d="M-10,320 L440,335" />
              <path d="M-10,410 L440,400" />
              <path d="M80,-10 L70,510" />
              <path d="M150,-10 L160,510" />
              <path d="M260,-10 L250,510" />
              <path d="M330,-10 L340,510" />
              <path d="M400,-10 L390,510" />
            </g>

            {/* Primary Ring Arterials */}
            <g fill="none" opacity="0.9" stroke="#FED7AA" strokeWidth="2.5">
              <circle cx="214" cy="245" r="140" strokeDasharray="8 4" />
              <path d="M -10,180 C 120,180 230,200 440,210" />
              <path d="M 214,-10 L 218,510" />
            </g>

            {/* Sabarmati River Corridor */}
            <path
              d="M 390,-20 C 330,40 295,95 240,145 C 210,175 190,215 195,260 C 200,310 150,370 100,420 C 60,460 20,490 -10,510"
              fill="none"
              stroke="#93C5FD"
              strokeWidth="19"
              strokeLinecap="round"
            />
            <path
              d="M 390,-20 C 330,40 295,95 240,145 C 210,175 190,215 195,260 C 200,310 150,370 100,420 C 60,460 20,490 -10,510"
              fill="none"
              stroke="#60A5FA"
              strokeWidth="13"
              strokeLinecap="round"
            />

            {/* Hazard Polygons */}
            {(activeFilter === 'All' || activeFilter === 'Flood') && (
              <path
                d="M 148,135 C 130,120 140,100 160,95 C 180,85 200,105 205,125 C 215,145 195,170 180,180 C 165,190 140,170 135,150 Z"
                fill="url(#riskGrad)"
                stroke="#EF4444"
                strokeWidth="1.5"
                strokeDasharray="4 2"
              />
            )}

            {(activeFilter === 'All' || activeFilter === 'Fire' || activeFilter === 'Landslide') && (
              <path
                d="M 120,175 C 100,165 110,150 135,155 C 160,160 175,185 160,210 C 145,230 115,225 105,200 Z"
                fill="url(#warningGrad)"
                stroke="#F97316"
                strokeWidth="1.5"
                strokeDasharray="4 2"
              />
            )}

            {(activeFilter === 'All' || activeFilter === 'Flood') && (
              <path
                d="M 75,260 C 95,240 140,245 155,270 C 175,290 180,330 150,350 C 120,365 75,340 65,300 Z"
                fill="url(#floodGrad)"
                stroke="#3B82F6"
                strokeWidth="1.5"
                strokeDasharray="4 2"
              />
            )}

            {/* Dynamic Evacuation Safe Route Line */}
            {safeRouteActive && (
              <path
                d="M 235,170 C 270,170 310,160 320,130 C 330,100 290,60 290,30"
                fill="none"
                stroke="#10B981"
                strokeWidth="4.5"
                strokeLinecap="round"
                strokeDasharray="8 4"
                className="animate-pulse"
              />
            )}
          </svg>

          {/* Neighborhood Labels */}
          <div className="absolute top-[8%] left-[17%] text-[11px] font-semibold text-gray-500 pointer-events-none">Gota</div>
          <div className="absolute top-[9%] left-[45%] text-[11px] font-semibold text-gray-500 pointer-events-none">Sola</div>
          <div className="absolute top-[6%] left-[60%] text-[11px] font-semibold text-gray-500 pointer-events-none">Chandkheda</div>
          <div className="absolute top-[18%] left-[82%] text-[11px] font-semibold text-gray-500 pointer-events-none">Naroda</div>
          <div className="absolute top-[52%] left-[39%] text-[11px] font-semibold text-gray-500 pointer-events-none">Paldi</div>
          <div className="absolute top-[46%] left-[67%] text-[11px] font-semibold text-gray-500 pointer-events-none">Bapunagar</div>
          <div className="absolute top-[48%] left-[85%] text-[11px] font-semibold text-gray-500 pointer-events-none">Vastral</div>
          <div className="absolute top-[64%] left-[58%] text-[11px] font-semibold text-gray-500 pointer-events-none">Isanpur</div>
          <div className="absolute top-[71%] left-[64%] text-[11px] font-semibold text-gray-500 pointer-events-none">Vatva</div>

          {/* Highway Badges */}
          <div className="absolute top-[23%] left-[13%] bg-[#FACC15] text-[10px] font-bold px-1.5 py-0.5 rounded text-gray-900 border border-yellow-600/30 shadow-2xs">147</div>
          <div className="absolute top-[28%] right-[6%] bg-[#FACC15] text-[10px] font-bold px-1.5 py-0.5 rounded text-gray-900 border border-yellow-600/30 shadow-2xs">48</div>

          {/* River Label */}
          <div className="absolute top-[45%] left-[12%] text-[10px] font-semibold text-sky-700 leading-tight pointer-events-none">
            Sabarmati<br />River
          </div>

          {/* Primary City Anchor */}
          <div className="absolute top-[45%] left-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
            <h2 className="text-base font-extrabold text-gray-900 tracking-tight leading-tight">Ahmedabad</h2>
            <span className="text-sm font-semibold text-gray-700 block">અમદાવાદ</span>
          </div>

          {/* Map Pins */}
          {/* 1. High Risk Alert Pin (North) */}
          <button
            type="button"
            onClick={() => setSelectedPinInfo('High Risk Hazard Zone (North Sola Sector) - Active Waterlogging')}
            className="absolute top-[17%] left-[39%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
          >
            <div className="w-8 h-8 rounded-full bg-red-600 border-2 border-white shadow-lg flex items-center justify-center text-white">
              <span className="text-sm font-black">!</span>
            </div>
          </button>

          {/* 2. Warning Hazard Pin (Mid-West) */}
          <button
            type="button"
            onClick={() => setSelectedPinInfo('Moderate Warning Zone - Fallen electric cables on SG Highway')}
            className="absolute top-[29%] left-[30%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
          >
            <div className="w-7 h-7 rounded-lg bg-[#EA580C] border-2 border-white shadow-md flex items-center justify-center text-white transform rotate-3">
              <AlertTriangle className="w-4 h-4 fill-current" />
            </div>
          </button>

          {/* 3. Flood Marker (South-West) */}
          <button
            type="button"
            onClick={() => setSelectedPinInfo('Submerged Riverbank Zone - Water level 1.8m above danger mark')}
            className="absolute top-[54%] left-[28%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
          >
            <div className="w-8 h-8 rounded-full bg-blue-600 border-2 border-white shadow-md flex items-center justify-center text-white">
              <Waves className="w-4 h-4 stroke-[2.5]" />
            </div>
          </button>

          {/* 4. Shelter Pins */}
          <button
            type="button"
            onClick={onNavigateToShelters}
            className="absolute top-[21%] left-[68%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
            title="Safe Shelter"
          >
            <div className="w-7 h-7 rounded-full bg-[#15803D] border-2 border-white shadow-md flex items-center justify-center text-white">
              <Home className="w-3.5 h-3.5 fill-current" />
            </div>
          </button>
          <button
            type="button"
            onClick={onNavigateToShelters}
            className="absolute top-[55%] left-[69%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
            title="Safe Shelter"
          >
            <div className="w-7 h-7 rounded-full bg-[#15803D] border-2 border-white shadow-md flex items-center justify-center text-white">
              <Home className="w-3.5 h-3.5 fill-current" />
            </div>
          </button>

          {/* 5. Medical Pins */}
          <button
            type="button"
            onClick={onNavigateToMedical}
            className="absolute top-[32%] left-[74%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
            title="Hospital"
          >
            <div className="w-7 h-7 rounded-full bg-[#DC2626] border-2 border-white shadow-md flex items-center justify-center text-white">
              <Plus className="w-3.5 h-3.5 stroke-[3]" />
            </div>
          </button>
          <button
            type="button"
            onClick={onNavigateToMedical}
            className="absolute top-[65%] left-[78%] -translate-x-1/2 -translate-y-1/2 focus:outline-none hover:scale-110 transition-transform"
            title="Hospital"
          >
            <div className="w-7 h-7 rounded-full bg-[#DC2626] border-2 border-white shadow-md flex items-center justify-center text-white">
              <Plus className="w-3.5 h-3.5 stroke-[3]" />
            </div>
          </button>

          {/* User Active Beacon */}
          <div className="absolute top-[34%] left-[55%] -translate-x-1/2 -translate-y-1/2 pointer-events-none">
            <div className="relative flex items-center justify-center">
              <div className="w-12 h-12 rounded-full bg-blue-500/20 animate-beacon absolute" />
              <div className="w-5 h-5 rounded-full bg-white shadow-md flex items-center justify-center z-10">
                <div className="w-3.5 h-3.5 rounded-full bg-[#2563EB]" />
              </div>
            </div>
          </div>
        </div>

        {/* Selected Pin Callout */}
        {selectedPinInfo && (
          <div className="absolute top-4 left-4 right-4 bg-white/95 backdrop-blur-xs p-3 rounded-2xl shadow-lg border border-slate-200 z-30 flex items-center justify-between text-xs animate-in fade-in">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
              <span className="font-semibold text-slate-800 text-[11px] leading-tight">{selectedPinInfo}</span>
            </div>
            <button
              type="button"
              onClick={() => setSelectedPinInfo(null)}
              className="text-slate-400 hover:text-slate-700 text-sm font-bold ml-2"
            >
              ✕
            </button>
          </div>
        )}

        {/* Floating Map Controls */}
        <button
          type="button"
          onClick={() => {
            setZoomLevel(1);
            setSelectedPinInfo('Centered to your GPS location (SG Highway, Ahmedabad)');
          }}
          className="absolute bottom-5 left-4 z-20 bg-white border border-gray-100 shadow-lg px-3.5 py-2 rounded-xl flex items-center space-x-2 active:scale-95 transition-all text-gray-800"
        >
          <Navigation className="w-4 h-4 fill-gray-900" />
          <span className="text-xs font-semibold">My Location</span>
        </button>

        {/* Zoom & Recenter Stack */}
        <div className="absolute bottom-5 right-4 z-20 flex flex-col items-center space-y-2">
          <button
            type="button"
            onClick={() => setZoomLevel(1)}
            aria-label="Re-center position"
            className="w-10 h-10 bg-white rounded-xl shadow-md border border-gray-100 flex items-center justify-center text-gray-700 active:bg-gray-50"
          >
            <Crosshair className="w-5 h-5" />
          </button>
          <div className="w-10 bg-white rounded-xl shadow-md border border-gray-100 flex flex-col divide-y divide-gray-100 overflow-hidden">
            <button
              type="button"
              onClick={() => setZoomLevel((z) => Math.min(z + 0.25, 2))}
              aria-label="Zoom in"
              className="h-9 flex items-center justify-center text-gray-800 text-lg font-bold active:bg-gray-50 leading-none"
            >
              +
            </button>
            <button
              type="button"
              onClick={() => setZoomLevel((z) => Math.max(z - 0.25, 0.8))}
              aria-label="Zoom out"
              className="h-9 flex items-center justify-center text-gray-800 text-lg font-bold active:bg-gray-50 leading-none"
            >
              −
            </button>
          </div>
        </div>

        {/* Distance Scale Indicator */}
        <div className="absolute bottom-2 right-16 z-10 flex flex-col items-center pointer-events-none opacity-80">
          <div className="flex justify-between w-20 text-[9px] font-medium text-gray-600 px-0.5">
            <span>0</span>
            <span>2</span>
            <span>4 km</span>
          </div>
          <div className="w-20 h-1 border-b-2 border-l border-r border-gray-800" />
        </div>
      </main>

      {/* Bottom Sheet Modal: Nearby Alerts */}
      <section className="bg-white rounded-t-[32px] shadow-2xl px-5 pt-3 pb-6 z-40 border-t border-gray-100 shrink-0">
        <div className="w-10 h-1.5 bg-gray-300 rounded-full mx-auto mb-3" />

        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[17px] font-bold tracking-tight text-gray-900">Nearby Alerts</h3>
          <button
            type="button"
            onClick={() => setShowAffectedAreasModal(true)}
            className="inline-flex items-center text-xs font-semibold text-gray-500 hover:text-gray-800"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5 ml-0.5 stroke-[2]" />
          </button>
        </div>

        {/* Alert Card */}
        <article className="bg-gray-50 border border-gray-100 rounded-2xl p-3 flex items-center justify-between mb-3.5 shadow-2xs">
          <div className="flex items-start space-x-3">
            <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0 mt-0.5">
              <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center text-white text-xs font-extrabold">
                !
              </div>
            </div>
            <div className="space-y-0.5 text-left">
              <h4 className="text-sm font-bold text-gray-900 leading-snug">Flood Alert</h4>
              <p className="text-[12px] text-gray-600 leading-snug font-normal line-clamp-1">
                Low-lying areas near Sabarmati at risk of flooding.
              </p>
              <div className="flex items-center space-x-1.5 text-[11px] text-gray-500 pt-0.5">
                <span>2 km away</span>
                <span className="inline-block w-1 h-1 rounded-full bg-gray-400" />
                <span>30 mins ago</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-1 shrink-0 pl-1">
            <span className="bg-[#FEE2E2] text-[#DC2626] text-[11px] font-semibold px-2.5 py-1 rounded-lg">
              High Risk
            </span>
            <ChevronRight className="w-4 h-4 text-gray-400 stroke-[2]" />
          </div>
        </article>

        {/* Primary Action Buttons */}
        <div className="grid grid-cols-2 gap-3 pt-0.5">
          <button
            type="button"
            onClick={() => setShowAffectedAreasModal(true)}
            className="w-full py-3.5 px-3 bg-[#F1F5F9] hover:bg-gray-200 active:scale-[0.98] text-gray-900 rounded-2xl font-bold text-xs flex items-center justify-center space-x-2 transition-all"
          >
            <List className="w-4 h-4" />
            <span>View Affected Areas</span>
          </button>

          <button
            type="button"
            onClick={() => setSafeRouteActive(!safeRouteActive)}
            className={`w-full py-3.5 px-3 rounded-2xl font-bold text-xs flex items-center justify-center space-x-2 shadow-lg transition-all active:scale-[0.98] ${
              safeRouteActive
                ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-500/25'
                : 'bg-red-600 hover:bg-red-700 text-white shadow-red-500/25'
            }`}
          >
            <Navigation className="w-4 h-4 rotate-45" />
            <span>{safeRouteActive ? 'Route Active' : 'Get Safe Route'}</span>
          </button>
        </div>
      </section>

      {/* About Modal */}
      {showAboutModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full shadow-2xl border border-slate-100 text-left">
            <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-3">
              <Info className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">About Disaster Map</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              This system aggregates real-time geographical disaster intelligence from the Gujarat State Disaster Management Authority (GSDMA), Meteorological Department, and verified on-ground citizens.
            </p>
            <div className="bg-slate-50 p-3 rounded-xl my-3 text-[11px] text-slate-600 space-y-1 border border-slate-100">
              <div>• <strong>Red Zones:</strong> Active flash flooding & immediate evacuation</div>
              <div>• <strong>Orange Zones:</strong> Hazard warning & tree/powerline damage</div>
              <div>• <strong>Blue Corridors:</strong> Rising river discharge points</div>
            </div>
            <button
              type="button"
              onClick={() => setShowAboutModal(false)}
              className="w-full py-2.5 bg-slate-900 text-white font-semibold text-xs rounded-xl hover:bg-slate-800"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Affected Areas Modal */}
      {showAffectedAreasModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full shadow-2xl border border-slate-100 text-left">
            <h3 className="text-base font-bold text-slate-900">Affected Zones in Ahmedabad</h3>
            <p className="text-xs text-slate-500 mt-1 mb-3">Last updated 10 minutes ago</p>

            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              <div className="p-2.5 rounded-xl bg-red-50 border border-red-100 text-xs">
                <div className="font-bold text-red-700">North Sola & Ghatlodia Underpass</div>
                <div className="text-[11px] text-slate-600">Water levels 3-4 feet. Avoid travel.</div>
              </div>
              <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-100 text-xs">
                <div className="font-bold text-amber-800">SG Highway & Memnagar Bridge</div>
                <div className="text-[11px] text-slate-600">Heavy congestion due to localized waterlogging.</div>
              </div>
              <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-100 text-xs">
                <div className="font-bold text-blue-800">Sabarmati Riverfront Promenade</div>
                <div className="text-[11px] text-slate-600">Closed for public safety due to dam outflow.</div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setShowAffectedAreasModal(false)}
              className="w-full py-2.5 bg-red-600 text-white font-semibold text-xs rounded-xl hover:bg-red-700 mt-4"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
