#!/usr/bin/env python3
"""
Comprehensive Runtime and Memory Analysis for ALL 9 Algorithms
Compares performance across all graph types (real and synthetic) with detailed
analysis of how runtime and memory scale with graph characteristics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 10

# ALL algorithms including Approximate Betweenness
ALL_ALGORITHMS = [
    'K-Core',
    'Betweenness (Exact)',
    'Betweenness (Approximate)',
    'Degree Centrality',
    'Bridging Centrality',
    'Katz',
    'Eigenvector',
    'HITS (Hub)',
    'HITS (Authority)',
    'PageRank'
]

def load_from_detailed_files(result_dir, algorithm_name, suffix=None):
    """Load data from detailed.txt files when summary.csv doesn't exist"""
    summaries = []
    result_path = Path(result_dir)
    import re
    
    if suffix:
        detailed_files = list(result_path.glob(f'*{suffix}_detailed.txt'))
    else:
        detailed_files = list(result_path.glob('*_detailed.txt'))
    
    for detailed_file in detailed_files:
        try:
            dataset_name = detailed_file.stem.replace(f'{suffix}_detailed', '').replace('_detailed', '')
            stats = {}
            
            with open(detailed_file, 'r') as f:
                content = f.read()
                
                # Extract common fields - try both "Vertices" and "Nodes"
                match = re.search(r'(?:Vertices|Nodes):\s*(\d+)', content)
                if match:
                    stats['Vertices'] = int(match.group(1))
                
                match = re.search(r'Edges:\s*(\d+)', content)
                if match:
                    stats['Edges'] = int(match.group(1))
                
                # Runtime patterns: "Runtime: X seconds" or "Runtime (seconds): X"
                match = re.search(r'Runtime[^:]*:\s*([\d.]+)', content)
                if match:
                    stats['Runtime_sec'] = float(match.group(1))
                
                # Memory patterns: "Peak Memory: X MB" or "Memory Usage (MB): X"
                match = re.search(r'(?:Peak Memory|Memory Usage)[^:]*:\s*([\d.]+)', content)
                if match:
                    stats['Memory_MB'] = float(match.group(1))
                else:
                    # Try alternative pattern
                    match = re.search(r'Memory[^:]*\(MB\)[^:]*:\s*([\d.]+)', content)
                    if match:
                        stats['Memory_MB'] = float(match.group(1))
                
                stats['Dataset'] = dataset_name
                if 'Vertices' in stats and 'Edges' in stats:
                    stats['Density'] = stats['Edges'] / (stats['Vertices'] * (stats['Vertices'] - 1)) if stats['Vertices'] > 1 else 0
                    stats['AvgDegree'] = 2 * stats['Edges'] / stats['Vertices'] if stats['Vertices'] > 0 else 0
                    summaries.append(stats)
        except Exception as e:
            continue
    
    if summaries:
        return pd.DataFrame(summaries)
    return None

