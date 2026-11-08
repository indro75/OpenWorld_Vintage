# js_entities.py - 3D Vehicles, Cockpit, Player, Viewmodel, Pedestrians, Police AI

def get_js_vehicle_and_cockpit():
    return r"""
    /* ==========================================================================
       8. 3D VEHICLES & FIRST-PERSON COCKPIT SYSTEM
       ========================================================================== */
    class Vehicle {
      constructor(x, y, angle, type = 'sedan') {
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.type = type;
        this.driver = null;

        const specs = {
          sports: { w: 34, l: 72, h: 18, maxSpd: 590, accel: 490, reverseSpd: 180, turnSpd: 3.3, driftGrip: 0.94, hp: 100, col: [1.0, 0.0, 0.5, 1.0] },
          muscle: { w: 36, l: 74, h: 20, maxSpd: 530, accel: 530, reverseSpd: 170, turnSpd: 2.9, driftGrip: 0.91, hp: 135, col: [0.54, 0.17, 0.89, 1.0] },
          sedan:  { w: 34, l: 68, h: 21, maxSpd: 460, accel: 400, reverseSpd: 150, turnSpd: 3.0, driftGrip: 0.88, hp: 110, col: [0.0, 0.85, 1.0, 1.0] },
          taxi:   { w: 34, l: 68, h: 21, maxSpd: 460, accel: 400, reverseSpd: 150, turnSpd: 3.0, driftGrip: 0.88, hp: 115, col: [1.0, 0.88, 0.0, 1.0] },
          police: { w: 35, l: 72, h: 22, maxSpd: 550, accel: 520, reverseSpd: 180, turnSpd: 3.3, driftGrip: 0.89, hp: 150, col: [0.95, 0.95, 0.98, 1.0] },
          van:    { w: 40, l: 82, h: 28, maxSpd: 390, accel: 320, reverseSpd: 130, turnSpd: 2.4, driftGrip: 0.82, hp: 195, col: [0.92, 0.92, 0.94, 1.0] }
        };

        const s = specs[type] || specs.sedan;
        this.width = s.w;
        this.length = s.l;
        this.height = s.h;
        this.maxSpeed = s.maxSpd;
        this.accel = s.accel;
        this.reverseSpeed = s.reverseSpd;
        this.turnSpeed = s.turnSpd;
        this.driftGrip = s.driftGrip;
        this.maxHp = s.hp;
        this.hp = s.hp;
        this.color = s.col;

        this.vx = 0;
        this.vy = 0;
        this.steer = 0;
        this.wheelRotation = 0;
        this.speed = 0;
        this.isHandbraking = false;
        this.isSkidding = false;
        this.isPolice = type === 'police';
        this.sirenActive = this.isPolice;
        this.sirenTimer = 0;

        this.wrecked = false;
        this.burning = false;
        this.burnTimer = 3.0;

        this.prevRearL = null;
        this.prevRearR = null;
      }

      getForwardVector() {
        return { x: Math.cos(this.angle), y: Math.sin(this.angle) };
      }

      getRightVector() {
        return { x: -Math.sin(this.angle), y: Math.cos(this.angle) };
      }

      getCollisionCircles() {
        const fwd = this.getForwardVector();
        const r = this.width * 0.45;
        const d = this.length * 0.28;
        return [
          { x: this.x - fwd.x * d, y: this.y - fwd.y * d, r: r },
          { x: this.x, y: this.y, r: r },
          { x: this.x + fwd.x * d, y: this.y + fwd.y * d, r: r }
        ];
      }

      takeDamage(amount) {
        if (this.wrecked) return;
        this.hp -= amount;
        if (this.hp <= this.maxHp * 0.35 && !this.burning) {
          this.burning = true;
        }
        if (this.hp <= 0) {
          this.hp = 0;
          this.wrecked = true;
          this.burning = false;
          audio.playExplosion();
          if (window.game) {
            window.game.addScreenShake(14, 0.4);
            window.game.dealRadiusDamage(this.x, this.y, 140, 120, this);
            for (let i = 0; i < 24; i++) {
              window.game.spawnParticle(this.x, this.y, (Math.random() - 0.5) * 220, (Math.random() - 0.5) * 220, '#ff4400', 8, 0.8, 1.2, 'smoke');
            }
          }
        }
      }

      updatePhysics(dt, throttle, steeringInput, handbrake) {
        if (this.wrecked) {
          this.vx *= 0.92;
          this.vy *= 0.92;
          this.x += this.vx * dt;
          this.y += this.vy * dt;
          return;
        }

        const fwd = this.getForwardVector();
        const right = this.getRightVector();

        let vFwd = this.vx * fwd.x + this.vy * fwd.y;
        let vLat = this.vx * right.x + this.vy * right.y;

        const targetSteer = steeringInput * 0.55;
        this.steer += (targetSteer - this.steer) * 12 * dt;

        if (throttle > 0) {
          if (vFwd < -20) {
            vFwd += this.accel * 1.5 * dt;
          } else {
            vFwd += this.accel * dt;
            if (vFwd > this.maxSpeed) vFwd = this.maxSpeed;
          }
        } else if (throttle < 0) {
          if (vFwd > 20) {
            vFwd -= this.accel * 1.7 * dt;
          } else {
            vFwd -= this.accel * 0.65 * dt;
            if (vFwd < -this.reverseSpeed) vFwd = -this.reverseSpeed;
          }
        } else {
          vFwd *= Math.pow(0.85, dt);
        }

        this.isHandbraking = handbrake;
        let lateralFrictionFactor = 0.82;
        if (handbrake) {
          lateralFrictionFactor = 0.95;
          vFwd *= Math.pow(0.7, dt);
        } else if (Math.abs(vLat) > 40) {
          lateralFrictionFactor = this.driftGrip;
        }

        vLat *= Math.pow(1 - lateralFrictionFactor, dt * 10);

        if (Math.abs(vFwd) > 10) {
          const turnAmount = (vFwd / (this.length * 0.9)) * Math.sin(this.steer) * this.turnSpeed * dt;
          this.angle += turnAmount;
        }

        const newFwd = this.getForwardVector();
        const newRight = this.getRightVector();
        this.vx = newFwd.x * vFwd + newRight.x * vLat;
        this.vy = newFwd.y * vFwd + newRight.y * vLat;
        this.speed = Math.hypot(this.vx, this.vy);

        this.wheelRotation += (vFwd / 8.0) * dt;

        this.isSkidding = (Math.abs(vLat) > 45 && this.speed > 55) || (handbrake && this.speed > 35);

        const rearDist = -this.length * 0.35;
        const halfW = this.width * 0.42;
        const curRearL = {
          x: this.x + fwd.x * rearDist - right.x * halfW,
          y: this.y + fwd.y * rearDist - right.y * halfW
        };
        const curRearR = {
          x: this.x + fwd.x * rearDist + right.x * halfW,
          y: this.y + fwd.y * rearDist + right.y * halfW
        };

        if (this.isSkidding && this.prevRearL && window.game && window.game.decals) {
          window.game.decals.addTireSkid(this.prevRearL.x, this.prevRearL.y, curRearL.x, curRearL.y);
          window.game.decals.addTireSkid(this.prevRearR.x, this.prevRearR.y, curRearR.x, curRearR.y);
          if (Math.random() < 0.25) audio.playTireSqueal();
          window.game.spawnParticle(curRearL.x, curRearL.y, (Math.random() - 0.5) * 20, (Math.random() - 0.5) * 20, 'rgba(180,180,200,0.4)', 4, 0.4, 1.2, 'smoke');
        }
        this.prevRearL = curRearL;
        this.prevRearR = curRearR;

        this.x += this.vx * dt;
        this.y += this.vy * dt;

        if (this.sirenActive) {
          this.sirenTimer += dt * 8;
          if (this.driver && Math.floor(this.sirenTimer) % 6 === 0) {
            audio.playSirenTone(Math.floor(this.sirenTimer) % 12 < 6 ? 750 : 920);
          }
        }

        if (this.burning && !this.wrecked) {
          this.burnTimer -= dt;
          if (window.game && Math.random() < 0.6) {
            const hood = { x: this.x + fwd.x * (this.length * 0.35), y: this.y + fwd.y * (this.length * 0.35) };
            window.game.spawnParticle(hood.x, hood.y, (Math.random() - 0.5) * 30, (Math.random() - 0.5) * 30, '#ff3300', 6, 0.5, 1.5, 'spark');
            window.game.spawnParticle(hood.x, hood.y, (Math.random() - 0.5) * 15, -30, 'rgba(40,40,40,0.7)', 8, 0.8, 1.0, 'smoke');
          }
          if (this.burnTimer <= 0) {
            this.takeDamage(this.maxHp);
          }
        }
      }

      render3D(mesh) {
        // Vehicle 3D Extrusion
        const halfL = this.length / 2;
        const halfW = this.width / 2;
        const h = this.height;

        const cosA = Math.cos(this.angle);
        const sinA = Math.sin(this.angle);

        // Helper to transform vehicle local coordinates to world
        const toWorld = (lx, ly, lz) => {
          const wx = this.x + lx * cosA - lz * sinA;
          const wz = this.y + lx * sinA + lz * cosA;
          return [wx, ly, wz];
        };

        const col = this.wrecked ? [0.15, 0.15, 0.18, 1.0] : this.color;
        const colDark = [col[0] * 0.7, col[1] * 0.7, col[2] * 0.7, 1.0];
        const colGlass = [0.10, 0.18, 0.28, 0.9];
        const colTire = [0.12, 0.12, 0.14, 1.0];
        const colRim = [0.75, 0.78, 0.82, 1.0];

        // 1. Lower Chassis Box (MatType 6)
        const chassisH = h * 0.55;
        this.addTransformedBox(mesh, toWorld, -halfL, 3, -halfW, halfL, chassisH, halfW, col, 6);

        // 2. Cabin / Glass Greenhouse Box
        const cabinBack = -halfL * 0.6;
        const cabinFront = halfL * 0.25;
        const cabinHalfW = halfW * 0.85;
        this.addTransformedBox(mesh, toWorld, cabinBack, chassisH, -cabinHalfW, cabinFront, h, cabinHalfW, colGlass, 6);

        // 3. Cabin Roof
        this.addTransformedBox(mesh, toWorld, cabinBack + 2, h, -cabinHalfW + 1, cabinFront - 2, h + 1.2, cabinHalfW - 1, colDark, 6);

        // 4. Wheels (4 3D cylinders/boxes)
        const wheelR = 5.5;
        const wheelW = 3.0;
        const wheelY = wheelR;
        const frontAxle = halfL * 0.6;
        const rearAxle = -halfL * 0.6;
        const axleHalfW = halfW + 0.5;

        // Front Left & Right (steerable)
        [-axleHalfW, axleHalfW].forEach(wz => {
          this.addTransformedBox(mesh, toWorld, frontAxle - 5, 0, wz - wheelW / 2, frontAxle + 5, wheelR * 2, wz + wheelW / 2, colTire, 6);
          this.addTransformedBox(mesh, toWorld, rearAxle - 5, 0, wz - wheelW / 2, rearAxle + 5, wheelR * 2, wz + wheelW / 2, colTire, 6);
        });

        // 5. Headlights & Taillights
        const hlCol = [1.0, 0.95, 0.8, 1.0];
        const tlCol = [1.0, 0.05, 0.05, 1.0];
        // Dual Front Headlights
        this.addTransformedBox(mesh, toWorld, halfL - 0.8, chassisH * 0.5, -halfW * 0.75, halfL + 0.5, chassisH * 0.85, -halfW * 0.35, hlCol, 9);
        this.addTransformedBox(mesh, toWorld, halfL - 0.8, chassisH * 0.5, halfW * 0.35, halfL + 0.5, chassisH * 0.85, halfW * 0.75, hlCol, 9);

        // Dual Rear Taillights
        this.addTransformedBox(mesh, toWorld, -halfL - 0.5, chassisH * 0.5, -halfW * 0.8, -halfL + 0.8, chassisH * 0.85, -halfW * 0.4, tlCol, 9);
        this.addTransformedBox(mesh, toWorld, -halfL - 0.5, chassisH * 0.5, halfW * 0.4, -halfL + 0.8, chassisH * 0.85, halfW * 0.8, tlCol, 9);

        // 6. Police Emergency Lightbar (flashes Red & Blue)
        if (this.isPolice && this.sirenActive) {
          const isRed = Math.floor(this.sirenTimer) % 2 === 0;
          const colLbar1 = isRed ? [1.0, 0.0, 0.2, 1.0] : [0.0, 0.4, 1.0, 1.0];
          const colLbar2 = isRed ? [0.0, 0.4, 1.0, 1.0] : [1.0, 0.0, 0.2, 1.0];

          this.addTransformedBox(mesh, toWorld, cabinBack * 0.3, h + 1.2, -cabinHalfW * 0.8, cabinBack * 0.3 + 5, h + 5.5, 0, colLbar1, 9);
          this.addTransformedBox(mesh, toWorld, cabinBack * 0.3, h + 1.2, 0, cabinBack * 0.3 + 5, h + 5.5, cabinHalfW * 0.8, colLbar2, 9);
        }

        // 7. Sports Car Rear Spoiler
        if (this.type === 'sports') {
          this.addTransformedBox(mesh, toWorld, -halfL + 3, chassisH + 5, -halfW * 0.85, -halfL + 7, chassisH + 7, halfW * 0.85, colDark, 6);
        }
      }

      addTransformedBox(mesh, toWorld, minX, minY, minZ, maxX, maxY, maxZ, color, matType) {
        // Compute 8 corners in world coordinates
        const p000 = toWorld(minX, minY, minZ);
        const p100 = toWorld(maxX, minY, minZ);
        const p110 = toWorld(maxX, maxY, minZ);
        const p010 = toWorld(minX, maxY, minZ);

        const p001 = toWorld(minX, minY, maxZ);
        const p101 = toWorld(maxX, minY, maxZ);
        const p111 = toWorld(maxX, maxY, maxZ);
        const p011 = toWorld(minX, maxY, maxZ);

        // Top (Y+)
        mesh.addQuad(p010, p110, p111, p011, [0, 1, 0], color, matType);
        // Bottom (Y-)
        mesh.addQuad(p001, p101, p100, p000, [0, -1, 0], color, matType);
        // Front (X+)
        mesh.addQuad(p100, p101, p111, p110, [1, 0, 0], color, matType);
        // Back (X-)
        mesh.addQuad(p001, p000, p010, p011, [-1, 0, 0], color, matType);
        // Right (Z+)
        mesh.addQuad(p101, p001, p011, p111, [0, 0, 1], color, matType);
        // Left (Z-)
        mesh.addQuad(p000, p100, p110, p010, [0, 0, -1], color, matType);
      }

      renderCockpit3D(mesh) {
        // First-Person Cockpit Interior
        // Rendered in player viewmodel space: driver is seated at [0, 0, 0] looking out forward (-Z)
        const colDash = [0.12, 0.13, 0.16, 1.0];
        const colWheel = [0.18, 0.18, 0.22, 1.0];
        const colGauge = [0.0, 0.95, 1.0, 1.0];
        const colHood = this.color;

        // 1. Sleek Dashboard stretching across the windshield base
        mesh.addBox(-26, -16, -26, 26, -7, -12, colDash, 8);

        // 2. Instrument Binnacle with Speedometer & Tachometer Dials
        mesh.addBox(-14, -7, -22, -2, -3, -15, colDash, 8);
        // Speedometer Dial Face
        mesh.addBox(-12, -6, -22.2, -8, -4, -22.0, colGauge, 9);
        // Tachometer Dial Face
        mesh.addBox(-6, -6, -22.2, -2, -4, -22.0, [1.0, 0.2, 0.4, 1.0], 9);

        // 3. 3D Steering Wheel directly in front of driver (rotates with steer!)
        const wheelSteerAngle = this.steer * 2.2;
        const wheelCenterX = -8;
        const wheelCenterY = -7;
        const wheelCenterZ = -14;
        const wheelRadius = 5.8;

        // Draw rotated circular steering wheel rim
        for (let i = 0; i < 12; i++) {
          const a1 = (i / 12) * Math.PI * 2 + wheelSteerAngle;
          const a2 = ((i + 1) / 12) * Math.PI * 2 + wheelSteerAngle;
          const x1 = wheelCenterX + Math.cos(a1) * wheelRadius;
          const y1 = wheelCenterY + Math.sin(a1) * wheelRadius;
          const x2 = wheelCenterX + Math.cos(a2) * wheelRadius;
          const y2 = wheelCenterY + Math.sin(a2) * wheelRadius;
          mesh.addBox(Math.min(x1, x2) - 0.7, Math.min(y1, y2) - 0.7, wheelCenterZ - 0.6,
                      Math.max(x1, x2) + 0.7, Math.max(y1, y2) + 0.7, wheelCenterZ + 0.6, colWheel, 8);
        }
        // Steering Column & Hub
        mesh.addBox(wheelCenterX - 1.8, wheelCenterY - 1.8, wheelCenterZ - 0.8,
                    wheelCenterX + 1.8, wheelCenterY + 1.8, wheelCenterZ + 0.8, [0.3, 0.3, 0.35, 1.0], 8);

        // 4. Sloped Windshield Frame & A-Pillars
        mesh.addBox(-26, -7, -26, -23, 18, -10, colDash, 8); // Left A-Pillar
        mesh.addBox(23, -7, -26, 26, 18, -10, colDash, 8);   // Right A-Pillar
        mesh.addBox(-26, 15, -26, 26, 18, -12, colDash, 8);  // Roof Visor Header

        // 5. Rearview Mirror
        mesh.addBox(-4, 10, -16, 4, 13, -15, [0.15, 0.15, 0.18, 1.0], 8);
        mesh.addBox(-3.6, 10.3, -15.1, 3.6, 12.7, -14.9, [0.4, 0.6, 0.8, 1.0], 9);

        // 6. Visible Car Hood in perspective extending out front
        mesh.addBox(-22, -13, -55, 22, -7.5, -26, colHood, 8);
      }
    }
    """

