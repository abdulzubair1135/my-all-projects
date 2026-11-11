import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, Volume2, Sparkles, Sliders, Radio, Music, Download, RefreshCw, Activity, Layers } from 'lucide-react';

export default function App() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeWaveform, setActiveWaveform] = useState('sine');
  const [frequency, setFrequency] = useState(440);
  const [volume, setVolume] = useState(0.5);
  const [octave, setOctave] = useState(4);
  const [visualizerMode, setVisualizerMode] = useState('spectrum'); // 'spectrum' | 'circular' | 'particles'
  const [activePreset, setActivePreset] = useState('Synth');
  const [statusText, setStatusText] = useState('Ready - Click Play or any Piano Key to start');

  const canvasRef = useRef(null);
  const audioCtxRef = useRef(null);
  const oscRef = useRef(null);
  const gainRef = useRef(null);
  const analyserRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);

  // Initialize Web Audio Context
  const getAudioContext = () => {
    if (!audioCtxRef.current) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(volume, ctx.currentTime);
      gain.connect(analyser);
      analyser.connect(ctx.destination);

      audioCtxRef.current = ctx;
      analyserRef.current = analyser;
      gainRef.current = gain;
    }
    if (audioCtxRef.current.state === 'suspended') {
      audioCtxRef.current.resume();
    }
    return audioCtxRef.current;
  };

  const startTone = (freq) => {
    const ctx = getAudioContext();
    if (oscRef.current) {
      try { oscRef.current.stop(); oscRef.current.disconnect(); } catch (e) {}
    }
    const osc = ctx.createOscillator();
    osc.type = activeWaveform;
    osc.frequency.setValueAtTime(freq || frequency, ctx.currentTime);
    osc.connect(gainRef.current);
    osc.start();
    oscRef.current = osc;
    setIsPlaying(true);
    setStatusText(`Playing: ${activeWaveform.toUpperCase()} at ${Math.round(freq || frequency)} Hz`);
  };

  const stopTone = () => {
    if (oscRef.current) {
      try {
        oscRef.current.stop();
        oscRef.current.disconnect();
      } catch (e) {}
      oscRef.current = null;
    }
    setIsPlaying(false);
    setStatusText('Audio paused');
  };

  const togglePlay = () => {
    if (isPlaying) {
      stopTone();
    } else {
      startTone(frequency);
    }
  };

  // Soundboard Presets
  const presets = [
    { name: 'Synth', wave: 'sawtooth', freq: 440, desc: 'Classic 80s Brass Synth' },
    { name: 'Bass', wave: 'triangle', freq: 110, desc: 'Deep Sub-Bass Rumble' },
    { name: 'Arp', wave: 'square', freq: 660, desc: 'Chiptune Pixel Arpeggio' },
    { name: 'Pad', wave: 'sine', freq: 330, desc: 'Silky Ambient Meditation' },
  ];

  const applyPreset = (p) => {
    setActivePreset(p.name);
    setActiveWaveform(p.wave);
    setFrequency(p.freq);
    if (gainRef.current && audioCtxRef.current) {
      gainRef.current.gain.setValueAtTime(volume, audioCtxRef.current.currentTime);
    }
    if (isPlaying && oscRef.current && audioCtxRef.current) {
      oscRef.current.type = p.wave;
      oscRef.current.frequency.setValueAtTime(p.freq, audioCtxRef.current.currentTime);
    }
    setStatusText(`Preset activated: ${p.name} (${p.desc})`);
  };

  // Keyboard notes
  const notes = [
    { name: 'C', freq: 261.63 },
    { name: 'C#', freq: 277.18, sharp: true },
    { name: 'D', freq: 293.66 },
    { name: 'D#', freq: 311.13, sharp: true },
    { name: 'E', freq: 329.63 },
    { name: 'F', freq: 349.23 },
    { name: 'F#', freq: 369.99, sharp: true },
    { name: 'G', freq: 392.00 },
    { name: 'G#', freq: 415.30, sharp: true },
    { name: 'A', freq: 440.00 },
    { name: 'A#', freq: 466.16, sharp: true },
    { name: 'B', freq: 493.88 },
  ];

  const playNote = (noteFreq) => {
    const adjustedFreq = noteFreq * Math.pow(2, octave - 4);
    setFrequency(adjustedFreq);
    startTone(adjustedFreq);
  };

  // Export Canvas snapshot
  const exportCanvasImage = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = `generative-sound-canvas-${Date.now()}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
    setStatusText('Canvas artwork exported successfully as PNG!');
  };

  // Volume slider update
  const handleVolumeChange = (newVol) => {
    setVolume(newVol);
    if (gainRef.current && audioCtxRef.current) {
      gainRef.current.gain.setValueAtTime(newVol, audioCtxRef.current.currentTime);
    }
  };

  // Frequency slider update
  const handleFreqChange = (newFreq) => {
    setFrequency(newFreq);
    if (isPlaying && oscRef.current && audioCtxRef.current) {
      oscRef.current.frequency.setValueAtTime(newFreq, audioCtxRef.current.currentTime);
    }
  };

  // Waveform change
  const handleWaveformChange = (w) => {
    setActiveWaveform(w);
    if (isPlaying && oscRef.current) {
      oscRef.current.type = w;
    }
  };

  // Generative Canvas Visualizer loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Setup particles for particle mode
    if (particlesRef.current.length === 0) {
      for (let i = 0; i < 70; i++) {
        particlesRef.current.push({
          x: Math.random() * 800,
          y: Math.random() * 300,
          vx: (Math.random() - 0.5) * 1.5,
          vy: (Math.random() - 0.5) * 1.5,
          size: Math.random() * 3 + 1,
          hue: Math.random() * 360,
        });
      }
    }

    let frame = 0;
    const render = () => {
      frame++;
      const width = canvas.width;
      const height = canvas.height;

      // Soft trailing clear for neon glow
      ctx.fillStyle = 'rgba(10, 14, 26, 0.25)';
      ctx.fillRect(0, 0, width, height);

      let dataArray = new Uint8Array(128);
      if (analyserRef.current && isPlaying) {
        analyserRef.current.getByteFrequencyData(dataArray);
      } else {
        // Ambient breathing visualization when paused
        for (let i = 0; i < 128; i++) {
          dataArray[i] = Math.sin(frame * 0.05 + i * 0.1) * 20 + 25;
        }
      }

      if (visualizerMode === 'spectrum') {
        const barWidth = (width / 64);
        for (let i = 0; i < 64; i++) {
          const val = dataArray[i * 2] || 0;
          const barHeight = (val / 255) * (height * 0.85);
          const hue = (i * 5 + frame) % 360;
          const grad = ctx.createLinearGradient(0, height, 0, height - barHeight);
          grad.addColorStop(0, `hsla(${hue}, 90%, 55%, 0.8)`);
          grad.addColorStop(1, `hsla(${hue + 40}, 100%, 75%, 0.95)`);

          ctx.fillStyle = grad;
          ctx.fillRect(i * barWidth, height - barHeight, barWidth - 2, barHeight);

          // Specular cap
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(i * barWidth, height - barHeight - 2, barWidth - 2, 2);
        }
      } else if (visualizerMode === 'circular') {
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.25;

        ctx.save();
        ctx.translate(centerX, centerY);
        const count = 48;
        for (let i = 0; i < count; i++) {
          const angle = (i / count) * Math.PI * 2;
          const val = dataArray[i % 64] || 10;
          const len = (val / 255) * 80 + 10;
          const hue = (i * 7 + frame * 2) % 360;

          ctx.strokeStyle = `hsl(${hue}, 95%, 65%)`;
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
          ctx.lineTo(Math.cos(angle) * (radius + len), Math.sin(angle) * (radius + len));
          ctx.stroke();
        }
        ctx.restore();
      } else {
        // Generative Floating Particles Reacting to Audio
        const avgEnergy = Array.from(dataArray).slice(0, 32).reduce((a, b) => a + b, 0) / 32;
        particlesRef.current.forEach((p) => {
          p.x += p.vx * (1 + avgEnergy / 50);
          p.y += p.vy * (1 + avgEnergy / 50);
          if (p.x < 0) p.x = width;
          if (p.x > width) p.x = 0;
          if (p.y < 0) p.y = height;
          if (p.y > height) p.y = 0;

          const currentSize = p.size + (avgEnergy / 255) * 6;
          ctx.fillStyle = `hsla(${p.hue + frame}, 90%, 65%, 0.8)`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, currentSize, 0, Math.PI * 2);
          ctx.fill();
        });
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    render();
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isPlaying, visualizerMode]);

  return (
    <div className="app-container" style={{ minHeight: '100vh', background: '#090d16', color: '#f8fafc', padding: '24px 32px' }}>
      {/* Header */}
      <header className="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-slate-800/80 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Music className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              Autonomous Audio Synthesizer & Canvas Studio
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Web Audio API
              </span>
            </h1>
            <p className="text-xs text-slate-400">Interactive Generative Sound Waves, Soundboard & 60FPS Reactive Visualizer</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={exportCanvasImage}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-all shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" /> Export Artwork
          </button>
          <button
            onClick={togglePlay}
            className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg ${
              isPlaying
                ? 'bg-rose-500 hover:bg-rose-600 text-white shadow-rose-500/30'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30'
            }`}
          >
            {isPlaying ? <Square className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
            {isPlaying ? 'Stop Synth' : 'Play Synth'}
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Canvas Visualizer & Soundboard */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          {/* Canvas Studio */}
          <div className="relative rounded-2xl bg-slate-900/90 border border-slate-800 p-4 shadow-xl overflow-hidden backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-800/50">
              <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                Real-Time Frequency Canvas
              </span>
              <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-lg border border-slate-700/50 text-[11px]">
                {['spectrum', 'circular', 'particles'].map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setVisualizerMode(mode)}
                    className={`px-2.5 py-1 rounded-md capitalize font-medium transition-all ${
                      visualizerMode === mode
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>

            <canvas
              ref={canvasRef}
              width={760}
              height={280}
              className="w-full h-[280px] rounded-xl bg-slate-950/80 border border-slate-900 shadow-inner"
            />

            <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 px-1">
              <span>{statusText}</span>
              <span className="text-emerald-400 font-mono">60 FPS Render Loop</span>
            </div>
          </div>

          {/* Interactive Keyboard */}
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-300 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-indigo-400" />
                Interactive Touch / Piano Keyboard
              </span>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Octave:</span>
                {[3, 4, 5].map((oct) => (
                  <button
                    key={oct}
                    onClick={() => setOctave(oct)}
                    className={`w-6 h-6 rounded-md font-mono text-xs font-bold transition-all ${
                      octave === oct ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {oct}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-center gap-1.5 overflow-x-auto py-2">
              {notes.map((n) => (
                <button
                  key={n.name}
                  onClick={() => playNote(n.freq)}
                  className={`flex flex-col items-center justify-end pb-3 rounded-xl transition-all shadow-md active:scale-95 ${
                    n.sharp
                      ? 'w-10 h-28 bg-slate-950 text-slate-300 border border-slate-800 hover:bg-slate-900 -mx-3 z-10'
                      : 'w-14 h-40 bg-slate-800/90 text-white border border-slate-700/60 hover:bg-slate-700/80 z-0'
                  }`}
                >
                  <span className="text-xs font-bold">{n.name}</span>
                  <span className="text-[9px] font-mono text-slate-400 mt-1">
                    {Math.round(n.freq * Math.pow(2, octave - 4))}Hz
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Controls & Soundboard Presets */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          {/* Soundboard Presets */}
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Soundboard Presets
            </h3>
            <div className="grid grid-cols-2 gap-2.5">
              {presets.map((p) => (
                <button
                  key={p.name}
                  onClick={() => applyPreset(p)}
                  className={`p-3 rounded-xl border text-left flex flex-col gap-1 transition-all ${
                    activePreset === p.name
                      ? 'bg-indigo-600/20 border-indigo-500/60 text-white shadow-lg shadow-indigo-600/10'
                      : 'bg-slate-800/50 border-slate-700/40 text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <span className="text-xs font-bold">{p.name}</span>
                  <span className="text-[10px] text-slate-400 line-clamp-1">{p.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Synthesizer Waveform Engine */}
          <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-xl flex flex-col gap-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Radio className="w-3.5 h-3.5 text-indigo-400" />
              Oscillator Waveform
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {['sine', 'square', 'sawtooth', 'triangle'].map((w) => (
                <button
                  key={w}
                  onClick={() => handleWaveformChange(w)}
                  className={`py-2 px-3 rounded-xl capitalize text-xs font-bold border transition-all ${
                    activeWaveform === w
                      ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-800/60 border-slate-700/50 text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  {w}
                </button>
              ))}
            </div>

            {/* Frequency Control */}
            <div className="flex flex-col gap-1.5 mt-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Frequency (Pitch)</span>
                <span className="font-mono text-indigo-400 font-bold">{Math.round(frequency)} Hz</span>
              </div>
              <input
                type="range"
                min={65}
                max={1200}
                step={1}
                value={frequency}
                onChange={(e) => handleFreqChange(Number(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
              />
            </div>

            {/* Master Volume */}
            <div className="flex flex-col gap-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Volume2 className="w-3.5 h-3.5" /> Master Volume
                </span>
                <span className="font-mono text-emerald-400 font-bold">{Math.round(volume * 100)}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={volume}
                onChange={(e) => handleVolumeChange(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
