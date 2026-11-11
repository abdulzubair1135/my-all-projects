OUT_PATH = r"c:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Presentation.html"

with open(OUT_PATH, "a", encoding="utf-8") as f:
    f.write("""
    <!-- SLIDE 9 -->
    <section class="slide" data-notes="Now entering Phase 3. Pillar 1 is the Laptop Edge Supernode. In a relief camp, a laptop acts as a local server hub running on port 8888. Our mobile browser automatically discovers and connects to it without typing IP addresses. The laptop hosts offline Kiwix medical encyclopedias, OpenStreetMap vector tiles, and an interactive Incident Command Dashboard.">
      <div class="slide-badge">💻 Phase 3 Deep Dive: Edge Supernode</div>
      <h2 class="slide-title">Laptop Supernodes & Offline Knowledge Hub</h2>
      <p class="slide-subtitle">Field laptops with high-gain Wi-Fi serve as decentralized edge servers, providing complete encyclopedias, mapping, and incident management.</p>

      <div class="grid-2">
        <div>
          <div class="card" style="margin-bottom: 16px;">
            <div class="card-icon">⚡</div>
            <h3 class="card-title">Auto-Connect Offline Browser</h3>
            <p class="card-desc">Phones automatically probe local candidates (<code>127.0.0.1:8888</code>) upon opening the Browser tab. Zero IP typing or port configuration required by end users.</p>
          </div>
          <div class="card" style="margin-bottom: 16px;">
            <div class="card-icon">📖</div>
            <h3 class="card-title">Offline Medical & Survival Wikipedia</h3>
            <p class="card-desc">Laptop hosts full Kiwix ZIM archives of medical first aid, disaster response procedures, and emergency engineering guides searchable offline.</p>
          </div>
          <div class="card">
            <div class="card-icon">🗺️</div>
            <h3 class="card-title">Offline Vector Map Tile Server</h3>
            <p class="card-desc">Serves OpenStreetMap high-resolution vector tiles locally, allowing field rescue teams to navigate streets and terrain without satellite data.</p>
          </div>
        </div>

        <div class="phone-showcase">
          <div class="phone-mockup">
            <img src="presentation_assets/nexus_browser_view.png" alt="Nexus Offline Browser Station">
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 10 -->
    <section class="slide" data-notes="Phase 3 Pillar 2 introduces the Autonomous Disaster Grid. This includes Dead-Man's Digital Geo-Drops — encrypted messages pinned to GPS coordinates that only decrypt when a responder physically enters that bounding box. It also features standardized 64-byte START medical triage micro-packets and acoustic sirens to locate victims trapped under debris.">
      <div class="slide-badge">🚨 Phase 3 Deep Dive: Disaster Tools</div>
      <h2 class="slide-title">Dead-Man's Geo-Drops, START Triage & Hazard Mapping</h2>
      <p class="slide-subtitle">Equipping disaster rescue personnel (NDRF/SDRF) with military-grade autonomous field coordination tools.</p>

      <div class="grid-3">
        <div class="card">
          <div class="card-icon">📍</div>
          <h3 class="card-title">Dead-Man's Geo-Drop</h3>
          <p class="card-desc">Responders can drop an encrypted mission objective or supply coordinate at a GPS pin. The message remains encrypted across the mesh until a responder physically enters that bounding radius.</p>
        </div>
        <div class="card">
          <div class="card-icon">🩺</div>
          <h3 class="card-title">START Disaster Triage</h3>
          <p class="card-desc">Standardized Simple Triage (Green/Yellow/Red/Black) compressed into a 64-byte micro-packet. Transmits medical priorities across BLE in under 50ms without network overhead.</p>
        </div>
        <div class="card">
          <div class="card-icon">⚠️</div>
          <h3 class="card-title">Offline Hazard Mapping</h3>
          <p class="card-desc">Responders pin localized dangers (downed high-voltage powerlines, flooded underpasses, collapsed bridges) propagating live vector hazard warnings to all nearby civilian nodes.</p>
        </div>
      </div>

      <div class="grid-2" style="margin-top: 20px;">
        <div class="card">
          <h4 style="color: var(--accent); margin-bottom: 6px;">🔊 Acoustic Rescue Beacon (2.8 kHz)</h4>
          <p style="font-size: 0.9rem; color: var(--text-muted);">Pulsed high-frequency audio generated directly on speaker hardware to guide search dogs and rescue squads through concrete rubble.</p>
        </div>
        <div class="card">
          <h4 style="color: var(--accent); margin-bottom: 6px;">🔦 Optical Morse Distress Strobe</h4>
          <p style="font-size: 0.9rem; color: var(--text-muted);">Camera LED strobes international Morse code <code>... --- ...</code> with synchronized high-visibility display flash visible over 500 meters at night.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 11 -->
    <section class="slide" data-notes="Perhaps the most powerful capability of Phase 3 is Asymmetric Gateway Bridging. If an entire disaster sector of 10,000 citizens has zero connectivity, but a single emergency vehicle gets momentary Starlink or perimeter cellular uplink, all queued distress packets across the entire mesh are safely bridged to disaster relief HQ.">
      <div class="slide-badge">🛰️ Phase 3 Deep Dive: Global Bridging</div>
      <h2 class="slide-title">Asynchronous Satellite & Gateway Bridging</h2>
      <p class="slide-subtitle">When 99% of nodes have zero internet, a single fleeting uplink bridges the entire mesh to the global world.</p>

      <div class="card" style="margin-bottom: 20px; padding: 24px; background: rgba(18, 24, 38, 0.95);">
        <div style="display: flex; justify-content: space-between; align-items: center; text-align: center; gap: 14px; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 150px;">
            <div style="font-size: 2rem;">📱</div>
            <strong style="color: #FFF; display: block; margin-top: 6px;">Trapped Survivors</strong>
            <span style="font-size: 0.78rem; color: var(--danger);">100% Offline Mesh</span>
          </div>
          <div style="color: var(--accent); font-weight: bold; font-size: 1.1rem;">─── Encrypted SOS ───►</div>
          <div style="flex: 1; min-width: 150px;">
            <div style="font-size: 2rem;">🏃</div>
            <strong style="color: #FFF; display: block; margin-top: 6px;">Moving Volunteers</strong>
            <span style="font-size: 0.78rem; color: var(--warning);">DTN Store & Forward</span>
          </div>
          <div style="color: var(--accent); font-weight: bold; font-size: 1.1rem;">─── BLE Relay ───►</div>
          <div style="flex: 1; min-width: 150px;">
            <div style="font-size: 2rem;">🚙</div>
            <strong style="color: #FFF; display: block; margin-top: 6px;">Gateway Vehicle</strong>
            <span style="font-size: 0.78rem; color: var(--accent);">Starlink / 5G Perimeter</span>
          </div>
          <div style="color: var(--accent); font-weight: bold; font-size: 1.1rem;">─── Secure Uplink ───►</div>
          <div style="flex: 1; min-width: 150px;">
            <div style="font-size: 2rem;">🌐</div>
            <strong style="color: #FFF; display: block; margin-top: 6px;">Disaster Relief HQ</strong>
            <span style="font-size: 0.78rem; color: var(--blue);">Helicopter Dispatch</span>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <h3 class="card-title">🛡️ Cryptographic Integrity Maintained</h3>
          <p class="card-desc">The gateway node cannot tamper with or read message contents; it acts purely as a signed cryptographic pipe uploading verified packets to disaster relief headquarters.</p>
        </div>
        <div class="card">
          <h3 class="card-title">🔋 Battery-Adaptive Duty Cycling</h3>
          <p class="card-desc">When a node's battery level drops below 20%, the scanning duty cycle throttles from 100% to 15%, conserving survival standby power for up to 48 additional operating hours.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 12 -->
    <section class="slide" data-notes="In conclusion, Nexus provides an unbreakable survival layer for the modern world. Phase 1 is complete and tested live. Phase 2 brings double-ratchet cryptography and Wi-Fi Direct calling. And Phase 3 unlocks the autonomous disaster grid and satellite gateway. I will now demonstrate the live application running on our test hardware. Thank you!">
      <div class="slide-badge">🚀 82-Feature Milestone Master Roadmap</div>
      <h2 class="slide-title">Roadmap & Live Hardware Demonstration</h2>
      <p class="slide-subtitle">Shaikh Abdul Zubair Abdul Kabir • SRK Institute of Management and Computer Application • NEXUS</p>

      <div class="grid-3">
        <div class="card" style="border-top: 3px solid var(--accent);">
          <span class="chip chip-green">MILESTONE 1 (COMPLETED ✅)</span>
          <h3 class="card-title" style="margin-top: 8px;">Core Protocol & Identity</h3>
          <ul style="margin-left: 18px; line-height: 1.75; color: var(--text-muted); font-size: 0.88rem;">
            <li>Hardware DID Keypair (Zero-Login)</li>
            <li>BLE 5.0 Gossip Relay Protocol</li>
            <li>Direct WhatsApp/Bluetooth APK Share</li>
            <li>Auto-Connected Offline Browser</li>
            <li>Tactical Siren & Optical Morse Strobe</li>
            <li>Minimalist WhatsApp-Style Theme</li>
          </ul>
        </div>

        <div class="card" style="border-top: 3px solid var(--warning);">
          <span class="chip" style="background: rgba(245, 158, 11, 0.15); color: #FDE68A;">MILESTONE 2 (PHASE 2 ⏳)</span>
          <h3 class="card-title" style="margin-top: 8px;">Hardware Crypto & P2P Media</h3>
          <ul style="margin-left: 18px; line-height: 1.75; color: var(--text-muted); font-size: 0.88rem;">
            <li>Signal-Grade Double Ratchet E2EE</li>
            <li>Hardware 720p H.264 P2P Video Calls</li>
            <li>Low-latency Opus bidirectional audio</li>
            <li>Delay-Tolerant Store-and-Forward Mules</li>
            <li>Sonar Radar Scanner with dBm Heatmap</li>
            <li>Web-of-Trust (WoT) Peer Verification</li>
          </ul>
        </div>

        <div class="card" style="border-top: 3px solid var(--blue);">
          <span class="chip chip-blue">MILESTONE 3 (PHASE 3 🔭)</span>
          <h3 class="card-title" style="margin-top: 8px;">Autonomous Grid & Uplink</h3>
          <ul style="margin-left: 18px; line-height: 1.75; color: var(--text-muted); font-size: 0.88rem;">
            <li>Dead-Man's GPS Geo-Drops</li>
            <li>START Medical Triage Micro-Packets</li>
            <li>Laptop Supernode & Offline Kiwix Hub</li>
            <li>Asymmetric Satellite Gateway Bridging</li>
            <li>Battery-Adaptive 15% Duty Cycling</li>
            <li>Decentralized Incident Dispatch GUI</li>
          </ul>
        </div>
      </div>

      <div class="card" style="margin-top: 20px; background: rgba(16, 185, 129, 0.1); border-color: var(--accent); display: flex; justify-content: space-between; align-items: center; padding: 18px 28px;">
        <div>
          <h4 style="color: #FFF; font-size: 1.15rem; margin-bottom: 4px;">🎯 Ready for Live Device Demonstration</h4>
          <p style="color: var(--accent-light); font-size: 0.95rem;">Presented by <strong>Shaikh Abdul Zubair Abdul Kabir</strong> • SRK Institute of Management and Computer Application</p>
        </div>
        <button class="btn-nav btn-accent" style="padding: 10px 22px; font-size: 0.95rem;" onclick="alert('Proceeding to live demonstration on Android phone!')">
          📱 Launch Live Demo
        </button>
      </div>
    </section>

  </main>

  <aside class="notes-drawer" id="notesDrawer">
    <div class="notes-title">
      <span>🎙️ Presenter Script (Shaikh Abdul Zubair)</span>
      <span style="font-size: 0.8rem; color: var(--text-muted);">Press 'N' or toggle button</span>
    </div>
    <div class="notes-content" id="notesContent">Loading presenter notes...</div>
  </aside>

  <footer class="dock-bar">
    <button class="dock-btn" id="btnPrev" title="Previous Slide [←]">❮</button>
    <span class="slide-counter" id="slideCounter">01 / 12</span>
    <button class="dock-btn" id="btnNext" title="Next Slide [→]">❯</button>
  </footer>

  <script>
    const slides = document.querySelectorAll('.slide');
    const progressBar = document.getElementById('progressBar');
    const slideCounter = document.getElementById('slideCounter');
    const notesDrawer = document.getElementById('notesDrawer');
    const notesContent = document.getElementById('notesContent');
    const btnToggleNotes = document.getElementById('btnToggleNotes');
    const btnFullscreen = document.getElementById('btnFullscreen');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const btnNextHeader = document.getElementById('btnNextHeader');

    let currentSlide = 0;
    const totalSlides = slides.length;

    function updateSlide(index) {
      if (index < 0) index = 0;
      if (index >= totalSlides) index = totalSlides - 1;
      currentSlide = index;

      slides.forEach((slide, i) => {
        slide.classList.remove('active', 'prev');
        if (i === currentSlide) {
          slide.classList.add('active');
        } else if (i < currentSlide) {
          slide.classList.add('prev');
        }
      });

      const progressPercent = ((currentSlide + 1) / totalSlides) * 100;
      progressBar.style.width = `${progressPercent}%`;
      slideCounter.textContent = `${String(currentSlide + 1).padStart(2, '0')} / ${String(totalSlides).padStart(2, '0')}`;

      const activeSlide = slides[currentSlide];
      const notes = activeSlide.getAttribute('data-notes') || 'No speaker notes for this slide.';
      notesContent.textContent = notes;
    }

    function nextSlide() {
      if (currentSlide < totalSlides - 1) updateSlide(currentSlide + 1);
    }

    function prevSlide() {
      if (currentSlide > 0) updateSlide(currentSlide - 1);
    }

    function toggleNotes() {
      notesDrawer.classList.toggle('open');
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => alert(err.message));
      } else {
        document.exitFullscreen();
      }
    }

    btnNext.addEventListener('click', nextSlide);
    btnNextHeader.addEventListener('click', nextSlide);
    btnPrev.addEventListener('click', prevSlide);
    btnToggleNotes.addEventListener('click', toggleNotes);
    btnFullscreen.addEventListener('click', toggleFullscreen);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        nextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp' || e.key === 'Backspace') {
        prevSlide();
      } else if (e.key === 'n' || e.key === 'N') {
        toggleNotes();
      } else if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
      } else if (e.key === 'Home') {
        updateSlide(0);
      } else if (e.key === 'End') {
        updateSlide(totalSlides - 1);
      }
    });

    updateSlide(0);
  </script>
</body>
</html>
""")
print("Slides 9 to 12 and full scripts appended successfully.")
