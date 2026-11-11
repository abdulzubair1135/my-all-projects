import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft,
  Phone,
  Send,
  Radio,
  MapPin,
  Shield,
  Paperclip,
  CheckCheck,
  AlertTriangle,
} from 'lucide-react';
import { ChatMessage, UserProfile } from '../../types';
import { initialChatMessages } from '../../data/mockData';

interface EmergencyChatScreenProps {
  onBack: () => void;
  userProfile: UserProfile;
}

export const EmergencyChatScreen: React.FC<EmergencyChatScreenProps> = ({ onBack, userProfile }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([...initialChatMessages]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (textToSend?: string) => {
    const content = textToSend || inputText;
    if (!content.trim()) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: userProfile.name,
      senderRole: 'citizen',
      message: content,
      timestamp: 'Just now',
      isMe: true,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputText('');

    // Simulate response from Command Control
    setTimeout(() => {
      const responses = [
        'Command Control acknowledged your message. Team Alpha-3 has noted your coordinates.',
        'Rescue boats are clearing the underpass near your location. Please stay on higher floors.',
        'Emergency supplies and water tankers are en route. Nearest distribution center is Sardar Patel School.',
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      const dispatchMsg: ChatMessage = {
        id: `msg-resp-${Date.now()}`,
        sender: 'GSDMA Disaster Control',
        senderRole: 'responder',
        message: randomResponse,
        timestamp: 'Just now',
        isMe: false,
      };
      setMessages((prev) => [...prev, dispatchMsg]);
    }, 1500);
  };

  const handleSendGPS = () => {
    handleSend('📍 My Live GPS Location: 23.0395° N, 72.5082° E (SG Highway, Bodakdev, Ahmedabad)');
  };

  return (
    <div className="w-full flex-1 flex flex-col justify-between bg-[#F4F6F9] select-none">
      {/* Top Header */}
      <header className="px-4 py-2.5 bg-white border-b border-slate-100 flex items-center justify-between z-20 shrink-0">
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={onBack}
            aria-label="Go Back"
            className="p-1 -ml-1 text-slate-700 hover:text-slate-900"
          >
            <ArrowLeft className="w-6 h-6 stroke-[2.2]" />
          </button>
          <div className="w-9 h-9 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-bold shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          <div className="text-left">
            <h1 className="text-sm font-bold text-slate-900 leading-tight">Emergency Response Desk</h1>
            <div className="flex items-center space-x-1.5 text-[10px] text-emerald-600 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Mesh Relay Connected • GSDMA Squad</span>
            </div>
          </div>
        </div>

        <a
          href="tel:108"
          className="flex items-center space-x-1 px-3 py-1.5 bg-red-50 text-red-600 rounded-full text-xs font-bold border border-red-100 hover:bg-red-100 transition"
        >
          <Phone className="w-3.5 h-3.5 fill-current" />
          <span>108</span>
        </a>
      </header>

      {/* Connectivity Notice */}
      <div className="bg-amber-50 px-4 py-1.5 border-b border-amber-100 flex items-center justify-between text-[11px] text-amber-800 shrink-0">
        <div className="flex items-center space-x-1.5 truncate">
          <Radio className="w-3.5 h-3.5 text-amber-600 animate-pulse shrink-0" />
          <span className="truncate">Bluetooth Peer Relay is active. Messages will sync offline.</span>
        </div>
        <span className="text-[10px] font-bold bg-amber-200/60 px-2 py-0.5 rounded text-amber-900">
          MESH
        </span>
      </div>

      {/* Quick Template Chips */}
      <div className="px-3 py-1.5 bg-white border-b border-slate-100 flex items-center space-x-2 overflow-x-auto no-scrollbar shrink-0 text-xs">
        <button
          type="button"
          onClick={handleSendGPS}
          className="flex items-center space-x-1 px-3 py-1 rounded-full bg-red-50 text-red-600 font-semibold border border-red-100 shrink-0 active:scale-95"
        >
          <MapPin className="w-3 h-3 fill-current" />
          <span>Share GPS</span>
        </button>
        <button
          type="button"
          onClick={() => handleSend('Urgent: Water is rising above 3 feet near my house.')}
          className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 shrink-0 active:scale-95"
        >
          Water Rising
        </button>
        <button
          type="button"
          onClick={() => handleSend('Need immediate medical assistance for an elderly person.')}
          className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 shrink-0 active:scale-95"
        >
          Medical Need
        </button>
        <button
          type="button"
          onClick={() => handleSend('We need drinking water and dry food rations.')}
          className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 font-medium hover:bg-slate-200 shrink-0 active:scale-95"
        >
          Food & Water
        </button>
      </div>

      {/* Messages Thread */}
      <main className="flex-1 overflow-y-auto px-4 py-3 space-y-3 text-xs no-scrollbar">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.isMe ? 'items-end' : 'items-start'}`}
          >
            <div className="flex items-center space-x-1.5 mb-1 text-[10px] text-slate-500">
              <span className="font-semibold text-slate-700">{msg.sender}</span>
              {msg.senderRole === 'responder' && (
                <span className="bg-red-100 text-red-600 px-1.5 py-0.2 rounded font-bold text-[9px]">
                  OFFICIAL
                </span>
              )}
              <span>•</span>
              <span>{msg.timestamp}</span>
            </div>

            <div
              className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 shadow-2xs leading-relaxed ${
                msg.isMe
                  ? 'bg-red-600 text-white rounded-tr-xs'
                  : msg.senderRole === 'responder'
                  ? 'bg-white border border-red-100 text-slate-900 rounded-tl-xs shadow-xs'
                  : 'bg-white border border-slate-100 text-slate-800 rounded-tl-xs'
              }`}
            >
              <p className="text-xs">{msg.message}</p>
              {msg.isMe && (
                <div className="flex justify-end mt-1 text-white/80">
                  <CheckCheck className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Form Footer */}
      <footer className="p-3 bg-white border-t border-slate-100 shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-2"
        >
          <button
            type="button"
            onClick={handleSendGPS}
            title="Attach GPS Location"
            className="w-10 h-10 rounded-xl bg-slate-100 text-slate-600 hover:text-slate-900 flex items-center justify-center shrink-0"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type emergency message or coordinate..."
            className="flex-1 bg-slate-100/80 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-red-500 focus:bg-white border border-transparent focus:border-red-400"
          />

          <button
            type="submit"
            disabled={!inputText.trim()}
            className="w-10 h-10 rounded-xl bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white flex items-center justify-center shrink-0 shadow-md shadow-red-200 active:scale-95 transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </footer>
    </div>
  );
};
