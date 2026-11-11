import React, { useState } from 'react';
import {
  ArrowLeft,
  Radio,
  Wifi,
  Smartphone,
  Shield,
  RefreshCw,
  Send,
  CheckCircle,
} from 'lucide-react';

interface OfflineNetworkScreenProps {
  onBack: () => void;
}

export const OfflineNetworkScreen: React.FC<OfflineNetworkScreenProps> = ({ onBack }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [broadcastSent, setBroadcastSent] = useState(false);

  const [peers] = useState([
    { id: '1', name: 'GSDMA Relay Node #04', distance: '120m', battery: '94%', hops: 'Direct', type: 'Node' },
    { id: '2', name: 'Citizen Device (Samsung M34)', distance: '45m', battery: '78%', hops: '1 Hop', type: 'Peer' },
    { id: '3', name: 'NDRF Responder Unit B', distance: '310m', battery: '85%', hops: '2 Hops', type: 'Rescue' },
    { id: '4', name: 'Shelter Hub Gateway', distance: '650m', battery: 'Solar Power', hops: '3 Hops', type: 'Gateway' },
  ]);

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
    }, 1500);
  };

  const handleSendBroadcast = (e: React.FormEvent) => {
    e.preventDefault();
    if (!broadcastMessage.trim()) return;
    setBroadcastSent(true);
    setTimeout(() => {
      setBroadcastSent(false);
      setBroadcastMessage('');
    }, 2500);
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#0F172A] text-white select-none">
      {/* Top Header */}
      <header className="px-5 pt-3 pb-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between shrink-0">
        <button
          type="button"
          onClick={onBack}
          aria-label="Go Back"
          className="p-1 -ml-1 text-slate-300 hover:text-white"
        >
          <ArrowLeft className="w-6 h-6 stroke-[2.2]" />
        </button>
        <div className="text-center">
          <h1 className="text-base font-bold text-white">Peer-to-Peer Mesh Network</h1>
          <p className="text-[11px] text-emerald-400 font-medium">4 Active Nodes in Range</p>
        </div>
        <button
          type="button"
          onClick={handleScan}
          className="p-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-slate-300 active:scale-95"
          title="Rescan peers"
        >
          <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin text-emerald-400' : ''}`} />
        </button>
      </header>

      {/* Main Radar View */}
      <main className="flex-1 overflow-y-auto px-4 py-4 space-y-4 no-scrollbar">
        {/* Radar Graphic */}
        <div className="relative w-full h-52 rounded-3xl bg-slate-900/60 border border-slate-800 flex items-center justify-center overflow-hidden shadow-inner">
          <div className="absolute w-44 h-44 rounded-full border border-slate-700/50" />
          <div className="absolute w-32 h-32 rounded-full border border-slate-700/60" />
          <div className="absolute w-20 h-20 rounded-full border border-emerald-500/30 animate-ping" />

          {/* Central User Node */}
          <div className="relative z-10 w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-500/50">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>

          {/* Connected Peripheral Nodes */}
          <div className="absolute top-10 left-16 text-center animate-bounce">
            <div className="w-6 h-6 rounded-full bg-blue-500 border border-white flex items-center justify-center text-[10px]">
              <Smartphone className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-[9px] text-slate-400">45m</span>
          </div>

          <div className="absolute top-8 right-20 text-center">
            <div className="w-6 h-6 rounded-full bg-amber-500 border border-white flex items-center justify-center text-[10px]">
              <Shield className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-[9px] text-slate-400">310m</span>
          </div>

          <div className="absolute bottom-10 right-14 text-center">
            <div className="w-6 h-6 rounded-full bg-emerald-400 border border-white flex items-center justify-center text-[10px]">
              <Wifi className="w-3.5 h-3.5 text-slate-900" />
            </div>
            <span className="text-[9px] text-slate-400">120m</span>
          </div>
        </div>

        {/* Broadcast Packet Form */}
        <div className="bg-slate-900 p-3.5 rounded-2xl border border-slate-800">
          <h2 className="text-xs font-bold text-slate-200 mb-1 flex items-center space-x-1.5">
            <Radio className="w-4 h-4 text-emerald-400" />
            <span>Broadcast Packet to Mesh (No Internet Needed)</span>
          </h2>
          <p className="text-[10px] text-slate-400 mb-2">
            Messages propagate hop-by-hop across Bluetooth & Wi-Fi Direct until reaching an internet-connected gateway.
          </p>

          <form onSubmit={handleSendBroadcast} className="flex space-x-2">
            <input
              type="text"
              value={broadcastMessage}
              onChange={(e) => setBroadcastMessage(e.target.value)}
              placeholder="e.g. SOS! 3 trapped near underpass..."
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              className="px-3 py-2 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-slate-950 font-bold rounded-xl text-xs flex items-center space-x-1"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Relay</span>
            </button>
          </form>

          {broadcastSent && (
            <div className="mt-2 text-[11px] text-emerald-400 flex items-center space-x-1.5 animate-in fade-in">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Packet relayed across 4 hops to GSDMA command gateway!</span>
            </div>
          )}
        </div>

        {/* Nodes List */}
        <div className="space-y-2">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">Nearby Mesh Relays</div>
          {peers.map((peer) => (
            <div
              key={peer.id}
              className="bg-slate-900/80 border border-slate-800 rounded-2xl p-3 flex items-center justify-between"
            >
              <div className="flex items-center space-x-3">
                <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center text-emerald-400">
                  <Smartphone className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs font-bold text-white">{peer.name}</div>
                  <div className="text-[10px] text-slate-400">
                    {peer.distance} • {peer.hops} • Battery: {peer.battery}
                  </div>
                </div>
              </div>

              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Connected
              </span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};
