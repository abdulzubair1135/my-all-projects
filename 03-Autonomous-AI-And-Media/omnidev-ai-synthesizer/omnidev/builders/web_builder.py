import time
from pathlib import Path
from typing import Dict, Any
from config import console
from tools.file_manager import FileManager
from tools.process_manager import ProcessManager

class WebsiteBuilder:
    """
    Generates modern, responsive landing pages and websites with Tailwind CSS,
    hero sections, feature grids, responsive navbars, and interactive JavaScript.
    """
    def __init__(self, brain, workspace_dir: Path):
        self.brain = brain
        self.workspace_dir = Path(workspace_dir)

    def build_website(self, prompt: str, site_name: str = "my_website") -> Dict[str, Any]:
        target_dir = self.workspace_dir / site_name
        target_dir.mkdir(parents=True, exist_ok=True)
        file_mgr = FileManager(target_dir)

        console.print(f"[bold cyan]🌐 Building modern website for:[/bold cyan] '{prompt}'")

        web_prompt = f"""You are OmniDev AI, an elite UI/UX Designer and Frontend Developer.

⚠️ CRITICAL OUTPUT RULE — FOLLOW THIS EXACTLY:
Your response MUST start with the following two lines (no other text before them):
FILE: index.html
```html

Then output the complete HTML file, and close with:
```

---

Create a stunning, fully responsive, modern website based on:
"{prompt}"

REQUIREMENTS:
- HTML5 with Tailwind CSS (via CDN: https://cdn.tailwindcss.com)
- Font: Inter / Outfit via Google Fonts
- Icons: Lucide / FontAwesome CDN or SVG icons
- Sections:
  1. Sticky modern navigation bar with logo and CTA
  2. Eye-catching Hero section with headline, subheadline, CTA buttons, and mockups/illustrations
  3. Features / Services grid with glassmorphism cards and hover effects
  4. Testimonials or Statistics counter section
  5. Pricing or FAQ section (with interactive accordion in JS)
  6. Contact form and modern footer
- Modern animations and interactive JavaScript (smooth scrolling, mobile menu toggle, FAQ accordion).
- All features MUST be in one single self-contained index.html file.
"""
        console.print("[magenta]🤖 Asking DeepSeek/Gemini to write complete website...[/magenta]")
        try:
            response = self.brain.ask(web_prompt)
        except Exception as e:
            console.print(f"[yellow]Note: Brain query ({e}), generating modern SaaS landing page...[/yellow]")
            response = ""

        # Extract HTML — multi-layer fallback so we never lose the generated page
        import re
        html_code = ""

        # Layer 1: FILE: index.html tag with optional html fence label
        match = re.search(r"FILE:\s*index\.html\s*```(?:html)?\n(.*?)```", response, re.DOTALL)
        if match:
            html_code = match.group(1).strip()

        # Layer 2: Any ```html ... ``` block (pick the largest one)
        if not html_code:
            blocks = re.findall(r"```html\n(.*?)```", response, re.DOTALL | re.IGNORECASE)
            if blocks:
                html_code = max(blocks, key=len).strip()

        # Layer 3: Generic ``` block that contains <!DOCTYPE html>
        if not html_code:
            blocks = re.findall(r"```[a-z]*\n(.*?)```", response, re.DOTALL | re.IGNORECASE)
            html_blocks = [b for b in blocks if "<!DOCTYPE html>" in b or "<html" in b]
            if html_blocks:
                html_code = max(html_blocks, key=len).strip()

        # Layer 4: Unclosed fence — response was cut off before closing ```
        if not html_code:
            fence_match = re.search(r"```html\n(.*)", response, re.DOTALL | re.IGNORECASE)
            if fence_match and ("<!DOCTYPE html>" in fence_match.group(1) or "<html" in fence_match.group(1)):
                raw = fence_match.group(1)
                end = raw.rfind("</html>")
                html_code = (raw[:end + 7] if end != -1 else raw).strip()

        # Check if extracted code is valid
        if not html_code or len(html_code) < 300 or "No response captured" in html_code:
            html_code = self._get_master_website_template(prompt)

        file_mgr.write_file("index.html", html_code)
        index_file = target_dir / "index.html"
        console.print(f"[green]✓ Website saved to: {index_file}[/green]")

        # Launch preview server
        import sys
        port = ProcessManager.find_free_port(8080)
        cmd = f'"{sys.executable}" -m http.server {port} --bind 127.0.0.1'
        self.process_manager.start_server(name=f"web_{site_name}_{port}", command=cmd, port=port, cwd=target_dir)
        url = f"http://127.0.0.1:{port}"
        console.print(f"[bold green]✅ Website preview running at: {url}[/bold green]")
        
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception:
            pass

        return {
            "success": True,
            "url": url,
            "index_file": str(index_file),
            "directory": str(target_dir)
        }

    def _get_master_website_template(self, prompt: str) -> str:
        """Returns a high-end, responsive modern SaaS landing page."""
        title = prompt.title()[:30]
        return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Next-Gen Platform</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script>