def get_js_player_and_viewmodel():
    return r"""
    /* ==========================================================================
       9. FIRST-PERSON PLAYER & 3D WEAPON VIEWMODEL RIG
       ========================================================================== */
    class Player {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.z = 24.0; // Eye-height in 3D
        this.vx = 0;
        this.vy = 0;
        this.vz = 0;
        this.angle = 0;
        this.radius = 14;

        this.health = 100;
        this.maxHealth = 100;
        this.armor = 100;
        this.maxArmor = 100;
        this.cash = 500;
        this.inVehicle = null;

        // Jumping & Physics
        this.isGrounded = true;
        this.gravity = -340;
        this.jumpPower = 115;

        // First-Person Walk / Sway Animation
        this.walkCycle = 0;
        this.headBobY = 0;
        this.headBobX = 0;
        this.adsRatio = 0; // 0 = hip fire, 1 = aiming down sights

        // Weapon Inventory
        this.weaponIdx = 1;
        this.weapons = [
          { name: 'FISTS', fireRate: 0.35, ammo: Infinity, dmg: 25, spread: 0.08, speed: 0, range: 45 },
          { name: 'PISTOL', fireRate: 0.22, ammo: 80, dmg: 35, spread: 0.035, speed: 1800, range: 850 },
          { name: 'MICRO UZI', fireRate: 0.08, ammo: 180, dmg: 22, spread: 0.085, speed: 1700, range: 750 },
          { name: 'SHOTGUN', fireRate: 0.75, ammo: 36, dmg: 24, spread: 0.20, speed: 1400, range: 600 }
        ];

        // Weapon Animations & FX
        this.fireCooldown = 0;
        this.recoilPitch = 0;
        this.recoilSlide = 0;
        this.muzzleFlashTimer = 0;
        this.shotgunPumpTimer = 0;
        this.punchHand = 0; // 0 = left, 1 = right
        this.punchAnim = 0;

        this.alive = true;
      }

      switchWeapon(dir) {
        this.weaponIdx = (this.weaponIdx + dir + this.weapons.length) % this.weapons.length;
      }

      setWeapon(idx) {
        if (idx >= 0 && idx < this.weapons.length) this.weaponIdx = idx;
      }

      takeDamage(amount) {
        if (!this.alive) return;
        if (this.armor > 0) {
          const armorAbsorb = amount * 0.7;
          this.armor -= armorAbsorb;
          amount -= armorAbsorb;
          if (this.armor < 0) {
            amount += Math.abs(this.armor);
            this.armor = 0;
          }
        }
        this.health -= amount;
        window.game.addScreenShake(8, 0.25);
        if (this.health <= 0) {
          this.health = 0;
          this.alive = false;
          window.game.triggerWasted();
        }
      }

      update(dt) {
        if (!this.alive) return;

        if (this.fireCooldown > 0) this.fireCooldown -= dt;
        if (this.muzzleFlashTimer > 0) this.muzzleFlashTimer -= dt;
        if (this.shotgunPumpTimer > 0) this.shotgunPumpTimer -= dt;
        if (this.punchAnim > 0) this.punchAnim -= dt * 6.5;

        // Recoil Spring Recovery
        this.recoilPitch *= Math.pow(0.15, dt * 10);
        this.recoilSlide *= Math.pow(0.2, dt * 10);

        // Aim Down Sights (ADS) smooth interpolation on Right Click
        const targetADS = (input.rightMouseDown && !this.inVehicle) ? 1.0 : 0.0;
        this.adsRatio += (targetADS - this.adsRatio) * 14 * dt;

        // IN VEHICLE
        if (this.inVehicle) {
          this.x = this.inVehicle.x;
          this.y = this.inVehicle.y;
          this.z = 16.0;
          this.angle = this.inVehicle.angle;

          let throttle = 0;
          if (input.isDown('w') || input.isDown('arrowup')) throttle = 1;
          if (input.isDown('s') || input.isDown('arrowdown')) throttle = -1;

          let steer = 0;
          if (input.isDown('a') || input.isDown('arrowleft')) steer = -1;
          if (input.isDown('d') || input.isDown('arrowright')) steer = 1;

          const handbrake = input.isDown(' ');
          this.inVehicle.updatePhysics(dt, throttle, steer, handbrake);

          audio.updateEngineSound(this.inVehicle.speed / this.inVehicle.maxSpeed, true);

          if (input.wasJustPressed('h')) audio.playHorn();

          if (input.wasJustPressed('f') || input.wasJustPressed('enter')) {
            this.exitVehicle();
          }
          return;
        }

        audio.updateEngineSound(0, false);

        // ON FOOT FIRST-PERSON MOVEMENT (STRAFE & MOVE RELATIVE TO CAMERA YAW)
        const yaw = input.yaw;
        this.angle = yaw;

        let forward = 0;
        let strafe = 0;
        if (input.isDown('w') || input.isDown('arrowup')) forward += 1;
        if (input.isDown('s') || input.isDown('arrowdown')) forward -= 1;
        if (input.isDown('a') || input.isDown('arrowleft')) strafe -= 1;
        if (input.isDown('d') || input.isDown('arrowright')) strafe += 1;

        const isSprinting = input.isDown('shift') && forward > 0;
        let maxSpeed = isSprinting ? 275 : 180;
        if (this.adsRatio > 0.5) maxSpeed *= 0.65; // Slower movement when aiming down sights

        const fwdX = Math.cos(yaw);
        const fwdY = Math.sin(yaw);
        const rightX = -Math.sin(yaw);
        const rightY = Math.cos(yaw);

        let moveX = fwdX * forward + rightX * strafe;
        let moveY = fwdY * forward + rightY * strafe;

        const len = Math.hypot(moveX, moveY);
        if (len > 0.01) {
          moveX = (moveX / len) * maxSpeed;
          moveY = (moveY / len) * maxSpeed;
          this.vx = moveX;
          this.vy = moveY;

          this.walkCycle += dt * (isSprinting ? 18 : 11);
          this.headBobY = Math.sin(this.walkCycle * 2) * (isSprinting ? 1.6 : 1.0);
          this.headBobX = Math.cos(this.walkCycle) * (isSprinting ? 1.2 : 0.7);
        } else {
          this.vx *= 0.82;
          this.vy *= 0.82;
          this.headBobY *= 0.85;
          this.headBobX *= 0.85;
        }

        // Jump physics (Spacebar)
        if (input.wasJustPressed(' ') && this.isGrounded) {
          this.vz = this.jumpPower;
          this.isGrounded = false;
        }

        if (!this.isGrounded) {
          this.vz += this.gravity * dt;
          this.z += this.vz * dt;
          if (this.z <= 24.0) {
            this.z = 24.0;
            this.vz = 0;
            this.isGrounded = true;
          }
        }

        this.x += this.vx * dt;
        this.y += this.vy * dt;

        // Weapon selection keys
        if (input.wasJustPressed('1')) this.setWeapon(0);
        if (input.wasJustPressed('2')) this.setWeapon(1);
        if (input.wasJustPressed('3')) this.setWeapon(2);
        if (input.wasJustPressed('4')) this.setWeapon(3);
        if (input.wasJustPressed('q')) this.switchWeapon(-1);
        if (input.wasJustPressed('e')) this.switchWeapon(1);

        if (input.wasJustPressed('f') || input.wasJustPressed('enter')) {
          this.tryEnterVehicle();
        }

        // Fire Weapon on Left Click
        if (input.mouseDown && this.fireCooldown <= 0) {
          this.attack();
        }
      }

      attack() {
        const wep = this.weapons[this.weaponIdx];
        if (wep.ammo <= 0) return;

        this.fireCooldown = wep.fireRate;
        if (wep.ammo !== Infinity) wep.ammo--;

        window.game.police.addHeat(12);

        if (wep.name === 'FISTS') {
          audio.playShoot('punch');
          this.punchHand = (this.punchHand + 1) % 2;
          this.punchAnim = 1.0;
          const hitTarget = window.game.findMeleeTarget(this.x, this.y, this.angle, wep.range);
          if (hitTarget) {
            hitTarget.takeDamage(wep.dmg, this);
            audio.playHitMarker();
            window.game.showHitMarker();
            window.game.spawnParticle(hitTarget.x, hitTarget.y, (Math.random() - 0.5) * 60, (Math.random() - 0.5) * 60, '#ff0055', 4, 0.3, 1.0, 'spark');
          }
          return;
        }

        this.muzzleFlashTimer = 0.06;
        this.recoilSlide = 3.5;

        if (wep.name === 'PISTOL') {
          audio.playShoot('pistol');
          this.recoilPitch = 0.08;
          window.game.addScreenShake(2.5, 0.1);
          this.fireBullet(this.angle + (Math.random() - 0.5) * wep.spread, wep);
        } else if (wep.name === 'MICRO UZI') {
          audio.playShoot('smg');
          this.recoilPitch = 0.05;
          window.game.addScreenShake(2.0, 0.08);
          this.fireBullet(this.angle + (Math.random() - 0.5) * wep.spread, wep);
        } else if (wep.name === 'SHOTGUN') {
          audio.playShoot('shotgun');
          this.recoilPitch = 0.16;
          this.shotgunPumpTimer = 0.42;
          setTimeout(() => audio.playShotgunPump(), 200);
          window.game.addScreenShake(6.5, 0.2);
          for (let i = 0; i < 6; i++) {
            this.fireBullet(this.angle + (Math.random() - 0.5) * wep.spread, wep);
          }
        }
      }

      fireBullet(angle, wep) {
        const barrelDist = 18;
        const bx = this.x + Math.cos(this.angle) * barrelDist;
        const by = this.y + Math.sin(this.angle) * barrelDist;
        const vx = Math.cos(angle) * wep.speed;
        const vy = Math.sin(angle) * wep.speed;
        window.game.projectiles.push(new Projectile(bx, by, vx, vy, wep.dmg, 'player', '#ffe600'));
        window.game.spawnParticle(bx, by, 0, 0, '#ffffff', 5, 0.05, 2.0, 'spark');
      }

      tryEnterVehicle() {
        const cars = window.game.vehicles;
        let closest = null;
        let minDist = 85;

        for (const car of cars) {
          if (car.wrecked) continue;
          const dist = Math.hypot(car.x - this.x, car.y - this.y);
          if (dist < minDist) {
            minDist = dist;
            closest = car;
          }
        }

        if (closest) {
          if (closest.driver && closest.driver !== this) {
            closest.driver.carjacked();
            window.game.police.addHeat(30);
            window.game.showFloatingNotification('CARJACKED! +1 WANTED', '#ff007f');
          }
          this.inVehicle = closest;
          closest.driver = this;
          audio.playCrash(0.15);
        }
      }

      exitVehicle() {
        if (!this.inVehicle) return;
        const car = this.inVehicle;
        const right = car.getRightVector();
        let spawnX = car.x - right.x * (car.width * 0.7 + 18);
        let spawnY = car.y - right.y * (car.width * 0.7 + 18);

        this.x = spawnX;
        this.y = spawnY;
        this.z = 24.0;
        this.vx = car.vx * 0.3;
        this.vy = car.vy * 0.3;
        car.driver = null;
        this.inVehicle = null;
        audio.playCrash(0.15);
      }

      renderViewmodel(mesh) {
        if (this.inVehicle) {
          this.inVehicle.renderCockpit3D(mesh);
          return;
        }

        // FIRST-PERSON WEAPONS & HANDS (Rendered in camera-local space)
        // Camera looks towards -Z, Y is up, X is right
        const wep = this.weapons[this.weaponIdx];
        const colSkin = [1.0, 0.72, 0.54, 1.0];
        const colSleeve = [0.0, 0.95, 1.0, 1.0]; // Hawaiian teal shirt
        const colGunSteel = [0.12, 0.13, 0.16, 1.0];
        const colWood = [0.45, 0.25, 0.12, 1.0];
        const colFlash = [1.0, 0.9, 0.2, 1.0];

        // Head bobbing offset on viewmodel
        const bobX = this.headBobX * 0.6;
        const bobY = this.headBobY * 0.8 - this.recoilPitch * 14;

        // FISTS VIEWMODEL
        if (wep.name === 'FISTS') {
          const punchL = (this.punchHand === 0) ? Math.sin(this.punchAnim * Math.PI) * 12 : 0;
          const punchR = (this.punchHand === 1) ? Math.sin(this.punchAnim * Math.PI) * 12 : 0;

          // Left Arm & Fist
          mesh.addBox(-14 + bobX, -15 + bobY, -14 - punchL, -8 + bobX, -8 + bobY, -8 - punchL, colSleeve, 8);
          mesh.addBox(-12 + bobX, -13 + bobY, -20 - punchL, -7 + bobX, -8 + bobY, -14 - punchL, colSkin, 8);

          // Right Arm & Fist
          mesh.addBox(8 + bobX, -15 + bobY, -14 - punchR, 14 + bobX, -8 + bobY, -8 - punchR, colSleeve, 8);
          mesh.addBox(7 + bobX, -13 + bobY, -20 - punchR, 12 + bobX, -8 + bobY, -14 - punchR, colSkin, 8);
          return;
        }

        // WEAPONS (Hip fire vs Aim Down Sights)
        // ADS positions weapon in center of screen
        const hipX = 8.5 + bobX;
        const hipY = -7.5 + bobY;
        const hipZ = -16.0;

        const adsX = 0.0 + bobX * 0.2;
        const adsY = -5.0 + bobY * 0.2;
        const adsZ = -14.0;

        const gx = hipX + (adsX - hipX) * this.adsRatio;
        const gy = hipY + (adsY - hipY) * this.adsRatio;
        const gz = hipZ + (adsZ - hipZ) * this.adsRatio;

        // PISTOL
        if (wep.name === 'PISTOL') {
          // Slide & Barrel
          const slideBack = this.recoilSlide * 0.4;
          mesh.addBox(gx - 1.2, gy + 1.2, gz - 14, gx + 1.2, gy + 4.2, gz + slideBack, colGunSteel, 8);
          // Grip & Hand
          mesh.addBox(gx - 1.4, gy - 6.5, gz - 2, gx + 1.4, gy + 1.2, gz + 2, [0.18, 0.18, 0.22, 1.0], 8);
          mesh.addBox(gx - 2.2, gy - 6.0, gz - 4, gx + 2.2, gy + 0.5, gz + 4, colSkin, 8);

          // Front Sight & Rear Sights
          mesh.addBox(gx - 0.3, gy + 4.2, gz - 13.5, gx + 0.3, gy + 5.2, gz - 12.5, [1.0, 0.85, 0.0, 1.0], 9);
          mesh.addBox(gx - 1.2, gy + 4.2, gz - 1.5, gx - 0.5, gy + 5.0, gz - 0.5, [1.0, 0.85, 0.0, 1.0], 9);
          mesh.addBox(gx + 0.5, gy + 4.2, gz - 1.5, gx + 1.2, gy + 5.0, gz - 0.5, [1.0, 0.85, 0.0, 1.0], 9);

          // Muzzle Flash
          if (this.muzzleFlashTimer > 0) {
            mesh.addBox(gx - 3.5, gy + 1.0, gz - 18, gx + 3.5, gy + 6.0, gz - 14, colFlash, 9);
          }
        }
        // MICRO UZI
        else if (wep.name === 'MICRO UZI') {
          mesh.addBox(gx - 1.6, gy, gz - 16, gx + 1.6, gy + 4.5, gz + 2, colGunSteel, 8);
          // Long Magazine
          mesh.addBox(gx - 1.0, gy - 12, gz - 2, gx + 1.0, gy, gz + 1, [0.10, 0.10, 0.12, 1.0], 8);
          // Hands holding grip and front receiver
          mesh.addBox(gx - 2.2, gy - 5.5, gz - 3, gx + 2.2, gy + 0.8, gz + 3, colSkin, 8);

          if (this.muzzleFlashTimer > 0) {
            mesh.addBox(gx - 4.0, gy + 0.5, gz - 21, gx + 4.0, gy + 6.5, gz - 16, colFlash, 9);
          }
        }
        // SHOTGUN
        else if (wep.name === 'SHOTGUN') {
          // Long Steel Barrel & Mag Tube
          mesh.addBox(gx - 1.4, gy + 1.5, gz - 24, gx + 1.4, gy + 4.2, gz + 6, colGunSteel, 8);
          mesh.addBox(gx - 1.2, gy - 0.5, gz - 20, gx + 1.2, gy + 1.5, gz + 4, colGunSteel, 8);

          // Pump Slide (slides back during pump reload animation!)
          const pumpOffset = (this.shotgunPumpTimer > 0.15) ? 4.0 : 0.0;
          mesh.addBox(gx - 1.8, gy - 1.2, gz - 14 + pumpOffset, gx + 1.8, gy + 2.0, gz - 6 + pumpOffset, colWood, 8);

          // Wooden Stock
          mesh.addBox(gx - 1.5, gy - 4.5, gz + 6, gx + 1.5, gy + 2.0, gz + 16, colWood, 8);
          // Hands
          mesh.addBox(gx - 2.4, gy - 3.5, gz + 4, gx + 2.4, gy + 2.0, gz + 9, colSkin, 8);

          if (this.muzzleFlashTimer > 0) {
            mesh.addBox(gx - 6.5, gy - 1.5, gz - 32, gx + 6.5, gy + 8.5, gz - 24, colFlash, 9);
          }
        }
      }
    }
    """

