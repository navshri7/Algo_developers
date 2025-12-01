#!/usr/bin/env python3
"""
Calculate Additional Performance Metrics: Comparisons and Throughput
Computes these metrics from existing algorithm results:
1. Number of Comparisons - Estimated based on algorithm complexity
2. Throughput - Nodes/Edges processed per second
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import re
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 10

# All algorithms
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

def estimate_comparisons(algorithm, vertices, edges, runtime_sec, **kwargs):
    """
    Estimate number of comparisons based on algorithm complexity
    Comparisons include: node comparisons, edge comparisons, value comparisons
    """
    n = vertices
    m = edges
    
    if algorithm == 'K-Core':
        # O(V + E) - each edge visited once, each vertex processed
        return n + m
    
    elif algorithm == 'Degree Centrality':
        # O(E) - scan all edges once
        return m
    
    elif algorithm == 'Betweenness (Exact)':
        # O(V*E) - for each vertex, BFS/DFS visits all edges
        # Each edge comparison in shortest path computation
        return n * m
    
    elif algorithm == 'Betweenness (Approximate)':
        # O(k*E) where k is number of samples
        samples = kwargs.get('samples', 100)  # Default sampling
        return samples * m
    
    elif algorithm == 'Bridging Centrality':
        # O(V*E) for betweenness + O(E) for bridging coefficient
        return n * m + m
    
    elif algorithm == 'Katz':
        # O(V*E*iterations) - each iteration: V*E operations
        iterations = kwargs.get('iterations', 50)  # Default iterations
        return n * m * iterations
    
    elif algorithm == 'Eigenvector':
        # O(V*E*iterations) - power iteration method
        iterations = kwargs.get('iterations', 50)  # Default iterations
        return n * m * iterations
    
    elif algorithm in ['HITS (Hub)', 'HITS (Authority)']:
        # O(V*E*iterations) - iterative computation
        iterations = kwargs.get('iterations', 50)  # Default iterations
        return n * m * iterations
    
    elif algorithm == 'PageRank':
        # O(V*E*iterations) - iterative computation
        iterations = kwargs.get('iterations', 50)  # Default iterations
        return n * m * iterations
    
    return 0

def calculate_throughput(vertices, edges, runtime_sec):
    """Calculate throughput: nodes/second and edges/second"""
    if runtime_sec <= 0:
        return 0.0, 0.0
    
    nodes_per_sec = vertices / runtime_sec
    edges_per_sec = edges / runtime_sec
    
    return nodes_per_sec, edges_per_sec

def load_from_detailed_files(result_dir, algorithm_name, suffix=None):
    """Load data from detailed.txt files"""
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
                
                # Extract vertices/nodes
                match = re.search(r'(?:Vertices|Nodes):\s*(\d+)', content)
                if match:
                    stats['Vertices'] = int(match.group(1))
                
                # Extract edges
                match = re.search(r'Edges:\s*(\d+)', content)
                if match:
                    stats['Edges'] = int(match.group(1))
                
                # Extract runtime
                match = re.search(r'Runtime[^:]*:\s*([\d.]+)', content)
                if match:
                    stats['Runtime_sec'] = float(match.group(1))
                
                # Extract memory
                match = re.search(r'(?:Peak Memory|Memory Usage)[^:]*:\s*([\d.]+)', content)
                if match:
                    stats['Memory_MB'] = float(match.group(1))
                
                # Extract iterations for iterative algorithms
                match = re.search(r'Iterations[^:]*:\s*(\d+)', content)
                if match:
                    stats['Iterations'] = int(match.group(1))
                else:
                    stats['Iterations'] = None
                
                # Extract samples for approximate algorithms
                match = re.search(r'Samples[^:]*:\s*(\d+)', content)
                if match:
                    stats['Samples'] = int(match.group(1))
                else:
                    stats['Samples'] = None
                
                stats['Dataset'] = dataset_name
                
                if 'Vertices' in stats and 'Edges' in stats and 'Runtime_sec' in stats:
                    # Calculate throughput
                    nodes_per_sec, edges_per_sec = calculate_throughput(
                        stats['Vertices'], stats['Edges'], stats['Runtime_sec']
                    )
                    stats['Throughput_NodesPerSec'] = nodes_per_sec
                    stats['Throughput_EdgesPerSec'] = edges_per_sec
                    
                    # Estimate comparisons
                    comparisons = estimate_comparisons(
                        algorithm_name,
                        stats['Vertices'],
                        stats['Edges'],
                        stats['Runtime_sec'],
                        iterations=stats.get('Iterations', 50),
                        samples=stats.get('Samples', 100)
                    )
                    stats['Comparisons'] = comparisons
                    
                    stats['Density'] = stats['Edges'] / (stats['Vertices'] * (stats['Vertices'] - 1)) if stats['Vertices'] > 1 else 0
                    stats['AvgDegree'] = 2 * stats['Edges'] / stats['Vertices'] if stats['Vertices'] > 0 else 0
                    summaries.append(stats)
        except Exception as e:
            continue
    
    if summaries:
        return pd.DataFrame(summaries)
    return None

def load_all_results():
    """Load results from all algorithms"""
    results = {}
    
    # K-Core
    kcore_csv = Path("results/synthetic/summary.csv")
    if kcore_csv.exists():
        df = pd.read_csv(kcore_csv)
        df['Algorithm'] = 'K-Core'
        df['Category'] = 'Foundational'
        results['K-Core'] = df
    else:
        df = load_from_detailed_files('results/synthetic', 'K-Core')
        if df is not None:
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
    else:
        df = load_from_detailed_files('results/betweenness/exact', 'Betweenness (Exact)')
        if df is not None:
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
    else:
        df = load_from_detailed_files('results/betweenness/approximate', 'Betweenness (Approximate)')
        if df is not None:
            df['Algorithm'] = 'Betweenness (Approximate)'
            df['Category'] = 'Foundational'
            results['Betweenness (Approximate)'] = df
    
    # Degree Centrality
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
    
    # Bridging Centrality
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
    else:
        df = load_from_detailed_files('results/centrality/katz', 'Katz')
        if df is not None:
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
    else:
        df = load_from_detailed_files('results/centrality/eigenvector', 'Eigenvector')
        if df is not None:
            df['Algorithm'] = 'Eigenvector'
            df['Category'] = 'Frontier'
            results['Eigenvector'] = df
    
    # HITS (Hub)
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
    
    # HITS (Authority)
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
    else:
        df = load_from_detailed_files('results/centrality/pagerank', 'PageRank', '_pagerank')
        if df is not None:
            df['Algorithm'] = 'PageRank'
            df['Category'] = 'Frontier'
            results['PageRank'] = df
    
    if not results:
        return None
    
    # Combine all results
    combined_df = pd.concat(results.values(), ignore_index=True)
    
    # Calculate metrics for all rows
    if 'Throughput_NodesPerSec' not in combined_df.columns:
        combined_df['Throughput_NodesPerSec'] = np.nan
    if 'Throughput_EdgesPerSec' not in combined_df.columns:
        combined_df['Throughput_EdgesPerSec'] = np.nan
    if 'Comparisons' not in combined_df.columns:
        combined_df['Comparisons'] = np.nan
    
    for idx, row in combined_df.iterrows():
        # Calculate throughput
        if pd.isna(combined_df.at[idx, 'Throughput_NodesPerSec']):
            nodes_per_sec, edges_per_sec = calculate_throughput(
                row['Vertices'], row['Edges'], row['Runtime_sec']
            )
            combined_df.at[idx, 'Throughput_NodesPerSec'] = nodes_per_sec
            combined_df.at[idx, 'Throughput_EdgesPerSec'] = edges_per_sec
        
        # Calculate comparisons
        if pd.isna(combined_df.at[idx, 'Comparisons']):
            iterations = 50
            samples = 100
            if 'Iterations' in row and pd.notna(row['Iterations']):
                iterations = int(row['Iterations'])
            if 'Samples' in row and pd.notna(row['Samples']):
                samples = int(row['Samples'])
            
            comparisons = estimate_comparisons(
                row['Algorithm'],
                row['Vertices'],
                row['Edges'],
                row['Runtime_sec'],
                iterations=iterations,
                samples=samples
            )
            combined_df.at[idx, 'Comparisons'] = comparisons
    
    # Classify graph types
    real_datasets = ['cit-DBLP', 'cit-HepTh', 'citeseer', 'cora']
    combined_df['GraphType'] = combined_df['Dataset'].apply(
        lambda x: 'Real' if x in real_datasets else 'Synthetic'
    )
    
    return combined_df

def analyze_comparisons(df, output_dir):
    """Analyze number of comparisons across algorithms"""
    print("Analyzing comparison metrics...")
    
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    axes = axes.flatten()
    
    # Color mapping
    colors = plt.cm.tab10(np.linspace(0, 1, len(ALL_ALGORITHMS)))
    algo_colors = {algo: colors[i] for i, algo in enumerate(ALL_ALGORITHMS)}
    
    # 1. Comparisons vs Vertices
    ax = axes[0]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['Comparisons'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Comparisons (log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Comparisons vs Vertices - All Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 2. Comparisons vs Edges
    ax = axes[1]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Edges'], data['Comparisons'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Comparisons (log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Comparisons vs Edges - All Algorithms', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # 3. Comparisons by Algorithm (box plot)
    ax = axes[2]
    data_list = []
    labels = []
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]['Comparisons']
        if len(data) > 0:
            data_list.append(data.values)
            labels.append(algo)
    if data_list:
        bp = ax.boxplot(data_list, labels=labels, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        ax.set_ylabel('Number of Comparisons (log scale)', fontsize=12, fontweight='bold')
        ax.set_title('Comparison Distribution by Algorithm', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Comparisons per Vertex
    ax = axes[3]
    df['ComparisonsPerVertex'] = df['Comparisons'] / df['Vertices']
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['ComparisonsPerVertex'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Comparisons per Vertex (log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Efficiency: Comparisons per Vertex', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    # 5. Comparisons Heatmap
    ax = axes[4]
    df_pivot = df.pivot_table(values='Comparisons', index='Dataset', columns='Algorithm', aggfunc='mean')
    if len(df_pivot) > 0:
        df_pivot_log = np.log10(df_pivot + 1)
        sns.heatmap(df_pivot_log, annot=False, fmt='.2f', cmap='YlOrRd', ax=ax,
                   cbar_kws={'label': 'log10(Comparisons)'})
        ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax.set_ylabel('Dataset', fontsize=12, fontweight='bold')
        ax.set_title('Comparisons Heatmap: All Algorithms vs All Datasets', fontsize=14, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=0, fontsize=8)
    
    # 6. Comparisons vs Runtime
    ax = axes[5]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Comparisons'], data['Runtime_sec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Comparisons (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Comparisons vs Runtime', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'comparisons_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: comparisons_analysis.png")
    plt.close()

def analyze_throughput(df, output_dir):
    """Analyze throughput metrics across algorithms"""
    print("Analyzing throughput metrics...")
    
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    axes = axes.flatten()
    
    # Color mapping
    colors = plt.cm.tab10(np.linspace(0, 1, len(ALL_ALGORITHMS)))
    algo_colors = {algo: colors[i] for i, algo in enumerate(ALL_ALGORITHMS)}
    
    # 1. Throughput (Nodes/sec) vs Vertices
    ax = axes[0]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Vertices'], data['Throughput_NodesPerSec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Vertices (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (Nodes/Second, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Throughput (Nodes/sec) vs Vertices', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    # 2. Throughput (Edges/sec) vs Edges
    ax = axes[1]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Edges'], data['Throughput_EdgesPerSec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Number of Edges (log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (Edges/Second, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Throughput (Edges/sec) vs Edges', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    # 3. Throughput by Algorithm (box plot)
    ax = axes[2]
    data_list = []
    labels = []
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]['Throughput_NodesPerSec']
        if len(data) > 0:
            data_list.append(data.values)
            labels.append(algo)
    if data_list:
        bp = ax.boxplot(data_list, labels=labels, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightgreen')
        ax.set_ylabel('Throughput (Nodes/Second, log scale)', fontsize=12, fontweight='bold')
        ax.set_title('Throughput Distribution by Algorithm', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Throughput comparison: Nodes vs Edges
    ax = axes[3]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Throughput_NodesPerSec'], data['Throughput_EdgesPerSec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Throughput (Nodes/Second, log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (Edges/Second, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Throughput: Nodes/sec vs Edges/sec', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    # 5. Throughput Heatmap
    ax = axes[4]
    df_pivot = df.pivot_table(values='Throughput_NodesPerSec', index='Dataset', columns='Algorithm', aggfunc='mean')
    if len(df_pivot) > 0:
        df_pivot_log = np.log10(df_pivot + 1)
        sns.heatmap(df_pivot_log, annot=False, fmt='.2f', cmap='YlGnBu', ax=ax,
                   cbar_kws={'label': 'log10(Nodes/Second)'})
        ax.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
        ax.set_ylabel('Dataset', fontsize=12, fontweight='bold')
        ax.set_title('Throughput Heatmap: All Algorithms vs All Datasets', fontsize=14, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=0, fontsize=8)
    
    # 6. Throughput vs Runtime
    ax = axes[5]
    for algo in ALL_ALGORITHMS:
        data = df[df['Algorithm'] == algo]
        if len(data) > 0:
            category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
            marker = 'o' if category == 'Foundational' else 's'
            ax.scatter(data['Runtime_sec'], data['Throughput_NodesPerSec'], 
                      label=algo, alpha=0.7, s=100, marker=marker,
                      color=algo_colors.get(algo, 'gray'),
                      edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (Nodes/Second, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Throughput vs Runtime', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(fontsize=8, ncol=2, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'throughput_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: throughput_analysis.png")
    plt.close()

def generate_metrics_report(df, output_dir):
    """Generate comprehensive metrics report"""
    print("Generating metrics report...")
    
    report_file = output_dir / 'metrics_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 120 + "\n")
        f.write("PERFORMANCE METRICS ANALYSIS: COMPARISONS AND THROUGHPUT\n")
        f.write("=" * 120 + "\n\n")
        
        f.write("METRICS DOCUMENTATION\n")
        f.write("-" * 120 + "\n\n")
        
        f.write("1. WALL-CLOCK TIME (Runtime)\n")
        f.write("   - Definition: Total elapsed time from algorithm start to completion\n")
        f.write("   - Unit: Seconds\n")
        f.write("   - Measurement: High-resolution clock timestamps\n")
        f.write("   - Includes: Graph loading, computation, and result writing\n\n")
        
        f.write("2. MEMORY USAGE\n")
        f.write("   - Definition: Peak memory consumption during algorithm execution\n")
        f.write("   - Unit: Megabytes (MB)\n")
        f.write("   - Measurement: System resource usage tracking (getrusage)\n")
        f.write("   - Includes: Data structures, temporary variables, graph representation\n\n")
        
        f.write("3. SOLUTION QUALITY\n")
        f.write("   - Definition: Maximum centrality value computed by the algorithm\n")
        f.write("   - Metrics:\n")
        f.write("     • K-Core: Maximum coreness value\n")
        f.write("     • Betweenness: Maximum betweenness centrality\n")
        f.write("     • Degree: Maximum degree (in/out/total)\n")
        f.write("     • Katz/Eigenvector/HITS/PageRank: Maximum centrality score\n")
        f.write("   - Purpose: Validates correctness and identifies most important nodes\n\n")
        
        f.write("4. NUMBER OF COMPARISONS (NEW METRIC)\n")
        f.write("   - Definition: Estimated number of comparison operations performed\n")
        f.write("   - Unit: Count (operations)\n")
        f.write("   - Estimation: Based on algorithm complexity and graph characteristics\n")
        f.write("   - Includes:\n")
        f.write("     • Node comparisons (for sorting, searching)\n")
        f.write("     • Edge comparisons (for path finding, traversal)\n")
        f.write("     • Value comparisons (for ranking, selection)\n")
        f.write("   - Algorithm-specific estimates:\n")
        f.write("     • K-Core: O(V + E) = V + E comparisons\n")
        f.write("     • Degree: O(E) = E comparisons\n")
        f.write("     • Betweenness (Exact): O(V*E) = V*E comparisons\n")
        f.write("     • Betweenness (Approx): O(k*E) = samples * E comparisons\n")
        f.write("     • Iterative algorithms: O(V*E*iterations) comparisons\n\n")
        
        f.write("5. THROUGHPUT (NEW METRIC)\n")
        f.write("   - Definition: Processing rate of graph elements\n")
        f.write("   - Units:\n")
        f.write("     • Nodes per second: Vertices / Runtime\n")
        f.write("     • Edges per second: Edges / Runtime\n")
        f.write("   - Purpose: Measures algorithm efficiency and scalability\n")
        f.write("   - Interpretation: Higher throughput = more efficient processing\n\n")
        
        f.write("ALGORITHM-SPECIFIC METRICS\n")
        f.write("-" * 120 + "\n\n")
        
        for algo in ALL_ALGORITHMS:
            data = df[df['Algorithm'] == algo]
            if len(data) == 0:
                continue
            
            f.write(f"{algo}:\n")
            f.write(f"  Comparisons:\n")
            f.write(f"    - Min: {data['Comparisons'].min():,.0f}\n")
            f.write(f"    - Max: {data['Comparisons'].max():,.0f}\n")
            f.write(f"    - Mean: {data['Comparisons'].mean():,.0f}\n")
            f.write(f"    - Median: {data['Comparisons'].median():,.0f}\n")
            
            f.write(f"  Throughput (Nodes/sec):\n")
            f.write(f"    - Min: {data['Throughput_NodesPerSec'].min():,.0f}\n")
            f.write(f"    - Max: {data['Throughput_NodesPerSec'].max():,.0f}\n")
            f.write(f"    - Mean: {data['Throughput_NodesPerSec'].mean():,.0f}\n")
            f.write(f"    - Median: {data['Throughput_NodesPerSec'].median():,.0f}\n")
            
            f.write(f"  Throughput (Edges/sec):\n")
            f.write(f"    - Min: {data['Throughput_EdgesPerSec'].min():,.0f}\n")
            f.write(f"    - Max: {data['Throughput_EdgesPerSec'].max():,.0f}\n")
            f.write(f"    - Mean: {data['Throughput_EdgesPerSec'].mean():,.0f}\n")
            f.write(f"    - Median: {data['Throughput_EdgesPerSec'].median():,.0f}\n")
            f.write("\n")
        
        # Rankings
        f.write("ALGORITHM RANKINGS\n")
        f.write("-" * 120 + "\n\n")
        
        avg_comparisons = df.groupby('Algorithm')['Comparisons'].mean().sort_values()
        f.write("Most Comparison-Efficient (fewest comparisons):\n")
        for i, (algo, comp) in enumerate(avg_comparisons.items(), 1):
            f.write(f"  {i}. {algo}: {comp:,.0f} comparisons\n")
        f.write("\n")
        
        avg_throughput = df.groupby('Algorithm')['Throughput_NodesPerSec'].mean().sort_values(ascending=False)
        f.write("Highest Throughput (nodes/second):\n")
        for i, (algo, tp) in enumerate(avg_throughput.items(), 1):
            f.write(f"  {i}. {algo}: {tp:,.0f} nodes/sec\n")
        f.write("\n")
        
        f.write("=" * 120 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 120 + "\n")
    
    print(f"  ✓ Saved: metrics_report.txt")

def main():
    print("=" * 100)
    print("CALCULATING ADDITIONAL PERFORMANCE METRICS: COMPARISONS AND THROUGHPUT")
    print("=" * 100)
    print()
    
    # Create output directory
    output_dir = Path("results/metrics_analysis")
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
    analyze_comparisons(df, output_dir)
    print()
    analyze_throughput(df, output_dir)
    print()
    generate_metrics_report(df, output_dir)
    
    print()
    print("=" * 100)
    print("Metrics calculation complete!")
    print("=" * 100)
    print(f"\nAll outputs saved to: {output_dir.absolute()}")
    print("\nGenerated files:")
    print("  - comparisons_analysis.png (Number of comparisons analysis)")
    print("  - throughput_analysis.png (Throughput analysis)")
    print("  - metrics_report.txt (Comprehensive metrics documentation and statistics)")
    print()

if __name__ == "__main__":
    main()

