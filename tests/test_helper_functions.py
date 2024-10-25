import unittest

from main import (
    REDUCTION_FACTOR,
    Drink,
    calculate_adjusted_metabolism_rate,
    calculate_age_factor,
    calculate_bac,
    calculate_reduction_factor,
    calculate_time_to_sober,
    calculate_total_alcohol_in_liters,
    get_combined_drinks,
)


class TestHelperFunctions(unittest.TestCase):
    def test_calculate_age_factor(self):
        """Test age factor calculation."""
        self.assertEqual(calculate_age_factor(18), 1.0)
        self.assertEqual(calculate_age_factor(20), 1.0)
        self.assertAlmostEqual(calculate_age_factor(30), 0.99, places=2)
        self.assertAlmostEqual(calculate_age_factor(50), 0.97, places=2)

    # def test_calculate_reduction_factor(self):
    #     """Test reduction factor calculation for gender and age."""
    #     self.assertAlmostEqual(calculate_reduction_factor("male", 25), 0.99, places=2)
    #     self.assertAlmostEqual(calculate_reduction_factor("female", 40), 0.94, places=2)
    #     self.assertEqual(calculate_reduction_factor("unknown", 30), 1)

    # def test_calculate_bac(self):
    #     """Test BAC calculation."""
    #     self.assertAlmostEqual(calculate_bac(70, "male", 30, 20), 0.072, places=3)
    #     self.assertAlmostEqual(calculate_bac(55, "female", 25, 10), 0.123, places=3)

    # def test_calculate_adjusted_metabolism_rate(self):
    #     """Test adjusted metabolism rate calculation."""
    #     self.assertAlmostEqual(
    #         calculate_adjusted_metabolism_rate(30, 70), 0.015, places=3
    #     )
    #     self.assertAlmostEqual(
    #         calculate_adjusted_metabolism_rate(40, 80), 0.017, places=3
    #     )

    # def test_calculate_time_to_sober(self):
    #     """Test time to sober calculation."""
    #     self.assertAlmostEqual(calculate_time_to_sober(0.1, 70, 30), 0.67, places=2)
    #     self.assertAlmostEqual(calculate_time_to_sober(0.2, 60, 25), 1.25, places=2)

    # def test_calculate_total_alcohol_in_liters(self):
    #     """Test total alcohol content calculation."""
    #     drinks = [
    #         Drink(name="Beer", volume=500, unit="ml", alcohol=5),
    #         Drink(name="Wine", volume=200, unit="ml", alcohol=12),
    #     ]
    #     self.assertAlmostEqual(
    #         calculate_total_alcohol_in_liters(drinks), 0.045, places=3
    #     )

    # def test_get_combined_drinks(self):
    #     """Test drink combination and sorting by volume."""
    #     session = {
    #         "user_drinks": [
    #             {"name": "Beer", "volume": 500, "unit": "ml", "alcohol": 5}
    #         ],
    #         "custom_drinks": [
    #             {"name": "Wine", "volume": 200, "unit": "ml", "alcohol": 12}
    #         ],
    #     }
    #     session["user_drinks"] = [Drink(**drink) for drink in session["user_drinks"]]
    #     session["custom_drinks"] = [
    #         Drink(**drink) for drink in session["custom_drinks"]
    #     ]

    #     drinks = get_combined_drinks()  # Simulate session usage in the function

    #     self.assertEqual(len(drinks), 2)
    #     self.assertEqual(drinks[0].name, "Beer")  # Larger volume first
    #     self.assertEqual(drinks[1].name, "Wine")


if __name__ == "__main__":
    unittest.main()
