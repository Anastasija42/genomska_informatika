import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

CSV_FILE = 'results.csv'
PLOTS_DIRECTORY = 'plots'

def create_plots_for_dataset(df, dataset_name):
    """
    Creates and saves a 2x2 set of plots for one specific dataset (genome).
    """
    print(f"--- Creating plots for: {dataset_name} ---")

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 14))
    fig.suptitle(f'FM-Index Performance Analysis for: {dataset_name}', fontsize=20, weight='bold')

    # Plot 1: Search Time vs. Occ Rate
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
    ax1.set_title('Search Time vs. Occ Rate', fontsize=14, weight='bold')
    ax1.set_xlabel('Checkpoint Interval (occ_rate)', fontsize=12)
    ax1.set_ylabel('Average Search Time (ms)', fontsize=12)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax1.legend(title='SA Rate')

    # Plot 2: Index Size vs. SA Rate
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
    ax2.set_title('Index Size vs. SA Rate', fontsize=14, weight='bold')
    ax2.set_xlabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)
    ax2.set_ylabel('Index Size (MB)', fontsize=12)
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax2.legend(title='Occ Rate')

    # Plot 3: Heatmap for Search Time (formerly Plot 4)
    ax3 = axes[1, 0]
    pivot_time = df.pivot(index='sa_rate', columns='occ_rate', values='Avg Search Time (ms)')
    sns.heatmap(
        pivot_time,
        annot=True,
        fmt=".3f",
        cmap="Reds",
        linewidths=.5,
        ax=ax3
    )
    ax3.set_title('Trade-off: Search Time (ms)', fontsize=14, weight='bold')
    ax3.set_xlabel('Checkpoint Interval (occ_rate)', fontsize=12)
    ax3.set_ylabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)

    # Plot 4: Heatmap for Index Size (formerly Plot 3)
    ax4 = axes[1, 1]
    pivot_mem = df.pivot(index='sa_rate', columns='occ_rate', values='Index Size (MB)')
    sns.heatmap(
        pivot_mem,
        annot=True,
        fmt=".1f",
        cmap="Greens",
        linewidths=.5,
        ax=ax4
    )
    ax4.set_title('Trade-off: Index Size (MB)', fontsize=14, weight='bold')
    ax4.set_xlabel('Checkpoint Interval (occ_rate)', fontsize=12)
    ax4.set_ylabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)


    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the figure
    safe_filename = dataset_name.replace(" ", "_").replace(",", "")
    output_path = os.path.join(PLOTS_DIRECTORY, f'analysis_{safe_filename}.png')
    plt.savefig(output_path, dpi=150)
    print(f"  -> Plot saved: {output_path}")
    plt.close(fig)

def create_pattern_comparison_plots(df, dataset_name):
    """
    Creates and saves a 1x3 set of plots for a specific dataset,
    comparing performance across three different search patterns.
    """
    print(f"--- Creating pattern comparison plots for: {dataset_name} ---")

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6), sharey='row')
    fig.suptitle(f'Performance Analysis by Pattern for: {dataset_name}', fontsize=24, weight='bold')

    patterns = [
        {'time_col': 'P1_Search_Time_ms', 'pattern_col': 'Pattern_1'},
        {'time_col': 'P2_Search_Time_ms', 'pattern_col': 'Pattern_2'},
        {'time_col': 'P3_Search_Time_ms', 'pattern_col': 'Pattern_3'}
    ]

    plot_df = df.copy()
    plot_df['occ_rate'] = plot_df['occ_rate'].astype('category')

    for i, p_info in enumerate(patterns):
        # --- Search Time vs. SA Rate ---
        ax_time = axes[i]
        sns.lineplot(
            data=plot_df,
            x='sa_rate',
            y=p_info['time_col'],
            hue='occ_rate',
            marker='o',
            palette='magma',
            ax=ax_time
        )
        pattern_name = df[p_info['pattern_col']].iloc[0]
        ax_time.set_title(f'{pattern_name}', fontsize=16, weight='bold')
        ax_time.set_xlabel('Suffix Array Sampling Rate (sa_rate)', fontsize=12)
        if i == 0:
            ax_time.set_ylabel('Search Time (ms)', fontsize=14)
        else:
            ax_time.set_ylabel('') # Remove redundant y-axis labels
        ax_time.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax_time.legend(title='Occ Rate')


    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the figure
    safe_filename = dataset_name.replace(" ", "_").replace(",", "")
    output_path = os.path.join(PLOTS_DIRECTORY, f'pattern_comparison_{safe_filename}.png')
    plt.savefig(output_path, dpi=150)
    print(f"  -> Plot saved: {output_path}")
    plt.close(fig)

if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: File '{CSV_FILE}' not found. Please run 'main_analysis.py' first.")
        sys.exit(1)

    if not os.path.exists(PLOTS_DIRECTORY):
        os.makedirs(PLOTS_DIRECTORY)
        print(f"Created folder '{PLOTS_DIRECTORY}' to save plots.")

    # Load the data
    df = pd.read_csv(CSV_FILE)

    # Filter for optimized results only
    df_optimized = df[df['Algorithm'] == 'Optimized'].copy()

    if df_optimized.empty:
        print("No results for 'Optimized' algorithm in the CSV file. Aborting.")
        sys.exit(1)

    # Ensure correct data types for plotting
    df_optimized['occ_rate'] = pd.to_numeric(df_optimized['occ_rate'])
    df_optimized['sa_rate'] = pd.to_numeric(df_optimized['sa_rate'])

    # Get unique dataset names and generate plots for each
    unique_datasets = df_optimized['Dataset Name'].unique()

    for dataset in unique_datasets:
        subset_df = df_optimized[df_optimized['Dataset Name'] == dataset]
        create_plots_for_dataset(subset_df, dataset)
        create_pattern_comparison_plots(subset_df, dataset)

    print("\nAll plots have been successfully generated!")