def get_js_ai_and_entities():
    return r"""
    /* ==========================================================================
       10. PEDESTRIANS, POLICE AI, PROJECTILES & PICKUPS
       ========================================================================== */
    class Pedestrian {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.angle = Math.random() * Math.PI * 2;
        this.radius = 11;
        this.speed = 45 + Math.random() * 25;
        this.hp = 30;
        this.state = 'WANDER';
        this.fleeTimer = 0;
        this.walkCycle = Math.random() * 10;

        const shirts = [
          [1.0, 0.0, 0.5, 1.0], [0.0, 0.95, 1.0, 1.0], [1.0, 0.88, 0.0, 1.0],
          [0.74, 0.0, 1.0, 1.0], [0.95, 0.95, 0.95, 1.0], [1.0, 0.55, 0.0, 1.0]
        ];
        this.shirtColor = shirts[Math.floor(Math.random() * shirts.length)];
        this.hairColor = [[0.1, 0.1, 0.1, 1], [0.4, 0.25, 0.15, 1], [0.8, 0.6, 0.25, 1]][Math.floor(Math.random() * 3)];
      }

      takeDamage(amount, attacker) {
        if (this.state === 'DEAD') return;
        this.hp -= amount;
        if (this.hp <= 0) {
          this.state = 'DEAD';
          if (window.game && window.game.decals) window.game.decals.addBloodSplatter(this.x, this.y);
          if (window.game) {
            window.game.pickups.push(new Pickup(this.x, this.y, 'cash'));
            window.game.police.addHeat(35);
          }
        } else {
          this.panic(attacker.x, attacker.y);
        }
      }

      panic(fromX, fromY) {
        if (this.state === 'DEAD') return;
        this.state = 'FLEE';
        this.fleeTimer = 6.0;
        this.angle = Math.atan2(this.y - fromY, this.x - fromX);
      }

      update(dt) {
        if (this.state === 'DEAD') return;

        if (this.state === 'FLEE') {
          this.fleeTimer -= dt;
          if (this.fleeTimer <= 0) this.state = 'WANDER';
          const runSpeed = this.speed * 2.2;
          this.vx = Math.cos(this.angle) * runSpeed;
          this.vy = Math.sin(this.angle) * runSpeed;
          this.walkCycle += dt * 18;
        } else {
          if (Math.random() < 0.015) {
            this.angle += (Math.random() - 0.5) * 1.5;
          }
          this.vx = Math.cos(this.angle) * this.speed;
          this.vy = Math.sin(this.angle) * this.speed;
          this.walkCycle += dt * 8;
        }

        this.x += this.vx * dt;
        this.y += this.vy * dt;

        this.x = Math.max(30, Math.min(CONFIG.WORLD_WIDTH - 30, this.x));
        this.y = Math.max(30, Math.min(CONFIG.WORLD_HEIGHT - 30, this.y));
      }

      render3D(mesh) {
        if (this.state === 'DEAD') {
          // Dead body flat on ground
          mesh.addBox(this.x - 7, 0.2, this.y - 7, this.x + 7, 3.5, this.y + 7, this.shirtColor, 7);
          return;
        }

        const legSwing = Math.sin(this.walkCycle) * 4.5;
        const colSkin = [1.0, 0.72, 0.54, 1.0];
        const colPants = [0.18, 0.20, 0.28, 1.0];

        // 3D Animated Legs
        mesh.addBox(this.x - 3.5, 0, this.y - 2.5 + legSwing, this.x - 0.5, 10, this.y + 2.5 + legSwing, colPants, 7);
        mesh.addBox(this.x + 0.5, 0, this.y - 2.5 - legSwing, this.x + 3.5, 10, this.y + 2.5 - legSwing, colPants, 7);

        // 3D Torso
        mesh.addBox(this.x - 5, 10, this.y - 3.5, this.x + 5, 20, this.y + 3.5, this.shirtColor, 7);

        // 3D Head & Hair
        mesh.addBox(this.x - 3, 20, this.y - 3, this.x + 3, 26, this.y + 3, colSkin, 7);
        mesh.addBox(this.x - 3.2, 23.5, this.y - 3.2, this.x + 3.2, 27, this.y + 3.2, this.hairColor, 7);
      }
    }

    class TrafficDriver {
      constructor(vehicle, laneDirection, axis) {
        this.vehicle = vehicle;
        this.vehicle.driver = this;
        this.direction = laneDirection;
        this.axis = axis;
        this.targetSpeed = 160 + Math.random() * 80;
        this.honkCooldown = 0;
      }

      carjacked() {
        this.vehicle.driver = null;
        const ped = new Pedestrian(this.vehicle.x, this.vehicle.y);
        ped.panic(window.game.player.x, window.game.player.y);
        window.game.pedestrians.push(ped);
      }

      update(dt) {
        if (this.vehicle.wrecked || this.vehicle.driver !== this) return;

        if (this.honkCooldown > 0) this.honkCooldown -= dt;

        const fwd = this.vehicle.getForwardVector();
        const checkDist = 85;
        const frontX = this.vehicle.x + fwd.x * (this.vehicle.length * 0.5 + checkDist);
        const frontY = this.vehicle.y + fwd.y * (this.vehicle.length * 0.5 + checkDist);

        let obstacleDetected = false;

        for (const other of window.game.vehicles) {
          if (other === this.vehicle) continue;
          if (Math.hypot(other.x - frontX, other.y - frontY) < 55) {
            obstacleDetected = true;
            break;
          }
        }

        if (Math.hypot(window.game.player.x - frontX, window.game.player.y - frontY) < 50) {
          obstacleDetected = true;
          if (this.honkCooldown <= 0) {
            audio.playHorn();
            this.honkCooldown = 3.0;
          }
        }

        let throttle = 0;
        if (obstacleDetected) {
          throttle = -0.5;
        } else if (this.vehicle.speed < this.targetSpeed) {
          throttle = 0.8;
        }

        let targetAngle = 0;
        if (this.axis === 'x') {
          targetAngle = this.direction > 0 ? 0 : Math.PI;
        } else {
          targetAngle = this.direction > 0 ? Math.PI * 0.5 : -Math.PI * 0.5;
        }

        let diff = targetAngle - this.vehicle.angle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;

        const steer = Math.max(-1, Math.min(1, diff * 3));
        this.vehicle.updatePhysics(dt, throttle, steer, false);
      }
    }

    class PoliceOfficer {
      constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.angle = 0;
        this.radius = 12;
        this.hp = 60;
        this.speed = 175;
        this.fireCooldown = 0.5;
        this.alive = true;
        this.walkCycle = 0;
      }

      takeDamage(amount, attacker) {
        if (!this.alive) return;
        this.hp -= amount;
        if (this.hp <= 0) {
          this.alive = false;
          if (window.game && window.game.decals) window.game.decals.addBloodSplatter(this.x, this.y);
          if (window.game) {
            window.game.police.addHeat(80);
            window.game.pickups.push(new Pickup(this.x, this.y, 'smg'));
          }
        }
      }

      update(dt) {
        if (!this.alive) return;

        if (this.fireCooldown > 0) this.fireCooldown -= dt;

        const targetX = window.game.player.x;
        const targetY = window.game.player.y;
        const dist = Math.hypot(targetX - this.x, targetY - this.y);

        this.angle = Math.atan2(targetY - this.y, targetX - this.x);

        if (dist > 220) {
          this.vx = Math.cos(this.angle) * this.speed;
          this.vy = Math.sin(this.angle) * this.speed;
          this.walkCycle += dt * 14;
        } else {
          this.vx *= 0.8;
          this.vy *= 0.8;
          if (this.fireCooldown <= 0 && dist < 550) {
            this.fireCooldown = 0.45 + Math.random() * 0.3;
            audio.playShoot('pistol');
            const bx = this.x + Math.cos(this.angle) * 18;
            const by = this.y + Math.sin(this.angle) * 18;
            const bvx = Math.cos(this.angle + (Math.random() - 0.5) * 0.08) * 1400;
            const bvy = Math.sin(this.angle + (Math.random() - 0.5) * 0.08) * 1400;
            window.game.projectiles.push(new Projectile(bx, by, bvx, bvy, 15, 'cop', '#ff0055'));
          }
        }

        this.x += this.vx * dt;
        this.y += this.vy * dt;
      }

      render3D(mesh) {
        if (!this.alive) {
          mesh.addBox(this.x - 7, 0.2, this.y - 7, this.x + 7, 3.5, this.y + 7, [0.08, 0.14, 0.26, 1.0], 7);
          return;
        }

        const legSwing = Math.sin(this.walkCycle) * 4.5;
        const colUniform = [0.06, 0.14, 0.28, 1.0];
        const colBadge = [1.0, 0.85, 0.0, 1.0];
        const colSkin = [1.0, 0.72, 0.54, 1.0];

        // 3D Legs
        mesh.addBox(this.x - 3.5, 0, this.y - 2.5 + legSwing, this.x - 0.5, 10, this.y + 2.5 + legSwing, colUniform, 7);
        mesh.addBox(this.x + 0.5, 0, this.y - 2.5 - legSwing, this.x + 3.5, 10, this.y + 2.5 - legSwing, colUniform, 7);

        // 3D Torso with Gold Police Badge
        mesh.addBox(this.x - 5, 10, this.y - 3.5, this.x + 5, 20, this.y + 3.5, colUniform, 7);
        mesh.addBox(this.x + 1, 14, this.y + 3.6, this.x + 3.5, 17, this.y + 4.0, colBadge, 9);

        // 3D Head & Police Cap
        mesh.addBox(this.x - 3, 20, this.y - 3, this.x + 3, 26, this.y + 3, colSkin, 7);
        mesh.addBox(this.x - 3.8, 24.5, this.y - 3.8, this.x + 3.8, 27.5, this.y + 5.0, colUniform, 7);
      }
    }

    class PoliceManager {
      constructor() {
        this.heat = 0;
        this.wantedLevel = 0;
        this.evading = false;
        this.cooldownTimer = 16.0;
        this.maxCooldown = 16.0;
        this.cruisers = [];
        this.officers = [];
        this.spawnTimer = 2.0;
        this.flashTimer = 0;
      }

      addHeat(amount) {
        this.heat += amount;
        this.evading = false;
        this.cooldownTimer = this.maxCooldown;
        this.updateWantedLevel();
      }

      updateWantedLevel() {
        const prev = this.wantedLevel;
        if (this.heat >= 500) this.wantedLevel = 5;
        else if (this.heat >= 320) this.wantedLevel = 4;
        else if (this.heat >= 180) this.wantedLevel = 3;
        else if (this.heat >= 80) this.wantedLevel = 2;
        else if (this.heat >= 20) this.wantedLevel = 1;
        else this.wantedLevel = 0;

        if (this.wantedLevel > prev && window.game) {
          window.game.showFloatingNotification(`WANTED LEVEL ${this.wantedLevel}!`, '#ff007f');
          audio.playSirenTone(880);
        }
      }

      clearWanted() {
        this.heat = 0;
        this.wantedLevel = 0;
        this.evading = false;
        this.cruisers.forEach(c => { c.sirenActive = false; });
        if (window.game) window.game.showFloatingNotification('WANTED LEVEL CLEARED!', '#00ff66');
      }

      update(dt) {
        if (this.wantedLevel === 0) return;

        this.flashTimer += dt * 6;
        const hasSight = this.checkPoliceLineOfSight();

        if (!hasSight) {
          this.evading = true;
          this.cooldownTimer -= dt;
          if (this.cooldownTimer <= 0) {
            this.clearWanted();
            return;
          }
        } else {
          this.evading = false;
          this.cooldownTimer = this.maxCooldown;
        }

        this.spawnTimer -= dt;
        const targetCruisers = this.wantedLevel;
        const activeCruisers = this.cruisers.filter(c => !c.wrecked).length;

        if (this.spawnTimer <= 0 && activeCruisers < targetCruisers) {
          this.spawnPoliceCruiser();
          this.spawnTimer = 4.0;
        }

        for (const car of this.cruisers) {
          if (car.wrecked) continue;
          this.updateCruiserAI(car, dt);
        }

        for (let i = this.officers.length - 1; i >= 0; i--) {
          const off = this.officers[i];
          off.update(dt);
        }
      }

      checkPoliceLineOfSight() {
        const px = window.game.player.x;
        const py = window.game.player.y;

        for (const car of this.cruisers) {
          if (car.wrecked) continue;
          const dist = Math.hypot(car.x - px, car.y - py);
          if (dist < 680 && window.game.hasLineOfSight(car.x, car.y, px, py)) {
            return true;
          }
        }

        for (const off of this.officers) {
          if (!off.alive) continue;
          const dist = Math.hypot(off.x - px, off.y - py);
          if (dist < 580 && window.game.hasLineOfSight(off.x, off.y, px, py)) {
            return true;
          }
        }
        return false;
      }

      spawnPoliceCruiser() {
        const p = window.game.player;
        const angle = Math.random() * Math.PI * 2;
        const spawnDist = 800;
        let sx = p.x + Math.cos(angle) * spawnDist;
        let sy = p.y + Math.sin(angle) * spawnDist;

        const nearestRoadX = CONFIG.GRID_ROADS_X.reduce((prev, curr) => Math.abs(curr - sx) < Math.abs(prev - sx) ? curr : prev);
        const nearestRoadY = CONFIG.GRID_ROADS_Y.reduce((prev, curr) => Math.abs(curr - sy) < Math.abs(prev - sy) ? curr : prev);

        if (Math.abs(nearestRoadX - sx) < Math.abs(nearestRoadY - sy)) {
          sx = nearestRoadX;
        } else {
          sy = nearestRoadY;
        }

        sx = Math.max(100, Math.min(CONFIG.WORLD_WIDTH - 100, sx));
        sy = Math.max(100, Math.min(CONFIG.WORLD_HEIGHT - 100, sy));

        const cruiser = new Vehicle(sx, sy, Math.atan2(p.y - sy, p.x - sx), 'police');
        cruiser.sirenActive = true;
        this.cruisers.push(cruiser);
        window.game.vehicles.push(cruiser);
      }

      updateCruiserAI(car, dt) {
        const p = window.game.player;
        const dist = Math.hypot(p.x - car.x, p.y - car.y);

        if (!p.inVehicle && dist < 190 && car.speed < 90) {
          if (!car.officersDeployed) {
            car.officersDeployed = true;
            const off1 = new PoliceOfficer(car.x - 22, car.y);
            const off2 = new PoliceOfficer(car.x + 22, car.y);
            this.officers.push(off1, off2);
          }
        }

        const targetAngle = Math.atan2(p.y - car.y, p.x - car.x);
        let diff = targetAngle - car.angle;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;

        const steer = Math.max(-1, Math.min(1, diff * 2.5));
        let throttle = (p.inVehicle && dist < 120) ? 1.2 : 1.0;

        car.updatePhysics(dt, throttle, steer, false);
      }
    }

    class Projectile {
      constructor(x, y, vx, vy, damage, owner, color = '#ffe600') {
        this.x = x;
        this.y = y;
        this.z = 20.0;
        this.prevX = x;
        this.prevY = y;
        this.vx = vx;
        this.vy = vy;
        this.damage = damage;
        this.owner = owner;
        this.color = color;
        this.life = 1.2;
      }

      update(dt) {
        this.prevX = this.x;
        this.prevY = this.y;
        this.x += this.vx * dt;
        this.y += this.vy * dt;
        this.life -= dt;
        return this.life > 0;
      }

      render3D(mesh) {
        // 3D Glowing Tracer Beam
        const col = this.owner === 'player' ? [1.0, 0.9, 0.2, 1.0] : [1.0, 0.1, 0.3, 1.0];
        mesh.addBox(this.x - 1.2, this.z - 1.2, this.y - 1.2, this.prevX + 1.2, this.z + 1.2, this.prevY + 1.2, col, 9);
      }
    }

    class Particle {
      constructor(x, y, vx, vy, color, size, life, decay, type = 'normal') {
        this.x = x;
        this.y = y;
        this.z = 15.0;
        this.vx = vx;
        this.vy = vy;
        this.vz = (Math.random() - 0.2) * 20;
        this.color = color;
        this.size = size;
        this.life = life;
        this.maxLife = life;
        this.decay = decay;
        this.type = type;
      }

      update(dt) {
        this.x += this.vx * dt;
        this.y += this.vy * dt;
        this.z += this.vz * dt;
        if (this.z < 1.0) {
          this.z = 1.0;
          this.vz *= -0.5;
        }

        if (this.type === 'smoke') {
          this.size += 8 * dt;
          this.vx *= 0.95;
          this.vy *= 0.95;
          this.vz += 15 * dt; // Rises into air
        } else if (this.type === 'spark') {
          this.vx *= 0.92;
          this.vy *= 0.92;
          this.vz -= 60 * dt; // Falls with gravity
        }
        this.life -= this.decay * dt;
        return this.life > 0;
      }

      render3D(mesh) {
        const alpha = Math.max(0, this.life / this.maxLife);
        const s = this.size;
        let col = [1.0, 0.6, 0.1, alpha];
        if (this.type === 'smoke') col = [0.25, 0.25, 0.3, alpha * 0.7];
        mesh.addBox(this.x - s, this.z - s, this.y - s, this.x + s, this.z + s, this.y + s, col, 9);
      }
    }

    class Pickup {
      constructor(x, y, type, respawns = false) {
        this.x = x;
        this.y = y;
        this.origX = x;
        this.origY = y;
        this.type = type;
        this.val = type === 'cash' ? 100 : (type === 'health' || type === 'armor' ? 50 : 30);
        this.bob = Math.random() * Math.PI * 2;
        this.active = true;
        this.respawns = respawns;
        this.respawnTimer = 0;
      }

      update(dt) {
        if (!this.active) {
          if (this.respawns) {
            this.respawnTimer -= dt;
            if (this.respawnTimer <= 0) {
              this.active = true;
              this.x = this.origX;
              this.y = this.origY;
            }
          }
          return;
        }
        this.bob += 3.5 * dt;
      }

      render3D(mesh) {
        if (!this.active) return;
        const hoverY = 7.0 + Math.sin(this.bob) * 2.5;
        let col = [1.0, 0.88, 0.0, 1.0];
        if (this.type === 'health') col = [1.0, 0.0, 0.45, 1.0];
        else if (this.type === 'armor') col = [0.0, 0.95, 1.0, 1.0];
        else if (this.type === 'cash') col = [0.0, 1.0, 0.45, 1.0];

        // 3D Spinning Pickup Cube / Icon
        const s = 4.5;
        mesh.addBox(this.x - s, hoverY - s, this.y - s, this.x + s, hoverY + s, this.y + s, col, 9);
      }
    }

    class DecalManager {
      constructor(width, height) {
        this.canvas = document.createElement('canvas');
        this.canvas.width = width / 2;
        this.canvas.height = height / 2;
        this.ctx = this.canvas.getContext('2d');
        this.scale = 0.5;
        this.ctx.scale(this.scale, this.scale);
      }

      addTireSkid(x1, y1, x2, y2) {
        this.ctx.strokeStyle = 'rgba(10, 10, 16, 0.35)';
        this.ctx.lineWidth = 4.5;
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
      }

      addBloodSplatter(x, y) {
        this.ctx.fillStyle = 'rgba(160, 0, 30, 0.7)';
        this.ctx.beginPath();
        this.ctx.arc(x, y, 10 + Math.random() * 8, 0, Math.PI * 2);
        this.ctx.fill();
        for (let i = 0; i < 5; i++) {
          const sx = x + (Math.random() - 0.5) * 36;
          const sy = y + (Math.random() - 0.5) * 36;
          this.ctx.beginPath();
          this.ctx.arc(sx, sy, 2 + Math.random() * 4, 0, Math.PI * 2);
          this.ctx.fill();
        }
      }
    }

    class SpatialGrid {
      constructor(width, height, cellSize) {
        this.width = width;
        this.height = height;
        this.cellSize = cellSize;
        this.cols = Math.ceil(width / cellSize);
        this.rows = Math.ceil(height / cellSize);
        this.cells = Array.from({ length: this.cols * this.rows }, () => []);
      }

      insert(obj, box) {
        const minCol = Math.max(0, Math.floor(box.x / this.cellSize));
        const maxCol = Math.min(this.cols - 1, Math.floor((box.x + box.w) / this.cellSize));
        const minRow = Math.max(0, Math.floor(box.y / this.cellSize));
        const maxRow = Math.min(this.rows - 1, Math.floor((box.y + box.h) / this.cellSize));

        for (let r = minRow; r <= maxRow; r++) {
          for (let c = minCol; c <= maxCol; c++) {
            this.cells[r * this.cols + c].push(obj);
          }
        }
      }

      getNearby(x, y, radius) {
        const minCol = Math.max(0, Math.floor((x - radius) / this.cellSize));
        const maxCol = Math.min(this.cols - 1, Math.floor((x + radius) / this.cellSize));
        const minRow = Math.max(0, Math.floor((y - radius) / this.cellSize));
        const maxRow = Math.min(this.rows - 1, Math.floor((y + radius) / this.cellSize));

        const result = new Set();
        for (let r = minRow; r <= maxRow; r++) {
          for (let c = minCol; c <= maxCol; c++) {
            const list = this.cells[r * this.cols + c];
            for (let i = 0; i < list.length; i++) {
              result.add(list[i]);
            }
          }
        }
        return Array.from(result);
      }
    }
    """

