#!/usr/bin/env python3
"""
K-Core Results Visualization and Analysis
Generates comprehensive visualizations and statistical analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_summary_data():
    """Load all summary CSV files"""
    synthetic_csv = Path("results/synthetic/summary.csv")
    real_csv = Path("results/real_datasets/summary.csv")
    
    dfs = []
    
    if synthetic_csv.exists():
        df_synth = pd.read_csv(synthetic_csv)
        df_synth['Type'] = 'Synthetic'
        dfs.append(df_synth)
    
    if real_csv.exists():
        df_real = pd.read_csv(real_csv)
        df_real['Type'] = 'Real'
        dfs.append(df_real)
    
    if not dfs:
        print("Error: No summary files found!")
        return None
    
    df = pd.concat(dfs, ignore_index=True)
    return df

def parse_detailed_results(filename):
    """Parse detailed result file to extract core distribution"""
    if not Path(filename).exists():
        return None, None
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Extract max k-core
    max_core = None
    for line in lines:
        if line.startswith("Max K-Core:"):
            max_core = int(line.split(":")[1].strip())
            break
    
    # Extract core distribution
    core_dist = {}
    in_dist = False
    for line in lines:
        if "=== Core Distribution ===" in line:
            in_dist = True
            continue
        if in_dist and line.strip() and not line.startswith("Core"):
            if line.startswith("==="):
                break
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                try:
                    core = int(parts[0])
                    count = int(parts[1])
                    core_dist[core] = count
                except ValueError:
                    continue
    
    return max_core, core_dist

def plot_runtime_vs_size(df, output_dir):
    """Plot runtime vs graph size with log-log analysis"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Runtime vs Vertices (log-log)
    for graph_type in df['Type'].unique():
        data = df[df['Type'] == graph_type]
        ax1.scatter(data['Vertices'], data['Runtime_sec'], 
                   label=graph_type, alpha=0.6, s=100)
    
    ax1.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Runtime vs Vertices (Log-Log)', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Runtime vs Edges (log-log)
    for graph_type in df['Type'].unique():
        data = df[df['Type'] == graph_type]
        ax2.scatter(data['Edges'], data['Runtime_sec'], 
                   label=graph_type, alpha=0.6, s=100)
    
    ax2.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Runtime vs Edges (Log-Log)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Runtime vs Density (log-log)
    df_nonzero_density = df[df['Density'] > 0].copy()
    for graph_type in df_nonzero_density['Type'].unique():
        data = df_nonzero_density[df_nonzero_density['Type'] == graph_type]
        ax3.scatter(data['Density'], data['Runtime_sec'], 
                   label=graph_type, alpha=0.6, s=100)
    
    ax3.set_xlabel('Graph Density (log scale)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax3.set_title('Runtime vs Density (Log-Log)', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    # Runtime vs Average Degree (log-log)
    for graph_type in df['Type'].unique():
        data = df[df['Type'] == graph_type]
        ax4.scatter(data['AvgDegree'], data['Runtime_sec'], 
                   label=graph_type, alpha=0.6, s=100)
    
    ax4.set_xlabel('Average Degree (log scale)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax4.set_title('Runtime vs Average Degree (Log-Log)', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'runtime_vs_size.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: runtime_vs_size.png")
    plt.close()

def plot_memory_vs_size(df, output_dir):
    """Plot memory usage vs graph size"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for graph_type in df['Type'].unique():
        data = df[df['Type'] == graph_type]
        ax.scatter(data['Vertices'], data['Memory_MB'], 
                  label=graph_type, alpha=0.6, s=100)
    
    ax.set_xlabel('Number of Vertices', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory Usage (MB)', fontsize=12, fontweight='bold')
    ax.set_title('Memory Usage vs Graph Size', fontsize=14, fontweight='bold')
    ax.legend()
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'memory_vs_size.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: memory_vs_size.png")
    plt.close()

def plot_density_analysis(df, output_dir):
    """Plot analysis of density vs k-core"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Density vs Max K-Core
    scatter1 = ax1.scatter(df['Density'], df['MaxCore'], 
                          c=df['Vertices'], cmap='viridis', 
                          alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Graph Density', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Maximum K-Core', fontsize=12, fontweight='bold')
    ax1.set_title('Density vs Maximum K-Core', fontsize=14, fontweight='bold')
    ax1.set_xscale('log')
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label('Vertices', fontsize=10)
    
    # Average Degree vs Max K-Core
    scatter2 = ax2.scatter(df['AvgDegree'], df['MaxCore'], 
                          c=df['Vertices'], cmap='plasma', 
                          alpha=0.6, s=100, edgecolors='black', linewidth=0.5)
    ax2.set_xlabel('Average Degree', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Maximum K-Core', fontsize=12, fontweight='bold')
    ax2.set_title('Average Degree vs Maximum K-Core', fontsize=14, fontweight='bold')
    ax2.set_xscale('log')
    ax2.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label('Vertices', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'density_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: density_analysis.png")
    plt.close()

def plot_core_distributions(output_dir):
    """Plot k-core distributions for selected graphs"""
    # Select interesting graphs to visualize
    interesting_files = [
        ('results/synthetic/verify_known_structure_detailed.txt', 'Known Structure (Verification)'),
        ('results/real_datasets/cit-DBLP_detailed.txt', 'DBLP Citation Network'),
        ('results/real_datasets/cit-HepTh_detailed.txt', 'HepTh Citation Network'),
        ('results/synthetic/ba_5k_m5_detailed.txt', 'Barabási-Albert (5K nodes)'),
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (filename, title) in enumerate(interesting_files):
        if idx >= len(axes):
            break
        
        max_core, core_dist = parse_detailed_results(filename)
        
        if core_dist:
            cores = sorted(core_dist.keys())
            counts = [core_dist[c] for c in cores]
            
            axes[idx].bar(cores, counts, alpha=0.7, edgecolor='black', linewidth=0.8)
            axes[idx].set_xlabel('K-Core Number', fontsize=11, fontweight='bold')
            axes[idx].set_ylabel('Number of Vertices', fontsize=11, fontweight='bold')
            axes[idx].set_title(f'{title}\n(Max Core: {max_core})', fontsize=12, fontweight='bold')
            axes[idx].grid(True, alpha=0.3, axis='y')
            axes[idx].set_yscale('log')
        else:
            axes[idx].text(0.5, 0.5, 'Data not available', 
                          ha='center', va='center', fontsize=12)
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'core_distributions.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: core_distributions.png")
    plt.close()

def plot_density_based_runtime(df, output_dir):
    """Analyze runtime based on graph density/sparseness"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Categorize graphs by density
    df_analysis = df.copy()
    df_analysis = df_analysis[df_analysis['Density'] > 0]
    
    # Create density categories
    def categorize_density(density):
        if density < 0.001:
            return 'Very Sparse'
        elif density < 0.01:
            return 'Sparse'
        elif density < 0.1:
            return 'Medium'
        else:
            return 'Dense'
    
    df_analysis['DensityCategory'] = df_analysis['Density'].apply(categorize_density)
    
    # 1. Runtime by density category
    categories = ['Very Sparse', 'Sparse', 'Medium', 'Dense']
    category_data = [df_analysis[df_analysis['DensityCategory'] == cat]['Runtime_sec'].values 
                     for cat in categories if cat in df_analysis['DensityCategory'].values]
    category_labels = [cat for cat in categories if cat in df_analysis['DensityCategory'].values]
    
    bp = ax1.boxplot(category_data, labels=category_labels, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    ax1.set_ylabel('Runtime (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Runtime Distribution by Density Category', fontsize=14, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. Runtime vs Density colored by sparseness
    scatter = ax2.scatter(df_analysis['Density'], df_analysis['Runtime_sec'],
                         c=df_analysis['AvgDegree'], cmap='RdYlGn_r', 
                         s=150, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax2.set_xlabel('Graph Density (log scale)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Runtime vs Density (colored by Avg Degree)', fontsize=14, fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Avg Degree', fontsize=10)
    
    # 3. Sparseness metric: (V+E) / (V^2) vs Runtime
    df_analysis['Sparseness'] = (df_analysis['Vertices'] + df_analysis['Edges']) / (df_analysis['Vertices'] ** 2)
    scatter2 = ax3.scatter(df_analysis['Sparseness'], df_analysis['Runtime_sec'],
                          c=df_analysis['Vertices'], cmap='viridis',
                          s=150, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax3.set_xlabel('Sparseness Metric (log scale)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax3.set_title('Runtime vs Sparseness Metric (colored by Vertices)', fontsize=14, fontweight='bold')
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    cbar2 = plt.colorbar(scatter2, ax=ax3)
    cbar2.set_label('Vertices', fontsize=10)
    
    # 4. Normalized runtime by density
    df_analysis['RuntimePerEdge'] = df_analysis['Runtime_sec'] / (df_analysis['Edges'] + 1)
    scatter3 = ax4.scatter(df_analysis['Density'], df_analysis['RuntimePerEdge'],
                          c=df_analysis['MaxCore'], cmap='plasma',
                          s=150, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax4.set_xlabel('Graph Density (log scale)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Runtime per Edge (log scale)', fontsize=12, fontweight='bold')
    ax4.set_title('Normalized Runtime vs Density (colored by Max K-Core)', fontsize=14, fontweight='bold')
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    cbar3 = plt.colorbar(scatter3, ax=ax4)
    cbar3.set_label('Max K-Core', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'density_based_runtime.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: density_based_runtime.png")
    plt.close()

def plot_scalability_analysis(df, output_dir):
    """Analyze algorithmic scalability"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Filter synthetic graphs for cleaner analysis
    df_synth = df[df['Type'] == 'Synthetic'].copy()
    df_synth = df_synth.sort_values('Vertices')
    
    # Runtime vs (V + E) - Expected O(V + E)
    df_synth['V_plus_E'] = df_synth['Vertices'] + df_synth['Edges']
    
    ax1.scatter(df_synth['V_plus_E'], df_synth['Runtime_sec'], alpha=0.6, s=100)
    
    # Fit line in log-log space
    log_x = np.log10(df_synth['V_plus_E'])
    log_y = np.log10(df_synth['Runtime_sec'])
    z = np.polyfit(log_x, log_y, 1)
    p = np.poly1d(z)
    
    x_fit = np.logspace(np.log10(df_synth['V_plus_E'].min()), 
                        np.log10(df_synth['V_plus_E'].max()), 100)
    y_fit = 10 ** p(np.log10(x_fit))
    
    ax1.plot(x_fit, y_fit, 'r--', linewidth=2, 
            label=f'Fitted: O(n^{z[0]:.2f})')
    
    ax1.set_xlabel('V + E (Vertices + Edges)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Runtime (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Scalability Analysis: Runtime vs (V+E)', fontsize=14, fontweight='bold')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Memory vs V - Expected O(V)
    ax2.scatter(df_synth['Vertices'], df_synth['Memory_MB'], alpha=0.6, s=100)
    
    log_x2 = np.log10(df_synth['Vertices'])
    log_y2 = np.log10(df_synth['Memory_MB'])
    z2 = np.polyfit(log_x2, log_y2, 1)
    p2 = np.poly1d(z2)
    
    x_fit2 = np.logspace(np.log10(df_synth['Vertices'].min()), 
                         np.log10(df_synth['Vertices'].max()), 100)
    y_fit2 = 10 ** p2(np.log10(x_fit2))
    
    ax2.plot(x_fit2, y_fit2, 'r--', linewidth=2, 
            label=f'Fitted: O(n^{z2[0]:.2f})')
    
    ax2.set_xlabel('Vertices (V)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Memory (MB)', fontsize=12, fontweight='bold')
    ax2.set_title('Scalability Analysis: Memory vs V', fontsize=14, fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scalability_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: scalability_analysis.png")
    plt.close()
    
    return z[0], z2[0]  # Return exponents

def generate_statistical_report(df, output_dir, runtime_exp, memory_exp):
    """Generate comprehensive statistical report"""
    report_file = output_dir / 'statistical_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("K-CORE DECOMPOSITION: STATISTICAL ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Overall statistics
        f.write("1. OVERALL STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total graphs analyzed: {len(df)}\n")
        f.write(f"  - Synthetic: {len(df[df['Type'] == 'Synthetic'])}\n")
        f.write(f"  - Real datasets: {len(df[df['Type'] == 'Real'])}\n\n")
        
        f.write(f"Graph size range:\n")
        f.write(f"  - Vertices: {df['Vertices'].min():,} to {df['Vertices'].max():,}\n")
        f.write(f"  - Edges: {df['Edges'].min():,} to {df['Edges'].max():,}\n\n")
        
        # Runtime statistics
        f.write("2. RUNTIME ANALYSIS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Runtime range: {df['Runtime_sec'].min():.6f}s to {df['Runtime_sec'].max():.2f}s\n")
        f.write(f"Average runtime: {df['Runtime_sec'].mean():.6f}s\n")
        f.write(f"Median runtime: {df['Runtime_sec'].median():.6f}s\n")
        f.write(f"Std deviation: {df['Runtime_sec'].std():.6f}s\n\n")
        f.write(f"Empirical time complexity: O(n^{runtime_exp:.2f})\n")
        f.write(f"  (Expected: O(V + E) ≈ O(n^1.0) for sparse graphs)\n\n")
        
        # Memory statistics
        f.write("3. MEMORY USAGE ANALYSIS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Memory range: {df['Memory_MB'].min():.2f} MB to {df['Memory_MB'].max():.2f} MB\n")
        f.write(f"Average memory: {df['Memory_MB'].mean():.2f} MB\n")
        f.write(f"Median memory: {df['Memory_MB'].median():.2f} MB\n")
        f.write(f"Std deviation: {df['Memory_MB'].std():.2f} MB\n\n")
        f.write(f"Empirical space complexity: O(n^{memory_exp:.2f})\n")
        f.write(f"  (Expected: O(V + E) ≈ O(n^1.0) for sparse graphs)\n\n")
        
        # K-core statistics
        f.write("4. K-CORE STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Max k-core range: {df['MaxCore'].min()} to {df['MaxCore'].max()}\n")
        f.write(f"Average max k-core: {df['MaxCore'].mean():.2f}\n")
        f.write(f"Median max k-core: {df['MaxCore'].median():.0f}\n\n")
        
        # Density analysis
        f.write("5. GRAPH DENSITY ANALYSIS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Density range: {df['Density'].min():.6e} to {df['Density'].max():.6e}\n")
        f.write(f"Average degree range: {df['AvgDegree'].min():.2f} to {df['AvgDegree'].max():.2f}\n\n")
        
        # Correlation analysis
        f.write("6. CORRELATION ANALYSIS\n")
        f.write("-" * 80 + "\n")
        corr_density_maxcore = df['Density'].corr(df['MaxCore'])
        corr_avgdeg_maxcore = df['AvgDegree'].corr(df['MaxCore'])
        corr_size_runtime = df['Vertices'].corr(df['Runtime_sec'])
        
        f.write(f"Density vs Max K-Core: {corr_density_maxcore:.4f}\n")
        f.write(f"Avg Degree vs Max K-Core: {corr_avgdeg_maxcore:.4f}\n")
        f.write(f"Graph Size vs Runtime: {corr_size_runtime:.4f}\n\n")
        
        # Real dataset highlights
        if len(df[df['Type'] == 'Real']) > 0:
            f.write("7. REAL DATASET HIGHLIGHTS\n")
            f.write("-" * 80 + "\n")
            real_df = df[df['Type'] == 'Real'].sort_values('MaxCore', ascending=False)
            for idx, row in real_df.iterrows():
                f.write(f"\n{row['Dataset']}:\n")
                f.write(f"  - Vertices: {row['Vertices']:,}\n")
                f.write(f"  - Edges: {row['Edges']:,}\n")
                f.write(f"  - Max K-Core: {row['MaxCore']}\n")
                f.write(f"  - Runtime: {row['Runtime_sec']:.6f}s\n")
                f.write(f"  - Memory: {row['Memory_MB']:.2f} MB\n")
                f.write(f"  - Avg Degree: {row['AvgDegree']:.2f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"  ✓ Saved: statistical_report.txt")

def plot_algorithm_comparison(output_dir):
    """Compare k-core with betweenness algorithms if data available"""
    kcore_csv = Path("results/synthetic/summary.csv")
    bet_exact_csv = Path("results/betweenness/exact/summary.csv")
    bet_approx_csv = Path("results/betweenness/approximate/summary_approx.csv")
    
    dfs = []
    
    if kcore_csv.exists():
        df_kcore = pd.read_csv(kcore_csv)
        df_kcore['Algorithm'] = 'K-Core'
        dfs.append(df_kcore)
    
    if bet_exact_csv.exists():
        df_bet = pd.read_csv(bet_exact_csv)
        df_bet['Algorithm'] = 'Betweenness (Exact)'
        dfs.append(df_bet)
    
    if bet_approx_csv.exists():
        df_approx = pd.read_csv(bet_approx_csv)
        df_approx['Algorithm'] = 'Betweenness (Approx)'
        dfs.append(df_approx)
    
    if len(dfs) < 2:
        return  # Not enough data for comparison
    
    df_all = pd.concat(dfs, ignore_index=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Runtime comparison
    for algo in df_all['Algorithm'].unique():
        data = df_all[df_all['Algorithm'] == algo]
        ax1.scatter(data['Vertices'], data['Runtime_sec'], 
                   label=algo, alpha=0.7, s=100, edgecolors='black', linewidth=0.5)
    
    ax1.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Algorithm Comparison: Runtime vs Vertices', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Memory comparison
    for algo in df_all['Algorithm'].unique():
        data = df_all[df_all['Algorithm'] == algo]
        ax2.scatter(data['Vertices'], data['Memory_MB'], 
                   label=algo, alpha=0.7, s=100, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Memory Usage (MB, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Algorithm Comparison: Memory vs Vertices', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'algorithm_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: algorithm_comparison.png")
    plt.close()

def main():
    print("=" * 70)
    print("K-Core Results Visualization and Analysis")
    print("=" * 70)
    print()
    
    # Create output directory
    viz_dir = Path("results/visualizations")
    viz_dir.mkdir(exist_ok=True, parents=True)
    
    # Load data
    print("Loading data...")
    df = load_summary_data()
    
    if df is None:
        print("Error: Could not load data")
        return
    
    print(f"  ✓ Loaded {len(df)} experiments\n")
    
    # Generate visualizations
    print("Generating visualizations...")
    print("-" * 70)
    
    plot_runtime_vs_size(df, viz_dir)
    plot_memory_vs_size(df, viz_dir)
    plot_density_analysis(df, viz_dir)
    plot_density_based_runtime(df, viz_dir)
    plot_core_distributions(viz_dir)
    runtime_exp, memory_exp = plot_scalability_analysis(df, viz_dir)
    plot_algorithm_comparison(viz_dir)
    
    print()
    print("Generating statistical report...")
    print("-" * 70)
    generate_statistical_report(df, viz_dir, runtime_exp, memory_exp)
    
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print(f"\nAll outputs saved to: {viz_dir.absolute()}")
    print("\nGenerated files:")
    print("  - runtime_vs_size.png (log-log plots)")
    print("  - memory_vs_size.png")
    print("  - density_analysis.png")
    print("  - density_based_runtime.png (sparseness analysis)")
    print("  - core_distributions.png")
    print("  - scalability_analysis.png")
    print("  - statistical_report.txt")
    print()

if __name__ == "__main__":
    main()
