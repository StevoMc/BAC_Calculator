import unittest

from flake8.api import legacy as flake8


class TestCodeQuality(unittest.TestCase):
    def test_code_quality(self):
        """Test code quality with flake8."""
        style_guide = flake8.get_style_guide(ignore=["W503"])  # Example: ignoring W503
        report = style_guide.check_files(["main.py", "tests/test_app.py"])

        # Assert that there are fewer than 50 code quality issues
        self.assertTrue(
            report.total_errors < 50,
            f"Code quality issues found: {report.total_errors}",
        )


if __name__ == "__main__":
    unittest.main()
