/**
 * Main Application Coordinator
 * Manages WebSocket state sync, role switching, dynamic UI layout,
 * and tactical order modal interactions.
 */

class TacticalApp {
  constructor() {
    this.ws = null;
    this.currentRole = "COMMANDER";
    this.simState = null;
    this.pendingOrder = null; // { unitId, worldPos }

    this.map = null;
    this.comms = null;
    this.flir = null;
    this.spectrum = null;
    this.instructor = null;

    this.init();
  }

  init() {
    // Initialize components
    this.map = new TacticalMap("tacticalCanvas");
    
    this.comms = new CommsTerminal("commsTerminal", (channel, content, msgType) => {
      this.sendMessage({
        action: "TRANSMIT_COMMS",
        channel: channel,
        content: content,
        msg_type: msgType
      });
    });

    this.flir = new FLIRDroneSimulator("flirCanvas");
    this.flirFull = new FLIRDroneSimulator("flirFullCanvas");

    this.spectrum = new SpectrumAnalyzer("spectrumCanvas");
    this.spectrumFull = new SpectrumAnalyzer("spectrumFullCanvas");
    
    this.instructor = new InstructorConsole("instructorConsolePanel", (actionData) => {
      this.sendMessage({
        action: "INSTRUCTOR_ACTION",
        ...actionData
      });
    });
    this.instructorFull = new InstructorConsole("exconFullPanel", (actionData) => {
      this.sendMessage({
        action: "INSTRUCTOR_ACTION",
        ...actionData
      });
    });
    window.instructorConsole = this.instructor;

    // Initialize In-App Live AAR Viewer
    this.aarViewer = new AARViewer("aarViewerContainer");
    window.aarViewer = this.aarViewer;

    this.currentScreen = "LOGIN"; // LOGIN, LOBBY, SIMULATION
    this.userProfile = {
      callsign: "WARLORD-6",
      userType: "TRAINEE",
      role: "COMMANDER",
      roomCode: "ALPHA-6"
    };

    // Initialize Login Screen Controls
    this.initLoginScreen();

    // Initialize Lobby & Scenario Config Controls
    this.initLobbyScreen();

    // View Navigation Tabs
    const viewTabs = document.querySelectorAll(".view-tab");
    viewTabs.forEach(tab => {
      tab.addEventListener("click", () => {
        const viewName = tab.dataset.view;
        this.switchView(viewName);
      });
    });

    // Quick AAR button in top bar
    const btnNavAAR = document.getElementById("btnNavAAR");
    if (btnNavAAR) {
      btnNavAAR.addEventListener("click", () => {
        this.switchView("AAR");
      });
    }

    // Manual End Exercise (Instructor only)
    const btnEndSimManual = document.getElementById("btnEndSimManual");
    if (btnEndSimManual) {
      btnEndSimManual.addEventListener("click", () => {
        if (confirm("End current simulation exercise and generate AAR report for all participants?")) {
          this.sendMessage({ action: "END_EXERCISE" });
        }
      });
    }

    // Bind map order trigger
    this.map.onOrderRequested = (unitId, worldPos) => {
      this.openOrderModal(unitId, worldPos);
    };

    this.map.onJammerMoved = (jammerId, newX, newY) => {
      this.sendMessage({
        action: "INSTRUCTOR_ACTION",
        sub_action: "MOVE_JAMMER",
        jammer_id: jammerId,
        x: newX,
        y: newY
      });
    };

    // Role switcher dropdown
    const roleSelect = document.getElementById("roleSelect");
    if (roleSelect) {
      roleSelect.addEventListener("change", (e) => {
        this.currentRole = e.target.value;
        this.onRoleChanged(this.currentRole);
      });
    }

    // Audio mute toggle
    const audioBtn = document.getElementById("btnToggleAudio");
    if (audioBtn) {
      audioBtn.addEventListener("click", () => {
        if (!window.tacticalAudio.initialized) window.tacticalAudio.init();
        const isMuted = window.tacticalAudio.toggleMute();
        audioBtn.textContent = isMuted ? "AUDIO: OFF" : "AUDIO: ON";
        audioBtn.style.color = isMuted ? "var(--text-muted)" : "var(--c2-blue)";
      });
    }

    // Modal controls
    const btnCancel = document.getElementById("btnCancelOrder");
    const btnConfirm = document.getElementById("btnConfirmOrder");
    if (btnCancel) btnCancel.addEventListener("click", () => this.closeOrderModal());
    if (btnConfirm) btnConfirm.addEventListener("click", () => this.submitOrder());

    // Specialist station buttons
    const btnToggleFHSS = document.getElementById("btnToggleFHSS");
    if (btnToggleFHSS) {
      btnToggleFHSS.addEventListener("click", () => {
        const active = this.spectrumFull.toggleFrequencyHopping();
        this.spectrum.frequencyHoppingActive = active;
        btnToggleFHSS.textContent = active ? "DISABLE FHSS" : "ENABLE FHSS (1,200 hops/sec)";
        btnToggleFHSS.style.borderColor = active ? "#ef4444" : "#4ade80";
        btnToggleFHSS.style.color = active ? "#ef4444" : "#4ade80";
        if (window.tacticalAudio) window.tacticalAudio.playAlertPing();
      });
    }

    const btnArmLaser = document.getElementById("btnArmLaser");
    if (btnArmLaser) {
      btnArmLaser.addEventListener("click", () => {
        btnArmLaser.textContent = "TARGET DESIGNATED [1688]";
        btnArmLaser.style.background = "#22c55e";
        if (window.tacticalAudio) window.tacticalAudio.playAlertPing(true);
        setTimeout(() => {
          btnArmLaser.textContent = "DESIGNATE TARGET";
          btnArmLaser.style.background = "";
        }, 3000);
      });
    }

    const btnSimPause = document.getElementById("btnSimPause");
    if (btnSimPause) {
      btnSimPause.addEventListener("click", () => {
        const isPaused = btnSimPause.textContent === "RESUME SIM";
        btnSimPause.textContent = isPaused ? "PAUSE SIM" : "RESUME SIM";
        this.sendMessage({
          action: "INSTRUCTOR_ACTION",
          sub_action: "SIM_CONTROL",
          command: isPaused ? "RESUME" : "PAUSE"
        });
      });
    }

    const btnSimReset = document.getElementById("btnSimReset");
    if (btnSimReset) {
      btnSimReset.addEventListener("click", () => {
        if (confirm("Reset exercise to initial state?")) {
          this.sendMessage({
            action: "INSTRUCTOR_ACTION",
            sub_action: "SIM_CONTROL",
            command: "RESET"
          });
        }
      });
    }

    // Connect WebSocket
    this.connectWebSocket();

    // First click user gesture to unlock Web Audio API
    document.addEventListener("click", () => {
      if (window.tacticalAudio && !window.tacticalAudio.initialized) {
        window.tacticalAudio.init();
      }
    }, { once: true });
  }

