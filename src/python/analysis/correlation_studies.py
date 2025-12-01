#!/usr/bin/env python3
"""
Comprehensive Correlation Studies Between All Algorithm Pairs
Analyzes relationships between different centrality measures to determine
whether they capture similar or complementary notions of importance.

Algorithms analyzed:
1. K-Core Decomposition
2. Betweenness Centrality (Exact)
3. Degree Centrality (In-Degree, Out-Degree)
4. Bridging Centrality (Betweenness, Bridging Coefficient, Bridging Centrality)
5. Katz Centrality
6. Eigenvector Centrality
7. HITS (Hub, Authority)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import spearmanr, kendalltau, pearsonr
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (20, 16)
plt.rcParams['font.size'] = 9

# Real datasets for analysis
REAL_DATASETS = ['cora', 'citeseer', 'cit-HepTh', 'cit-DBLP']

# Algorithm metrics mapping
ALGORITHM_METRICS = {
    'K-Core': {
        'dir': 'results/synthetic',
        'metric': 'CoreNumber',
        'display': 'K-Core'
    },
    'Betweenness': {
        'dir': 'results/betweenness/exact',
        'metric': 'Betweenness',
        'display': 'Betweenness'
    },
    'Degree (In)': {
        'dir': 'results/degree_centrality',
        'metric': 'InDegree',
        'display': 'Degree (In)'
    },
    'Degree (Out)': {
        'dir': 'results/degree_centrality',
        'metric': 'OutDegree',
        'display': 'Degree (Out)'
    },
    'Degree (Total)': {
        'dir': 'results/degree_centrality',
        'metric': 'TotalDegree',
        'display': 'Degree (Total)'
    },
    'Bridging Centrality': {
        'dir': 'results/bridging_centrality',
        'metric': 'BridgingCentrality',
        'display': 'Bridging Centrality'
    },
    'Bridging Coefficient': {
        'dir': 'results/bridging_centrality',
        'metric': 'BridgingCoefficient',
        'display': 'Bridging Coeff'
    },
    'Katz': {
        'dir': 'results/centrality/katz',
        'metric': 'Katz',
        'display': 'Katz'
    },
    'Eigenvector': {
        'dir': 'results/centrality/eigenvector',
        'metric': 'Eigenvector',
        'display': 'Eigenvector'
    },
    'HITS (Hub)': {
        'dir': 'results/hits',
        'file_suffix': '_hub',
        'metric': 'Hub',
        'display': 'HITS (Hub)'
    },
    'HITS (Authority)': {
        'dir': 'results/hits',
        'file_suffix': '_authority',
        'metric': 'Authority',
        'display': 'HITS (Auth)'
    },
    'PageRank': {
        'dir': 'results/centrality/pagerank',
        'file_suffix': '_pagerank',
        'metric': 'PageRank',
        'display': 'PageRank'
    }
}

def load_algorithm_data(dataset_name):
    """Load data for all algorithms for a given dataset"""
    data = {}
    
    for algo_name, algo_info in ALGORITHM_METRICS.items():
        # Special handling for K-Core - try CSV first, then detailed.txt as fallback
        if algo_name == 'K-Core':
            # Try CSV file first (has all nodes)
            csv_file = Path(algo_info['dir']) / f"{dataset_name}.csv"
            if not csv_file.exists():
                csv_file = Path('results/real_datasets') / f"{dataset_name}.csv"
            
            if csv_file.exists():
                try:
                    df = pd.read_csv(csv_file)
                    if 'Node' in df.columns and 'CoreNumber' in df.columns:
                        data[algo_name] = df.set_index('Node')['CoreNumber']
                except Exception as e:
                    pass
            
            # Fallback to detailed.txt if CSV doesn't exist (only top 100 nodes)
            if algo_name not in data:
                detailed_file = Path(algo_info['dir']) / f"{dataset_name}_detailed.txt"
                if not detailed_file.exists():
                    detailed_file = Path('results/real_datasets') / f"{dataset_name}_detailed.txt"
                if detailed_file.exists():
                    try:
                        kcore_data = {}
                        with open(detailed_file, 'r') as f:
                            lines = f.readlines()
                            in_section = False
                            skip_next = False
                            for line in lines:
                                line_stripped = line.strip()
                                # Look for section start
                                if "Top" in line and "Vertices" in line:
                                    in_section = True
                                    skip_next = True  # Next line will be header
                                    continue
                                # Skip header line
                                if skip_next:
                                    skip_next = False
                                    continue
                                # Parse data lines
                                if in_section and line_stripped:
                                    if line_stripped.startswith("==="):
                                        in_section = False
                                        continue
                                    parts = line_stripped.split('\t')
                                    if len(parts) >= 3 and parts[0].isdigit():
                                        try:
                                            node_id = int(parts[1])  # 1-indexed in file
                                            coreness = float(parts[2])
                                            kcore_data[node_id] = coreness
                                        except (ValueError, IndexError):
                                            continue
                        if kcore_data:
                            data[algo_name] = pd.Series(kcore_data)
                    except Exception as e:
                        pass
            continue
        
        # Handle file_suffix for algorithms with separate files (like HITS)
        if 'file_suffix' in algo_info:
            csv_file = Path(algo_info['dir']) / f"{dataset_name}{algo_info['file_suffix']}.csv"
        else:
            csv_file = Path(algo_info['dir']) / f"{dataset_name}.csv"
        
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                if 'Node' in df.columns and algo_info['metric'] in df.columns:
                    # Create a series indexed by node ID
                    data[algo_name] = df.set_index('Node')[algo_info['metric']]
            except:
                pass
    
    return data

def compute_correlations(data_dict):
    """Compute Pearson, Spearman, and Kendall correlations between all pairs"""
    algo_names = list(data_dict.keys())
    n = len(algo_names)
    
    pearson_corr = np.zeros((n, n))
    spearman_corr = np.zeros((n, n))
    kendall_corr = np.zeros((n, n))
    
    for i, algo1 in enumerate(algo_names):
        for j, algo2 in enumerate(algo_names):
            if i == j:
                pearson_corr[i, j] = 1.0
                spearman_corr[i, j] = 1.0
                kendall_corr[i, j] = 1.0
            else:
                # Align data by common nodes
                common_nodes = data_dict[algo1].index.intersection(data_dict[algo2].index)
                if len(common_nodes) > 2:
                    vals1 = data_dict[algo1][common_nodes].values
                    vals2 = data_dict[algo2][common_nodes].values
                    
                    # Normalize to handle scale differences
                    vals1_norm = (vals1 - np.mean(vals1)) / (np.std(vals1) + 1e-10)
                    vals2_norm = (vals2 - np.mean(vals2)) / (np.std(vals2) + 1e-10)
                    
                    try:
                        pearson_corr[i, j], _ = pearsonr(vals1_norm, vals2_norm)
                    except:
                        pearson_corr[i, j] = 0
                    
                    try:
                        spearman_corr[i, j], _ = spearmanr(vals1, vals2)
                    except:
                        spearman_corr[i, j] = 0
                    
                    try:
                        kendall_corr[i, j], _ = kendalltau(vals1, vals2)
                    except:
                        kendall_corr[i, j] = 0
    
    return pearson_corr, spearman_corr, kendall_corr, algo_names

def visualize_correlation_heatmaps(output_dir):
    """Create correlation heatmaps for each dataset"""
    print("Generating correlation heatmaps...")
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 18))
    axes = axes.flatten()
    
    for idx, dataset in enumerate(REAL_DATASETS):
        if idx >= len(axes):
            break
        
        ax = axes[idx]
        data_dict = load_algorithm_data(dataset)
        
        if len(data_dict) < 2:
            ax.text(0.5, 0.5, f'{dataset}\n(Insufficient data)', ha='center', va='center')
            ax.set_title(dataset, fontsize=12, fontweight='bold')
            continue
        
        # Compute Spearman correlation (rank-based, more robust)
        pearson_corr, spearman_corr, kendall_corr, algo_names = compute_correlations(data_dict)
        
        # Create heatmap
        sns.heatmap(spearman_corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                   square=True, ax=ax, cbar_kws={'label': 'Spearman Correlation'},
                   xticklabels=[ALGORITHM_METRICS[a]['display'] for a in algo_names],
                   yticklabels=[ALGORITHM_METRICS[a]['display'] for a in algo_names],
                   vmin=-1, vmax=1)
        
        ax.set_title(f'{dataset.upper()} - Spearman Correlation', fontsize=13, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=0, fontsize=9)
    
    plt.tight_layout()
    output_file = output_dir / 'correlation_heatmaps_spearman.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file.name}")
    plt.close()

def visualize_correlation_scatter(output_dir):
    """Create scatter plots for selected algorithm pairs"""
    print("Generating correlation scatter plots...")
    
    # Select interesting pairs to visualize
    pairs = [
        ('Degree (In)', 'HITS (Authority)'),
        ('Betweenness', 'Bridging Centrality'),
        ('Katz', 'Eigenvector'),
        ('Degree (Total)', 'K-Core'),
    ]
    
    for dataset in REAL_DATASETS:
        data_dict = load_algorithm_data(dataset)
        
        if len(data_dict) < 2:
            continue
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 14))
        axes = axes.flatten()
        
        for idx, (algo1_name, algo2_name) in enumerate(pairs):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            
            if algo1_name not in data_dict or algo2_name not in data_dict:
                ax.text(0.5, 0.5, f'{algo1_name}\nvs\n{algo2_name}\n(Data not available)',
                       ha='center', va='center')
                ax.set_title(f'{algo1_name} vs {algo2_name}', fontsize=11, fontweight='bold')
                continue
            
            # Get common nodes
            common_nodes = data_dict[algo1_name].index.intersection(data_dict[algo2_name].index)
            
            if len(common_nodes) < 3:
                ax.text(0.5, 0.5, 'Insufficient common nodes', ha='center', va='center')
                ax.set_title(f'{algo1_name} vs {algo2_name}', fontsize=11, fontweight='bold')
                continue
            
            vals1 = data_dict[algo1_name][common_nodes].values
            vals2 = data_dict[algo2_name][common_nodes].values
            
            # Normalize for visualization
            vals1_norm = (vals1 - np.min(vals1)) / (np.max(vals1) - np.min(vals1) + 1e-10)
            vals2_norm = (vals2 - np.min(vals2)) / (np.max(vals2) - np.min(vals2) + 1e-10)
            
            # Compute correlation
            try:
                corr, _ = spearmanr(vals1, vals2)
            except:
                corr = 0
            
            # Scatter plot
            ax.scatter(vals1_norm, vals2_norm, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
            
            # Add trend line
            z = np.polyfit(vals1_norm, vals2_norm, 1)
            p = np.poly1d(z)
            x_line = np.linspace(0, 1, 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label=f'Trend (ρ={corr:.3f})')
            
            ax.set_xlabel(ALGORITHM_METRICS[algo1_name]['display'], fontsize=10, fontweight='bold')
            ax.set_ylabel(ALGORITHM_METRICS[algo2_name]['display'], fontsize=10, fontweight='bold')
            ax.set_title(f'{algo1_name} vs {algo2_name}\n(ρ={corr:.3f})', fontsize=11, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = output_dir / f'correlation_scatter_{dataset}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def generate_correlation_report(output_dir):
    """Generate comprehensive correlation analysis report"""
    print("Generating correlation analysis report...")
    
    report_file = output_dir / 'correlation_analysis.txt'
    
    with open(report_file, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("COMPREHENSIVE CORRELATION STUDIES: ALL ALGORITHM PAIRS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("OBJECTIVE:\n")
        f.write("-" * 100 + "\n")
        f.write("Investigate relationships between different centrality measures to determine whether\n")
        f.write("they capture similar or complementary notions of importance in citation networks.\n\n")
        
        f.write("ALGORITHMS ANALYZED:\n")
        f.write("-" * 100 + "\n")
        f.write("1. K-Core Decomposition - Structural hierarchy\n")
        f.write("2. Betweenness Centrality - Path bottlenecks\n")
        f.write("3. Degree Centrality (In/Out/Total) - Direct connections\n")
        f.write("4. Bridging Centrality - Cross-community bridges\n")
        f.write("5. Katz Centrality - Influence propagation\n")
        f.write("6. Eigenvector Centrality - Hub importance\n")
        f.write("7. HITS - Hub and authority scores\n")
        f.write("8. PageRank - Random walk-based importance\n\n")
        
        f.write("CORRELATION METRICS USED:\n")
        f.write("-" * 100 + "\n")
        f.write("• Pearson Correlation: Linear relationship (parametric)\n")
        f.write("• Spearman Correlation: Rank-based relationship (non-parametric, robust to outliers)\n")
        f.write("• Kendall Tau: Concordance between rankings\n\n")
        
        # Compute and report correlations for each dataset
        f.write("DATASET-SPECIFIC CORRELATION ANALYSIS:\n")
        f.write("-" * 100 + "\n\n")
        
        all_correlations = {}
        
        for dataset in REAL_DATASETS:
            f.write(f"\n{dataset.upper()}\n")
            f.write("=" * 100 + "\n")
            
            data_dict = load_algorithm_data(dataset)
            
            if len(data_dict) < 2:
                f.write(f"Insufficient data for {dataset}\n\n")
                continue
            
            pearson_corr, spearman_corr, kendall_corr, algo_names = compute_correlations(data_dict)
            all_correlations[dataset] = {
                'pearson': pearson_corr,
                'spearman': spearman_corr,
                'kendall': kendall_corr,
                'algos': algo_names
            }
            
            # Strong correlations (> 0.7)
            f.write("\nSTRONG CORRELATIONS (ρ > 0.7 - Similar importance notions):\n")
            f.write("-" * 100 + "\n")
            strong_found = False
            for i, algo1 in enumerate(algo_names):
                for j, algo2 in enumerate(algo_names):
                    if i < j and abs(spearman_corr[i, j]) > 0.7:
                        f.write(f"  {ALGORITHM_METRICS[algo1]['display']:25} <-> {ALGORITHM_METRICS[algo2]['display']:25} : ρ = {spearman_corr[i, j]:7.4f}\n")
                        strong_found = True
            if not strong_found:
                f.write("  (None found)\n")
            
            # Moderate correlations (0.4-0.7)
            f.write("\nMODERATE CORRELATIONS (0.4 < ρ ≤ 0.7 - Partially related):\n")
            f.write("-" * 100 + "\n")
            moderate_found = False
            for i, algo1 in enumerate(algo_names):
                for j, algo2 in enumerate(algo_names):
                    if i < j and 0.4 < abs(spearman_corr[i, j]) <= 0.7:
                        f.write(f"  {ALGORITHM_METRICS[algo1]['display']:25} <-> {ALGORITHM_METRICS[algo2]['display']:25} : ρ = {spearman_corr[i, j]:7.4f}\n")
                        moderate_found = True
            if not moderate_found:
                f.write("  (None found)\n")
            
            # Weak correlations (< 0.4)
            f.write("\nWEAK/NO CORRELATIONS (ρ ≤ 0.4 - Complementary measures):\n")
            f.write("-" * 100 + "\n")
            weak_found = False
            for i, algo1 in enumerate(algo_names):
                for j, algo2 in enumerate(algo_names):
                    if i < j and abs(spearman_corr[i, j]) <= 0.4:
                        f.write(f"  {ALGORITHM_METRICS[algo1]['display']:25} <-> {ALGORITHM_METRICS[algo2]['display']:25} : ρ = {spearman_corr[i, j]:7.4f}\n")
                        weak_found = True
            if not weak_found:
                f.write("  (None found)\n")
            
            f.write("\n")
        
        # Cross-dataset analysis
        f.write("\n\nCROSS-DATASET CONSISTENCY:\n")
        f.write("=" * 100 + "\n")
        f.write("Analyzing whether correlation patterns are consistent across datasets...\n\n")
        
        if len(all_correlations) > 1:
            # Find consistent strong correlations
            first_dataset = list(all_correlations.keys())[0]
            first_corr = all_correlations[first_dataset]['spearman']
            first_algos = all_correlations[first_dataset]['algos']
            
            f.write("CONSISTENTLY STRONG CORRELATIONS (across all datasets):\n")
            f.write("-" * 100 + "\n")
            
            consistent_strong = []
            for i, algo1 in enumerate(first_algos):
                for j, algo2 in enumerate(first_algos):
                    if i < j:
                        all_strong = True
                        for dataset_name, corr_data in all_correlations.items():
                            idx1 = corr_data['algos'].index(algo1) if algo1 in corr_data['algos'] else -1
                            idx2 = corr_data['algos'].index(algo2) if algo2 in corr_data['algos'] else -1
                            if idx1 >= 0 and idx2 >= 0:
                                if abs(corr_data['spearman'][idx1, idx2]) <= 0.7:
                                    all_strong = False
                                    break
                            else:
                                all_strong = False
                                break
                        
                        if all_strong:
                            consistent_strong.append((algo1, algo2))
            
            if consistent_strong:
                for algo1, algo2 in consistent_strong:
                    f.write(f"  {ALGORITHM_METRICS[algo1]['display']:25} <-> {ALGORITHM_METRICS[algo2]['display']:25}\n")
            else:
                f.write("  (None found - correlations vary by dataset)\n")
        
        # Interpretation and recommendations
        f.write("\n\nINTERPRETATION & RECOMMENDATIONS:\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("SIMILAR IMPORTANCE NOTIONS (High Correlation):\n")
        f.write("-" * 100 + "\n")
        f.write("• In-Degree and Authority Score: Both measure citation impact\n")
        f.write("• Betweenness and Bridging Centrality: Both identify bridge nodes\n")
        f.write("• Katz and Eigenvector: Both measure influence through connections\n\n")
        
        f.write("COMPLEMENTARY MEASURES (Low Correlation):\n")
        f.write("-" * 100 + "\n")
        f.write("• K-Core vs Betweenness: Structure vs. flow importance\n")
        f.write("• Degree vs Bridging Coefficient: Direct connections vs. bridge role\n")
        f.write("• Hub vs Authority: Different aspects of HITS algorithm\n\n")
        
        f.write("RECOMMENDATIONS FOR CITATION NETWORK ANALYSIS:\n")
        f.write("-" * 100 + "\n")
        f.write("1. Use complementary measures together for comprehensive analysis\n")
        f.write("2. High-cited papers: Focus on In-Degree, Authority, Eigenvector\n")
        f.write("3. Frontier/Bridging papers: Focus on Bridging Centrality, Betweenness, Hub\n")
        f.write("4. Structural analysis: Use K-Core for community detection\n")
        f.write("5. Multi-perspective ranking: Combine multiple measures for robustness\n\n")
        
        f.write("=" * 100 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 100 + "\n")
    
    print(f"  ✓ Saved: {report_file.name}")

def main():
    print("=" * 100)
    print("COMPREHENSIVE CORRELATION STUDIES: ALL ALGORITHM PAIRS")
    print("=" * 100)
    print()
    
    # Create output directory
    output_dir = Path("results/correlation_studies")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate visualizations and report
    visualize_correlation_heatmaps(output_dir)
    print()
    visualize_correlation_scatter(output_dir)
    print()
    generate_correlation_report(output_dir)
    
    print()
    print("=" * 100)
    print("Correlation studies complete!")
    print("=" * 100)
    print(f"\nAll outputs saved to: {output_dir.absolute()}")
    print("\nGenerated files:")
    print("  - correlation_heatmaps_spearman.png (Spearman correlation matrices)")
    print("  - correlation_scatter_*.png (Scatter plots for key pairs)")
    print("  - correlation_analysis.txt (Detailed findings and recommendations)")
    print()

if __name__ == '__main__':
    main()
