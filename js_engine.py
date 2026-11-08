# js_engine.py - Core engine, Audio, Input, 3D Math & WebGL Renderer

def get_js_config_and_audio():
    return r"""
    /* ==========================================================================
       1. GAME CONFIGURATION & PALETTES
       ========================================================================== */
    const CONFIG = {
      WORLD_WIDTH: 3600,
      WORLD_HEIGHT: 3600,
      ROAD_WIDTH: 140,
      SIDEWALK_WIDTH: 26,
      GRID_ROADS_X: [200, 800, 1400, 2000, 2600, 3200],
      GRID_ROADS_Y: [200, 800, 1400, 2000, 2600, 3200],
      PALETTE: {
        BG: '#080811',
        ROAD: '#14151b',
        ROAD_LINE: '#ffcc00',
        ROAD_LINE_DASH: '#ffffff',
        CROSSWALK: '#f0f0f0',
        SIDEWALK: '#8c919a',
        CURB: '#686b72',
        BEACH_SAND: '#dab37c',
        OCEAN_WATER: '#004c70',
        OCEAN_FOAM: '#00f3ff',
        NEON_PINK: '#ff007f',
        NEON_CYAN: '#00f3ff',
        NEON_YELLOW: '#ffe600',
        NEON_PURPLE: '#bd00ff',
        NEON_GREEN: '#00ff66'
      }
    };

    /* ==========================================================================
       2. PROCEDURAL SYNTHWAVE AUDIO ENGINE (WEB AUDIO API)
       ========================================================================== */
    class AudioEngine {
      constructor() {
        this.ctx = null;
        this.sfxEnabled = true;
        this.musicEnabled = true;
        this.initialized = false;
        this.engineOsc = null;
        this.engineGain = null;
        this.musicTimer = null;
        this.musicStep = 0;
        this.bpm = 118;
      }

      init() {
        if (this.initialized) return;
        try {
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          this.ctx = new AudioContext();
          this.setupEngineSynth();
          this.startMusicSequencer();
          this.initialized = true;
          const prompt = document.getElementById('pointerPrompt');
          if (prompt) {
            prompt.textContent = 'FIRST-PERSON MOUSE LOOK ENGAGED [CLICK CANVAS / ESC TO RELEASE]';
            setTimeout(() => { if (prompt) prompt.style.opacity = '0'; }, 3500);
          }
        } catch (e) {
          console.warn('AudioContext not supported or blocked:', e);
        }
      }

      setupEngineSynth() {
        if (!this.ctx) return;
        this.engineOsc = this.ctx.createOscillator();
        this.engineOsc.type = 'sawtooth';
        this.engineOsc.frequency.setValueAtTime(45, this.ctx.currentTime);

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(220, this.ctx.currentTime);

        this.engineGain = this.ctx.createGain();
        this.engineGain.gain.setValueAtTime(0, this.ctx.currentTime);

        this.engineOsc.connect(filter);
        filter.connect(this.engineGain);
        this.engineGain.connect(this.ctx.destination);
        this.engineOsc.start();
      }

      updateEngineSound(speedRatio, isDriving) {
        if (!this.ctx || !this.sfxEnabled || !this.engineGain) return;
        if (!isDriving) {
          this.engineGain.gain.setTargetAtTime(0, this.ctx.currentTime, 0.05);
          return;
        }
        const targetGain = 0.08 + speedRatio * 0.12;
        const targetFreq = 42 + speedRatio * 140;
        this.engineGain.gain.setTargetAtTime(targetGain, this.ctx.currentTime, 0.05);
        this.engineOsc.frequency.setTargetAtTime(targetFreq, this.ctx.currentTime, 0.05);
      }

      playNoise(duration, decay, filterFreq, filterType = 'lowpass', gainVal = 0.2) {
        if (!this.ctx || !this.sfxEnabled) return;
        const bufferSize = Math.floor(this.ctx.sampleRate * duration);
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
          data[i] = Math.random() * 2 - 1;
        }
        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;

        const filter = this.ctx.createBiquadFilter();
        filter.type = filterType;
        filter.frequency.setValueAtTime(filterFreq, this.ctx.currentTime);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + decay);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);
        noise.start();
      }

      playShoot(type) {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        if (type === 'pistol') {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(750, now);
          osc.frequency.exponentialRampToValueAtTime(80, now + 0.14);
          gain.gain.setValueAtTime(0.35, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(now + 0.15);
          this.playNoise(0.14, 0.12, 2000, 'lowpass', 0.28);
        } else if (type === 'smg') {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'square';
          osc.frequency.setValueAtTime(980, now);
          osc.frequency.exponentialRampToValueAtTime(120, now + 0.08);
          gain.gain.setValueAtTime(0.22, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(now + 0.09);
          this.playNoise(0.09, 0.07, 2800, 'bandpass', 0.28);
        } else if (type === 'shotgun') {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(290, now);
          osc.frequency.exponentialRampToValueAtTime(35, now + 0.38);
          gain.gain.setValueAtTime(0.48, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.38);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(now + 0.39);
          this.playNoise(0.38, 0.34, 1300, 'lowpass', 0.5);
        } else if (type === 'punch') {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(170, now);
          osc.frequency.exponentialRampToValueAtTime(45, now + 0.16);
          gain.gain.setValueAtTime(0.32, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(now + 0.17);
        }
      }

      playShotgunPump() {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(500, now);
        osc.frequency.exponentialRampToValueAtTime(200, now + 0.08);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.09);
        this.playNoise(0.08, 0.06, 3200, 'bandpass', 0.16);
      }

      playHitMarker() {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1800, now);
        osc.frequency.exponentialRampToValueAtTime(1200, now + 0.04);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
      }

      playCrash(volume = 0.3) {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(130, now);
        osc.frequency.exponentialRampToValueAtTime(28, now + 0.32);
        gain.gain.setValueAtTime(volume, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.32);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(now + 0.34);
        this.playNoise(0.36, 0.3, 850, 'lowpass', volume * 0.85);
      }

      playTireSqueal() {
        if (!this.ctx || !this.sfxEnabled) return;
        this.playNoise(0.16, 0.14, 1500, 'bandpass', 0.14);
      }

      playHorn() {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        [440, 554].forEach(freq => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(freq, now);
          gain.gain.setValueAtTime(0.1, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(now + 0.32);
        });
      }

      playSirenTone(freq) {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(now + 0.24);
      }

      playExplosion() {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(100, now);
        osc.frequency.exponentialRampToValueAtTime(18, now + 0.9);
        gain.gain.setValueAtTime(0.65, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.95);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(now + 1.0);
        this.playNoise(1.0, 0.85, 600, 'lowpass', 0.65);
      }

      playCash() {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        [1320, 1760].forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.08);
          gain.gain.setValueAtTime(0.2, now + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.2);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now + idx * 0.08);
          osc.stop(now + idx * 0.08 + 0.22);
        });
      }

      playRespray() {
        if (!this.ctx || !this.sfxEnabled) return;
        const now = this.ctx.currentTime;
        const chord = [523.25, 659.25, 783.99, 1046.50];
        chord.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.09);
          gain.gain.setValueAtTime(0.18, now + idx * 0.09);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.4);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now + idx * 0.09);
          osc.stop(now + idx * 0.09 + 0.45);
        });
      }

      startMusicSequencer() {
        const stepTime = (60 / this.bpm) / 4;
        const bassNotes = [
          73.42, 73.42, 73.42, 73.42, 73.42, 73.42, 73.42, 73.42,
          58.27, 58.27, 58.27, 58.27, 58.27, 58.27, 58.27, 58.27,
          87.31, 87.31, 87.31, 87.31, 87.31, 87.31, 87.31, 87.31,
          65.41, 65.41, 65.41, 65.41, 65.41, 65.41, 65.41, 65.41
        ];
        const arps = [
          293.66, 349.23, 440.00, 587.33, 440.00, 349.23, 293.66, 440.00,
          233.08, 293.66, 349.23, 466.16, 349.23, 293.66, 233.08, 349.23,
          349.23, 440.00, 523.25, 698.46, 523.25, 440.00, 349.23, 523.25,
          261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 261.63, 392.00
        ];

        this.musicTimer = setInterval(() => {
          if (!this.musicEnabled || !this.ctx) return;
          const now = this.ctx.currentTime;
          const step16 = this.musicStep % 32;

          // Bass synth
          const bFreq = bassNotes[step16];
          const bOsc = this.ctx.createOscillator();
          const bGain = this.ctx.createGain();
          const bFilter = this.ctx.createBiquadFilter();
          bOsc.type = 'sawtooth';
          bOsc.frequency.setValueAtTime(bFreq, now);
          bFilter.type = 'lowpass';
          bFilter.frequency.setValueAtTime(260, now);
          bFilter.frequency.exponentialRampToValueAtTime(100, now + stepTime * 0.9);
          bGain.gain.setValueAtTime(0.12, now);
          bGain.gain.exponentialRampToValueAtTime(0.001, now + stepTime * 0.9);
          bOsc.connect(bFilter);
          bFilter.connect(bGain);
          bGain.connect(this.ctx.destination);
          bOsc.start(now);
          bOsc.stop(now + stepTime);

          // Arpeggio Lead
          if (step16 % 2 === 0) {
            const aFreq = arps[step16];
            const aOsc = this.ctx.createOscillator();
            const aGain = this.ctx.createGain();
            aOsc.type = 'triangle';
            aOsc.frequency.setValueAtTime(aFreq, now);
            aGain.gain.setValueAtTime(0.06, now);
            aGain.gain.exponentialRampToValueAtTime(0.001, now + stepTime * 1.8);
            aOsc.connect(aGain);
            aGain.connect(this.ctx.destination);
            aOsc.start(now);
            aOsc.stop(now + stepTime * 2);
          }

          // Synth Kick
          if (step16 % 4 === 0) {
            const kOsc = this.ctx.createOscillator();
            const kGain = this.ctx.createGain();
            kOsc.type = 'sine';
            kOsc.frequency.setValueAtTime(140, now);
            kOsc.frequency.exponentialRampToValueAtTime(35, now + 0.12);
            kGain.gain.setValueAtTime(0.3, now);
            kGain.gain.exponentialRampToValueAtTime(0.001, now + 0.13);
            kOsc.connect(kGain);
            kGain.connect(this.ctx.destination);
            kOsc.start(now);
            kOsc.stop(now + 0.14);
          }

          // Synth Snare
          if (step16 % 8 === 4) {
            this.playNoise(0.18, 0.15, 2400, 'bandpass', 0.15);
          }

          this.musicStep++;
        }, stepTime * 1000);
      }
    }

    const audio = new AudioEngine();
    """

