let currentSessionId = "staff-alex-chen-canonical";
let socket = null;
let radarChartInstance = null;
let currentSessionData = null;
let lastFocusedElement = null;

// DOM Elements
const btnRunSimulation = document.getElementById("btnRunSimulation");
const btnLoadStaff = document.getElementById("btnLoadStaff");
const btnLoadBorderline = document.getElementById("btnLoadBorderline");
const btnToggleTranscript = document.getElementById("btnToggleTranscript");
const btnCloseDrawer = document.getElementById("btnCloseDrawer");
const transcriptDrawer = document.getElementById("transcriptDrawer");
const transcriptList = document.getElementById("transcriptList");
const debateStream = document.getElementById("debateStream");
const synthesisSection = document.getElementById("sectionAdjudication");
const independenceCertBanner = document.getElementById("independenceCertBanner");
const a11yAnnouncer = document.getElementById("a11yAnnouncer");

const candidateName = document.getElementById("candidateName");
const candidateTargetRole = document.getElementById("candidateTargetRole");
const candidateExperienceBadge = document.getElementById("candidateExperienceBadge");
const candidateResumeSummary = document.getElementById("candidateResumeSummary");
const candidateSkillsList = document.getElementById("candidateSkillsList");

const jdRoleTitle = document.getElementById("jdRoleTitle");
const jdRoleLevelBadge = document.getElementById("jdRoleLevelBadge");
const jdTeam = document.getElementById("jdTeam");
const jdResponsibilitiesList = document.getElementById("jdResponsibilitiesList");
const jdSkillsTags = document.getElementById("jdSkillsTags");

const badgeSystemState = document.getElementById("badgeSystemState");
const transcriptTurnCount = document.getElementById("transcriptTurnCount");
const badgeActiveRound = document.getElementById("badgeActiveRound");
const wsStatusDot = document.getElementById("wsStatusDot");
const wsStatusText = document.getElementById("wsStatusText");

// Steps
const stepRound1 = document.getElementById("stepRound1");
const stepRound2 = document.getElementById("stepRound2");
const stepRound3 = document.getElementById("stepRound3");

// Citation Modal Elements
const citationModal = document.getElementById("citationModal");
const btnCloseCitModal = document.getElementById("btnCloseCitModal");
const citModalVerifiedBadge = document.getElementById("citModalVerifiedBadge");
const citModalClaim = document.getElementById("citModalClaim");
const citModalTurnSpeaker = document.getElementById("citModalTurnSpeaker");
const citModalQuote = document.getElementById("citModalQuote");
const citModalNotes = document.getElementById("citModalNotes");

function announceA11y(message) {
  if (a11yAnnouncer) {
    a11yAnnouncer.textContent = "";
    setTimeout(() => {
      a11yAnnouncer.textContent = message;
    }, 50);
  }
}

async function init() {
  lucide.createIcons();
  await loadSession(currentSessionId);
  setupWebSocket(currentSessionId);
  setupListeners();
}

function setupListeners() {
  btnRunSimulation.addEventListener("click", runSimulation);

  btnLoadStaff.addEventListener("click", () => {
    btnLoadStaff.className = "px-3 py-1.5 text-xs font-semibold rounded-md bg-indigo-600 text-white shadow transition-all focus:ring-2 focus:ring-indigo-300";
    btnLoadStaff.setAttribute("aria-selected", "true");
    btnLoadBorderline.className = "px-3 py-1.5 text-xs font-semibold rounded-md text-slate-300 hover:text-white hover:bg-slate-800 transition-all focus:ring-2 focus:ring-indigo-300";
    btnLoadBorderline.setAttribute("aria-selected", "false");
    announceA11y("Switched to candidate Alex Chen, Staff Distributed Systems Engineer.");
    loadSession("staff-alex-chen-canonical");
  });

  btnLoadBorderline.addEventListener("click", async () => {
    btnLoadBorderline.className = "px-3 py-1.5 text-xs font-semibold rounded-md bg-indigo-600 text-white shadow transition-all focus:ring-2 focus:ring-indigo-300";
    btnLoadBorderline.setAttribute("aria-selected", "true");
    btnLoadStaff.className = "px-3 py-1.5 text-xs font-semibold rounded-md text-slate-300 hover:text-white hover:bg-slate-800 transition-all focus:ring-2 focus:ring-indigo-300";
    btnLoadStaff.setAttribute("aria-selected", "false");
    announceA11y("Switched to candidate David Vance, Borderline Risk candidate.");
    await loadBorderlineSession();
  });

  btnToggleTranscript.addEventListener("click", () => {
    const isExpanded = transcriptDrawer.classList.contains("translate-x-full");
    if (isExpanded) {
      openDrawer();
    } else {
      closeDrawer();
    }
  });

  btnCloseDrawer.addEventListener("click", closeDrawer);
  btnCloseCitModal.addEventListener("click", closeCitationModal);

  citationModal.addEventListener("click", (e) => {
    if (e.target === citationModal) closeCitationModal();
  });

  // Global Keyboard Navigation (ESC closes modal and drawer)
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (!citationModal.classList.contains("hidden")) {
        closeCitationModal();
      } else if (!transcriptDrawer.classList.contains("translate-x-full")) {
        closeDrawer();
      }
    }
  });
}

