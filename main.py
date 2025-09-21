import time
import sys
import os
import csv
from fm_index_basic import FMIndexBasic
from fm_index_optimized import FMIndexOptimized, FMIndexBuilder

# --- Configuration ---
OCC_RATES_TO_TEST = [32, 64, 128, 256, 512]
SA_RATES_TO_TEST = [4, 16, 64, 128, 256]
OUTPUT_CSV_FILE = 'results_2.csv'
DETAILED_LOG_FILE = 'analysis_log_2.txt'

DATASETS = [
        {"name": "Coffea arabica", "filepath": "genomes/coffea_arabica_1c.fasta", "patterns": ["ATGCATG", "TCTCTCTA", "TTCACTACTCTCA"]},
        {"name": "Mus pahari", "filepath": "genomes/mus_pahari_x.fasta", "patterns": ["ATGATG", "CTCTCTA", "TCACTACTCTCA"]},
        {"name": "Platypus", "filepath": "genomes/platypus_x.fasta", "patterns": ["GCAGTGG", "ACAAAGGGCAAGAAGAA", "GATGTTGTGGCAGAGCTTGAAGATT"]}
    ]

# --- Utility functions ---
def read_fasta(filepath):
    """Reads a FASTA file and returns the entire sequence as a single string."""
    try:
        with open(filepath, 'r') as f:
            sequence_parts = [line.strip() for line in f if not line.startswith('>')]
            return "".join(sequence_parts).upper()
    except FileNotFoundError:
        print(f"ERROR: File not found at path: {filepath}")
        return None


def get_deep_size(obj, seen=None):
    """Recursively finds the size of an object in bytes."""
    size = sys.getsizeof(obj)
    if seen is None: seen = set()
    obj_id = id(obj)
    if obj_id in seen: return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum(get_deep_size(v, seen) for v in obj.values())
        size += sum(get_deep_size(k, seen) for k in obj.keys())
    elif hasattr(obj, '__dict__'):
        size += get_deep_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_deep_size(i, seen) for i in obj)
    return size


# --- Analysis Functions ---

def _analyze_instance(fm_index, patterns):
    """Internal helper: Analyzes a pre-built fm_index instance."""

    print(f"  Calculating memory usage for {fm_index.__class__.__name__}...")
    mem_usage = get_deep_size(fm_index) / (1024 * 1024)
    
    print(f"  Searching started...")
    
    match_details = []
    total_search_time = 0
    
    for p in patterns:
        query_start_time = time.perf_counter()
        num_matches, locations = fm_index.query(p)
        query_end_time = time.perf_counter()
        query_duration_s = query_end_time - query_start_time
        total_search_time += query_duration_s
        match_details.append({
            "pattern": p, "count": num_matches, "locations": locations,
            "search_time_ms": query_duration_s * 1000
        })

    print(f"  Searching finished in {total_search_time:.2f} seconds.")
    
    return {
        "performance": {"memory_mb": mem_usage, "avg_search_time_ms": total_search_time / len(patterns) * 1000},
        "matches": match_details
    }


def analyze_implementation(FMIndexClass, text, patterns, params={}):
    """Builds an index from scratch and analyzes it."""

    print(f"\n--- Analyzing: {FMIndexClass.__name__} with parameters {params}")
    
    if FMIndexClass == FMIndexOptimized:
        builder = FMIndexBuilder(text)
        start_time = time.perf_counter()
        fm_index = builder.build(**params)
        build_time = time.perf_counter() - start_time
    else:
        start_time = time.perf_counter()
        fm_index = FMIndexClass(text, **params)
        build_time = time.perf_counter() - start_time
    
    analysis_results = _analyze_instance(fm_index, patterns)
    
    del fm_index
    
    analysis_results["performance"]["build_time_ms"] = build_time * 1000
    
    return analysis_results


def analyze_from_builder(builder, patterns, params={}):
    """Builds an index from a pre-existing builder and analyzes it."""

    print(f"\n--- Analyzing from builder: FMIndexOptimized with parameters {params}")
    
    start_time = time.perf_counter()
    fm_index = builder.build(**params)
    build_time = time.perf_counter() - start_time
    analysis_results = _analyze_instance(fm_index, patterns)
    
    del fm_index
    
    analysis_results["performance"]["build_time_ms"] = build_time * 1000
    
    return analysis_results


# --- Logging and Setup Functions ---

