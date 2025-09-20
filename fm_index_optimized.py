from pydivsufsort import divsufsort

class FMIndexOptimized:
    def __init__(self, text, occ_rate=128, sa_rate=16):
        if not text.endswith('$'):
            text += '$'
        self.text = text
        self.occ_rate = occ_rate
        self.sa_rate = sa_rate
        n = len(text)

        print(f"  1. Sufiksni Niz za tekst dužine {n}...")
        sa = divsufsort(text)
        print("  Sufiksni Niz napravljen. Generisanje BWT...")
        self.bwt = "".join([text[sa[i] - 1] for i in range(n)])
        print("  BWT kreiran.")

        print("  2. Kreiranje 'C' Tabela...")
        self.counts = {char: self.bwt.count(char) for char in set(self.bwt)}
        self.c_table = {}
        total = 0
        for char in sorted(self.counts.keys()):
            self.c_table[char] = total
            total += self.counts[char]
        print("  'C' Tabela kreirana.")

        print(f"  3. Kreiranje 'Occurrence' checkpoint-e (rate={self.occ_rate})...")
        self.occ_checkpoints = []
        running_counts = {char: 0 for char in self.counts}
        for i, char in enumerate(self.bwt):
            if i % self.occ_rate == 0:
                self.occ_checkpoints.append(running_counts.copy())
            running_counts[char] += 1
        print("  'Occurrence' checkpoint-i kreirani.")

        print(f"  4. Kreiranje uzorkovani Sufiksni Niz (rate={self.sa_rate})...")
        self.sa_samples = {i: sa_val for i, sa_val in enumerate(sa) if i % self.sa_rate == 0}
        print("Optimizovani FM-indeks je uspešno napravljen.")

    def get_occ(self, char, index):
        if char not in self.counts or index <= 0:
            return 0
        checkpoint_idx = index // self.occ_rate
        start_pos = checkpoint_idx * self.occ_rate
        count = self.occ_checkpoints[checkpoint_idx].get(char, 0)
        count += self.bwt[start_pos:index].count(char)
        return count

    def _lf_map(self, rank):
        char = self.bwt[rank]
        return self.c_table[char] + self.get_occ(char, rank)

    def _get_pos(self, rank):
        """
        Pronalazi originalnu poziciju za dati rank koristeći uzorkovani SA.
        """
        steps = 0
        curr_rank = rank
        while curr_rank not in self.sa_samples:
            curr_rank = self._lf_map(curr_rank)
            steps += 1
        if steps > len(self.bwt):
             raise RuntimeError("LF mapping cycle predugačak!")

        final_pos = (self.sa_samples[curr_rank] + steps) % len(self.bwt)

        return final_pos

    def query(self, pattern):
        if not pattern:
            return 0, []

        last_char = pattern[-1]
        if last_char not in self.c_table:
            return 0, []

        start = self.c_table[last_char]
        end = self.c_table[last_char] + self.counts[last_char]

        for char in reversed(pattern[:-1]):
            if char not in self.c_table:
                return 0, []
            if start >= end:
                return 0, []
            start = self.c_table[char] + self.get_occ(char, start)
            end = self.c_table[char] + self.get_occ(char, end)

        if start >= end:
            return 0, []

        locations = sorted([self._get_pos(i) for i in range(start, end)])
        num_matches = len(locations)
        return num_matches, locations