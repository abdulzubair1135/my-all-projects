"""
Unit tests for AURA Working Memory module.
"""

import unittest
from memory.working_memory import WorkingMemory, ContextStep

class TestWorkingMemory(unittest.TestCase):
    def test_working_memory_sliding_window(self):
        wm = WorkingMemory(max_items=3)
        wm.set_active_goal("g1", "Goal 1")
        wm.set_active_task("t1", "Task 1")

        for i in range(5):
            wm.add_step(ContextStep(
                step_id=f"step_{i}",
                action="test",
                input_data=f"in_{i}",
                output_data=f"out_{i}",
                status="success",
                timestamp="now"
            ))

        self.assertEqual(len(wm.history), 3)
        self.assertEqual(wm.history[0].step_id, "step_2")
        self.assertEqual(wm.history[-1].step_id, "step_4")

    def test_context_summary(self):
        wm = WorkingMemory()
        wm.set_active_goal("g1", "Goal 1")
        summary = wm.get_context_summary()
        self.assertIn("Goal 1", summary)

if __name__ == "__main__":
    unittest.main()