def get_js_input_handler():
    return r"""
    /* ==========================================================================
       3. INPUT HANDLER WITH POINTER LOCK & FIRST-PERSON CONTROLS
       ========================================================================== */
    class InputHandler {
      constructor() {
        this.keys = {};
        this.prevKeys = {};
        this.mouseX = 0;
        this.mouseY = 0;
        this.worldMouseX = 0;
        this.worldMouseY = 0;
        this.mouseDown = false;
        this.rightMouseDown = false;
        this.isPointerLocked = false;

        // FPP Camera Angles
        this.yaw = 0;   // Horizontal look angle in radians
        this.pitch = 0; // Vertical look angle in radians [-1.42 to 1.42]
        this.mouseSensitivity = 0.0024;

        this.canvas = document.getElementById('gameCanvas');

        // Request Pointer Lock on canvas click
        this.canvas.addEventListener('click', () => {
          audio.init();
          if (!this.isPointerLocked && document.pointerLockElement !== this.canvas) {
            this.canvas.requestPointerLock = this.canvas.requestPointerLock || this.canvas.mozRequestPointerLock;
            if (this.canvas.requestPointerLock) {
              this.canvas.requestPointerLock();
            }
          }
        });

        document.addEventListener('pointerlockchange', () => {
          this.isPointerLocked = (document.pointerLockElement === this.canvas);
          const prompt = document.getElementById('pointerPrompt');
          if (prompt) {
            if (this.isPointerLocked) {
              prompt.style.opacity = '0';
            } else {
              prompt.textContent = 'CLICK GAME TO LOCK FIRST-PERSON MOUSE AIM [ESC TO UNLOCK]';
              prompt.style.opacity = '1';
            }
          }
        });

        window.addEventListener('keydown', (e) => {
          audio.init();
          this.keys[e.key.toLowerCase()] = true;
          this.keys[e.code] = true;

          if (e.key.toLowerCase() === 'm') {
            audio.musicEnabled = !audio.musicEnabled;
            const btn = document.getElementById('btnMusic');
            if (btn) btn.textContent = `🎵 MUSIC: ${audio.musicEnabled ? 'ON' : 'OFF'}`;
          }
          if (e.key.toLowerCase() === 'n') {
            audio.sfxEnabled = !audio.sfxEnabled;
            const btn = document.getElementById('btnSfx');
            if (btn) btn.textContent = `🔊 SFX: ${audio.sfxEnabled ? 'ON' : 'OFF'}`;
          }
          if (e.key.toLowerCase() === 'p') {
            const modal = document.getElementById('helpModal');
            if (modal) modal.classList.toggle('open');
          }
          if (e.key.toLowerCase() === 'v') {
            if (window.game) window.game.toggleViewMode();
          }
        });

        window.addEventListener('keyup', (e) => {
          this.keys[e.key.toLowerCase()] = false;
          this.keys[e.code] = false;
        });

        window.addEventListener('mousemove', (e) => {
          this.mouseX = e.clientX;
          this.mouseY = e.clientY;

          if (this.isPointerLocked) {
            const movementX = e.movementX || e.mozMovementX || 0;
            const movementY = e.movementY || e.mozMovementY || 0;

            this.yaw += movementX * this.mouseSensitivity;
            this.pitch -= movementY * this.mouseSensitivity;

            const maxPitch = 1.42;
            if (this.pitch > maxPitch) this.pitch = maxPitch;
            if (this.pitch < -maxPitch) this.pitch = -maxPitch;
          } else {
            // Drag or cursor tracking when pointer lock is not active
            if (this.mouseDown && window.game && window.game.viewMode === 'FPP') {
              const dx = e.movementX || 0;
              const dy = e.movementY || 0;
              this.yaw += dx * this.mouseSensitivity;
              this.pitch -= dy * this.mouseSensitivity;
              const maxPitch = 1.42;
              if (this.pitch > maxPitch) this.pitch = maxPitch;
              if (this.pitch < -maxPitch) this.pitch = -maxPitch;
            }
          }
        });

        window.addEventListener('mousedown', (e) => {
          audio.init();
          if (e.button === 0) this.mouseDown = true;
          if (e.button === 2) this.rightMouseDown = true;
        });

        window.addEventListener('mouseup', (e) => {
          if (e.button === 0) this.mouseDown = false;
          if (e.button === 2) this.rightMouseDown = false;
        });

        window.addEventListener('contextmenu', (e) => e.preventDefault());

        window.addEventListener('wheel', (e) => {
          if (window.game && window.game.player) {
            if (e.deltaY > 0) window.game.player.switchWeapon(1);
            else if (e.deltaY < 0) window.game.player.switchWeapon(-1);
          }
        }, { passive: true });
      }

      isDown(key) {
        return !!this.keys[key.toLowerCase()];
      }

      wasJustPressed(key) {
        const k = key.toLowerCase();
        return !!this.keys[k] && !this.prevKeys[k];
      }

      update() {
        this.prevKeys = { ...this.keys };
      }
    }

    const input = new InputHandler();
    """

