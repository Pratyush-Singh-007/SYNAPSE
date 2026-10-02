/**
 * Tactical RF Spectrum Analyzer
 * Visualizes radio frequency spectrum (VHF, UHF, GPS), active EW jamming power spikes,
 * and Electronic Counter-Countermeasures (ECCM frequency hopping).
 */

class SpectrumAnalyzer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    this.bands = [
      { name: "VHF (30-88 MHz)", freq: 45, power: 0.15, jammed: false },
      { name: "UHF/BFT (225-400 MHz)", freq: 310, power: 0.2, jammed: false },
      { name: "GPS L1 (1575.42 MHz)", freq: 1575, power: 0.1, jammed: false },
      { name: "SATCOM (7.2 GHz)", freq: 7200, power: 0.05, jammed: false }
    ];
    this.frequencyHoppingActive = false;
    this.timeOffset = 0;

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

  updateState(jammers = []) {
    // Check if jammers are active
    const vhfJam = jammers.find(j => j.active && j.frequency_band === "VHF");
    const gpsJam = jammers.find(j => j.active && j.frequency_band === "GPS");

    this.bands[0].jammed = !!vhfJam;
    this.bands[0].power = vhfJam ? vhfJam.power : 0.15;

    this.bands[2].jammed = !!gpsJam;
    this.bands[2].power = gpsJam ? gpsJam.power : 0.1;
  }

  toggleFrequencyHopping() {
    this.frequencyHoppingActive = !this.frequencyHoppingActive;
    return this.frequencyHoppingActive;
  }

  animate() {
    this.timeOffset += 0.05;
    this.render();
    requestAnimationFrame(() => this.animate());
  }

  render() {
    if (!this.ctx || !this.canvas) return;
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // Clean white analyzer background
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, w, h);

    // Spectrum grid lines
    ctx.strokeStyle = "rgba(0, 0, 0, 0.08)";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Spectrum RF Curve
    ctx.beginPath();
    ctx.strokeStyle = this.frequencyHoppingActive ? "#15803d" : "#000000";
    ctx.lineWidth = 2;

    const baselineY = h * 0.75;
    ctx.moveTo(0, baselineY);

    for (let x = 0; x < w; x += 3) {
      const normX = x / w;
      let amp = Math.sin(x * 0.05 + this.timeOffset) * 4 + (Math.random() * 3);

      // Check spike near band locations
      for (const band of this.bands) {
        const bandCenter = band.freq < 100 ? 0.2 : band.freq < 500 ? 0.5 : 0.8;
        const dist = Math.abs(normX - bandCenter);
        if (dist < 0.08) {
          const jamMult = band.jammed ? (band.power * 90) : 12;
          amp += Math.exp(-dist * 40) * jamMult;
        }
      }

      ctx.lineTo(x, baselineY - amp);
    }
    ctx.stroke();

    // Band Headers & Status
    ctx.font = "bold 9px monospace";
    for (let i = 0; i < this.bands.length; i++) {
      const b = this.bands[i];
      const bx = 12 + i * (w / 4);
      ctx.fillStyle = b.jammed ? "#b91c1c" : "#000000";
      ctx.fillText(b.name, bx, 18);
      ctx.fillStyle = b.jammed ? "#b91c1c" : "#15803d";
      ctx.fillText(b.jammed ? "SIGNAL SUPPRESSED" : "CLEAR LINK", bx, 30);
    }

    // ECCM Status Banner
    ctx.font = "bold 10px monospace";
    ctx.fillStyle = this.frequencyHoppingActive ? "#15803d" : "#52525b";
    ctx.fillText(
      `ECCM: ${this.frequencyHoppingActive ? "FHSS ACTIVE (HOPPING 1200 h/s)" : "STANDARD CARRIER"}`,
      12,
      h - 10
    );
  }
}

window.SpectrumAnalyzer = SpectrumAnalyzer;
