# build_game.py - Generates the complete FPP 3D Open World Game

import os
import sys

from js_engine import get_js_config_and_audio, get_js_input_handler, get_js_math_and_mesh, get_js_webgl_renderer
from js_world import get_js_world_builder
from js_entities import get_js_vehicle_and_cockpit, get_js_player_and_viewmodel, get_js_ai_and_entities
from js_main import get_js_game_engine_and_hud

def main():
    print("Generating complete Vice City '86 First-Person Perspective 3D Open World...")
    
    html = build_full_html()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    size = os.path.getsize("index.html")
    print(f"Generated index.html successfully ({size} bytes).")

def build_full_html():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>VICE CITY '86 - First-Person Open World 3D</title>
  <style>
{get_css()}
  </style>
</head>
<body>

{get_html_elements()}

  <!-- GAME ENGINE SCRIPT -->
  <script>
  (function() {{
    'use strict';

{get_js_config_and_audio()}
{get_js_input_handler()}
{get_js_math_and_mesh()}
{get_js_webgl_renderer()}
{get_js_world_builder()}
{get_js_vehicle_and_cockpit()}
{get_js_player_and_viewmodel()}
{get_js_ai_and_entities()}
{get_js_game_engine_and_hud()}

  }})();
  </script>
</body>
</html>"""

def get_css():
    return """
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
    }
    html, body {
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #080811;
      font-family: 'Segoe UI', Impact, Arial, sans-serif;
      color: #fff;
    }
    #canvasContainer {
      position: relative;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }
    #gameCanvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: block;
      cursor: crosshair;
    }
    #hudCanvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 15;
    }
    /* Retro CRT Scanlines & Vignette */
    .crt-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      background: linear-gradient(rgba(18, 16, 38, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
                  radial-gradient(circle at center, transparent 65%, rgba(0, 0, 0, 0.6) 100%);
      background-size: 100% 4px, 100% 100%;
      z-index: 20;
      opacity: 0.65;
      transition: opacity 0.3s ease;
    }
    .crt-overlay.disabled {
      opacity: 0;
    }

    /* Top Left Retro Title Badge */
    .title-badge {
      position: absolute;
      top: 16px;
      left: 18px;
      z-index: 25;
      pointer-events: none;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .title-badge h1 {
      font-size: 24px;
      font-weight: 900;
      font-style: italic;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: #fff;
      text-shadow: 0 0 10px #ff007f, 0 0 20px #ff007f, 2px 2px 0px #00f3ff;
    }
    .title-badge .subtitle {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      color: #00f3ff;
      text-shadow: 0 0 8px #00f3ff;
      text-transform: uppercase;
    }

    /* Top Center Control Bar */
    .top-controls {
      position: absolute;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 25;
      display: flex;
      gap: 8px;
    }
    .btn-retro {
      background: rgba(15, 15, 28, 0.88);
      border: 1px solid #00f3ff;
      color: #00f3ff;
      padding: 6px 14px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      cursor: pointer;
      border-radius: 4px;
      box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
      transition: all 0.2s ease;
    }
    .btn-retro:hover {
      background: #00f3ff;
      color: #0c0c16;
      box-shadow: 0 0 15px #00f3ff;
    }
    .btn-retro.active-pink {
      border-color: #ff007f;
      color: #ff007f;
      box-shadow: 0 0 8px rgba(255, 0, 127, 0.4);
    }
    .btn-retro.active-pink:hover {
      background: #ff007f;
      color: #fff;
      box-shadow: 0 0 16px #ff007f;
    }

    /* Crosshair Center Reticle for FPP */
    .fpp-crosshair {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: 22;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.05s ease-out;
    }
    .ch-dot {
      width: 4px;
      height: 4px;
      background: #00f3ff;
      border-radius: 50%;
      box-shadow: 0 0 6px #00f3ff;
    }
    .ch-bar {
      position: absolute;
      background: rgba(0, 243, 255, 0.85);
      box-shadow: 0 0 4px #00f3ff;
    }
    .ch-top { width: 2px; height: 9px; top: -14px; }
    .ch-bottom { width: 2px; height: 9px; bottom: -14px; }
    .ch-left { height: 2px; width: 9px; left: -14px; }
    .ch-right { height: 2px; width: 9px; right: -14px; }

    /* Hit Marker Animation */
    .hit-marker {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 26px;
      height: 26px;
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: 23;
      opacity: 0;
      transition: opacity 0.1s ease-out;
    }
    .hit-marker.active {
      opacity: 1;
    }
    .hm-line {
      position: absolute;
      background: #ff0055;
      box-shadow: 0 0 6px #ff0055;
    }
    .hm-tl { width: 7px; height: 2px; top: 2px; left: 2px; transform: rotate(45deg); }
    .hm-tr { width: 7px; height: 2px; top: 2px; right: 2px; transform: rotate(-45deg); }
    .hm-bl { width: 7px; height: 2px; bottom: 2px; left: 2px; transform: rotate(-45deg); }
    .hm-br { width: 7px; height: 2px; bottom: 2px; right: 2px; transform: rotate(45deg); }

    /* Pointer Lock Prompt */
    #pointerPrompt {
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(17, 17, 34, 0.94);
      border: 1px solid #ffe600;
      color: #ffe600;
      padding: 9px 22px;
      font-size: 12px;
      font-weight: bold;
      letter-spacing: 1px;
      border-radius: 20px;
      z-index: 30;
      box-shadow: 0 0 18px rgba(255, 230, 0, 0.4);
      pointer-events: none;
      transition: opacity 0.3s ease;
      animation: pulsePrompt 1.8s infinite alternate;
    }
    @keyframes pulsePrompt {
      from { opacity: 0.8; transform: translateX(-50%) scale(0.98); }
      to { opacity: 1; transform: translateX(-50%) scale(1.02); }
    }

    /* Modal Instructions Overlay */
    .modal-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(8, 8, 16, 0.88);
      backdrop-filter: blur(5px);
      z-index: 50;
      display: none;
      align-items: center;
      justify-content: center;
    }
    .modal-overlay.open {
      display: flex;
    }
    .modal-card {
      background: #111124;
      border: 2px solid #ff007f;
      border-radius: 8px;
      width: 92%;
      max-width: 620px;
      padding: 24px;
      box-shadow: 0 0 35px rgba(255, 0, 127, 0.4), inset 0 0 15px rgba(0, 243, 255, 0.2);
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      border-bottom: 1px solid rgba(255, 0, 127, 0.3);
      padding-bottom: 10px;
    }
    .modal-header h2 {
      font-size: 22px;
      font-style: italic;
      color: #fff;
      text-shadow: 0 0 10px #ff007f;
    }
    .modal-body {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      font-size: 13px;
      line-height: 1.6;
    }
    .control-group h3 {
      font-size: 13px;
      color: #00f3ff;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
      text-shadow: 0 0 6px #00f3ff;
    }
    .control-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
    }
    .control-row span.key {
      background: #1c1c38;
      border: 1px solid #ff007f;
      color: #ff007f;
      padding: 1px 6px;
      border-radius: 3px;
      font-weight: bold;
      font-family: monospace;
    }
    .modal-footer {
      margin-top: 20px;
      text-align: center;
    }
