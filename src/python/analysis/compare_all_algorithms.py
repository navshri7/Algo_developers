#!/usr/bin/env python3
"""
Comprehensive Algorithm Comparison: Foundational vs Frontier Research
Analyzes which algorithms detect what across all centrality measures
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr, kendalltau, pearsonr
import warnings
import re
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

# Algorithm classification
FOUNDATIONAL = ['K-Core', 'Betweenness (Exact)', 'Degree Centrality', 'Bridging Centrality']
FRONTIER = ['Katz', 'Eigenvector', 'HITS (Hub)', 'HITS (Authority)', 'PageRank']
CITATION_SPECIFIC = ['Degree Centrality', 'Bridging Centrality', 'HITS (Hub)', 'HITS (Authority)']

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
    
    # Betweenness Exact
    bet_csv = Path("results/betweenness/exact/summary.csv")
    if bet_csv.exists():
        df = pd.read_csv(bet_csv)
        df['Algorithm'] = 'Betweenness (Exact)'
        df['Category'] = 'Foundational'
        results['Betweenness (Exact)'] = df
    
    # Degree Centrality
    deg_csv = Path("results/degree_centrality/summary.csv")
    if deg_csv.exists():
        df = pd.read_csv(deg_csv)
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
    
    # HITS (Hub)
    hits_hub_csv = Path("results/hits/summary_hub.csv")
    if hits_hub_csv.exists():
        df = pd.read_csv(hits_hub_csv)
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
    
    # PageRank
    pagerank_csv = Path("results/centrality/pagerank/summary.csv")
    if pagerank_csv.exists():
        df = pd.read_csv(pagerank_csv)
        df['Algorithm'] = 'PageRank'
        df['Category'] = 'Frontier'
        results['PageRank'] = df
    
    if not results:
        return None
    
    return pd.concat(results.values(), ignore_index=True)

def analyze_node_rankings(output_dir):
    """Analyze which nodes are ranked highest by each algorithm"""
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    axes = axes.flatten()
    
    # Get top nodes for each algorithm on a real dataset
    datasets_to_check = ['cit-DBLP', 'cit-HepTh', 'citeseer', 'cora']
    overlap_report = []
    
    for idx, dataset in enumerate(datasets_to_check):
        if idx >= len(axes):
            break
        
        ax = axes[idx]
        top_nodes = {}
        
        # K-Core
        kcore_file = Path(f"results/synthetic/{dataset}_detailed.txt")
        if kcore_file.exists():
            top_nodes['K-Core'] = extract_top_nodes(kcore_file, 20)
        
        # Betweenness
        bet_file = Path(f"results/betweenness/exact/{dataset}_detailed.txt")
        if bet_file.exists():
            top_nodes['Betweenness'] = extract_top_nodes(bet_file, 20)
        
        # Degree Centrality
        deg_file = Path(f"results/degree_centrality/{dataset}_detailed.txt")
        if deg_file.exists():
            top_nodes['Degree'] = extract_top_nodes(deg_file, 20)
        
        # Bridging Centrality
        brid_file = Path(f"results/bridging_centrality/{dataset}_detailed.txt")
        if brid_file.exists():
            top_nodes['Bridging'] = extract_top_nodes(brid_file, 20)
        
        # Katz
        katz_file = Path(f"results/centrality/katz/{dataset}_detailed.txt")
        if katz_file.exists():
            top_nodes['Katz'] = extract_top_nodes(katz_file, 20)
        
        # Eigenvector
        eigen_file = Path(f"results/centrality/eigenvector/{dataset}_detailed.txt")
        if eigen_file.exists():
            top_nodes['Eigenvector'] = extract_top_nodes(eigen_file, 20)
        
        # HITS (Hub)
        hits_hub_file = Path(f"results/hits/{dataset}_hub_detailed.txt")
        if hits_hub_file.exists():
            top_nodes['HITS (Hub)'] = extract_top_nodes(hits_hub_file, 20)
        
        # HITS (Authority)
        hits_auth_file = Path(f"results/hits/{dataset}_authority_detailed.txt")
        if hits_auth_file.exists():
            top_nodes['HITS (Auth)'] = extract_top_nodes(hits_auth_file, 20)
        
        # PageRank
        pagerank_file = Path(f"results/centrality/pagerank/{dataset}_pagerank_detailed.txt")
        if pagerank_file.exists():
            top_nodes['PageRank'] = extract_top_nodes(pagerank_file, 20)
        
        if not top_nodes:
            ax.text(0.5, 0.5, f'{dataset}\n(No data)', ha='center', va='center')
            ax.set_title(dataset, fontsize=12, fontweight='bold')
            continue
        
        # Create overlap matrix
        all_nodes = set()
        for nodes in top_nodes.values():
            all_nodes.update(nodes)
        
        overlap_matrix = np.zeros((len(top_nodes), len(top_nodes)))
        algos = list(top_nodes.keys())
        
        for i, algo1 in enumerate(algos):
            for j, algo2 in enumerate(algos):
                overlap = len(set(top_nodes[algo1]) & set(top_nodes[algo2]))
                overlap_matrix[i, j] = overlap
        
        # Plot heatmap
        sns.heatmap(overlap_matrix, annot=True, fmt='.0f', cmap='YlOrRd',
                   xticklabels=algos, yticklabels=algos, ax=ax,
                   cbar_kws={'label': 'Overlap (Top 20)'})
        ax.set_title(f'{dataset} - Top 20 Node Overlap', fontsize=12, fontweight='bold')
        
        # Store overlap data for report
        overlap_report.append({
            'dataset': dataset,
            'algos': algos,
            'matrix': overlap_matrix,
            'top_nodes': top_nodes
        })
    
    plt.tight_layout()
    plt.savefig(output_dir / 'node_ranking_overlap.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: node_ranking_overlap.png")
    plt.close()
    
    # Save overlap report to file
    save_overlap_report(output_dir, overlap_report)

def save_overlap_report(output_dir, overlap_report):
    """Save node ranking overlap analysis to file"""
    report_file = output_dir / 'node_ranking_overlap_report.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 120 + "\n")
        f.write("TOP 20 NODE RANKING OVERLAP ANALYSIS\n")
        f.write("=" * 120 + "\n\n")
        
        for report_data in overlap_report:
            dataset = report_data['dataset']
            algos = report_data['algos']
            matrix = report_data['matrix']
            top_nodes = report_data['top_nodes']
            
            f.write(f"\n{dataset.upper()}\n")
            f.write("-" * 120 + "\n\n")
            
            # Overlap matrix
            f.write("OVERLAP MATRIX (Top 20 nodes):\n")
            f.write("-" * 120 + "\n")
            
            # Header
            f.write(f"{'Algorithm':<25}")
            for algo in algos:
                f.write(f"{algo:<20}")
            f.write("\n")
            f.write("-" * 120 + "\n")
            
            # Rows
            for i, algo1 in enumerate(algos):
                f.write(f"{algo1:<25}")
                for j, algo2 in enumerate(algos):
                    f.write(f"{int(matrix[i, j]):<20}")
                f.write("\n")
            
            f.write("\n")
            
            # Top 20 nodes for each algorithm
            f.write("TOP 20 NODES BY ALGORITHM:\n")
            f.write("-" * 120 + "\n\n")
            
            for algo in algos:
                f.write(f"{algo}:\n")
                nodes = top_nodes[algo]
                for rank, node_id in enumerate(nodes, 1):
                    f.write(f"  {rank:2d}. Node {node_id}\n")
                f.write("\n")
            
            f.write("\n")
    
    print(f"  ✓ Saved: node_ranking_overlap_report.txt")

def extract_top_nodes(filepath, k=10):
    """Extract top k nodes from detailed results file"""
    nodes = []
    try:
        with open(filepath, 'r') as f:
            in_section = False
            count = 0
            for line in f:
                if "Top" in line or "Rank" in line:
                    in_section = True
                    continue
                if in_section and line.strip() and not line.startswith("==="):
                    # Try tab-separated format first (betweenness, etc.)
                    parts = line.strip().split('\t')
                    if len(parts) >= 2 and parts[0].isdigit():
                        try:
                            node_id = int(parts[1])
                            nodes.append(node_id)
                            count += 1
                            if count >= k:
                                break
                        except (ValueError, IndexError):
                            continue
                    else:
                        # Try space-separated format with "Node" prefix (degree centrality)
                        # Format: "  1. Node 62: 709"
                        match = re.search(r'Node\s+(\d+)', line)
                        if match:
                            try:
                                node_id = int(match.group(1))
                                nodes.append(node_id)
                                count += 1
                                if count >= k:
                                    break
                            except (ValueError, IndexError):
                                continue
    except:
        pass
    
    return nodes

def analyze_runtime_characteristics(df, output_dir):
    """Analyze runtime characteristics of each algorithm"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Runtime vs Vertices
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
        marker = 'o' if category == 'Foundational' else 's'
        ax1.scatter(data['Vertices'], data['Runtime_sec'], label=algo, 
                   alpha=0.7, s=120, marker=marker, edgecolors='black', linewidth=0.5)
    
    ax1.set_xlabel('Vertices (log scale)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Runtime (seconds, log scale)', fontsize=12, fontweight='bold')
    ax1.set_title('Runtime Comparison: All Algorithms', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Runtime by category
    df_pivot = df.pivot_table(values='Runtime_sec', index='Dataset', columns='Algorithm')
    if len(df_pivot) > 0:
        df_pivot.plot(kind='bar', ax=ax2, alpha=0.7, edgecolor='black', linewidth=0.8)
        ax2.set_xlabel('Dataset', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Runtime (seconds)', fontsize=12, fontweight='bold')
        ax2.set_title('Runtime by Dataset', fontsize=14, fontweight='bold')
        ax2.set_yscale('log')
        ax2.legend(fontsize=9, title='Algorithm', loc='best')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Memory comparison
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
        marker = 'o' if category == 'Foundational' else 's'
        ax3.scatter(data['Vertices'], data['Memory_MB'], label=algo,
                   alpha=0.7, s=120, marker=marker, edgecolors='black', linewidth=0.5)
    
    ax3.set_xlabel('Vertices (log scale)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Memory (MB, log scale)', fontsize=12, fontweight='bold')
    ax3.set_title('Memory Usage Comparison', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    ax3.grid(True, alpha=0.3)
    
    # Efficiency: Runtime per vertex
    df['RuntimePerVertex'] = df['Runtime_sec'] / df['Vertices']
    for algo in df['Algorithm'].unique():
        data = df[df['Algorithm'] == algo]
        category = data['Category'].iloc[0] if 'Category' in data.columns else 'Unknown'
        marker = 'o' if category == 'Foundational' else 's'
        ax4.scatter(data['Vertices'], data['RuntimePerVertex'], label=algo,
                   alpha=0.7, s=120, marker=marker, edgecolors='black', linewidth=0.5)
    
    ax4.set_xlabel('Vertices (log scale)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Runtime per Vertex (log scale)', fontsize=12, fontweight='bold')
    ax4.set_title('Efficiency: Runtime per Vertex', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'runtime_characteristics.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: runtime_characteristics.png")
    plt.close()

def generate_comprehensive_report(df, output_dir):
    """Generate comprehensive comparison report"""
    report_file = output_dir / 'comprehensive_analysis.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("COMPREHENSIVE ALGORITHM COMPARISON: FOUNDATIONAL vs FRONTIER RESEARCH\n")
        f.write("=" * 100 + "\n\n")
        
        # Executive Summary
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 100 + "\n")
        f.write("This report compares four centrality algorithms across synthetic and real-world datasets:\n\n")
        f.write("FOUNDATIONAL ALGORITHMS (Classical Graph Theory):\n")
        f.write("  1. K-Core Decomposition - Identifies nested core-periphery structure\n")
        f.write("     - Time: O(V + E), Space: O(V + E)\n")
        f.write("     - Detects: Structural cohesion, network hierarchy\n\n")
        f.write("  2. Betweenness Centrality (Exact) - Measures node importance in shortest paths\n")
        f.write("     - Time: O(V·E), Space: O(V + E)\n")
        f.write("     - Detects: Bridge nodes, network bottlenecks\n\n")
        
        f.write("FRONTIER ALGORITHMS (Modern Network Science):\n")
        f.write("  3. Katz Centrality - Iterative measure with attenuation factor\n")
        f.write("     - Time: O(V·E·iterations), Space: O(V + E)\n")
        f.write("     - Detects: Influence propagation, weighted connections\n\n")
        f.write("  4. Eigenvector Centrality - Importance based on connections to important nodes\n")
        f.write("     - Time: O(V·E·iterations), Space: O(V + E)\n")
        f.write("     - Detects: Hub nodes, network prestige\n\n")
        
        # Performance Analysis
        f.write("\n1. PERFORMANCE ANALYSIS\n")
        f.write("-" * 100 + "\n")
        
        for algo in df['Algorithm'].unique():
            data = df[df['Algorithm'] == algo]
            f.write(f"\n{algo}:\n")
            f.write(f"  Runtime:\n")
            f.write(f"    - Min: {data['Runtime_sec'].min():.6f}s\n")
            f.write(f"    - Max: {data['Runtime_sec'].max():.6f}s\n")
            f.write(f"    - Mean: {data['Runtime_sec'].mean():.6f}s\n")
            f.write(f"    - Median: {data['Runtime_sec'].median():.6f}s\n")
            f.write(f"  Memory:\n")
            f.write(f"    - Min: {data['Memory_MB'].min():.2f} MB\n")
            f.write(f"    - Max: {data['Memory_MB'].max():.2f} MB\n")
            f.write(f"    - Mean: {data['Memory_MB'].mean():.2f} MB\n")
        
        # What Each Algorithm Detects
        f.write("\n\n2. WHAT EACH ALGORITHM DETECTS\n")
        f.write("-" * 100 + "\n")
        
        f.write("\nK-CORE DECOMPOSITION:\n")
        f.write("  Detects:\n")
        f.write("    • Core-periphery structure\n")
        f.write("    • Network hierarchy and layers\n")
        f.write("    • Structural cohesion groups\n")
        f.write("    • Robustness and resilience\n")
        f.write("  Best for:\n")
        f.write("    • Social network analysis\n")
        f.write("    • Identifying influential communities\n")
        f.write("    • Network stability analysis\n")
        f.write("  Limitations:\n")
        f.write("    • Doesn't consider path importance\n")
        f.write("    • Treats all edges equally\n")
        f.write("    • Undirected perspective\n")
        
        f.write("\nBETWEENNESS CENTRALITY (EXACT):\n")
        f.write("  Detects:\n")
        f.write("    • Bridge nodes and bottlenecks\n")
        f.write("    • Information flow control points\n")
        f.write("    • Network vulnerability points\n")
        f.write("    • Shortest path dependencies\n")
        f.write("  Best for:\n")
        f.write("    • Communication networks\n")
        f.write("    • Transportation networks\n")
        f.write("    • Finding critical infrastructure\n")
        f.write("  Limitations:\n")
        f.write("    • Computationally expensive O(V·E)\n")
        f.write("    • Assumes shortest path routing\n")
        f.write("    • Sensitive to network structure\n")
        
        f.write("\nKATZ CENTRALITY:\n")
        f.write("  Detects:\n")
        f.write("    • Influence and reachability\n")
        f.write("    • Weighted path importance\n")
        f.write("    • Attenuation-based importance\n")
        f.write("    • Connection quality and distance\n")
        f.write("  Best for:\n")
        f.write("    • Citation networks\n")
        f.write("    • Recommendation systems\n")
        f.write("    • Influence propagation models\n")
        f.write("  Advantages over Betweenness:\n")
        f.write("    • Considers all paths, not just shortest\n")
        f.write("    • Faster convergence\n")
        f.write("    • More stable for sparse networks\n")
        
        f.write("\nEIGENVECTOR CENTRALITY:\n")
        f.write("  Detects:\n")
        f.write("    • Hub nodes and prestige\n")
        f.write("    • Recursive importance\n")
        f.write("    • Network influence propagation\n")
        f.write("    • Spectral properties\n")
        f.write("  Best for:\n")
        f.write("    • Web page ranking (PageRank basis)\n")
        f.write("    • Scientific collaboration networks\n")
        f.write("    • Identifying key opinion leaders\n")
        f.write("  Advantages over Katz:\n")
        f.write("    • No attenuation parameter needed\n")
        f.write("    • Theoretically grounded in spectral analysis\n")
        f.write("    • Better for recursive importance\n")
        
        # Comparative Analysis
        f.write("\n\n3. COMPARATIVE ANALYSIS\n")
        f.write("-" * 100 + "\n")
        
        f.write("\nFOUNDATIONAL vs FRONTIER:\n")
        f.write("  Foundational (K-Core, Betweenness):\n")
        f.write("    • Established mathematical foundations\n")
        f.write("    • Well-understood properties\n")
        f.write("    • Deterministic results\n")
        f.write("    • Limited parameters\n")
        f.write("    • Slower for large graphs\n\n")
        
        f.write("  Frontier (Katz, Eigenvector):\n")
        f.write("    • Modern network science approach\n")
        f.write("    • Parameter-dependent\n")
        f.write("    • Iterative computation\n")
        f.write("    • Better scalability\n")
        f.write("    • More flexible modeling\n")
        
        # Recommendations
        f.write("\n\n4. RECOMMENDATIONS BY USE CASE\n")
        f.write("-" * 100 + "\n")
        
        f.write("\nSmall Networks (< 1000 nodes):\n")
        f.write("  • Use: Betweenness Centrality (exact)\n")
        f.write("  • Reason: Accurate, deterministic, manageable computation\n")
        f.write("  • Also try: K-Core for structure, Eigenvector for hubs\n\n")
        
        f.write("Medium Networks (1000-100k nodes):\n")
        f.write("  • Use: Katz or Eigenvector Centrality\n")
        f.write("  • Reason: Good balance of accuracy and speed\n")
        f.write("  • Also try: K-Core for fast structural analysis\n\n")
        
        f.write("Large Networks (> 100k nodes):\n")
        f.write("  • Use: K-Core Decomposition\n")
        f.write("  • Reason: Linear time complexity\n")
        f.write("  • Alternative: Approximate Betweenness\n\n")
        
        f.write("Citation Networks:\n")
        f.write("  • Primary: Eigenvector or Katz Centrality\n")
        f.write("  • Secondary: Betweenness for bottlenecks\n")
        f.write("  • Tertiary: K-Core for community structure\n\n")
        
        f.write("Social Networks:\n")
        f.write("  • Primary: K-Core for communities\n")
        f.write("  • Secondary: Eigenvector for influencers\n")
        f.write("  • Tertiary: Betweenness for bridges\n\n")
        
        f.write("Infrastructure Networks:\n")
        f.write("  • Primary: Betweenness for critical nodes\n")
        f.write("  • Secondary: K-Core for robustness\n")
        f.write("  • Tertiary: Katz for redundancy\n")
        
        # Correlation Analysis
        f.write("\n\n5. CORRELATION ANALYSIS\n")
        f.write("-" * 100 + "\n")
        f.write("Analyzing how different algorithms rank the same nodes...\n\n")
        
        # Dataset-specific analysis
        f.write("\n\n6. DATASET-SPECIFIC INSIGHTS\n")
        f.write("-" * 100 + "\n")
        
        for dataset in df['Dataset'].unique():
            data = df[df['Dataset'] == dataset]
            f.write(f"\n{dataset}:\n")
            f.write(f"  Vertices: {data['Vertices'].iloc[0]:,}\n")
            f.write(f"  Edges: {data['Edges'].iloc[0]:,}\n")
            f.write(f"  Density: {data['Density'].iloc[0]:.6e}\n")
            f.write(f"  Avg Degree: {data['AvgDegree'].iloc[0]:.2f}\n")
            f.write(f"  Algorithm Performance:\n")
            for algo in data['Algorithm'].unique():
                algo_data = data[data['Algorithm'] == algo]
                f.write(f"    {algo}: {algo_data['Runtime_sec'].iloc[0]:.6f}s, "
                       f"{algo_data['Memory_MB'].iloc[0]:.2f} MB\n")
        
        f.write("\n" + "=" * 100 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 100 + "\n")
    
    print(f"  ✓ Saved: comprehensive_analysis.txt")

def print_top_20_comparison(output_dir):
    """Visualize, print, and save top 20 nodes for each algorithm side-by-side (REAL GRAPHS ONLY)"""
    report_file = output_dir / 'top_20_nodes_comparison.txt'
    
    # Real graphs only - for foundational vs frontier comparison
    graphs = [
        ('data/converted_datasets/cit-DBLP.txt', 'cit-DBLP'),
        ('data/converted_datasets/cit-HepTh.txt', 'cit-HepTh'),
        ('data/converted_datasets/citeseer.txt', 'CiteSeer'),
        ('data/converted_datasets/cora.txt', 'Cora'),
    ]
    
    # Create visualization figure
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()
    
    with open(report_file, 'w') as f:
        f.write("\n" + "=" * 150 + "\n")
        f.write("TOP 20 NODES BY EACH ALGORITHM - FOUNDATIONAL vs FRONTIER (REAL GRAPHS)\n")
        f.write("=" * 150 + "\n\n")
        
        for idx, (graph_file, graph_name) in enumerate(graphs):
            if idx >= len(axes):
                break
                
            if not Path(graph_file).exists():
                continue
            
            ax = axes[idx]
            f.write(f"\n{graph_name}\n")
            f.write("-" * 150 + "\n\n")
            
            # Print to console
            print(f"\n{'='*100}")
            print(f"{graph_name.upper()} - TOP 20 NODES COMPARISON")
            print(f"{'='*100}\n")
            
            graph_base = Path(graph_file).stem
            
            # Load top 20 from each algorithm
            all_top_20 = {}
            
            algorithms = [
                ('K-Core', 'results/synthetic', None),
                ('Betweenness', 'results/betweenness/exact', None),
                ('Degree', 'results/degree_centrality', None),
                ('Bridging', 'results/bridging_centrality', None),
                ('Katz', 'results/centrality/katz', None),
                ('Eigenvector', 'results/centrality/eigenvector', None),
                ('HITS (Hub)', 'results/hits', '_hub'),
                ('HITS (Auth)', 'results/hits', '_authority'),
                ('PageRank', 'results/centrality/pagerank', None),
            ]
            
            for algo_name, result_dir, suffix in algorithms:
                if suffix:
                    result_file = Path(result_dir) / f"{graph_base}{suffix}_detailed.txt"
                else:
                    if algo_name == 'PageRank':
                        result_file = Path(result_dir) / f"{graph_base}_pagerank_detailed.txt"
                    else:
                        result_file = Path(result_dir) / f"{graph_base}_detailed.txt"
                
                if result_file.exists():
                    rankings = extract_top_nodes_with_values(result_file, 20)
                    all_top_20[algo_name] = rankings
                else:
                    all_top_20[algo_name] = []
        
            # Write side-by-side table to file
            max_rows = max(len(v) for v in all_top_20.values()) if all_top_20.values() else 0
            
            # Header
            header = ""
            for algo_name in all_top_20.keys():
                header += f"{algo_name:25} | "
            f.write(header + "\n")
            f.write("-" * 150 + "\n")
            print(header)
            print("-" * 150)
            
            # Rows
            for row_idx in range(max_rows):
                row_str = ""
                for algo_name in all_top_20.keys():
                    if row_idx < len(all_top_20[algo_name]):
                        node_id, value = all_top_20[algo_name][row_idx]
                        row_str += f"N{node_id:4d}({value:9.6f}) | "
                    else:
                        row_str += f"{'':25} | "
                f.write(row_str + "\n")
                print(row_str)
            
            f.write("\n")
            print()
            
            # Create visualization: Node overlap heatmap
            if all_top_20:
                algo_names = list(all_top_20.keys())
                overlap_matrix = np.zeros((len(algo_names), len(algo_names)))
                
                for i, algo1 in enumerate(algo_names):
                    nodes1 = set(node_id for node_id, _ in all_top_20[algo1])
                    for j, algo2 in enumerate(algo_names):
                        nodes2 = set(node_id for node_id, _ in all_top_20[algo2])
                        overlap = len(nodes1 & nodes2)
                        overlap_matrix[i, j] = overlap
                
                sns.heatmap(overlap_matrix, annot=True, fmt='.0f', cmap='YlOrRd',
                           xticklabels=algo_names, yticklabels=algo_names, ax=ax,
                           cbar_kws={'label': 'Overlap (Top 20)'})
                ax.set_title(f'{graph_name} - Top 20 Node Overlap', fontsize=11, fontweight='bold')
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    viz_file = output_dir / 'top_20_nodes_comparison_visualization.png'
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved visualization: top_20_nodes_comparison_visualization.png")
    plt.close()
    
    print(f"  ✓ Saved: top_20_nodes_comparison.txt")

def extract_top_nodes_with_values(filepath, k=20):
    """Extract top k nodes with their values from detailed results file"""
    nodes = []
    try:
        with open(filepath, 'r') as f:
            in_section = False
            count = 0
            for line in f:
                if "Top" in line or "Rank" in line:
                    in_section = True
                    continue
                if in_section and line.strip() and not line.startswith("==="):
                    # Try tab-separated format first (betweenness, etc.)
                    parts = line.strip().split('\t')
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            node_id = int(parts[1])
                            value = float(parts[2])
                            nodes.append((node_id, value))
                            count += 1
                            if count >= k:
                                break
                        except (ValueError, IndexError):
                            continue
                    else:
                        # Try space-separated format with "Node" prefix (degree centrality)
                        # Format: "  1. Node 62: 709"
                        match = re.search(r'Node\s+(\d+):\s*([\d.]+)', line)
                        if match:
                            try:
                                node_id = int(match.group(1))
                                value = float(match.group(2))
                                nodes.append((node_id, value))
                                count += 1
                                if count >= k:
                                    break
                            except (ValueError, IndexError):
                                continue
    except:
        pass
    
    return nodes

def main():
    print("=" * 100)
    print("COMPREHENSIVE ALGORITHM COMPARISON: FOUNDATIONAL vs FRONTIER RESEARCH")
    print("=" * 100)
    print()
    
    # Create output directory
    viz_dir = Path("results/algorithm_comparison")
    viz_dir.mkdir(exist_ok=True, parents=True)
    
    # Load data
    print("Loading data from all algorithms...")
    df = load_all_results()
    
    if df is None:
        print("Error: Could not load data from algorithms")
        return
    
    print(f"  ✓ Loaded {len(df)} experiments\n")
    
    # Generate visualizations
    print("Generating visualizations...")
    print("-" * 100)
    
    analyze_node_rankings(viz_dir)
    analyze_runtime_characteristics(df, viz_dir)
    
    print()
    print("Generating comprehensive report...")
    print("-" * 100)
    generate_comprehensive_report(df, viz_dir)
    
    print()
    
    # Save final comparison to file
    print_top_20_comparison(viz_dir)
    
    print()
    print("=" * 100)
    print("Analysis complete!")
    print("=" * 100)
    print(f"\nAll outputs saved to: {viz_dir.absolute()}")
    print("\nGenerated files:")
    print("  - node_ranking_overlap.png (Which nodes each algorithm ranks highest)")
    print("  - node_ranking_overlap_report.txt (Detailed overlap analysis)")
    print("  - runtime_characteristics.png (Performance comparison)")
    print("  - comprehensive_analysis.txt (Detailed findings and recommendations)")
    print("  - top_20_nodes_comparison.txt (Top 20 nodes side-by-side comparison)")
    print("  - top_20_nodes_comparison_visualization.png (Visualization of top 20 node overlaps)")
    print()

if __name__ == "__main__":
    main()