function openDrawer() {
  transcriptDrawer.classList.remove("translate-x-full");
  btnToggleTranscript.setAttribute("aria-expanded", "true");
  btnCloseDrawer.focus();
}

function closeDrawer() {
  transcriptDrawer.classList.add("translate-x-full");
  btnToggleTranscript.setAttribute("aria-expanded", "false");
  if (lastFocusedElement) {
    lastFocusedElement.focus();
  } else {
    btnToggleTranscript.focus();
  }
}

function closeCitationModal() {
  citationModal.classList.add("hidden");
  if (lastFocusedElement) {
    lastFocusedElement.focus();
  }
}

async function loadSession(sessionId) {
  try {
    const res = await fetch(`/api/v1/sessions/${sessionId}`);
    if (!res.ok) throw new Error("Session not found");
    const session = await res.json();
    currentSessionId = sessionId;
    currentSessionData = session;
    renderSession(session);
    setupWebSocket(sessionId);
  } catch (err) {
    console.error("Failed to load session:", err);
  }
}

async function loadBorderlineSession() {
  try {
    let res = await fetch("/api/v1/sessions/borderline-david-vance");
    if (!res.ok) {
      const sampleResp = await fetch("/api/v1/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "Staff Systems Engineer (David Vance - Risk Audit)",
          candidate: {
            id: "cand-david-vance",
            name: "David Vance",
            target_role: "Staff Distributed Systems Engineer",
            target_level: "L6",
            experience_years: 8,
            resume_summary: "Claims sole ownership of global multi-region caching system serving 50M DAU.",
            key_skills: ["Redis", "Java", "Caching", "Microservices"]
          },
          job_description: {
            role_title: "Staff Distributed Systems Engineer",
            level: "L6",
            team: "Cloud Infrastructure & Data Engine Platform",
            core_responsibilities: [
              "Architect globally replicated active-active distributed storage",
              "Ensure 99.999% availability and data integrity under network partitions",
              "Lead incident post-mortems and enforce high operational reliability bars"
            ],
            required_skills: ["Distributed Storage", "Raft / Paxos Consensus", "High Concurrency", "Storage Engines"]
          },
          transcript_turns: [
            { turn_id: 1, speaker: "Interviewer", text: "David, describe how you designed your multi-datacenter distributed caching system." },
            { turn_id: 2, speaker: "Candidate", text: "Sure, we deployed Redis Sentinel across three global regions. It easily supported 50 million daily active users with sub-millisecond lookups." },
            { turn_id: 3, speaker: "Interviewer", text: "How did you manage cross-region replication lag and avoid stale reads between US-East and EU-West?" },
            { turn_id: 4, speaker: "Candidate", text: "Honestly Redis handles replication asynchronously out of the box, so we didn't really have to write custom conflict resolution logic. We just assumed Redis Sentinel would handle it." },
            { turn_id: 5, speaker: "Interviewer", text: "What happened if a network partition occurred while a client wrote to a minority partition?" },
            { turn_id: 6, speaker: "Candidate", text: "I think the client just retried. We didn't experience any major data drift that I was aware of, because the DevOps team maintained the network switches." },
            { turn_id: 7, speaker: "Interviewer", text: "Can you elaborate on your specific personal code contribution vs what was configured by the infrastructure team?" },
            { turn_id: 8, speaker: "Candidate", text: "Well, my team mostly wrote the REST wrapper endpoints in Java Spring Boot that made the Redis calls. The underlying cluster configuration was mostly set up by another team before I joined." }
          ]
        })
      });
      const created = await sampleResp.json();
      currentSessionId = created.id;
      currentSessionData = created;
      renderSession(created);
      setupWebSocket(created.id);
      return;
    }
    const session = await res.json();
    currentSessionId = session.id;
    currentSessionData = session;
    renderSession(session);
    setupWebSocket(session.id);
  } catch (e) {
    console.error("Error loading borderline session:", e);
  }
}

