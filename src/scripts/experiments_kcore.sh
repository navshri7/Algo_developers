#!/bin/bash

# K-Core Decomposition Experiment Runner
# This script runs comprehensive experiments on synthetic and real datasets

set -e  # Exit on error

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "K-Core Decomposition: Comprehensive Experiment Suite"
echo "======================================================================"
echo ""

# Create directory structure
mkdir -p results/synthetic
mkdir -p results/real_datasets
mkdir -p results/bridging_centrality
mkdir -p results/degree_centrality
mkdir -p results/hits
mkdir -p data/synthetic_graphs
mkdir -p data/converted_datasets

# Compile the C++ program
echo "Step 1: Compiling K-Core implementation..."
g++ -std=c++17 -O3 -o bin/kcore src/algorithms/kcore.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Compilation successful"
else
    echo "  ✗ Compilation failed"
    exit 1
fi

g++ -std=c++17 -O3 -o bin/bridging_centrality src/algorithms/bridging_centrality.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Bridging Centrality compilation successful"
else
    echo "  ✗ Bridging Centrality compilation failed"
    exit 1
fi

g++ -std=c++17 -O3 -o bin/degree_centrality src/algorithms/degree_centrality.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ Degree Centrality compilation successful"
else
    echo "  ✗ Degree Centrality compilation failed"
    exit 1
fi

g++ -std=c++17 -O3 -o bin/hits src/algorithms/hits.cpp
if [ $? -eq 0 ]; then
    echo "  ✓ HITS compilation successful"
else
    echo "  ✗ HITS compilation failed"
    exit 1
fi
echo ""

# Generate synthetic graphs
echo "Step 2: Generating synthetic test graphs..."
python3 src/python/data/generate_synthetic_graphs.py
echo ""

# Convert real datasets
echo "Step 3: Converting real datasets to standard format..."
python3 src/python/data/convert_datasets.py
echo ""

# Run experiments on synthetic graphs
echo "Step 4: Running experiments on synthetic graphs..."
echo "----------------------------------------------------------------------"

# Verification graphs (small, known structure)
echo "4.1 Verification Graphs:"
for graph in data/synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Small graphs
echo "4.2 Small Test Graphs (100-1000 nodes):"
for graph in data/synthetic_graphs/er_*_*.txt data/synthetic_graphs/ba_1k_*.txt data/synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Medium graphs
echo "4.3 Medium Test Graphs (5000-10000 nodes):"
for graph in data/synthetic_graphs/er_5k_*.txt data/synthetic_graphs/er_10k_*.txt data/synthetic_graphs/ba_5k_*.txt data/synthetic_graphs/ba_10k_*.txt data/synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Clique-based graphs
echo "4.4 Clique-Based Graphs:"
for graph in data/synthetic_graphs/cliques_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Power-law cluster graphs
echo "4.5 Power-Law Cluster Graphs:"
for graph in data/synthetic_graphs/plc_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/kcore "$graph" "results/synthetic" "$basename"
    fi
done
echo ""

# Run experiments on real datasets
echo "Step 5: Running experiments on real datasets..."
echo "----------------------------------------------------------------------"

# cit-DBLP (converted)
if [ -f "data/converted_datasets/cit-DBLP.txt" ]; then
    echo "5.1 Running on cit-DBLP..."
    bin/kcore "data/converted_datasets/cit-DBLP.txt" "results/real_datasets" "cit-DBLP"
    echo ""
else
    echo "5.1 Skipping cit-DBLP (not found)"
    echo ""
fi

# cit-HepTh (converted)
if [ -f "data/converted_datasets/cit-HepTh.txt" ]; then
    echo "5.2 Running on cit-HepTh..."
    bin/kcore "data/converted_datasets/cit-HepTh.txt" "results/real_datasets" "cit-HepTh"
    echo ""
else
    echo "5.2 Skipping cit-HepTh (not found)"
    echo ""
fi

# CiteSeer (converted)
if [ -f "data/converted_datasets/citeseer.txt" ]; then
    echo "5.3 Running on CiteSeer..."
    bin/kcore "data/converted_datasets/citeseer.txt" "results/real_datasets" "citeseer"
    echo ""
else
    echo "5.3 Skipping CiteSeer (not found)"
    echo ""
fi

# Cora (converted)
if [ -f "data/converted_datasets/cora.txt" ]; then
    echo "5.4 Running on Cora..."
    bin/kcore "data/converted_datasets/cora.txt" "results/real_datasets" "cora"
    echo ""
else
    echo "5.4 Skipping Cora (not found)"
    echo ""
fi

# ============================================================================
# BRIDGING CENTRALITY - Synthetic Graphs
# ============================================================================
echo "Step 6: Running Bridging Centrality on synthetic graphs..."
echo "----------------------------------------------------------------------"

echo "6.1 Verification Graphs:"
for graph in data/synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/bridging_centrality "$graph" "results/bridging_centrality"
    fi
