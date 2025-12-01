#!/usr/bin/env python3
"""
Convert real datasets to standard edge list format for k-core analysis
Handles various dataset formats and outputs to converted_datasets/
"""

import os
from pathlib import Path

def convert_cit_dblp():
    """Convert cit-DBLP dataset (already in edge format)"""
    input_file = "data/cit-DBLP.edges"
    output_file = "data/converted_datasets/cit-DBLP.txt"
    
    if not os.path.exists(input_file):
        print(f"  ✗ {input_file} not found")
        return False
    
    try:
        edges = set()
        nodes = set()
        
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    u, v = int(parts[0]), int(parts[1])
                    if u != v:
                        edges.add((min(u, v), max(u, v)))
                        nodes.add(u)
                        nodes.add(v)
        
        if not edges:
            print(f"  ✗ No edges found in {input_file}")
            return False
        
        # Remap nodes to 1-indexed
        node_map = {node: i+1 for i, node in enumerate(sorted(nodes))}
        
        with open(output_file, 'w') as f:
            f.write(f"{len(nodes)} {len(edges)}\n")
            for u, v in sorted(edges):
                f.write(f"{node_map[u]} {node_map[v]}\n")
        
        print(f"  ✓ cit-DBLP: {len(nodes)} nodes, {len(edges)} edges")
        return True
    except Exception as e:
        print(f"  ✗ Error converting cit-DBLP: {e}")
        return False

def convert_cit_hepth():
    """Convert cit-HepTh dataset"""
    input_file = "data/cit-HepTh.txt/Cit-HepTh.txt"
    output_file = "data/converted_datasets/cit-HepTh.txt"
    
    if not os.path.exists(input_file):
        print(f"  ✗ {input_file} not found")
        return False
    
    try:
        edges = set()
        nodes = set()
        
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    u, v = int(parts[0]), int(parts[1])
                    if u != v:
                        edges.add((min(u, v), max(u, v)))
                        nodes.add(u)
                        nodes.add(v)
        
        if not edges:
            print(f"  ✗ No edges found in {input_file}")
            return False
        
        # Remap nodes to 1-indexed
        node_map = {node: i+1 for i, node in enumerate(sorted(nodes))}
        
        with open(output_file, 'w') as f:
            f.write(f"{len(nodes)} {len(edges)}\n")
            for u, v in sorted(edges):
                f.write(f"{node_map[u]} {node_map[v]}\n")
        
        print(f"  ✓ cit-HepTh: {len(nodes)} nodes, {len(edges)} edges")
        return True
    except Exception as e:
        print(f"  ✗ Error converting cit-HepTh: {e}")
        return False

def convert_citeseer():
    """Convert CiteSeer dataset (comma-separated format)"""
    input_file = "data/citeseer/citeseer.edges"
    output_file = "data/converted_datasets/citeseer.txt"
    
    if not os.path.exists(input_file):
        print(f"  ✗ {input_file} not found")
        return False
    
    try:
        edges = set()
        nodes = set()
        
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Handle comma-separated format
                parts = line.replace(',', ' ').split()
                if len(parts) >= 2:
                    u, v = int(parts[0]), int(parts[1])
                    if u != v:
                        edges.add((min(u, v), max(u, v)))
                        nodes.add(u)
                        nodes.add(v)
        
        if not edges:
            print(f"  ✗ No edges found in {input_file}")
            return False
        
        # Remap nodes to 1-indexed
        node_map = {node: i+1 for i, node in enumerate(sorted(nodes))}
        
        with open(output_file, 'w') as f:
            f.write(f"{len(nodes)} {len(edges)}\n")
            for u, v in sorted(edges):
                f.write(f"{node_map[u]} {node_map[v]}\n")
        
        print(f"  ✓ CiteSeer: {len(nodes)} nodes, {len(edges)} edges")
        return True
    except Exception as e:
        print(f"  ✗ Error converting CiteSeer: {e}")
        return False

def convert_cora():
    """Convert Cora dataset from cites format"""
    input_file = "data/cora-dataset/cora/cora.cites"
    output_file = "data/converted_datasets/cora.txt"
    
    if not os.path.exists(input_file):
        print(f"  ✗ {input_file} not found")
        return False
    
    try:
        edges = set()
        nodes = set()
        
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    u, v = int(parts[0]), int(parts[1])
                    if u != v:
                        edges.add((min(u, v), max(u, v)))
                        nodes.add(u)
                        nodes.add(v)
        
        if not edges:
            print(f"  ✗ No edges found in {input_file}")
            return False
        
        # Remap nodes to 1-indexed
        node_map = {node: i+1 for i, node in enumerate(sorted(nodes))}
        
        with open(output_file, 'w') as f:
            f.write(f"{len(nodes)} {len(edges)}\n")
            for u, v in sorted(edges):
                f.write(f"{node_map[u]} {node_map[v]}\n")
        
        print(f"  ✓ Cora: {len(nodes)} nodes, {len(edges)} edges")
        return True
    except Exception as e:
        print(f"  ✗ Error converting Cora: {e}")
        return False

def main():
    output_dir = Path("data/converted_datasets")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("Converting real datasets to standard format...")
    print("=" * 60)
    
    results = []
    results.append(("cit-DBLP", convert_cit_dblp()))
    results.append(("cit-HepTh", convert_cit_hepth()))
    results.append(("CiteSeer", convert_citeseer()))
    results.append(("Cora", convert_cora()))
    
    print("\n" + "=" * 60)
    successful = sum(1 for _, success in results if success)
    print(f"Successfully converted {successful}/{len(results)} datasets")
    print(f"Output directory: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
