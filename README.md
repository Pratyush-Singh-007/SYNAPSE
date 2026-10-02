# SYNAPSE // Tactical Multi-Domain Decision-Making Trainer
### Immersive Training for Degraded, Intermittent & Contested Communication Environments (DMUU)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Dependencies: Zero](https://img.shields.io/badge/Dependencies-Zero%20(Stdlib%20Only)-success.svg)](https://docs.python.org/3/library/)
[![Protocol: RFC--6455 WebSockets](https://img.shields.io/badge/Protocol-RFC--6455%20WebSockets-informational.svg)](https://datatracker.ietf.org/doc/html/rfc6455)
[![Military Standards](https://img.shields.io/badge/Symbology-NATO%20MIL--STD--2525D-red.svg)](#military-symbology--grid-cartography)
[![Doctrine: ADP 6-0](https://img.shields.io/badge/Doctrine-Mission%20Command%20(ADP%206--0)-purple.svg)](#doctrinal-foundation-mission-command)
[![Theme: High--Contrast](https://img.shields.io/badge/UI-High--Contrast%20Daylight%20C2-black.svg)](#high-contrast-white--black-tactical-theme)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

```
███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗███████╗
██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗█████╗  
╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║██╔══╝  
███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║███████╗
╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
  MULTI-DOMAIN DECISION-MAKING UNDER UNCERTAINTY (DMUU) TRAINER
```

**SYNAPSE** is an immersive, web-based Command and Control (C2) simulation system built to train small-team leaders, company commanders, and tactical staffs in **Decision-Making Under Uncertainty (DMUU)**. 

Contemporary conflicts across Ukraine, the Middle East, and contested maritime littorals demonstrate that **Electronic Warfare (EW)**, **GPS deception**, and **cyber disruption** sever communications at the precise instant critical tactical decisions must be made. Traditional military exercises (TEWTs, CPXs) largely assume continuous situational awareness, zero-latency Blue Force Tracking (BFT), and uncorrupted radio networks. **SYNAPSE strips away ideal assumptions**, forcing commanders to exercise disciplined initiative under delayed, partial, and contradictory information feeds.

---

## 📑 Table of Contents

1. [The Operational Problem Solved](#-the-operational-problem-solved)
2. [Doctrinal Foundation: Mission Command](#-doctrinal-foundation-mission-command)
3. [The 6 Core Platform Functions](#-the-6-core-platform-functions)
4. [Visual Interface & Operational Showcase](#-visual-interface--operational-showcase)
5. [System Architecture & Dataflow](#-system-architecture--dataflow)
6. [Multi-Domain Degradation Pipeline](#-multi-domain-degradation-pipeline)
7. [Station Roles & Echelons](#-station-roles--echelons)
8. [Mathematical Models of Friction](#-mathematical-models-of-friction)
9. [Automated After Action Review & PDF Dossier](#-automated-after-action-review--pdf-dossier)
10. [High-Contrast White & Black Tactical Theme](#-high-contrast-white--black-tactical-theme)
11. [Scenario Catalog](#-scenario-catalog)
12. [Quick Start & Installation](#-quick-start--installation)
13. [REST API & WebSocket Protocol Reference](#-rest-api--websocket-protocol-reference)
14. [Codebase Anatomy](#-codebase-anatomy)
15. [Test Suite & Verification](#-test-suite--verification)

---

## ⚔️ The Operational Problem Solved

| Traditional Simulation Formats (TEWT / CPX) | Contested Peer Combat Reality | SYNAPSE Training Paradigm |
| :--- | :--- | :--- |
| **COP Reliability**: 100% accurate, sub-second BFT icons | **Severe Jamming**: BFT freezes, signals lag 20–120s, positions stale | **Stale Track Uncertainty**: Dynamic uncertainty circles expand as latency spikes |
| **Comms Channels**: Crystal-clear voice and text nets | **RF Denial**: Krasukha-4 VHF voice suppression, dropped SITREPs | **Stochastic Comms Degradation**: Parity noise, word drops, severed links |
| **Navigation**: Precise GPS pinpoints every asset | **Ephemeris Spoofing**: Coordinated offset drift into kill zones | **Deceptive Drift**: Units must verify coordinates against terrain contours |
| **Intelligence Consistency**: Single undisputed enemy track | **Contradictory Feeds**: Thermal UAV sightings contradict radio reports | **Conflicting Injects**: Evaluates commander hesitation vs decisive cross-check |
| **AAR Metric**: Simple task completion / casualty ratios | **Decision Rationale**: Did the commander understand *why* they acted? | **Decision Audit Trail**: Mandatory operational rationale captured with each order |

---

## 🎖️ Doctrinal Foundation: Mission Command

SYNAPSE is built directly upon the tenets of **ADP 6-0 (Mission Command: Command and Control of Army Forces)**:

1. **Competence & Mutual Trust**: Operators must trust forward elements when tactical repeaters go dark.
2. **Shared Understanding**: Building a mental operational picture when digital COP displays freeze.
3. **Commander's Intent**: Subordinate units must execute mission intent without awaiting step-by-step confirmation.
4. **Disciplined Initiative**: Rewarding prompt action to exploit fleeting windows of tactical advantage over paralysis by analysis.
5. **Acceptance of Prudent Risk**: Operating boldly despite degraded sensors and jammed air-ground links.

---

## 🎛️ The 6 Core Platform Functions

SYNAPSE delivers all 6 foundational training functions within **a single, unified web application** on `http://localhost:8000`:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       SYNAPSE UNIFIED WEB PLATFORM                              │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────────┤
│  1. LOGIN    │  2. CONFIG   │  3. LOBBY    │  4. LIVE C2  │  5. EXCON / 6. AAR  │
│  Trainee vs  │  Scenarios,  │  Multiplayer │  2D Vector   │  God-Mode Injector  │
│  Instructor  │  Difficulty, │  Room Net &  │  MIL-STD Map │  & Auto-Generated   │
│  Role Select │  Duration    │  Comms Check │  & Decision  │  PDF Report Dossier │
└──────────────┴──────────────┴──────────────┴──────────────┴─────────────────────┘
```

### 1. Home / Station Authentication Portal
- Role selection tailored to tactical stations:
  - **Company Commander** (`WARLORD-6`) — COP Decision Maker.
  - **1st Platoon Leader** (`IRONCLAD-1`) — Forward Mechanized Armor.
  - **2nd Platoon Leader** (`STALWART-2`) — Overwatch & Support-by-Fire.
  - **JTAC / Air Liaison** (`HAWKEYE-9`) — Sensor Recon & CAS Controller.
  - **EW & Cyber Specialist** (`SPECTRE-4`) — RF Spectrum Defense.
  - **EXCON Instructor** (`EXCON-LEAD`) — Exercise White Cell Controller.
- Custom simulation room codes (e.g. `ALPHA-6`, `TASKFORCE-9`) for multi-seat team exercises.
- **Instant Solo Launch (`⚡`)**: One-click launch initializing a standalone scenario with local synthetic team bots.

### 2. Scenario & Degradation Configuration
- Select operational scenarios (*Broken Uplink*, *Urban Aegis*).
- Calibrate exercise duration (5, 10, 15, or 20 minutes).
- Choose threat difficulty:
  - `STANDARD`: Baseline latency, intermittent carrier noise.
  - `CONTESTED`: High directional VHF jamming, selective GPS spoofing.
  - `SEVERE BLACKOUT`: Continuous RF suppression, cyclic cyber BFT freeze.
- Set team user capacity (4, 6, or 10 operators).

### 3. Multiplayer Room Net & Readiness Hub
- Real-time roster synchronization across all connected browser tabs and client devices.
- Live readiness state tracking (`PREPARING` vs `READY FOR DEPLOYMENT`).
- Integrated **Tactical Audio Net Comms Check**: Synthesizes authentic radio squelch bursts and alert pings via Web Audio API.

### 4. Live Tactical C2 Cockpit & Decision Capture
- **2D Military Map Canvas**: High-performance vector cartography with MGRS coordinate grid, topographic contour defiles, and NATO MIL-STD symbols.
- **Tactical Communications Net (TAC-NET)**: Multichannel VHF/UHF tactical radio channels (`TAC-1 CMD`, `TAC-2 FIRES`, `SQUAD-A`, `SQUAD-B`).
- **Tactical Directive Modal**: Clicking any friendly unit and targeting a location opens a mandatory **Commander Decision Rationale** modal. This captures *why* the commander ordered an action under the current information clarity level.
- **Dedicated Sensor Stations**:
  - **UAV FLIR Thermal Feed**: Dual Black-Hot / White-Hot IR optics with laser rangefinder and targeting crosshair.
  - **RF Spectrum Analyzer**: Live carrier wave sweep (30 MHz - 7.2 GHz) displaying active jammer power spikes and FHSS countermeasures.

### 5. Instructor EXCON (Exercise Control) God-Mode Dashboard
- **Ground Truth vs Perceived Reality**: Displays actual physical unit locations side-by-side with ghost markers of trainee perceived positions.
- **Interactive Jammer Manipulation**: Click and drag active EW jamming bubbles directly on the map.
- **Ad-Hoc Injections**:
  - `⚡ CONTRADICTORY SITREP`: Transmits false ground scout contact reports conflicting with aerial drone video.
  - `🛑 CYBER BFT FREEZE`: Locks digital blue force updates for 60 seconds.
  - `🛰️ GPS EPHEMERIS DRIFT`: Injects mathematical coordinate skew.
- **Live Cognitive Telemetry**: Real-time monitoring of Command Effectiveness Score, EW reaction latency, and divergence errors.

### 6. Automated After Action Review (AAR) & Downloadable PDF
- Permanent event-sourcing ledger tracking every directive, transmission drop, jammer state change, and combat casualty.
- **Algorithmic Doctrine Scoring**: Evaluates hesitation vs initiative and calculates target divergence metrics.
- **Downloadable Standard PDF Dossier (`/api/aar/download-pdf`)**: Built using a zero-dependency standard PDF 1.4 binary engine.
- Interactive standalone HTML report viewer (`/aar`) with chronological timeline filters (`ALL`, `ORDERS`, `COMMS`, `CRITICAL`).

---

## 📸 Visual Interface & Operational Showcase

SYNAPSE is engineered with a **high-contrast, daylight C2 military cartography theme** (clean high-visibility white operational canvas `#ffffff`, deep-black structural framing `#0a0a0a`, and precise NATO MIL-STD operational accents). Below is a comprehensive visual walkthrough of the platform's four primary operational interfaces and their underlying capabilities.

---

### 1. Tactical C2 Cockpit & Cartographic Vector Map
> **Primary Command Station (`WARLORD-6`)** — Where small-team and sub-unit commanders analyze spatial friction, track units under uncertainty, and issue directives with captured operational rationale.

<p align="center">
  <img src="docs/images/tactical_cockpit.jpg" alt="Tactical C2 Cockpit & Cartographic Vector Map" width="100%">
</p>

#### Operational Features & Visual Anatomy:
* **MGRS 1:50,000 Precision Vector Grid**: Real-time canvas rendering NATO Military Grid Reference System (MGRS) grid coordinates and topographic contour defiles for terrain-association navigation when satellite navigation is degraded.
* **NATO MIL-STD-2525D Symbology**: Standardized operational blue rectangles for friendly mechanized infantry (`IRONCLAD-1`) and support armor (`STALWART-2`); hostile red diamonds for OPFOR reconnaissance and armor formations.
* **Dynamic Uncertainty Circles (Amber Rings)**: Concentric expanding dashed rings representing positional variance ($\sigma_{pos}$). When RF jamming causes blue-force telemetry packets to drop, the uncertainty circle expands dynamically to visualize the commander's fog of war.
* **Krasukha-4 Jamming Bubble (Purple Radius)**: Directional electronic warfare boundary projecting RF suppression across forward defiles.
* **Tactical Communications Net (TAC-NET)**: Lower-left tactical radio terminal featuring multichannel selection (`TAC-1 CMD`, `TAC-2 FIRES`, `SQUAD-A`), real-time signal integrity telemetry (`SIGNAL: 28% // DROPPED: 42%`), and parity noise corruption simulation (`[STATIC... BREAKING...]`).
* **Miniature FLIR UAV Sensor Inset**: Floating high-angle airborne reconnaissance feed providing thermal overwatch directly within the main tactical map canvas.
* **Mandatory Decision Rationale Prompt**: Clicking any friendly unit to issue a movement or fire directive triggers the Commander Rationale Modal, enforcing doctrine reflection before committing forces.

---

### 2. Specialist Stations: UAV Black-Hot FLIR & RF Spectrum Analyzer
> **Dual Multi-Domain Sensor Feed** — Real-time airborne thermal surveillance combined with electronic warfare signal detection and frequency-hopping counter-countermeasures (ECCM).

<p align="center">
  <img src="docs/images/flir_spectrum.jpg" alt="Specialist Stations: UAV FLIR & Spectrum Analyzer" width="100%">
</p>

#### Operational Features & Visual Anatomy:
* **UAV Airborne Black-Hot Thermal Camera (Left)**:
  - **Military Thermal Polarities**: Black-Hot / White-Hot IR imaging exposing engine heat blooms and troop positions through dense foliage and smoke screens.
  - **PRF Laser Target Designator**: Pulse Repetition Frequency code tracking (`PRF: 1688`) with high-resolution targeting crosshairs and angular gimbal coordinates (`AZ: 042°` / `EL: -28°`).
  - **Target Tracking & Bounding Box**: Autonomous optical detection tracking hostile armor columns moving along northern roads.
  - **Comms Link Health Alarm**: Live banner warning of airborne C2 uplink disruption (`UPLINK JAMMING DETECTED - TELEMETRY DEGRADED`).
* **RF Spectrum Analyzer & ECCM Suite (Right)**:
  - **Wideband Radio Frequency Sweep**: Real-time power spectrum scanning frequencies from 30 MHz to 7.2 GHz with waterfall spectral density display.
  - **Hostile Jamming Power Spike**: Clear visualization of enemy Krasukha-4 carrier suppression centered at 450 MHz with high signal-to-noise degradation.
  - **Fast Frequency-Hopping Spread Spectrum (FHSS)**: Toggleable electronic counter-countermeasure (ECCM) hopping across 1,200 frequencies/second to punch critical tactical directives through enemy electronic noise.

---

### 3. Instructor EXCON (Exercise Control) God-Mode & Injections
> **Exercise White Cell Control Center (`EXCON-LEAD`)** — The supervisory dashboard giving instructors ground truth visibility, live trainee cognitive telemetry, and ad-hoc friction injection controls.

<p align="center">
  <img src="docs/images/excon_controller.jpg" alt="Instructor EXCON God-Mode Controller" width="100%">
</p>

#### Operational Features & Visual Anatomy:
* **Dual-Layer Reality Map**:
  - **Ground Truth Tracks (Solid Vector Icons)**: Exact physical coordinates of all blue and red assets in real time.
  - **Trainee Perceived Reality (Ghosted Markers)**: Visualizes the delayed, drifted, and stale unit locations currently displayed on the trainees' screens.
* **Interactive EW Jammer Node**: Direct click-and-drag Krasukha-4 emitter node on the tactical map with live adjustment of suppression radius, frequency band, and transmit output.
* **One-Click Dynamic Injections**:
  - `⚡ CONTRADICTORY SITREP`: Transmits synthetic ground reports that directly contradict live UAV optical reconnaissance, testing whether commanders cross-reference multiple intelligence domains.
  - `🛑 CYBER BFT FREEZE`: Locks digital blue force updates for 60 seconds, forcing leaders to switch to voice-procedural reporting.
  - `🛰️ GPS EPHEMERIS DRIFT`: Injects progressive coordinate spoofing, shifting navigation fixes toward an ambush kill zone.
* **Live Cognitive & Doctrinal Telemetry**:
  - **Command Effectiveness Score**: Real-time algorithmic performance metric (85% SUPERIOR).
  - **Reaction Latency**: Real-time measurement of seconds elapsed between threat emergence and commander decision (14.2s).
  - **Target Divergence Metric**: Average spatial deviation between commander intended waypoints and actual ground truth positions (310m).
* **Live Decision Rationale Audit Feed**: Scrolling chronological log displaying every order executed by trainees alongside their written operational rationale.

---

### 4. Automated After Action Review (AAR) & Downloadable PDF Dossier
> **Post-Mission Analysis & Doctrinal Debrief (`/aar`)** — Comprehensive event-sourcing evaluation and one-click PDF generation capturing the full decision lifecycle under uncertainty.

<p align="center">
  <img src="docs/images/aar_report.jpg" alt="Automated After Action Review (AAR) Dossier" width="100%">
</p>

#### Operational Features & Visual Anatomy:
* **Executive Mission Performance Header**:
  - Doctrinal Combat Readiness Grade: **85% (SUPERIOR - MISSION COMMAND QUALIFIED)**.
  - Multi-Domain Operational Metrics: Hesitation Latency (12.4s), Communications Loss Tolerance (88%), Team Positional Divergence (240m), Unit Combat Survivability (91%).
* **Chronological Decision & Incident Timeline**:
  - Event category filtering tabs (`ALL EVENTS`, `COMMAND ORDERS`, `COMMS FAILURES`, `CRITICAL INJECTS`).
  - Microsecond-accurate event timestamps linked to scenario mission clock.
* **Commander Decision Rationale Audit Cards**:
  - In-depth cards dissecting each tactical directive issued during the exercise.
  - Compares the **Commander's Perceived State** at the moment of decision against **Actual Ground Truth**.
  - Displays the raw rationale text entered by the trainee: *"Ordered 1st Platoon to fall back to defile due to thermal contact contradicting radio silence"*.
  - Algorithmic doctrinal commentary assessing whether the action adhered to ADP 6-0 Mission Command principles.
* **One-Click Standard PDF Report Download (`/api/aar/download-pdf`)**:
  - Generates a formal, printable military debrief dossier using a zero-dependency standard PDF 1.4 binary engine.

---

## 🏛️ System Architecture & Dataflow

SYNAPSE is architected as an **ultra-low-latency, zero-external-dependency distributed tactical simulation engine**. Built entirely on Python 3.10+ standard asynchronous primitives (`asyncio`, `socket`, `hashlib`, `mimetypes`) and standards-compliant browser APIs (HTML5 Canvas, WebSockets RFC-6455, Web Audio API), it delivers deterministic 10 Hz physics and multi-domain friction without requiring Redis, Celery, Node.js, or external database servers.

---

### 1. Multi-Tiered System Architecture

<p align="center">
  <img src="docs/images/system_architecture.jpg" alt="SYNAPSE System Architecture Blueprint" width="100%">
</p>

```mermaid
flowchart TD
    subgraph L1 ["🖥️ 1. CLIENT PRESENTATION TIER (Web Client)"]
        UI_1["Tactical C2 Cockpit Canvas"]:::clientStyle
        UI_2["Web Audio TAC-NET Radio"]:::clientStyle
        UI_3["UAV Black-Hot FLIR Inset"]:::clientStyle
        UI_4["RF Spectrum Analyzer"]:::clientStyle
        UI_5["EXCON God-Mode Console"]:::clientStyle
        UI_6["Interactive AAR Dossier"]:::clientStyle
    end

    subgraph L2 ["⚡ 2. NETWORK PROTOCOL & GATEWAY TIER (Python Stdlib)"]
        GW_1["RFC-6455 WebSocket Engine"]:::gatewayStyle
        GW_2["HTTP/1.1 REST & Asset Server"]:::gatewayStyle
        GW_3["Room Session Multiplexer"]:::gatewayStyle
    end

    subgraph L3 ["⚙️ 3. SIMULATION & PHYSICS ENGINE (sim.engine)"]
        SIM_1["10 Hz Asyncio Event Loop"]:::simStyle
        SIM_2["Ground Truth Kinematics & LOS"]:::simStyle
        SIM_3["Rules of Engagement Calculus"]:::simStyle
    end

    subgraph L4 ["📡 4. MULTI-DOMAIN DEGRADATION PIPELINE (sim.degradation)"]
        DEG_1["Krasukha-4 Jamming Margin"]:::degradeStyle
        DEG_2["Stochastic Delay Queue"]:::degradeStyle
        DEG_3["Markov Packet Loss Filter"]:::degradeStyle
        DEG_4["GPS Ephemeris Spoofing"]:::degradeStyle
        DEG_5["Cyber BFT Freeze Clamp"]:::degradeStyle
    end

    subgraph L5 ["📊 5. AAR ANALYTICS & DOCUMENT CORE (sim.aar)"]
        AAR_1["Event-Sourcing Audit Ledger"]:::aarStyle
        AAR_2["ADP 6-0 Cognitive Grader"]:::aarStyle
        AAR_3["Zero-Dependency PDF 1.4 Binary Generator"]:::aarStyle
    end

    classDef clientStyle fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0c4a6e;
    classDef gatewayStyle fill:#d1fae5,stroke:#059669,stroke-width:2px,color:#064e3b;
    classDef simStyle fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef degradeStyle fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#991b1b;
    classDef aarStyle fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#4c1d95;

    style L1 fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0369a1
    style L2 fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#047857
    style L3 fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#b45309
    style L4 fill:#fff1f2,stroke:#e11d48,stroke-width:2px,color:#be123c
    style L5 fill:#f5f3ff,stroke:#7c3aed,stroke-width:2px,color:#5b21b6

    L1 ==>|RFC-6455 Bi-Directional Frames / REST| L2
    L2 ==>|Session Directives & Auth Dispatch| L3
    L3 ==>|Ground Truth Kinematic Coordinates| L4
    L4 ==>|Station-Tailored Perceived World State| L2
    L3 -.->|Ground Truth State Telemetry| L5
    L1 -.->|Commander Rationale Audit Log| L5
    L5 ==>|Automated PDF 1.4 Binary Dossier| L2
```

---

### 2. End-to-End Operational Lifecycle & Sequence Flow

<p align="center">
  <img src="docs/images/operational_workflow.jpg" alt="SYNAPSE Operational Decision Workflow & Tactical Lifecycle" width="100%">
</p>

The following sequence diagram details the end-to-end dataflow of a complete tactical decision cycle: from operator session registration, continuous 10 Hz physical state updates, mandatory decision rationale capture, instructor EW injects, and degradation filtering, to post-mission PDF dossier generation:

```mermaid
sequenceDiagram
    autonumber
    actor Trainee as Trainee Commander (WARLORD-6)
    participant Client as Web Client (Cockpit / TAC-NET)
    participant Server as Async Gateway (server.py)
    participant SimEngine as Simulation Engine (sim.engine)
    participant Degrade as Degradation Pipeline (sim.degradation)
    actor EXCON as Instructor White Cell (EXCON-LEAD)
    participant AAR as AAR & PDF Engine (sim.aar)

    rect rgb(235, 248, 255)
    Note over Trainee,AAR: 🌐 PHASE 1: SESSION ESTABLISHMENT & AUTHENTICATION
    Trainee->>Client: Selects Callsign "WARLORD-6", Room "ALPHA-6"
    Client->>Server: HTTP GET / & Upgrade to RFC-6455 WebSocket
    Server->>SimEngine: Register Trainee to Session Room ALPHA-6
    SimEngine-->>Client: Initial Perceived Operational Picture (Clear Weather, 0% Noise)
    end

    rect rgb(236, 253, 245)
    Note over Trainee,AAR: ⚙️ PHASE 2: 10 Hz REAL-TIME SIMULATION & TELEMETRY LOOP
    loop Every 100ms (10 Hz Tick)
        SimEngine->>SimEngine: Update Unit Kinematics & Physics Vectors
        SimEngine->>Degrade: Submit Physical Ground Truth
        Degrade->>Degrade: Compute Line-of-Sight & RF Jamming Radius
        Degrade-->>Client: Stream Station-Tailored Perceived World State
    end
    end

    rect rgb(254, 249, 195)
    Note over Trainee,AAR: 🎯 PHASE 3: DIRECTIVE SUBMISSION WITH MANDATORY RATIONALE
    Trainee->>Client: Orders "1st Platoon Advance to Defile"
    Client->>Trainee: Prompts Mandatory "Commander Decision Rationale"
    Trainee->>Client: Inputs "Advancing to secure high ground before enemy air arrive"
    Client->>Server: WebSocket Frame: ORDER + RATIONALE + PERCEIVED_TIMESTAMP
    Server->>AAR: Record Directive, Rationale, and Ground Truth Delta
    Server->>SimEngine: Queue Unit Movement Vector
    end

    rect rgb(254, 226, 226)
    Note over Trainee,AAR: 🚨 PHASE 4: INSTRUCTOR AD-HOC INJECTIONS & MULTI-DOMAIN FRICTION
    EXCON->>Server: Injects "Krasukha-4 Jamming (450 MHz, 2.5km Radius)"
    Server->>Degrade: Activate RF Suppression Field
    EXCON->>Server: Injects "Contradictory SITREP (Scout reports ambush at Defile)"
    Server->>Degrade: Intercept TAC-NET Voice/Text Stream
    Degrade->>Degrade: Apply Parity Noise & 35s Delay Buffer
    Degrade-->>Client: Corrupted Alert: "[STATIC]... ENEMY ARMOR AT DEFILE ...[BREAK]"
    Client-->>Trainee: Displays Expanding Amber Uncertainty Circle (σ = 450m)
    end

    rect rgb(243, 232, 255)
    Note over Trainee,AAR: 🧠 PHASE 5: TACTICAL DECISION UNDER DEGRADED CONDITIONS
    Trainee->>Client: Reviews Contradictory Feeds (UAV Clear vs Scout Ambush)
    Trainee->>Client: Submits Counter-Order: "Halt at Phase Line Red, Request UAV Cross-Check"
    Client->>Server: WebSocket Frame: ORDER + RATIONALE
    Server->>AAR: Log Reaction Latency (14.2s), Hesitation Index, and Adherence to Doctrine
    end

    rect rgb(224, 242, 254)
    Note over Trainee,AAR: 📑 PHASE 6: EXERCISE COMPLETION & AUTOMATED AAR DOSSIER EXPORT
    EXCON->>Server: Triggers "END SIMULATION & COMPILE AAR"
    Server->>AAR: Aggregate All Audit Events, Attrition, and Decision Timelines
    AAR->>AAR: Execute ADP 6-0 Mission Command Scoring Algorithm
    Client->>Server: HTTP GET /api/aar/download-pdf
    Server->>AAR: Generate Zero-Dependency PDF 1.4 Binary Dossier
    AAR-->>Server: Return Formatted PDF Binary Stream
    Server-->>Client: Transmit "AAR_ALPHA-6_Report.pdf" (Instant Download)
    end
```

---

### 3. Component Responsibility Matrix

| Subsystem Component | File Path | Architectural Layer | Concurrency Model | Primary Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **Network Gateway** | [`server.py`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/server.py) | Protocol & Transport | `asyncio.StreamServer` | Handshake RFC-6455 WebSockets, route REST endpoints, manage client connection pools, multiplex rooms. |
| **Simulation Engine** | [`sim/engine.py`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/sim/engine.py) | Physics & State | 10 Hz Non-Blocking Loop | Update entity kinematic vectors, compute line-of-sight defiles, resolve Rules of Engagement, manage room state. |
| **Degradation Pipeline** | [`sim/degradation.py`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/sim/degradation.py) | Multi-Domain Friction | Stateless per-tick Transform | Calculate RF jamming margins (SINR), queue stochastic latency buffers, inject Markov packet loss, spoof GPS vectors. |
| **Scenario Catalog** | [`sim/scenarios.py`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/sim/scenarios.py) | Domain Configurations | Declarative Factory | Define operational OOBs (Order of Battle), terrain contour defiles, waypoint networks, initial jammer nodes. |
| **AAR & PDF Engine** | [`sim/aar.py`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/sim/aar.py) | Analytics & Documents | Event Sourcing & Synchronous | Immutable telemetry ledger, ADP 6-0 Mission Command scoring algorithms, zero-dependency PDF 1.4 binary compiler. |
| **Tactical Client App** | [`static/app.js`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/static/app.js) | Presentation & UI | Single-threaded Browser Loop | High-contrast vector canvas cartography, Web Audio radio squelch synthesizer, decision modal, WebSocket state sync. |
| **Tactical Shell** | [`static/index.html`](file:///Users/pratyush/Desktop/Immersive%20Multi-Domain%20Decision-Making%20Trainer%20for%20Degraded%20Communication%20Environments/static/index.html) | Presentation & Styles | DOM / CSS3 Grid | High-contrast White & Black daylight C2 styling, NATO iconography, UAV FLIR optic, RF spectrum visualizer. |

---

## 📡 Multi-Domain Degradation Pipeline

The degradation engine acts as an active **Man-in-the-Middle (MitM) filter** between physical battlefield ground truth and what is displayed on each commander's workstation:

```mermaid
flowchart TD
    GT["🌐 Ground Truth Physical Unit State\n(True Coordinates X, Y, Z, Status)"]:::slateNode --> LOS_Check{"📡 Line-of-Sight & Proximity Check\nDistance to Krasukha-4 <= R_jam?"}:::decisionNode

    LOS_Check -- "YES (Within Jamming Cone)" --> JammedZone["🚨 CONTESTED RF DOMAIN\n(SINR < Threshold Gamma)"]:::dangerNode
    LOS_Check -- "NO (Clear Field)" --> ClearZone["✅ UNCONTESTED RF DOMAIN\n(SINR >= Threshold Gamma)"]:::safeNode

    JammedZone --> LatencyCalc["⏱️ Apply Stochastic Latency Buffer\nDelta_t = Uniform(15s, 90s)"]:::warnNode
    JammedZone --> MarkovLoss{"🎲 Markov Packet Loss Check\nRandom() < P_drop (45% - 85%)?"}:::decisionNode

    MarkovLoss -- "DROP (Loss)" --> PacketDropped["❌ Drop Telemetry Frame\n(Trainee Receives No Update)"]:::dropNode
    MarkovLoss -- "PASS (Arrived)" --> NoiseInject["📻 Apply Lexical Parity Noise\nReplace Characters with [STATIC/CORRUPT]"]:::warnNode

    ClearZone --> NormalDelay["⚡ Standard Network Latency\nDelta_t = 25ms // Loss < 1%"]:::softGreenNode

    LatencyCalc --> GPSSpoofCheck{"🛰️ GPS Ephemeris Spoofing Active?\nTarget in Spoofing Polygon?"}:::decisionNode
    NoiseInject --> GPSSpoofCheck
    NormalDelay --> GPSSpoofCheck

    GPSSpoofCheck -- "YES" --> ApplyDrift["📐 Add Ephemeris Offset Vector\nX_perceived = X_true + Delta_X (+85m)\nY_perceived = Y_true + Delta_Y (-45m)"]:::warnNode
    GPSSpoofCheck -- "NO" --> CyberFreezeCheck{"🛑 Cyber BFT Freeze Active?\nT_now - T_freeze < 60s?"}:::decisionNode

    ApplyDrift --> CyberFreezeCheck

    CyberFreezeCheck -- "YES" --> ClampCoords["🔒 Clamp Unit Coordinates\nX_perceived = X_frozen\nY_perceived = Y_frozen\nExpand Uncertainty Radius (sigma)"]:::warnNode
    CyberFreezeCheck -- "NO" --> FinalState["📦 Assemble Tailored Perceived World State\nSerialize into RFC-6455 Frame"]:::purpleNode

    ClampCoords --> FinalState
    FinalState --> TraineeStation["🖥️ Deliver to Station Cockpit Display"]:::cockpitNode

    classDef slateNode fill:#f1f5f9,stroke:#334155,stroke-width:2px,color:#0f172a;
    classDef decisionNode fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,color:#78350f;
    classDef dangerNode fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#991b1b;
    classDef safeNode fill:#dcfce7,stroke:#10b981,stroke-width:2px,color:#065f46;
    classDef warnNode fill:#ffedd5,stroke:#f97316,stroke-width:2px,color:#9a3412;
    classDef dropNode fill:#fca5a5,stroke:#b91c1c,stroke-width:2px,color:#7f1d1d;
    classDef softGreenNode fill:#ecfdf5,stroke:#34d399,stroke-width:1px,color:#064e3b;
    classDef purpleNode fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px,color:#4c1d95;
    classDef cockpitNode fill:#e0f2fe,stroke:#0284c7,stroke-width:3px,color:#0c4a6e;
```

---

## 👥 Station Roles & Echelons

| Role Symbol | Station Role | Call Sign | Tactical Authority & Scope | Information Vulnerabilities |
| :---: | :--- | :--- | :--- | :--- |
| **HQ** | **Company Commander** | `WARLORD-6` | Exercises overall mission command; issues strategic redeployment orders; authorizes CAS and fires. | Susceptible to stale BFT tracks, frozen COP displays, and conflicting intelligence feeds. |
| **INF** | **1st Platoon Leader** | `IRONCLAD-1` | Directs forward mechanized infantry platoon; leads main avenue of advance. | High vulnerability to directional VHF radio cutoff; mountain ridges cause complete LOS shadow. |
| **INF** | **2nd Platoon Leader** | `STALWART-2` | Directs overwatch element; establishes support-by-fire positions; guards flank. | Prone to GPS spoofing drift, drawing support elements out of position into enemy engagement areas. |
| **UAV** | **JTAC / Air Liaison** | `HAWKEYE-9` | Operates Sentinel-1 MQ-9 UAV sensor; designates targets via PRF 1688 laser; coordinates CAS 9-lines. | Downlink RF noise causes thermal video tearing; decoy thermal reflectors simulate ghost radar contacts. |
| **EW** | **EW & Cyber Specialist**| `SPECTRE-4` | Monitors RF spectrum (30 MHz - 7.2 GHz); identifies enemy Krasukha-4 signatures; activates FHSS counter-measures. | Subject to broadband saturation; cyber penetration attempts on tactical routers. |
| **EXCON** | **Exercise Controller** | `EXCON-LEAD` | White Cell God-Mode; inspects true battlefield state; injects ad-hoc EW and cyber disruptions. | Maintains complete ground truth transparency. |

---

## 📐 Mathematical Models of Friction

### 1. RF Jamming Margin & Signal-to-Interference-plus-Noise Ratio (SINR)

The degradation pipeline computes effective received power for VHF voice and UHF data nets using the inverse-square propagation model:

$$P_{rx} = P_{tx} \cdot \left(\frac{\lambda}{4\pi d}\right)^2$$

In the presence of an active jammer with power $P_j$ at distance $d_j$:

$$\text{SINR} = \frac{P_{rx}}{P_j \cdot \left(\frac{\lambda}{4\pi d_j}\right)^2 + N_0}$$

When $\text{SINR} < \gamma_{\text{threshold}}$, tactical comms experience packet drop with probability:

$$P_{\text{drop}} = 1 - \frac{1}{1 + e^{-k(\gamma - \text{SINR})}}$$

### 2. GPS Spoofing Ephemeris Drift Vector

When an asset enters the effective radiated radius of a deception spoofer, its perceived coordinate vector $\mathbf{P}_{\text{perceived}}$ diverges from its physical ground truth $\mathbf{P}_{\text{true}}$:

$$\mathbf{P}_{\text{perceived}}(t) = \mathbf{P}_{\text{true}}(t) + \mathbf{D}(t)$$

$$\mathbf{D}(t) = \mathbf{D}_{\text{max}} \cdot \left(1 - e^{-\alpha (t - t_0)}\right) + \mathbf{\mathcal{N}}(0, \sigma^2)$$

This replicates real-world deceptive GPS drift, which starts imperceptibly before drawing forces kilometers off-course.

### 3. Mission Command Effectiveness Score

Upon completion of the exercise, the AAR engine evaluates team performance on a normalized scale (0 - 100):

$$S_{\text{effective}} = \max\left(15, \min\left(100, 100 - \left(N_{\text{divergence}} \cdot 20\right) - \left(N_{\text{dropped}} \cdot 2\right) + \left(N_{\text{orders}} \cdot 5\right)\right)\right)$$

- $S \ge 85$: **SUPERIOR** — Displayed disciplined initiative and agile command.
- $65 \le S < 85$: **ADEQUATE** — Sound execution with minor hesitation under jamming.
- $S < 65$: **CRITICAL GAPS OBSERVED** — Significant hesitation, blind obedience to spoofed telemetry, or lost team cohesion.

---

## 📄 Automated After Action Review & PDF Dossier

SYNAPSE includes a **zero-dependency PDF 1.4 binary engine** that produces print-ready military debrief reports without requiring external tools like ReportLab, WeasyPrint, or headless Chromium.

### What the AAR Report Contains:
1. **Executive Debrief Summary**: Exercise title, operational theater, sim time elapsed, and total events logged.
2. **Key Telemetry Metrics**:
   - **Command Effectiveness Score** (0–100%).
   - **EW Reaction Latency** (Time in seconds between first jamming detection and first tactical directive).
   - **Divergence Incidents** (Number of directives issued based on spoofed or corrupted data).
   - **Comms Severed Ratio** (Dropped vs delivered transmissions).
3. **Decision Audit Timeline**: Chronological log of every directive with the **Commander's exact operational rationale**:
   > *"Advancing 1st Platoon along Highway 4 despite degraded BFT because UAV FLIR confirms northern defile is clear of hostile armor."*

---

## ⚪⚫ High-Contrast White & Black Tactical Theme

SYNAPSE features a **high-contrast White and Black visual design**, matching military daylight paper cartography and command post operations:

- **Cartographic Paper Grid**: Clean `#ffffff` canvas with dark slate MGRS coordinate markings and topographic elevation defiles.
- **MIL-STD Symbology**: Deep navy blue (`#1e40af`) friendly rectangles and tactical red (`#b91c1c`) enemy diamonds with solid black borders.
- **Black-Hot Thermal FLIR**: Authentic military Black-Hot IR imaging where vehicle engine blocks and gun barrels appear as crisp dark heat signatures against a light ground contour.
- **High-Visibility Readability**: Razor-sharp black typography and bold borders designed for high legibility under both daylight and operational briefing screens.

---

## 🗺️ Scenario Catalog

### Scenario 1: "Operation Broken Uplink" (Default)
- **Theater**: Rugged Mountain Defile // Highway 4 pass.
- **Operational Challenge**: Combined-arms force must assault eastward to secure a mountain crossroads.
- **Threat Vector**: Hostile Krasukha-4 mobile jammer suppresses 45 MHz VHF voice net, while a valley-floor GPS spoofer alters BFT positions to steer units toward a concealed Kornet ATGM ambush.

### Scenario 2: "Operation Urban Aegis"
- **Theater**: High-Density Megacity Sector // Metro Corridor.
- **Operational Challenge**: Clear motorized reconnaissance elements through urban street canyons.
- **Threat Vector**: Severe multipath attenuation from high-rise buildings, coupled with low-altitude commercial drone spoofers creating ghost radar tracks.

---

## 🚀 Quick Start & Installation

### System Requirements
- **OS**: macOS, Linux, or Windows.
- **Python**: Python 3.10 or newer (tested up to Python 3.14).
- **Browser**: Any modern browser (Chrome, Edge, Safari, Firefox).
- **External Dependencies**: **NONE** (100% Python standard library).

### One-Command Launch

```bash
# Clone the repository
git clone https://github.com/Pratyush-Singh-007/SYNAPSE.git
cd SYNAPSE

# Make launcher executable and start
chmod +x run.sh
./run.sh
```

*Or launch directly via Python:*
```bash
python3 server.py
```

### Accessing the Platform

| Interface | URL | Purpose |
| :--- | :--- | :--- |
| **Tactical Web Platform** | [http://localhost:8000](http://localhost:8000) | Main application (Login, Lobby, C2 Cockpit, FLIR, Spectrum, EXCON) |
| **Live AAR Debrief** | [http://localhost:8000/aar](http://localhost:8000/aar) | Full-screen interactive After Action Review report |
| **Download PDF Report** | [http://localhost:8000/api/aar/download-pdf](http://localhost:8000/api/aar/download-pdf) | Direct download of binary AAR dossier in PDF format |
| **REST Metrics API** | [http://localhost:8000/api/aar.json](http://localhost:8000/api/aar.json) | Machine-readable JSON telemetry feed |

---

## 🔌 REST API & WebSocket Protocol Reference

### WebSocket Protocol (`ws://localhost:8000/ws`)

Connect with standard RFC-6455 client. Upon handshake, the server streams 10 Hz `STATE_UPDATE` packets.

#### Client Action Payloads:

```json
// 1. Authenticate Station
{ "action": "LOGIN", "callsign": "WARLORD-6", "user_type": "TRAINEE", "role": "COMMANDER", "room_code": "ALPHA-6" }

// 2. Issue Order with Mandatory Rationale
{
  "action": "ISSUE_ORDER",
  "unit_id": "unit_alpha_1",
  "order_type": "MOVE",
  "target": { "x": 520.0, "y": 480.0 },
  "rationale": "Advancing to seize key defile junction while voice link is open."
}

// 3. Transmit Radio Comms
{ "action": "TRANSMIT_COMMS", "channel": "TAC-1", "content": "CONTACT: Enemy armor grid 742 481", "msg_type": "CONTACT" }

// 4. Trigger EXCON Inject (Instructor)
{ "action": "INSTRUCTOR_ACTION", "sub_action": "CONTRADICTORY_INTEL", "channel": "TAC-1" }
```

### HTTP Endpoints

- `GET /` — Serves the unified single-page tactical web platform.
- `GET /aar` — Serves the standalone After Action Review report.
- `GET /api/aar.json?room=ALPHA-6` — Returns JSON structured timeline and metrics.
- `GET /api/aar/download-pdf?room=ALPHA-6` — Generates and returns binary `application/pdf`.
- `GET /api/scenarios` — Lists available scenarios and operational parameters.

---

## 📂 Codebase Anatomy

```
SYNAPSE/
├── server.py                   # High-concurrency asyncio WebSocket & HTTP web engine
├── run.sh                      # Zero-configuration launch script
├── README.md                   # Technical documentation & training guide
├── .gitignore                  # Clean repository ignore rules
├── sim/                        # Simulation Physics & Scenario Core
│   ├── models.py               # Tactical units, Vector2D, Jamming zones, Comms packets
│   ├── scenario_engine.py      # 10 Hz world clock, combat resolution, and state manager
│   ├── degradation_pipeline.py # RF signal degradation, latency delay, and spoofing logic
│   ├── scenarios.py            # Battle orders for Operation Broken Uplink & Urban Aegis
│   └── aar_engine.py           # Telemetry sourcing, doctrine metrics, and PDF generator
├── static/                     # Frontend C2 Cockpit & Tactical UI
│   ├── index.html              # Unified single-page HTML application
│   ├── css/
│   │   └── tactical.css        # High-contrast White & Black daylight theme
│   └── js/
│       ├── app.js              # Coordinator, WebSocket bridge, and modal controller
│       ├── tactical_map.js     # 2D vector canvas, MGRS grid, and NATO symbology
│       ├── flir_drone.js       # Synthetic Black-Hot thermal drone simulator
│       ├── spectrum_analyzer.js# Real-time RF spectrum analyzer & ECCM monitor
│       ├── comms_terminal.js   # Multichannel tactical radio terminal & audio triggers
│       ├── instructor_console.js# EXCON God-Mode console & live decision audit
│       ├── aar_viewer.js       # Live in-app AAR debrief renderer
│       └── audio.js            # Web Audio API procedural squelch & jamming sound generator
└── tests/                      # Automated Verification Suite
    ├── test_sim.py             # Simulation loop, physics, engagements, and AAR tests
    └── test_protocol.py        # WebSocket handshake, framing, and HTTP route tests
```

---

## 🧪 Test Suite & Verification

SYNAPSE includes a complete automated test suite verifying scenario execution, degradation mathematics, multi-room isolation, and PDF generation:

```bash
# Run all automated tests
python3 -m unittest discover tests
```

Output:
```
.............
----------------------------------------------------------------------
Ran 13 tests in 0.020s

OK
```

---

## 📜 Doctrinal References & Citations

1. **Headquarters, Department of the Army (2019)**. *ADP 6-0: Mission Command — Command and Control of Army Forces*. Washington, DC: U.S. Government Publishing Office.
2. **Chairman of the Joint Chiefs of Staff (2020)**. *Joint Publication 6-0: Joint Communications System*. Washington, DC: Department of Defense.
3. **NATO Standardization Office (2017)**. *MIL-STD-2525D / APP-6(D): Joint Military Symbology*. Brussels: North Atlantic Treaty Organization.
4. **Defense Science Board (2021)**. *Report on Electronic Warfare and Resilient Communications in Contested Environments*. Washington, DC: Office of the Under Secretary of Defense for Acquisition and Sustainment.

---

## 📄 License

This project is licensed under the **MIT License**.

Built for defense research, operational experimentation, and military staff decision-making training.
