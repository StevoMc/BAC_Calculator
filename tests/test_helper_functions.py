import unittest

from main import (
    DRINKS,
    REDUCTION_FACTOR,
    Drink,
    calculate_adjusted_metabolism_rate,
    calculate_age_factor,
    calculate_bac,
    calculate_reduction_factor,
    calculate_time_to_sober,
    calculate_total_alcohol_in_grams,
    get_combined_drinks,
)


class TestHelperFunctions(unittest.TestCase):
    def test_calculate_age_factor(self):
        """Test age factor calculation."""
        self.assertEqual(calculate_age_factor(18), 1.0)
        self.assertEqual(calculate_age_factor(20), 1.0)
        self.assertAlmostEqual(calculate_age_factor(30), 0.99, places=2)
        self.assertAlmostEqual(calculate_age_factor(50), 0.97, places=2)

    def test_calculate_reduction_factor(self):
        """Test reduction factor calculation for gender and age."""
        self.assertAlmostEqual(calculate_reduction_factor("male", 18), 0.7, places=2)
        self.assertAlmostEqual(calculate_reduction_factor("male", 25), 0.693, places=2)
        self.assertAlmostEqual(
            calculate_reduction_factor("female", 40), 0.588, places=2
        )
        self.assertEqual(calculate_reduction_factor("unknown", 20), 0.7)

    def test_calculate_bac(self):
        """Test BAC calculation."""
        self.assertAlmostEqual(
            calculate_bac(
                70,
                "male",
                18,
                40,
            ),
            0.694,
            places=3,
        )
        self.assertAlmostEqual(calculate_bac(55, "female", 25, 10), 0.26, places=3)

    def test_calculate_adjusted_metabolism_rate(self):
        """Test adjusted metabolism rate calculation."""
        self.assertAlmostEqual(
            calculate_adjusted_metabolism_rate(30, 70), 0.15, places=3
        )
        self.assertAlmostEqual(
            calculate_adjusted_metabolism_rate(40, 80), 0.17, places=3
        )

    def test_calculate_time_to_sober(self):
        """Test time to sober calculation."""
        self.assertAlmostEqual(calculate_time_to_sober(0.1, 70, 20), 0.67, places=2)
        self.assertAlmostEqual(calculate_time_to_sober(1, 70, 20), 6.67, places=2)
        self.assertAlmostEqual(calculate_time_to_sober(0.2, 60, 20), 1.54, places=2)

    def test_calculate_total_alcohol_in_liters(self):
        """Test total alcohol content calculation."""
        drinks = [
            Drink(name="Beer", volume=500, unit="ml", alcohol=5),
            Drink(name="Wine", volume=200, unit="ml", alcohol=12),
        ]
        self.assertAlmostEqual(
            calculate_total_alcohol_in_grams(drinks), 38.67, places=3
        )


if __name__ == "__main__":
    unittest.main()