done
echo ""

echo "6.2 Small Test Graphs (100-1000 nodes):"
for graph in data/synthetic_graphs/er_*_*.txt data/synthetic_graphs/ba_1k_*.txt data/synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/bridging_centrality "$graph" "results/bridging_centrality"
    fi
done
echo ""

echo "6.3 Medium Test Graphs (5000-10000 nodes):"
for graph in data/synthetic_graphs/er_5k_*.txt data/synthetic_graphs/er_10k_*.txt data/synthetic_graphs/ba_5k_*.txt data/synthetic_graphs/ba_10k_*.txt data/synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        echo "  Running: $basename"
        bin/bridging_centrality "$graph" "results/bridging_centrality"
    fi
done
echo ""

# ============================================================================
# BRIDGING CENTRALITY - Real Datasets
# ============================================================================
echo "Step 7: Running Bridging Centrality on real datasets..."
echo "----------------------------------------------------------------------"

for dataset in "cit-DBLP" "cit-HepTh" "citeseer" "cora"; do
    if [ -f "data/converted_datasets/${dataset}.txt" ]; then
        echo "  Running: $dataset"
        bin/bridging_centrality "data/converted_datasets/${dataset}.txt" "results/bridging_centrality"
    fi
done
echo ""

# ============================================================================
# DEGREE CENTRALITY - Synthetic Graphs
# ============================================================================
echo "Step 8: Running Degree Centrality on synthetic graphs..."
echo "----------------------------------------------------------------------"

echo "8.1 Verification Graphs:"
for graph in data/synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        bin/degree_centrality "$graph" "results/degree_centrality"
    fi
done
echo ""

echo "8.2 Small Test Graphs (100-1000 nodes):"
for graph in data/synthetic_graphs/er_*_*.txt data/synthetic_graphs/ba_1k_*.txt data/synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        bin/degree_centrality "$graph" "results/degree_centrality"
    fi
done
echo ""

echo "8.3 Medium Test Graphs (5000-10000 nodes):"
for graph in data/synthetic_graphs/er_5k_*.txt data/synthetic_graphs/er_10k_*.txt data/synthetic_graphs/ba_5k_*.txt data/synthetic_graphs/ba_10k_*.txt data/synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        bin/degree_centrality "$graph" "results/degree_centrality"
    fi
done
echo ""

# ============================================================================
# DEGREE CENTRALITY - Real Datasets
# ============================================================================
echo "Step 9: Running Degree Centrality on real datasets..."
echo "----------------------------------------------------------------------"

for dataset in "cit-DBLP" "cit-HepTh" "citeseer" "cora"; do
    if [ -f "data/converted_datasets/${dataset}.txt" ]; then
        echo "  Running: $dataset"
        bin/degree_centrality "data/converted_datasets/${dataset}.txt" "results/degree_centrality"
    fi
done
echo ""

# ============================================================================
# HITS - Synthetic Graphs
# ============================================================================
echo "Step 10: Running HITS on synthetic graphs..."
echo "----------------------------------------------------------------------"

echo "10.1 Verification Graphs:"
for graph in data/synthetic_graphs/verify_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        bin/hits "$graph" "results/hits"
    fi
done
echo ""

echo "10.2 Small Test Graphs (100-1000 nodes):"
for graph in data/synthetic_graphs/er_*_*.txt data/synthetic_graphs/ba_1k_*.txt data/synthetic_graphs/ws_1k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        bin/hits "$graph" "results/hits"
    fi
done
echo ""

echo "10.3 Medium Test Graphs (5000-10000 nodes):"
for graph in data/synthetic_graphs/er_5k_*.txt data/synthetic_graphs/er_10k_*.txt data/synthetic_graphs/ba_5k_*.txt data/synthetic_graphs/ba_10k_*.txt data/synthetic_graphs/ws_5k_*.txt; do
    if [ -f "$graph" ]; then
        basename=$(basename "$graph" .txt)
        bin/hits "$graph" "results/hits"
    fi
done
echo ""

# ============================================================================
# HITS - Real Datasets
# ============================================================================
echo "Step 11: Running HITS on real datasets..."
echo "----------------------------------------------------------------------"

for dataset in "cit-DBLP" "cit-HepTh" "citeseer" "cora"; do
    if [ -f "data/converted_datasets/${dataset}.txt" ]; then
        echo "  Running: $dataset"
        bin/hits "data/converted_datasets/${dataset}.txt" "results/hits"
    fi
done
echo ""

echo "======================================================================"
echo "All experiments completed!"
echo "======================================================================"
echo ""
echo "Results are available in:"
echo "  - results/synthetic/            (K-Core synthetic results)"
echo "  - results/real_datasets/        (K-Core real dataset results)"
echo "  - results/bridging_centrality/  (Bridging centrality results)"
echo "  - results/degree_centrality/    (Degree centrality results)"
echo "  - results/hits/                 (HITS algorithm results)"
echo ""