def load_all_results():
    """Load results from ALL algorithms"""
    results = {}
    
    # K-Core
    kcore_csv = Path("results/synthetic/summary.csv")
    if kcore_csv.exists():
        df = pd.read_csv(kcore_csv)
        df['Algorithm'] = 'K-Core'
        df['Category'] = 'Foundational'
        results['K-Core'] = df
    
    # Betweenness Exact
    bet_csv = Path("results/betweenness/exact/summary.csv")
    if bet_csv.exists():
        df = pd.read_csv(bet_csv)
        df['Algorithm'] = 'Betweenness (Exact)'
        df['Category'] = 'Foundational'
        results['Betweenness (Exact)'] = df
    
    # Betweenness Approximate
    bet_approx_csv = Path("results/betweenness/approximate/summary_approx.csv")
    if bet_approx_csv.exists():
        df = pd.read_csv(bet_approx_csv)
        df['Algorithm'] = 'Betweenness (Approximate)'
        df['Category'] = 'Foundational'
        results['Betweenness (Approximate)'] = df
    
    # Degree Centrality - try summary first, then detailed files
    deg_csv = Path("results/degree_centrality/summary.csv")
    if deg_csv.exists():
        df = pd.read_csv(deg_csv)
        df['Algorithm'] = 'Degree Centrality'
        df['Category'] = 'Foundational'
        results['Degree Centrality'] = df
    else:
        df = load_from_detailed_files('results/degree_centrality', 'Degree Centrality')
        if df is not None:
            df['Algorithm'] = 'Degree Centrality'
            df['Category'] = 'Foundational'
            results['Degree Centrality'] = df
    
    # Bridging Centrality - try summary first, then detailed files
    brid_csv = Path("results/bridging_centrality/summary.csv")
    if brid_csv.exists():
        df = pd.read_csv(brid_csv)
        df['Algorithm'] = 'Bridging Centrality'
        df['Category'] = 'Foundational'
        results['Bridging Centrality'] = df
    else:
        df = load_from_detailed_files('results/bridging_centrality', 'Bridging Centrality')
        if df is not None:
            df['Algorithm'] = 'Bridging Centrality'
            df['Category'] = 'Foundational'
            results['Bridging Centrality'] = df
    
    # Katz
    katz_csv = Path("results/centrality/katz/summary.csv")
    if katz_csv.exists():
        df = pd.read_csv(katz_csv)
        df['Algorithm'] = 'Katz'
        df['Category'] = 'Frontier'
        results['Katz'] = df
    
    # Eigenvector
    eigen_csv = Path("results/centrality/eigenvector/summary.csv")
    if eigen_csv.exists():
        df = pd.read_csv(eigen_csv)
        df['Algorithm'] = 'Eigenvector'
        df['Category'] = 'Frontier'
        results['Eigenvector'] = df
    
    # HITS (Hub) - try summary first, then detailed files
    hits_hub_csv = Path("results/hits/summary_hub.csv")
    if hits_hub_csv.exists():
        df = pd.read_csv(hits_hub_csv)
        df['Algorithm'] = 'HITS (Hub)'
        df['Category'] = 'Frontier'
        results['HITS (Hub)'] = df
    else:
        df = load_from_detailed_files('results/hits', 'HITS (Hub)', '_hub')
        if df is not None:
            df['Algorithm'] = 'HITS (Hub)'
            df['Category'] = 'Frontier'
            results['HITS (Hub)'] = df
    
    # HITS (Authority) - try summary first, then detailed files
    hits_auth_csv = Path("results/hits/summary_authority.csv")
    if hits_auth_csv.exists():
        df = pd.read_csv(hits_auth_csv)
        df['Algorithm'] = 'HITS (Authority)'
        df['Category'] = 'Frontier'
        results['HITS (Authority)'] = df
    else:
        df = load_from_detailed_files('results/hits', 'HITS (Authority)', '_authority')
        if df is not None:
            df['Algorithm'] = 'HITS (Authority)'
            df['Category'] = 'Frontier'
            results['HITS (Authority)'] = df
    
    # PageRank
    pagerank_csv = Path("results/centrality/pagerank/summary_pagerank.csv")
    if pagerank_csv.exists():
        df = pd.read_csv(pagerank_csv)
        df['Algorithm'] = 'PageRank'
        df['Category'] = 'Frontier'
        results['PageRank'] = df
    
    if not results:
        return None
    
    # Combine all results
    combined_df = pd.concat(results.values(), ignore_index=True)
    
    # Classify graph types
    real_datasets = ['cit-DBLP', 'cit-HepTh', 'citeseer', 'cora']
    combined_df['GraphType'] = combined_df['Dataset'].apply(
        lambda x: 'Real' if x in real_datasets else 'Synthetic'
    )
    
    return combined_df

