import unittest
from fm_index_basic import FMIndexBasic
from fm_index_optimized import FMIndexOptimized

TEST_TEXT = "abra_cadabra_abra_cadabra$"

class BaseFMIndexTests:
    FMIndexClass = None
    fm_index = None

    @classmethod
    def setUpClass(cls):
        """
        Ova metoda se poziva JEDNOM pre svih testova.
        unittest runner će je pozvati automatski.
        """
        if cls is BaseFMIndexTests:
            raise unittest.SkipTest("Preskakanje bazne test klase")

        if not cls.FMIndexClass:
            raise TypeError("FMIndexClass mora biti definisan u podklasi.")

        print(f"\n--- Kreiranje indeks za testiranje klase: {cls.FMIndexClass.__name__} ---")
        cls.fm_index = cls.FMIndexClass(TEST_TEXT)

    def test_pattern_found_multiple_times(self):
        """Testira patern koji se pojavljuje više puta."""
        pattern = "abra"
        expected_locations = [0, 8, 13, 21]
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, len(expected_locations))
        self.assertCountEqual(locations, expected_locations, "Lokacije za 'abra' se ne poklapaju")

    def test_pattern_found_once(self):
        """Testira patern koji se pojavljuje tačno jednom."""
        pattern = "_cadabra$"
        expected_locations = [17]
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, len(expected_locations))
        self.assertCountEqual(locations, expected_locations, "Lokacije za '_cadabra$' se ne poklapaju")

    def test_pattern_not_found(self):
        """Testira patern koji ne postoji u tekstu."""
        pattern = "CAT"
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, 0)
        self.assertEqual(len(locations), 0, "Pronađen je nepostojeći patern 'CAT'")

    def test_pattern_is_single_character(self):
        """Testira pretragu jednog karaktera."""
        pattern = "c"
        expected_locations = [5, 18]
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, len(expected_locations))
        self.assertCountEqual(locations, expected_locations, "Lokacije za 'c' se ne poklapaju")

    def test_pattern_with_invalid_character(self):
        """Testira patern koji sadrži karakter kog nema u tekstu."""
        pattern = "abXra"
        num_matches, locations = self.fm_index.query(pattern)
        self.assertEqual(num_matches, 0)
        self.assertEqual(len(locations), 0, "Pronađen je patern sa nepostojećim karakterom 'X'")

class TestFMIndexBasic(BaseFMIndexTests, unittest.TestCase):
    """Pokreće sve testove iz BaseFMIndexTests nad FMIndexBasic klasom."""
    FMIndexClass = FMIndexBasic

class TestFMIndexOptimized(BaseFMIndexTests, unittest.TestCase):
    """Pokreće sve testove iz BaseFMIndexTests nad FMIndexOptimized klasom."""
    FMIndexClass = FMIndexOptimized

if __name__ == '__main__':
    unittest.main()