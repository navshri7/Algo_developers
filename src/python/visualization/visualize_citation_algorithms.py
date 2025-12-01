#!/usr/bin/env python3
"""
Visualization for Citation-Specific Algorithms
Visualizes node rankings and metrics for:
- Degree Centrality (In-Degree, Out-Degree, Total)
- Bridging Centrality (Bridging Score, Betweenness, Bridging Coefficient)
- HITS (Hub Score, Authority Score)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

# Algorithm metadata
ALGORITHMS = {
    'degree': {
        'name': 'Degree Centrality',
        'color': 'Blues',
        'result_dir': 'results/degree_centrality',
        'metrics': ['InDegree', 'OutDegree', 'TotalDegree'],
        'metric_labels': ['In-Degree (Citations Received)', 'Out-Degree (Citations Made)', 'Total Degree']
    },
    'bridging': {
        'name': 'Bridging Centrality',
        'color': 'Greens',
        'result_dir': 'results/bridging_centrality',
        'metrics': ['Betweenness', 'BridgingCoefficient', 'BridgingCentrality'],
        'metric_labels': ['Betweenness', 'Bridging Coefficient', 'Bridging Centrality']
    },
    'hits': {
        'name': 'HITS',
        'color': 'Purples',
        'result_dir': 'results/hits',
        'metrics': ['Hub', 'Authority'],
        'metric_labels': ['Hub Score', 'Authority Score']
    }
}

def load_csv_results(filepath):
    """Load results from CSV file"""
    try:
        return pd.read_csv(filepath)
    except:
        return None

def visualize_top_nodes_by_dataset(output_dir):
    """Create visualizations of top nodes for each algorithm on real datasets"""
    print("Generating top nodes visualizations...")
    
    real_datasets = ['cora', 'citeseer', 'cit-HepTh', 'cit-DBLP']
    
    # Create figure for each algorithm
    for algo_key, algo_info in ALGORITHMS.items():
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        axes = axes.flatten()
        
        for idx, dataset in enumerate(real_datasets):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            csv_file = Path(algo_info['result_dir']) / f"{dataset}.csv"
            
            if not csv_file.exists():
                ax.text(0.5, 0.5, f'{dataset}\n(No data)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            df = load_csv_results(str(csv_file))
            if df is None or df.empty:
                ax.text(0.5, 0.5, f'{dataset}\n(Empty data)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            # Get top 10 by first metric
            metric = algo_info['metrics'][0]
            if metric not in df.columns:
                ax.text(0.5, 0.5, f'{dataset}\n(Metric not found)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            top_10 = df.nlargest(10, metric)
            
            # Create bar plot
            colors = sns.color_palette(algo_info['color'], len(top_10))
            bars = ax.barh(range(len(top_10)), top_10[metric].values, color=colors, edgecolor='black', linewidth=0.8)
            
            # Customize
            ax.set_yticks(range(len(top_10)))
            ax.set_yticklabels([f"N{int(nid)}" for nid in top_10['Node'].values], fontsize=9)
            ax.set_xlabel(algo_info['metric_labels'][0], fontsize=11, fontweight='bold')
            ax.set_title(f'{dataset} - Top 10 by {algo_info["metric_labels"][0]}', fontsize=12, fontweight='bold')
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, top_10[metric].values)):
                ax.text(val, i, f' {val:.2e}', va='center', fontsize=8)
        
        plt.tight_layout()
        output_file = output_dir / f'{algo_key}_top_nodes.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def visualize_metric_distributions(output_dir):
    """Visualize distributions of metrics across all nodes"""
    print("Generating metric distribution visualizations...")
    
    real_datasets = ['cora', 'citeseer', 'cit-HepTh', 'cit-DBLP']
    
    for algo_key, algo_info in ALGORITHMS.items():
        num_metrics = len(algo_info['metrics'])
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        axes = axes.flatten()
        
        for idx, dataset in enumerate(real_datasets):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            csv_file = Path(algo_info['result_dir']) / f"{dataset}.csv"
            
            if not csv_file.exists():
                ax.text(0.5, 0.5, f'{dataset}\n(No data)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            df = load_csv_results(str(csv_file))
            if df is None or df.empty:
                ax.text(0.5, 0.5, f'{dataset}\n(Empty data)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            # Create box plots for all metrics
            data_to_plot = []
            labels = []
            for metric, label in zip(algo_info['metrics'], algo_info['metric_labels']):
                if metric in df.columns:
                    data_to_plot.append(df[metric].values)
                    labels.append(label.replace(' ', '\n'))
            
            if data_to_plot:
                bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
                
                # Color the boxes
                colors = sns.color_palette(algo_info['color'], len(data_to_plot))
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                
                ax.set_title(f'{dataset} - Metric Distributions', fontsize=12, fontweight='bold')
                ax.set_ylabel('Value', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=15, ha='right')
        
        plt.tight_layout()
        output_file = output_dir / f'{algo_key}_distributions.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def visualize_metric_correlations(output_dir):
    """Visualize correlations between metrics within each algorithm"""
    print("Generating metric correlation visualizations...")
    
    real_datasets = ['cora', 'citeseer', 'cit-HepTh', 'cit-DBLP']
    
    for algo_key, algo_info in ALGORITHMS.items():
        if len(algo_info['metrics']) < 2:
            continue
        
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        axes = axes.flatten()
        
        for idx, dataset in enumerate(real_datasets):
            if idx >= len(axes):
                break
            
            ax = axes[idx]
            csv_file = Path(algo_info['result_dir']) / f"{dataset}.csv"
            
            if not csv_file.exists():
                ax.text(0.5, 0.5, f'{dataset}\n(No data)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            df = load_csv_results(str(csv_file))
            if df is None or df.empty:
                ax.text(0.5, 0.5, f'{dataset}\n(Empty data)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            # Select only numeric columns that are metrics
            metric_cols = [m for m in algo_info['metrics'] if m in df.columns]
            if len(metric_cols) < 2:
                ax.text(0.5, 0.5, f'{dataset}\n(Insufficient metrics)', ha='center', va='center')
                ax.set_title(dataset, fontsize=12, fontweight='bold')
                continue
            
            # Create correlation heatmap
            corr_matrix = df[metric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap=algo_info['color'],
                       square=True, ax=ax, cbar_kws={'label': 'Correlation'},
                       xticklabels=algo_info['metric_labels'][:len(metric_cols)],
                       yticklabels=algo_info['metric_labels'][:len(metric_cols)])
            ax.set_title(f'{dataset} - Metric Correlations', fontsize=12, fontweight='bold')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            plt.setp(ax.yaxis.get_majorticklabels(), rotation=0)
        
        plt.tight_layout()
        output_file = output_dir / f'{algo_key}_correlations.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file.name}")
        plt.close()

def visualize_algorithm_comparison(output_dir):
    """Compare metrics across algorithms on the same datasets"""
    print("Generating cross-algorithm comparison visualizations...")
    
    real_datasets = ['cora', 'citeseer', 'cit-HepTh', 'cit-DBLP']
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    axes = axes.flatten()
    
    for idx, dataset in enumerate(real_datasets):
        if idx >= len(axes):
            break
        
        ax = axes[idx]
        
        # Collect top 10 nodes from each algorithm
        top_nodes_by_algo = {}
        
        for algo_key, algo_info in ALGORITHMS.items():
            csv_file = Path(algo_info['result_dir']) / f"{dataset}.csv"
            if csv_file.exists():
                df = load_csv_results(str(csv_file))
                if df is not None and not df.empty:
                    metric = algo_info['metrics'][0]
                    if metric in df.columns:
                        top_10 = set(df.nlargest(10, metric)['Node'].values)
                        top_nodes_by_algo[algo_info['name']] = top_10
        
        if not top_nodes_by_algo:
            ax.text(0.5, 0.5, f'{dataset}\n(No data)', ha='center', va='center')
            ax.set_title(dataset, fontsize=12, fontweight='bold')
            continue
        
        # Create overlap matrix
        algo_names = list(top_nodes_by_algo.keys())
        overlap_matrix = np.zeros((len(algo_names), len(algo_names)))
        
        for i, algo1 in enumerate(algo_names):
            for j, algo2 in enumerate(algo_names):
                overlap = len(top_nodes_by_algo[algo1] & top_nodes_by_algo[algo2])
                overlap_matrix[i, j] = overlap
        
        # Plot heatmap
        sns.heatmap(overlap_matrix, annot=True, fmt='.0f', cmap='RdYlGn',
                   xticklabels=algo_names, yticklabels=algo_names, ax=ax,
                   cbar_kws={'label': 'Overlap (Top 10)'}, vmin=0, vmax=10)
        ax.set_title(f'{dataset} - Algorithm Overlap (Top 10 Nodes)', fontsize=12, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    output_file = output_dir / 'citation_algorithms_overlap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file.name}")
    plt.close()

def main():
    print("=" * 80)
    print("Citation Algorithm Visualizations")
    print("Degree Centrality, Bridging Centrality, HITS")
    print("=" * 80)
    print()
    
    # Create output directory
    viz_dir = Path("results/node_visualizations")
    viz_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate visualizations
    visualize_top_nodes_by_dataset(viz_dir)
    print()
    visualize_metric_distributions(viz_dir)
    print()
    visualize_metric_correlations(viz_dir)
    print()
    visualize_algorithm_comparison(viz_dir)
    
    print()
    print("=" * 80)
    print("Visualization complete!")
    print("=" * 80)
    print(f"\nAll outputs saved to: {viz_dir.absolute()}")
    print()

if __name__ == '__main__':
    main()