function renderSession(session) {
  // Screen 1: Context
  candidateName.textContent = session.candidate.name;
  candidateTargetRole.textContent = `Target Role: ${session.candidate.target_role}`;
  candidateExperienceBadge.textContent = `${session.candidate.experience_years} Years Exp`;
  candidateResumeSummary.textContent = session.candidate.resume_summary;

  if (session.candidate.key_skills) {
    candidateSkillsList.innerHTML = session.candidate.key_skills.map(s => `
      <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200">${escapeHtml(s)}</span>
    `).join("");
  }

  jdRoleTitle.textContent = session.job_description.role_title;
  jdRoleLevelBadge.textContent = session.job_description.level || "L6 / Staff";
  jdTeam.textContent = session.job_description.team;

  if (session.job_description.core_responsibilities) {
    jdResponsibilitiesList.innerHTML = session.job_description.core_responsibilities.map(r => `
      <li class="flex items-start gap-1.5"><span class="text-indigo-400 font-bold" aria-hidden="true">&bull;</span> ${escapeHtml(r)}</li>
    `).join("");
  }

  if (session.job_description.required_skills) {
    jdSkillsTags.innerHTML = session.job_description.required_skills.map(s => `
      <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200">${escapeHtml(s)}</span>
    `).join("");
  }

  badgeSystemState.textContent = session.status;
  transcriptTurnCount.textContent = `${session.transcript_turns.length} Turns Indexed & Verified`;

  renderTranscriptTurns(session.transcript_turns);

  // Screen 2: Evaluations
  resetAgentCards();
  if (session.independent_evaluations && Object.keys(session.independent_evaluations).length > 0) {
    for (const [agentId, ev] of Object.entries(session.independent_evaluations)) {
      renderAgentEvaluation(agentId, ev);
    }
    if (Object.keys(session.independent_evaluations).length === 4) {
      independenceCertBanner.classList.remove("hidden");
    }
  } else {
    independenceCertBanner.classList.add("hidden");
  }

  // Screen 3: Debate Stream
  debateStream.innerHTML = "";
  if (session.debate_rounds && session.debate_rounds.length > 0) {
    badgeActiveRound.textContent = `Debate Completed (${session.debate_rounds.length} Rounds)`;
    highlightRoundStep(3);
    for (const round of session.debate_rounds) {
      for (const arg of round.arguments) {
        appendDebateArgument(arg);
      }
    }
  } else {
    badgeActiveRound.textContent = "Round: Awaiting Start";
    highlightRoundStep(0);
    debateStream.innerHTML = `
      <div class="text-center py-12 text-slate-400 text-xs space-y-2">
        <i data-lucide="message-square" class="w-8 h-8 mx-auto text-slate-500" aria-hidden="true"></i>
        <p>Debate discourse will stream live in real time once Phase 1 evaluations complete.</p>
      </div>
    `;
  }

  // Screen 4: Opinion Evolution & Calibration
  if (session.synthesis && session.synthesis.agent_calibrations) {
    renderOpinionEvolution(session.synthesis.agent_calibrations, session.independent_evaluations);
  } else {
    document.getElementById("evolutionGrid").innerHTML = `
      <div class="text-center py-8 text-slate-400 text-xs col-span-full">
        Opinion evolution will populate automatically after Round 3 debate calibration completes.
      </div>
    `;
  }

  // Screen 5: Final Adjudication
  if (session.synthesis) {
    renderSynthesis(session.synthesis);
  } else {
    synthesisSection.classList.add("hidden");
  }
  lucide.createIcons();
}

