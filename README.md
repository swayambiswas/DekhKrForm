# Multi-Agent AI Interview Panel Simulator

An enterprise-grade, distributed Multi-Agent AI Interview Panel Simulator that orchestrates 4 distinct AI evaluators through independent transcript evaluations, a structured multi-round debate arena, and evidence-grounded non-averaged consensus synthesis.

---

## Key Capabilities & Core Guarantees

1. **Strict Concurrency Isolation Barrier (Phase 1)**:
   - Evaluators (**Technical Architect**, **Culture & Leadership Lead**, **Hiring Manager**, **Bar Raiser & Risk Skeptic**) make pure independent LLM evaluations before seeing any other agent's opinion.
   - Guaranteed via `asyncio.gather` context segregation and cryptographically verified with SHA-256 execution hashes.

2. **Structured 3-Round Evidence-Grounded Debate (Phase 2)**:
   - **Round 1 (Divergence Mapping)**: Automatically identifies rubric variance and extracts primary contention topics.
   - **Round 2 (Cross-Examination & Rebuttal)**: Agents challenge opposing views and defend stances with mandatory transcript quotes.
   - **Round 3 (Epistemic Calibration)**: Agents formalize concessions, hardened positions, and delta confidence shifts.

3. **Delphi Evidence-Weighted Synthesis — No Score Averaging (Phase 3)**:
   - **Non-Averaged Synthesis**: Mathematical score averaging is strictly banned to prevent critical technical or integrity disqualifiers from being diluted.
   - **Evidence Credibility Weighting**: Agent influence is proportional to $\text{DomainExpertise} \times \text{Confidence} \times \text{GroundingScore}$.
   - **Bar Raiser Veto Circuit Breaker**: Substantiated red flags enforce a hard veto recommendation (`STRONG_REJECT`) regardless of secondary scores.
   - **Minority Dissent Preservation**: Unresolved objections and targeted onboarding risk mitigations are recorded in the final dossier.

4. **Evidence-Tracing Engine**:
   - Automated double-pass string & fuzzy matcher verifying every quote citation against indexed transcript turns.
   - Hallucinated citations are penalized and flagged in real time.
   - Interactive UI inspector allowing instantaneous spotlighting of transcript context.

5. **Real-Time Streaming Visual Dashboard**:
   - WebSocket streaming of agent thoughts, live debate turn-taking, interactive radar charts, and consensus verdicts.

---

## Architecture Overview

```
                        +-------------------------------------------------+
                        |   Frontend: Interactive Web UI (Static/Tailwind)|
                        +-------------------------------------------------+
                                      |                     ^
                          REST (/api) |                     | WebSocket Stream
                                      v                     |
                        +-------------------------------------------------+
                        |     FastAPI Orchestration & State Engine        |
                        +-------------------------------------------------+
                                                |
                        +-------------------------------------------------+
                        |   Phase 1: Zero-Knowledge Isolation Barrier     |
                        |   [Tech]       [Culture]     [Hiring Mgr] [Skeptic]|
                        +-------------------------------------------------+
                                                | (SHA-256 Verified)
                        +-------------------------------------------------+
                        |   Phase 2: Structured 3-Round Debate Engine     |
                        |   - Divergence -> Rebuttals -> Calibration      |
                        +-------------------------------------------------+
                                                |
                        +-------------------------------------------------+
                        |   Phase 3: Delphi Evidence Synthesis            |
                        |   - Non-Averaged Consensus + Bar Raiser Veto    |
                        +-------------------------------------------------+
```

---

## 4 Agent Personas

| Agent Persona | Name | Focus | Key Evaluation Rubric |
| :--- | :--- | :--- | :--- |
| **Agent 1: Technical Architect** | Dr. Elena Vance | System Depth & Correctness | Architecture, Concurrency, CAP Theorem, Edge-Case Resilience |
| **Agent 2: Culture & Leadership Lead** | Marcus Aurelius | Behavioral Dynamics & Ownership | Empathy, Handling Ambiguity, Blameless Culture, Mentorship |
| **Agent 3: Hiring Manager** | Priya Sharma | Domain & Execution • Practical Velocity & ROI | MVP Prioritization, Shipped Value, Customer Impact, CD/CI |
| **Agent 4: Bar Raiser & Risk Skeptic** | Kaelen Thorne | Adversarial Auditing & Veto | Unverified Claims, Inconsistency Detection, Overclaiming |

---

## QUICK START

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables (Optional)
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"   # Optional: for live Gemini LLM calls

# Linux / macOS
export GEMINI_API_KEY="your_api_key_here" # Optional: for live Gemini LLM calls
```
> **Offline Demo Mode**: If no API key is supplied, the simulator automatically runs in full offline heuristic mode using grounded domain benchmarks with zero external API dependencies.

### 3. Start the Backend Server
```bash
# Windows PowerShell
$env:PYTHONPATH="backend"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Linux / macOS
PYTHONPATH=backend python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open the Website
Open your browser and navigate to:
**`http://localhost:8000/`** (or **`http://127.0.0.1:8000/`**)

---

## Running Automated Tests

```bash
# Windows PowerShell
$env:PYTHONPATH="backend"; python -m pytest tests/ -v

# Linux / macOS
PYTHONPATH=backend python -m pytest tests/ -v
```

Test Coverage includes:
- `tests/unit/test_evidence_engine.py`: Verbatim quote verification, fuzzy matching, turn relocation, and hallucination rejection.
- `tests/unit/test_isolation_barrier.py`: 4-agent parallel execution, SHA-256 isolation hash verification.
- `tests/unit/test_debate_manager.py`: 3-round debate orchestration, divergence detection, stance calibration.
- `tests/unit/test_synthesis_engine.py`: Non-averaging logic, Bar Raiser veto circuit breakers, minority dissent preservation.
- `tests/integration/test_full_simulation.py`: End-to-end multi-agent pipeline simulation.

---

## API Endpoints

- `POST /api/v1/sessions` - Create interview simulation session
- `GET /api/v1/sessions/{id}` - Retrieve session state and transcript turns
- `POST /api/v1/sessions/{id}/evaluate` - Trigger 3-phase multi-agent evaluation pipeline
- `GET /api/v1/sessions/{id}/evaluations/independent` - Retrieve Phase 1 independent dossiers & isolation hashes
- `GET /api/v1/sessions/{id}/debate` - Retrieve multi-round debate history
- `GET /api/v1/sessions/{id}/synthesis` - Retrieve non-averaged final dossier
- `POST /api/v1/evidence/verify` - On-demand evidence citation verification
- `WS /api/v1/ws/{session_id}` - Real-time WebSocket streaming of agent thoughts, debate, and synthesis

---

## License
MIT License. Built for the PromptWars Multi-Agent AI Benchmark.