  initLoginScreen() {
    const btnTrainee = document.getElementById("typeTrainee");
    const btnInstructor = document.getElementById("typeInstructor");
    const roleGroup = document.getElementById("loginRoleGroup");
    const callsignInput = document.getElementById("loginCallsign");
    const roleSelect = document.getElementById("loginRoleSelect");
    const roomInput = document.getElementById("loginRoomCode");
    const btnSubmit = document.getElementById("btnLoginSubmit");

    if (btnTrainee && btnInstructor) {
      btnTrainee.addEventListener("click", () => {
        btnTrainee.classList.add("active");
        btnInstructor.classList.remove("active");
        this.userProfile.userType = "TRAINEE";
        if (roleGroup) roleGroup.style.display = "block";
        if (callsignInput) callsignInput.value = "WARLORD-6";
      });

      btnInstructor.addEventListener("click", () => {
        btnInstructor.classList.add("active");
        btnTrainee.classList.remove("active");
        this.userProfile.userType = "INSTRUCTOR";
        if (roleGroup) roleGroup.style.display = "none";
        if (callsignInput) callsignInput.value = "EXCON-LEAD";
      });
    }

    if (btnSubmit) {
      btnSubmit.addEventListener("click", () => {
        this.userProfile.callsign = callsignInput?.value?.trim() || "OPERATOR-1";
        this.userProfile.role = this.userProfile.userType === "INSTRUCTOR" ? 
          "INSTRUCTOR" : (roleSelect?.value || "COMMANDER");
        this.userProfile.roomCode = roomInput?.value?.trim() || "ALPHA-6";
        this.currentRole = this.userProfile.role;

        // Send login message to WebSocket
        this.sendMessage({
          action: "LOGIN",
          callsign: this.userProfile.callsign,
          user_type: this.userProfile.userType,
          role: this.userProfile.role,
          room_code: this.userProfile.roomCode
        });

        // Switch to Lobby Screen
        this.switchScreen("LOBBY");
      });
    }

    const btnInstant = document.getElementById("btnInstantLaunch");
    if (btnInstant) {
      btnInstant.addEventListener("click", () => {
        this.userProfile.callsign = callsignInput?.value?.trim() || "WARLORD-6";
        this.userProfile.role = this.userProfile.userType === "INSTRUCTOR" ? 
          "INSTRUCTOR" : (roleSelect?.value || "COMMANDER");
        this.userProfile.roomCode = roomInput?.value?.trim() || "ALPHA-6";
        this.currentRole = this.userProfile.role;

        this.sendMessage({
          action: "LOGIN",
          callsign: this.userProfile.callsign,
          user_type: this.userProfile.userType,
          role: this.userProfile.role,
          room_code: this.userProfile.roomCode
        });

        this.sendMessage({ action: "START_EXERCISE" });
        this.switchScreen("SIMULATION");
      });
    }
  }

