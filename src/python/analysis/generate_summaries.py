#!/usr/bin/env python3
"""
Generate summary CSV files from detailed results for all algorithms
This script reads detailed .txt files and creates summary.csv files
"""

import pandas as pd
import os
from pathlib import Path
import re

def extract_stats_from_detailed(filepath):
    """Extract statistics from detailed results file"""
    stats = {
        'Nodes': 0,
        'Edges': 0,
        'Runtime_sec': 0.0,
        'Memory_MB': 0.0,
    }
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
            # Extract Nodes
            match = re.search(r'Nodes:\s*(\d+)', content)
            if match:
                stats['Nodes'] = int(match.group(1))
            
            # Extract Edges
            match = re.search(r'Edges:\s*(\d+)', content)
            if match:
                stats['Edges'] = int(match.group(1))
            
            # Extract Runtime
            match = re.search(r'Runtime:\s*([\d.]+)\s*seconds', content)
            if match:
                stats['Runtime_sec'] = float(match.group(1))
            
            # Extract Memory
            match = re.search(r'Peak Memory:\s*([\d.]+)\s*MB', content)
            if match:
                stats['Memory_MB'] = float(match.group(1))
    except:
        pass
    
    return stats

def generate_summary_for_algorithm(result_dir, algorithm_name, suffix=None):
    """Generate summary CSV for an algorithm from its detailed results"""
    
    result_path = Path(result_dir)
    if not result_path.exists():
        print(f"  ⚠ Directory not found: {result_dir}")
        return
    
    # Find all detailed files
    if suffix:
        # For HITS hub/authority, look for files with specific suffix
        detailed_files = list(result_path.glob(f'*{suffix}_detailed.txt'))
    else:
        detailed_files = list(result_path.glob('*_detailed.txt'))
    
    if not detailed_files:
        print(f"  ⚠ No detailed files found in {result_dir}")
        return
    
    # Extract stats from each file
    summaries = []
    for detailed_file in detailed_files:
        dataset_name = detailed_file.stem.replace(f'{suffix}_detailed', '').replace('_detailed', '')
        stats = extract_stats_from_detailed(str(detailed_file))
        stats['Dataset'] = dataset_name
        stats['Density'] = stats['Edges'] / (stats['Nodes'] * (stats['Nodes'] - 1)) if stats['Nodes'] > 1 else 0
        stats['AvgDegree'] = 2 * stats['Edges'] / stats['Nodes'] if stats['Nodes'] > 0 else 0
        summaries.append(stats)
    
    if summaries:
        df = pd.DataFrame(summaries)
        if suffix:
            summary_csv = result_path / f'summary{suffix}.csv'
        else:
            summary_csv = result_path / 'summary.csv'
        df.to_csv(summary_csv, index=False)
        print(f"  ✓ Generated: {summary_csv} ({len(df)} entries)")
    else:
        print(f"  ⚠ No data extracted for {algorithm_name}")

def main():
    print("=" * 80)
    print("Generating Summary CSV Files from Detailed Results")
    print("=" * 80)
    print()
    
    algorithms = [
        ('Bridging Centrality', 'results/bridging_centrality', None),
        ('Degree Centrality', 'results/degree_centrality', None),
        ('HITS (Hub)', 'results/hits', '_hub'),
        ('HITS (Authority)', 'results/hits', '_authority'),
    ]
    
    for algo_name, result_dir, suffix in algorithms:
        print(f"Processing {algo_name}...")
        generate_summary_for_algorithm(result_dir, algo_name, suffix)
    
    print()
    print("=" * 80)
    print("Summary generation complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
