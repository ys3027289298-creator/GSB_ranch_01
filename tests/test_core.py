import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_register(self):
        state = core.new_game()
        self.assertTrue(core.register(state, "A1"))
        self.assertFalse(core.register(state, "A1"))

    def test_02_no_graze_when_overloaded(self):
        state = core.new_game()
        core.register(state, "A1")
        core.register(state, "A2")
        result = core.graze(state, "A3")
        self.assertFalse(result)

    def test_03_feed_exact(self):
        state = core.new_game()
        self.assertEqual(core.feed_days(state, "A1", 4), 3)

    def test_04_cancel_breed_refunds(self):
        state = core.new_game()
        state["feed"] = 90
        core.cancel_breed(state, "A1")
        self.assertEqual(state["feed"], 100)

    def test_05_no_treat_with_absent_vet(self):
        state = core.new_game()
        result = core.treat(state, "A1", "V2")
        self.assertFalse(result)

    def test_06_disease_deducts_once(self):
        state = core.new_game()
        core.register(state, "A1")
        core.disease(state)
        self.assertEqual(state["livestock"]["A1"]["health"], 90)

    def test_07_no_gain_without_water(self):
        state = core.new_game()
        state["water"] = 0
        result = core.gain(state, "A1")
        self.assertFalse(result)

    def test_08_load_preserves_stock(self):
        state = core.new_game()
        state["stock_id"] = 4
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["stock_id"], 4)


if __name__ == "__main__":
    unittest.main()
