/**
 * Instructor EXCON Console Panel
 * Provides God-Mode Ground Truth controls, manual inject triggering,
 * jamming radius overrides, participant monitoring, and decision tracking.
 */

class InstructorConsole {
  constructor(containerId, onAction) {
    this.container = document.getElementById(containerId);
    this.onAction = onAction;
    this.executedInjectIds = new Set();
  }

  updateState(stateData) {
    if (!this.container) return;

    const injects = stateData.injects || [];
    const executed = stateData.executed_injects || [];
    const participants = stateData.participants || [];
    const metrics = stateData.metrics || {};
    const orders = stateData.orders || [];

    this.executedInjectIds = new Set(executed);

    // 1. Participant Monitor
    let participantsHtml = "";
    if (participants.length > 0) {
      participantsHtml = `
        <div style="background:#ffffff;border:1.5px solid #000000;padding:8px;border-radius:4px;margin-bottom:10px;box-shadow:2px 2px 0px rgba(0,0,0,0.06);">
          <div style="font-size:10px;color:#000000;font-weight:800;margin-bottom:4px;display:flex;justify-content:space-between;">
            <span>ACTIVE OPERATORS (${participants.length})</span>
            <span style="color:#52525b;font-size:9px;">ROOM: ${stateData.scenario_id ? stateData.scenario_id.toUpperCase() : "LIVE"}</span>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:4px;">
            ${participants.map(p => `
              <span style="font-size:9px;background:#f4f4f5;border:1px solid #000000;padding:2px 6px;border-radius:3px;color:#000000;">
                <strong style="color:${p.is_ready ? '#15803d' : '#b45309'};">${p.is_ready ? '✓' : '…'}</strong> ${this.escapeHtml(p.callsign)} [${p.role}]
              </span>
            `).join("")}
          </div>
        </div>
      `;
    }

    // 2. Cognitive & Decision Telemetry
    let metricsHtml = `
      <div style="background:#ffffff;border:1.5px solid #000000;padding:8px;border-radius:4px;margin-bottom:10px;box-shadow:2px 2px 0px rgba(0,0,0,0.06);">
        <div style="font-size:10px;color:#000000;font-weight:800;margin-bottom:4px;">LIVE COGNITIVE & DECISION TELEMETRY</div>
        <div style="display:flex;justify-content:space-between;font-size:10px;color:#000000;">
          <span>Command Score: <strong style="color:${metrics.command_effectiveness_score >= 75 ? '#15803d' : '#b45309'};">${metrics.command_effectiveness_score || 100}%</strong></span>
          <span>Orders Logged: <strong>${metrics.total_orders_issued || 0}</strong></span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:10px;margin-top:2px;color:#000000;">
          <span>EW Reaction Time: <strong>${metrics.first_jamming_reaction_sec || 0}s</strong></span>
          <span>Divergence Errors: <strong style="color:${metrics.spoofed_divergence_actions > 0 ? '#b91c1c' : '#15803d'};">${metrics.spoofed_divergence_actions || 0}</strong></span>
        </div>
      </div>
    `;

    // 3. Ad-Hoc Injects Panel (Contradictory Intel, Cyber, GPS Spoof)
    let adhocHtml = `
      <div style="background:#ffffff;border:1.5px solid #000000;padding:8px;border-radius:4px;margin-bottom:10px;box-shadow:2px 2px 0px rgba(0,0,0,0.06);">
        <div style="font-size:10px;color:#000000;font-weight:800;margin-bottom:6px;">⚡ AD-HOC DEGRADATION & CONTRADICTORY INJECTS</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <button id="btnInjectContradictory" class="btn-header" style="font-size:9px;border:1.5px solid #b45309;color:#b45309;background:#fff;padding:6px 4px;text-align:center;">
            ⚡ CONTRADICTORY SITREP
          </button>
          <button id="btnInjectCyberBlackout" class="btn-header" style="font-size:9px;border:1.5px solid #b91c1c;color:#b91c1c;background:#fff;padding:6px 4px;text-align:center;">
            🛑 CYBER BFT FREEZE (60s)
          </button>
        </div>
      </div>
    `;

    // 4. Direct Jammer Controls
    const jammers = stateData.active_jammers || [];
    let jammerControlsHtml = `
      <div style="margin-bottom:10px;">
        <div style="font-size:10px;color:#000000;font-weight:800;margin-bottom:6px;">DIRECT EW CONTROLS</div>
        <div style="display:flex;flex-direction:column;gap:6px;">
    `;
    for (const j of jammers) {
      jammerControlsHtml += `
        <div style="display:flex;justify-content:space-between;align-items:center;background:#ffffff;padding:6px 8px;border-radius:3px;border:1.5px solid #000000;box-shadow:2px 2px 0px rgba(0,0,0,0.05);">
          <div>
            <div style="font-size:10px;font-weight:800;color:#000000;">${this.escapeHtml(j.name)}</div>
            <div style="font-size:8px;color:#52525b;">${j.frequency_band} | Radius: ${Math.round(j.radius)}m ${j.spoofing ? '| GPS SPOOFER' : ''}</div>
          </div>
          <button class="btn-header" onclick="window.instructorConsole.toggleJammer('${j.id}', ${!j.active})" 
                  style="font-size:9px;border:1.5px solid ${j.active ? '#b91c1c' : '#15803d'};color:${j.active ? '#b91c1c' : '#15803d'};">
            ${j.active ? "DEACTIVATE" : "ACTIVATE"}
          </button>
        </div>
      `;
    }
    jammerControlsHtml += `</div></div>`;

    // 5. Recent Trainee Decisions & Rationale
    let decisionsHtml = "";
    if (orders.length > 0) {
      decisionsHtml = `
        <div style="margin-bottom:10px;background:#ffffff;border:1.5px solid #000000;padding:8px;border-radius:4px;box-shadow:2px 2px 0px rgba(0,0,0,0.06);">
          <div style="font-size:10px;color:#000000;font-weight:800;margin-bottom:6px;">LIVE DECISION & RATIONALE AUDIT</div>
          <div style="max-height:130px;overflow-y:auto;display:flex;flex-direction:column;gap:4px;">
            ${orders.slice(-5).reverse().map(o => `
              <div style="background:#f4f4f5;border-left:3px solid #000000;padding:4px 6px;font-size:9px;">
                <div style="display:flex;justify-content:space-between;color:#52525b;">
                  <span style="font-weight:800;color:#000000;">[${o.issuer_role}] &rarr; ${o.unit_id}</span>
                  <span style="color:#b45309;font-weight:700;">${o.order_type}</span>
                </div>
                ${o.rationale ? `<div style="color:#000000;margin-top:2px;font-style:italic;">"${this.escapeHtml(o.rationale)}"</div>` : ''}
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }

    // 6. Scripted Injects
    let injectsHtml = "";
    for (const inj of injects) {
      const isDone = this.executedInjectIds.has(inj.id);
      injectsHtml += `
        <div class="inject-card" style="margin-bottom:6px;">
          <div class="inject-title">${this.escapeHtml(inj.title)} (T+${Math.floor(inj.sim_time)}s)</div>
          <div class="inject-desc">${this.escapeHtml(inj.description)}</div>
          <div style="font-size:9px;color:#52525b;margin-bottom:4px;"><em>Note: ${this.escapeHtml(inj.instructor_note || "N/A")}</em></div>
          <button class="btn-inject ${isDone ? "executed" : ""}" 
                  data-inject-id="${inj.id}" 
                  ${isDone ? "disabled" : ""}>
            ${isDone ? "EXECUTED" : "TRIGGER INJECT NOW"}
          </button>
        </div>
      `;
    }

    this.container.innerHTML = `
      ${participantsHtml}
      ${metricsHtml}
      ${adhocHtml}
      ${jammerControlsHtml}
      ${decisionsHtml}
      <div style="font-size:10px;color:#000000;font-weight:800;margin-bottom:6px;">SCRIPTED SCENARIO INJECTS</div>
      ${injectsHtml}
    `;

    // Bind scripted inject buttons
    const btns = this.container.querySelectorAll(".btn-inject");
    btns.forEach(btn => {
      btn.addEventListener("click", () => {
        const iid = btn.dataset.injectId;
        if (iid && this.onAction) {
          this.onAction({ sub_action: "TRIGGER_INJECT", inject_id: iid });
        }
      });
    });

    // Bind ad-hoc buttons
    const btnContra = this.container.querySelector("#btnInjectContradictory");
    if (btnContra) {
      btnContra.addEventListener("click", () => {
        if (this.onAction) {
          this.onAction({ sub_action: "CONTRADICTORY_INTEL", channel: "TAC-1" });
          if (window.tacticalAudio) window.tacticalAudio.playAlertPing(true);
        }
      });
    }

    const btnCyber = this.container.querySelector("#btnInjectCyberBlackout");
    if (btnCyber) {
      btnCyber.addEventListener("click", () => {
        if (this.onAction) {
          this.onAction({
            sub_action: "CYBER_ATTACK",
            target_role: "ALL",
            subsystem: "BFT",
            disruption_type: "BLACKOUT",
            duration: 60.0
          });
          if (window.tacticalAudio) window.tacticalAudio.playAlertPing(true);
        }
      });
    }
  }

  toggleJammer(jammerId, newState) {
    if (this.onAction) {
      this.onAction({ sub_action: "TOGGLE_JAMMER", jammer_id: jammerId, active: newState });
    }
  }

  escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.innerText = str;
    return div.innerHTML;
  }
}

window.InstructorConsole = InstructorConsole;
