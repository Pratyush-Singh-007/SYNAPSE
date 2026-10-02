/**
 * In-App After Action Review (AAR) Viewer
 * High-Contrast White and Black Edition
 * Embedded live debrief suite rendering real-time performance scores,
 * divergence metrics, and an interactive decision timeline without leaving the app.
 */

class AARViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.filterSeverity = "ALL";
    this.cachedData = null;
  }

  async fetchAndRender() {
    try {
      const room = window.app?.userProfile?.roomCode || "ALPHA-6";
      const resp = await fetch(`/api/aar.json?room=${encodeURIComponent(room)}`);
      if (!resp.ok) return;
      const data = await resp.json();
      this.cachedData = data;
      this.render(data);
    } catch (e) {
      console.warn("[AAR] Error fetching live AAR:", e);
    }
  }

  render(data) {
    if (!this.container || !data) return;
    const metrics = data.metrics || {};
    const events = data.events || [];
    const room = window.app?.userProfile?.roomCode || "ALPHA-6";

    const filteredEvents = events.filter(e => {
      if (this.filterSeverity === "ALL") return true;
      if (this.filterSeverity === "CRITICAL") return e.severity === "CRITICAL";
      if (this.filterSeverity === "ORDERS") return e.event_type === "ORDER_ISSUED";
      if (this.filterSeverity === "COMMS") return e.event_type.includes("COMMS") || e.event_type.includes("JAMMER");
      return true;
    });

    let eventsHtml = "";
    for (const e of filteredEvents.slice().reverse()) {
      let sevColor = "#000000";
      if (e.severity === "CRITICAL") {
        sevColor = "#b91c1c";
      } else if (e.severity === "WARNING") {
        sevColor = "#b45309";
      }

      let divergenceTag = "";
      if (e.divergence_metric > 40) {
        divergenceTag = `<span style="background:#fef2f2;border:1px solid #b91c1c;color:#b91c1c;padding:2px 6px;border-radius:3px;font-size:9px;font-weight:800;margin-left:8px;">TARGET DIVERGENCE: ${Math.round(e.divergence_metric)}m</span>`;
      }

      let rationaleBlock = "";
      if (e.rationale) {
        rationaleBlock = `
          <div style="margin-top:6px;padding:6px 10px;background:#f4f4f5;border-left:3px solid #000000;font-size:11px;color:#000000;border-radius:0 4px 4px 0;">
            <strong style="color:#000000;">Commander Rationale:</strong> "${this.escapeHtml(e.rationale)}"
          </div>
        `;
      }

      const mins = Math.floor(e.sim_time / 60);
      const secs = Math.floor(e.sim_time % 60);
      const timeStr = `T+${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

      eventsHtml += `
        <div style="background:#ffffff;border:1.5px solid #000000;border-left:5px solid ${sevColor};padding:10px 14px;border-radius:4px;margin-bottom:8px;box-shadow:2px 2px 0px rgba(0,0,0,0.06);">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:10px;color:#52525b;margin-bottom:4px;">
            <div>
              <span style="font-family:monospace;font-weight:800;color:#000000;">${timeStr}</span> &bull;
              <span style="background:#000000;color:#ffffff;padding:2px 6px;border-radius:3px;font-weight:800;">${e.actor}</span>
              ${divergenceTag}
            </div>
            <span style="font-size:9px;font-weight:800;color:${sevColor}">${e.severity}</span>
          </div>
          <div style="font-weight:800;color:#000000;font-size:12px;">${this.escapeHtml(e.title)}</div>
          <div style="color:#27272a;font-size:11px;margin-top:2px;">${this.escapeHtml(e.description)}</div>
          ${rationaleBlock}
        </div>
      `;
    }

    this.container.innerHTML = `
      <div style="max-width:1100px;margin:0 auto;padding:16px;background:#ffffff;">
        <!-- REPORT TOP BANNER -->
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #000000;padding-bottom:14px;margin-bottom:16px;">
          <div>
            <h2 style="font-size:18px;color:#000000;font-weight:900;letter-spacing:1px;font-family:monospace;margin:0;">
              AFTER ACTION REVIEW // EXERCISE DEBRIEF
            </h2>
            <div style="font-size:11px;color:#52525b;margin-top:4px;">
              Scenario: <strong style="color:#000000;">${metrics.scenario_title || "Operation Broken Uplink"}</strong> &bull; Total Events Logged: <strong style="color:#000000;">${metrics.total_events_logged || 0}</strong>
            </div>
          </div>
          <div style="display:flex;gap:8px;">
            <a href="/api/aar/download-pdf?room=${encodeURIComponent(room)}" class="btn-header btn-aar" style="font-size:10px;text-decoration:none;">
              📥 DOWNLOAD PDF REPORT
            </a>
            <a href="/api/aar/download-report?room=${encodeURIComponent(room)}" class="btn-header" style="font-size:10px;text-decoration:none;">
              📄 DOWNLOAD HTML
            </a>
            <button onclick="window.print()" class="btn-header" style="font-size:10px;">
              🖨️ PRINT / SAVE AS PDF
            </button>
            <button onclick="window.aarViewer.fetchAndRender()" class="btn-header" style="font-size:10px;">
              🔄 REFRESH
            </button>
          </div>
        </div>

        <!-- SCORE METRICS GRID -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(170px, 1fr));gap:12px;margin-bottom:20px;">
          <div style="background:#ffffff;border:2px solid #000000;padding:12px;border-radius:6px;box-shadow:3px 3px 0px rgba(0,0,0,0.08);">
            <div style="font-size:10px;color:#52525b;font-weight:700;text-transform:uppercase;font-family:monospace;">Effectiveness Score</div>
            <div style="font-size:24px;font-weight:900;font-family:monospace;margin:4px 0;color:${metrics.command_effectiveness_score >= 75 ? '#15803d' : '#b45309'};">
              ${metrics.command_effectiveness_score || 100}%
            </div>
            <small style="color:#52525b;font-weight:700;font-size:10px;">${metrics.doctrine_rating || 'ADEQUATE'}</small>
          </div>

          <div style="background:#ffffff;border:2px solid #000000;padding:12px;border-radius:6px;box-shadow:3px 3px 0px rgba(0,0,0,0.08);">
            <div style="font-size:10px;color:#52525b;font-weight:700;text-transform:uppercase;font-family:monospace;">EW Reaction Latency</div>
            <div style="font-size:24px;font-weight:900;font-family:monospace;margin:4px 0;color:#000000;">
              ${metrics.first_jamming_reaction_sec || 0}s
            </div>
            <small style="color:#52525b;font-size:10px;">Jamming to Order Response</small>
          </div>

          <div style="background:#ffffff;border:2px solid #000000;padding:12px;border-radius:6px;box-shadow:3px 3px 0px rgba(0,0,0,0.08);">
            <div style="font-size:10px;color:#52525b;font-weight:700;text-transform:uppercase;font-family:monospace;">Divergence Incidents</div>
            <div style="font-size:24px;font-weight:900;font-family:monospace;margin:4px 0;color:${metrics.spoofed_divergence_actions > 0 ? '#b91c1c' : '#15803d'};">
              ${metrics.spoofed_divergence_actions || 0}
            </div>
            <small style="color:#52525b;font-size:10px;">Orders on Spoofed Data</small>
          </div>

          <div style="background:#ffffff;border:2px solid #000000;padding:12px;border-radius:6px;box-shadow:3px 3px 0px rgba(0,0,0,0.08);">
            <div style="font-size:10px;color:#52525b;font-weight:700;text-transform:uppercase;font-family:monospace;">Dropped Radio Comms</div>
            <div style="font-size:24px;font-weight:900;font-family:monospace;margin:4px 0;color:#000000;">
              ${metrics.dropped_comms_count || 0}
            </div>
            <small style="color:#52525b;font-size:10px;">Severed Transmissions</small>
          </div>

          <div style="background:#ffffff;border:2px solid #000000;padding:12px;border-radius:6px;box-shadow:3px 3px 0px rgba(0,0,0,0.08);">
            <div style="font-size:10px;color:#52525b;font-weight:700;text-transform:uppercase;font-family:monospace;">Orders Issued</div>
            <div style="font-size:24px;font-weight:900;font-family:monospace;margin:4px 0;color:#000000;">
              ${metrics.total_orders_issued || 0}
            </div>
            <small style="color:#52525b;font-size:10px;">Decisions Captured</small>
          </div>
        </div>

        <!-- FILTER TABS -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <h3 style="font-size:12px;color:#000000;font-weight:900;text-transform:uppercase;letter-spacing:1px;font-family:monospace;margin:0;">
            CHRONOLOGICAL TIMELINE & DECISION AUDIT
          </h3>
          <div style="display:flex;gap:6px;">
            <button class="btn-header ${this.filterSeverity === 'ALL' ? 'active' : ''}" onclick="window.aarViewer.setFilter('ALL')" style="font-size:10px;">ALL</button>
            <button class="btn-header ${this.filterSeverity === 'ORDERS' ? 'active' : ''}" onclick="window.aarViewer.setFilter('ORDERS')" style="font-size:10px;">ORDERS</button>
            <button class="btn-header ${this.filterSeverity === 'COMMS' ? 'active' : ''}" onclick="window.aarViewer.setFilter('COMMS')" style="font-size:10px;">COMMS / EW</button>
            <button class="btn-header ${this.filterSeverity === 'CRITICAL' ? 'active' : ''}" onclick="window.aarViewer.setFilter('CRITICAL')" style="font-size:10px;">CRITICAL</button>
          </div>
        </div>

        <!-- TIMELINE FEED -->
        <div style="max-height:550px;overflow-y:auto;padding-right:4px;">
          ${eventsHtml || '<div style="text-align:center;padding:40px;color:#52525b;font-family:monospace;font-weight:600;">No exercise events recorded yet. Issue orders or trigger injects to populate timeline.</div>'}
        </div>
      </div>
    `;
  }

  setFilter(filter) {
    this.filterSeverity = filter;
    if (this.cachedData) {
      this.render(this.cachedData);
    }
  }

  escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.innerText = str;
    return div.innerHTML;
  }
}

window.AARViewer = AARViewer;