def get_js_math_and_mesh():
    return r"""
    /* ==========================================================================
       4. 3D VECTOR & MATRIX MATHEMATICS (MAT4 & VEC3)
       ========================================================================== */
    const Mat4 = {
      create() {
        return new Float32Array([
          1, 0, 0, 0,
          0, 1, 0, 0,
          0, 0, 1, 0,
          0, 0, 0, 1
        ]);
      },
      identity(out) {
        out[0] = 1; out[1] = 0; out[2] = 0; out[3] = 0;
        out[4] = 0; out[5] = 1; out[6] = 0; out[7] = 0;
        out[8] = 0; out[9] = 0; out[10] = 1; out[11] = 0;
        out[12] = 0; out[13] = 0; out[14] = 0; out[15] = 1;
        return out;
      },
      perspective(out, fovy, aspect, near, far) {
        const f = 1.0 / Math.tan(fovy / 2);
        const nf = 1 / (near - far);
        out[0] = f / aspect;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = f;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = (far + near) * nf;
        out[11] = -1;
        out[12] = 0;
        out[13] = 0;
        out[14] = (2 * far * near) * nf;
        out[15] = 0;
        return out;
      },
      lookAt(out, eye, center, up) {
        let x0, x1, x2, y0, y1, y2, z0, z1, z2, len;
        let eyex = eye[0], eyey = eye[1], eyez = eye[2];
        let upx = up[0], upy = up[1], upz = up[2];
        let centerx = center[0], centery = center[1], centerz = center[2];

        z0 = eyex - centerx;
        z1 = eyey - centery;
        z2 = eyez - centerz;
        len = 1 / Math.hypot(z0, z1, z2);
        z0 *= len; z1 *= len; z2 *= len;

        x0 = upy * z2 - upz * z1;
        x1 = upz * z0 - upx * z2;
        x2 = upx * z1 - upy * z0;
        len = Math.hypot(x0, x1, x2);
        if (!len) {
          x0 = 0; x1 = 0; x2 = 0;
        } else {
          len = 1 / len;
          x0 *= len; x1 *= len; x2 *= len;
        }

        y0 = z1 * x2 - z2 * x1;
        y1 = z2 * x0 - z0 * x2;
        y2 = z0 * x1 - z1 * x0;
        len = Math.hypot(y0, y1, y2);
        if (!len) {
          y0 = 0; y1 = 0; y2 = 0;
        } else {
          len = 1 / len;
          y0 *= len; y1 *= len; y2 *= len;
        }

        out[0] = x0; out[1] = y0; out[2] = z0; out[3] = 0;
        out[4] = x1; out[5] = y1; out[6] = z1; out[7] = 0;
        out[8] = x2; out[9] = y2; out[10] = z2; out[11] = 0;
        out[12] = -(x0 * eyex + x1 * eyey + x2 * eyez);
        out[13] = -(y0 * eyex + y1 * eyey + y2 * eyez);
        out[14] = -(z0 * eyex + z1 * eyey + z2 * eyez);
        out[15] = 1;
        return out;
      },
      multiply(out, a, b) {
        const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        const a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];

        let b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        out[0] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[1] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[2] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[3] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;

        b0 = b[4]; b1 = b[5]; b2 = b[6]; b3 = b[7];
        out[4] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[5] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[6] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[7] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;

        b0 = b[8]; b1 = b[9]; b2 = b[10]; b3 = b[11];
        out[8] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[9] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[10] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[11] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;

        b0 = b[12]; b1 = b[13]; b2 = b[14]; b3 = b[15];
        out[12] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[13] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[14] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[15] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
        return out;
      },
      translate(out, a, v) {
        const x = v[0], y = v[1], z = v[2];
        if (a === out) {
          out[12] = a[0] * x + a[4] * y + a[8] * z + a[12];
          out[13] = a[1] * x + a[5] * y + a[9] * z + a[13];
          out[14] = a[2] * x + a[6] * y + a[10] * z + a[14];
          out[15] = a[3] * x + a[7] * y + a[11] * z + a[15];
        } else {
          Mat4.multiply(out, a, [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            x, y, z, 1
          ]);
        }
        return out;
      },
      rotateY(out, a, rad) {
        const s = Math.sin(rad), c = Math.cos(rad);
        const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        out[0] = a00 * c - a20 * s;
        out[1] = a01 * c - a21 * s;
        out[2] = a02 * c - a22 * s;
        out[3] = a03 * c - a23 * s;
        out[8] = a00 * s + a20 * c;
        out[9] = a01 * s + a21 * c;
        out[10] = a02 * s + a22 * c;
        out[11] = a03 * s + a23 * c;
        return out;
      },
      rotateX(out, a, rad) {
        const s = Math.sin(rad), c = Math.cos(rad);
        const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        const a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        out[4] = a10 * c + a20 * s;
        out[5] = a11 * c + a21 * s;
        out[6] = a12 * c + a22 * s;
        out[7] = a13 * c + a23 * s;
        out[8] = a20 * c - a10 * s;
        out[9] = a21 * c - a11 * s;
        out[10] = a22 * c - a12 * s;
        out[11] = a23 * c - a13 * s;
        return out;
      },
      rotateZ(out, a, rad) {
        const s = Math.sin(rad), c = Math.cos(rad);
        const a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        const a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        out[0] = a00 * c + a10 * s;
        out[1] = a01 * c + a11 * s;
        out[2] = a02 * c + a12 * s;
        out[3] = a03 * c + a13 * s;
        out[4] = a10 * c - a00 * s;
        out[5] = a11 * c - a01 * s;
        out[6] = a12 * c - a02 * s;
        out[7] = a13 * c - a03 * s;
        return out;
      },
      scale(out, a, v) {
        const x = v[0], y = v[1], z = v[2];
        out[0] = a[0] * x; out[1] = a[1] * x; out[2] = a[2] * x; out[3] = a[3] * x;
        out[4] = a[4] * y; out[5] = a[5] * y; out[6] = a[6] * y; out[7] = a[7] * y;
        out[8] = a[8] * z; out[9] = a[9] * z; out[10] = a[10] * z; out[11] = a[11] * z;
        return out;
      }
    };

    /* ==========================================================================
       5. 3D MESH BUFFER ACCUMULATOR
       ========================================================================== */
    class MeshBuffer {
      constructor(initialCapacity = 25000) {
        this.capacity = initialCapacity;
        // Format: x, y, z, nx, ny, nz, r, g, b, a, u, v, matType (13 floats)
        this.stride = 13;
        this.data = new Float32Array(this.capacity * this.stride);
        this.vertexCount = 0;
      }

      clear() {
        this.vertexCount = 0;
      }

      ensureCapacity(additionalVertices) {
        if (this.vertexCount + additionalVertices > this.capacity) {
          this.capacity = Math.max(this.capacity * 2, this.vertexCount + additionalVertices + 5000);
          const newData = new Float32Array(this.capacity * this.stride);
          newData.set(this.data);
          this.data = newData;
        }
      }

      addVertex(x, y, z, nx, ny, nz, r, g, b, a, u, v, matType) {
        this.ensureCapacity(1);
        const idx = this.vertexCount * this.stride;
        this.data[idx] = x;
        this.data[idx + 1] = y;
        this.data[idx + 2] = z;
        this.data[idx + 3] = nx;
        this.data[idx + 4] = ny;
        this.data[idx + 5] = nz;
        this.data[idx + 6] = r;
        this.data[idx + 7] = g;
        this.data[idx + 8] = b;
        this.data[idx + 9] = a;
        this.data[idx + 10] = u;
        this.data[idx + 11] = v;
        this.data[idx + 12] = matType;
        this.vertexCount++;
      }

      addQuad(p1, p2, p3, p4, normal, color, matType = 0, u1 = 0, v1 = 0, u2 = 1, v2 = 1) {
        const [nx, ny, nz] = normal;
        const [r, g, b, a] = color;
        // Tri 1: p1, p2, p3
        this.addVertex(p1[0], p1[1], p1[2], nx, ny, nz, r, g, b, a, u1, v1, matType);
        this.addVertex(p2[0], p2[1], p2[2], nx, ny, nz, r, g, b, a, u2, v1, matType);
        this.addVertex(p3[0], p3[1], p3[2], nx, ny, nz, r, g, b, a, u2, v2, matType);

        // Tri 2: p1, p3, p4
        this.addVertex(p1[0], p1[1], p1[2], nx, ny, nz, r, g, b, a, u1, v1, matType);
        this.addVertex(p3[0], p3[1], p3[2], nx, ny, nz, r, g, b, a, u2, v2, matType);
        this.addVertex(p4[0], p4[1], p4[2], nx, ny, nz, r, g, b, a, u1, v2, matType);
      }

      addBox(minX, minY, minZ, maxX, maxY, maxZ, color, matType = 0, uScale = 1, vScale = 1) {
        const c = color;
        // Top Face (Y+)
        this.addQuad(
          [minX, maxY, minZ], [maxX, maxY, minZ], [maxX, maxY, maxZ], [minX, maxY, maxZ],
          [0, 1, 0], c, matType, 0, 0, (maxX - minX) * uScale, (maxZ - minZ) * vScale
        );
        // Bottom Face (Y-)
        this.addQuad(
          [minX, minY, maxZ], [maxX, minY, maxZ], [maxX, minY, minZ], [minX, minY, minZ],
          [0, -1, 0], [c[0]*0.4, c[1]*0.4, c[2]*0.4, c[3]], matType, 0, 0, 1, 1
        );
        // Front Face (Z+)
        this.addQuad(
          [minX, minY, maxZ], [maxX, minY, maxZ], [maxX, maxY, maxZ], [minX, maxY, maxZ],
          [0, 0, 1], c, matType, 0, 0, (maxX - minX) * uScale, (maxY - minY) * vScale
        );
        // Back Face (Z-)
        this.addQuad(
          [maxX, minY, minZ], [minX, minY, minZ], [minX, maxY, minZ], [maxX, maxY, minZ],
          [0, 0, -1], [c[0]*0.8, c[1]*0.8, c[2]*0.8, c[3]], matType, 0, 0, (maxX - minX) * uScale, (maxY - minY) * vScale
        );
        // Right Face (X+)
        this.addQuad(
          [maxX, minY, maxZ], [maxX, minY, minZ], [maxX, maxY, minZ], [maxX, maxY, maxZ],
          [1, 0, 0], [c[0]*0.9, c[1]*0.9, c[2]*0.9, c[3]], matType, 0, 0, (maxZ - minZ) * uScale, (maxY - minY) * vScale
        );
        // Left Face (X-)
        this.addQuad(
          [minX, minY, minZ], [minX, minY, maxZ], [minX, maxY, maxZ], [minX, maxY, minZ],
          [-1, 0, 0], [c[0]*0.85, c[1]*0.85, c[2]*0.85, c[3]], matType, 0, 0, (maxZ - minZ) * uScale, (maxY - minY) * vScale
        );
      }

      addCylinder(cx, cy, cz, r, h, segs, color, matType = 0) {
        const halfH = h / 2;
        for (let i = 0; i < segs; i++) {
          const a1 = (i / segs) * Math.PI * 2;
          const a2 = ((i + 1) / segs) * Math.PI * 2;
          const x1 = Math.cos(a1) * r, z1 = Math.sin(a1) * r;
          const x2 = Math.cos(a2) * r, z2 = Math.sin(a2) * r;

          const n1x = Math.cos(a1), n1z = Math.sin(a1);
          const n2x = Math.cos(a2), n2z = Math.sin(a2);

          this.addVertex(cx + x1, cy - halfH, cz + z1, n1x, 0, n1z, color[0], color[1], color[2], color[3], 0, 0, matType);
          this.addVertex(cx + x2, cy - halfH, cz + z2, n2x, 0, n2z, color[0], color[1], color[2], color[3], 1, 0, matType);
          this.addVertex(cx + x2, cy + halfH, cz + z2, n2x, 0, n2z, color[0], color[1], color[2], color[3], 1, 1, matType);

          this.addVertex(cx + x1, cy - halfH, cz + z1, n1x, 0, n1z, color[0], color[1], color[2], color[3], 0, 0, matType);
          this.addVertex(cx + x2, cy + halfH, cz + z2, n2x, 0, n2z, color[0], color[1], color[2], color[3], 1, 1, matType);
          this.addVertex(cx + x1, cy + halfH, cz + z1, n1x, 0, n1z, color[0], color[1], color[2], color[3], 0, 1, matType);
        }
      }
    }
    """

