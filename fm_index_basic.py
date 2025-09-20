from pydivsufsort import divsufsort

class FMIndexBasic:
    def __init__(self, text):
        if not text.endswith('$'):
            text += '$'
        self.text = text
        n = len(text)

        print(f"  1. Sufiksni Niz za tekst dužine {n}...")
        sa = divsufsort(text)
        print("  Sufiksni Niz napravljen. Generisanje BWT...")
        self.bwt = "".join([text[sa[i] - 1] for i in range(n)])
        self.suffix_array = sa
        print("  BWT kreiran.")

        self.counts = {char: self.bwt.count(char) for char in set(self.bwt)}

        print("  2. Kreiranje 'First Occurrence' tabele...")
        first_col = sorted(self.text)
        self.first_occurrence = {char: first_col.index(char) for char in sorted(set(self.text))}

        print("  3. Kreiranje pune 'Occurrence' matrice...")
        self.occ_matrix = self._create_occ_matrix()
        print("Osnovni FM-indeks je uspešno napravljen.")

    def _create_occ_matrix(self):
        """
        Kreira i vraća kompletnu Occ matricu.
        Ovo je memorijski i vremenski neefikasno.
        """
        occ = {char: [0] * (len(self.bwt) + 1) for char in self.text}
        for i, char in enumerate(self.bwt):
            for c in occ:
                occ[c][i+1] = occ[c][i]
            occ[char][i+1] += 1
        return occ

    def query(self, pattern):
        """
        Vrši 'backward search' koristeći pune matrice.
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