import unittest
from fm_index_basic import FMIndexBasic
from fm_index_optimized import FMIndexOptimized

TEST_TEXT = "abra_cadabra_abra_cadabra$"

class BaseFMIndexTests:
    """
    Base class for FM-Index tests.
    Subclasses must define FMIndexClass.
    """
    FMIndexClass = None
    fm_index = None

    @classmethod
    def setUpClass(cls):
        """
        This method is called ONCE before all tests in the class.
        The unittest runner will call it automatically.
        """
        if cls is BaseFMIndexTests:
            raise unittest.SkipTest("Skipping base test class")

        if not cls.FMIndexClass:
            raise TypeError("FMIndexClass must be defined in the subclass.")

        print(f"\n--- Creating index for testing class: {cls.FMIndexClass.__name__} ---")
        cls.fm_index = cls.FMIndexClass(TEST_TEXT)

    def test_pattern_found_multiple_times(self):
        """Tests a pattern that appears multiple times."""
        pattern = "abra"
        expected_locations = [0, 8, 13, 21]
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, len(expected_locations))
        self.assertCountEqual(locations, expected_locations, "Locations for 'abra' do not match")

    def test_pattern_found_once(self):
        """Tests a pattern that appears exactly once."""
        pattern = "_cadabra$"
        expected_locations = [17]
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, len(expected_locations))
        self.assertCountEqual(locations, expected_locations, "Locations for '_cadabra$' do not match")

    def test_pattern_not_found(self):
        """Tests a pattern that does not exist in the text."""
        pattern = "CAT"
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, 0)
        self.assertEqual(len(locations), 0, "A non-existent pattern 'CAT' was found")

    def test_pattern_is_single_character(self):
        """Tests the search for a single character."""
        pattern = "c"
        expected_locations = [5, 18]
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, len(expected_locations))
        self.assertCountEqual(locations, expected_locations, "Locations for 'c' do not match")

    def test_pattern_with_invalid_character(self):
        """Tests a pattern containing a character not present in the text."""
        pattern = "abXra"
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, 0)
        self.assertEqual(len(locations), 0, "A pattern with a non-existent character 'X' was found")

class TestFMIndexBasic(BaseFMIndexTests, unittest.TestCase):
    """Runs all tests from BaseFMIndexTests on the FMIndexBasic class."""
    FMIndexClass = FMIndexBasic

class TestFMIndexOptimized(BaseFMIndexTests, unittest.TestCase):
    """Runs all tests from BaseFMIndexTests on the FMIndexOptimized class."""
    FMIndexClass = FMIndexOptimized

if __name__ == '__main__':
    unittest.main()