#!/usr/bin/env python3
"""
Verification Testing for All Algorithms
Tests correctness of all algorithms on verification graphs with known expected results.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

# Add root directory to path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Verification graphs and their expected properties
VERIFICATION_GRAPHS = {
    'verify_complete_7': {
        'name': 'Complete Graph K7',
        'nodes': 7,
        'edges': 21,
        'expected': {
            'kcore': {'all_equal': True, 'value': 6},
            'degree': {'all_equal': True, 'value': 6},
            'betweenness': {'all_equal': True, 'value': 0},
            'bridging': {'all_equal': True, 'value': 0},
            'katz': {'all_equal': True},
            'eigenvector': {'all_equal': True},
            'hits_hub': {'all_equal': True},
            'hits_auth': {'all_equal': True},
            'pagerank': {'all_equal': True},
        }
    },
    'verify_cycle_6': {
        'name': 'Cycle Graph C6',
        'nodes': 6,
        'edges': 6,
        'expected': {
            'kcore': {'all_equal': True, 'value': 2},
            'degree': {'all_equal': True, 'value': 2},
            'betweenness': {'all_equal': True, 'value_range': (0, 10)},
            'katz': {'all_equal': True},
            'eigenvector': {'all_equal': True},
            'hits_hub': {'all_equal': True},
            'hits_auth': {'all_equal': True},
            'pagerank': {'all_equal': True},
        }
    },
    'verify_star_9': {
        'name': 'Star Graph',
        'nodes': 9,
        'edges': 8,
        'expected': {
            'kcore': {'center_highest': False, 'all_equal': True, 'value': 1},
            'degree': {'center_highest': True, 'center_value': 8, 'leaves_value': 1},
            'betweenness': {'center_highest': True, 'center_value_range': (20, 30), 'leaves_value': 0},
            'bridging': {'center_highest': True},
            'katz': {'center_highest': True},
            'eigenvector': {'center_highest': True},
            'hits_hub': {'center_highest': True},
            'hits_auth': {'center_lowest': True, 'leaves_higher': True},
            'pagerank': {'center_highest': True},
        }
    },
    'verify_path_5': {
        'name': 'Path Graph P5',
        'nodes': 5,
        'edges': 4,
        'expected': {
            'kcore': {'all_equal': True, 'value': 1},
            'degree': {'ends_lowest': True, 'middle_higher': True},
            'betweenness': {'middle_highest': True, 'ends_zero': True},
            'bridging': {'middle_highest': True},
            'katz': {'middle_higher': True},
            'eigenvector': {'middle_higher': True},
            'hits_hub': {'middle_higher': True},
            'hits_auth': {'middle_higher': True},
            'pagerank': {'middle_higher': True},
        }
    },
    'verify_known_structure': {
        'name': 'Known K-Core Structure',
        'nodes': 20,
        'edges': 35,
        'expected': {
            'kcore': {'core5_nodes': list(range(1, 7)), 'core3_nodes': list(range(7, 11)), 
                     'core2_nodes': list(range(11, 16)), 'core1_nodes': list(range(16, 21)),
                     'core5_value': 5, 'core3_value': 3, 'core2_value': 2, 'core1_value': 1},
            'degree': {'core5_highest': True, 'core1_lowest': True},
            'betweenness': {'connectors_highest': True},
            'katz': {'core5_highest': True, 'core1_lowest': True},
            'eigenvector': {'core5_highest': True, 'core1_lowest': True},
        }
    }
}

# Algorithm file paths (relative to ROOT_DIR)
ALGORITHM_PATHS = {
    'kcore': {
        'dirs': ['results/synthetic', 'results/real_datasets'],
        'file_pattern': '{graph}_detailed.txt',
        'csv_pattern': '{graph}.csv'
    },
    'degree': {
        'dirs': ['results/degree_centrality'],
        'file_pattern': '{graph}_detailed.txt'
    },
    'betweenness': {
        'dirs': ['results/betweenness/exact'],
        'file_pattern': '{graph}_detailed.txt'
    },
    'bridging': {
        'dirs': ['results/bridging_centrality'],
        'file_pattern': '{graph}_detailed.txt'
    },
    'katz': {
        'dirs': ['results/centrality/katz'],
        'file_pattern': '{graph}_detailed.txt'
    },
    'eigenvector': {
        'dirs': ['results/centrality/eigenvector'],
        'file_pattern': '{graph}_detailed.txt'
    },
    'hits_hub': {
        'dirs': ['results/hits'],
        'file_pattern': '{graph}_hub_detailed.txt'
    },
    'hits_auth': {
        'dirs': ['results/hits'],
        'file_pattern': '{graph}_authority_detailed.txt'
    },
    'pagerank': {
        'dirs': ['results/centrality/pagerank'],
        'file_pattern': '{graph}_pagerank_detailed.txt'
    }
}

def parse_kcore_results(filepath):
    """Parse K-Core results from detailed file or CSV"""
    results = {}
    
    # Try CSV first (has all nodes)
    csv_file = filepath.parent / f"{filepath.stem.replace('_detailed', '')}.csv"
    if csv_file.exists():
        try:
            with open(csv_file, 'r') as f:
                next(f)  # Skip header
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        node_id = int(parts[0])
                        coreness = int(parts[1])
                        results[node_id] = coreness
            return results
        except:
            pass
    
    # Fallback to detailed file
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            in_section = False
            skip_next = False
            
            for line in lines:
                line_stripped = line.strip()
                if "Top" in line and "Vertices" in line:
                    in_section = True
                    skip_next = True
                    continue
                if skip_next:
                    skip_next = False
                    continue
                if in_section and line_stripped:
                    if line_stripped.startswith("==="):
                        break
                    parts = line_stripped.split('\t')
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            node_id = int(parts[1])
                            coreness = int(parts[2])
                            results[node_id] = coreness
                        except:
                            continue
    except:
        pass
    
    return results

def parse_detailed_results(filepath, algo_type):
    """Parse detailed results file"""
    results = {}
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            in_section = False
            skip_next = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Detect section start
                if not in_section and "Top" in line:
                    if "Vertices" in line:
                        in_section = True
                        skip_next = True
                        continue
                    elif any(kw in line for kw in ["Total Degree", "Bridging Centrality", "Hub Score", 
                                                   "Authority Score", "Rank", "Betweenness", "Katz", 
                                                   "Eigenvector", "PageRank"]):
                        in_section = True
                        skip_next = False
                        continue
                
                if in_section and line_stripped.startswith("Top"):
                    break
                
                if skip_next:
                    skip_next = False
                    continue
                
                if in_section and line_stripped:
                    if line_stripped.startswith("==="):
                        in_section = False
                        continue
                    if not line_stripped or ("Rank" in line_stripped and not line_stripped[0].isdigit()):
                        continue
                    
                    # Try tab-separated format
                    parts = line_stripped.split('\t')
                    if len(parts) >= 3 and parts[0].isdigit():
                        try:
                            node_id = int(parts[1])
                            value = float(parts[2])
                            results[node_id] = value
                        except:
                            continue
                    else:
                        # Try "Node X: Y" format
                        match = re.search(r'(\d+)\.\s*Node\s+(\d+):\s*([\d.]+)', line)
                        if match:
                            try:
                                node_id = int(match.group(2))
                                value = float(match.group(3))
                                results[node_id] = value
                            except:
                                continue
    except Exception as e:
        pass
    
    return results

def load_algorithm_results(graph_name, algo_type):
    """Load results for a specific algorithm and graph"""
    algo_info = ALGORITHM_PATHS.get(algo_type)
    if not algo_info:
        return {}
    
    for dir_path in algo_info['dirs']:
        filepath = ROOT_DIR / dir_path / algo_info['file_pattern'].format(graph=graph_name)
        if filepath.exists():
            if algo_type == 'kcore':
                return parse_kcore_results(filepath)
            else:
                return parse_detailed_results(filepath, algo_type)
    
    return {}

def check_all_equal(values, tolerance=1e-6):
    """Check if all values are equal within tolerance"""
    if not values:
        return False
    values_list = list(values.values())
    return all(abs(v - values_list[0]) < tolerance for v in values_list)

def check_center_highest(values, center_node=1):
    """Check if center node has highest value"""
    if center_node not in values:
        return False
    center_value = values[center_node]
    return all(v <= center_value for node, v in values.items() if node != center_node)

def check_center_lowest(values, center_node=1):
    """Check if center node has lowest value"""
    if center_node not in values:
        return False
    center_value = values[center_node]
    return all(v >= center_value for node, v in values.items() if node != center_node)

def verify_graph(graph_name, graph_info):
    """Verify results for a single graph"""
    results = {}
    issues = []
    
    print(f"\n{'='*80}")
    print(f"Testing: {graph_info['name']} ({graph_name})")
    print(f"{'='*80}")
    
    # Load results for each algorithm
    for algo_type in ['kcore', 'degree', 'betweenness', 'bridging', 'katz', 
                      'eigenvector', 'hits_hub', 'hits_auth', 'pagerank']:
        algo_results = load_algorithm_results(graph_name, algo_type)
        results[algo_type] = algo_results
        
        if not algo_results:
            issues.append(f"{algo_type.upper()}: No results found")
            continue
        
        expected = graph_info['expected'].get(algo_type, {})
        if not expected:
            continue
        
        # Perform checks based on expected behavior
        checks_passed = []
        checks_failed = []
        
        # Check all_equal
        if expected.get('all_equal'):
            if check_all_equal(algo_results):
                checks_passed.append("All nodes have equal values")
            else:
                values_list = list(algo_results.values())
                unique_values = len(set(values_list))
                checks_failed.append(f"Expected all equal, but found {unique_values} unique values: {sorted(set(values_list))[:5]}")
        
        # Check specific value
        if 'value' in expected:
            expected_value = expected['value']
            if all(abs(v - expected_value) < 0.1 for v in algo_results.values()):
                checks_passed.append(f"All values match expected: {expected_value}")
            else:
                actual_values = sorted(set(algo_results.values()))
                checks_failed.append(f"Expected value {expected_value}, but found: {actual_values[:5]}")
        
        # Check center highest
        if expected.get('center_highest'):
            center_node = 1  # Default center for star graph
            if check_center_highest(algo_results, center_node):
                center_val = algo_results.get(center_node, 0)
                checks_passed.append(f"Center node {center_node} has highest value: {center_val:.4f}")
            else:
                center_val = algo_results.get(center_node, 0)
                max_val = max(algo_results.values())
                checks_failed.append(f"Center node {center_node} value {center_val:.4f} < max {max_val:.4f}")
        
        # Check center lowest
        if expected.get('center_lowest'):
            center_node = 1
            if check_center_lowest(algo_results, center_node):
                center_val = algo_results.get(center_node, 0)
                checks_passed.append(f"Center node {center_node} has lowest value: {center_val:.4f}")
            else:
                center_val = algo_results.get(center_node, 0)
                min_val = min(algo_results.values())
                checks_failed.append(f"Center node {center_node} value {center_val:.4f} > min {min_val:.4f}")
        
        # Check K-Core structure
        if algo_type == 'kcore' and 'core5_nodes' in expected:
            core5_nodes = expected['core5_nodes']
            core3_nodes = expected['core3_nodes']
            core2_nodes = expected['core2_nodes']
            core1_nodes = expected['core1_nodes']
            
            core5_value = expected['core5_value']
            core3_value = expected['core3_value']
            core2_value = expected['core2_value']
            core1_value = expected['core1_value']
            
            # Check each core
            core5_correct = all(algo_results.get(n, 0) == core5_value for n in core5_nodes)
            core3_correct = all(algo_results.get(n, 0) == core3_value for n in core3_nodes)
            core2_correct = all(algo_results.get(n, 0) == core2_value for n in core2_nodes)
            core1_correct = all(algo_results.get(n, 0) == core1_value for n in core1_nodes)
            
            if core5_correct and core3_correct and core2_correct and core1_correct:
                checks_passed.append(f"K-Core structure correct: 5-core={core5_value}, 3-core={core3_value}, 2-core={core2_value}, 1-core={core1_value}")
            else:
                if not core5_correct:
                    actual = [algo_results.get(n, 0) for n in core5_nodes[:3]]
                    checks_failed.append(f"5-core nodes should be {core5_value}, found: {actual}")
                if not core3_correct:
                    actual = [algo_results.get(n, 0) for n in core3_nodes[:3]]
                    checks_failed.append(f"3-core nodes should be {core3_value}, found: {actual}")
                if not core2_correct:
                    actual = [algo_results.get(n, 0) for n in core2_nodes[:3]]
                    checks_failed.append(f"2-core nodes should be {core2_value}, found: {actual}")
                if not core1_correct:
                    actual = [algo_results.get(n, 0) for n in core1_nodes[:3]]
                    checks_failed.append(f"1-core nodes should be {core1_value}, found: {actual}")
        
        # Print results
        print(f"\n{algo_type.upper()}:")
        print(f"  Nodes with data: {len(algo_results)}/{graph_info['nodes']}")
        if algo_results:
            values_list = list(algo_results.values())
            print(f"  Value range: [{min(values_list):.4f}, {max(values_list):.4f}]")
            print(f"  Unique values: {len(set(values_list))}")
        
        if checks_passed:
            print(f"  ✓ PASSED: {len(checks_passed)} checks")
            for check in checks_passed:
                print(f"    - {check}")
        
        if checks_failed:
            print(f"  ✗ FAILED: {len(checks_failed)} checks")
            for check in checks_failed:
                print(f"    - {check}")
            issues.append(f"{algo_type.upper()}: {len(checks_failed)} checks failed")
        elif not checks_passed and not checks_failed:
            print(f"  ⚠ No specific checks defined")
    
    return results, issues

def generate_report():
    """Generate comprehensive verification report"""
    print("="*80)
    print("VERIFICATION TESTING REPORT: ALL ALGORITHMS")
    print("="*80)
    print("\nThis report verifies correctness of all algorithms on graphs with known expected results.")
    print("Each graph tests different aspects of algorithm behavior.\n")
    
    all_results = {}
    all_issues = []
    
    # Test each verification graph
    for graph_name, graph_info in VERIFICATION_GRAPHS.items():
        results, issues = verify_graph(graph_name, graph_info)
        all_results[graph_name] = results
        all_issues.extend([f"{graph_name}: {issue}" for issue in issues])
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_tests = sum(len(VERIFICATION_GRAPHS[g]['expected']) for g in VERIFICATION_GRAPHS)
    total_issues = len(all_issues)
    
    print(f"\nTotal verification graphs: {len(VERIFICATION_GRAPHS)}")
    print(f"Total algorithm tests: {total_tests}")
    print(f"Total issues found: {total_issues}")
    
    if all_issues:
        print(f"\nISSUES FOUND:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("\n✓ ALL TESTS PASSED!")
    
    # Write report to file
    report_file = ROOT_DIR / "results" / "verification_testing_report.txt"
    report_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("VERIFICATION TESTING REPORT: ALL ALGORITHMS\n")
        f.write("="*80 + "\n\n")
        f.write("This report verifies correctness of all algorithms on graphs with known expected results.\n")
        f.write("Each graph tests different aspects of algorithm behavior.\n\n")
        
        for graph_name, graph_info in VERIFICATION_GRAPHS.items():
            f.write(f"\n{'='*80}\n")
            f.write(f"Graph: {graph_info['name']} ({graph_name})\n")
            f.write(f"{'='*80}\n")
            f.write(f"Nodes: {graph_info['nodes']}, Edges: {graph_info['edges']}\n\n")
            
            results = all_results.get(graph_name, {})
            for algo_type in ['kcore', 'degree', 'betweenness', 'bridging', 'katz', 
                            'eigenvector', 'hits_hub', 'hits_auth', 'pagerank']:
                algo_results = results.get(algo_type, {})
                f.write(f"{algo_type.upper()}:\n")
                if algo_results:
                    values_list = list(algo_results.values())
                    f.write(f"  Nodes with data: {len(algo_results)}/{graph_info['nodes']}\n")
                    f.write(f"  Value range: [{min(values_list):.4f}, {max(values_list):.4f}]\n")
                    f.write(f"  Unique values: {len(set(values_list))}\n")
                    if len(algo_results) <= 20:
                        f.write(f"  All values: {sorted(algo_results.items())}\n")
                else:
                    f.write(f"  No data found\n")
                f.write("\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"\nTotal verification graphs: {len(VERIFICATION_GRAPHS)}\n")
        f.write(f"Total algorithm tests: {total_tests}\n")
        f.write(f"Total issues found: {total_issues}\n")
        
        if all_issues:
            f.write(f"\nISSUES FOUND:\n")
            for issue in all_issues:
                f.write(f"  - {issue}\n")
        else:
            f.write("\n✓ ALL TESTS PASSED!\n")
    
    print(f"\n✓ Report saved to: {report_file.absolute()}")

if __name__ == "__main__":
    generate_report()

