from __future__ import annotations

import unittest

from lib.model_tier import is_high_risk
from lib.pilot import pick_smoke_task


class SmokeTaskPickTest(unittest.TestCase):
    def test_default_smoke_not_high_hint(self):
        task = pick_smoke_task()
        self.assertFalse(is_high_risk(task))
        self.assertIn("id", task)

    def test_reject_high_hint_task(self):
        with self.assertRaises(ValueError):
            pick_smoke_task(prefer_id="T-P05-006")


if __name__ == "__main__":
    unittest.main()