tailwind.config = {{
  darkMode: 'class',
  theme: {{
    extend: {{
      fontFamily: {{ sans: ['Plus Jakarta Sans', 'sans-serif'] }},
      colors: {{
        brand: {{ 50: '#f0f9ff', 500: '#0ea5e9', 600: '#0284c7', 900: '#0c4a6e' }}
      }}
    }}
  }}
}}
</script>
<style>
  .glass {{
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }}
  .glow {{
    box-shadow: 0 0 50px -10px rgba(14, 165, 233, 0.3);
  }}
</style>
</head>
<body class="bg-slate-950 text-slate-100 selection:bg-sky-500 selection:text-white">

<!-- Navigation -->
<header class="sticky top-0 z-50 glass border-b border-slate-800/80">
  <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-white text-xl shadow-lg shadow-sky-500/20">
        <i class="fa-solid fa-bolt"></i>
      </div>
      <span class="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">{title}</span>
    </div>
    <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
      <a href="#features" class="hover:text-sky-400 transition">Features</a>
      <a href="#solutions" class="hover:text-sky-400 transition">Architecture</a>
      <a href="#pricing" class="hover:text-sky-400 transition">Pricing</a>
      <a href="#faq" class="hover:text-sky-400 transition">FAQ</a>
    </nav>
    <div class="flex items-center gap-4">
      <button class="hidden sm:inline-flex text-sm font-semibold text-slate-300 hover:text-white transition">Sign In</button>
      <a href="#pricing" class="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-5 py-2.5 rounded-full text-sm shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 transition">Get Started</a>
    </div>
  </div>
</header>

<!-- Hero Section -->
<section class="relative pt-24 pb-20 overflow-hidden">
  <div class="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-sky-500/15 blur-[120px] rounded-full pointer-events-none"></div>
  <div class="max-w-7xl mx-auto px-6 text-center relative z-10">
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass border border-sky-500/30 text-xs font-semibold text-sky-400 mb-8">
      <span class="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
      Next-Generation Autonomous Intelligence
    </div>
    <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl mx-auto leading-tight md:leading-none mb-8">
      Build, Scale & Automate <span class="bg-clip-text text-transparent bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-400">At Light Speed</span>
    </h1>
    <p class="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
      Empower your engineering workflow with fully autonomous agent orchestration, zero-latency execution, and self-healing memory architecture.
    </p>
    <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
      <a href="#features" class="w-full sm:w-auto bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold px-8 py-4 rounded-xl shadow-xl shadow-sky-500/25 hover:shadow-sky-500/40 transition flex items-center justify-center gap-3">
        <span>Explore Platform</span>
        <i class="fa-solid fa-arrow-right"></i>
      </a>
      <a href="#solutions" class="w-full sm:w-auto glass hover:bg-slate-800 text-slate-200 font-semibold px-8 py-4 rounded-xl border border-slate-700 transition flex items-center justify-center gap-3">
        <i class="fa-solid fa-play text-xs text-sky-400"></i>
        <span>Live Architecture</span>
      </a>
    </div>

    <!-- Stats Bar -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto mt-20 p-6 glass rounded-2xl border border-slate-800">
      <div>
        <div class="text-3xl font-extrabold text-sky-400">30x</div>
        <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Faster Velocity</div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-indigo-400">99.98%</div>
        <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Uptime Reliability</div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-purple-400">&lt; 25ms</div>
        <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Execution Latency</div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-emerald-400">100%</div>
        <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Sandbox Isolated</div>
      </div>
    </div>
  </div>
</section>

