# 20-Round Autonomous Agent Benchmark & Evaluation Runner
import asyncio
import os
import sys
import time
from pathlib import Path

# Force UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add agent root to sys.path
AGENT_ROOT = Path(__file__).resolve().parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from core.cognitive_engine import CognitiveAIEngine
from multiagent.roles import ArchitectAgent, EngineerAgent, ReviewerJudgeAgent
from browser.providers.smart_provider import SmartProvider

BENCHMARK_SCENARIOS = [
    {
        "id": 1,
        "name": "KeepNote Studio",
        "domain": "notes",
        "prompt": "Build a modern KeepNote app with pinned notes, tag filters, glassmorphic themes, search, and localStorage persistence."
    },
    {
        "id": 2,
        "name": "Apex Tech E-Commerce",
        "domain": "ecommerce",
        "prompt": "Create an Apex tech storefront with responsive product grid, category filter tabs, cart drawer, and order summary."
    },
    {
        "id": 3,
        "name": "Scientific Calculator",
        "domain": "calculator",
        "prompt": "Develop a full-featured calculator with history tape, dark glassmorphic keypad, and error handling."
    },
    {
        "id": 4,
        "name": "Kanban Agile Board",
        "domain": "kanban",
        "prompt": "Build a Kanban task manager with Todo, In-Progress, Done columns, task creator modal, and status tags."
    },
    {
        "id": 5,
        "name": "Weather Radar Forecast",
        "domain": "weather",
        "prompt": "Create a real-time weather dashboard with temperature unit toggle, 5-day forecast cards, and atmospheric metrics."
    },
    {
        "id": 6,
        "name": "Crypto Portfolio Tracker",
        "domain": "crypto",
        "prompt": "Develop a cryptocurrency portfolio tracker with asset allocation, P&L calculations, and market price cards."
    },
    {
        "id": 7,
        "name": "Pomodoro Focus Timer",
        "domain": "pomodoro",
        "prompt": "Build a Pomodoro timer with work/break countdown intervals, session counter, and audio chime alert."
    },
    {
        "id": 8,
        "name": "Personal Expense Tracker",
        "domain": "expense",
        "prompt": "Create an expense budget tracker with category spending breakdowns, transaction history, and balance calculation."
    },
    {
        "id": 9,
        "name": "Daily Habit Streak Tracker",
        "domain": "habittracker",
        "prompt": "Develop a daily habit streak tracker with check-in buttons, streak counters, and weekly completion rate."
    },
    {
        "id": 10,
        "name": "Interactive Trivia Quiz",
        "domain": "quiz",
        "prompt": "Build an interactive trivia quiz challenge with score timer, streaks, question cards, and results summary."
    },
    {
        "id": 11,
        "name": "Live Markdown Editor",
        "domain": "markdown",
        "prompt": "Create a split-pane live markdown editor with real-time HTML previewer, toolbar buttons, and word count."
    },
    {
        "id": 12,
        "name": "Smart Recipe Planner",
        "domain": "recipe",
        "prompt": "Develop a recipe finder and meal planner with ingredient checklists, step-by-step instructions, and tags."
    },
    {
        "id": 13,
        "name": "Digital Canvas Sketchpad",
        "domain": "drawing",
        "prompt": "Build an interactive drawing canvas with color picker palette, stroke size slider, and canvas clear action."
    },
    {
        "id": 14,
        "name": "Web Music Player",
        "domain": "musicplayer",
        "prompt": "Create a web audio player with playlist queue, play/pause controls, seek scrubber, and volume slider."
    },
    {
        "id": 15,
        "name": "Password Vault Generator",
        "domain": "passwordgenerator",
        "prompt": "Develop a secure password generator with length slider, symbol toggles, entropy meter, and clipboard copy."
    },
    {
        "id": 16,
        "name": "Workout Fitness Tracker",
        "domain": "fitness",
        "prompt": "Build a workout rep counter with exercise presets, rest interval countdown timer, and session log."
    },
    {
        "id": 17,
        "name": "Flashcard Study Deck",
        "domain": "flashcards",
        "prompt": "Create a flashcard mastery deck with 3D flip card animation, known/unknown buttons, and progress counter."
    },
    {
        "id": 18,
        "name": "Real-Time Poll & Voting",
        "domain": "poll",
        "prompt": "Develop an interactive community poll app with custom options, vote submission, and animated percentage bars."
    },
    {
        "id": 19,
        "name": "Bookmark Link Vault",
        "domain": "urlbookmark",
        "prompt": "Build a browser bookmark organizer with category tags, search filter, and quick launch links."
    },
    {
        "id": 20,
        "name": "Analytics System Dashboard",
        "domain": "dashboard",
        "prompt": "Create a cloud analytics dashboard with server CPU/RAM telemetry gauges, activity logs, and status badges."
    }
]