def setup_output_files(max_patterns):
    """Creates and initializes the CSV and log files."""
    csv_header = [
        "Dataset Name", "Algorithm", "Text Length",
        "Pre-computation Time (ms)", "occ_rate", "sa_rate", "Final Build Time (ms)",
        "Avg Search Time (ms)", "Index Size (MB)"
    ]
    for i in range(1, max_patterns + 1):
        csv_header.extend([f"Pattern_{i}", f"P{i}_Occurrences", f"P{i}_Search_Time_ms"])
    
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(csv_header)
    
    with open(DETAILED_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("="*50 + "\nDETAILED SEARCH ANALYSIS LOG\n" + "="*50 + "\n")
    print(f"Files created: '{OUTPUT_CSV_FILE}' and '{DETAILED_LOG_FILE}'")


def log_results_to_csv(common_data, matches, max_patterns):
    """Formats and writes a single result row to the main CSV file."""
    pattern_specific_data = []
    for item in matches:
        pattern_specific_data.extend([item["pattern"], item["count"], item["search_time_ms"]])
    
    padding_needed = max_patterns - len(matches)
    if padding_needed > 0:
        pattern_specific_data.extend(['N/A'] * (padding_needed * 3))
    
    with open(OUTPUT_CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(common_data + pattern_specific_data)


def log_details_to_file(log_header, matches):
    """Writes the detailed match locations to the log file."""
    with open(DETAILED_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n--- LOG: {log_header} ---\n")
        for item in matches:
            locs_str = str(item['locations'][:5])
            if item['count'] > 5: locs_str += "..."
            f.write(f"  Pattern: '{item['pattern']}' | Found: {item['count']} times | Locations: {locs_str}\n")


# --- Function to run simple short demo ---

def run_short_demo(max_patterns):
    """Runs the short demonstration for both Basic and Optimized implementations."""
    print("\n" + "="*80 + "\nPART 1: SHORT DEMONSTRATION ON A SMALL EXAMPLE\n" + "="*80)
    short_text = "abra_cadabra_abra_cadabra"
    short_patterns = ["abra", "_cadabra", "CAT"]

    for algo_name, algo_class, algo_params in [("Basic", FMIndexBasic, {}), ("Optimized", FMIndexOptimized, {'occ_rate': 128, 'sa_rate': 16})]:
        results = analyze_implementation(algo_class, short_text, short_patterns, algo_params)
        perf = results["performance"]
        
        common_data = [
            "Short Demo", algo_name, len(short_text), "N/A",
            algo_params.get('occ_rate', "N/A"), algo_params.get('sa_rate', "N/A"),
            perf["build_time_ms"], perf["avg_search_time_ms"], perf["memory_mb"]
        ]
        log_results_to_csv(common_data, results["matches"], max_patterns)
        log_details_to_file(f"Short Demo | {algo_name}", results["matches"])

    print("Short demonstration finished and results written.")


# --- Function to run analyzes on DATASET ---

def run_large_analysis(datasets, max_patterns, run_basic=False):
    """Runs the full performance analysis across all datasets and parameters."""
    print("\n" + "="*80 + "\nPART 2: LARGE PERFORMANCE ANALYSIS WITH DIFFERENT PARAMETERS\n" + "="*80)
    
    for dataset in datasets:
        print(f"\nLoading genome: {dataset['name']}...")
        genome_text = read_fasta(dataset["filepath"])
        if not genome_text: continue
        
        print(f"Genome loaded (length: {len(genome_text):,}).")
        if run_basic:
            # Basic algorithm
            print("\n--- Running analysis for Basic Implementation ---")
            try:
                # Use analyze_implementation which handles the Basic class directly
                results = analyze_implementation(FMIndexBasic, genome_text, dataset["patterns"], {})
                perf = results["performance"]

                # Prepare data for logging, using "N/A" for non-applicable fields
                common_data = [
                    dataset["name"], "Basic", len(genome_text),
                    "N/A",  # Pre-computation Time
                    "N/A",  # occ_rate
                    "N/A",  # sa_rate
                    perf["build_time_s"],
                    perf["memory_mb"]
                ]
                log_results_to_csv(common_data, results["matches"], max_patterns)
                log_details_to_file(f"{dataset['name']} | Basic", results["matches"])

                print("  -> Finished baseline for Basic. Results saved.")
            except Exception as e:
                print(f"  -> ERROR during Basic implementation analysis: {e}") 

        # Optimized algorithm
        print("\n--- Starting analysis for Optimized Implementation ---")
        precomp_start_time = time.perf_counter()
        builder = FMIndexBuilder(genome_text)
        precomputation_time = time.perf_counter() - precomp_start_time
        print(f"Pre-computation finished in {precomputation_time:.2f} s. Starting parameter testing...")

        total_tests = len(OCC_RATES_TO_TEST) * len(SA_RATES_TO_TEST)
        for i, (occ, sa) in enumerate([(o, s) for o in OCC_RATES_TO_TEST for s in SA_RATES_TO_TEST], 1):
            params = {'occ_rate': occ, 'sa_rate': sa}
            try:
                results = analyze_from_builder(builder, dataset["patterns"], params)
                perf = results["performance"]
                
                common_data = [
                    dataset["name"], "Optimized", len(genome_text),
                    precomputation_time, occ, sa, 
                    perf["build_time_ms"], perf["avg_search_time_ms"], perf["memory_mb"]
                ]
                log_results_to_csv(common_data, results["matches"], max_patterns)
                log_details_to_file(f"{dataset['name']} | Optimized | occ={occ}, sa={sa}", results["matches"])
                
                print(f"  -> Finished {i}/{total_tests} for occ_rate={occ}, sa_rate={sa}. Results saved.")
            except Exception as e:
                print(f"  -> ERROR for occ_rate={occ}, sa_rate={sa}: {e}")



if __name__ == "__main__":
    
    max_patterns = max(len(d["patterns"]) for d in DATASETS)
    
    setup_output_files(max_patterns)
    
    run_short_demo(max_patterns)
    run_large_analysis(DATASETS, max_patterns)

    print("\n" + "="*80 + "\nALL ANALYSIS IS COMPLETE!\n" +
          f"Summary results are saved in '{OUTPUT_CSV_FILE}'.\n" +
          f"Detailed search results are saved in '{DETAILED_LOG_FILE}'.\n" + "="*80)