  initLobbyScreen() {
    const btnLeave = document.getElementById("btnLeaveRoom");
    if (btnLeave) {
      btnLeave.addEventListener("click", () => {
        this.switchScreen("LOGIN");
      });
    }

    const btnBackToLobby = document.getElementById("btnBackToLobby");
    if (btnBackToLobby) {
      btnBackToLobby.addEventListener("click", () => {
        this.switchScreen("LOBBY");
      });
    }

    const btnTestComms = document.getElementById("btnTestCommsLobby");
    if (btnTestComms) {
      btnTestComms.addEventListener("click", () => {
        if (window.tacticalAudio) {
          window.tacticalAudio.playRadioSquelch(false);
          setTimeout(() => window.tacticalAudio.playAlertPing(), 250);
        }
      });
    }

    const btnReady = document.getElementById("btnToggleReady");
    if (btnReady) {
      btnReady.addEventListener("click", () => {
        const isReady = btnReady.textContent.includes("UNMARK");
        btnReady.textContent = isReady ? "✓ MARK READY FOR DEPLOYMENT" : "✕ UNMARK READY";
        btnReady.style.background = isReady ? "#15803d" : "#78350f";
        this.sendMessage({ action: "TOGGLE_READY" });
      });
    }

    // Instructor Scenario Configuration Controls
    const scenarioSelect = document.getElementById("configScenarioSelect");
    const durationSelect = document.getElementById("configDurationSelect");
    const diffSelect = document.getElementById("configDifficultySelect");
    const maxUsersSelect = document.getElementById("configMaxUsersSelect");
    const btnStart = document.getElementById("btnStartSimulation");

    const sendConfigUpdate = () => {
      this.sendMessage({
        action: "UPDATE_CONFIG",
        config: {
          scenario_id: scenarioSelect?.value,
          duration_minutes: durationSelect?.value,
          difficulty: diffSelect?.value,
          max_users: maxUsersSelect?.value
        }
      });
    };

    if (scenarioSelect) scenarioSelect.addEventListener("change", sendConfigUpdate);
    if (durationSelect) durationSelect.addEventListener("change", sendConfigUpdate);
    if (diffSelect) diffSelect.addEventListener("change", sendConfigUpdate);
    if (maxUsersSelect) maxUsersSelect.addEventListener("change", sendConfigUpdate);

    if (btnStart) {
      btnStart.addEventListener("click", () => {
        sendConfigUpdate();
        this.sendMessage({ action: "START_EXERCISE" });
      });
    }
  }

