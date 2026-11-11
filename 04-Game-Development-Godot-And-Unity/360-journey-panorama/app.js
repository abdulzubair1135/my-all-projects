// Indian Highway Virtual Driving Adventure Engine (Three.js WebGL + Real-Time Road Animation + Web Audio)

class AudioEngine {
  constructor() {
    this.ctx = null;
    this.osc1 = null;
    this.osc2 = null;
    this.filter = null;
    this.masterGain = null;
    this.isPlaying = false;
    this.vehicleType = 'thar'; // 'thar', 'sedan', 'cruiser'
  }

  init() {
    if (this.ctx) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AudioContext();

    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.setValueAtTime(0.2, this.ctx.currentTime);

    this.filter = this.ctx.createBiquadFilter();
    this.filter.type = 'lowpass';
    this.filter.frequency.setValueAtTime(220, this.ctx.currentTime);

    this.osc1 = this.ctx.createOscillator();
    this.osc1.type = 'sawtooth';
    this.osc1.frequency.setValueAtTime(40, this.ctx.currentTime);

    this.osc2 = this.ctx.createOscillator();
    this.osc2.type = 'square';
    this.osc2.frequency.setValueAtTime(20, this.ctx.currentTime);

    this.osc1.connect(this.filter);
    this.osc2.connect(this.filter);
    this.filter.connect(this.masterGain);
    this.masterGain.connect(this.ctx.destination);

    this.osc1.start();
    this.osc2.start();
    this.isPlaying = true;
  }

  setVehicle(type) {
    this.vehicleType = type;
    if (!this.ctx) return;
    if (type === 'thar') {
      this.osc1.type = 'sawtooth';
      this.osc2.type = 'square';
    } else if (type === 'sedan') {
      this.osc1.type = 'sawtooth';
      this.osc2.type = 'triangle';
    } else {
      this.osc1.type = 'sine';
      this.osc2.type = 'sawtooth';
    }
  }

  update(rpm, speed) {
    if (!this.isPlaying || !this.ctx) return;
    const now = this.ctx.currentTime;
    
    let baseFreq = 40;
    if (this.vehicleType === 'thar') baseFreq = 35;
    else if (this.vehicleType === 'sedan') baseFreq = 50;
    else baseFreq = 42;

    const freq = baseFreq + (rpm / 7000) * 230;
    this.osc1.frequency.setTargetAtTime(freq, now, 0.05);
    this.osc2.frequency.setTargetAtTime(freq * 0.5, now, 0.05);

    const cutoff = 160 + (speed / 180) * 1400 + (rpm / 7000) * 900;
    this.filter.frequency.setTargetAtTime(cutoff, now, 0.05);
  }

  toggle() {
    if (!this.ctx) {
      this.init();
      return true;
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
      this.isPlaying = true;
      return true;
    } else if (this.ctx.state === 'running') {
      this.ctx.suspend();
      this.isPlaying = false;
      return false;
    }
  }
}

// 100% Reliable HD Canvas Highway Texture & Motion Generator
class HDCanvasRoadGenerator {
  constructor(tourName, vehicleName) {
    this.tourName = tourName;
    this.vehicleName = vehicleName;
    this.canvas = document.createElement('canvas');
    this.canvas.width = 2048;
    this.canvas.height = 1024;
    this.ctx = this.canvas.getContext('2d');
    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.minFilter = THREE.LinearFilter;
    this.texture.magFilter = THREE.LinearFilter;
    this.roadOffset = 0;
  }

  update(speed, dt, tourName, vehicleName) {
    if (tourName) this.tourName = tourName;
    if (vehicleName) this.vehicleName = vehicleName;

    // Advance road markings & scenery motion based on vehicle speed!
    this.roadOffset += (speed * 8 * dt);
    if (this.roadOffset > 100) this.roadOffset %= 100;

    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // 1. Sky Gradient (Sunset / Daytime Atmosphere)
    const sky = ctx.createLinearGradient(0, 0, 0, h * 0.55);
    sky.addColorStop(0, '#0c1a26');
    sky.addColorStop(0.5, '#1f3c4d');
    sky.addColorStop(1, '#34627a');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, w, h * 0.55);

