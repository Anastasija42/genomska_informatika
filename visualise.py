import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

CSV_FILE = 'results.csv'
PLOTS_DIRECTORY = 'plots'

def create_plots_for_dataset(df, dataset_name):
    """
    Kreira i čuva 2x2 set grafikona za jedan specifičan set podataka (genom).
    """
    print(f"--- Kreiranje grafikona za: {dataset_name} ---")

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 14))
    fig.suptitle(f'Analiza Performansi FM-Indeksa za: {dataset_name}', fontsize=20, weight='bold')

    ax1 = axes[0, 0]
    sns.lineplot(
        data=df,
        x='occ_rate',
        y='Avg Search Time (ms)',
        hue='sa_rate',
        marker='o',
        palette='viridis',
        ax=ax1
    )
    ax1.set_title('Vreme pretrage u zavisnosti od Occ Rate', fontsize=14, weight='bold')
    ax1.set_xlabel('Checkpoint Interval (occ_rate)', fontsize=12)
    ax1.set_ylabel('Prosečno vreme pretrage (ms)', fontsize=12)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax1.legend(title='SA Rate')

    ax2 = axes[0, 1]
    sns.lineplot(
        data=df,
        x='sa_rate',
        y='Index Size (MB)',
        hue='occ_rate',
        marker='s',
        palette='plasma',
        ax=ax2
    )
    ax2.set_title('Veličina indeksa u zavisnosti od SA Rate', fontsize=14, weight='bold')
    ax2.set_xlabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)
    ax2.set_ylabel('Veličina indeksa (MB)', fontsize=12)
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax2.legend(title='Occ Rate')

    ax3 = axes[1, 0]
    pivot_mem = df.pivot(index='sa_rate', columns='occ_rate', values='Index Size (MB)')
    sns.heatmap(
        pivot_mem,
        annot=True,
        fmt=".1f",
        cmap="Greens",
        linewidths=.5,
        ax=ax3
    )
    ax3.set_title('Trade-off: Veličina indeksa (MB)', fontsize=14, weight='bold')
    ax3.set_xlabel('Checkpoint Interval (occ_rate)', fontsize=12)
    ax3.set_ylabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)

    ax4 = axes[1, 1]
    pivot_time = df.pivot(index='sa_rate', columns='occ_rate', values='Avg Search Time (ms)')
    sns.heatmap(
        pivot_time,
        annot=True,
        fmt=".3f",
        cmap="Reds",
        linewidths=.5,
        ax=ax4
    )
    ax4.set_title('Trade-off: Vreme pretrage (ms)', fontsize=14, weight='bold')
    ax4.set_xlabel('Checkpoint Interval (occ_rate)', fontsize=12)
    ax4.set_ylabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    safe_filename = dataset_name.replace(" ", "_").replace(",", "")
    output_path = os.path.join(PLOTS_DIRECTORY, f'analiza_{safe_filename}.png')
    plt.savefig(output_path, dpi=150)
    print(f"  -> Grafikon sačuvan: {output_path}")
    plt.close(fig)

if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"GREŠKA: Fajl '{CSV_FILE}' nije pronađen. Molim vas, prvo pokrenite 'main_analysis.py'.")
        sys.exit(1)

    if not os.path.exists(PLOTS_DIRECTORY):
        os.makedirs(PLOTS_DIRECTORY)
        print(f"Kreiran folder '{PLOTS_DIRECTORY}' za čuvanje grafikona.")

    df = pd.read_csv(CSV_FILE)

    df_optimized = df[df['Algorithm'] == 'Optimized'].copy()

    if df_optimized.empty:
        print("U CSV fajlu nema rezultata za 'Optimized' algoritam. Prekidam.")
        sys.exit(1)

    df_optimized['occ_rate'] = pd.to_numeric(df_optimized['occ_rate'])
    df_optimized['sa_rate'] = pd.to_numeric(df_optimized['sa_rate'])

    unique_datasets = df_optimized['Dataset Name'].unique()

    for dataset in unique_datasets:
        subset_df = df_optimized[df_optimized['Dataset Name'] == dataset]
        create_plots_for_dataset(subset_df, dataset)

    print("\nSvi grafikoni su uspešno generisani!")