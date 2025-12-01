#!/usr/bin/env python3
"""
Betweenness Centrality: Exact vs Approximate Comparison
Generates comparative visualizations and analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

def load_betweenness_data():
    """Load exact and approximate betweenness results"""
    exact_csv = Path("results/betweenness/exact/summary.csv")
    approx_csv = Path("results/betweenness/approximate/summary_approx.csv")
    
    dfs = []
    
    if exact_csv.exists():
        df_exact = pd.read_csv(exact_csv)
        df_exact['Algorithm'] = 'Exact'
        dfs.append(df_exact)
    
    if approx_csv.exists():
        df_approx = pd.read_csv(approx_csv)
        df_approx['Algorithm'] = 'Approximate'
        dfs.append(df_approx)
    
    if not dfs:
        print("Error: No betweenness summary files found!")
        return None
    
    df = pd.concat(dfs, ignore_index=True)
    return df

def plot_runtime_comparison(df, output_dir):
    """Compare runtime between exact and approximate algorithms"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Runtime vs Vertices (log-log)
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        ax1.scatter(data['Vertices'], data['Runtime_sec'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax1.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Runtime vs Vertices: Exact vs Approximate', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Runtime vs Edges (log-log)
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        ax2.scatter(data['Edges'], data['Runtime_sec'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Runtime vs Edges: Exact vs Approximate', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Speedup factor (Exact / Approximate)
    df_merged = df.pivot_table(values='Runtime_sec', index='Dataset', columns='Algorithm')
    if 'Exact' in df_merged.columns and 'Approximate' in df_merged.columns:
        df_merged['Speedup'] = df_merged['Exact'] / df_merged['Approximate']
        df_merged = df_merged.sort_values('Speedup', ascending=False)
        
        colors = ['green' if x > 1 else 'red' for x in df_merged['Speedup']]
        ax3.barh(range(len(df_merged)), df_merged['Speedup'], color=colors, alpha=0.7, edgecolor='black')
        ax3.set_yticks(range(len(df_merged)))
        ax3.set_yticklabels(df_merged.index, fontsize=10)
        ax3.set_xlabel('Speedup Factor (Exact / Approximate)', fontsize=12, fontweight='bold')
        ax3.set_title('Speedup: How much faster is Approximate?', fontsize=14, fontweight='bold')
        ax3.axvline(x=1, color='black', linestyle='--', linewidth=2, label='No speedup')
        ax3.grid(True, alpha=0.3, axis='x')
        ax3.legend()
    
    # Runtime ratio by dataset size
    df_exact = df[df['Algorithm'] == 'Exact'].copy()
    df_approx = df[df['Algorithm'] == 'Approximate'].copy()
    
    if len(df_exact) > 0 and len(df_approx) > 0:
        df_exact = df_exact.sort_values('Vertices')
        df_approx = df_approx.sort_values('Vertices')
        
        ax4.plot(df_exact['Vertices'], df_exact['Runtime_sec'], 'o-', 
                label='Exact', linewidth=2, markersize=8, alpha=0.7)
        ax4.plot(df_approx['Vertices'], df_approx['Runtime_sec'], 's-', 
                label='Approximate', linewidth=2, markersize=8, alpha=0.7)
        
        ax4.set_xlabel('Number of Vertices', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Runtime (seconds)', fontsize=12, fontweight='bold')
        ax4.set_title('Runtime Trend: Exact vs Approximate', fontsize=14, fontweight='bold')
        ax4.legend(fontsize=11)
        ax4.set_xscale('log')
        ax4.set_yscale('log')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'runtime_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: runtime_comparison.png")
    plt.close()

def plot_memory_comparison(df, output_dir):
    """Compare memory usage between algorithms"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Memory vs Vertices
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        ax1.scatter(data['Vertices'], data['Memory_MB'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax1.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Memory Usage (MB, log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Memory Usage vs Vertices', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Memory comparison by dataset
    df_pivot = df.pivot_table(values='Memory_MB', index='Dataset', columns='Algorithm')
    if len(df_pivot) > 0:
        df_pivot.plot(kind='bar', ax=ax2, alpha=0.7, edgecolor='black', linewidth=0.8)
        ax2.set_xlabel('Dataset', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Memory Usage (MB)', fontsize=12, fontweight='bold')
        ax2.set_title('Memory Usage Comparison by Dataset', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11, title='Algorithm')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'memory_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: memory_comparison.png")
    plt.close()

def plot_efficiency_analysis(df, output_dir):
    """Analyze efficiency metrics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Runtime per edge
    df['RuntimePerEdge'] = df['Runtime_sec'] / (df['Edges'] + 1)
    
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        ax1.scatter(data['Edges'], data['RuntimePerEdge'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax1.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Runtime per Edge (log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Efficiency: Runtime per Edge', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Memory per vertex
    df['MemoryPerVertex'] = df['Memory_MB'] / df['Vertices']
    
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        ax2.scatter(data['Vertices'], data['MemoryPerVertex'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax2.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Memory per Vertex (MB, log scale)', fontsize=12, fontweight='bold')
    ax2.set_title('Efficiency: Memory per Vertex', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # Runtime vs Density
    df_nonzero = df[df['Density'] > 0].copy()
    for algo in df_nonzero['Algorithm'].unique():
        data = df_nonzero[df_nonzero['Algorithm'] == algo]
        ax3.scatter(data['Density'], data['Runtime_sec'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax3.set_xlabel('Graph Density (log scale)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax3.set_title('Runtime vs Graph Density', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=11)
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    # Max Betweenness vs Vertices
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        ax4.scatter(data['Vertices'], data['MaxBC'], 
                   label=algo, alpha=0.7, s=120, edgecolors='black', linewidth=0.5)
    
    ax4.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Maximum Betweenness Centrality', fontsize=12, fontweight='bold')
    ax4.set_title('Max Betweenness vs Graph Size', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=11)
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'efficiency_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: efficiency_analysis.png")
    plt.close()

def generate_comparison_report(df, output_dir):
    """Generate detailed comparison report"""
    report_file = output_dir / 'comparison_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("BETWEENNESS CENTRALITY: EXACT vs APPROXIMATE COMPARISON\n")
        f.write("=" * 80 + "\n\n")
        
        # Overall statistics
        f.write("1. OVERALL STATISTICS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total experiments: {len(df)}\n")
        f.write(f"  - Exact: {len(df[df['Algorithm'] == 'Exact'])}\n")
        f.write(f"  - Approximate: {len(df[df['Algorithm'] == 'Approximate'])}\n\n")
        
        # Runtime comparison
        f.write("2. RUNTIME COMPARISON\n")
        f.write("-" * 80 + "\n")
        
        for algo in ['Exact', 'Approximate']:
            data = df[df['Algorithm'] == algo]
            if len(data) > 0:
                f.write(f"\n{algo} Algorithm:\n")
                f.write(f"  Runtime range: {data['Runtime_sec'].min():.6f}s to {data['Runtime_sec'].max():.6f}s\n")
                f.write(f"  Average runtime: {data['Runtime_sec'].mean():.6f}s\n")
                f.write(f"  Median runtime: {data['Runtime_sec'].median():.6f}s\n")
                f.write(f"  Std deviation: {data['Runtime_sec'].std():.6f}s\n")
        
        # Speedup analysis
        df_merged = df.pivot_table(values='Runtime_sec', index='Dataset', columns='Algorithm')
        if 'Exact' in df_merged.columns and 'Approximate' in df_merged.columns:
            f.write(f"\nSpeedup Analysis (Exact / Approximate):\n")
            df_merged['Speedup'] = df_merged['Exact'] / df_merged['Approximate']
            f.write(f"  Average speedup: {df_merged['Speedup'].mean():.2f}x\n")
            f.write(f"  Min speedup: {df_merged['Speedup'].min():.2f}x\n")
            f.write(f"  Max speedup: {df_merged['Speedup'].max():.2f}x\n\n")
            
            f.write("  Speedup by dataset:\n")
            for dataset, speedup in df_merged['Speedup'].items():
                f.write(f"    {dataset}: {speedup:.2f}x\n")
        
        # Memory comparison
        f.write("\n3. MEMORY USAGE COMPARISON\n")
        f.write("-" * 80 + "\n")
        
        for algo in ['Exact', 'Approximate']:
            data = df[df['Algorithm'] == algo]
            if len(data) > 0:
                f.write(f"\n{algo} Algorithm:\n")
                f.write(f"  Memory range: {data['Memory_MB'].min():.2f} MB to {data['Memory_MB'].max():.2f} MB\n")
                f.write(f"  Average memory: {data['Memory_MB'].mean():.2f} MB\n")
                f.write(f"  Median memory: {data['Memory_MB'].median():.2f} MB\n")
        
        # Betweenness statistics
        f.write("\n4. BETWEENNESS CENTRALITY STATISTICS\n")
        f.write("-" * 80 + "\n")
        
        for algo in ['Exact', 'Approximate']:
            data = df[df['Algorithm'] == algo]
            if len(data) > 0:
                f.write(f"\n{algo} Algorithm:\n")
                f.write(f"  Max BC range: {data['MaxBC'].min():.6f} to {data['MaxBC'].max():.6f}\n")
                f.write(f"  Average max BC: {data['MaxBC'].mean():.6f}\n")
                f.write(f"  Median max BC: {data['MaxBC'].median():.6f}\n")
        
        # Sampling information
        if 'Samples' in df.columns:
            f.write("\n5. SAMPLING INFORMATION (Approximate Only)\n")
            f.write("-" * 80 + "\n")
            approx_data = df[df['Algorithm'] == 'Approximate']
            if len(approx_data) > 0:
                f.write(f"Sample size range: {approx_data['Samples'].min()} to {approx_data['Samples'].max()}\n")
                f.write(f"Average samples: {approx_data['Samples'].mean():.0f}\n")
                approx_data['SamplePercent'] = (approx_data['Samples'] / approx_data['Vertices'] * 100)
                f.write(f"Sample percentage range: {approx_data['SamplePercent'].min():.2f}% to {approx_data['SamplePercent'].max():.2f}%\n")
        
        # Correlation analysis
        f.write("\n6. CORRELATION ANALYSIS\n")
        f.write("-" * 80 + "\n")
        
        corr_vertices_runtime = df['Vertices'].corr(df['Runtime_sec'])
        corr_edges_runtime = df['Edges'].corr(df['Runtime_sec'])
        corr_density_runtime = df['Density'].corr(df['Runtime_sec'])
        
        f.write(f"Vertices vs Runtime: {corr_vertices_runtime:.4f}\n")
        f.write(f"Edges vs Runtime: {corr_edges_runtime:.4f}\n")
        f.write(f"Density vs Runtime: {corr_density_runtime:.4f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"  ✓ Saved: comparison_report.txt")

def main():
    print("=" * 70)
    print("Betweenness Centrality: Exact vs Approximate Comparison")
    print("=" * 70)
    print()
    
    # Create output directory
    viz_dir = Path("results/betweenness/comparison")
    viz_dir.mkdir(exist_ok=True, parents=True)
    
    # Load data
    print("Loading data...")
    df = load_betweenness_data()
    
    if df is None:
        print("Error: Could not load data")
        return
    
    print(f"  ✓ Loaded {len(df)} experiments\n")
    
    # Generate visualizations
    print("Generating visualizations...")
    print("-" * 70)
    
    plot_runtime_comparison(df, viz_dir)
    plot_memory_comparison(df, viz_dir)
    plot_efficiency_analysis(df, viz_dir)
    
    print()
    print("Generating comparison report...")
    print("-" * 70)
    generate_comparison_report(df, viz_dir)
    
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print(f"\nAll outputs saved to: {viz_dir.absolute()}")
    print("\nGenerated files:")
    print("  - runtime_comparison.png")
    print("  - memory_comparison.png")
    print("  - efficiency_analysis.png")
    print("  - comparison_report.txt")
    print()

if __name__ == "__main__":
    main()
