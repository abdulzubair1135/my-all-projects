"""
AURA - Autonomous Local AI Research & Learning System.
Full End-to-End Autonomous Cognitive Core.
"""

import sys
import argparse
from config import config
from core.agent import Agent, agent
from scheduler.scheduler import autonomous_scheduler
from evolution.report_generator import report_generator
from core.context import context_manager
from core.logger import setup_logger

logger = setup_logger("Main")

def main():
    parser = argparse.ArgumentParser(description="AURA - Autonomous Local AI Research & Learning System")
    parser.add_argument("--goal", type=str, help="Explicit goal to set for AURA")
    parser.add_argument("--steps", type=int, default=5, help="Maximum cognitive steps to execute")
    parser.add_argument("--mock", action="store_true", help="Use Mock LLM backend for testing")
    parser.add_argument("--autonomous", action="store_true", help="Run in continuous autonomous curiosity mode")
    parser.add_argument("--report", action="store_true", help="Generate AURA Daily Learning Report")
    args = parser.parse_args()

    if args.mock:
        config.models.use_mock = True

    logger.info("Initializing AURA Autonomous Local AI System...")
    context_manager.start_session(f"sess_aura_{args.steps}")

    if args.report:
        report = report_generator.generate_report()
        print("\n" + report)
        context_manager.end_session()
        return

    if args.autonomous or not args.goal:
        logger.info("Starting AURA in AUTONOMOUS CURIOSITY MODE...")
        for step_i in range(args.steps):
            logger.info(f"--- Autonomous Cycle Step {step_i+1}/{args.steps} ---")
            res = autonomous_scheduler.run_autonomous_cycle()
            if not res:
                break
    else:
        logger.info(f"Setting explicit goal: '{args.goal}'")
        agent.set_goal(args.goal)
        results = agent.run_loop(max_steps=args.steps)
        logger.info(f"Goal execution completed. Executed {len(results)} steps.")

    # Generate end-of-session report
    print("\n" + report_generator.generate_report())
    context_manager.end_session()

if __name__ == "__main__":
    main()
