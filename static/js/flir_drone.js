/**
 * FLIR Synthetic Thermal Drone Camera Simulator
 * Provides White-Hot IR rendering, target box tracking, laser rangefinder,
 * and EW jamming noise / sensor distortion.
 */

class FLIRDroneSimulator {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    this.noiseOffset = 0;
    this.trackingUnit = null;
    this.jammingLevel = 0.0;

    this.resize();
    window.addEventListener("resize", () => this.resize());
    this.animate();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  updateState(units, jammingLevel = 0.0) {
    this.jammingLevel = jammingLevel;
    // Track primary OPFOR target or leading unit
    this.trackingUnit = Object.values(units).find(u => u.allegiance === "RED" && u.is_active) || null;
  }

  animate() {
    this.noiseOffset += 1;
    this.render();
    requestAnimationFrame(() => this.animate());
  }

  render() {
    if (!this.ctx || !this.canvas) return;
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // Thermal Black-Hot Light Background
    ctx.fillStyle = "#f4f4f5";
    ctx.fillRect(0, 0, w, h);

    // FLIR Ground Contours (Subtle gray lines)
    ctx.strokeStyle = "#d4d4d8";
    ctx.lineWidth = 1;
    for (let i = 0; i < 6; i++) {
      ctx.beginPath();
      const y = (h * 0.2) + i * 25 + Math.sin(this.noiseOffset * 0.02 + i) * 6;
      ctx.moveTo(0, y);
      ctx.bezierCurveTo(w * 0.3, y - 10, w * 0.7, y + 15, w, y - 5);
      ctx.stroke();
    }

    // Thermal Target Heat Signature
    const targetX = w / 2;
    const targetY = h / 2;

    if (this.trackingUnit) {
      // Black-Hot heat bloom (dark heat signature)
      const grad = ctx.createRadialGradient(targetX, targetY, 0, targetX, targetY, 35);
      grad.addColorStop(0, "rgba(0, 0, 0, 0.8)");
      grad.addColorStop(0.3, "rgba(24, 24, 27, 0.6)");
      grad.addColorStop(0.7, "rgba(39, 39, 42, 0.2)");
      grad.addColorStop(1, "rgba(255, 255, 255, 0)");

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(targetX, targetY, 35, 0, Math.PI * 2);
      ctx.fill();

      // Vehicle silhouette (Hot target = solid dark)
      ctx.fillStyle = "#000000";
      ctx.fillRect(targetX - 16, targetY - 10, 32, 20);
      ctx.fillRect(targetX - 22, targetY - 3, 10, 6); // Barrel

      // Target Tracking Box
      ctx.strokeStyle = "#000000";
      ctx.lineWidth = 2;
      ctx.strokeRect(targetX - 24, targetY - 20, 48, 40);

      // Target Metadata
      ctx.fillStyle = "#000000";
      ctx.font = "bold 9px monospace";
      ctx.fillText(`TRK: ${this.trackingUnit.callsign}`, targetX - 24, targetY - 24);
      ctx.fillText("LRF: 2,410m", targetX - 24, targetY + 32);
    } else {
      ctx.fillStyle = "#52525b";
      ctx.font = "bold 10px monospace";
      ctx.fillText("SEARCHING SECTOR // NO HOT SIGNATURE", w / 2 - 100, h / 2);
    }

    // EW Jamming Noise & Sensor Snow
    if (this.jammingLevel > 0.1) {
      const numLines = Math.floor(this.jammingLevel * 20);
      ctx.fillStyle = "rgba(0, 0, 0, 0.25)";
      for (let i = 0; i < numLines; i++) {
        const ry = Math.random() * h;
        const rh = Math.random() * 4 + 1;
        ctx.fillRect(0, ry, w, rh);
      }

      if (this.jammingLevel > 0.6) {
        ctx.fillStyle = "rgba(185, 28, 28, 0.9)";
        ctx.font = "bold 12px monospace";
        ctx.fillText("UAV DATA-LINK CRITICAL NOISE", 12, h - 20);
      }
    }
  }
}

window.FLIRDroneSimulator = FLIRDroneSimulator;