function renderTranscriptTurns(turns) {
  transcriptList.innerHTML = "";
  turns.forEach(t => {
    const isInterviewer = t.speaker.toLowerCase().includes("interviewer");
    const div = document.createElement("article");
    div.id = `turn-${t.turn_id}`;
    div.className = `p-3 rounded-lg border text-xs transition-all ${
      isInterviewer ? "bg-slate-950/70 border-slate-800 text-slate-300" : "bg-slate-800/90 border-slate-700 text-slate-100"
    }`;
    div.setAttribute("tabindex", "0");
    div.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <span class="font-bold uppercase tracking-wider text-[10px] ${isInterviewer ? "text-indigo-300" : "text-emerald-300"}">
          Turn ${t.turn_id} • ${t.speaker}
        </span>
        <span class="text-[10px] text-slate-400">${t.timestamp_start || ""}</span>
      </div>
      <p class="leading-relaxed select-text">${escapeHtml(t.text)}</p>
    `;
    transcriptList.appendChild(div);
  });
}

function resetAgentCards() {
  const agentIds = ["technical_architect", "culture_lead", "domain_specialist", "bar_raiser"];
  agentIds.forEach(id => {
    const card = document.getElementById(`card-${id}`);
    if (card) {
      card.querySelector(".agent-hash").textContent = "hash: #pending";
      card.querySelector(".status-box").innerHTML = `<span class="text-slate-400 italic">Waiting to evaluate independently...</span>`;
      card.querySelector(".agent-rec").textContent = "--";
      card.querySelector(".agent-rec").className = "agent-rec text-slate-300 font-bold";
      card.querySelector(".agent-conf").textContent = "--";
      card.querySelector(".agent-evidence-count").textContent = "0 Quotes";
    }
  });
}

function renderAgentEvaluation(agentId, ev) {
  const card = document.getElementById(`card-${agentId}`);
  if (!card) return;

  card.querySelector(".agent-hash").textContent = `hash: #${ev.execution_hash.substring(0, 8)}`;
  
  const citCount = (ev.citations && ev.citations.length) || 0;
  card.querySelector(".agent-evidence-count").textContent = `${citCount} Verified ${citCount === 1 ? 'Quote' : 'Quotes'}`;

  let citationsHtml = "";
  if (ev.citations && ev.citations.length > 0) {
    citationsHtml = `
      <div class="mt-2 pt-1.5 border-t border-slate-800 flex flex-wrap gap-1">
        ${ev.citations.map(c => `
          <button type="button" onclick="inspectCitation('${escapeQuotes(JSON.stringify(c))}')" aria-label="Inspect evidence citation Turn ${c.turn_id} (${Math.round(c.grounding_score*100)}% grounding)" class="citation-pill inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-indigo-950/90 border border-indigo-600 text-[10px] text-indigo-200 font-mono focus:ring-2 focus:ring-indigo-300">
            <i data-lucide="check" class="w-2.5 h-2.5 text-emerald-400" aria-hidden="true"></i> Turn ${c.turn_id} (${Math.round(c.grounding_score*100)}%)
          </button>
        `).join("")}
      </div>
    `;
  }

  card.querySelector(".status-box").innerHTML = `
    <p class="text-xs text-slate-200 leading-snug line-clamp-3">${escapeHtml(ev.summary_assessment)}</p>
    ${citationsHtml}
  `;
  
  const recEl = card.querySelector(".agent-rec");
  recEl.textContent = ev.recommendation.replace("_", " ");
  recEl.className = `agent-rec font-bold ${getRecommendationClass(ev.recommendation)}`;

  card.querySelector(".agent-conf").textContent = `${Math.round(ev.confidence_score * 100)}%`;
  lucide.createIcons();
}

function appendDebateArgument(arg) {
  if (debateStream.children.length === 1 && debateStream.children[0].textContent.includes("Debate discourse will stream live")) {
    debateStream.innerHTML = "";
  }

  const div = document.createElement("article");
  div.className = "bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs space-y-2 animate-fade-in shadow-sm";
  div.setAttribute("tabindex", "0");
  
  let badgeClass = "badge-clarify";
  if (arg.stance === "CHALLENGE") badgeClass = "badge-challenge";
  if (arg.stance === "DEFEND") badgeClass = "badge-defend";
  if (arg.stance === "CONCEDE") badgeClass = "badge-concede";

  div.innerHTML = `
    <div class="flex items-center justify-between border-b border-slate-800/80 pb-2">
      <div class="flex items-center gap-2">
        <span class="font-bold text-slate-100">${escapeHtml(arg.speaker_name)}</span>
        <span class="text-[10px] font-bold px-2 py-0.5 rounded ${badgeClass}">${arg.stance}</span>
        ${arg.target_agent_name ? `<span class="text-[10px] text-slate-300 flex items-center gap-1"><span aria-hidden="true">&rarr;</span> <strong class="text-slate-100">${escapeHtml(arg.target_agent_name)}</strong></span>` : ""}
      </div>
      <div class="text-[11px] text-slate-300">
        Post-Argument Confidence: <strong class="text-indigo-200 font-bold">${Math.round(arg.confidence_after_argument * 100)}%</strong>
      </div>
    </div>

    <div class="space-y-1">
      <span class="text-[10px] font-bold text-slate-300 uppercase tracking-wider block">Topic: ${escapeHtml(arg.contention_topic)}</span>
      <p class="text-slate-100 text-xs leading-relaxed">${escapeHtml(arg.argument_text)}</p>
    </div>

    ${arg.evidence_citations && arg.evidence_citations.length > 0 ? `
      <div class="pt-2 border-t border-slate-900 flex flex-wrap gap-1.5 items-center">
        <span class="text-[10px] text-slate-400 uppercase font-semibold">Evidence Cited:</span>
        ${arg.evidence_citations.map(c => `
          <button type="button" onclick="inspectCitation('${escapeQuotes(JSON.stringify(c))}')" aria-label="Inspect citation Turn ${c.turn_id}" class="citation-pill inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-indigo-600 text-[10px] text-indigo-200 hover:bg-slate-800 focus:ring-2 focus:ring-indigo-300">
            <i data-lucide="file-text" class="w-3 h-3 text-emerald-400" aria-hidden="true"></i> Turn ${c.turn_id}: "${escapeHtml(c.verbatim_quote.substring(0, 45))}..."
          </button>
        `).join("")}
      </div>
    ` : ""}
  `;
  debateStream.appendChild(div);
  debateStream.scrollTop = debateStream.scrollHeight;
  lucide.createIcons();
}

function renderOpinionEvolution(calibrations, initialEvals) {
  const container = document.getElementById("evolutionGrid");
  if (!container) return;

  container.innerHTML = calibrations.map(cal => {
    const initScore = Math.round(cal.initial_confidence * 100);
    const finalScore = Math.round(cal.final_confidence * 100);
    const delta = Math.round(cal.confidence_delta * 100);
    
    let deltaClass = "text-slate-300";
    let deltaSign = "";
    if (delta > 0) {
      deltaClass = "text-emerald-300";
      deltaSign = "+";
    } else if (delta < 0) {
      deltaClass = "text-rose-300";
    }

    const hasShift = (cal.initial_recommendation !== cal.final_recommendation) || (delta !== 0);

    return `
      <article class="bg-slate-950 border ${hasShift ? 'border-indigo-800 shadow-indigo-950/30' : 'border-slate-800'} rounded-xl p-4 space-y-3 shadow-sm" tabindex="0">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h3 class="font-bold text-xs text-white">${escapeHtml(cal.agent_name)}</h3>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
            ${cal.final_recommendation.replace("_", " ")}
          </span>
        </div>

        <div class="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          <div>
            <span class="text-[10px] text-slate-300 block">Initial</span>
            <strong class="text-slate-100">${initScore}%</strong>
          </div>
          <div class="text-slate-400 font-bold" aria-hidden="true">&rarr;</div>
          <div>
            <span class="text-[10px] text-slate-300 block">Calibrated</span>
            <strong class="text-indigo-200 font-bold">${finalScore}%</strong>
          </div>
          <div class="text-right">
            <span class="text-[10px] text-slate-300 block">Delta</span>
            <strong class="${deltaClass} font-mono font-bold">${deltaSign}${delta}%</strong>
          </div>
        </div>

        <div class="space-y-1 text-xs">
          ${cal.concessions_made && cal.concessions_made.length > 0 ? `
            <div class="bg-amber-950/40 border border-amber-800/60 p-2 rounded text-[11px] text-amber-200">
              <strong class="text-amber-300 block text-[10px] uppercase font-bold">Concession Made:</strong>
              ${escapeHtml(cal.concessions_made.join(", "))}
            </div>
          ` : ""}
          <p class="text-[11px] text-slate-300 leading-relaxed pt-1">
            <strong class="text-slate-100">Calibration Rationale:</strong> ${escapeHtml(cal.calibration_reasoning)}
          </p>
        </div>
      </article>
    `;
  }).join("");
  lucide.createIcons();
}

function renderSynthesis(synthesis) {
  synthesisSection.classList.remove("hidden");

  const verdictBadge = document.getElementById("finalVerdictBadge");
  verdictBadge.textContent = synthesis.final_decision.replace("_", " ");
  verdictBadge.className = `text-sm font-black px-3.5 py-1.5 rounded-lg uppercase tracking-wider ${getVerdictBadgeClass(synthesis.final_decision)}`;

  document.getElementById("synthesisConfidenceScore").textContent = `${Math.round(synthesis.confidence_score * 100)}% Calibrated Confidence`;
  document.getElementById("synthesisSummaryText").textContent = synthesis.decision_summary;
  document.getElementById("nonAveragingRationaleText").textContent = synthesis.non_averaging_rationale;

  const strengthsList = document.getElementById("synthesisStrengthsList");
  strengthsList.innerHTML = synthesis.primary_strengths.map(s => `
    <li class="flex items-start gap-1.5">
      <span class="text-emerald-400 font-bold" aria-hidden="true">&bull;</span>
      <span class="leading-relaxed">${escapeHtml(s)}</span>
    </li>
  `).join("");

  const risksList = document.getElementById("synthesisRisksList");
  risksList.innerHTML = synthesis.critical_risks_and_mitigations.map(r => `
    <li class="flex items-start gap-1.5">
      <span class="text-rose-400 font-bold" aria-hidden="true">&bull;</span>
      <span class="leading-relaxed">${escapeHtml(r)}</span>
    </li>
  `).join("");

  const decisiveList = document.getElementById("decisiveEvidenceList");
  if (synthesis.decisive_evidence && synthesis.decisive_evidence.length > 0) {
    decisiveList.innerHTML = synthesis.decisive_evidence.map(c => `
      <button type="button" onclick="inspectCitation('${escapeQuotes(JSON.stringify(c))}')" aria-label="Inspect decisive evidence Turn ${c.turn_id}" class="citation-pill w-full text-left bg-slate-900 border border-slate-800 hover:border-indigo-600 focus:ring-2 focus:ring-indigo-300 p-2 rounded-lg flex items-center justify-between text-xs">
        <span class="text-indigo-200 font-mono text-[11px]">Turn ${c.turn_id} (${c.speaker || 'Candidate'}): "${escapeHtml(c.verbatim_quote.substring(0, 75))}..."</span>
        <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700">Verified ${Math.round(c.grounding_score*100)}%</span>
      </button>
    `).join("");
  } else {
    decisiveList.innerHTML = `<span class="text-slate-400 text-xs italic">No decisive citations logged.</span>`;
  }

  const dissentBox = document.getElementById("dissentItems");
  if (synthesis.dissenting_opinions && synthesis.dissenting_opinions.length > 0) {
    dissentBox.innerHTML = synthesis.dissenting_opinions.map(d => `
      <div class="bg-slate-900 p-2 rounded border border-slate-800">
        <strong class="text-slate-100 block">${escapeHtml(d.agent)} (${escapeHtml(d.role || '')}):</strong>
        <p class="text-slate-300 mt-0.5">${escapeHtml(d.dissent_summary)}</p>
      </div>
    `).join("");
  } else {
    dissentBox.innerHTML = `<span class="text-slate-400 italic">Unanimous consensus after calibration. Zero unresolved dissents.</span>`;
  }

  renderRadarChart(synthesis.calibrated_rubric_scores);
  lucide.createIcons();
}

function renderRadarChart(scores) {
  const ctx = document.getElementById("rubricRadarChart");
  if (!ctx) return;

  const labels = Object.keys(scores);
  const dataValues = Object.values(scores);

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  radarChartInstance = new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [{
        label: "Calibrated Dimension Score",
        data: dataValues,
        backgroundColor: "rgba(99, 102, 241, 0.25)",
        borderColor: "#818cf8",
        pointBackgroundColor: "#a5b4fc",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "#818cf8",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 10,
          ticks: { stepSize: 2, display: false },
          angleLines: { color: "#334155" },
          grid: { color: "#1e293b" },
          pointLabels: {
            color: "#e2e8f0",
            font: { size: 10, weight: "bold" }
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function setupWebSocket(sessionId) {
  if (socket) {
    socket.close();
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/${sessionId}`;
  
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    wsStatusDot.className = "inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
    wsStatusText.textContent = "WebSocket Live";
  };

  socket.onclose = () => {
    wsStatusDot.className = "inline-block w-2 h-2 rounded-full bg-rose-400";
    wsStatusText.textContent = "Disconnected";
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleSimulationEvent(data);
    } catch (e) {
      console.error("WS Parse error:", e);
    }
  };

  socket.onerror = (err) => console.log("WebSocket status:", err);
}

function handleSimulationEvent(event) {
  const { event_type, payload } = event;

  if (event_type === "SESSION_STATUS_CHANGED") {
    badgeSystemState.textContent = payload.status;
    announceA11y(`System status changed to ${payload.status}`);
  }
  else if (event_type === "AGENT_THINKING") {
    const card = document.getElementById(`card-${payload.agent_id}`);
    if (card) {
      card.querySelector(".status-box").innerHTML = `
        <span class="inline-flex items-center gap-1 text-indigo-300 font-semibold animate-pulse">
          <i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin" aria-hidden="true"></i> ${escapeHtml(payload.status)}
        </span>
      `;
      lucide.createIcons();
    }
  }
  else if (event_type === "AGENT_EVALUATION_COMPLETED") {
    renderAgentEvaluation(payload.agent_id, payload.evaluation);
  }
  else if (event_type === "PHASE_COMPLETED" && payload.phase === "PHASE_1_INDEPENDENT_EVALUATION") {
    independenceCertBanner.classList.remove("hidden");
    announceA11y("Phase 1 complete. 4-Agent Independence verified with zero cross-agent context leakage.");
  }
  else if (event_type === "DEBATE_ROUND_STARTED") {
    badgeActiveRound.textContent = `Round ${payload.round_number}: ${payload.title}`;
    highlightRoundStep(payload.round_number);
    announceA11y(`Debate Round ${payload.round_number} started: ${payload.title}`);
  }
  else if (event_type === "DEBATE_ARGUMENT_GENERATED") {
    appendDebateArgument(payload.argument);
  }
  else if (event_type === "SYNTHESIS_COMPLETED") {
    renderSynthesis(payload.synthesis);
    if (payload.synthesis.agent_calibrations) {
      renderOpinionEvolution(payload.synthesis.agent_calibrations);
    }
    announceA11y(`Final Delphi Synthesis completed. Final decision: ${payload.synthesis.final_decision}`);
  }
}

function highlightRoundStep(roundNum) {
  [stepRound1, stepRound2, stepRound3].forEach((el, idx) => {
    if (idx + 1 === roundNum) {
      el.className = "p-2 rounded-lg bg-indigo-950 border border-indigo-500 text-indigo-200 font-bold";
      el.setAttribute("aria-selected", "true");
    } else if (idx + 1 < roundNum) {
      el.className = "p-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-300";
      el.setAttribute("aria-selected", "false");
    } else {
      el.className = "p-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400";
      el.setAttribute("aria-selected", "false");
    }
  });
}

async function runSimulation() {
  btnRunSimulation.disabled = true;
  btnRunSimulation.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin" aria-hidden="true"></i> Running Panel...`;
  announceA11y("Multi-Agent Simulation started. Independent evaluations running in parallel.");
  lucide.createIcons();

  try {
    const res = await fetch(`/api/v1/sessions/${currentSessionId}/evaluate`, {
      method: "POST"
    });
    if (!res.ok) throw new Error("Evaluation trigger failed");
  } catch (err) {
    console.error("Simulation run failed:", err);
    announceA11y("Simulation run failed. Check server connection.");
  } finally {
    setTimeout(() => {
      btnRunSimulation.disabled = false;
      btnRunSimulation.innerHTML = `<i data-lucide="play" class="w-3.5 h-3.5 fill-current" aria-hidden="true"></i><span>Run Simulation</span>`;
      lucide.createIcons();
    }, 2500);
  }
}

function inspectCitation(citJsonStr) {
  try {
    lastFocusedElement = document.activeElement;
    const cit = typeof citJsonStr === "string" ? JSON.parse(citJsonStr) : citJsonStr;
    citModalClaim.textContent = cit.claim_supported;
    citModalTurnSpeaker.textContent = `Turn ${cit.turn_id} (${cit.speaker || "Candidate"}):`;
    citModalQuote.textContent = `"${cit.verbatim_quote}"`;
    citModalNotes.textContent = cit.verification_notes || "Grounded against interview transcript corpus.";
    
    if (cit.is_verified) {
      citModalVerifiedBadge.textContent = `VERIFIED EVIDENCE (${Math.round(cit.grounding_score * 100)}% GROUNDING)`;
      citModalVerifiedBadge.className = "text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-950 text-emerald-200 border border-emerald-700";
    } else {
      citModalVerifiedBadge.textContent = "UNVERIFIED / HALLUCINATED";
      citModalVerifiedBadge.className = "text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-950 text-rose-200 border border-rose-700";
    }

    citationModal.classList.remove("hidden");
    btnCloseCitModal.focus();
    highlightTranscriptTurn(cit.turn_id);
    announceA11y(`Opened Evidence Inspector for Turn ${cit.turn_id}. Status: ${cit.is_verified ? 'Verified' : 'Unverified'}.`);
  } catch (e) {
    console.error("Error inspecting citation:", e);
  }
}

function highlightTranscriptTurn(turnId) {
  transcriptDrawer.classList.remove("translate-x-full");
  btnToggleTranscript.setAttribute("aria-expanded", "true");
  const turnEl = document.getElementById(`turn-${turnId}`);
  if (turnEl) {
    document.querySelectorAll(".turn-highlight").forEach(el => el.classList.remove("turn-highlight"));
    turnEl.classList.add("turn-highlight");
    turnEl.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function getRecommendationClass(rec) {
  switch (rec) {
    case "STRONG_HIRE": return "text-emerald-300";
    case "HIRE": return "text-teal-300";
    case "LEAN_HIRE": return "text-blue-300";
    case "LEAN_REJECT": return "text-amber-300";
    case "STRONG_REJECT": return "text-rose-300";
    default: return "text-slate-300";
  }
}

function getVerdictBadgeClass(verdict) {
  switch (verdict) {
    case "STRONG_HIRE": return "bg-emerald-950 text-emerald-200 border border-emerald-600";
    case "HIRE": return "bg-teal-950 text-teal-200 border border-teal-600";
    case "LEAN_HIRE": return "bg-blue-950 text-blue-200 border border-blue-600";
    case "LEAN_REJECT": return "bg-amber-950 text-amber-200 border border-amber-600";
    case "STRONG_REJECT": return "bg-rose-950 text-rose-200 border border-rose-600";
    default: return "bg-slate-800 text-slate-100 border border-slate-700";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function escapeQuotes(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'");
}

// Start application
window.addEventListener("DOMContentLoaded", init);
