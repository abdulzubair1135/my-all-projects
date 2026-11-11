# AURA — Autonomous Local AI Research & Learning System

AURA is a fully local, autonomous AI research and learning system designed for model independence, hardware efficiency (optimized for NVIDIA RTX 2050 4GB VRAM), and continuous self-driven cognitive execution.

## Full System Architecture (Phases 1 – 9 Completed)

```text
               +----------------------------------+
               |     AURA Autonomous Scheduler    |
               +----------------------------------+
                                |
               +----------------------------------+
               |       Curiosity Engine           |
               |  (Discovers Knowledge Gaps)      |
               +----------------------------------+
                                |
               +----------------------------------+
               |   THINK → PLAN → EXECUTE → VERIFY|
               |         → REFLECT → STORE        |
               +----------------------------------+
                                |
       +------------------------+------------------------+
       |                        |                        |
+--------------+       +------------------+     +-------------------+
| Memory Store |       | Research Engine  |     | Code Experiment   |
| - Semantic   |       | - DDG Search     |     |   Sandbox         |
| - Episodic   |       | - Web Reader     |     | - Subprocess Exec |
| - Procedural |       | - Source Ranker  |     | - Result Record   |
| - Skill      |       | - Fact Verifier  |     | - Pass/Fail Track |
| - Graph      |       +------------------+     +-------------------+
+--------------+                |                        |
       |                        +------------------------+
       v                                                 v
+------------------------+                     +--------------------+
|  FastAPI Local Web     |                     | Git Checkpointed   |
|  Dashboard (Port 8000) |                     | Self-Improvement   |
+------------------------+                     +--------------------+
```

## System Capabilities Implemented

1. **Phase 1 — Core Cognitive Engine**:
   - Model Adapter decoupling AURA from LLMs (Ollama REST API + Mock fallback).
   - Model Router selecting model sizes (`0.6B-1.7B`, `4B`, `8B-9B`) based on task complexity and VRAM budget.
   - SQLite relational schema (`database/schema.sql`).
   - Planner, Task Queue, Executor, Critic, Reflection, Working Memory, Controller.

2. **Phase 2 — Multi-Tier Memory Architecture**:
   - Local Embedding Service & Vector Store (`memory/embedding_service.py`, `memory/vector_store.py`).
   - Semantic Memory (indexed facts), Episodic Memory (past lessons & fixes), Procedural Memory, Skill Memory, Knowledge Graph, and Self-Model awareness.

3. **Phase 3 — Research Engine**:
   - Web Search parsing (`research/search.py`).
   - Webpage content reader & text extraction (`research/webpage_reader.py`).
   - Source ranker boost by domain authority (`research/source_ranker.py`).
   - Fact verification & cross-checking (`research/verification.py`).

4. **Phase 4 — Autonomous Curiosity Engine**:
   - Discovers open knowledge gaps (`learning/knowledge_gap.py`).
   - Generates next candidate learning topics without user commands (`learning/curiosity.py`).
   - Continuous Autonomous Scheduler (`scheduler/scheduler.py`).

5. **Phase 5 — Media & Browser Automation**:
   - Playwright browser navigation with accessibility DOM extraction (`research/browser.py`).
   - YouTube caption & transcript extraction pipeline (`research/youtube_reader.py`).
   - PDF document reader (`research/pdf_reader.py`).

6. **Phase 6 — Computer Control & Perception**:
   - Desktop screenshot capture & screen change delta detection (`perception/screen.py`).
   - OCR text extraction (`perception/ocr.py`).
   - Mouse & keyboard automation gated by autonomy level checks (`computer/mouse.py`, `computer/keyboard.py`).

7. **Phase 7 — Coding Agent & Experiment Engine**:
   - Subprocess sandbox code execution (`coding/sandbox.py`).
   - Practical experiment engine tracking hypotheses, outputs, PASS/FAIL/ERROR, and lessons (`experiments/experiment_engine.py`).

8. **Phase 8 — Self-Evaluation & Daily Learning Reports**:
   - System performance metrics & success rate analytics (`evolution/self_evaluation.py`).
   - Structured Daily Learning Report generator (`evolution/report_generator.py`).

9. **Phase 9 — Controlled Self-Improvement**:
   - Git branch checkpointing, benchmark evaluation, and safe rollback (`evolution/self_improvement.py`).

10. **Local Web Dashboard**:
    - Real-time FastAPI dashboard on `http://127.0.0.1:8000` (`dashboard/app.py`).

---

## Running AURA

### 1. Run All 40 Unit & Integration Tests

```bash
python -m pytest -v
```
or double click **`run_tests.bat`**.

### 2. Run Interactive Launcher

Double click **`run_aura.bat`** or run:

```bash
run_aura.bat
```

### 3. Run Autonomous Curiosity Mode (No User Command Needed)

```bash
python main.py --autonomous --steps 5
```

### 4. Generate Daily Learning Report

```bash
python main.py --report
```
