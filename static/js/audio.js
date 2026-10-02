/**
 * Tactical Procedural Audio Engine
 * Uses the Web Audio API to procedurally synthesize military radio squelches,
 * background RF noise, bandpass radio frequency filters, and EW jamming static.
 */

class TacticalAudioEngine {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.noiseNode = null;
    this.noiseGain = null;
    this.isMuted = false;
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();

      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.3, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);

      this.initialized = true;
      console.log("[AUDIO] Tactical Audio Engine initialized.");
    } catch (e) {
      console.warn("[AUDIO] Web Audio API failed to initialize:", e);
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.masterGain) {
      this.masterGain.gain.setValueAtTime(this.isMuted ? 0.0 : 0.3, this.ctx.currentTime);
    }
    return this.isMuted;
  }

  /**
   * Generates a realistic VHF radio squelch burst (push-to-talk onset/tail).
   */
  playRadioSquelch(isEnd = false) {
    if (!this.initialized || this.isMuted) return;
    if (this.ctx.state === "suspended") this.ctx.resume();

    const t = this.ctx.currentTime;
    const dur = isEnd ? 0.08 : 0.04;

    // Buffer for white noise burst
    const bufferSize = this.ctx.sampleRate * dur;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.4));
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    // Bandpass filter for radio resonance
    const filter = this.ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(isEnd ? 1800 : 2600, t);
    filter.Q.setValueAtTime(3.0, t);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(isEnd ? 0.25 : 0.4, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + dur);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    noise.start(t);
  }

  /**
   * Tactical high-priority alert ping (for enemy contacts / incoming orders).
   */
  playAlertPing(isWarning = false) {
    if (!this.initialized || this.isMuted) return;
    if (this.ctx.state === "suspended") this.ctx.resume();

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sine";
    const freq = isWarning ? 880 : 1200;
    osc.frequency.setValueAtTime(freq, t);
    osc.frequency.exponentialRampToValueAtTime(freq * 0.75, t + 0.12);

    gain.gain.setValueAtTime(0.2, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(t);
    osc.stop(t + 0.15);
  }

  /**
   * Simulates active Electronic Warfare RF jamming static hiss.
   * @param {number} interferenceLevel 0.0 to 1.0
   */
  playJammingCrackle(interferenceLevel = 0.5) {
    if (!this.initialized || this.isMuted || interferenceLevel <= 0.05) return;
    if (this.ctx.state === "suspended") this.ctx.resume();

    const t = this.ctx.currentTime;
    const dur = 0.25;
    const bufferSize = this.ctx.sampleRate * dur;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < bufferSize; i++) {
      // Noise with pulsed crackle
      const crackle = Math.random() < 0.15 ? (Math.random() * 2 - 1) : 0;
      data[i] = ((Math.random() * 2 - 1) * 0.4 + crackle * 0.6);
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = "highpass";
    filter.frequency.setValueAtTime(1200 + (interferenceLevel * 2000), t);

    const gain = this.ctx.createGain();
    const vol = Math.min(0.3, interferenceLevel * 0.35);
    gain.gain.setValueAtTime(vol, t);
    gain.gain.linearRampToValueAtTime(0.001, t + dur);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    noise.start(t);
  }
}

window.tacticalAudio = new TacticalAudioEngine();
