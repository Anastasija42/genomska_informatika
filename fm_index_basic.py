from pydivsufsort import divsufsort
import collections

class FMIndexBasic:
    def __init__(self, text):
        if not text.endswith('$'):
            text += '$'
        self.text = text
        n = len(text)

        print(f"  1. Suffix Array for text of length {n}...")
        sa = divsufsort(text)
        print("  Suffix Array created. Generating BWT...")
        self.bwt = "".join([text[sa[i] - 1] for i in range(n)])
        self.suffix_array = sa
        print("  BWT created.")

        self.counts = collections.Counter(self.bwt)

        print("  2. Creating 'First Occurrence' table...")
        first_col = sorted(self.text)
        self.first_occurrence = {char: first_col.index(char) for char in sorted(set(self.text))}

        print("  3. Creating full 'Occurrence' matrix...")
        self.occ_matrix = self._create_occ_matrix()
        print("Basic FM-index has been successfully created.")

    def _create_occ_matrix(self):
        """
        Creates and returns the complete Occ matrix.
        This is memory and time inefficient.
        """
        occ = {char: [0] * (len(self.bwt) + 1) for char in self.text}
        for i, char in enumerate(self.bwt):
            for c in occ:
                occ[c][i+1] = occ[c][i]
            occ[char][i+1] += 1
        return occ

    def query(self, pattern):
        """
        Performs 'backward search' using full matrices.
        """
        if not pattern:
            return 0, []

        last_char = pattern[-1]
        if last_char not in self.first_occurrence:
            return 0, []

        start = self.first_occurrence[last_char]
        end = self.first_occurrence[last_char] + self.counts[last_char]

        for char in reversed(pattern[:-1]):
            if char not in self.first_occurrence:
                return 0, []
            if start >= end:
                return 0, []

            start = self.first_occurrence[char] + self.occ_matrix[char][start]
            end = self.first_occurrence[char] + self.occ_matrix[char][end]

        if start >= end:
            return 0, []

        locations = sorted([self.suffix_array[i] for i in range(start, end)])
        num_matches = len(locations)
        return num_matches, locations