<!-- Features Grid -->
<section id="features" class="py-24 bg-slate-900/50 relative">
  <div class="max-w-7xl mx-auto px-6">
    <div class="text-center max-w-3xl mx-auto mb-16">
      <h2 class="text-sm font-bold uppercase tracking-wider text-sky-400 mb-3">Core Capabilities</h2>
      <p class="text-3xl md:text-4xl font-extrabold text-white">Engineered for Sovereign Autonomy</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Card 1 -->
      <div class="glass p-8 rounded-2xl border border-slate-800 hover:border-sky-500/50 transition group">
        <div class="w-12 h-12 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center text-xl mb-6 group-hover:scale-110 transition">
          <i class="fa-solid fa-microchip"></i>
        </div>
        <h3 class="text-xl font-bold text-white mb-3">Finite State Engine</h3>
        <p class="text-slate-400 text-sm leading-relaxed">40-state deterministic state machine ensures predictable transitions and dependency synthesis without hallucination loops.</p>
      </div>

      <!-- Card 2 -->
      <div class="glass p-8 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition group">
        <div class="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xl mb-6 group-hover:scale-110 transition">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <h3 class="text-xl font-bold text-white mb-3">Command Guard Sandbox</h3>
        <p class="text-slate-400 text-sm leading-relaxed">Deep AST security verification pre-screens all shell execution and system mutations to prevent destructive operations.</p>
      </div>

      <!-- Card 3 -->
      <div class="glass p-8 rounded-2xl border border-slate-800 hover:border-purple-500/50 transition group">
        <div class="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center text-xl mb-6 group-hover:scale-110 transition">
          <i class="fa-solid fa-brain"></i>
        </div>
        <h3 class="text-xl font-bold text-white mb-3">Error Memory Vault</h3>
        <p class="text-slate-400 text-sm leading-relaxed">Vectorized SQLite fingerprint memory caches resolved runtime errors for instant automated root-cause healing.</p>
      </div>
    </div>
  </div>
</section>

<!-- Pricing Section -->
<section id="pricing" class="py-24 relative">
  <div class="max-w-7xl mx-auto px-6 text-center">
    <h2 class="text-sm font-bold uppercase tracking-wider text-sky-400 mb-3">Transparent Pricing</h2>
    <p class="text-3xl md:text-4xl font-extrabold text-white mb-16">Choose the Power You Need</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto text-left">
      <!-- Starter -->
      <div class="glass p-8 rounded-2xl border border-slate-800 flex flex-col justify-between">
        <div>
          <div class="text-lg font-bold text-slate-300 mb-2">Developer</div>
          <div class="text-4xl font-extrabold text-white mb-6">$0 <span class="text-sm font-normal text-slate-400">/mo</span></div>
          <ul class="space-y-4 text-sm text-slate-300">
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Full Local Execution</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Standard Toolchain</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Single-Agent Mode</li>
          </ul>
        </div>
        <button class="mt-8 w-full glass hover:bg-slate-800 text-white font-bold py-3 rounded-xl border border-slate-700 transition">Get Started Free</button>
      </div>

      <!-- Pro (Featured) -->
      <div class="glass p-8 rounded-2xl border-2 border-sky-500 glow flex flex-col justify-between relative">
        <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-sky-500 text-slate-950 text-xs font-extrabold uppercase px-3 py-1 rounded-full">Most Popular</div>
        <div>
          <div class="text-lg font-bold text-sky-400 mb-2">Enterprise Team</div>
          <div class="text-4xl font-extrabold text-white mb-6">$49 <span class="text-sm font-normal text-slate-400">/mo</span></div>
          <ul class="space-y-4 text-sm text-slate-300">
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Multi-Agent Swarm Orchestration</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Unlimited Vector Error Memory</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Playwright & Android Hardware Interop</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Priority Local GPU Acceleration</li>
          </ul>
        </div>
        <button class="mt-8 w-full bg-sky-500 hover:bg-sky-400 text-slate-950 font-extrabold py-3 rounded-xl transition shadow-lg shadow-sky-500/30">Start 14-Day Trial</button>
      </div>

      <!-- Custom -->
      <div class="glass p-8 rounded-2xl border border-slate-800 flex flex-col justify-between">
        <div>
          <div class="text-lg font-bold text-slate-300 mb-2">Sovereign Cluster</div>
          <div class="text-4xl font-extrabold text-white mb-6">Custom</div>
          <ul class="space-y-4 text-sm text-slate-300">
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Air-Gapped Deployment</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Custom AST Security Policies</li>
            <li class="flex items-center gap-3"><i class="fa-solid fa-check text-sky-400"></i> Dedicated Support Engineering</li>
          </ul>
        </div>
        <button class="mt-8 w-full glass hover:bg-slate-800 text-white font-bold py-3 rounded-xl border border-slate-700 transition">Contact Sales</button>
      </div>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="border-t border-slate-800/80 py-12 text-center text-sm text-slate-500 glass">
  <div class="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
    <div>© 2026 {title}. Built autonomously with OmniDev OS.</div>
    <div class="flex gap-6">
      <a href="#" class="hover:text-slate-300 transition">Privacy</a>
      <a href="#" class="hover:text-slate-300 transition">Terms</a>
      <a href="#" class="hover:text-slate-300 transition">Documentation</a>
    </div>
  </div>
</footer>

</body>
</html>"""

