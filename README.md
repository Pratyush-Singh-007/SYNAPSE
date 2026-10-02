# SYNAPSE: Immersive Multi-Domain Decision-Making Trainer
### For Degraded & Contested Communication Environments (DMUU)

A web-based Command & Control (C2) simulation system designed to train junior and mid-level commanders in **Decision-Making Under Uncertainty (DMUU)** when Electronic Warfare (EW), GPS spoofing, and cyber disruptions degrade or sever communications.

---

## 🌟 The Core Problem Solved

Standard military simulation exercises (TEWTs, CPXs) largely assume continuous, crystal-clear situational awareness: Blue Force Trackers (BFT) update with sub-second latency, voice nets never drop, and radar feeds are uncorrupted. 

In contested peer/near-peer conflicts:
- **Electronic Warfare (EW)** creates localized or broad RF denial bubbles, severing voice nets (VHF) and digital data links (UHF).
- **GPS Spoofing** falsifies satellite timing ephemeris, causing blue force coordinates to drift into enemy kill zones or ambushes.
- **Cyber Disruption** freezes Common Operational Picture (COP) terminals, injects false telemetry, or disables remote drone video downlinks.
- **Contradictory Intel** pits thermal drone camera sightings against garbled ground scout radio SITREPs.

This trainer places small-team leaders (Company Commander, Platoon Leaders, JTAC, EW Officers) into these high-friction conditions, forcing them to exercise disciplined initiative and the doctrine of Mission Command.

---

## 🏗️ System Architecture & 4 Core Pillars

```
                                  ┌───────────────────────────────┐
                                  │      EXCON / INSTRUCTOR       │
                                  │  • Ground Truth God-Mode View │
                                  │  • Dynamic Injects & Jamming  │
                                  └──────────────┬────────────────┘
                                                 │
                                                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        SIMULATION SERVER & WORLD STATE ENGINE                          │
│          • Multi-domain physics loop (Land, Air, Cyber, EW)                            │
│          • Ground Truth unit coordinates, headings, health, and combat engagements     │
└────────────────────────────────────────────────┬───────────────────────────────────────┘
                                                 │
                                                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               DEGRADATION PIPELINE                                     │
│     [Synthetic Latency]  ──►  [Stochastic Dropout]  ──►  [Spoofing & Corruption]       │
└────────────┬───────────────────────────┬────────────────────────────┬──────────────────┘
             │ Perceived Stream A        │ Perceived Stream B         │ Perceived Stream C
             ▼                           ▼                            ▼
  ┌───────────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐
  │   COMPANY COMMANDER   │   │   PLATOON LEADER (1st) │   │   JTAC / AIR LIAISON   │
  │ • Stale BFT lag       │   │ • Local sight only     │   │ • Thermal UAV feed     │
  │ • Strategic COP       │   │ • Radio cutoff risk    │   │ • Jamming snow/glitch  │
  └───────────────────────┘   └────────────────────────┘   └────────────────────────┘
```

### 1. Scenario & Degradation Engine
- **Ground Truth vs Perceived Truth**: Server maintains absolute physical ground truth; each trainee receives a mathematically degraded projection customized to their physical location, line of sight, and active jammer proximity.
- **Latency & Stale Markers**: Positions lag; units with comms drop display expanding circular uncertainty radii (`+35s UNCERTAINTY`).
- **GPS Deception**: Spoofed emitters distort apparent coordinates by calculated offset vectors.
- **Digital Comms Corruption**: Radio text packets suffer parity degradation, dropping words or substituting characters with noise glyphs (`***`).

### 2. Multi-Role Team Coordination
- **Company Commander**: Oversees high-level Common Operational Picture (COP), coordinates assets, and issues high-level orders.
- **1st Platoon Leader (Mech Alpha)** & **2nd Platoon Leader (Inf Bravo)**: Direct forward elements; highly vulnerable to line-of-sight cutoff.
- **JTAC / Air Liaison**: Controls the Sentinel-1 UAV FLIR thermal camera feed (white-hot mode, laser rangefinder, targeting crosshairs, video jamming degradation).
- **EW & Cyber Specialist**: Operates the real-time RF Spectrum Analyzer (30 MHz - 7.2 GHz), identifies enemy emitter signatures, and activates frequency hopping (FHSS).
- **Procedural Tactical Audio**: Synthesizes realistic VHF radio squelch bursts, bandpass filter resonance (300Hz - 3.2kHz), and RF jamming crackle using the Web Audio API.

### 3. Instructor (EXCON / White Cell) Dashboard
- **Ground Truth God-View**: Overlay showing actual unit positions alongside ghost markers of where trainees perceive them to be.
- **Dynamic EW Drag & Drop**: Click and reposition active jamming bubbles in real time on the canvas.
- **Ad-Hoc Injections**:
  - Activate Krasukha-4 VHF Voice Jammer.
  - Turn on GPS Spoofing Station.
  - Launch Cyber Terminal Blackout.
  - Inject Decoy/Ghost Radar armor contact.
- **Live Cognitive Telemetry**: Real-time display of decision reaction time, divergence errors, dropped comms, and team command effectiveness scores.

### 4. Automated After Action Review (AAR)
- **Event Sourcing Engine**: Every order, jamming toggle, message drop, and engagement is permanently recorded with exact sim time.
- **Decision Rationale Capture**: Trainees must record their rationale when issuing key directives, directly preserving their thought process during ambiguity.
- **Interactive Report**: Complete standalone, exportable, print-ready HTML/CSS dossier (`/aar`) and JSON API (`/api/aar.json`).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- **Zero external pip dependencies required** (Runs on Python's built-in `asyncio` and standard library, with an RFC-6455 compliant WebSocket server).

### Running the Trainer

```bash
# 1. Run the launcher script
./run.sh

# Or run directly with Python:
python3 server.py
```

### Access URLs
- **Tactical Cockpit & C2 Terminal**: [http://localhost:8000](http://localhost:8000)
- **Live Interactive After Action Review (AAR)**: [http://localhost:8000/aar](http://localhost:8000/aar)
- **Download Standard PDF Report**: [http://localhost:8000/api/aar/download-pdf](http://localhost:8000/api/aar/download-pdf)
- **AAR Structured JSON API**: [http://localhost:8000/api/aar.json](http://localhost:8000/api/aar.json)

---

## 🧪 Testing

To run the automated test suite verifying scenario models, degradation pipeline, latency injects, combat engagements, and AAR generation:

```bash
.venv/bin/python -m unittest tests/test_sim.py
```

---

## 🎖️ Default Scenario: "Operation Broken Uplink"

- **Mission**: Combined-arms force must assault through a contested mountain defile to secure Highway 4.
- **Friendly Assets**: Alpha Coy HQ (`WARLORD-6`), 1st Platoon Mech (`IRONCLAD-1`), 2nd Platoon Inf (`STALWART-2`), MQ-9 Drone (`HAWKEYE-9`), EW Recon (`SPECTRE-4`).
- **Threat Assets**: Krasukha-4 Heavy Jammer, Valley Pass GPS Spoofing Emitter, Advancing Mechanized OPFOR Column, Concealed ATGM Ambush Team.
- **Training Objectives**:
  1. Identify onset of VHF voice jamming and switch to secondary channel or visual signals.
  2. Detect GPS coordinate drift by cross-referencing terrain contours before driving into the ATGM ambush.
  3. Maintain disciplined initiative and tactical momentum when the Commander's COP terminal is temporarily frozen by cyber intrusion.