def analyze_runtime_scaling(df, output_dir):
    """Analyze how runtime scales with graph characteristics"""
    print("Analyzing runtime scaling...")
    
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    axes = axes.flatten()
    
    # Color mapping for algorithms
    colors = plt.cm.tab10(np.linspace(0, 1, len(ALL_ALGORITHMS)))
    algo_colors = {algo: colors[i] for i, algo in enumerate(ALL_ALGORITHMS)}
    
    # 1. Runtime vs Vertices
    ax = axes[0]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['Runtime_sec'], 
                      label=algo, alpha=0.7, s=100, marker=marker, 
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Runtime vs Vertices - All 9 Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 2. Runtime vs Edges
    ax = axes[1]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Edges'], data['Runtime_sec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Runtime vs Edges - All 9 Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 3. Runtime vs Density
    ax = axes[2]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Density'], data['Runtime_sec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Graph Density (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Runtime vs Density - All 9 Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 4. Runtime by Graph Type (Real vs Synthetic)
    ax = axes[3]
    df_pivot = df.pivot_table(values='Runtime_sec', index='GraphType', columns='Algorithm', aggfunc='mean')
    if len(df_pivot) > 0:
        df_pivot.plot(kind='bar', ax=ax, alpha=0.8, edgecolor='black', linewidth=0.8)
        ax.set_xlabel('Graph Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
        ax.set_title('Average Runtime: Real vs Synthetic Graphs', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.legend(fontsize=8, title='Algorithm', loc='best', ncol=2)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)
    
    # 5. Runtime per Vertex
    ax = axes[4]
    df['RuntimePerVertex'] = df['Runtime_sec'] / df['Vertices']
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['RuntimePerVertex'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime per Vertex (log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Efficiency: Runtime per Vertex', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    # 6. Runtime Heatmap by Algorithm and Dataset
    ax = axes[5]
    df_pivot2 = df.pivot_table(values='Runtime_sec', index='Dataset', columns='Algorithm', aggfunc='mean')
    if len(df_pivot2) > 0:
        # Log scale for better visualization
        df_pivot2_log = np.log10(df_pivot2 + 1e-6)
        sns.heatmap(df_pivot2_log, annot=False, fmt='.2f', cmap='YlOrRd', ax=ax,
                   cbar_kws={'label': 'log10(Runtime in seconds)'})
        ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax.set_ylabel('Dataset', fontsize=12, fontweight='bold')
        ax.set_title('Runtime Heatmap: All Algorithms vs All Datasets', fontsize=14, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=0, fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'runtime_scaling_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: runtime_scaling_analysis.png")
    plt.close()

def analyze_memory_scaling(df, output_dir):
    """Analyze how memory scales with graph characteristics"""
    print("Analyzing memory scaling...")
    
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    axes = axes.flatten()
    
    # Color mapping for algorithms
    colors = plt.cm.tab10(np.linspace(0, 1, len(ALL_ALGORITHMS)))
    algo_colors = {algo: colors[i] for i, algo in enumerate(ALL_ALGORITHMS)}
    
    # 1. Memory vs Vertices
    ax = axes[0]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['Memory_MB'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory Usage (MB, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Memory vs Vertices - All 9 Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 2. Memory vs Edges
    ax = axes[1]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Edges'], data['Memory_MB'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory Usage (MB, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Memory vs Edges - All 9 Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 3. Memory vs Density
    ax = axes[2]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Density'], data['Memory_MB'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Graph Density (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory Usage (MB, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Memory vs Density - All 9 Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 4. Memory by Graph Type (Real vs Synthetic)
    ax = axes[3]
    df_pivot = df.pivot_table(values='Memory_MB', index='GraphType', columns='Algorithm', aggfunc='mean')
    if len(df_pivot) > 0:
        df_pivot.plot(kind='bar', ax=ax, alpha=0.8, edgecolor='black', linewidth=0.8)
        ax.set_xlabel('Graph Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Memory (MB, log scale)', fontsize=12, fontweight='bold')
        ax.set_title('Average Memory: Real vs Synthetic Graphs', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.legend(fontsize=8, title='Algorithm', loc='best', ncol=2)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0)
    
    # 5. Memory per Vertex
    ax = axes[4]
    df['MemoryPerVertex'] = df['Memory_MB'] / df['Vertices']
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['MemoryPerVertex'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory per Vertex (MB, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Efficiency: Memory per Vertex', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    # 6. Memory Heatmap by Algorithm and Dataset
    ax = axes[5]
    df_pivot2 = df.pivot_table(values='Memory_MB', index='Dataset', columns='Algorithm', aggfunc='mean')
    if len(df_pivot2) > 0:
        # Log scale for better visualization
        df_pivot2_log = np.log10(df_pivot2 + 1e-6)
        sns.heatmap(df_pivot2_log, annot=False, fmt='.2f', cmap='YlGnBu', ax=ax,
                   cbar_kws={'label': 'log10(Memory in MB)'})
        ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax.set_ylabel('Dataset', fontsize=12, fontweight='bold')
        ax.set_title('Memory Heatmap: All Algorithms vs All Datasets', fontsize=14, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=0, fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'memory_scaling_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: memory_scaling_analysis.png")
    plt.close()

def generate_comprehensive_report(df, output_dir):
    """Generate comprehensive runtime and memory report"""
    print("Generating comprehensive report...")
    
    report_file = output_dir / 'comprehensive_runtime_memory_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 120 + "\n")
        f.write("COMPREHENSIVE RUNTIME AND MEMORY ANALYSIS: ALL 9 ALGORITHMS\n")
        f.write("=" * 120 + "\n\n")
        
        f.write("ALGORITHMS ANALYZED:\n")
        f.write("-" * 120 + "\n")
        for i, algo in enumerate(ALL_ALGORITHMS, 1):
            category = df[df['Algorithm'] == algo]['Category'].iloc[0] if len(df[df['Algorithm'] == algo]) > 0 else 'Unknown'
            f.write(f"{i}. {algo} ({category})\n")
        f.write("\n")
        
        # Overall statistics
        f.write("1. OVERALL STATISTICS\n")
        f.write("-" * 120 + "\n")
        f.write(f"Total experiments: {len(df)}\n")
        f.write(f"  - Real datasets: {len(df[df['GraphType'] == 'Real'])}\n")
        f.write(f"  - Synthetic graphs: {len(df[df['GraphType'] == 'Synthetic'])}\n")
        f.write(f"Graph size range:\n")
        f.write(f"  - Vertices: {df['Vertices'].min():,} to {df['Vertices'].max():,}\n")
        f.write(f"  - Edges: {df['Edges'].min():,} to {df['Edges'].max():,}\n")
        f.write(f"  - Density: {df['Density'].min():.6e} to {df['Density'].max():.6e}\n\n")
        
        # Runtime analysis by algorithm
        f.write("2. RUNTIME ANALYSIS BY ALGORITHM\n")
        f.write("-" * 120 + "\n\n")
        
        for algo in ALL_ALGORITHMS:
            data = df[df['Algorithm'] == algo]
            if len(data) == 0:
                continue
                
            f.write(f"{algo}:\n")
            f.write(f"  Runtime:\n")
            f.write(f"    - Min: {data['Runtime_sec'].min():.6f}s\n")
            f.write(f"    - Max: {data['Runtime_sec'].max():.6f}s\n")
            f.write(f"    - Mean: {data['Runtime_sec'].mean():.6f}s\n")
            f.write(f"    - Median: {data['Runtime_sec'].median():.6f}s\n")
            f.write(f"    - Std Dev: {data['Runtime_sec'].std():.6f}s\n")
            
            # Correlation with graph size
            if len(data) > 2:
                try:
                    corr_v, _ = spearmanr(data['Vertices'], data['Runtime_sec'])
                    corr_e, _ = spearmanr(data['Edges'], data['Runtime_sec'])
                    f.write(f"  Scaling:\n")
                    f.write(f"    - Correlation with Vertices: {corr_v:.4f}\n")
                    f.write(f"    - Correlation with Edges: {corr_e:.4f}\n")
                except:
                    pass
            
            f.write("\n")
        
        # Memory analysis by algorithm
        f.write("3. MEMORY ANALYSIS BY ALGORITHM\n")
        f.write("-" * 120 + "\n\n")
        
        for algo in ALL_ALGORITHMS:
            data = df[df['Algorithm'] == algo]
            if len(data) == 0:
                continue
                
            f.write(f"{algo}:\n")
            f.write(f"  Memory:\n")
            f.write(f"    - Min: {data['Memory_MB'].min():.2f} MB\n")
            f.write(f"    - Max: {data['Memory_MB'].max():.2f} MB\n")
            f.write(f"    - Mean: {data['Memory_MB'].mean():.2f} MB\n")
            f.write(f"    - Median: {data['Memory_MB'].median():.2f} MB\n")
            f.write(f"    - Std Dev: {data['Memory_MB'].std():.2f} MB\n")
            
            # Correlation with graph size
            if len(data) > 2:
                try:
                    corr_v, _ = spearmanr(data['Vertices'], data['Memory_MB'])
                    corr_e, _ = spearmanr(data['Edges'], data['Memory_MB'])
                    f.write(f"  Scaling:\n")
                    f.write(f"    - Correlation with Vertices: {corr_v:.4f}\n")
                    f.write(f"    - Correlation with Edges: {corr_e:.4f}\n")
                except:
                    pass
            
            f.write("\n")
        
        # Comparison: Real vs Synthetic
        f.write("4. REAL vs SYNTHETIC GRAPH COMPARISON\n")
        f.write("-" * 120 + "\n\n")
        
        for graph_type in ['Real', 'Synthetic']:
            data = df[df['GraphType'] == graph_type]
            if len(data) == 0:
                continue
                
            f.write(f"{graph_type} Graphs:\n")
            f.write(f"  Average Runtime: {data['Runtime_sec'].mean():.6f}s\n")
            f.write(f"  Average Memory: {data['Memory_MB'].mean():.2f} MB\n")
            f.write(f"  Average Vertices: {data['Vertices'].mean():.0f}\n")
            f.write(f"  Average Edges: {data['Edges'].mean():.0f}\n\n")
        
        # Algorithm rankings
        f.write("5. ALGORITHM RANKINGS\n")
        f.write("-" * 120 + "\n\n")
        
        # Fastest algorithms
        avg_runtime = df.groupby('Algorithm')['Runtime_sec'].mean().sort_values()
        f.write("Fastest Algorithms (by average runtime):\n")
        for i, (algo, runtime) in enumerate(avg_runtime.items(), 1):
            f.write(f"  {i}. {algo}: {runtime:.6f}s\n")
        f.write("\n")
        
        # Most memory efficient
        avg_memory = df.groupby('Algorithm')['Memory_MB'].mean().sort_values()
        f.write("Most Memory Efficient Algorithms:\n")
        for i, (algo, memory) in enumerate(avg_memory.items(), 1):
            f.write(f"  {i}. {algo}: {memory:.2f} MB\n")
        f.write("\n")
        
        f.write("=" * 120 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 120 + "\n")
    
    print(f"  ✓ Saved: comprehensive_runtime_memory_report.txt")

def main():
    print("=" * 100)
    print("COMPREHENSIVE RUNTIME AND MEMORY ANALYSIS: ALL 9 ALGORITHMS")
    print("=" * 100)
    print()
    
    # Create output directory
    output_dir = Path("results/comprehensive_runtime_memory")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load all results
    print("Loading data from all algorithms...")
    df = load_all_results()
    
    if df is None:
        print("Error: Could not load data from algorithms")
        return
    
    print(f"  ✓ Loaded {len(df)} experiments")
    print(f"  ✓ Algorithms found: {', '.join(df['Algorithm'].unique())}\n")
    
    # Generate analyses
    analyze_runtime_scaling(df, output_dir)
    print()
    analyze_memory_scaling(df, output_dir)
    print()
    generate_comprehensive_report(df, output_dir)
    
    print()
    print("=" * 100)
    print("Analysis complete!")
    print("=" * 100)
    print(f"\nAll outputs saved to: {output_dir.absolute()}")
    print("\nGenerated files:")
    print("  - runtime_scaling_analysis.png (Runtime vs graph characteristics)")
    print("  - memory_scaling_analysis.png (Memory vs graph characteristics)")
    print("  - comprehensive_runtime_memory_report.txt (Detailed statistics)")
    print()

if __name__ == "__main__":
    main()

