# Builder for Nexus Master Deck
import os

OUT_PATH = r"c:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Presentation.html"

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NEXUS - Phase 2 & 3 Master Deck | Shaikh Abdul Zubair</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-main: #0B0F19;
      --bg-card: rgba(18, 24, 38, 0.82);
      --bg-card-hover: rgba(28, 36, 56, 0.92);
      --border: rgba(255, 255, 255, 0.1);
      --accent: #10B981;
      --accent-glow: rgba(16, 185, 129, 0.28);
      --accent-light: #D1FAE5;
      --text-main: #F9FAFB;
      --text-muted: #9CA3AF;
      --danger: #EF4444;
      --warning: #F59E0B;
      --blue: #3B82F6;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: var(--bg-main);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      user-select: none;
    }
    .ambient-glow {
      position: absolute; width: 650px; height: 650px;
      background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
      top: 5%; left: 10%; border-radius: 50%; filter: blur(90px); z-index: 0; pointer-events: none;
      animation: pulse 12s infinite alternate ease-in-out;
    }
    .ambient-glow-2 {
      position: absolute; width: 550px; height: 550px;
      background: radial-gradient(circle, rgba(59, 130, 246, 0.18) 0%, transparent 70%);
      bottom: 5%; right: 10%; border-radius: 50%; filter: blur(90px); z-index: 0; pointer-events: none;
    }
    @keyframes pulse { 0% { transform: scale(1); } 100% { transform: scale(1.15) translate(40px, 30px); } }
    .top-nav {
      position: fixed; top: 0; left: 0; right: 0; height: 64px;
      display: flex; align-items: center; justify-content: space-between; padding: 0 32px;
      background: rgba(11, 15, 25, 0.85); backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border); z-index: 50;
    }
    .brand { display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 1.25rem; }
    .brand-logo {
      width: 34px; height: 34px; background: var(--accent); border-radius: 50%;
      display: flex; align-items: center; justify-content: center; color: #064E3B;
      font-weight: 900; font-size: 1.1rem; box-shadow: 0 0 16px var(--accent-glow);
    }
    .brand-tag {
      font-size: 0.75rem; padding: 3px 10px; background: rgba(16, 185, 129, 0.15);
      color: var(--accent); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px;
      font-weight: 600; text-transform: uppercase;
    }
    .progress-container { flex: 1; max-width: 380px; margin: 0 28px; height: 5px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden; }
    .progress-bar { height: 100%; background: linear-gradient(90deg, var(--accent), #3B82F6); width: 8%; transition: width 0.35s ease; }
    .nav-controls { display: flex; align-items: center; gap: 10px; }
    .btn-nav {
      background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border); color: var(--text-main);
      padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer;
      display: flex; align-items: center; gap: 6px; transition: all 0.2s ease;
    }
    .btn-nav:hover { background: rgba(255, 255, 255, 0.12); border-color: rgba(255, 255, 255, 0.25); }
    .btn-accent { background: var(--accent); color: #064E3B; border-color: var(--accent); box-shadow: 0 0 14px var(--accent-glow); }
    .btn-accent:hover { background: #34D399; color: #064E3B; }
    .deck-container { position: relative; width: 100vw; height: calc(100vh - 64px); margin-top: 64px; overflow: hidden; z-index: 10; }
    .slide {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; padding: 40px 60px 80px;
      display: flex; flex-direction: column; justify-content: center; opacity: 0; pointer-events: none;
      transform: translateX(60px); transition: all 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .slide.active { opacity: 1; pointer-events: auto; transform: translateX(0); }
    .slide.prev { transform: translateX(-60px); }
    .slide-badge { display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
    .slide-title {
      font-size: 2.6rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.15; margin-bottom: 12px;
      background: linear-gradient(135deg, #FFFFFF 30%, #9CA3AF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .slide-subtitle { font-size: 1.15rem; color: var(--text-muted); line-height: 1.55; max-width: 900px; margin-bottom: 24px; }
    .grid-2 { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 32px; align-items: center; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
    .card {
      background: var(--bg-card); backdrop-filter: blur(14px); border: 1px solid var(--border);
      border-radius: 14px; padding: 22px; transition: all 0.3s ease; position: relative; overflow: hidden;
    }
    .card:hover { background: var(--bg-card-hover); border-color: rgba(255, 255, 255, 0.22); transform: translateY(-3px); }
    .card-icon {
      width: 42px; height: 42px; background: rgba(16, 185, 129, 0.12); color: var(--accent);
      border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;
      margin-bottom: 14px; border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .card-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; color: #FFF; }
    .card-desc { font-size: 0.9rem; color: var(--text-muted); line-height: 1.55; }
    .phone-showcase { display: flex; justify-content: center; align-items: center; }
    .phone-mockup {
      width: 260px; height: 520px; background: #000; border-radius: 34px; border: 5px solid #222B3D;
      box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.8), 0 0 25px var(--accent-glow); overflow: hidden;
    }
    .phone-mockup img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .chip {
      display: inline-flex; align-items: center; gap: 6px; font-size: 0.78rem; padding: 4px 10px;
      border-radius: 16px; background: rgba(255, 255, 255, 0.08); color: #E5E7EB; border: 1px solid rgba(255, 255, 255, 0.12);
      margin-right: 6px; margin-bottom: 8px; font-weight: 600;
    }
    .chip-green { background: rgba(16, 185, 129, 0.18); color: var(--accent-light); border-color: rgba(16, 185, 129, 0.35); }
    .chip-blue { background: rgba(59, 130, 246, 0.18); color: #BFDBFE; border-color: rgba(59, 130, 246, 0.35); }
    .spec-table { width: 100%; border-collapse: separate; border-spacing: 0; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); overflow: hidden; }
    .spec-table th {
      background: rgba(255, 255, 255, 0.05); color: var(--text-muted); font-weight: 600; font-size: 0.82rem;
      text-transform: uppercase; letter-spacing: 0.05em; padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--border);
    }
    .spec-table td { padding: 12px 14px; font-size: 0.9rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: #E5E7EB; }
    .spec-table tr:last-child td { border-bottom: none; }
    .notes-drawer {
      position: fixed; bottom: 0; left: 0; right: 0; background: rgba(15, 23, 42, 0.96); backdrop-filter: blur(20px);
      border-top: 2px solid var(--accent); padding: 18px 48px; max-height: 200px; overflow-y: auto;
      transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); z-index: 60;
      box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.5);
    }
    .notes-drawer.open { transform: translateY(0); }
    .notes-title {
      font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--accent); margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;
    }
    .notes-content { font-size: 1rem; line-height: 1.65; color: #F1F5F9; }
    .dock-bar {
      position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
      display: flex; align-items: center; gap: 16px; background: rgba(18, 24, 38, 0.9); backdrop-filter: blur(16px);
      border: 1px solid var(--border); padding: 6px 18px; border-radius: 40px; z-index: 50;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
    }
    .dock-btn {
      background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1rem;
      display: flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 50%; transition: all 0.2s ease;
    }
    .dock-btn:hover { color: #FFF; background: rgba(255, 255, 255, 0.12); }
    .slide-counter { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 600; color: var(--accent-light); padding: 0 8px; }
    .author-card {
      display: flex; align-items: center; gap: 16px; padding: 16px 20px; background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border); border-radius: 12px; margin-top: 18px; max-width: 720px;
    }
    .author-avatar {
      width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, var(--accent), #3B82F6);
      display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.2rem; color: #064E3B;
    }
  </style>
</head>
<body>
  <div class="ambient-glow"></div>
  <div class="ambient-glow-2"></div>
  <header class="top-nav">
    <div class="brand">
      <div class="brand-logo">N</div>
      <span>NEXUS</span>
      <span class="brand-tag">Phase 2 & 3 Master Deck</span>
    </div>
    <div class="progress-container">
      <div class="progress-bar" id="progressBar"></div>
    </div>
    <div class="nav-controls">
      <button class="btn-nav" id="btnToggleNotes">🎙️ Speaker Notes [N]</button>
      <button class="btn-nav" id="btnFullscreen">⛶ Fullscreen [F]</button>
      <button class="btn-nav btn-accent" id="btnNextHeader">Next Slide →</button>
    </div>
  </header>
  <main class="deck-container">
""")
print("Part 1 written successfully.")
