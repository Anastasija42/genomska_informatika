from pydivsufsort import divsufsort
import collections

class FMIndexOptimized:
    """
    The queryable FM-Index. This class holds the final data structures 
    and contains all the logic for performing queries.
    """
    def __init__(self, text, bwt, counts, c_table, occ_checkpoints, sa_samples, occ_rate, sa_rate):
        self.text = text
        self.bwt = bwt
        self.counts = counts
        self.c_table = c_table
        self.occ_checkpoints = occ_checkpoints
        self.sa_samples = sa_samples
        self.occ_rate = occ_rate
        self.sa_rate = sa_rate
    
    def _get_occ(self, char, index):
        if char not in self.counts or index <= 0:
            return 0
        checkpoint_idx = index // self.occ_rate
        start_pos = checkpoint_idx * self.occ_rate
        count = self.occ_checkpoints[checkpoint_idx].get(char, 0)
        count += self.bwt[start_pos:index].count(char)
        return count

    def _lf_map(self, rank):
        char = self.bwt[rank]
        return self.c_table[char] + self._get_occ(char, rank)

    def _get_pos(self, rank):
        steps = 0
        curr_rank = rank
        while curr_rank not in self.sa_samples:
            curr_rank = self._lf_map(curr_rank)
            steps += 1
        # A safety check against unexpected infinite loops
        # if steps > len(self.bwt):
        #      raise RuntimeError("LF mapping cycle is unexpectedly long!")
        if steps > self.sa_rate:
            raise RuntimeError(
                f"LF mapping cycle is unexpectedly long! "
                f"Exceeded sa_rate ({self.sa_rate}) steps. "
            )


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
            start = self.c_table[char] + self._get_occ(char, start)
            end = self.c_table[char] + self._get_occ(char, end)

        if start >= end:
            return 0, []

        locations = sorted([self._get_pos(i) for i in range(start, end)])
        num_matches = len(locations)
        return num_matches, locations


class FMIndexBuilder:
    def __init__(self, text):
        if not text.endswith('$'):
            text += '$'
        self.text = text
        self.n = len(text)
        
        self._precompute()

    def _precompute(self):
        """Creates the suffix array and C-table."""
        print(f"--- Pre-computation - start ---")

        print(f"  Creating Suffix Array for text of length {self.n}...")
        self.sa = divsufsort(self.text)
        
        print("  Suffix Array created. Generating BWT...")
        self.bwt = "".join([self.text[self.sa[i] - 1] for i in range(self.n)])
        
        print("  BWT created. Creating 'C' Table...")
        self.counts = collections.Counter(self.bwt)
        self.c_table = {}
        total = 0
        for char in sorted(self.counts.keys()):
            self.c_table[char] = total
            total += self.counts[char]
            
        print("  'C' Table created.")
        print("--- Pre-computation - finished ---")


    def _create_occ_checkpoints(self, occ_rate):
        """Creates the occurrence checkpoints for a given rate."""
        print(f"  Creating 'Occurrence' checkpoints (rate={occ_rate})...")
        occ_checkpoints = []
        running_counts = {char: 0 for char in self.counts}
        for i, char in enumerate(self.bwt):
            if i % occ_rate == 0:
                occ_checkpoints.append(running_counts.copy())
            running_counts[char] += 1

        return occ_checkpoints
    
    def _create_sa_samples(self, sa_rate):
        """Creates the sampled suffix array for a given rate."""
        print(f"  Creating sampled Suffix Array (rate={sa_rate})...")
        return {i: sa_val for i, sa_val in enumerate(self.sa) if i % sa_rate == 0}

    def build(self, sa_rate=16, occ_rate=128):
        """
        Builds and returns a queryable FMIndex instance with the specified rates.
        """
        print(f"--- Building index with sa_rate={sa_rate}, occ_rate={occ_rate} ---")
        
        # Generate the parameter-dependent data structures
        occ_checkpoints = self._create_occ_checkpoints(occ_rate)
        sa_samples = self._create_sa_samples(sa_rate)
        
        print("Optimized FM-index created successfully.")
        
        # Create and return the final index object
        return FMIndexOptimized(
            text=self.text,
            bwt=self.bwt,
            counts=self.counts,
            c_table=self.c_table,
            occ_checkpoints=occ_checkpoints,
            sa_samples=sa_samples,
            occ_rate=occ_rate,
            sa_rate=sa_rate
        )
