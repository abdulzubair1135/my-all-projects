import React from 'react';
import { Navigation, MapPin, X, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

interface DirectionsModalProps {
  destinationName: string;
  destinationArea: string;
  distance: string;
  onClose: () => void;
  onOpenMap: () => void;
}

export const DirectionsModal: React.FC<DirectionsModalProps> = ({
  destinationName,
  destinationArea,
  distance,
  onClose,
  onOpenMap,
}) => {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-4 z-50 animate-in fade-in">
      <div className="bg-white rounded-t-3xl sm:rounded-3xl p-5 w-full max-w-md shadow-2xl border border-slate-100 text-left">
        <div className="flex items-start justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-2xl bg-red-600 text-white flex items-center justify-center shadow-md">
              <Navigation className="w-5 h-5 fill-current" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 leading-tight">{destinationName}</h3>
              <p className="text-xs text-slate-500">{destinationArea} • {distance}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close directions"
            className="p-1 text-slate-400 hover:text-slate-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Hazard Route Status */}
        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 my-3 flex items-center space-x-2.5 text-xs text-emerald-800">
          <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <span className="font-bold">Safe Route Verified:</span> Low risk of flood waterlogging along Sarkhej-Gandhinagar corridor.
          </div>
        </div>

        {/* Turn by Turn */}
        <div className="space-y-2 text-xs text-slate-700 my-3">
          <div className="flex items-start space-x-2.5">
            <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-700 shrink-0 mt-0.5">
              1
            </div>
            <div>
              <p className="font-semibold text-slate-900">Head North on SG Highway</p>
              <p className="text-[11px] text-slate-500">Continue for 1.2 km towards Thaltej Underpass</p>
            </div>
          </div>
          <div className="flex items-start space-x-2.5">
            <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-bold text-slate-700 shrink-0 mt-0.5">
              2
            </div>
            <div>
              <p className="font-semibold text-slate-900">Take elevated flyover (Avoid ground lane)</p>
              <p className="text-[11px] text-slate-500">Stay in right lane for 800 meters</p>
            </div>
          </div>
          <div className="flex items-start space-x-2.5">
            <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center text-[10px] font-bold text-red-600 shrink-0 mt-0.5">
              <MapPin className="w-3 h-3 fill-current" />
            </div>
            <div>
              <p className="font-semibold text-slate-900">Arrive at destination</p>
              <p className="text-[11px] text-slate-500">{destinationName} will be on your left</p>
            </div>
          </div>
        </div>

        {/* Estimated Time */}
        <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl mb-4 text-xs">
          <div className="flex items-center space-x-1.5 text-slate-600">
            <Clock className="w-4 h-4" />
            <span>Estimated Drive: <strong>8-12 mins</strong></span>
          </div>
          <span className="text-[11px] font-semibold text-emerald-600">No severe roadblocks</span>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50"
          >
            Close
          </button>
          <button
            type="button"
            onClick={() => {
              onClose();
              onOpenMap();
            }}
            className="flex-1 py-2.5 rounded-xl bg-red-600 text-white text-xs font-bold hover:bg-red-700 flex items-center justify-center space-x-1 shadow-md shadow-red-200"
          >
            <Navigation className="w-3.5 h-3.5 fill-current" />
            <span>View on Disaster Map</span>
          </button>
        </div>
      </div>
    </div>
  );
};
