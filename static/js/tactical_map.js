/**
 * Tactical Map Canvas Engine
 * High-performance 2D vector map renderer with MGRS grid, NATO MIL-STD symbology,
 * EW jamming wave visualization, stale position uncertainty circles, and order plotting.
 */

class TacticalMap {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    
    // Viewport transform
    this.panX = 50;
    this.panY = 50;
    this.zoom = 1.0;
    this.isDragging = false;
    this.dragStartX = 0;
    this.dragStartY = 0;

    // Tactical State
    this.units = {};
    this.jammers = [];
    this.ghostContacts = [];
    this.selectedUnitId = null;
    this.hoveredUnitId = null;
    this.currentRole = "COMMANDER";
    this.isGroundTruth = false;

    // Jammer dragging (Instructor)
    this.draggedJammerId = null;

    // Sweep animation
    this.sweepAngle = 0;

    this.onOrderRequested = null; // Callback when user targets a point
    this.onJammerMoved = null;

    this.initEvents();
    this.resize();
    window.addEventListener("resize", () => this.resize());
    this.animate();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  initEvents() {
    this.canvas.addEventListener("mousedown", (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const screenX = e.clientX - rect.left;
      const screenY = e.clientY - rect.top;
      const worldPos = this.screenToWorld(screenX, screenY);

      if (e.button === 0) { // Left click
        // Check if instructor is dragging a jammer
        if (this.currentRole === "INSTRUCTOR") {
          for (const jammer of this.jammers) {
            const d = Math.hypot(jammer.position.x - worldPos.x, jammer.position.y - worldPos.y);
            if (d < 30) {
              this.draggedJammerId = jammer.id;
              return;
            }
          }
        }

        // Check if clicking a unit
        let clickedUnitId = null;
        for (const [uid, u] of Object.entries(this.units)) {
          const d = Math.hypot(u.position.x - worldPos.x, u.position.y - worldPos.y);
          if (d < 25) {
            clickedUnitId = uid;
            break;
          }
        }

        if (clickedUnitId) {
          this.selectedUnitId = clickedUnitId;
          if (window.tacticalAudio) window.tacticalAudio.playAlertPing();
        } else if (this.selectedUnitId && this.currentRole !== "INSTRUCTOR") {
          // Clicked empty ground while unit selected -> Request Order!
          if (this.onOrderRequested) {
            this.onOrderRequested(this.selectedUnitId, worldPos);
          }
        } else {
          // Pan map
          this.isDragging = true;
          this.dragStartX = screenX - this.panX;
          this.dragStartY = screenY - this.panY;
        }
      } else if (e.button === 2) { // Right click to pan
        this.isDragging = true;
        this.dragStartX = screenX - this.panX;
        this.dragStartY = screenY - this.panY;
      }
    });

    this.canvas.addEventListener("mousemove", (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const screenX = e.clientX - rect.left;
      const screenY = e.clientY - rect.top;
      const worldPos = this.screenToWorld(screenX, screenY);

      if (this.draggedJammerId) {
        if (this.onJammerMoved) {
          this.onJammerMoved(this.draggedJammerId, worldPos.x, worldPos.y);
        }
        return;
      }

      if (this.isDragging) {
        this.panX = screenX - this.dragStartX;
        this.panY = screenY - this.dragStartY;
      }

      // Update HUD MGRS
      const mgrsEl = document.getElementById("hudMGRS");
      if (mgrsEl) {
        const easting = Math.max(0, Math.min(9999, Math.floor(worldPos.x * 10)));
        const northing = Math.max(0, Math.min(9999, Math.floor(worldPos.y * 10)));
        mgrsEl.textContent = `38T KM ${easting.toString().padStart(4, "0")} ${northing.toString().padStart(4, "0")}`;
      }
    });

    this.canvas.addEventListener("mouseup", () => {
      this.isDragging = false;
      this.draggedJammerId = null;
    });

    this.canvas.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.zoom = Math.max(0.4, Math.min(3.5, this.zoom * zoomFactor));
    });

    this.canvas.addEventListener("contextmenu", (e) => e.preventDefault());
  }

  worldToScreen(wx, wy) {
    return {
      x: this.panX + wx * this.zoom,
      y: this.panY + wy * this.zoom
    };
  }

  screenToWorld(sx, sy) {
    return {
      x: (sx - this.panX) / this.zoom,
      y: (sy - this.panY) / this.zoom
    };
  }

  updateState(stateData) {
    this.units = stateData.units || {};
    this.jammers = stateData.active_jammers || [];
    this.ghostContacts = stateData.ghost_contacts || [];
    this.currentRole = stateData.role;
    this.isGroundTruth = stateData.is_ground_truth;
  }

  animate() {
    this.sweepAngle = (this.sweepAngle + 0.02) % (Math.PI * 2);
    this.render();
    requestAnimationFrame(() => this.animate());
  }

  render() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // Clear background to clean white paper-map style
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, w, h);

    // Draw Terrain / Topo Features
    this.drawTerrain(ctx);

    // Draw MGRS Grid
    this.drawMGRSGrid(ctx, w, h);

    // Draw EW Jamming Fields (Visible to Instructor & EW Specialist)
    if (this.currentRole === "INSTRUCTOR" || this.currentRole === "EW_CYBER") {
      this.drawJammingFields(ctx);
    }

    // Draw Order Routing Lines
    this.drawOrderRoutes(ctx);

    // Draw Units
    for (const [uid, unit] of Object.entries(this.units)) {
      this.drawTacticalUnit(ctx, unit, uid === this.selectedUnitId);
    }

    // Draw Radar Sweep Line (Tactical effect)
    this.drawRadarSweep(ctx);
  }

  drawTerrain(ctx) {
    // Stylized tactical topographic contour lines & elevation defiles
    ctx.save();
    ctx.strokeStyle = "rgba(0, 0, 0, 0.14)";
    ctx.lineWidth = 1;

    const contours = [
      [{x: 100, y: 100}, {x: 400, y: 150}, {x: 700, y: 300}, {x: 900, y: 250}],
      [{x: 150, y: 700}, {x: 350, y: 550}, {x: 650, y: 600}, {x: 850, y: 800}],
      [{x: 450, y: 250}, {x: 520, y: 480}, {x: 600, y: 650}] // Mountain Pass Defile
    ];

    for (const pts of contours) {
      ctx.beginPath();
      const p0 = this.worldToScreen(pts[0].x, pts[0].y);
      ctx.moveTo(p0.x, p0.y);
      for (let i = 1; i < pts.length; i++) {
        const pt = this.worldToScreen(pts[i].x, pts[i].y);
        ctx.lineTo(pt.x, pt.y);
      }
      ctx.stroke();
    }

    // Main Valley Road / Avenue of Approach
    ctx.strokeStyle = "rgba(0, 0, 0, 0.4)";
    ctx.setLineDash([8 * this.zoom, 6 * this.zoom]);
    ctx.beginPath();
    const r1 = this.worldToScreen(150, 220);
    const r2 = this.worldToScreen(450, 380);
    const r3 = this.worldToScreen(750, 430);
    ctx.moveTo(r1.x, r1.y);
    ctx.lineTo(r2.x, r2.y);
    ctx.lineTo(r3.x, r3.y);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.restore();
  }

  drawMGRSGrid(ctx, w, h) {
    ctx.save();
    ctx.strokeStyle = "rgba(0, 0, 0, 0.08)";
    ctx.lineWidth = 1;
    ctx.font = `bold ${Math.max(9, 10 * this.zoom)}px monospace`;
    ctx.fillStyle = "rgba(0, 0, 0, 0.65)";

    const gridSize = 100 * this.zoom;
    const startX = this.panX % gridSize;
    const startY = this.panY % gridSize;

    for (let x = startX; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();

      const worldCoord = Math.floor(this.screenToWorld(x, 0).x);
      if (worldCoord >= 0 && worldCoord <= 1000) {
        ctx.fillText(`${worldCoord}E`, x + 4, 14);
      }
    }

    for (let y = startY; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      const worldCoord = Math.floor(this.screenToWorld(0, y).y);
      if (worldCoord >= 0 && worldCoord <= 1000) {
        ctx.fillText(`${worldCoord}N`, 4, y - 4);
      }
    }

    ctx.restore();
  }

  drawJammingFields(ctx) {
    ctx.save();
    for (const jammer of this.jammers) {
      if (!jammer.active && this.currentRole !== "INSTRUCTOR") continue;

      const sp = this.worldToScreen(jammer.position.x, jammer.position.y);
      const sRadius = jammer.radius * this.zoom;

      // Color based on band & spoofing
      let baseColor = "rgba(168, 85, 247, "; // Purple for VHF
      if (jammer.spoofing) {
        baseColor = "rgba(245, 158, 11, "; // Amber for GPS spoofing
      }

      // Fill transparent radial bubble
      const grad = ctx.createRadialGradient(sp.x, sp.y, 0, sp.x, sp.y, sRadius);
      grad.addColorStop(0, baseColor + (jammer.active ? "0.28)" : "0.05)"));
      grad.addColorStop(0.8, baseColor + (jammer.active ? "0.12)" : "0.02)"));
      grad.addColorStop(1, baseColor + "0)");

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, sRadius, 0, Math.PI * 2);
      ctx.fill();

      // Pulsating outer border
      ctx.strokeStyle = baseColor + (jammer.active ? "0.8)" : "0.3)");
      ctx.lineWidth = jammer.active ? 2 : 1;
      ctx.setLineDash(jammer.active ? [6, 4] : [2, 4]);
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, sRadius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);

      // Emitter Center Icon
      ctx.fillStyle = jammer.active ? "#a855f7" : "#64748b";
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, 6 * this.zoom, 0, Math.PI * 2);
      ctx.fill();

      // Label
      ctx.fillStyle = jammer.spoofing ? "#fde68a" : "#e9d5ff";
      ctx.font = "10px monospace";
      ctx.fillText(`EW: ${jammer.name} [${jammer.active ? "ACTIVE" : "OFF"}]`, sp.x + 10, sp.y + 4);
    }
    ctx.restore();
  }

  drawOrderRoutes(ctx) {
    ctx.save();
    for (const [uid, unit] of Object.entries(this.units)) {
      if (unit.metadata && unit.metadata.target_destination) {
        const p1 = this.worldToScreen(unit.position.x, unit.position.y);
        const p2 = this.worldToScreen(unit.metadata.target_destination.x, unit.metadata.target_destination.y);

        ctx.strokeStyle = "rgba(56, 189, 248, 0.7)";
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();

        // Target waypoint crosshair
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.arc(p2.x, p2.y, 5, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
    ctx.restore();
  }

  drawTacticalUnit(ctx, unit, isSelected) {
    const sp = this.worldToScreen(unit.position.x, unit.position.y);
    const size = 18 * this.zoom;
    const isBlue = unit.allegiance === "BLUE";
    const isRed = unit.allegiance === "RED";
    const isStale = unit.metadata && unit.metadata.stale;
    const isGpsSpoofed = unit.metadata && unit.metadata.gps_spoofed;

    ctx.save();

    // If unit position is STALE due to comms disruption, draw expanding uncertainty radius
    if (isStale) {
      const staleSec = unit.metadata.stale_seconds || 10;
      const uncertaintyRadius = Math.min(80, staleSec * 2.5) * this.zoom;

      ctx.strokeStyle = "rgba(245, 158, 11, 0.4)";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, uncertaintyRadius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = "#f59e0b";
      ctx.font = "9px monospace";
      ctx.fillText(`UNCERTAINTY: +${staleSec}s`, sp.x - 30, sp.y - size - 8);
    }

    // Selection ring
    if (isSelected) {
      ctx.strokeStyle = "#000000";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, size * 1.5, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Heading Velocity Vector
    if (unit.speed > 0.5) {
      const rad = (unit.heading * Math.PI) / 180;
      const vx = Math.cos(rad) * (size * 1.6);
      const vy = Math.sin(rad) * (size * 1.6);

      ctx.strokeStyle = isBlue ? "#1e40af" : "#b91c1c";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(sp.x, sp.y);
      ctx.lineTo(sp.x + vx, sp.y + vy);
      ctx.stroke();
    }

    // MIL-STD Symbol Base
    if (isBlue) {
      // Blue Friendly: Rectangle
      ctx.fillStyle = isStale ? "rgba(30, 58, 138, 0.5)" : "#1e40af";
      ctx.strokeStyle = isGpsSpoofed ? "#b45309" : "#000000";
      ctx.lineWidth = 2;
      if (isGpsSpoofed) ctx.setLineDash([4, 2]);

      ctx.fillRect(sp.x - size / 2, sp.y - size / 2, size, size);
      ctx.strokeRect(sp.x - size / 2, sp.y - size / 2, size, size);
      ctx.setLineDash([]);

      // Tactical internal glyph
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      if (unit.unit_type === "ARMOR") {
        // Armor oval
        ctx.beginPath();
        ctx.ellipse(sp.x, sp.y, size * 0.35, size * 0.22, 0, 0, Math.PI * 2);
        ctx.stroke();
      } else if (unit.unit_type === "HQ") {
        // HQ flag
        ctx.beginPath();
        ctx.moveTo(sp.x - size * 0.25, sp.y + size * 0.3);
        ctx.lineTo(sp.x - size * 0.25, sp.y - size * 0.3);
        ctx.lineTo(sp.x + size * 0.25, sp.y - size * 0.1);
        ctx.stroke();
      } else if (unit.unit_type === "UAV") {
        // Delta UAV
        ctx.beginPath();
        ctx.moveTo(sp.x, sp.y - size * 0.35);
        ctx.lineTo(sp.x + size * 0.3, sp.y + size * 0.3);
        ctx.lineTo(sp.x, sp.y + size * 0.15);
        ctx.lineTo(sp.x - size * 0.3, sp.y + size * 0.3);
        ctx.closePath();
        ctx.stroke();
      } else {
        // Infantry 'X'
        ctx.beginPath();
        ctx.moveTo(sp.x - size * 0.3, sp.y - size * 0.3);
        ctx.lineTo(sp.x + size * 0.3, sp.y + size * 0.3);
        ctx.moveTo(sp.x + size * 0.3, sp.y - size * 0.3);
        ctx.lineTo(sp.x - size * 0.3, sp.y + size * 0.3);
        ctx.stroke();
      }
    } else if (isRed) {
      // Red Hostile: Diamond
      ctx.fillStyle = unit.spoofed ? "rgba(185, 28, 28, 0.4)" : "#b91c1c";
      ctx.strokeStyle = unit.spoofed ? "#b45309" : "#000000";
      ctx.lineWidth = 2;
      if (unit.spoofed) ctx.setLineDash([3, 2]);

      ctx.beginPath();
      ctx.moveTo(sp.x, sp.y - size * 0.7);
      ctx.lineTo(sp.x + size * 0.7, sp.y);
      ctx.lineTo(sp.x, sp.y + size * 0.7);
      ctx.lineTo(sp.x - size * 0.7, sp.y);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Callsign & Status Label (Crisp Black / Dark Red on White Map)
    ctx.fillStyle = isBlue ? "#000000" : "#991b1b";
    ctx.font = "bold 11px monospace";
    ctx.fillText(unit.callsign, sp.x + size * 0.8, sp.y + 4);

    // Health / Engagement bar
    if (unit.health < 100) {
      ctx.fillStyle = "#e4e4e7";
      ctx.fillRect(sp.x - size / 2, sp.y + size * 0.7, size, 3);
      ctx.fillStyle = unit.health > 40 ? "#15803d" : "#b91c1c";
      ctx.fillRect(sp.x - size / 2, sp.y + size * 0.7, (size * unit.health) / 100, 3);
    }

    ctx.restore();
  }

  drawRadarSweep(ctx) {
    // Stylized radar sweep arm centered on UAV or map center
    ctx.save();
    const uav = Object.values(this.units).find(u => u.unit_type === "UAV");
    const center = uav ? this.worldToScreen(uav.position.x, uav.position.y) : { x: 200, y: 200 };
    const radius = 180 * this.zoom;

    const grad = ctx.createConicGradient(this.sweepAngle, center.x, center.y);
    grad.addColorStop(0, "rgba(0, 0, 0, 0.08)");
    grad.addColorStop(0.1, "rgba(0, 0, 0, 0.0)");
    grad.addColorStop(1, "rgba(0, 0, 0, 0.0)");

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(center.x, center.y, radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }
}

window.TacticalMap = TacticalMap;