  switchScreen(screenName) {
    this.currentScreen = screenName;
    const screens = document.querySelectorAll(".app-screen");
    screens.forEach(s => s.classList.remove("active"));

    if (screenName === "LOGIN") {
      document.getElementById("screenLogin")?.classList.add("active");
    } else if (screenName === "LOBBY") {
      document.getElementById("screenLobby")?.classList.add("active");
      this.updateLobbyView();
    } else if (screenName === "SIMULATION") {
      document.getElementById("screenSimulation")?.classList.add("active");
      setTimeout(() => {
        this.map.resize();
        this.flir.resize();
        this.flirFull.resize();
        this.spectrum.resize();
        this.spectrumFull.resize();
      }, 60);
    }
  }

  updateLobbyView() {
    const isInst = this.userProfile.userType === "INSTRUCTOR";
    const instPanel = document.getElementById("lobbyInstructorConfig");
    const traineePanel = document.getElementById("lobbyTraineeBriefing");
    const userCallsignEl = document.getElementById("lobbyUserCallsign");
    const roomBadge = document.getElementById("lobbyRoomBadge");
    const roomDisp = document.getElementById("lobbyRoomDisplay");
    const topRoomBadge = document.getElementById("topRoomBadge");
    const btnEndSimManual = document.getElementById("btnEndSimManual");

    if (instPanel) instPanel.style.display = isInst ? "flex" : "none";
    if (traineePanel) traineePanel.style.display = isInst ? "none" : "flex";
    if (userCallsignEl) userCallsignEl.textContent = `${this.userProfile.callsign} (${this.userProfile.userType})`;
    if (roomBadge) roomBadge.textContent = this.userProfile.roomCode;
    if (roomDisp) roomDisp.textContent = this.userProfile.roomCode;
    if (topRoomBadge) topRoomBadge.textContent = `ROOM: ${this.userProfile.roomCode}`;
    if (btnEndSimManual) btnEndSimManual.style.display = isInst ? "inline-block" : "none";
  }

  switchView(viewName) {
    const tabs = document.querySelectorAll(".view-tab");
    tabs.forEach(t => {
      t.classList.toggle("active", t.dataset.view === viewName);
    });

    const sections = document.querySelectorAll(".view-section");
    sections.forEach(s => s.classList.remove("active"));

    if (viewName === "COCKPIT") {
      document.getElementById("viewCockpit")?.classList.add("active");
      this.map.resize();
    } else if (viewName === "FLIR") {
      document.getElementById("viewFLIR")?.classList.add("active");
      this.flirFull.resize();
    } else if (viewName === "SPECTRUM") {
      document.getElementById("viewSpectrum")?.classList.add("active");
      this.spectrumFull.resize();
    } else if (viewName === "EXCON") {
      document.getElementById("viewEXCON")?.classList.add("active");
      if (this.simState) this.instructorFull.updateState(this.simState);
    } else if (viewName === "AAR") {
      document.getElementById("viewAAR")?.classList.add("active");
      this.aarViewer.fetchAndRender();
    }
  }

  connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    console.log("[WS] Connecting to tactical server at:", wsUrl);
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log("[WS] Connected to tactical simulation engine.");
      this.sendMessage({ action: "SELECT_ROLE", role: this.currentRole });
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "STATE_UPDATE") {
          this.handleStateUpdate(msg.data);
        }
      } catch (e) {
        console.error("[WS] Error parsing state message:", e);
      }
    };

    this.ws.onclose = () => {
      console.warn("[WS] Disconnected. Retrying in 2 seconds...");
      setTimeout(() => this.connectWebSocket(), 2000);
    };
  }

  sendMessage(payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    }
  }

  onRoleChanged(newRole) {
    this.sendMessage({ action: "SELECT_ROLE", role: newRole });
    this.map.currentRole = newRole;

    // Adjust UI Panels
    const specHeader = document.getElementById("specialistHeader");
    const flirBox = document.getElementById("flirContainer");
    const specBox = document.getElementById("spectrumContainer");
    const instBox = document.getElementById("instructorContainer");

    if (flirBox) flirBox.style.display = "none";
    if (specBox) specBox.style.display = "none";
    if (instBox) instBox.style.display = "none";

    if (newRole === "JTAC_INTEL") {
      if (specHeader) specHeader.textContent = "UAV FLIR SENSOR RECON LINK";
      if (flirBox) flirBox.style.display = "block";
      this.flir.resize();
    } else if (newRole === "EW_CYBER") {
      if (specHeader) specHeader.textContent = "TACTICAL RF SPECTRUM & CYBER";
      if (specBox) specBox.style.display = "block";
      this.spectrum.resize();
    } else if (newRole === "INSTRUCTOR") {
      if (specHeader) specHeader.textContent = "EXCON SCENARIO & INJECT CONTROLLER";
      if (instBox) instBox.style.display = "block";
    } else {
      // Default to FLIR mini view for Commander
      if (specHeader) specHeader.textContent = "BFT & RECON FEED";
      if (flirBox) flirBox.style.display = "block";
      this.flir.resize();
    }
  }

  handleStateUpdate(state) {
    this.simState = state;

    // Automatic Screen Transitions based on exercise status
    if (state.exercise_status === "RUNNING" && this.currentScreen === "LOBBY") {
      this.switchScreen("SIMULATION");
    } else if (state.exercise_status === "COMPLETED" && this.currentScreen === "SIMULATION") {
      this.switchView("AAR");
    }

    // Sync Lobby Roster & Briefing Info
    if (this.currentScreen === "LOBBY") {
      const rosterBody = document.getElementById("rosterTableBody");
      const rosterCount = document.getElementById("rosterCount");
      if (rosterBody && state.participants) {
        rosterBody.innerHTML = state.participants.map(p => `
          <tr>
            <td><strong>${this.escapeHtml(p.callsign)}</strong></td>
            <td>${this.escapeHtml(p.role)}</td>
            <td>${this.escapeHtml(p.user_type)}</td>
            <td><span class="${p.is_ready ? 'badge-ready' : 'badge-unready'}">${p.is_ready ? 'READY' : 'PREPARING'}</span></td>
          </tr>
        `).join("");
        if (rosterCount) rosterCount.textContent = state.participants.length;
      }

      const bTitle = document.getElementById("briefingTitle");
      if (bTitle && state.scenario_title) {
        bTitle.textContent = state.scenario_title;
      }

      const bTheater = document.getElementById("briefingTheater");
      if (bTheater && state.scenario_theater) {
        bTheater.textContent = state.scenario_theater;
      }

      const bObj = document.getElementById("briefingObjectivesList");
      const bThreat = document.getElementById("briefingThreatText");
      if (state.scenario_id === "urban_aegis") {
        if (bObj) {
          bObj.innerHTML = `
            <li>Advance assault elements through high-density urban corridors.</li>
            <li>Counter low-altitude commercial drone spoofers and multipath RF signal loss.</li>
            <li>Maintain coordinated sectors of fire when VHF voice repeaters are suppressed.</li>
          `;
        }
        if (bThreat) {
          bThreat.textContent = "Hostile motorized squads operating portable directional jammers from building rooftops. Concealed Kornet ATGM teams at intersection corners.";
        }
      } else {
        if (bObj) {
          bObj.innerHTML = `
            <li>Advance friendly mechanized forces to secure key highway pass junction.</li>
            <li>Anticipate hostile Krasukha-4 radio suppression and GPS ephemeris spoofing.</li>
            <li>Exercise mission command when digital BFT or voice nets drop.</li>
          `;
        }
        if (bThreat) {
          bThreat.textContent = "Enemy motorized battalion advancing from East. High probability of directional VHF voice jamming and decoy thermal radar reflectors.";
        }
      }
    }

    // Update Header Telemetry
    this.updateHeader(state);

    // Update Map
    this.map.updateState(state);

    // Update Comms
    if (state.messages) {
      this.comms.updateMessages(state.messages);
    }

    // Update FLIR & Spectrum (Mini and Dedicated full views)
    const interferencePct = state.network_status?.interference_pct || 0;
    this.flir.updateState(state.units, interferencePct / 100);
    if (this.flirFull) this.flirFull.updateState(state.units, interferencePct / 100);

    this.spectrum.updateState(state.active_jammers || []);
    if (this.spectrumFull) this.spectrumFull.updateState(state.active_jammers || []);

    // Update Instructor Consoles (Mini and Dedicated full views)
    if (this.currentRole === "INSTRUCTOR" || document.getElementById("viewEXCON")?.classList.contains("active")) {
      this.instructor.updateState(state);
      if (this.instructorFull) this.instructorFull.updateState(state);
    }

    // Update FLIR Jam Alert badge
    const flirJamAlert = document.getElementById("flirJamAlert");
    if (flirJamAlert) {
      flirJamAlert.style.display = interferencePct > 20 ? "inline" : "none";
    }

    // Play periodic audio jamming static if interference is high
    if (interferencePct > 35 && Math.random() < 0.15) {
      if (window.tacticalAudio) {
        window.tacticalAudio.playJammingCrackle(interferencePct / 100);
      }
    }
  }

  updateHeader(state) {
    const simTimeEl = document.getElementById("telemetrySimTime");
    const remainingEl = document.getElementById("telemetryRemaining");
    const voiceStatusEl = document.getElementById("telemetryVoice");
    const voiceDot = document.getElementById("voiceDot");
    const bftStatusEl = document.getElementById("telemetryBFT");
    const bftDot = document.getElementById("bftDot");
    const latencyEl = document.getElementById("telemetryLatency");

    if (simTimeEl) {
      const t = Math.floor(state.sim_time || 0);
      const mins = Math.floor(t / 60);
      const secs = t % 60;
      simTimeEl.textContent = `T+${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }

    if (remainingEl && state.time_remaining_sec !== undefined) {
      const tr = Math.max(0, Math.floor(state.time_remaining_sec));
      const rm = Math.floor(tr / 60);
      const rs = tr % 60;
      remainingEl.textContent = `${rm.toString().padStart(2, "0")}:${rs.toString().padStart(2, "0")}`;
      if (tr <= 60) {
        remainingEl.style.color = "var(--c2-red)";
      } else {
        remainingEl.style.color = "#fde68a";
      }
    }

    const net = state.network_status || {};
    if (voiceStatusEl) {
      voiceStatusEl.textContent = net.voice || "ONLINE";
      if (net.voice === "ONLINE") {
        voiceDot.className = "indicator-dot";
      } else if (net.voice?.includes("DEGRADED")) {
        voiceDot.className = "indicator-dot warning";
      } else {
        voiceDot.className = "indicator-dot danger";
      }
    }

    if (bftStatusEl) {
      bftStatusEl.textContent = net.bft || "ONLINE";
      if (net.bft === "ONLINE") {
        bftDot.className = "indicator-dot";
      } else if (net.bft?.includes("INTERMITTENT")) {
        bftDot.className = "indicator-dot warning";
      } else {
        bftDot.className = "indicator-dot danger";
      }
    }

    if (latencyEl) {
      latencyEl.textContent = `${net.latency_ms || 25}ms`;
    }
  }

  openOrderModal(unitId, worldPos) {
    this.pendingOrder = { unitId, worldPos };
    const modal = document.getElementById("orderModal");
    const modalTargetEl = document.getElementById("modalTargetCoords");
    const modalUnitEl = document.getElementById("modalUnitCallsign");

    const unit = this.simState?.units?.[unitId];
    if (modalUnitEl) modalUnitEl.textContent = unit?.callsign || unitId;

    if (modalTargetEl) {
      const easting = Math.floor(worldPos.x * 10);
      const northing = Math.floor(worldPos.y * 10);
      modalTargetEl.textContent = `38T KM ${easting.toString().padStart(4, "0")} ${northing.toString().padStart(4, "0")}`;
    }

    if (modal) modal.style.display = "flex";
  }

  closeOrderModal() {
    const modal = document.getElementById("orderModal");
    if (modal) modal.style.display = "none";
    this.pendingOrder = null;
  }

  submitOrder() {
    if (!this.pendingOrder) return;
    const orderType = document.getElementById("orderTypeSelect")?.value || "MOVE";
    const rationale = document.getElementById("orderRationaleInput")?.value || "";

    this.sendMessage({
      action: "ISSUE_ORDER",
      unit_id: this.pendingOrder.unitId,
      order_type: orderType,
      target: { x: this.pendingOrder.worldPos.x, y: this.pendingOrder.worldPos.y },
      rationale: rationale
    });

    if (window.tacticalAudio) {
      window.tacticalAudio.playAlertPing();
    }

    // Reset rationale input
    const input = document.getElementById("orderRationaleInput");
    if (input) input.value = "";

    this.closeOrderModal();
  }

  escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.innerText = str;
    return div.innerHTML;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new TacticalApp();
});
