/**
 * R04 Web UI Application Controller
 * Handles 5-stage UI workflow, REST API integration, and Viewer postMessage events.
 */

// State Machine Stages
const STAGES = {
  SOURCE: "surface-source",
  PREPARE: "surface-prepare",
  AUTH: "surface-auth",
  REVIEW: "surface-review",
  RESULT: "surface-result",
};

class LessonApp {
  constructor() {
    this.currentStage = STAGES.SOURCE;
    this.currentSourceId = null;
    this.currentRegistrationId = null;
    this.currentRevision = 1;
    this.currentRequestKey = null;
    this.currentGrant = null; // Ephemeral; never saved to localStorage
    this.pollTimer = null;

    this.init();
  }

  async init() {
    this.bindNavigation();
    this.bindActionButtons();
    this.setupViewerPostMessageListener();
  }

  bindActionButtons() {
    document.getElementById("btn-next-source-to-prep")?.addEventListener("click", () => {
      this.switchStage(STAGES.PREPARE);
    });

    document.getElementById("btn-next-to-auth")?.addEventListener("click", () => {
      this.switchStage(STAGES.AUTH);
    });

    document.getElementById("btn-next-to-review")?.addEventListener("click", () => {
      this.switchStage(STAGES.REVIEW);
    });

    document.getElementById("btn-auth-open")?.addEventListener("click", () => {
      this.mountViewer("mock-grant-soomgo-token-12345");
    });

    document.getElementById("btn-auth-finish")?.addEventListener("click", () => {
      this.disposeViewer();
      document.getElementById("auth-state-text").innerText = "인증 완료 (Verified)";
    });

    document.getElementById("btn-auth-close")?.addEventListener("click", () => {
      this.disposeViewer();
    });

    document.getElementById("btn-submit-start")?.addEventListener("click", () => {
      this.switchStage(STAGES.RESULT);
    });

    document.getElementById("btn-reset-workflow")?.addEventListener("click", () => {
      this.switchStage(STAGES.SOURCE);
    });
  }