    // 2. Sun Glow on Horizon
    const sunGlow = ctx.createRadialGradient(w * 0.5, h * 0.48, 10, w * 0.5, h * 0.48, 350);
    sunGlow.addColorStop(0, 'rgba(255, 230, 160, 0.95)');
    sunGlow.addColorStop(0.4, 'rgba(255, 120, 50, 0.4)');
    sunGlow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = sunGlow;
    ctx.fillRect(0, 0, w, h * 0.55);

    // 3. Mountain Ranges Silhouette
    ctx.fillStyle = '#081017';
    ctx.beginPath();
    ctx.moveTo(0, h * 0.55);
    for (let x = 0; x <= w; x += 40) {
      const mh = Math.sin((x + this.roadOffset * 2) * 0.005) * 80 + Math.cos(x * 0.018) * 30;
      ctx.lineTo(x, h * 0.51 - mh);
    }
    ctx.lineTo(w, h * 0.55);
    ctx.fill();

    // 4. Side Terrain / Grass Fields
    const ground = ctx.createLinearGradient(0, h * 0.55, 0, h);
    ground.addColorStop(0, '#15291b');
    ground.addColorStop(1, '#09120b');
    ctx.fillStyle = ground;
    ctx.fillRect(0, h * 0.55, w, h * 0.45);

    // 5. Indian Highway Asphalt Road
    const roadCenter = w * 0.5;
    const roadTopW = 120;
    const roadBotW = 1850;

    ctx.fillStyle = '#1c222b';
    ctx.beginPath();
    ctx.moveTo(roadCenter - roadTopW / 2, h * 0.55);
    ctx.lineTo(roadCenter + roadTopW / 2, h * 0.55);
    ctx.lineTo(roadCenter + roadBotW / 2, h);
    ctx.lineTo(roadCenter - roadBotW / 2, h);
    ctx.closePath();
    ctx.fill();

    // 6. Animated Yellow & White Lane Markings
    ctx.strokeStyle = '#e6c280';
    ctx.lineWidth = 16;
    ctx.setLineDash([60, 60]);
    ctx.lineDashOffset = -this.roadOffset * 2;
    ctx.beginPath();
    ctx.moveTo(roadCenter, h * 0.55);
    ctx.lineTo(roadCenter, h);
    ctx.stroke();

    // Solid Edge Lines
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 18;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(roadCenter - roadTopW / 2 + 10, h * 0.55);
    ctx.lineTo(roadCenter - roadBotW / 2 + 90, h);
    ctx.moveTo(roadCenter + roadTopW / 2 - 10, h * 0.55);
    ctx.lineTo(roadCenter + roadBotW / 2 - 90, h);
    ctx.stroke();

    // 7. Trees & Street Lights Moving Past Vehicle
    for (let side = -1; side <= 1; side += 2) {
      for (let i = 0; i < 8; i++) {
        const progress = ((i * 12.5 + this.roadOffset) % 100) / 100;
        const py = h * (0.55 + progress * 0.45);
        const px = roadCenter + side * (roadTopW / 2 + progress * (roadBotW / 2 - roadTopW / 2) + 70);
        const scale = 0.15 + progress * 1.8;

        // Tree Foliage
        ctx.fillStyle = '#0f381b';
        ctx.beginPath();
        ctx.arc(px, py - 45 * scale, 32 * scale, 0, Math.PI * 2);
        ctx.fill();

        // Trunk
        ctx.fillStyle = '#2d1d0e';
        ctx.fillRect(px - 5 * scale, py - 20 * scale, 10 * scale, 20 * scale);
      }
    }

    // 8. Milestone Highway Signboard Header
    ctx.fillStyle = 'rgba(0, 242, 254, 0.9)';
    ctx.font = 'bold 36px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`INDIAN EXPRESSWAY — ${this.tourName.toUpperCase()} [${this.vehicleName.toUpperCase()}]`, roadCenter, h * 0.59);

    this.texture.needsUpdate = true;
    return this.texture;
  }
}

