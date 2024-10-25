import unittest

from main import Drink, User


class TestModels(unittest.TestCase):
    def test_user_model(self):
        """Test the User model."""
        user = User(name="Alice", weight=65, age=34, gender="female")

        # Test attributes
        self.assertEqual(user.name, "Alice", "Expected 'Alice'")
        self.assertEqual(user.weight, 65, "Expected 65")
        self.assertEqual(user.age, 34, "Expected 34")
        self.assertEqual(user.gender, "female", "Expected 'female'")

        # Test string representation
        self.assertEqual(
            str(user),
            "Alice (34 years, female, 65 Kg)",
            "Unexpected string representation",
        )

        # Test equality
        user2 = User(name="Alice", weight=65, age=34, gender="female")
        self.assertEqual(user, user2, "Expected equality")

    def test_drink_model(self):
        """Test the Drink model."""
        drink = Drink(name="Beer", volume=500, unit="ml", alcohol=5)

        # Test attributes
        self.assertEqual(drink.name, "Beer", "Expected 'Beer'")
        self.assertEqual(drink.volume, 500, "Expected 500")
        self.assertEqual(drink.alcohol, 5, "Expected 5")
        self.assertEqual(drink.unit, "ml", "Expected 'ml'")

        # Test string representation
        self.assertEqual(
            str(drink), "Beer (500 ml, 5%)", "Unexpected string representation"
        )

        drink2 = Drink(name="Beer", volume=2000, unit="ml", alcohol=5)
        self.assertEqual(drink2.name, "Beer", "Expected 'Beer'")
        self.assertEqual(drink2.volume, 2, "Expected 2")
        self.assertEqual(drink2.alcohol, 5, "Expected 5")
        self.assertEqual(drink2.unit, "L", "Expected 'L'")

        # Test inequality
        self.assertNotEqual(drink, drink2, "Expected inequality")


if __name__ == "__main__":
    unittest.main()
