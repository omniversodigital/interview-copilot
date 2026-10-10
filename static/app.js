/**
 * Sovereign Interview Co-Pilot (The Cyrano Engine)
 * Client-side Controller: Web Speech API + WebSocket Stream + HUD Renderer
 */

class InterviewCoPilot {
  constructor() {
    this.ws = null;
    this.recognition = null;
    this.isListening = false;
    this.topics = [];
    this.currentTopicId = null;

    // DOM Elements
    this.wsDot = document.getElementById("wsStatusDot");
    this.wsText = document.getElementById("wsStatusText");
    this.micDot = document.getElementById("micStatusDot");
    this.micText = document.getElementById("micStatusText");
    this.micBtn = document.getElementById("micBtn");
    this.micIcon = document.getElementById("micIcon");
    this.micBtnText = document.getElementById("micBtnText");
    this.langSelect = document.getElementById("langSelect");
    this.streamPlaceholder = document.getElementById("streamPlaceholder");
    this.streamText = document.getElementById("streamText");
    this.transcriptionStream = document.getElementById("transcriptionStream");
    this.queryForm = document.getElementById("queryForm");
    this.queryInput = document.getElementById("queryInput");
    this.topicDeck = document.getElementById("topicDeck");
    this.teleprompterToggle = document.getElementById("teleprompterToggle");

    // HUD Elements
    this.hudCategory = document.getElementById("hudCategory");
    this.hudTitle = document.getElementById("hudTitle");
    this.hudConfidence = document.getElementById("hudConfidence");
    this.hudHook = document.getElementById("hudHook");
    this.hudArchitecture = document.getElementById("hudArchitecture");
    this.hudMetrics = document.getElementById("hudMetrics");
    this.hudTradeoff = document.getElementById("hudTradeoff");
    this.hudCounterQ = document.getElementById("hudCounterQ");

    this.initWebSocket();
    this.initSpeechRecognition();
    this.bindEvents();
  }