  // 1. Navigation & Stage Transitions
  bindNavigation() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const target = btn.getAttribute("data-target");
        this.switchStage(target);
      });
    });
  }

  switchStage(stageId) {
    this.currentStage = stageId;
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-target") === stageId);
    });
    document.querySelectorAll(".surface-pane").forEach((pane) => {
      pane.classList.toggle("active", pane.id === stageId);
    });
  }

  // 2. Viewer postMessage Handlers (R04 - R05 Protocol)
  setupViewerPostMessageListener() {
    window.addEventListener("message", (event) => {
      // Validate event source and structure
      const msg = event.data;
      if (!msg || !msg.type) return;

      switch (msg.type) {
        case "VIEWER_READY":
          console.log("[Viewer] Ready for user interaction:", msg);
          document.getElementById("btn-auth-finish")?.removeAttribute("disabled");
          break;

        case "VIEWER_ERROR":
          console.error("[Viewer] Remote error:", msg);
          alert(`뷰어 에러: ${msg.message}`);
          break;

        case "VIEWER_AUTH_DETECTED":
          console.log("[Viewer] Platform login detected at:", msg.detectedAt);
          document.getElementById("auth-state-text").innerText = "인증 감지됨 (확인 필요)";
          break;

        case "VIEWER_DISCONNECTED":
          console.log("[Viewer] Session disconnected");
          break;
      }
    });
  }

  mountViewer(grant) {
    this.currentGrant = grant; // Ephemeral
    const frame = document.getElementById("remote-viewer-frame");
    const placeholder = document.getElementById("viewer-placeholder");

    if (frame && placeholder) {
      placeholder.style.display = "none";
      frame.style.display = "block";
      // Convened Viewer URL protocol (Convention A)
      frame.src = `/remote/viewer?grant=${encodeURIComponent(grant)}`;

      // Post Init message to frame
      frame.onload = () => {
        frame.contentWindow.postMessage(
          { type: "VIEWER_INIT", grant: grant },
          "*"
        );
      };
    }
  }

  disposeViewer() {
    const frame = document.getElementById("remote-viewer-frame");
    const placeholder = document.getElementById("viewer-placeholder");
    const overlay = document.getElementById("viewer-overlay");

    if (frame) {
      try {
        frame.contentWindow.postMessage({ type: "VIEWER_DISPOSE" }, "*");
      } catch (e) {}
      frame.src = "about:blank";
      frame.style.display = "none";
    }

    if (overlay) overlay.style.display = "none";
    if (placeholder) placeholder.style.display = "flex";

    this.currentGrant = null; // Immediately clear ephemeral token
  }

  // 3. API Communication (Adheres to 8 Directives)
  async apiCall(method, path, body = null) {
    const headers = {
      "Accept": "application/json",
      "Cache-Control": "no-store", // Directive 8
      "X-Mock-Owner": "instructor-session", // Directive 6: context header only
    };

    let fetchBody = null;
    if (body) {
      // Directive 6: Strip owner from payload body if present
      const clean = { ...body };
      delete clean.owner;
      fetchBody = JSON.stringify(clean);
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(path, {
      method,
      headers,
      body: fetchBody,
    });

    const status = response.status;
    const json = await response.json().catch(() => ({}));

    return { status, data: json };
  }

  // 4. Step 4 Review & Step 5 Polling
  async submitStart() {
    if (!this.currentRegistrationId) return;

    if (!this.currentRequestKey) {
      this.currentRequestKey = `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    }

    const payload = {
      request_key: this.currentRequestKey,
      snapshot_digest: document.getElementById("rev-digest")?.innerText || "",
    };

    // Directive 2: H7 start accepts 202 (initial) or 200 (replay)
    const { status, data } = await this.apiCall(
      "POST",
      `/v1/registrations/${this.currentRegistrationId}/start`,
      payload
    );

    if (status === 202 || status === 200) {
      this.switchStage(STAGES.RESULT);
      this.startResultPolling();
    } else {
      alert(`등록 요청 실패 (${status}): ${data.message || "오류 발생"}`);
    }
  }

  startResultPolling() {
    if (this.pollTimer) clearInterval(this.pollTimer);

    let interval = 1500; // 1.5s base interval (Directive Option A)
    const maxPolls = 40; // 60s timeout
    let pollCount = 0;

    this.pollTimer = setInterval(async () => {
      pollCount++;
      if (pollCount > maxPolls) {
        clearInterval(this.pollTimer);
        this.renderFinalResult({
          verdict: "unknown",
          error: "POLLING_TIMEOUT",
          message: "작업 상태 조회 시간(60초)을 초과했습니다. 관리자 화면에서 직접 확인하세요.",
        });
        return;
      }

      // Directive 3: Observe job_state and progress
      const { status, data } = await this.apiCall(
        "GET",
        `/v1/registrations/${this.currentRegistrationId}`
      );

      if (status === 200 && data) {
        this.renderProgress(data.job_state, data.progress);

        if (data.job_state === "done" || data.job_state === "stopped") {
          clearInterval(this.pollTimer);
          // Directive 4: Render stored result upon completion
          this.renderFinalResult(data.result);
        }
      }
    }, interval);
  }

  renderProgress(jobState, progress) {
    const stateEl = document.getElementById("job-state-text");
    const stepEl = document.getElementById("progress-step-text");
    const barEl = document.getElementById("progress-bar-fill");

    if (stateEl) stateEl.innerText = jobState;
    if (progress && progress.current_step) {
      if (stepEl) stepEl.innerText = `단계: ${progress.current_step} (${progress.step_label || ""})`;
      if (barEl && progress.total_steps) {
        const pct = Math.round((progress.completed_steps / progress.total_steps) * 100);
        barEl.style.width = `${pct}%`;
      }
    }
  }

  renderFinalResult(result) {
    const box = document.getElementById("result-box");
    const title = document.getElementById("verdict-title");
    const desc = document.getElementById("verdict-desc");
    const unknownGuide = document.getElementById("unknown-action-guide");
    const evidenceEl = document.getElementById("result-evidence-json");

    if (box) box.style.display = "block";
    if (evidenceEl) evidenceEl.innerText = JSON.stringify(result, null, 2);

    const verdict = result ? result.verdict : "unknown";

    if (verdict === "confirmed") {
      title.innerText = "등록 완료 (Confirmed)";
      title.style.color = "var(--success)";
      desc.innerText = "모의 플랫폼 서비스 설정 등록이 성공적으로 완료되었습니다.";
      if (unknownGuide) unknownGuide.style.display = "none";
    } else if (verdict === "unknown") {
      // Directive 5: unknown blocks auto-retry and presents guidance
      title.innerText = "상태 불확실 (Unknown)";
      title.style.color = "var(--warning)";
      desc.innerText = "결과가 불확실합니다. 중복 방지를 위해 자동 재시도를 차단합니다.";
      if (unknownGuide) unknownGuide.style.display = "block";
    } else {
      title.innerText = "등록 실패 (Failed)";
      title.style.color = "var(--danger)";
      desc.innerText = result?.error || "등록 처리 중 오류가 발생했습니다.";
      if (unknownGuide) unknownGuide.style.display = "none";
    }
  }
}

// Global bootstrap
document.addEventListener("DOMContentLoaded", () => {
  window.lessonApp = new LessonApp();
});
