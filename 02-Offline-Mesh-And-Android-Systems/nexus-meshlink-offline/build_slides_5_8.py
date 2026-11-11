OUT_PATH = r"c:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Presentation.html"

with open(OUT_PATH, "a", encoding="utf-8") as f:
    f.write("""
    <!-- SLIDE 5 -->
    <section class="slide" data-notes="Now we begin the Phase 2 deep dive. Pillar 1 is Signal-Grade Double Ratchet End-to-End Encryption. Every message generates a fresh ephemeral key, providing Perfect Forward Secrecy. Intermediary relay nodes only see an encrypted binary envelope; they have zero visibility into message content, sender DID, or media attachments.">
      <div class="slide-badge">🔐 Phase 2 Deep Dive: Cryptography</div>
      <h2 class="slide-title">Double Ratchet E2EE & Multi-Hop Relay Blindness</h2>
      <p class="slide-subtitle">Signal-grade mathematical privacy operating on edge Android hardware without trusted third-party key servers.</p>

      <div class="grid-2">
        <div class="card">
          <h3 class="card-title" style="color: var(--accent-light);">🔑 Double Ratchet Algorithm (X3DH)</h3>
          <ul style="margin-left: 20px; line-height: 1.85; color: var(--text-muted); font-size: 0.92rem;">
            <li><strong>Diffie-Hellman + Symmetric KDF:</strong> Fresh keys derived per message exchange.</li>
            <li><strong>Perfect Forward Secrecy (PFS):</strong> Compromising today's key reveals zero historical messages.</li>
            <li><strong>Post-Compromise Break-in Recovery:</strong> Self-healing ratchet keys recover security after interception.</li>
            <li><strong>Android StrongBox TEE:</strong> Cryptographic private seeds never touch unencrypted RAM.</li>
          </ul>
        </div>

        <div class="card">
          <h3 class="card-title" style="color: var(--accent-light);">🛡️ Multi-Hop Relay Blindness</h3>
          <ul style="margin-left: 20px; line-height: 1.85; color: var(--text-muted); font-size: 0.92rem;">
            <li><strong>Zero-Knowledge Relays:</strong> Intermediate hops only inspect outer routing envelope.</li>
            <li><strong>Onion-Routed Packets:</strong> Forwarding hops peel off routing tokens without knowing payload or sender.</li>
            <li><strong>Anti-Forensics Duress PIN:</strong> Entering alternate PIN displays sanitized dummy messages.</li>
            <li><strong>SQLCipher AES-256-GCM:</strong> Local database on device flash storage is encrypted at rest.</li>
          </ul>
        </div>
      </div>

      <div style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
        <span class="chip chip-green">Ed25519 Signing</span>
        <span class="chip chip-green">X25519 Key Agreement</span>
        <span class="chip chip-blue">Onion Encapsulation</span>
        <span class="chip chip-blue">FLAG_SECURE Screen Armor</span>
        <span class="chip chip-green">Hardware Keystore</span>
      </div>
    </section>

    <!-- SLIDE 6 -->
    <section class="slide" data-notes="Phase 2's second milestone is Hardware-Accelerated P2P Audio and Video Calling. Using raw bidirectional PCM audio with the Opus codec, we achieve sub-100ms latency walkie-talkie quality. And by tapping the Android MediaCodec H.264 GPU pipeline, 720p 30fps video calls stream directly between phones over Wi-Fi Direct sockets.">
      <div class="slide-badge">📹 Phase 2 Deep Dive: Real-Time Media</div>
      <h2 class="slide-title">Hardware-Accelerated P2P Voice & Video Calling</h2>
      <p class="slide-subtitle">Direct Wi-Fi Direct UDP sockets deliver sub-100ms latency voice and 720p 30 FPS video without touching cell networks.</p>

      <div class="grid-2">
        <div>
          <div class="card" style="margin-bottom: 18px;">
            <div class="card-icon">📞</div>
            <h3 class="card-title">Crystal-Clear Opus Voice Engine</h3>
            <p class="card-desc">Bidirectional raw PCM audio sampled at 16/48 kHz, compressed using the ultra-low latency Opus codec. Features adaptive jitter buffer compensation and acoustic echo cancellation.</p>
          </div>

          <div class="card">
            <div class="card-icon">📹</div>
            <h3 class="card-title">720p 30 FPS Hardware H.264 Video</h3>
            <p class="card-desc">Direct hardware MediaCodec encoding leveraging onboard GPU pipelines (&lt; 8% CPU usage). Features Picture-in-Picture (PiP) and dynamic bitrate fallback based on signal RSSI.</p>
          </div>
        </div>

        <div class="phone-showcase">
          <div class="phone-mockup">
            <img src="presentation_assets/calls_view_awake.png" alt="Nexus Calls Tab">
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 7 -->
    <section class="slide" data-notes="How do messages cross kilometers when nodes are physically separated? Phase 2 implements Delay-Tolerant Networking (DTN) using 'Digital Mules'. A rescue volunteer walking or driving between two isolated relief camps carries encrypted bundles in flash memory. When they reach the destination zone, the bundles autonomously drop to recipients. SHA-256 deduplication prevents broadcast storms.">
      <div class="slide-badge">📦 Phase 2 Deep Dive: Delay-Tolerant Mesh</div>
      <h2 class="slide-title">Delay-Tolerant Networking (DTN) & "Digital Mules"</h2>
      <p class="slide-subtitle">Asynchronous store-and-forward routing allows encrypted emergency messages to cross physical kilometers across separated clusters.</p>

      <div class="grid-3">
        <div class="card">
          <div class="card-icon">🚶</div>
          <h3 class="card-title">Physical Digital Mules</h3>
          <p class="card-desc">When direct radio connection between Sector A and Sector B is blocked, moving personnel (relief volunteers, vehicles) silently carry encrypted DTN bundles in background flash storage.</p>
        </div>
        <div class="card">
          <div class="card-icon">⚡</div>
          <h3 class="card-title">Autonomous Proximity Drop</h3>
          <p class="card-desc">The moment the carrying device moves within radio range of the destination node or next relay node, the bundle transmits automatically within 120 milliseconds.</p>
        </div>
        <div class="card">
          <div class="card-icon">🛡️</div>
          <h3 class="card-title">Deduplication & Anti-Storm</h3>
          <p class="card-desc">Every packet has a SHA-256 fingerprint cached in memory. If a node has already seen or relayed a packet, it discards duplicates instantly to conserve airtime and battery.</p>
        </div>
      </div>

      <div class="card" style="margin-top: 20px;">
        <h4 style="color: var(--accent); margin-bottom: 6px;">Dynamic TTL (Time-To-Live) Matrix</h4>
        <p style="font-size: 0.92rem; color: var(--text-muted); line-height: 1.55;">
          Packets carry an intelligent hop counter (maximum 7 hops) and an epoch timestamp. Once delivered or expired, a decentralized tombstone acknowledgement is broadcast, prompting all nodes to purge the bundle from storage.
        </p>
      </div>
    </section>

    <!-- SLIDE 8 -->
    <section class="slide" data-notes="This is the live user interface of Nexus. We deliberately avoided complex or confusing sci-fi neon aesthetics. We adopted a clean White, Slate Gray, and Light Green design language inspired by Signal and WhatsApp. This ensures instant readability under harsh direct sunlight, zero learning curve for the general public, and thumb-accessible emergency triggers.">
      <div class="slide-badge">🎨 Tactile Human-Centric UI/UX</div>
      <h2 class="slide-title">Minimalist Interface: Engineered for Stressful Crises</h2>
      <p class="slide-subtitle">Clean White, Slate Gray & Emerald Green palette. Built with thumb-driven ergonomics for one-handed operation in the field.</p>

      <div class="grid-2">
        <div>
          <div class="card" style="margin-bottom: 16px;">
            <h3 class="card-title">☀️ High-Contrast Sunlight Legibility</h3>
            <p class="card-desc">Pure white cards (<code>#FFFFFF</code>) over slate gray canvas (<code>#F8F9FA</code>) with high-contrast emerald green indicators (<code>#16A34A</code>) readable under harsh sunlight during rescue operations.</p>
          </div>
          <div class="card" style="margin-bottom: 16px;">
            <h3 class="card-title">✓✓ WhatsApp-Familiar Delivery Status</h3>
            <p class="card-desc">Triple-check delivery status: Single tick (Dispatched), Double gray ticks (Relayed by mesh), Double green ticks (Decrypted on recipient screen). Zero learning curve for citizens.</p>
          </div>
          <div class="card" style="margin-bottom: 16px;">
            <h3 class="card-title">🚨 Instant Tactical Bottom Controls</h3>
            <p class="card-desc">Floating 2-second hold-to-activate SOS button, quick call pills, radar scanning chip, and one-tap app sharing available directly from the home view.</p>
          </div>
        </div>

        <div class="phone-showcase">
          <div class="phone-mockup">
            <img src="presentation_assets/nexus_main_now.png" alt="Nexus Clean Home UI">
          </div>
        </div>
      </div>
    </section>
""")
print("Slides 5 to 8 appended successfully.")
