# js_main.py - Main Game Engine, Cameras (FPP & Top-Down), Dynamic Lighting & Tactical HUD

def get_js_game_engine_and_hud():
    return r"""
    /* ==========================================================================
       11. MAIN GAME ENGINE, CAMERA PIPELINE & TACTICAL HUD
       ========================================================================== */
    class FloatingNotification {
      constructor(text, color = '#ffe600') {
        this.text = text;
        this.color = color;
        this.life = 2.0;
        this.maxLife = 2.0;
      }
      update(dt) {
        this.life -= dt;
        return this.life > 0;
      }
    }

    class GameEngine {
      constructor() {
        this.glCanvas = document.getElementById('gameCanvas');
        this.hudCanvas = document.getElementById('hudCanvas');
        this.hudCtx = this.hudCanvas.getContext('2d');

        // View Mode: 'FPP' (First-Person Perspective, default) or 'TOP_DOWN'
        this.viewMode = 'FPP';

        // Camera State
        this.camX = 1400;
        this.camY = 24.0;
        this.camZ = 1420;
        this.camPitch = 0;
        this.camYaw = 0;
        this.camFov = 74 * (Math.PI / 180); // 74 deg FOV
        this.screenShake = 0;

        // Matrices
        this.projMatrix = Mat4.create();
        this.viewMatrix = Mat4.create();
        this.identityModel = Mat4.create();

        // 3D WebGL Renderer
        this.renderer = new WebGLWorldRenderer(this.glCanvas);

        // Procedural City & Static Mesh
        this.world = new CityWorld3D();
        this.world.buildStaticMesh(this.renderer.staticMesh);
        this.renderer.uploadStaticMesh();

        // Spatial Partitioning Grid for fast building collision
        this.spatialGrid = new SpatialGrid(CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT, 300);
        this.world.buildings.forEach(b => this.spatialGrid.insert(b, b));

        this.decals = new DecalManager(CONFIG.WORLD_WIDTH, CONFIG.WORLD_HEIGHT);
        this.player = new Player(1400, 1420);
        this.police = new PoliceManager();

        this.vehicles = [];
        this.pedestrians = [];
        this.projectiles = [];
        this.particles = [];
        this.pickups = [];
        this.notifications = [];

        this.lastTime = performance.now();
        this.gameTime = 0;

        this.setupInitialEntities();
        this.resize();
        window.addEventListener('resize', () => this.resize());
      }

      resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        const w = window.innerWidth;
        const h = window.innerHeight;
        this.glCanvas.width = Math.floor(w * dpr);
        this.glCanvas.height = Math.floor(h * dpr);
        this.glCanvas.style.width = w + 'px';
        this.glCanvas.style.height = h + 'px';
        this.hudCanvas.width = w;
        this.hudCanvas.height = h;
        this.hudCanvas.style.width = w + 'px';
        this.hudCanvas.style.height = h + 'px';
        if (this.renderer && this.renderer.gl) {
          this.renderer.gl.viewport(0, 0, this.glCanvas.width, this.glCanvas.height);
        }
      }

      toggleViewMode() {
        this.viewMode = (this.viewMode === 'FPP') ? 'TOP_DOWN' : 'FPP';
        const btn = document.getElementById('btnView');
        if (btn) {
          btn.textContent = `👁️ VIEW: ${this.viewMode} [V]`;
        }
        const crosshair = document.getElementById('crosshair');
        if (crosshair) {
          crosshair.style.display = (this.viewMode === 'FPP') ? 'flex' : 'none';
        }
        this.showFloatingNotification(`CAMERA VIEW: ${this.viewMode}`, '#00f3ff');
      }

      setupInitialEntities() {
        const carTypes = ['sports', 'muscle', 'sedan', 'taxi', 'van'];

        // Malibu Club Parked Cars
        this.vehicles.push(new Vehicle(1020, 680, 0, 'sports'));
        this.vehicles.push(new Vehicle(1080, 680, 0, 'muscle'));

        // VCPD HQ Police Cruisers
        this.vehicles.push(new Vehicle(1600, 1100, Math.PI * 0.5, 'police'));
        this.vehicles.push(new Vehicle(1680, 1100, Math.PI * 0.5, 'police'));

        // Vice Hospital Ambulance
        this.vehicles.push(new Vehicle(2250, 1100, 0, 'van'));

        // Beachfront Sports Car
        this.vehicles.push(new Vehicle(3200, 1500, -Math.PI * 0.5, 'sports'));

        // Ammu-Nation Muscle Car
        this.vehicles.push(new Vehicle(450, 1200, 0, 'muscle'));

        // Traffic vehicles on roads
        for (let i = 0; i < 18; i++) {
          const rx = CONFIG.GRID_ROADS_X[Math.floor(Math.random() * CONFIG.GRID_ROADS_X.length)];
          const ry = 400 + Math.random() * 2600;
          const type = carTypes[Math.floor(Math.random() * carTypes.length)];
          const car = new Vehicle(rx + 35, ry, Math.PI * 0.5, type);
          new TrafficDriver(car, 1, 'y');
          this.vehicles.push(car);
        }

        // Ambient Pedestrians
        for (let i = 0; i < 40; i++) {
          const px = 300 + Math.random() * 2800;
          const py = 300 + Math.random() * 2800;
          this.pedestrians.push(new Pedestrian(px, py));
        }

        // Weapon Pickups at Ammu-Nation & Hospital
        this.pickups.push(new Pickup(480, 1000, 'smg', true));
        this.pickups.push(new Pickup(520, 1000, 'shotgun', true));
        this.pickups.push(new Pickup(560, 1000, 'armor', true));
        this.pickups.push(new Pickup(2200, 1050, 'health', true));
        this.pickups.push(new Pickup(1650, 1000, 'armor', true));
      }

      addScreenShake(intensity, duration) {
        this.screenShake = intensity;
      }

      showHitMarker() {
        const hm = document.getElementById('hitMarker');
        if (hm) {
          hm.classList.add('active');
          setTimeout(() => hm.classList.remove('active'), 120);
        }
      }

      showFloatingNotification(text, color = '#ffe600') {
        this.notifications.push(new FloatingNotification(text, color));
        if (this.notifications.length > 5) this.notifications.shift();
      }

      spawnParticle(x, y, vx, vy, color, size, life, decay, type) {
        this.particles.push(new Particle(x, y, vx, vy, color, size, life, decay, type));
      }

      hasLineOfSight(x1, y1, x2, y2) {
        const nearby = this.spatialGrid.getNearby((x1 + x2) / 2, (y1 + y2) / 2, Math.hypot(x2 - x1, y2 - y1) / 2);
        for (const b of nearby) {
          if (this.lineIntersectsRect(x1, y1, x2, y2, b)) {
            return false;
          }
        }
        return true;
      }

      lineIntersectsRect(x1, y1, x2, y2, r) {
        let t0 = 0;
        let t1 = 1;
        const dx = x2 - x1;
        const dy = y2 - y1;

        const p = [-dx, dx, -dy, dy];
        const q = [x1 - r.x, (r.x + r.w) - x1, y1 - r.y, (r.y + r.h) - y1];

        for (let i = 0; i < 4; i++) {
          if (p[i] === 0) {
            if (q[i] < 0) return false;
          } else {
            const t = q[i] / p[i];
            if (p[i] < 0) {
              if (t > t1) return false;
              if (t > t0) t0 = t;
            } else {
              if (t < t0) return false;
              if (t < t1) t1 = t;
            }
          }
        }
        return t0 <= t1;
      }

      findMeleeTarget(x, y, angle, range) {
        for (const ped of this.pedestrians) {
          if (ped.state === 'DEAD') continue;
          const dist = Math.hypot(ped.x - x, ped.y - y);
          if (dist < range) return ped;
        }
        for (const off of this.police.officers) {
          if (!off.alive) continue;
          const dist = Math.hypot(off.x - x, off.y - y);
          if (dist < range) return off;
        }
        for (const car of this.vehicles) {
          const dist = Math.hypot(car.x - x, car.y - y);
          if (dist < range + car.width) return car;
        }
        return null;
      }

      dealRadiusDamage(x, y, radius, damage, ignore) {
        const pDist = Math.hypot(this.player.x - x, this.player.y - y);
        if (pDist < radius) {
          this.player.takeDamage(damage * (1 - pDist / radius));
        }

        for (const car of this.vehicles) {
          if (car === ignore) continue;
          const dist = Math.hypot(car.x - x, car.y - y);
          if (dist < radius) {
            car.takeDamage(damage * (1 - dist / radius));
          }
        }

        for (const ped of this.pedestrians) {
          const dist = Math.hypot(ped.x - x, ped.y - y);
          if (dist < radius) {
            ped.takeDamage(damage, this.player);
          }
        }

        for (const off of this.police.officers) {
          const dist = Math.hypot(off.x - x, off.y - y);
          if (dist < radius) {
            off.takeDamage(damage, this.player);
          }
        }
      }

      triggerWasted() {
        this.showFloatingNotification('WASTED', '#ff0000');
        setTimeout(() => {
          this.player.x = 2200;
          this.player.y = 1150;
          this.player.z = 24.0;
          this.player.health = 100;
          this.player.alive = true;
          this.player.cash = Math.max(0, this.player.cash - 100);
          this.police.clearWanted();
          this.showFloatingNotification('RESPAWNED AT VICE HOSPITAL (-$100)', '#00f3ff');
        }, 2500);
      }

      checkPayNSpray() {
        if (!this.player.inVehicle) return;
        const car = this.player.inVehicle;
        const pSpot = this.world.specialSpots.payNSpray;
        if (!pSpot) return;

        const dist = Math.hypot(car.x - pSpot.x, car.y - pSpot.y);
        if (dist < 75 && (car.hp < car.maxHp || this.police.wantedLevel > 0)) {
          car.hp = car.maxHp;
          const neonColors = [
            [1.0, 0.0, 0.5, 1.0], [0.0, 0.95, 1.0, 1.0], [1.0, 0.88, 0.0, 1.0],
            [0.74, 0.0, 1.0, 1.0], [0.0, 1.0, 0.45, 1.0], [0.95, 0.95, 0.98, 1.0]
          ];
          car.color = neonColors[Math.floor(Math.random() * neonColors.length)];
          this.police.clearWanted();
          audio.playRespray();
          this.showFloatingNotification("PAY 'N' SPRAY: REPAIRED & REPAINTED!", '#00ff66');
        }
      }

      update(dt) {
        this.gameTime += dt;

        this.player.update(dt);
        this.checkPayNSpray();

        // Vehicles update
        for (const car of this.vehicles) {
          if (car.driver && car.driver !== this.player) {
            car.driver.update(dt);
          } else if (!car.driver) {
            car.updatePhysics(dt, 0, 0, false);
          }

          // Building Collision for Vehicles
          const circles = car.getCollisionCircles();
          for (const circle of circles) {
            const nearby = this.spatialGrid.getNearby(circle.x, circle.y, circle.r + 20);
            for (const b of nearby) {
              const cx = Math.max(b.x, Math.min(circle.x, b.x + b.w));
              const cy = Math.max(b.y, Math.min(circle.y, b.y + b.h));
              const dist = Math.hypot(circle.x - cx, circle.y - cy);
              if (dist < circle.r) {
                const nx = (circle.x - cx) / (dist || 1);
                const ny = (circle.y - cy) / (dist || 1);
                car.x += nx * (circle.r - dist);
                car.y += ny * (circle.r - dist);
                car.vx *= -0.3;
                car.vy *= -0.3;
                if (car.speed > 80) {
                  car.takeDamage(car.speed * 0.08);
                  audio.playCrash(0.3);
                  this.addScreenShake(6, 0.2);
                }
              }
            }
          }
        }

        // Vehicle vs Vehicle Collisions
        for (let i = 0; i < this.vehicles.length; i++) {
          for (let j = i + 1; j < this.vehicles.length; j++) {
            const c1 = this.vehicles[i];
            const c2 = this.vehicles[j];
            const dist = Math.hypot(c2.x - c1.x, c2.y - c1.y);
            if (dist < c1.width * 1.1) {
              const nx = (c2.x - c1.x) / (dist || 1);
              const ny = (c2.y - c1.y) / (dist || 1);
              const push = (c1.width * 1.1 - dist) * 0.5;
              c1.x -= nx * push;
              c1.y -= ny * push;
              c2.x += nx * push;
              c2.y += ny * push;

              const tempVx = c1.vx;
              const tempVy = c1.vy;
              c1.vx = c2.vx * 0.5;
              c1.vy = c2.vy * 0.5;
              c2.vx = tempVx * 0.5;
              c2.vy = tempVy * 0.5;

              const relSpeed = Math.hypot(tempVx - c2.vx, tempVy - c2.vy);
              if (((c1 === this.player.inVehicle && c2.isPolice) || (c2 === this.player.inVehicle && c1.isPolice)) && relSpeed > 140) {
                this.police.addHeat(20);
              }
              if (relSpeed > 90) audio.playCrash(0.25);
            }
          }
        }

        // Vehicle vs Pedestrian Collisions
        for (const car of this.vehicles) {
          if (car.speed > 55) {
            for (const ped of this.pedestrians) {
              if (ped.state === 'DEAD') continue;
              if (Math.hypot(car.x - ped.x, car.y - ped.y) < car.width * 0.8) {
                const attacker = (car.driver === this.player) ? this.player : null;
                ped.takeDamage(80, attacker);
                audio.playCrash(0.18);
              }
            }
          }
        }

        // On-foot Player vs Buildings Collision
        if (!this.player.inVehicle) {
          const nearby = this.spatialGrid.getNearby(this.player.x, this.player.y, this.player.radius + 15);
          for (const b of nearby) {
            const cx = Math.max(b.x, Math.min(this.player.x, b.x + b.w));
            const cy = Math.max(b.y, Math.min(this.player.y, b.y + b.h));
            const dist = Math.hypot(this.player.x - cx, this.player.y - cy);
            if (dist < this.player.radius) {
              const nx = (this.player.x - cx) / (dist || 1);
              const ny = (this.player.y - cy) / (dist || 1);
              this.player.x += nx * (this.player.radius - dist);
              this.player.y += ny * (this.player.radius - dist);
            }
          }
        }

        // Pedestrians Update
        for (const ped of this.pedestrians) {
          ped.update(dt);
        }

        // Police AI Update
        this.police.update(dt);

        // Projectiles Update
        for (let i = this.projectiles.length - 1; i >= 0; i--) {
          const p = this.projectiles[i];
          if (!p.update(dt)) {
            this.projectiles.splice(i, 1);
            continue;
          }

          // Building hit test
          const nearby = this.spatialGrid.getNearby(p.x, p.y, 10);
          let hitBuilding = false;
          for (const b of nearby) {
            if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h) {
              this.spawnParticle(p.x, p.y, (Math.random() - 0.5) * 50, (Math.random() - 0.5) * 50, '#ffe600', 3, 0.2, 1.2, 'spark');
              hitBuilding = true;
              break;
            }
          }
          if (hitBuilding) {
            this.projectiles.splice(i, 1);
            continue;
          }

          // Vehicle hit test
          let hitVehicle = false;
          for (const car of this.vehicles) {
            if (Math.hypot(car.x - p.x, car.y - p.y) < car.width * 0.8) {
              car.takeDamage(p.damage);
              this.spawnParticle(p.x, p.y, (Math.random() - 0.5) * 50, (Math.random() - 0.5) * 50, '#ff5500', 3, 0.2, 1.0, 'spark');
              this.projectiles.splice(i, 1);
              hitVehicle = true;
              break;
            }
          }
          if (hitVehicle) continue;

          // Pedestrian & Police hit test
          if (p.owner === 'player') {
            let hitTarget = false;
            for (const ped of this.pedestrians) {
              if (ped.state === 'DEAD') continue;
              if (Math.hypot(ped.x - p.x, ped.y - p.y) < ped.radius + 5) {
                ped.takeDamage(p.damage, this.player);
                audio.playHitMarker();
                this.showHitMarker();
                this.projectiles.splice(i, 1);
                hitTarget = true;
                break;
              }
            }
            if (hitTarget) continue;

            for (const off of this.police.officers) {
              if (!off.alive) continue;
              if (Math.hypot(off.x - p.x, off.y - p.y) < off.radius + 5) {
                off.takeDamage(p.damage, this.player);
                audio.playHitMarker();
                this.showHitMarker();
                this.projectiles.splice(i, 1);
                hitTarget = true;
                break;
              }
            }
            if (hitTarget) continue;
          } else if (p.owner === 'cop') {
            if (Math.hypot(this.player.x - p.x, this.player.y - p.y) < this.player.radius + 4) {
              this.player.takeDamage(p.damage);
              this.projectiles.splice(i, 1);
              continue;
            }
          }
        }

        // Pickups Update & Collection
        for (let i = this.pickups.length - 1; i >= 0; i--) {
          const pick = this.pickups[i];
          pick.update(dt);
          if (pick.active && Math.hypot(this.player.x - pick.x, this.player.y - pick.y) < 32) {
            if (pick.type === 'cash') {
              this.player.cash += pick.val;
              audio.playCash();
              this.showFloatingNotification(`+$${pick.val}`, '#00ff66');
            } else if (pick.type === 'health') {
              this.player.health = Math.min(this.player.maxHealth, this.player.health + pick.val);
              audio.playCash();
              this.showFloatingNotification('+50 HEALTH', '#ff007f');
            } else if (pick.type === 'armor') {
              this.player.armor = Math.min(this.player.maxArmor, this.player.armor + pick.val);
              audio.playCash();
              this.showFloatingNotification('+50 ARMOR', '#00f3ff');
            } else if (pick.type === 'smg') {
              this.player.weapons[2].ammo += 60;
              this.player.setWeapon(2);
              audio.playCash();
              this.showFloatingNotification('+60 UZI AMMO', '#ffe600');
            } else if (pick.type === 'shotgun') {
              this.player.weapons[3].ammo += 18;
              this.player.setWeapon(3);
              audio.playCash();
              this.showFloatingNotification('+18 SHOTGUN SHELLS', '#ffe600');
            }

            if (pick.respawns) {
              pick.active = false;
              pick.respawnTimer = 20.0;
            } else {
              this.pickups.splice(i, 1);
            }
          }
        }

        // Dynamic Pedestrian density recycling
        for (const ped of this.pedestrians) {
          const dist = Math.hypot(ped.x - this.player.x, ped.y - this.player.y);
          if (dist > 1600 || (ped.state === 'DEAD' && dist > 1100)) {
            const ang = Math.random() * Math.PI * 2;
            const d = 800 + Math.random() * 450;
            ped.x = Math.max(100, Math.min(CONFIG.WORLD_WIDTH - 100, this.player.x + Math.cos(ang) * d));
            ped.y = Math.max(100, Math.min(CONFIG.WORLD_HEIGHT - 100, this.player.y + Math.sin(ang) * d));
            ped.state = 'WANDER';
            ped.hp = 30;
          }
        }

        // Dynamic Traffic recycling
        for (const car of this.vehicles) {
          if (car.driver && car.driver !== this.player && !car.isPolice) {
            const dist = Math.hypot(car.x - this.player.x, car.y - this.player.y);
            if (dist > 1700 || (car.wrecked && dist > 1100)) {
              const rx = CONFIG.GRID_ROADS_X[Math.floor(Math.random() * CONFIG.GRID_ROADS_X.length)];
              const ry = Math.max(200, Math.min(CONFIG.WORLD_HEIGHT - 200, this.player.y + (Math.random() - 0.5) * 1400));
              car.x = rx + 35;
              car.y = ry;
              car.vx = 0;
              car.vy = 0;
              car.angle = Math.PI * 0.5;
              car.hp = car.maxHp;
              car.wrecked = false;
              car.burning = false;
            }
          }
        }

        // Particles Update
        for (let i = this.particles.length - 1; i >= 0; i--) {
          if (!this.particles[i].update(dt)) {
            this.particles.splice(i, 1);
          }
        }

        // Notifications Update
        for (let i = this.notifications.length - 1; i >= 0; i--) {
          if (!this.notifications[i].update(dt)) {
            this.notifications.splice(i, 1);
          }
        }

        if (this.screenShake > 0) {
          this.screenShake -= dt * 25;
          if (this.screenShake < 0) this.screenShake = 0;
        }

        input.update();
      }

      render() {
        const gl = this.renderer.gl;
        if (!gl) return;

        const w = this.glCanvas.width;
        const h = this.glCanvas.height;
        const aspect = w / h;

        // Dynamic FOV (Aim Down Sights narrows FOV for precision)
        const targetFov = (this.player.adsRatio > 0.1) ? 60 * (Math.PI / 180) : 74 * (Math.PI / 180);
        this.camFov += (targetFov - this.camFov) * 0.2;

        Mat4.perspective(this.projMatrix, this.camFov, aspect, 0.5, 3800.0);

        // CAMERA SETUP
        let eyeX, eyeY, eyeZ, targetX, targetY, targetZ;
        const shake = (Math.random() - 0.5) * this.screenShake * 0.4;

        if (this.viewMode === 'FPP') {
          // FIRST-PERSON PERSPECTIVE (FPP)
          if (this.player.inVehicle) {
            const car = this.player.inVehicle;
            const fwd = car.getForwardVector();
            const right = car.getRightVector();
            // Cockpit driver seat position
            eyeX = car.x + fwd.x * 4 - right.x * 7;
            eyeY = 16.0 + shake;
            eyeZ = car.y + fwd.y * 4 - right.y * 7;

            // Looking forward through the windshield with free-look pitch & yaw offset
            const lookYaw = car.angle + input.yaw;
            const lookPitch = input.pitch;

            targetX = eyeX + Math.cos(lookYaw) * Math.cos(lookPitch) * 100;
            targetY = eyeY + Math.sin(lookPitch) * 100;
            targetZ = eyeZ + Math.sin(lookYaw) * Math.cos(lookPitch) * 100;
          } else {
            // On-foot eye position with dynamic head bobbing
            eyeX = this.player.x;
            eyeY = this.player.z + this.player.headBobY + shake;
            eyeZ = this.player.y;

            const lookYaw = input.yaw;
            const lookPitch = input.pitch;

            targetX = eyeX + Math.cos(lookYaw) * Math.cos(lookPitch) * 100;
            targetY = eyeY + Math.sin(lookPitch) * 100;
            targetZ = eyeZ + Math.sin(lookYaw) * Math.cos(lookPitch) * 100;
          }
        } else {
          // TOP-DOWN / HELICOPTER CAMERA VIEW
          eyeX = this.player.x;
          eyeY = 320.0 + shake;
          eyeZ = this.player.y + 120.0;

          targetX = this.player.x;
          targetY = 0.0;
          targetZ = this.player.y;
        }

        this.camX = eyeX;
        this.camY = eyeY;
        this.camZ = eyeZ;

        Mat4.lookAt(this.viewMatrix, [eyeX, eyeY, eyeZ], [targetX, targetY, targetZ], [0, 1, 0]);

        // Clear WebGL Framebuffer
        gl.clearColor(0.08, 0.10, 0.18, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

        // 1. Render Sky Dome
        this.renderer.renderSky(this.projMatrix, this.viewMatrix, this.gameTime);

        // 2. Setup Lighting & Dynamic Point Lights
        gl.useProgram(this.renderer.program);
        gl.uniformMatrix4fv(this.renderer.uniforms.projection, false, this.projMatrix);
        gl.uniformMatrix4fv(this.renderer.uniforms.view, false, this.viewMatrix);
        gl.uniformMatrix4fv(this.renderer.uniforms.model, false, this.identityModel);
        gl.uniform3fv(this.renderer.uniforms.cameraPos, [eyeX, eyeY, eyeZ]);
        gl.uniform3fv(this.renderer.uniforms.sunDir, this.renderer.sunDir);
        gl.uniform3fv(this.renderer.uniforms.sunColor, this.renderer.sunColor);
        gl.uniform3fv(this.renderer.uniforms.ambientColor, this.renderer.ambientColor);
        gl.uniform3fv(this.renderer.uniforms.fogColor, this.renderer.fogColor);
        gl.uniform1f(this.renderer.uniforms.fogDensity, this.renderer.fogDensity);
        gl.uniform1f(this.renderer.uniforms.time, this.gameTime);

        // GATHER POINT LIGHTS (Headlights, Sirens, Muzzle Flashes)
        let lightIdx = 0;
        const lights = this.renderer.uLightsLoc;
        const lightCols = this.renderer.uLightColorsLoc;

        // Player Headlights or Muzzle Flash
        if (this.player.inVehicle) {
          const car = this.player.inVehicle;
          const fwd = car.getForwardVector();
          gl.uniform4f(lights[lightIdx], car.x + fwd.x * 35, 10, car.y + fwd.y * 35, 280.0);
          gl.uniform3f(lightCols[lightIdx], 1.0, 0.95, 0.85);
          lightIdx++;
        } else if (this.player.muzzleFlashTimer > 0) {
          gl.uniform4f(lights[lightIdx], this.player.x, 22, this.player.y, 160.0);
          gl.uniform3f(lightCols[lightIdx], 1.0, 0.85, 0.4);
          lightIdx++;
        }

        // Active Police Cruiser Strobes
        for (const car of this.vehicles) {
          if (car.isPolice && car.sirenActive && !car.wrecked && lightIdx < 7) {
            const isRed = Math.floor(car.sirenTimer) % 2 === 0;
            gl.uniform4f(lights[lightIdx], car.x, 18, car.y, 220.0);
            if (isRed) gl.uniform3f(lightCols[lightIdx], 1.0, 0.05, 0.2);
            else gl.uniform3f(lightCols[lightIdx], 0.05, 0.4, 1.0);
            lightIdx++;
          }
        }

        // Zero out unused lights
        for (let i = lightIdx; i < 8; i++) {
          gl.uniform4f(lights[i], 0, 0, 0, 0);
          gl.uniform3f(lightCols[i], 0, 0, 0);
        }

        // 3. Render Static World (Roads, Sidewalks, Buildings, Palms, Lamps, Ocean)
        this.renderer.bindVertexFormat(this.renderer.staticVBO);
        gl.drawArrays(gl.TRIANGLES, 0, this.renderer.staticMesh.vertexCount);

        // 4. Build & Render Dynamic Entities (Cars, Pedestrians, Police, Projectiles, Particles, Pickups)
        const dynMesh = this.renderer.dynamicMesh;
        dynMesh.clear();

        // 3D Vehicles
        for (const car of this.vehicles) {
          car.render3D(dynMesh);
        }

        // 3D Pedestrians
        for (const ped of this.pedestrians) {
          ped.render3D(dynMesh);
        }

        // 3D Police Officers
        for (const off of this.police.officers) {
          off.render3D(dynMesh);
        }

        // 3D Pickups
        for (const pick of this.pickups) {
          pick.render3D(dynMesh);
        }

        // 3D Projectiles
        for (const p of this.projectiles) {
          p.render3D(dynMesh);
        }

        // 3D Particles
        for (const part of this.particles) {
          part.render3D(dynMesh);
        }

        // In Top-Down mode, render on-foot 3D player body
        if (this.viewMode === 'TOP_DOWN' && !this.player.inVehicle && this.player.alive) {
          dynMesh.addBox(this.player.x - 4, 0, this.player.y - 4, this.player.x + 4, 24, this.player.y + 4, [0.0, 0.95, 1.0, 1.0], 7);
          dynMesh.addBox(this.player.x - 3, 24, this.player.y - 3, this.player.x + 3, 30, this.player.y + 3, [1.0, 0.72, 0.54, 1.0], 7);
        }

        this.renderer.uploadDynamicMesh();
        this.renderer.bindVertexFormat(this.renderer.dynamicVBO);
        gl.drawArrays(gl.TRIANGLES, 0, dynMesh.vertexCount);

        // 5. Render First-Person Viewmodel (Hands & Weapon / Cockpit)
        if (this.viewMode === 'FPP') {
          gl.clear(gl.DEPTH_BUFFER_BIT); // Clear depth so viewmodel never clips inside walls!

          const vmProj = Mat4.create();
          Mat4.perspective(vmProj, 72 * (Math.PI / 180), aspect, 0.1, 120.0);
          gl.uniformMatrix4fv(this.renderer.uniforms.projection, false, vmProj);

          // Local viewmodel matrix (centered at origin, looking forward)
          const vmView = Mat4.create();
          gl.uniformMatrix4fv(this.renderer.uniforms.view, false, vmView);

          const vmMesh = this.renderer.viewmodelMesh;
          vmMesh.clear();
          this.player.renderViewmodel(vmMesh);

          this.renderer.uploadViewmodelMesh();
          this.renderer.bindVertexFormat(this.renderer.viewmodelVBO);
          gl.drawArrays(gl.TRIANGLES, 0, vmMesh.vertexCount);
        }

        // 6. Render 2D Overlay HUD & Radar Minimap
        this.renderHUD();
      }

      renderHUD() {
        const ctx = this.hudCtx;
        const w = this.hudCanvas.width;
        const h = this.hudCanvas.height;
        ctx.clearRect(0, 0, w, h);

        const isMobile = w < 768;
        const hudW = isMobile ? 180 : 220;
        const hudH = isMobile ? 130 : 160;
        const hudX = w - hudW - (isMobile ? 10 : 20);
        const hudY = isMobile ? 42 : 18;

        // Tactical HUD Panel
        ctx.save();
        ctx.fillStyle = 'rgba(12, 12, 22, 0.88)';
        ctx.strokeStyle = '#00f3ff';
        ctx.lineWidth = 1.5;
        ctx.shadowColor = 'rgba(0, 243, 255, 0.35)';
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.roundRect(hudX, hudY, hudW, hudH, 6);
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0;

        const barW = isMobile ? 105 : 140;
        const barH = isMobile ? 10 : 12;

        // Health Bar
        ctx.fillStyle = '#ff007f';
        ctx.font = isMobile ? 'bold 10px Impact, sans-serif' : 'bold 12px Impact, sans-serif';
        ctx.fillText('HEALTH', hudX + 10, hudY + (isMobile ? 18 : 22));
        ctx.fillStyle = '#221122';
        ctx.fillRect(hudX + (isMobile ? 58 : 65), hudY + (isMobile ? 9 : 12), barW, barH);
        ctx.fillStyle = '#ff007f';
        ctx.shadowColor = '#ff007f';
        ctx.shadowBlur = 6;
        ctx.fillRect(hudX + (isMobile ? 58 : 65), hudY + (isMobile ? 9 : 12), (this.player.health / this.player.maxHealth) * barW, barH);
        ctx.shadowBlur = 0;

        // Armor Bar
        ctx.fillStyle = '#00f3ff';
        ctx.fillText('ARMOR', hudX + 10, hudY + (isMobile ? 36 : 44));
        ctx.fillStyle = '#11222b';
        ctx.fillRect(hudX + (isMobile ? 58 : 65), hudY + (isMobile ? 27 : 34), barW, barH);
        ctx.fillStyle = '#00f3ff';
        ctx.shadowColor = '#00f3ff';
        ctx.shadowBlur = 6;
        ctx.fillRect(hudX + (isMobile ? 58 : 65), hudY + (isMobile ? 27 : 34), (this.player.armor / this.player.maxArmor) * barW, barH);
        ctx.shadowBlur = 0;

        // Cash Counter
        ctx.font = isMobile ? '900 15px monospace' : '900 18px monospace';
        ctx.fillStyle = '#00ff66';
        ctx.shadowColor = '#00ff66';
        ctx.shadowBlur = 8;
        const cashStr = '$' + String(this.player.cash).padStart(7, '0');
        ctx.fillText(cashStr, hudX + 10, hudY + (isMobile ? 62 : 76));
        ctx.shadowBlur = 0;

        // Weapon & Ammo
        const wep = this.player.weapons[this.player.weaponIdx];
        ctx.font = isMobile ? 'bold 11px Impact, sans-serif' : 'bold 13px Impact, sans-serif';
        ctx.fillStyle = '#ffe600';
        ctx.fillText(wep.name, hudX + 10, hudY + (isMobile ? 84 : 102));

        ctx.font = isMobile ? 'bold 11px monospace' : 'bold 13px monospace';
        ctx.fillStyle = '#ffffff';
        const ammoStr = wep.ammo === Infinity ? '∞' : String(wep.ammo);
        ctx.fillText(`[ ${ammoStr} ]`, hudX + (isMobile ? 110 : 120), hudY + (isMobile ? 84 : 102));

        // Wanted Stars (1 to 5)
        const starX = hudX + (isMobile ? 12 : 16);
        const starY = hudY + (isMobile ? 108 : 132);
        const starGap = isMobile ? 30 : 38;
        const isBlinking = this.police.evading && Math.floor(this.police.flashTimer) % 2 === 0;

        for (let i = 1; i <= 5; i++) {
          const active = i <= this.police.wantedLevel;
          ctx.save();
          ctx.font = isMobile ? '16px sans-serif' : '20px sans-serif';
          if (active) {
            if (isBlinking) {
              ctx.fillStyle = 'rgba(150, 150, 150, 0.4)';
            } else {
              ctx.fillStyle = '#ffe600';
              ctx.shadowColor = '#ff007f';
              ctx.shadowBlur = 10;
            }
          } else {
            ctx.fillStyle = 'rgba(60, 60, 80, 0.5)';
          }
          ctx.fillText('★', starX + (i - 1) * starGap, starY);
          ctx.restore();
        }

        // Evading Countdown
        if (this.police.evading && this.police.wantedLevel > 0) {
          ctx.font = isMobile ? 'bold 10px Impact, sans-serif' : 'bold 11px Impact, sans-serif';
          ctx.fillStyle = '#ffe600';
          ctx.fillText(`EVADING: ${Math.ceil(this.police.cooldownTimer)}s`, hudX + 10, hudY + (isMobile ? 124 : 154));
        }
        ctx.restore();

        // Speedometer when in Car
        if (this.player.inVehicle) {
          const car = this.player.inVehicle;
          const spdW = isMobile ? 160 : 220;
          const spdX = w / 2 - spdW / 2;
          const spdY = isMobile ? 12 : h - 42;

          ctx.save();
          ctx.fillStyle = 'rgba(12, 12, 22, 0.9)';
          ctx.strokeStyle = '#ff007f';
          ctx.lineWidth = 1;
          ctx.fillRect(spdX, spdY, spdW, 28);
          ctx.strokeRect(spdX, spdY, spdW, 28);

          ctx.font = 'bold 11px Impact, sans-serif';
          ctx.fillStyle = '#ff007f';
          ctx.fillText('MPH', spdX + 6, spdY + 19);

          const mph = Math.floor((car.speed / car.maxSpeed) * 140);
          ctx.font = '900 13px monospace';
          ctx.fillStyle = '#00f3ff';
          ctx.fillText(String(mph).padStart(3, ' '), spdX + 32, spdY + 19);

          ctx.fillStyle = '#ff007f';
          ctx.shadowColor = '#ff007f';
          ctx.shadowBlur = 6;
          const ratio = Math.min(1, car.speed / car.maxSpeed);
          const barWidth = isMobile ? 40 : 70;
          ctx.fillRect(spdX + 65, spdY + 8, ratio * barWidth, 12);

          ctx.font = 'bold 10px Impact, sans-serif';
          ctx.fillStyle = '#00f3ff';
          ctx.fillText(isMobile ? '[F] / 🚗' : '[F] EXIT', spdX + (isMobile ? 112 : 160), spdY + 19);
          ctx.restore();
        }

        // Floating Prompt to Enter Nearest Car on Foot
        if (!this.player.inVehicle && this.player.alive) {
          let nearestCar = null;
          let minDist = 85;
          for (const car of this.vehicles) {
            if (car.wrecked) continue;
            const dist = Math.hypot(car.x - this.player.x, car.y - this.player.y);
            if (dist < minDist) {
              minDist = dist;
              nearestCar = car;
            }
          }
          if (nearestCar) {
            ctx.save();
            const actionVerb = nearestCar.driver ? 'JACK' : 'ENTER';
            const text = isMobile ? `TAP 🚗 TO ${actionVerb}` : `[F] ${actionVerb} VEHICLE`;
            ctx.font = '900 13px Impact, sans-serif';
            ctx.fillStyle = 'rgba(14, 14, 26, 0.92)';
            ctx.strokeStyle = '#00f3ff';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.roundRect(w / 2 - 80, h / 2 + 35, 160, 28, 4);
            ctx.fill();
            ctx.stroke();
            ctx.fillStyle = '#00f3ff';
            ctx.textAlign = 'center';
            ctx.fillText(text, w / 2, h / 2 + 54);
            ctx.textAlign = 'start';
            ctx.restore();
          }
        }

        // Circular Radar Minimap (Lower Left on Desktop, Upper Left on Mobile)
        this.renderMinimap(ctx);

        // Floating Notifications (Center Left)
        if (this.notifications.length > 0) {
          ctx.save();
          let ny = 80;
          for (const notif of this.notifications) {
            const alpha = Math.max(0, notif.life / notif.maxLife);
            ctx.globalAlpha = alpha;
            ctx.font = '900 15px Impact, sans-serif';
            ctx.fillStyle = notif.color;
            ctx.shadowColor = notif.color;
            ctx.shadowBlur = 8;
            ctx.fillText(notif.text, 24, ny);
            ny += 22;
          }
          ctx.restore();
        }
      }

      renderMinimap(ctx) {
        ctx.save();
        const isMobile = this.hudCanvas.width < 768;
        const mapSize = isMobile ? 115 : 175;
        const mapX = isMobile ? 14 : 20;
        const mapY = isMobile ? 54 : this.hudCanvas.height - mapSize - 20;

        ctx.beginPath();
        ctx.arc(mapX + mapSize / 2, mapY + mapSize / 2, mapSize / 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(10, 10, 20, 0.92)';
        ctx.fill();
        ctx.strokeStyle = '#00f3ff';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#00f3ff';
        ctx.shadowBlur = 10;
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.clip();

        // Crosshairs on Radar
        ctx.strokeStyle = 'rgba(0, 243, 255, 0.2)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(mapX, mapY + mapSize / 2);
        ctx.lineTo(mapX + mapSize, mapY + mapSize / 2);
        ctx.moveTo(mapX + mapSize / 2, mapY);
        ctx.lineTo(mapX + mapSize / 2, mapY + mapSize);
        ctx.stroke();

        const scale = mapSize / CONFIG.WORLD_WIDTH;

        // Roads
        ctx.fillStyle = '#1c1c34';
        CONFIG.GRID_ROADS_Y.forEach(ry => {
          ctx.fillRect(mapX, mapY + ry * scale - 2, mapSize, 4);
        });
        CONFIG.GRID_ROADS_X.forEach(rx => {
          ctx.fillRect(mapX + rx * scale - 2, mapY, 4, mapSize);
        });

        // Pay 'N' Spray [W]
        const pSpot = this.world.specialSpots.payNSpray;
        if (pSpot) {
          ctx.fillStyle = '#00ff66';
          ctx.font = 'bold 10px monospace';
          ctx.fillText('W', mapX + pSpot.x * scale - 4, mapY + pSpot.y * scale + 4);
        }

        // Ammu-Nation [+]
        const aSpot = this.world.specialSpots.ammuNation;
        if (aSpot) {
          ctx.fillStyle = '#ffe600';
          ctx.font = 'bold 10px monospace';
          ctx.fillText('+', mapX + aSpot.x * scale - 4, mapY + aSpot.y * scale + 4);
        }

        // Hospital [H]
        const hSpot = this.world.specialSpots.hospital;
        if (hSpot) {
          ctx.fillStyle = '#ff007f';
          ctx.font = 'bold 10px monospace';
          ctx.fillText('H', mapX + hSpot.x * scale - 4, mapY + hSpot.y * scale + 4);
        }

        // Civilian Vehicles
        ctx.fillStyle = 'rgba(255, 230, 0, 0.75)';
        for (const car of this.vehicles) {
          if (!car.isPolice) {
            ctx.fillRect(mapX + car.x * scale - 1.5, mapY + car.y * scale - 1.5, 3, 3);
          }
        }

        // Police Cruisers
        for (const car of this.police.cruisers) {
          if (!car.wrecked) {
            ctx.fillStyle = Math.floor(this.gameTime * 8) % 2 === 0 ? '#ff0055' : '#00a6ff';
            ctx.beginPath();
            ctx.arc(mapX + car.x * scale, mapY + car.y * scale, 3.5, 0, Math.PI * 2);
            ctx.fill();
          }
        }

        // Player Heading Arrow
        ctx.save();
        ctx.translate(mapX + this.player.x * scale, mapY + this.player.y * scale);
        ctx.rotate(this.player.angle);
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = '#00f3ff';
        ctx.shadowBlur = 6;
        ctx.beginPath();
        ctx.moveTo(6, 0);
        ctx.lineTo(-4, -4);
        ctx.lineTo(-2, 0);
        ctx.lineTo(-4, 4);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        ctx.restore();
      }

      start() {
        const loop = (timestamp) => {
          const dt = Math.min(0.08, (timestamp - this.lastTime) / 1000);
          this.lastTime = timestamp;

          this.update(dt);
          this.render();

          requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);
      }
    }

    /* ==========================================================================
       12. INITIALIZE GAME & UI CONTROLS
       ========================================================================== */
    window.addEventListener('load', () => {
      window.game = new GameEngine();
      window.game.start();

      const btnView = document.getElementById('btnView');
      const btnMusic = document.getElementById('btnMusic');
      const btnSfx = document.getElementById('btnSfx');
      const btnCrt = document.getElementById('btnCrt');
      const btnHelp = document.getElementById('btnHelp');
      const helpModal = document.getElementById('helpModal');
      const btnCloseModal = document.getElementById('btnCloseModal');
      const btnStartGame = document.getElementById('btnStartGame');
      const crtOverlay = document.getElementById('crtOverlay');

      btnView.addEventListener('click', () => {
        window.game.toggleViewMode();
      });

      btnMusic.addEventListener('click', () => {
        audio.init();
        audio.musicEnabled = !audio.musicEnabled;
        btnMusic.textContent = `🎵 MUSIC: ${audio.musicEnabled ? 'ON' : 'OFF'}`;
      });

      btnSfx.addEventListener('click', () => {
        audio.init();
        audio.sfxEnabled = !audio.sfxEnabled;
        btnSfx.textContent = `🔊 SFX: ${audio.sfxEnabled ? 'ON' : 'OFF'}`;
      });

      btnCrt.addEventListener('click', () => {
        crtOverlay.classList.toggle('disabled');
        const active = !crtOverlay.classList.contains('disabled');
        btnCrt.textContent = `📺 CRT: ${active ? 'ON' : 'OFF'}`;
      });

      const toggleModal = () => {
        helpModal.classList.toggle('open');
      };

      btnHelp.addEventListener('click', toggleModal);
      btnCloseModal.addEventListener('click', toggleModal);
      btnStartGame.addEventListener('click', toggleModal);
    });
    """