def get_js_webgl_renderer():
    return r"""
    /* ==========================================================================
       6. WEBGL WORLD RENDERER & GLSL SHADERS
       ========================================================================== */
    class WebGLWorldRenderer {
      constructor(canvas) {
        this.canvas = canvas;
        this.gl = canvas.getContext('webgl', { antialias: true, alpha: false, depth: true });
        if (!this.gl) {
          console.error("WebGL not supported!");
          return;
        }

        const gl = this.gl;
        gl.enable(gl.DEPTH_TEST);
        gl.depthFunc(gl.LEQUAL);
        gl.enable(gl.CULL_FACE);
        gl.cullFace(gl.BACK);

        this.initShaders();
        this.initBuffers();

        this.staticMesh = new MeshBuffer(45000);
        this.dynamicMesh = new MeshBuffer(25000);
        this.viewmodelMesh = new MeshBuffer(8000);

        this.sunDir = [0.45, 0.75, 0.48];
        this.sunColor = [1.0, 0.92, 0.78];
        this.ambientColor = [0.24, 0.26, 0.35];
        this.fogColor = [0.10, 0.12, 0.22];
        this.fogDensity = 0.0015;

        this.pointLights = [];
      }

      initShaders() {
        const gl = this.gl;

        const vsSource = `
          attribute vec3 aPosition;
          attribute vec3 aNormal;
          attribute vec4 aColor;
          attribute vec2 aTexCoord;
          attribute float aMatType;

          uniform mat4 uProjection;
          uniform mat4 uView;
          uniform mat4 uModel;
          uniform float uTime;

          varying vec3 vWorldPos;
          varying vec3 vNormal;
          varying vec4 vColor;
          varying vec2 vTexCoord;
          varying float vMatType;

          void main() {
              vec4 worldPos = uModel * vec4(aPosition, 1.0);
              
              // Animated ocean waves (matType == 4.0)
              if (aMatType > 3.5 && aMatType < 4.5) {
                  float wave = sin(worldPos.x * 0.035 + uTime * 2.4) * cos(worldPos.z * 0.025 + uTime * 1.8) * 3.2;
                  wave += sin(worldPos.z * 0.065 + uTime * 3.0) * 1.4;
                  worldPos.y += wave;
              }
              
              vWorldPos = worldPos.xyz;
              vNormal = normalize(mat3(uModel[0].xyz, uModel[1].xyz, uModel[2].xyz) * aNormal);
              vColor = aColor;
              vTexCoord = aTexCoord;
              vMatType = aMatType;
              
              gl_Position = uProjection * uView * worldPos;
          }
        `;

        const fsSource = `
          precision highp float;

          varying vec3 vWorldPos;
          varying vec3 vNormal;
          varying vec4 vColor;
          varying vec2 vTexCoord;
          varying float vMatType;

          uniform vec3 uCameraPos;
          uniform vec3 uSunDir;
          uniform vec3 uSunColor;
          uniform vec3 uAmbientColor;
          uniform vec3 uFogColor;
          uniform float uFogDensity;
          uniform float uTime;

          uniform vec4 uLights[8];
          uniform vec3 uLightColors[8];

          void main() {
              vec3 N = normalize(vNormal);
              vec3 V = normalize(uCameraPos - vWorldPos);
              vec3 L = normalize(uSunDir);
              
              vec4 baseColor = vColor;
              float roughness = 0.65;
              float specularStrength = 0.35;
              float emission = 0.0;
              
              // 0: Road
              if (vMatType > -0.5 && vMatType < 0.5) {
                  float grain = fract(sin(dot(vWorldPos.xz, vec2(12.9898, 78.233))) * 43758.5453);
                  baseColor.rgb *= (0.92 + grain * 0.16);
                  roughness = 0.85;
                  specularStrength = 0.18;
              }
              // 1: Sidewalk
              else if (vMatType > 0.5 && vMatType < 1.5) {
                  vec2 grid = abs(fract(vWorldPos.xz * 0.05) - 0.5);
                  float line = smoothstep(0.46, 0.49, max(grid.x, grid.y));
                  baseColor.rgb *= (1.0 - line * 0.22);
                  roughness = 0.9;
                  specularStrength = 0.12;
              }
              // 2: Building Facade with lit glass window grid
              else if (vMatType > 1.5 && vMatType < 2.5) {
                  vec2 winCoord = vTexCoord * vec2(16.0, 24.0);
                  vec2 winGrid = fract(winCoord);
                  vec2 winId = floor(winCoord);
                  
                  bool isWindow = winGrid.x > 0.16 && winGrid.x < 0.84 && winGrid.y > 0.18 && winGrid.y < 0.82;
                  if (isWindow && vWorldPos.y > 8.0) {
                      float hash = fract(sin(dot(winId + floor(vWorldPos.xz * 0.02), vec2(127.1, 311.7))) * 43758.5453);
                      if (hash > 0.52) {
                          vec3 roomColor = hash > 0.82 ? vec3(0.98, 0.88, 0.62) : (hash > 0.68 ? vec3(0.55, 0.88, 1.0) : vec3(1.0, 0.72, 0.35));
                          baseColor.rgb = roomColor;
                          emission = 0.88;
                      } else {
                          baseColor.rgb = vec3(0.04, 0.07, 0.14);
                          roughness = 0.12;
                          specularStrength = 1.3;
                      }
                  } else {
                      baseColor.rgb *= (0.88 + 0.12 * cos(vWorldPos.y * 0.4));
                      roughness = 0.75;
                  }
              }
              // 4: Ocean Water
              else if (vMatType > 3.5 && vMatType < 4.5) {
                  float fresnel = pow(1.0 - max(0.0, dot(N, V)), 2.5);
                  vec3 deepWater = vec3(0.01, 0.16, 0.32);
                  vec3 shallowWater = vec3(0.0, 0.62, 0.75);
                  baseColor.rgb = mix(deepWater, shallowWater, fresnel);
                  roughness = 0.06;
                  specularStrength = 2.4;
                  emission = 0.12;
              }
              // 5: Palm Fronds
              else if (vMatType > 4.5 && vMatType < 5.5) {
                  roughness = 0.7;
                  specularStrength = 0.25;
              }
              // 6: Vehicle Exterior Paint
              else if (vMatType > 5.5 && vMatType < 6.5) {
                  roughness = 0.22;
                  specularStrength = 1.6;
              }
              // 7: Pedestrian / Police
              else if (vMatType > 6.5 && vMatType < 7.5) {
                  roughness = 0.65;
                  specularStrength = 0.3;
              }
              // 8: Viewmodel Weapon / Cockpit
              else if (vMatType > 7.5 && vMatType < 8.5) {
                  roughness = 0.3;
                  specularStrength = 0.9;
              }
              // 9: Unlit / Emissive Lights
              else if (vMatType > 8.5) {
                  gl_FragColor = vColor;
                  return;
              }
              
              // Blinn-Phong Sun Lighting
              float NdotL = max(0.0, dot(N, L));
              vec3 H = normalize(L + V);
              float NdotH = max(0.0, dot(N, H));
              float spec = pow(NdotH, (1.0 - roughness) * 48.0) * specularStrength;
              
              vec3 lighting = uAmbientColor + uSunColor * NdotL;
              vec3 finalColor = baseColor.rgb * lighting + uSunColor * spec + baseColor.rgb * emission;
              
              // Dynamic Point Lights
              for (int i = 0; i < 8; i++) {
                  if (uLights[i].w <= 0.0) continue;
                  vec3 lightPos = uLights[i].xyz;
                  float radius = uLights[i].w;
                  vec3 lightDir = lightPos - vWorldPos;
                  float dist = length(lightDir);
                  if (dist < radius) {
                      vec3 lightN = lightDir / dist;
                      float atten = pow(1.0 - dist / radius, 2.0);
                      float pNdotL = max(0.0, dot(N, lightN));
                      finalColor += baseColor.rgb * uLightColors[i] * (pNdotL * atten * 1.5);
                      
                      vec3 pH = normalize(lightN + V);
                      float pSpec = pow(max(0.0, dot(N, pH)), 24.0) * specularStrength;
                      finalColor += uLightColors[i] * (pSpec * atten * 1.0);
                  }
              }
              
              // Distance Fog
              float distToCam = length(uCameraPos - vWorldPos);
              float fogFactor = 1.0 - exp(-pow(distToCam * uFogDensity, 1.8));
              fogFactor = clamp(fogFactor, 0.0, 1.0);
              
              finalColor = mix(finalColor, uFogColor, fogFactor);
              gl_FragColor = vec4(finalColor, baseColor.a);
          }
        `;

        this.program = this.createProgram(vsSource, fsSource);
        this.attribs = {
          position: gl.getAttribLocation(this.program, 'aPosition'),
          normal: gl.getAttribLocation(this.program, 'aNormal'),
          color: gl.getAttribLocation(this.program, 'aColor'),
          texCoord: gl.getAttribLocation(this.program, 'aTexCoord'),
          matType: gl.getAttribLocation(this.program, 'aMatType')
        };
        this.uniforms = {
          projection: gl.getUniformLocation(this.program, 'uProjection'),
          view: gl.getUniformLocation(this.program, 'uView'),
          model: gl.getUniformLocation(this.program, 'uModel'),
          cameraPos: gl.getUniformLocation(this.program, 'uCameraPos'),
          sunDir: gl.getUniformLocation(this.program, 'uSunDir'),
          sunColor: gl.getUniformLocation(this.program, 'uSunColor'),
          ambientColor: gl.getUniformLocation(this.program, 'uAmbientColor'),
          fogColor: gl.getUniformLocation(this.program, 'uFogColor'),
          fogDensity: gl.getUniformLocation(this.program, 'uFogDensity'),
          time: gl.getUniformLocation(this.program, 'uTime')
        };

        this.uLightsLoc = [];
        this.uLightColorsLoc = [];
        for (let i = 0; i < 8; i++) {
          this.uLightsLoc.push(gl.getUniformLocation(this.program, `uLights[${i}]`));
          this.uLightColorsLoc.push(gl.getUniformLocation(this.program, `uLightColors[${i}]`));
        }

        // Skybox Shader
        const skyVs = `
          attribute vec3 aPosition;
          uniform mat4 uProjection;
          uniform mat4 uView;
          varying vec3 vDir;
          void main() {
              vDir = aPosition;
              mat4 viewNoTrans = uView;
              viewNoTrans[3][0] = 0.0;
              viewNoTrans[3][1] = 0.0;
              viewNoTrans[3][2] = 0.0;
              vec4 pos = uProjection * viewNoTrans * vec4(aPosition, 1.0);
              gl_Position = pos.xyww;
          }
        `;
        const skyFs = `
          precision highp float;
          varying vec3 vDir;
          uniform vec3 uSunDir;
          uniform float uTime;
          void main() {
              vec3 dir = normalize(vDir);
              float h = clamp(dir.y, 0.0, 1.0);
              vec3 zenith = vec3(0.06, 0.08, 0.22);
              vec3 horizon = vec3(0.55, 0.24, 0.44);
              vec3 sky = mix(horizon, zenith, pow(h, 0.65));
              
              float sunDot = max(0.0, dot(dir, normalize(uSunDir)));
              vec3 sunColor = vec3(1.0, 0.88, 0.62);
              float sunDisc = smoothstep(0.996, 0.9985, sunDot);
              float sunHalo = pow(sunDot, 16.0) * 0.4;
              
              if (dir.y > 0.04) {
                  vec2 cloudUV = dir.xz / (dir.y + 0.15) * 0.14 + vec2(uTime * 0.012, 0.0);
                  float cloudNoise = sin(cloudUV.x * 6.0) * cos(cloudUV.y * 6.0) * 0.5 + 0.5;
                  sky += vec3(0.85, 0.65, 0.85) * pow(cloudNoise, 3.0) * 0.22 * smoothstep(0.04, 0.25, dir.y);
              }
              
              sky += sunColor * (sunDisc + sunHalo);
              gl_FragColor = vec4(sky, 1.0);
          }
        `;
        this.skyProgram = this.createProgram(skyVs, skyFs);
        this.skyAttribs = {
          position: gl.getAttribLocation(this.skyProgram, 'aPosition')
        };
        this.skyUniforms = {
          projection: gl.getUniformLocation(this.skyProgram, 'uProjection'),
          view: gl.getUniformLocation(this.skyProgram, 'uView'),
          sunDir: gl.getUniformLocation(this.skyProgram, 'uSunDir'),
          time: gl.getUniformLocation(this.skyProgram, 'uTime')
        };
      }

      createProgram(vsSrc, fsSrc) {
        const gl = this.gl;
        const vs = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vs, vsSrc);
        gl.compileShader(vs);
        if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) {
          console.error("VS error:", gl.getShaderInfoLog(vs));
        }

        const fs = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fs, fsSrc);
        gl.compileShader(fs);
        if (!gl.getShaderParameter(fs, gl.COMPILE_STATUS)) {
          console.error("FS error:", gl.getShaderInfoLog(fs));
        }

        const prog = gl.createProgram();
        gl.attachShader(prog, vs);
        gl.attachShader(prog, fs);
        gl.linkProgram(prog);
        if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
          console.error("Prog link error:", gl.getProgramInfoLog(prog));
        }
        return prog;
      }

      initBuffers() {
        const gl = this.gl;
        this.staticVBO = gl.createBuffer();
        this.dynamicVBO = gl.createBuffer();
        this.viewmodelVBO = gl.createBuffer();

        this.skyVBO = gl.createBuffer();
        const s = 50.0;
        const skyVerts = new Float32Array([
          -s,  s, -s,  -s, -s, -s,   s, -s, -s,   s, -s, -s,   s,  s, -s,  -s,  s, -s,
          -s, -s,  s,  -s, -s, -s,  -s,  s, -s,  -s,  s, -s,  -s,  s,  s,  -s, -s,  s,
           s, -s, -s,   s, -s,  s,   s,  s,  s,   s,  s,  s,   s,  s, -s,   s, -s, -s,
          -s, -s,  s,   s, -s,  s,   s,  s,  s,   s,  s,  s,  -s,  s,  s,  -s, -s,  s,
          -s,  s, -s,   s,  s, -s,   s,  s,  s,   s,  s,  s,  -s,  s,  s,  -s,  s, -s,
          -s, -s, -s,  -s, -s,  s,   s, -s, -s,   s, -s, -s,  -s, -s,  s,   s, -s,  s
        ]);
        gl.bindBuffer(gl.ARRAY_BUFFER, this.skyVBO);
        gl.bufferData(gl.ARRAY_BUFFER, skyVerts, gl.STATIC_DRAW);
      }

      bindVertexFormat(buffer) {
        const gl = this.gl;
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        const stride = 13 * 4;

        gl.enableVertexAttribArray(this.attribs.position);
        gl.vertexAttribPointer(this.attribs.position, 3, gl.FLOAT, false, stride, 0);

        gl.enableVertexAttribArray(this.attribs.normal);
        gl.vertexAttribPointer(this.attribs.normal, 3, gl.FLOAT, false, stride, 3 * 4);

        gl.enableVertexAttribArray(this.attribs.color);
        gl.vertexAttribPointer(this.attribs.color, 4, gl.FLOAT, false, stride, 6 * 4);

        gl.enableVertexAttribArray(this.attribs.texCoord);
        gl.vertexAttribPointer(this.attribs.texCoord, 2, gl.FLOAT, false, stride, 10 * 4);

        gl.enableVertexAttribArray(this.attribs.matType);
        gl.vertexAttribPointer(this.attribs.matType, 1, gl.FLOAT, false, stride, 12 * 4);
      }

      uploadStaticMesh() {
        const gl = this.gl;
        gl.bindBuffer(gl.ARRAY_BUFFER, this.staticVBO);
        gl.bufferData(gl.ARRAY_BUFFER, this.staticMesh.data.subarray(0, this.staticMesh.vertexCount * 13), gl.STATIC_DRAW);
      }

      uploadDynamicMesh() {
        const gl = this.gl;
        gl.bindBuffer(gl.ARRAY_BUFFER, this.dynamicVBO);
        gl.bufferData(gl.ARRAY_BUFFER, this.dynamicMesh.data.subarray(0, this.dynamicMesh.vertexCount * 13), gl.DYNAMIC_DRAW);
      }

      uploadViewmodelMesh() {
        const gl = this.gl;
        gl.bindBuffer(gl.ARRAY_BUFFER, this.viewmodelVBO);
        gl.bufferData(gl.ARRAY_BUFFER, this.viewmodelMesh.data.subarray(0, this.viewmodelMesh.vertexCount * 13), gl.DYNAMIC_DRAW);
      }

      renderSky(projMat, viewMat, time) {
        const gl = this.gl;
        gl.depthMask(false);
        gl.useProgram(this.skyProgram);

        gl.uniformMatrix4fv(this.skyUniforms.projection, false, projMat);
        gl.uniformMatrix4fv(this.skyUniforms.view, false, viewMat);
        gl.uniform3fv(this.skyUniforms.sunDir, this.sunDir);
        gl.uniform1f(this.skyUniforms.time, time);

        gl.bindBuffer(gl.ARRAY_BUFFER, this.skyVBO);
        gl.enableVertexAttribArray(this.skyAttribs.position);
        gl.vertexAttribPointer(this.skyAttribs.position, 3, gl.FLOAT, false, 0, 0);

        gl.drawArrays(gl.TRIANGLES, 0, 36);
        gl.depthMask(true);
      }
    }
    """

