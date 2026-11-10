# VICE CITY '86 - First-Person Open World 3D

A 3D open-world action game built with WebGL and Web Audio API, featuring First-Person Perspective (FPP) gameplay, realistic city rendering, procedural audio, driving physics, vehicle cockpits, weapons, and police pursuit AI.

## Features

- **First-Person Perspective (FPP):**
  - Full FPS mouse look with pointer lock and pitch/yaw controls.
  - On-foot movement (WASD) with realistic head bobbing, jumping (<kbd>Spacebar</kbd>), and sprinting (<kbd>Shift</kbd>).
  - Aim Down Sights (ADS) on right-click with FOV zoom.
  - 3D First-Person Weapon Rig:
    - Fists (alternate punching animation with impact effects)
    - Pistol (slide blowback, muzzle flash, spent brass ejection, recoil recovery)
    - Micro Uzi (rapid automatic fire, muzzle spark storm, brass spray)
    - Shotgun (pump slide rack animation with mechanical sound and shell ejection)
  - First-Person Vehicle Cockpit with turning 3D steering wheel, dashboard speed and RPM gauges, windshield, hood, and dual headlight projection beams.
  - Seamless camera toggle between FPP and Top-Down view with <kbd>V</kbd>.

- **Realistic 3D Open World:**
  - Procedural multi-story buildings and skyscrapers with architectural setbacks.
  - Realistic facade window grids with randomized lit office rooms and reflective tinted glass.
  - Rooftops with parapet edges, AC condenser units, water tanks, and radio antennas with blinking red aviation beacons.
  - Iconic landmarks: Ammu-Nation, Pay 'N' Spray, VCPD Headquarters, Vice General Hospital, The Malibu Club, Vice Casino.
  - Asphalt roadways with aggregate grain, double yellow center lines, white lane dashes, zebra crosswalks, concrete sidewalks, and curbs.
  - 3D ocean water with multi-harmonic animated wave displacement, Fresnel reflections, and shoreline foam.
  - 3D curved palm trees with segmented trunks and drooping fronds.
  - Streetlamps with luminaire fixtures emitting pools of light.

- **Vehicles & Police AI:**
  - 6 vehicle types: Sports Car, Muscle Car, Sedan, Taxi, Police Cruiser, Ambulance/Van.
  - 4 rotating wheels, drift grip physics, tire skid decals on asphalt, damage smoke, engine fires, and explosions.
  - Police cruisers with sirens and flashing red/blue emergency strobes.
  - 1 to 5 Wanted Stars with dynamic cruiser spawning, officer pursuit, and line-of-sight evasion cooldown.

- **Procedural Synthwave Audio:**
  - Web Audio API synthwave music sequencer with dynamic basslines, leads, and drums.
  - Procedural sound effects: gunshots, explosions, engine revs, tire squeals, crashes, sirens, horns, cash chimes, and hit markers.

## Controls

| Action | Key / Input |
|---|---|
| **Move & Strafe** | <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> |
| **Look / Aim** | **Mouse** (Click screen to lock mouse, <kbd>Esc</kbd> to unlock) |
| **Attack / Fire** | **Left Click** |
| **Aim Down Sights (ADS)** | **Right Click** (Hold) |
| **Sprint** | <kbd>Shift</kbd> |
| **Jump** | <kbd>Spacebar</kbd> |
| **Switch Weapons** | <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> <kbd>4</kbd> / **Scroll Wheel** / <kbd>Q</kbd> <kbd>E</kbd> |
| **Enter / Jack Vehicle** | <kbd>F</kbd> or <kbd>Enter</kbd> |
| **Toggle Camera View** | <kbd>V</kbd> (FPP / Top-Down) |
| **Vehicle Handbrake (Drift)** | <kbd>Spacebar</kbd> |
| **Vehicle Horn** | <kbd>H</kbd> |
| **Toggle Music** | <kbd>M</kbd> |
| **Toggle SFX** | <kbd>N</kbd> |
| **Game Manual** | <kbd>P</kbd> |


