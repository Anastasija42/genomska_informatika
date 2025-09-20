import time
import sys
import os
import csv
from fm_index_basic import FMIndexBasic
from fm_index_optimized import FMIndexOptimized

OCC_RATES_TO_TEST = [32, 64, 128, 256, 512]
SA_RATES_TO_TEST = [4, 16, 64, 128, 256]
OUTPUT_CSV_FILE = 'results.csv'
DETAILED_LOG_FILE = 'analysis_log.txt'

def read_fasta(filepath):
    """Čita FASTA fajl i vraća celu sekvencu kao jedan string."""
    try:
        with open(filepath, 'r') as f:
            sequence_parts = []
            for line in f:
                if not line.startswith('>'):
                    sequence_parts.append(line.strip())
            return "".join(sequence_parts).upper()
    except FileNotFoundError:
        print(f"GREŠKA: Fajl nije pronađen na putanji: {filepath}")
        return None

def get_deep_size(obj, seen=None):
    """Rekurzivno pronalazi veličinu objekta u bajtovima."""
    size = sys.getsizeof(obj)
    if seen is None: seen = set()
    obj_id = id(obj)
    if obj_id in seen: return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_deep_size(v, seen) for v in obj.values()])
        size += sum([get_deep_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_deep_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_deep_size(i, seen) for i in obj])
    return size

def analyze_implementation(FMIndexClass, text, patterns, params={}):
    """
    Analizira jednu implementaciju.
    Vraća performanse i detalje o pronađenim poklapanjima.
    """
    print(f"--- Analiziranje: {FMIndexClass.__name__} sa parametrima {params}")

    start_time = time.perf_counter()
    fm_index = FMIndexClass(text, **params)
    build_time = time.perf_counter() - start_time

    mem_usage = get_deep_size(fm_index) / (1024 * 1024)

    match_details = []
    search_start_time = time.perf_counter()
    for p in patterns:
        num_matches, locations = fm_index.query(p)
        match_details.append({
            "pattern": p,
            "count": num_matches,
            "locations": locations
        })
    search_time = time.perf_counter() - search_start_time

    del fm_index

    return {
        "performance": {
            "build_time_s": build_time,
            "memory_mb": mem_usage,
            "total_search_time_s": search_time,
            "avg_search_time_ms": (search_time / len(patterns)) * 1000
        },
        "matches": match_details
    }



if __name__ == "__main__":
    csv_header = [
        "Dataset Name", "Algorithm", "Text Length",
        "occ_rate", "sa_rate", "Build Time (s)",
        "Index Size (MB)", "Total Search Time (s)", "Avg Search Time (ms)"
    ]
    with open(OUTPUT_CSV_FILE, 'w', newline='',  encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

    with open(DETAILED_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("="*50 + "\n")
        f.write("DETALJNI LOG ANALIZE PRETRAGE\n")
        f.write("="*50 + "\n")

    print(f"Kreirani fajlovi: '{OUTPUT_CSV_FILE}' i '{DETAILED_LOG_FILE}'")

    print("\n" + "="*80)
    print("DEO 1: KRATKA DEMONSTRACIJA NA MALOM PRIMERU")
    print("="*80)
    short_text = "abra_cadabra_abra_cadabra"
    short_patterns = ["abra", "_cadabra", "CAT"]

    for algo_name, algo_class, algo_params in [("Basic", FMIndexBasic, {}), ("Optimized", FMIndexOptimized, {'occ_rate': 128, 'sa_rate': 16})]:
        results = analyze_implementation(algo_class, short_text, short_patterns, algo_params)
        perf = results["performance"]
        matches = results["matches"]

        with open(OUTPUT_CSV_FILE, 'a', newline='',  encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Short Demo", algo_name, len(short_text),
                algo_params.get('occ_rate', "N/A"), algo_params.get('sa_rate', "N/A"),
                perf["build_time_s"], perf["memory_mb"],
                perf["total_search_time_s"], perf["avg_search_time_ms"]
            ])

        with open(DETAILED_LOG_FILE, 'a',  encoding='utf-8') as f:
            f.write(f"\n--- LOG: Short Demo | {algo_name} ---\n")
            for item in matches:
                locs_str = str(item['locations'][:5])
                if item['count'] > 5: locs_str += "..."
                f.write(f"  Patern: '{item['pattern']}' | Pronađeno: {item['count']} puta | Lokacije: {locs_str}\n")

    print("Kratka demonstracija završena i rezultati upisani.")


    print("\n" + "="*80)
    print("DEO 2: VELIKA ANALIZA PERFORMANSI SA RAZLIČITIM PARAMETRIMA")
    print("="*80)

    DATASETS = [
        {
            "name": "Coffea arabica",
            "filepath": "genomes/coffea_arabica_1c.fasta",
            "patterns": ["ATGCATG", "TCTCTCTA", "TTCACTACTCTCA"]
        },
        {
            "name": "Mus pahari",
            "filepath": "genomes/mus_pahari_x.fasta",
            "patterns": ["ATGATG", "CTCTCTA", "TCACTACTCTCA"]
        },
        {
            "name": "Platypus",
            "filepath": "genomes/platypus_x.fasta",
            "patterns": ["GCTGGACAGAGCTGGGTGAGGAGGT", "CAGCCCACCAAAGAGAGAAACCAA", "GATGTTGTGGCAGAGCTTGAAGATT"]
        }
    ]

    for dataset in DATASETS:
        print(f"\nUčitavam genom: {dataset['name']}...")
        genome_text = read_fasta(dataset["filepath"])
        if not genome_text: continue

        print(f"Genom učitan (dužina: {len(genome_text):,}). Počinje testiranje parametara...")

        for occ in OCC_RATES_TO_TEST:
            for sa in SA_RATES_TO_TEST:
                params = {'occ_rate': occ, 'sa_rate': sa}

                try:
                    results = analyze_implementation(FMIndexOptimized, genome_text, dataset["patterns"], params)
                    perf = results["performance"]
                    matches = results["matches"]

                    with open(OUTPUT_CSV_FILE, 'a', newline='',  encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            dataset["name"], "Optimized", len(genome_text),
                            occ, sa, perf["build_time_s"], perf["memory_mb"],
                            perf["total_search_time_s"], perf["avg_search_time_ms"]
                        ])

                    with open(DETAILED_LOG_FILE, 'a',  encoding='utf-8') as f:
                        f.write(f"\n--- LOG: {dataset['name']} | Optimized | occ_rate={occ}, sa_rate={sa} ---\n")
                        for item in matches:
                            locs_str = str(item['locations'][:5])
                            if item['count'] > 5: locs_str += "..."
                            f.write(f"  Patern: '{item['pattern']}' | Pronađeno: {item['count']} puta | Lokacije: {locs_str}\n")

                    print(f"  -> Završeno za occ_rate={occ}, sa_rate={sa}. Rezultati sačuvani.")

                except Exception as e:
                    print(f"  -> GREŠKA za occ_rate={occ}, sa_rate={sa}: {e}")

    print("\n" + "="*80)
    print("SVA ANALIZA JE ZAVRŠENA!")
    print(f"Sumarni rezultati su sačuvani u '{OUTPUT_CSV_FILE}'.")
    print(f"Detaljni rezultati pretrage su sačuvani u '{DETAILED_LOG_FILE}'.")
    print("="*80)