"""

def get_html_elements():
    return """
  <!-- Fullscreen Game Canvas Container -->
  <div id="canvasContainer">
    <!-- WebGL 3D World Canvas -->
    <canvas id="gameCanvas"></canvas>
    
    <!-- 2D Overlay HUD & Radar Canvas -->
    <canvas id="hudCanvas"></canvas>

    <!-- FPP Center Crosshair -->
    <div id="crosshair" class="fpp-crosshair">
      <div class="ch-dot"></div>
      <div class="ch-bar ch-top"></div>
      <div class="ch-bar ch-bottom"></div>
      <div class="ch-bar ch-left"></div>
      <div class="ch-bar ch-right"></div>
      <div id="hitMarker" class="hit-marker">
        <div class="hm-line hm-tl"></div>
        <div class="hm-line hm-tr"></div>
        <div class="hm-line hm-bl"></div>
        <div class="hm-line hm-br"></div>
      </div>
    </div>
  </div>

  <!-- CRT Scanline Effect -->
  <div id="crtOverlay" class="crt-overlay"></div>

  <!-- Retro Title Badge -->
  <div class="title-badge">
    <h1>VICE CITY '86</h1>
    <div class="subtitle">FIRST-PERSON OPEN WORLD 3D</div>
  </div>

  <!-- Top Retro Control Bar -->
  <div class="top-controls">
    <button id="btnView" class="btn-retro active-pink">👁️ VIEW: FPP [V]</button>
    <button id="btnMusic" class="btn-retro">🎵 MUSIC: ON</button>
    <button id="btnSfx" class="btn-retro">🔊 SFX: ON</button>
    <button id="btnCrt" class="btn-retro">📺 CRT: ON</button>
    <button id="btnHelp" class="btn-retro active-pink">❓ CONTROLS [P]</button>
  </div>

  <!-- Pointer Lock / Audio Prompt Message -->
  <div id="pointerPrompt">CLICK GAME TO LOCK FIRST-PERSON MOUSE AIM [ESC TO UNLOCK]</div>

  <!-- Controls / Help Modal -->
  <div id="helpModal" class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <h2>VICE CITY - FPP OPERATIONAL MANUAL</h2>
        <button id="btnCloseModal" class="btn-retro active-pink" style="padding:4px 8px;">✕</button>
      </div>
      <div class="modal-body">
        <div class="control-group">
          <h3>First-Person On-Foot</h3>
          <div class="control-row"><span>Move & Strafe:</span> <span class="key">W A S D</span></div>
          <div class="control-row"><span>Look / Aim:</span> <span class="key">Mouse (Click to Lock)</span></div>
          <div class="control-row"><span>Attack / Shoot:</span> <span class="key">Left Click</span></div>
          <div class="control-row"><span>Aim Down Sights:</span> <span class="key">Right Click (Hold)</span></div>
          <div class="control-row"><span>Sprint:</span> <span class="key">Shift</span></div>
          <div class="control-row"><span>Jump:</span> <span class="key">Spacebar</span></div>
          <div class="control-row"><span>Weapons:</span> <span class="key">1 2 3 4 / Scroll / Q E</span></div>
          <div class="control-row"><span>Enter / Jack Car:</span> <span class="key">F or Enter</span></div>
        </div>
        <div class="control-group">
          <h3>Cockpit Driving & Views</h3>
          <div class="control-row"><span>Gas / Reverse:</span> <span class="key">W / S</span></div>
          <div class="control-row"><span>Steer Wheel:</span> <span class="key">A / D</span></div>
          <div class="control-row"><span>Handbrake (Drift):</span> <span class="key">Spacebar</span></div>
          <div class="control-row"><span>Honk Horn:</span> <span class="key">H</span></div>
          <div class="control-row"><span>Exit Vehicle:</span> <span class="key">F or Enter</span></div>
          <div class="control-row"><span>Toggle Camera:</span> <span class="key">V (FPP / Top-Down)</span></div>
          <div class="control-row"><span>Audio Toggles:</span> <span class="key">M (Music) / N (SFX)</span></div>
        </div>
        <div class="control-group" style="grid-column: span 2; margin-top: 4px;">
          <h3>Realistic World Landmarks</h3>
          <div style="color: #bbb; font-size: 12px; line-height: 1.5;">
            • <b>Pay 'N' Spray Garage (Green Wrench [W] on radar):</b> Drive inside to repair damage, respray neon paint, and immediately wipe Wanted Level!<br>
            • <b>Ammu-Nation (Yellow Crosshair [+] on radar):</b> Collect weapons, Micro Uzi, Shotgun shells, and body armor.<br>
            • <b>Vice Hospital ([H] on radar) & Police HQ ([P] on radar):</b> Health packs and parked cruisers.<br>
            • <b>Wanted Cooldown:</b> Break police line-of-sight behind 3D buildings; stars flash and cooldown ticks to zero!
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button id="btnStartGame" class="btn-retro active-pink" style="font-size:14px; padding:8px 24px;">BACK TO THE STREETS</button>
      </div>
    </div>
  </div>
"""

if __name__ == "__main__":
    main()
