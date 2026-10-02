/**
 * Tactical Communications Terminal
 * Manages multichannel radio nets, PTT voice audio triggers,
 * text degradation rendering, and quick report shortcuts.
 */

class CommsTerminal {
  constructor(containerId, onSendMessage) {
    this.container = document.getElementById(containerId);
    this.onSendMessage = onSendMessage;
    this.currentChannel = "TAC-1";
    this.renderedMsgIds = new Set();

    this.initUI();
  }

  initUI() {
    // Channel tabs
    const tabs = document.querySelectorAll(".channel-tab");
    tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        this.currentChannel = tab.dataset.channel;
        if (window.tacticalAudio) window.tacticalAudio.playRadioSquelch(false);
      });
    });

    // PTT Send button & Enter key
    const sendBtn = document.getElementById("btnSendMessage");
    const input = document.getElementById("commsInput");

    if (sendBtn && input) {
      sendBtn.addEventListener("click", () => this.handleSend(input));
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.handleSend(input);
        }
      });
    }

    // Quick Action Buttons (CONTACT, 9-LINE, SITREP)
    const btnContact = document.getElementById("btnQuickContact");
    if (btnContact && input) {
      btnContact.addEventListener("click", () => {
        input.value = "CONTACT REPORT: ENEMY MECH SQUAD ADVANCING GRID 7420 4810 // REQUESTING DIRECTIVES";
        input.focus();
      });
    }

    const btnSitrep = document.getElementById("btnQuickSitrep");
    if (btnSitrep && input) {
      btnSitrep.addEventListener("click", () => {
        input.value = "SITREP: SQUAD HOLDING LINE AT NORTH PASS // AMMO 85% // ALL STATIONS FUNCTIONAL";
        input.focus();
      });
    }
  }

  handleSend(input) {
    const text = input.value.trim();
    if (!text) return;

    if (window.tacticalAudio) {
      window.tacticalAudio.playRadioSquelch(false);
      setTimeout(() => window.tacticalAudio.playRadioSquelch(true), 300);
    }

    if (this.onSendMessage) {
      this.onSendMessage(this.currentChannel, text, "SITREP");
    }

    input.value = "";
  }

  updateMessages(messages) {
    const stream = document.getElementById("messageStream");
    if (!stream) return;

    let hasNew = false;
    for (const msg of messages) {
      if (!this.renderedMsgIds.has(msg.id)) {
        this.renderedMsgIds.add(msg.id);
        hasNew = true;

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        if (msg.is_corrupted) bubble.classList.add("msg-corrupted");
        if (msg.is_dropped) bubble.classList.add("msg-dropped");

        const delayBadge = msg.delivery_delay > 1.0 ? 
          `<span style="color:#f59e0b;font-size:9px;">(+${msg.delivery_delay.toFixed(1)}s LAG)</span>` : "";

        bubble.innerHTML = `
          <div class="msg-header">
            <span class="msg-sender">[${msg.channel}] ${msg.sender_role}</span>
            <span>${delayBadge} T+${Math.floor(msg.sim_time)}s</span>
          </div>
          <div class="msg-body">${this.escapeHtml(msg.perceived_content || msg.raw_content)}</div>
        `;

        stream.appendChild(bubble);
      }
    }

    if (hasNew) {
      stream.scrollTop = stream.scrollHeight;
      if (window.tacticalAudio) {
        window.tacticalAudio.playAlertPing();
      }
    }
  }

  escapeHtml(str) {
    const div = document.createElement("div");
    div.innerText = str;
    return div.innerHTML;
  }
}

window.CommsTerminal = CommsTerminal;