class SimulatorApp {
  constructor() {
    this.container = document.getElementById('canvas-container');
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.screenMesh = null;
    this.cockpitGroup = null;
    this.steeringWheel = null;
    this.carExteriorGroup = null;
    this.carBodyMesh = null;
    this.audioEngine = new AudioEngine();

    this.viewMode = '1st'; // '1st', '2nd', '3rd'
    this.currentVehicle = 'thar'; // 'thar', 'sedan', 'cruiser'
    this.speed = 0;
    this.maxSpeed = 140; // Thar default
    this.acceleration = 0;
    this.rpm = 1000;
    this.gear = 'N';

    this.keys = { w: false, s: false, a: false, d: false, space: false };
    this.isDragging = false;
    this.previousMousePosition = { x: 0, y: 0 };
    this.cameraRotation = { lon: 0, lat: 0 };

    this.vehicles = {
      'thar': {
        name: 'Mahindra Thar 4x4 SUV',
        badge: 'THAR 4x4',
        maxSpeed: 140,
        color: 0xff3b60,
        accel: 28
      },
      'sedan': {
        name: 'V8 Sports Sedan',
        badge: 'V8 SPORTS',
        maxSpeed: 180,
        color: 0x00f2fe,
        accel: 38
      },
      'cruiser': {
        name: 'Highway Cruiser',
        badge: 'CRUISER',
        maxSpeed: 160,
        color: 0xffb703,
        accel: 32
      }
    };

    this.tours = {
      'ahmedabad-mumbai': {
        name: 'Ahmedabad → Mumbai Expressway (NH 48)',
        from: 'Ahmedabad', to: 'Mumbai', distance: '530 km'
      },
      'mumbai-pune': {
        name: 'Mumbai → Pune Expressway',
        from: 'Mumbai', to: 'Pune', distance: '150 km'
      },
      'bengaluru-mysore': {
        name: 'Bengaluru → Mysore Highway',
        from: 'Bengaluru', to: 'Mysore', distance: '140 km'
      },
      'delhi-agra': {
        name: 'Delhi → Agra Yamuna Expressway',
        from: 'Delhi', to: 'Agra', distance: '210 km'
      }
    };
    this.currentTourKey = 'ahmedabad-mumbai';

    this.init();
  }

