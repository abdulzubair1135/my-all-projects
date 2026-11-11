OUT_PATH = r"c:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Presentation.html"

with open(OUT_PATH, "a", encoding="utf-8") as f:
    f.write("""
    <!-- SLIDE 1 -->
    <section class="slide active" data-notes="Respected faculty and audience, good day. My name is Shaikh Abdul Zubair Abdul Kabir from SRK Institute of Management and Computer Application. Today I present our sovereign, decentralized project: NEXUS (MeshLink Offline). In emergencies or disasters when cellular networks fail, Nexus turns every smartphone into an encrypted radio mesh node that enables messaging, calling, and rescue without touching the internet.">
      <div class="slide-badge">⚡ Autonomous Offline Mesh Communication Grid</div>
      <h1 class="slide-title">NEXUS: MeshLink Offline</h1>
      <p class="slide-subtitle">
        A Zero-Cloud, Zero-OTP, Hardware-Backed Cryptographic Peer-to-Peer Mesh Network for Tactical Survival and Disaster Relief.
      </p>

      <div class="author-card">
        <div class="author-avatar">AZ</div>
        <div>
          <div style="font-size: 1.15rem; font-weight: 700; color: #FFF;">Shaikh Abdul Zubair Abdul Kabir</div>
          <div style="font-size: 0.92rem; color: var(--accent); font-weight: 600;">SRK Institute of Management and Computer Application</div>
          <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 2px;">Product: <strong>NEXUS</strong> • Platform: Android Native (Java/C++) • 100% Offline</div>
        </div>
      </div>

      <div class="grid-4" style="margin-top: 22px;">
        <div class="card">
          <div class="card-icon">🔑</div>
          <h3 class="card-title">Zero-Login Identity</h3>
          <p class="card-desc">Hardware-backed Ed25519 cryptographic keypair generated in 2 seconds. No phone number or cloud signup.</p>
        </div>
        <div class="card">
          <div class="card-icon">📡</div>
          <h3 class="card-title">Tri-Transport Mesh</h3>
          <p class="card-desc">BLE 5.0 Gossip Relay for passive multi-hop range, promoting seamlessly to Wi-Fi Direct for heavy media.</p>
        </div>
        <div class="card">
          <div class="card-icon">📞</div>
          <h3 class="card-title">P2P Voice & Video</h3>
          <p class="card-desc">Crystal-clear Opus audio and 720p hardware H.264 video calls routed directly over peer-to-peer radio sockets.</p>
        </div>
        <div class="card">
          <div class="card-icon">🚨</div>
          <h3 class="card-title">Tactical Survival Hub</h3>
          <p class="card-desc">2.8 kHz acoustic rescue sirens, optical Morse code distress strobes, offline Wikipedia, and panic data wiping.</p>
        </div>
      </div>
    </section>

    <!-- SLIDE 2 -->
    <section class="slide" data-notes="Let us address the problem statement. When cyclones, earthquakes, or urban floods strike, cellular infrastructure loses power within 3 to 6 hours. Dense crowds in festivals or stadiums cause network congestion where messages fail to send. And in remote or underground areas, cellular signals simply do not exist. Nexus eliminates this entire reliance on centralized infrastructure.">
      <div class="slide-badge">⚠️ The Critical Vulnerability of Centralization</div>
      <h2 class="slide-title">Why Telecommunications Collapse in Emergencies</h2>
      <p class="slide-subtitle">Modern messaging giants (WhatsApp, Signal, Telegram) are completely dependent on centralized cell towers and clouds. When towers lose power, communication dies.</p>

      <div class="grid-3">
        <div class="card" style="border-top: 3px solid var(--danger);">
          <div class="card-icon" style="background: rgba(239, 68, 68, 0.15); color: var(--danger); border-color: rgba(239, 68, 68, 0.3);">💥</div>
          <h3 class="card-title">Disaster Infrastructure Blackouts</h3>
          <p class="card-desc">Cyclones, floods, and earthquakes snap fiber cables and exhaust cell tower diesel generators within 3 to 6 hours. Survivors cannot summon medical or rescue assistance.</p>
        </div>
        <div class="card" style="border-top: 3px solid var(--warning);">
          <div class="card-icon" style="background: rgba(245, 158, 11, 0.15); color: var(--warning); border-color: rgba(245, 158, 11, 0.3);">📶</div>
          <h3 class="card-title">Base Station Network Congestion</h3>
          <p class="card-desc">Large-scale gatherings, pilgrimages (Kumbh Mela), and stadiums overwhelm localized base stations. Packets are dropped at the tower despite full signal bars.</p>
        </div>
        <div class="card" style="border-top: 3px solid var(--blue);">
          <div class="card-icon" style="background: rgba(59, 130, 246, 0.15); color: var(--blue); border-color: rgba(59, 130, 246, 0.3);">🛡️</div>
          <h3 class="card-title">Surveillance & Internet Shutdowns</h3>
          <p class="card-desc">Centralized clouds log metadata, phone numbers, and geolocation. Government kill-switches or cloud server outages sever connectivity across entire states.</p>
        </div>
      </div>

      <div class="card" style="margin-top: 20px; background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.3);">
        <p style="font-size: 1.05rem; color: var(--accent-light);">
          <strong>💡 The Nexus Solution:</strong> By leveraging existing radio chips in smartphones (BLE, Wi-Fi Direct, Local AP), Nexus creates an ad-hoc decentralized web where every device acts as an independent encrypted router.
        </p>
      </div>
    </section>

    <!-- SLIDE 3 -->
    <section class="slide" data-notes="Here is our Phase 1 milestone recap. Everything on this slide is already developed, compiled, and actively running on our physical Android test hardware. We implemented hardware DID keypair generation, BLE multi-hop discovery, laptop server auto-connect, and a native FileProvider APK share mechanism in Settings that allows sending the entire 15MB app via WhatsApp or Bluetooth in zero-internet zones.">
      <div class="slide-badge">✅ Milestone 1: Live Hardware Verification</div>
      <h2 class="slide-title">Phase 1: Foundation Built & Running on Device</h2>
      <p class="slide-subtitle">Tested natively on Android 15 hardware. Features a clean, accessible WhatsApp-style UI with White, Slate Gray, and Light Green aesthetics.</p>

      <div class="grid-2">
        <div>
          <table class="spec-table">
            <thead>
              <tr>
                <th>Module</th>
                <th>Engineering Architecture</th>
                <th>Live Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Cryptographic DID</strong></td>
                <td>Hardware Keystore Ed25519/X25519 (e.g. <code>mesh@181550df7a64</code>)</td>
                <td><span class="chip chip-green">VERIFIED ✅</span></td>
              </tr>
              <tr>
                <td><strong>BLE Gossip Mesh</strong></td>
                <td>Autonomous BLE 5.0 advertising + scanning with RSSI distance math</td>
                <td><span class="chip chip-green">VERIFIED ✅</span></td>
              </tr>
              <tr>
                <td><strong>WhatsApp APK Share</strong></td>
                <td>Settings FileProvider intent sharing compiled APK via WhatsApp/Bluetooth</td>
                <td><span class="chip chip-green">VERIFIED ✅</span></td>
              </tr>
              <tr>
                <td><strong>Browser Auto-Connect</strong></td>
                <td>Auto TCP candidate probe (127.0.0.1:8888) with Zero-Config server load</td>
                <td><span class="chip chip-green">VERIFIED ✅</span></td>
              </tr>
              <tr>
                <td><strong>Survival Tool Suite</strong></td>
                <td>2.8 kHz acoustic rescue siren, optical Morse strobe, panic wipe button</td>
                <td><span class="chip chip-green">VERIFIED ✅</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="phone-showcase">
          <div class="phone-mockup">
            <img src="presentation_assets/sharesheet_verified.png" alt="Nexus WhatsApp Share Sheet">
          </div>
        </div>
      </div>
    </section>

    <!-- SLIDE 4 -->
    <section class="slide" data-notes="This diagram explains the core networking protocol: Tri-Transport Mesh Auto-Promotion Engine. Light text messages and emergency SOS beacons stay on BLE to conserve battery. When a user transmits high-res photos or starts a video call, the engine dynamically promotes the connection to a 150 Mbps Wi-Fi Direct socket. When near a command laptop, it auto-connects to port 8888.">
      <div class="slide-badge">🏗️ Architecture Blueprint</div>
      <h2 class="slide-title">Tri-Transport Auto-Promotion Engine</h2>
      <p class="slide-subtitle">Intelligently shifts between three physical radio layers to optimize battery life, range, and bandwidth.</p>

      <div class="grid-3">
        <div class="card">
          <div class="card-icon">📡</div>
          <h3 class="card-title">Transport 1: BLE 5.0 Mesh</h3>
          <p class="card-desc"><strong>Payload:</strong> &lt; 512 Bytes (Text, SOS, DIDs)<br>
          <strong>Range:</strong> Up to 100m direct, kilometers via 7 hops.<br>
          <strong>Power:</strong> &lt; 1% battery per hour in background.<br>
          <strong>Duty:</strong> Background presence, gossip routing.</p>
        </div>
        <div class="card">
          <div class="card-icon">📶</div>
          <h3 class="card-title">Transport 2: Wi-Fi Direct P2P</h3>
          <p class="card-desc"><strong>Payload:</strong> Heavy (Images, Audio, 720p Video)<br>
          <strong>Throughput:</strong> Up to 150 Mbps direct sockets.<br>
          <strong>Signaling:</strong> Initial handshake negotiated over BLE.<br>
          <strong>Duty:</strong> On-demand voice/video & bulk files.</p>
        </div>
        <div class="card">
          <div class="card-icon">💻</div>
          <h3 class="card-title">Transport 3: Edge Station Hub</h3>
          <p class="card-desc"><strong>Protocol:</strong> Local HTTP / mDNS Port 8888.<br>
          <strong>Range:</strong> Local AP / High-Gain Laptop Wi-Fi.<br>
          <strong>Discovery:</strong> Zero manual IP configuration.<br>
          <strong>Duty:</strong> Offline Wikipedia, maps & triage dispatch.</p>
        </div>
      </div>

      <div class="card" style="margin-top: 20px; background: rgba(59, 130, 246, 0.08); border-color: rgba(59, 130, 246, 0.3);">
        <p style="font-size: 0.98rem; color: #BFDBFE;">
          <strong>🔄 Autonomous Link Promotion:</strong> A chat starts over BLE gossip. The instant a voice note or camera snapshot is attached, the stack spins up a high-speed Wi-Fi Direct group owner, completes the transfer, and tears down the high-power radio to preserve survival battery.
        </p>
      </div>
    </section>
""")
print("Slides 1 to 4 appended successfully.")