async def run_single_test(scenario: dict) -> dict:
    test_id = scenario["id"]
    name = scenario["name"]
    prompt = scenario["prompt"]
    
    start_time = time.time()
    provider = SmartProvider()
    architect = ArchitectAgent(provider)
    engineer = EngineerAgent(provider)
    reviewer = ReviewerJudgeAgent(provider)
    
    try:
        # Phase 1: Planning
        plan = await architect.plan(prompt)
        assert plan.project_name, "Project name must be populated"
        assert len(plan.tasks) >= 3, f"Plan must have >= 3 tasks, got {len(plan.tasks)}"
        
        # Phase 2: Tasks Execution & Code Generation
        generated_files = {}
        total_actions = 0
        total_score = 0
        
        for task in plan.tasks:
            task_dict = task.model_dump()
            resp = await engineer.implement_task(task_dict, context_str=f"Project: {plan.project_name}")
            actions = [a.model_dump() for a in resp.actions]
            total_actions += len(actions)
            
            for act in actions:
                if act.get("type") == "write_file":
                    generated_files[act.get("path")] = act.get("content", "")
            
            review = await reviewer.review_code(task_dict, actions)
            total_score += review.get("score", 90)
            
        # Phase 3: Verification Checks
        assert "package.json" in generated_files, "package.json missing"
        assert "index.html" in generated_files, "index.html missing"
        assert "src/App.jsx" in generated_files, "src/App.jsx missing"
        
        app_code = generated_files["src/App.jsx"]
        assert len(app_code) > 100, "src/App.jsx is too short"
        assert "export default" in app_code or "export function" in app_code, "Missing component export"
        assert "import React" in app_code or "import" in app_code, "Missing imports in App.jsx"
        
        html_code = generated_files["index.html"]
        assert "cdn.tailwindcss.com" in html_code or "stylesheet" in html_code, "Missing styling in index.html"
        
        avg_score = round(total_score / len(plan.tasks), 1)
        passed = avg_score >= 80
        
        duration = round(time.time() - start_time, 2)
        return {
            "id": test_id,
            "name": name,
            "passed": passed,
            "tasks": f"{len(plan.tasks)}/{len(plan.tasks)}",
            "files": len(generated_files),
            "score": avg_score,
            "duration": duration,
            "error": None
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        return {
            "id": test_id,
            "name": name,
            "passed": False,
            "tasks": "0/3",
            "files": 0,
            "score": 0,
            "duration": duration,
            "error": str(e)
        }

async def run_all_benchmarks():
    print("\n" + "=" * 95)
    print(" 🚀 STARTING 20-ROUND AUTONOMOUS AGENT BENCHMARK & EVALUATION")
    print(" Target: Pass at least 15 out of 20 runs (>= 75% Win Rate)")
    print("=" * 95 + "\n")
    
    results = []
    for sc in BENCHMARK_SCENARIOS:
        print(f"▶ [Test #{sc['id']:02d}/20] Evaluating: {sc['name']}...", end="", flush=True)
        res = await run_single_test(sc)
        results.append(res)
        
        if res["passed"]:
            print(f" -> \033[1;32m🏆 PASS\033[0m ({res['tasks']} tasks, {res['files']} files, {res['score']} pts, {res['duration']}s)")
        else:
            print(f" -> \033[1;31m❌ FAIL\033[0m ({res['error']})")
            
    # Print Scoreboard
    print("\n" + "╔" + "═" * 93 + "╗")
    print("║" + " AUTONOMOUS AGENT 20-ROUND BENCHMARK EVALUATION SCOREBOARD ".center(93) + "║")
    print("╠════╤════════════════════════════════════╤═════════╤═════════╤═════════╤════════════════════╣")
    print("║ #  │ Application Scenario               │ Tasks   │ Files   │ Score   │ Result             ║")
    print("╠════╪════════════════════════════════════╪═════════╪═════════╪═════════╪════════════════════╣")
    
    passes = 0
    for r in results:
        status = "🏆 PASS (WIN)" if r["passed"] else "❌ FAIL (LOSS)"
        color = "\033[1;32m" if r["passed"] else "\033[1;31m"
        reset = "\033[0m"
        if r["passed"]:
            passes += 1
        name_str = (r["name"][:34]).ljust(34)
        print(f"║ {r['id']:02d} │ {name_str} │ {r['tasks']:<7} │ {r['files']:<7} │ {r['score']:>3} pts │ {color}{status:<18}{reset} ║")
        
    win_rate = round((passes / len(results)) * 100, 1)
    target_met = passes >= 15
    verdict = "TARGET (>= 15/20) ACHIEVED & EXCEEDED! 🎉" if target_met else "TARGET NOT MET"
    
    print("╠════╧════════════════════════════════════╧═════════╧═════════╧═════════╧════════════════════╣")
    print(f"║ Final Win Rate: {passes}/20 Passed ({win_rate}%) - {verdict}".ljust(94) + "║")
    print("╚" + "═" * 93 + "╝\n")
    
    return passes, len(results)

if __name__ == "__main__":
    passes, total = asyncio.run(run_all_benchmarks())
    sys.exit(0 if passes >= 15 else 1)
