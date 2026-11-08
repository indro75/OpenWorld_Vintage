# js_world.py - Realistic 3D Procedural City World Builder

def get_js_world_builder():
    return r"""
    /* ==========================================================================
       7. PROCEDURAL 3D CITY WORLD & ARCHITECTURE BUILDER
       ========================================================================== */
    class CityWorld3D {
      constructor() {
        this.buildings = [];
        this.streetlamps = [];
        this.decorations = [];
        this.specialSpots = {};
        this.generateCityLayout();
      }

      generateCityLayout() {
        const roadsX = CONFIG.GRID_ROADS_X;
        const roadsY = CONFIG.GRID_ROADS_Y;
        const halfRoad = CONFIG.ROAD_WIDTH / 2;

        for (let row = 0; row < roadsY.length - 1; row++) {
          for (let col = 0; col < roadsX.length - 1; col++) {
            const bx = roadsX[col] + halfRoad;
            const by = roadsY[row] + halfRoad;
            const bw = (roadsX[col + 1] - halfRoad) - bx;
            const bh = (roadsY[row + 1] - halfRoad) - by;

            this.generateBlock(col, row, bx, by, bw, bh);
          }
        }

        // Ocean Beach Shoreline on East Edge
        this.decorations.push({
          type: 'beach',
          x: 3270,
          y: 0,
          w: CONFIG.WORLD_WIDTH - 3270,
          h: CONFIG.WORLD_HEIGHT
        });

        // 3D Palm trees along beach coastal boulevard & avenues
        for (let py = 80; py < CONFIG.WORLD_HEIGHT - 80; py += 130) {
          this.decorations.push({ type: 'palm', x: 3280, y: py, h: 42 + Math.random() * 12, rot: Math.random() * Math.PI * 2 });
          this.decorations.push({ type: 'palm', x: 3390, y: py + 65, h: 45 + Math.random() * 14, rot: Math.random() * Math.PI * 2 });
        }

        // Additional palm trees in city parks and boulevards
        [800, 1400, 2000, 2600].forEach(rx => {
          for (let ry = 300; ry < CONFIG.WORLD_HEIGHT - 300; ry += 350) {
            this.decorations.push({ type: 'palm', x: rx - halfRoad - 14, y: ry, h: 36 + Math.random() * 8, rot: Math.random() * Math.PI * 2 });
            this.decorations.push({ type: 'palm', x: rx + halfRoad + 14, y: ry + 150, h: 36 + Math.random() * 8, rot: Math.random() * Math.PI * 2 });
          }
        });

        // 3D Streetlamps along all road sidewalks
        roadsY.forEach(ry => {
          for (let x = 160; x < CONFIG.WORLD_WIDTH - 160; x += 190) {
            this.streetlamps.push({ x: x, y: ry - halfRoad - 8, height: 28, armAngle: Math.PI * 0.5 });
            this.streetlamps.push({ x: x, y: ry + halfRoad + 8, height: 28, armAngle: -Math.PI * 0.5 });
          }
        });
      }

      generateBlock(col, row, bx, by, bw, bh) {
        const padding = 16;
        const blockInnerX = bx + padding;
        const blockInnerY = by + padding;
        const blockInnerW = bw - padding * 2;
        const blockInnerH = bh - padding * 2;

        // Ammu-Nation (Block 0, 1)
        if (col === 0 && row === 1) {
          this.specialSpots.ammuNation = { x: blockInnerX + 80, y: blockInnerY + 80 };
          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: blockInnerW,
            h: blockInnerH * 0.75,
            height: 95,
            name: 'AMMU-NATION',
            color: [0.18, 0.18, 0.22, 1.0],
            neonColor: [1.0, 0.88, 0.0, 1.0],
            signText: 'AMMU-NATION',
            floors: 3
          });
          return;
        }

        // Pay 'N' Spray Garage (Block 1, 2)
        if (col === 1 && row === 2) {
          this.specialSpots.payNSpray = { x: blockInnerX + blockInnerW * 0.5, y: blockInnerY + blockInnerH * 0.5 };
          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: blockInnerW,
            h: blockInnerH,
            height: 75,
            name: 'PAY N SPRAY',
            color: [0.15, 0.17, 0.20, 1.0],
            neonColor: [0.0, 1.0, 0.45, 1.0],
            signText: "PAY 'N' SPRAY",
            isPayNSpray: true,
            floors: 2
          });
          return;
        }

        // Vice City Police HQ (Block 2, 1)
        if (col === 2 && row === 1) {
          this.specialSpots.policeHQ = { x: blockInnerX + blockInnerW * 0.5, y: blockInnerY + blockInnerH * 0.5 };
          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: blockInnerW * 0.8,
            h: blockInnerH,
            height: 180,
            name: 'VCPD HQ',
            color: [0.12, 0.16, 0.26, 1.0],
            neonColor: [0.0, 0.85, 1.0, 1.0],
            signText: 'VCPD HEADQUARTERS',
            floors: 7
          });
          return;
        }

        // Vice General Hospital (Block 3, 1)
        if (col === 3 && row === 1) {
          this.specialSpots.hospital = { x: blockInnerX + blockInnerW * 0.5, y: blockInnerY + blockInnerH * 0.5 };
          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: blockInnerW,
            h: blockInnerH * 0.75,
            height: 160,
            name: 'VICE HOSPITAL',
            color: [0.26, 0.24, 0.26, 1.0],
            neonColor: [1.0, 0.0, 0.45, 1.0],
            signText: 'VICE GENERAL HOSPITAL',
            floors: 6
          });
          return;
        }

        // The Malibu Club (Block 1, 0)
        if (col === 1 && row === 0) {
          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: blockInnerW,
            h: blockInnerH,
            height: 110,
            name: 'THE MALIBU',
            color: [0.24, 0.14, 0.28, 1.0],
            neonColor: [1.0, 0.0, 0.55, 1.0],
            signText: 'THE MALIBU CLUB',
            floors: 4
          });
          return;
        }

        // Standard City High-Rises & Commercial Blocks
        const splitH = (col + row) % 2 === 0;
        const neonColors = [
          [0.0, 0.95, 1.0, 1.0],  // Cyan
          [1.0, 0.0, 0.55, 1.0],  // Hot Pink
          [0.75, 0.0, 1.0, 1.0],  // Purple
          [1.0, 0.88, 0.0, 1.0]   // Gold
        ];
        const signNames = [
          'VICE CASINO', 'OCEAN VIEW', 'RETRO ARCADE', 'NEON LOUNGE',
          'CYBER SUITES', 'VICE MOTEL', 'DISCO 86', 'PALM HOTEL', 'HAVANA CLUB'
        ];

        // Skyscraper height generation (taller towards center and beach)
        const distFromCenter = Math.hypot(col - 2.5, row - 2.5);
        const baseHeight = 120 + (5 - distFromCenter) * 35 + Math.random() * 60;

        if (splitH) {
          const midW = (blockInnerW - 22) / 2;
          const h1 = baseHeight * (0.8 + Math.random() * 0.5);
          const h2 = baseHeight * (0.8 + Math.random() * 0.5);

          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: midW,
            h: blockInnerH,
            height: Math.min(320, h1),
            color: [0.15, 0.15, 0.22, 1.0],
            neonColor: neonColors[(col + row) % neonColors.length],
            signText: signNames[(col * 3 + row) % signNames.length],
            floors: Math.floor(h1 / 25)
          });

          this.buildings.push({
            x: blockInnerX + midW + 22,
            y: blockInnerY,
            w: midW,
            h: blockInnerH,
            height: Math.min(320, h2),
            color: [0.18, 0.18, 0.26, 1.0],
            neonColor: neonColors[(col + row + 1) % neonColors.length],
            signText: signNames[(col * 3 + row + 1) % signNames.length],
            floors: Math.floor(h2 / 25)
          });
        } else {
          const midH = (blockInnerH - 22) / 2;
          const h1 = baseHeight * (0.8 + Math.random() * 0.5);
          const h2 = baseHeight * (0.8 + Math.random() * 0.5);

          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY,
            w: blockInnerW,
            h: midH,
            height: Math.min(320, h1),
            color: [0.16, 0.16, 0.24, 1.0],
            neonColor: neonColors[(col + row) % neonColors.length],
            signText: signNames[(col * 3 + row) % signNames.length],
            floors: Math.floor(h1 / 25)
          });

          this.buildings.push({
            x: blockInnerX,
            y: blockInnerY + midH + 22,
            w: blockInnerW,
            h: midH,
            height: Math.min(320, h2),
            color: [0.14, 0.14, 0.20, 1.0],
            neonColor: neonColors[(col + row + 2) % neonColors.length],
            signText: signNames[(col * 3 + row + 2) % signNames.length],
            floors: Math.floor(h2 / 25)
          });
        }
      }

      buildStaticMesh(mesh) {
        mesh.clear();

        const roadsX = CONFIG.GRID_ROADS_X;
        const roadsY = CONFIG.GRID_ROADS_Y;
        const rw = CONFIG.ROAD_WIDTH;
        const sw = CONFIG.SIDEWALK_WIDTH;
        const halfRoad = rw / 2;

        // 1. Sidewalk Base Plane & Curbs
        // Concrete Sidewalk Color: [0.55, 0.57, 0.60, 1.0] (MatType 1)
        const colSidewalk = [0.56, 0.58, 0.62, 1.0];
        const colCurb = [0.42, 0.44, 0.48, 1.0];

        roadsY.forEach(ry => {
          mesh.addBox(0, 0.0, ry - halfRoad - sw, CONFIG.WORLD_WIDTH, 1.2, ry + halfRoad + sw, colSidewalk, 1);
        });
        roadsX.forEach(rx => {
          mesh.addBox(rx - halfRoad - sw, 0.0, 0, rx + halfRoad + sw, 1.2, CONFIG.WORLD_HEIGHT, colSidewalk, 1);
        });

        // 2. Asphalt Roadways
        // Asphalt Color: [0.12, 0.13, 0.16, 1.0] (MatType 0)
        const colAsphalt = [0.11, 0.12, 0.15, 1.0];
        roadsY.forEach(ry => {
          mesh.addBox(0, 0.0, ry - halfRoad, CONFIG.WORLD_WIDTH, 0.25, ry + halfRoad, colAsphalt, 0);
        });
        roadsX.forEach(rx => {
          mesh.addBox(rx - halfRoad, 0.0, 0, rx + halfRoad, 0.25, CONFIG.WORLD_HEIGHT, colAsphalt, 0);
        });

        // 3. Double Yellow Center Lines & White Lane Dividers
        const colYellowLine = [1.0, 0.82, 0.0, 1.0];
        const colWhiteLine = [0.94, 0.94, 0.96, 1.0];

        roadsY.forEach(ry => {
          // Double yellow center divider
          mesh.addBox(0, 0.28, ry - 1.2, CONFIG.WORLD_WIDTH, 0.32, ry - 0.4, colYellowLine, 9);
          mesh.addBox(0, 0.28, ry + 0.4, CONFIG.WORLD_WIDTH, 0.32, ry + 1.2, colYellowLine, 9);

          // Outer white edge lines
          mesh.addBox(0, 0.28, ry - halfRoad + 4, CONFIG.WORLD_WIDTH, 0.32, ry - halfRoad + 5.2, colWhiteLine, 9);
          mesh.addBox(0, 0.28, ry + halfRoad - 5.2, CONFIG.WORLD_WIDTH, 0.32, ry + halfRoad - 4, colWhiteLine, 9);

          // Dashed lane lines
          for (let x = 0; x < CONFIG.WORLD_WIDTH; x += 32) {
            mesh.addBox(x, 0.28, ry - halfRoad / 2 - 0.4, x + 16, 0.32, ry - halfRoad / 2 + 0.4, colWhiteLine, 9);
            mesh.addBox(x, 0.28, ry + halfRoad / 2 - 0.4, x + 16, 0.32, ry + halfRoad / 2 + 0.4, colWhiteLine, 9);
          }
        });

        roadsX.forEach(rx => {
          // Double yellow center divider
          mesh.addBox(rx - 1.2, 0.28, 0, rx - 0.4, 0.32, CONFIG.WORLD_HEIGHT, colYellowLine, 9);
          mesh.addBox(rx + 0.4, 0.28, 0, rx + 1.2, 0.32, CONFIG.WORLD_HEIGHT, colYellowLine, 9);

          // Outer white edge lines
          mesh.addBox(rx - halfRoad + 4, 0.28, 0, rx - halfRoad + 5.2, 0.32, CONFIG.WORLD_HEIGHT, colWhiteLine, 9);
          mesh.addBox(rx + halfRoad - 5.2, 0.28, 0, rx + halfRoad - 4, 0.32, CONFIG.WORLD_HEIGHT, colWhiteLine, 9);

          // Dashed lane lines
          for (let y = 0; y < CONFIG.WORLD_HEIGHT; y += 32) {
            mesh.addBox(rx - halfRoad / 2 - 0.4, 0.28, y, rx - halfRoad / 2 + 0.4, 0.32, y + 16, colWhiteLine, 9);
            mesh.addBox(rx + halfRoad / 2 - 0.4, 0.28, y, rx + halfRoad / 2 + 0.4, 0.32, y + 16, colWhiteLine, 9);
          }
        });

        // 4. Pedestrian Crosswalks at Intersections
        roadsY.forEach(ry => {
          roadsX.forEach(rx => {
            const hw = halfRoad;
            // North & South zebra stripes
            for (let i = -hw + 10; i < hw - 10; i += 18) {
              mesh.addBox(rx + i, 0.28, ry - hw - sw + 3, rx + i + 10, 0.32, ry - hw - 3, colWhiteLine, 9);
              mesh.addBox(rx + i, 0.28, ry + hw + 3, rx + i + 10, 0.32, ry + hw + sw - 3, colWhiteLine, 9);
            }
            // West & East zebra stripes
            for (let i = -hw + 10; i < hw - 10; i += 18) {
              mesh.addBox(rx - hw - sw + 3, 0.28, ry + i, rx - hw - 3, 0.32, ry + i + 10, colWhiteLine, 9);
              mesh.addBox(rx + hw + 3, 0.28, ry + i, rx + hw + sw - 3, 0.32, ry + i + 10, colWhiteLine, 9);
            }
          });
        });

        // 5. Beach Sand Slope
        const colSand = [0.86, 0.72, 0.50, 1.0];
        mesh.addQuad(
          [3270, 1.2, 0], [3450, -0.6, 0], [3450, -0.6, CONFIG.WORLD_HEIGHT], [3270, 1.2, CONFIG.WORLD_HEIGHT],
          [-0.1, 0.99, 0], colSand, 0
        );

        // 6. Vast Ocean Water Grid
        const colOcean = [0.0, 0.55, 0.72, 0.95];
        const oceanStart = 3430;
        const oceanEnd = 4300;
        const step = 80;
        for (let x = oceanStart; x < oceanEnd; x += step) {
          for (let z = 0; z < CONFIG.WORLD_HEIGHT; z += step) {
            mesh.addQuad(
              [x, 0.0, z], [x + step, 0.0, z], [x + step, 0.0, z + step], [x, 0.0, z + step],
              [0, 1, 0], colOcean, 4
            );
          }
        }

        // 7. 3D Buildings & Landmarks
        this.buildings.forEach(b => {
          const colBase = b.color;
          const h = b.height;

          // Main Building Extruded Body (MatType 2: Procedural Glass Window Facade)
          mesh.addBox(b.x, 0, b.y, b.x + b.w, h, b.y + b.h, colBase, 2, 0.05, 0.05);

          // Roof Parapet Lip (MatType 3: Dark concrete/metal)
          const lipH = 3.5;
          const lipT = 2.0;
          mesh.addBox(b.x, h, b.y, b.x + b.w, h + lipH, b.y + lipT, [0.12, 0.12, 0.16, 1.0], 3);
          mesh.addBox(b.x, h, b.y + b.h - lipT, b.x + b.w, h + lipH, b.y + b.h, [0.12, 0.12, 0.16, 1.0], 3);
          mesh.addBox(b.x, h, b.y, b.x + lipT, h + lipH, b.y + b.h, [0.12, 0.12, 0.16, 1.0], 3);
          mesh.addBox(b.x + b.w - lipT, h, b.y, b.x + b.w, h + lipH, b.y + b.h, [0.12, 0.12, 0.16, 1.0], 3);

          // Roof Units (AC Compressors, Water Tanks, Antennas)
          mesh.addBox(b.x + 18, h, b.y + 18, b.x + 42, h + 9, b.y + 38, [0.22, 0.24, 0.28, 1.0], 3);
          mesh.addBox(b.x + b.w - 48, h, b.y + 24, b.x + b.w - 20, h + 12, b.y + 52, [0.18, 0.20, 0.24, 1.0], 3);

          // Water Tank on Wooden Legs for mid-rises
          if (h > 100 && h < 200) {
            const tx = b.x + b.w * 0.5;
            const ty = b.y + b.h * 0.5;
            mesh.addCylinder(tx, h + 10, ty, 8, 14, 8, [0.45, 0.35, 0.25, 1.0], 3);
          }

          // Radio Antenna Mast with Blinking Beacon
          if (h >= 170) {
            const ax = b.x + b.w * 0.5;
            const ay = b.y + b.h * 0.5;
            mesh.addCylinder(ax, h + 20, ay, 0.8, 38, 4, [0.75, 0.78, 0.82, 1.0], 3);
            // Red Beacon Bulb
            mesh.addBox(ax - 1.2, h + 38, ay - 1.2, ax + 1.2, h + 41, ay + 1.2, [1.0, 0.1, 0.1, 1.0], 9);
          }

          // Glowing Neon Cornice / Sign Band
          const nc = b.neonColor;
          mesh.addBox(b.x - 0.5, h - 3, b.y - 0.5, b.x + b.w + 0.5, h, b.y + b.h + 0.5, nc, 9);

          // Ground-Level Entrance Storefront / Garage
          if (b.isPayNSpray) {
            // Bright green garage roll-up door
            mesh.addBox(b.x + b.w * 0.2, 0, b.y - 1.0, b.x + b.w * 0.8, 22, b.y + 2, [0.0, 0.85, 0.35, 1.0], 9);
          } else if (b.name === 'AMMU-NATION') {
            mesh.addBox(b.x + b.w * 0.3, 0, b.y - 1.0, b.x + b.w * 0.7, 24, b.y + 2, [1.0, 0.85, 0.0, 1.0], 9);
          } else if (b.name === 'VICE HOSPITAL') {
            // Red Cross on facade
            const cx = b.x + b.w * 0.5;
            mesh.addBox(cx - 14, h * 0.65 - 4, b.y - 1.2, cx + 14, h * 0.65 + 4, b.y + 1, [1.0, 0.0, 0.2, 1.0], 9);
            mesh.addBox(cx - 4, h * 0.65 - 14, b.y - 1.2, cx + 4, h * 0.65 + 14, b.y + 1, [1.0, 0.0, 0.2, 1.0], 9);
          }
        });

        // 8. 3D Palm Trees
        for (const dec of this.decorations) {
          if (dec.type === 'palm') {
            this.buildPalmTree(mesh, dec.x, dec.y, dec.h, dec.rot);
          }
        }

        // 9. 3D Streetlamps
        for (const lamp of this.streetlamps) {
          this.buildStreetlamp(mesh, lamp.x, lamp.y, lamp.height, lamp.armAngle);
        }
      }

      buildPalmTree(mesh, x, z, trunkHeight, rot) {
        const colBark = [0.42, 0.28, 0.16, 1.0];
        const colLeaf = [0.08, 0.68, 0.32, 1.0];
        const segs = 6;
        let cx = x, cy = 0, cz = z;
        const segH = trunkHeight / segs;

        // Curved segmented trunk
        for (let i = 0; i < segs; i++) {
          const r = 2.2 - (i / segs) * 0.9;
          const curveX = Math.sin(rot) * (i * 1.8);
          mesh.addCylinder(cx + curveX, cy + segH / 2, cz, r, segH, 6, colBark, 5);
          cy += segH;
        }

        // Crown of 14 Drooping 3D Palm Fronds
        const crownX = cx + Math.sin(rot) * (segs * 1.8);
        const crownY = cy;
        const frondCount = 14;
        const frondLen = 22;

        for (let i = 0; i < frondCount; i++) {
          const ang = (i / frondCount) * Math.PI * 2;
          const fx = Math.cos(ang);
          const fz = Math.sin(ang);
          const tipX = crownX + fx * frondLen;
          const tipY = crownY - 6.5;
          const tipZ = cz + fz * frondLen;

          const rightX = -fz * 2.8;
          const rightZ = fx * 2.8;

          // Frond Quad
          mesh.addQuad(
            [crownX - rightX * 0.3, crownY, cz - rightZ * 0.3],
            [crownX + rightX * 0.3, crownY, cz + rightZ * 0.3],
            [tipX + rightX, tipY, tipZ + rightZ],
            [tipX - rightX, tipY, tipZ - rightZ],
            [0, 1, 0], colLeaf, 5
          );
        }
      }

      buildStreetlamp(mesh, x, z, h, armAngle) {
        const colPole = [0.65, 0.68, 0.72, 1.0];
        const colLight = [0.0, 0.95, 1.0, 1.0];

        // Vertical pole
        mesh.addCylinder(x, h / 2, z, 0.6, h, 5, colPole, 3);

        // Curved Arm
        const armX = Math.cos(armAngle) * 9;
        const armZ = Math.sin(armAngle) * 9;
        mesh.addBox(x, h - 1.0, z - 0.5, x + armX, h + 0.5, z + armZ + 0.5, colPole, 3);

        // Glowing Lamp Head Fixture
        mesh.addBox(x + armX - 1.5, h - 2.5, z + armZ - 1.5, x + armX + 1.5, h, z + armZ + 1.5, colLight, 9);
      }
    }
    """

