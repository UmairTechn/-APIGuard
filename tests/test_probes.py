import unittest
from probes.error_check import PATTERNS

class ErrorPatternTests(unittest.TestCase):
    def test_detects_simulated_database_error(self):
        text = "DatabaseError: simulated training failure"
        self.assertTrue(any(pattern.search(text) for pattern in PATTERNS))

    def test_clean_message_has_no_match(self):
        text = "Something went wrong. Please try again later."
        self.assertFalse(any(pattern.search(text) for pattern in PATTERNS))

if __name__ == "__main__":
    unittest.main()
