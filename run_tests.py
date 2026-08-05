import unittest
import os
from processor import process_file

class TestProcessor(unittest.TestCase):
    def test_process_csv(self):
        # This test requires DEEPSEEK_API_KEY to be set in the environment
        if "DEEPSEEK_API_KEY" not in os.environ:
            self.skipTest("DEEPSEEK_API_KEY not set")
        test_bytes = b"tenant,property,charge,due\nTestCo,Main Plaza,8000,2025-08-01"
        records = process_file(test_bytes)
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)
        rec = records[0]
        self.assertIn("title", rec)
        self.assertIn("status", rec)
        self.assertIn("due_date", rec)
        self.assertIsInstance(rec["details"], dict)
        # Status should be above_threshold:critical since 8000 > 5000
        self.assertEqual(rec["status"], "above_threshold:critical")
        # Title should be tenant name
        self.assertEqual(rec["title"], "TestCo")

if __name__ == "__main__":
    unittest.main()