  // ==========================================
  // WEBSOCKET LOGIC
  // ==========================================
  initWebSocket() {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${location.host}/ws/transcribe`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      this.wsDot.classList.add("active");
      this.wsText.textContent = "Telemetry Live";
    };

    this.ws.onclose = () => {
      this.wsDot.classList.remove("active");
      this.wsText.textContent = "Offline (Retrying...)";
      setTimeout(() => this.initWebSocket(), 2000);
    };

    this.ws.onerror = (err) => {
      console.error("WS Error:", err);
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "connected") {
          if (msg.topics) {
            this.topics = msg.topics;
            this.renderTopicDeck();
            // Automatically load first topic as default
            if (this.topics.length > 0) {
              this.selectTopic(this.topics[0].id);
            }
          }
        } else if (msg.type === "result") {
          this.renderHUD(msg.data);
        }
      } catch (err) {
        console.error("Parse Error:", err);
      }
    };
  }

  sendWebSocket(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  // ==========================================
  // SPEECH RECOGNITION (WEB SPEECH API)
  // ==========================================
  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      this.micBtn.disabled = true;
      this.micBtnText.textContent = "Speech API Unavailable";
      this.streamPlaceholder.textContent = "Web Speech API not supported in this browser. Use manual input.";
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = this.langSelect.value;

    this.recognition.onstart = () => {
      this.isListening = true;
      this.micBtn.classList.add("listening");
      this.micBtnText.textContent = "Listening Live...";
      this.micIcon.textContent = "🔴";
      this.micDot.classList.add("active");
      this.micText.textContent = "Mic Active";
      this.streamPlaceholder.style.display = "none";
    };

    this.recognition.onend = () => {
      if (this.isListening) {
        // Auto-restart if we didn't intentionally stop
        try {
          this.recognition.start();
        } catch (e) {}
      } else {
        this.micBtn.classList.remove("listening");
        this.micBtnText.textContent = "Start Listening";
        this.micIcon.textContent = "🎙️";
        this.micDot.classList.remove("active");
        this.micText.textContent = "Mic Idle";
      }
    };

    this.recognition.onresult = (event) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      if (interimTranscript) {
        this.streamText.textContent = interimTranscript;
        this.transcriptionStream.classList.add("interim");
        // Real-time interim trigger for ultra-fast reaction
        if (interimTranscript.trim().split(" ").length >= 4) {
          this.sendWebSocket({
            action: "speech",
            text: interimTranscript,
            is_final: false
          });
        }
      }

      if (finalTranscript) {
        this.streamText.textContent = finalTranscript;
        this.transcriptionStream.classList.remove("interim");
        this.sendWebSocket({
          action: "speech",
          text: finalTranscript,
          is_final: true
        });
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition notice:", event.error);
      if (event.error === "not-allowed") {
        alert("Microphone permission denied. Please allow microphone access in Chrome.");
      }
    };
  }

  toggleListening() {
    if (!this.recognition) return;
    if (this.isListening) {
      this.isListening = false;
      this.recognition.stop();
    } else {
      this.recognition.lang = this.langSelect.value;
      try {
        this.recognition.start();
      } catch (err) {
        console.error("Start Error:", err);
      }
    }
  }

  // ==========================================
  // TOPIC DECK & RENDERING
  // ==========================================
  renderTopicDeck() {
    this.topicDeck.innerHTML = "";
    this.topics.forEach((topic, idx) => {
      const pill = document.createElement("button");
      pill.className = "topic-pill";
      if (topic.id === this.currentTopicId) pill.classList.add("active");
      pill.innerHTML = `<span class="pill-number">${idx + 1}</span> ${topic.title}`;
      pill.onclick = () => this.selectTopic(topic.id);
      this.topicDeck.appendChild(pill);
    });
  }

  selectTopic(topicId) {
    this.currentTopicId = topicId;
    // Update pill states
    const pills = this.topicDeck.querySelectorAll(".topic-pill");
    pills.forEach((p, idx) => {
      if (this.topics[idx] && this.topics[idx].id === topicId) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });

    this.sendWebSocket({
      action: "select_topic",
      topic_id: topicId
    });
  }

  renderHUD(data) {
    const topic = data.topic || {};
    this.currentTopicId = topic.id;

    // Update active pill
    const pills = this.topicDeck.querySelectorAll(".topic-pill");
    pills.forEach((p, idx) => {
      if (this.topics[idx] && this.topics[idx].id === topic.id) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });

    this.hudCategory.textContent = topic.category || "General Architecture";
    this.hudTitle.textContent = topic.title || "Architectural Defense";
    this.hudConfidence.textContent = `${data.confidence || 95}% Match`;

    // ⚡ 1-Second Hook
    this.hudHook.textContent = topic.opening_hook || "Deliver confident direct opening thesis.";

    // 🏛 Architecture Pillars
    this.hudArchitecture.innerHTML = "";
    (topic.architecture_points || []).forEach(pt => {
      const li = document.createElement("li");
      li.textContent = pt;
      this.hudArchitecture.appendChild(li);
    });

    // 📊 Metrics Grid
    this.hudMetrics.innerHTML = "";
    (topic.metrics || []).forEach(m => {
      const pill = document.createElement("div");
      pill.className = "metric-pill";
      pill.innerHTML = `<span class="metric-icon">⚡</span><span class="metric-value">${m}</span>`;
      this.hudMetrics.appendChild(pill);
    });

    // ⚠️ Tradeoffs
    this.hudTradeoff.textContent = topic.tradeoffs || "Evaluate trade-off nuances based on scale.";

    // 🎯 Strategic Counter-Question
    this.hudCounterQ.textContent = topic.counter_question ? `"${topic.counter_question}"` : '""';
  }

  // ==========================================
  // EVENT BINDINGS & SHORTCUTS
  // ==========================================
  bindEvents() {
    this.micBtn.onclick = () => this.toggleListening();

    this.langSelect.onchange = () => {
      if (this.recognition && this.isListening) {
        this.recognition.stop();
        setTimeout(() => {
          this.recognition.lang = this.langSelect.value;
          this.recognition.start();
        }, 300);
      }
    };

    this.queryForm.onsubmit = (e) => {
      e.preventDefault();
      const q = this.queryInput.value.trim();
      if (q) {
        this.streamPlaceholder.style.display = "none";
        this.streamText.textContent = q;
        this.sendWebSocket({
          action: "query",
          text: q
        });
        this.queryInput.value = "";
      }
    };

    this.teleprompterToggle.onclick = () => {
      document.body.classList.toggle("teleprompter-mode");
      const isTeleprompter = document.body.classList.contains("teleprompter-mode");
      this.teleprompterToggle.classList.toggle("active", isTeleprompter);
      this.teleprompterToggle.innerHTML = isTeleprompter 
        ? "<span>🖥️</span> Full HUD Mode (T)"
        : "<span>👁️</span> Teleprompter Mode (T)";
    };

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      // Don't trigger shortcuts if typing in text input
      if (document.activeElement === this.queryInput) {
        if (e.key === "Escape") {
          this.queryInput.blur();
        }
        return;
      }

      if (e.key === " " || e.key.toLowerCase() === "m") {
        e.preventDefault();
        this.toggleListening();
      } else if (e.key.toLowerCase() === "t") {
        e.preventDefault();
        this.teleprompterToggle.click();
      } else if (e.key >= "1" && e.key <= "8") {
        const idx = parseInt(e.key) - 1;
        if (this.topics[idx]) {
          this.selectTopic(this.topics[idx].id);
        }
      } else if (e.key === "Escape") {
        this.streamText.textContent = "";
        this.streamPlaceholder.style.display = "inline";
      }
    });
  }
}

// Auto-boot on load
window.addEventListener("DOMContentLoaded", () => {
  window.copilot = new InterviewCoPilot();
});