  init() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 1000);
    this.camera.position.set(0, 0, 0);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    // 1. Create Dynamic Road Sphere
    this.roadGen = new HDCanvasRoadGenerator(
      this.tours[this.currentTourKey].name,
      this.vehicles[this.currentVehicle].name
    );

    const geometry = new THREE.SphereGeometry(500, 60, 40);
    this.screenMaterial = new THREE.MeshBasicMaterial({
      map: this.roadGen.update(0, 0.016, this.tours[this.currentTourKey].name, this.vehicles[this.currentVehicle].name),
      side: THREE.DoubleSide
    });

    this.screenMesh = new THREE.Mesh(geometry, this.screenMaterial);
    this.scene.add(this.screenMesh);

    // 2. Create 3D Cockpit & Vehicle
    this.create3DCockpit();

    // 3. Lights
    const ambient = new THREE.AmbientLight(0xffffff, 1.8);
    this.scene.add(ambient);
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(2, 5, 3);
    this.scene.add(dirLight);

    // 4. Bind Events
    this.bindEvents();

    // 5. Start Animation Loop
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  create3DCockpit() {
    this.cockpitGroup = new THREE.Group();

    // Steering Wheel
    const wheelGeom = new THREE.TorusGeometry(0.28, 0.035, 16, 32);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x11161d, roughness: 0.4, metalness: 0.8 });
    this.steeringWheel = new THREE.Mesh(wheelGeom, wheelMat);
    this.steeringWheel.position.set(0, -0.32, -0.55);
    this.steeringWheel.rotation.x = Math.PI * 0.12;

    const centerGeom = new THREE.CylinderGeometry(0.07, 0.07, 0.03, 32);
    const veh = this.vehicles[this.currentVehicle];
    this.centerMat = new THREE.MeshStandardMaterial({ color: veh.color, roughness: 0.2, metalness: 0.9 });
    const centerBadge = new THREE.Mesh(centerGeom, this.centerMat);
    centerBadge.rotation.x = Math.PI / 2;
    this.steeringWheel.add(centerBadge);

    this.cockpitGroup.add(this.steeringWheel);

    // Dashboard Console
    const dashGeom = new THREE.BoxGeometry(2.2, 0.4, 0.8);
    const dashMat = new THREE.MeshStandardMaterial({ color: 0x090c10, roughness: 0.7 });
    const dashBoard = new THREE.Mesh(dashGeom, dashMat);
    dashBoard.position.set(0, -0.5, -0.6);
    this.cockpitGroup.add(dashBoard);

    // Windshield A-Pillars
    const pillarMat = new THREE.MeshBasicMaterial({ color: 0x05070a });
    const leftPillarGeom = new THREE.BoxGeometry(0.12, 1.8, 0.12);
    const leftPillar = new THREE.Mesh(leftPillarGeom, pillarMat);
    leftPillar.position.set(-1.1, 0.3, -0.7);
    leftPillar.rotation.z = -Math.PI * 0.12;
    this.cockpitGroup.add(leftPillar);

    const rightPillar = new THREE.Mesh(leftPillarGeom, pillarMat);
    rightPillar.position.set(1.1, 0.3, -0.7);
    rightPillar.rotation.z = Math.PI * 0.12;
    this.cockpitGroup.add(rightPillar);

    // 3D Car Exterior Body Chassis (Visible in 3rd Person View)
    this.carExteriorGroup = new THREE.Group();
    
    const carBodyGeom = new THREE.BoxGeometry(1.6, 0.6, 3.2);
    this.carBodyMat = new THREE.MeshStandardMaterial({ color: veh.color, roughness: 0.3, metalness: 0.8 });
    this.carBodyMesh = new THREE.Mesh(carBodyGeom, this.carBodyMat);
    this.carBodyMesh.position.set(0, -0.4, 0.4);
    this.carExteriorGroup.add(this.carBodyMesh);

    const cabinGeom = new THREE.BoxGeometry(1.4, 0.5, 1.8);
    const cabinMat = new THREE.MeshStandardMaterial({ color: 0x11161d, roughness: 0.1, metalness: 0.9, transparent: true, opacity: 0.8 });
    const cabin = new THREE.Mesh(cabinGeom, cabinMat);
    cabin.position.set(0, 0.1, 0.2);
    this.carExteriorGroup.add(cabin);

    const wheelGeom = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 24);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x05070a, roughness: 0.8 });
    wheelGeom.rotateZ(Math.PI / 2);

    const positions = [
      [-0.8, -0.5, -0.8], [0.8, -0.5, -0.8],
      [-0.8, -0.5, 1.2],  [0.8, -0.5, 1.2]
    ];
    positions.forEach(pos => {
      const wheel = new THREE.Mesh(wheelGeom, wheelMat);
      wheel.position.set(...pos);
      this.carExteriorGroup.add(wheel);
    });

    this.cockpitGroup.add(this.carExteriorGroup);
    this.carExteriorGroup.visible = false;
    this.scene.add(this.cockpitGroup);
  }

  updateVehicleType(type) {
    this.currentVehicle = type;
    const veh = this.vehicles[type];
    this.maxSpeed = veh.maxSpeed;
    this.audioEngine.setVehicle(type);

    if (this.centerMat) this.centerMat.color.setHex(veh.color);
    if (this.carBodyMat) this.carBodyMat.color.setHex(veh.color);

    const vehicleBadge = document.getElementById('vehicle-badge');
    if (vehicleBadge) vehicleBadge.innerText = veh.badge;
  }

  bindEvents() {
    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Keyboard Physics Controls
    window.addEventListener('keydown', (e) => {
      const key = e.key.toLowerCase();
      if (key === 'w' || e.key === 'ArrowUp') this.keys.w = true;
      if (key === 's' || e.key === 'ArrowDown') this.keys.s = true;
      if (key === 'a' || e.key === 'ArrowLeft') this.keys.a = true;
      if (key === 'd' || e.key === 'ArrowRight') this.keys.d = true;
      if (e.code === 'Space') {
        this.keys.space = true;
        const banner = document.getElementById('pitstop-banner');
        if (banner && banner.style.display !== 'none') {
          banner.style.background = 'rgba(0, 242, 254, 0.2)';
          banner.style.borderColor = 'var(--accent-cyan)';
          banner.innerHTML = '✅ <strong>FASTag TOLL PAID!</strong> Proceeding Expressway...';
          setTimeout(() => { banner.style.display = 'none'; }, 2000);
        }
      }
    });

    window.addEventListener('keyup', (e) => {
      const key = e.key.toLowerCase();
      if (key === 'w' || e.key === 'ArrowUp') this.keys.w = false;
      if (key === 's' || e.key === 'ArrowDown') this.keys.s = false;
      if (key === 'a' || e.key === 'ArrowLeft') this.keys.a = false;
      if (key === 'd' || e.key === 'ArrowRight') this.keys.d = false;
      if (e.code === 'Space') this.keys.space = false;
    });

    // Mouse 360 Drag Controls
    const dom = this.renderer.domElement;
    dom.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => { this.isDragging = false; });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      const deltaX = e.clientX - this.previousMousePosition.x;
      const deltaY = e.clientY - this.previousMousePosition.y;

      this.cameraRotation.lon -= deltaX * 0.15;
      this.cameraRotation.lat += deltaY * 0.15;
      this.cameraRotation.lat = Math.max(-60, Math.min(60, this.cameraRotation.lat));

      this.previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    // Vehicle Select Dropdown
    const vehSelect = document.getElementById('vehicle-select');
    if (vehSelect) {
      vehSelect.addEventListener('change', (e) => {
        this.updateVehicleType(e.target.value);
      });
    }

    // View Switcher (1st, 2nd, 3rd Person View)
    const viewBtn = document.getElementById('btn-view-mode');
    const roleBadge = document.getElementById('room-role-badge');
    if (viewBtn) {
      viewBtn.addEventListener('click', () => {
        if (this.viewMode === '1st') {
          this.viewMode = '2nd';
          viewBtn.innerHTML = '🎥 View: 2nd Person (Passenger)';
          if (roleBadge) roleBadge.innerText = 'PASSENGER SEAT';
          this.camera.position.set(0.45, 0.05, -0.15);
          if (this.carExteriorGroup) this.carExteriorGroup.visible = false;
        } else if (this.viewMode === '2nd') {
          this.viewMode = '3rd';
          viewBtn.innerHTML = '🎥 View: 3rd Person (Exterior Car)';
          if (roleBadge) roleBadge.innerText = '3RD PERSON CAR CHASE';
          this.camera.position.set(0, 1.2, 3.2);
          if (this.carExteriorGroup) this.carExteriorGroup.visible = true;
        } else {
          this.viewMode = '1st';
          viewBtn.innerHTML = '🎥 View: 1st Person (Cockpit)';
          if (roleBadge) roleBadge.innerText = '1ST PERSON COCKPIT';
          this.camera.position.set(0, 0, 0);
          if (this.carExteriorGroup) this.carExteriorGroup.visible = false;
        }
      });
    }

    // WebXR VR Mode
    const vrBtn = document.getElementById('btn-vr-mode');
    if (vrBtn) {
      vrBtn.addEventListener('click', () => {
        alert('WebXR VR Mode: Connect Meta Quest or VR headset for stereoscopic 360° driving!');
      });
    }

    // Audio Toggle
    const audioBtn = document.getElementById('btn-audio');
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        const active = this.audioEngine.toggle();
        audioBtn.classList.toggle('active', active);
        audioBtn.innerHTML = active ? '🔊 Sound Engine' : '0️ Mute Engine';
      });
    }

    // Reset Camera
    const resetCamBtn = document.getElementById('btn-reset-cam');
    if (resetCamBtn) {
      resetCamBtn.addEventListener('click', () => {
        this.cameraRotation = { lon: 0, lat: 0 };
      });
    }

    // Tour Select Dropdown
    const tourSelect = document.getElementById('tour-select');
    if (tourSelect) {
      tourSelect.addEventListener('change', (e) => {
        this.currentTourKey = e.target.value;
        this.updateTourUI();
      });
    }

    // Start Drive Modal Button
    const startBtn = document.getElementById('btn-start-drive');
    const modal = document.getElementById('modal-overlay');
    if (startBtn && modal) {
      const dismissModal = () => {
        modal.classList.remove('active');
        modal.style.display = 'none';
        try {
          this.audioEngine.init();
        } catch (e) {}
        const audioBtn = document.getElementById('btn-audio');
        if (audioBtn) audioBtn.classList.add('active');
      };

      startBtn.addEventListener('click', dismissModal);
      modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target === startBtn) dismissModal();
      });
    }
  }

  updatePhysics(dt) {
    const veh = this.vehicles[this.currentVehicle];
    const accelRate = veh.accel || 30;

    if (this.keys.w) {
      this.acceleration = accelRate;
    } else if (this.keys.s) {
      this.acceleration = -45;
    } else if (this.keys.space) {
      this.acceleration = -95;
    } else {
      this.acceleration = -10;
    }

    this.speed += this.acceleration * dt;
    this.speed = Math.max(0, Math.min(this.maxSpeed, this.speed));

    if (this.speed === 0) this.gear = 'N';
    else if (this.speed < 25) this.gear = 'D1';
    else if (this.speed < 55) this.gear = 'D2';
    else if (this.speed < 90) this.gear = 'D3';
    else if (this.speed < 130) this.gear = 'D4';
    else this.gear = 'D5';

    this.rpm = 1000 + (this.speed % 35) * 140 + (this.speed / this.maxSpeed) * 2200;
    this.rpm = Math.min(7000, Math.max(900, this.rpm));

    this.audioEngine.update(this.rpm, this.speed);

    // Steering Wheel Rotation
    let targetWheelRot = 0;
    if (this.keys.a) targetWheelRot = Math.PI * 0.4;
    if (this.keys.d) targetWheelRot = -Math.PI * 0.4;
    if (this.steeringWheel) {
      this.steeringWheel.rotation.z += (targetWheelRot - this.steeringWheel.rotation.z) * 0.1;
    }

    // Update Real Road Atmosphere Texture Motion!
    if (this.roadGen) {
      const tour = this.tours[this.currentTourKey];
      this.roadGen.update(this.speed, dt, tour.name, veh.name);
    }
  }

  updateTourUI() {
    const tour = this.tours[this.currentTourKey];
    if (tour) {
      document.getElementById('route-city-from').innerText = tour.from;
      document.getElementById('route-city-to').innerText = tour.to;
      document.getElementById('route-distance').innerText = tour.distance;
      document.getElementById('nav-info').innerText = `GPS NAV ➔ ${tour.name} (${tour.distance})`;
    }
  }

  drawMiniMap() {
    const canvas = document.getElementById('minimap-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(0, 242, 254, 0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, 30, 0, Math.PI * 2);
    ctx.arc(w / 2, h / 2, 60, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(20, h - 20);
    ctx.quadraticCurveTo(w * 0.4, 20, w - 20, h * 0.3);
    ctx.stroke();

    const progressRatio = (this.speed / this.maxSpeed);
    const carX = 20 + ((Date.now() * 0.05 * (this.speed / 50)) % (w - 40));
    const carY = (h - 20) - Math.sin((carX / w) * Math.PI) * (h - 40);

    ctx.fillStyle = '#ffb703';
    ctx.shadowColor = '#ffb703';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(carX, carY, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
  }

  updateHUD() {
    this.drawMiniMap();
    
    const speedEl = document.getElementById('speed-display');
    if (speedEl) speedEl.innerText = Math.round(this.speed).toString().padStart(3, '0');

    const gearEl = document.getElementById('gear-display');
    if (gearEl) gearEl.innerText = this.gear;

    const rpmFill = document.getElementById('rpm-fill');
    if (rpmFill) {
      const pct = (this.rpm / 7000) * 100;
      rpmFill.style.width = `${pct}%`;
    }

    const progressFill = document.getElementById('route-progress-fill');
    if (progressFill) {
      const pct = Math.min(100, (this.speed / this.maxSpeed) * 100);
      progressFill.style.width = `${pct}%`;
    }
  }

  animate() {
    const dt = 0.016;

    this.updatePhysics(dt);
    this.updateHUD();

    const phi = THREE.MathUtils.degToRad(90 - this.cameraRotation.lat);
    const theta = THREE.MathUtils.degToRad(this.cameraRotation.lon);

    const targetX = this.camera.position.x + 500 * Math.sin(phi) * Math.cos(theta);
    const targetY = this.camera.position.y + 500 * Math.cos(phi);
    const targetZ = this.camera.position.z + 500 * Math.sin(phi) * Math.sin(theta);

    this.camera.lookAt(targetX, targetY, targetZ);

    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(this.animate);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.app = new SimulatorApp();
});
