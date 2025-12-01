#!/bin/bash

# Quick runner - activates venv and runs all experiments
# Usage: bash run.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "Algorithm Analysis Suite - Quick Runner"
echo "======================================================================"
echo ""

# Check if venv exists and activate it
if [ -d "venv/bin" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
else
    echo "⚠ Virtual environment not found at venv/"
    echo "  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "  Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Virtual environment created and dependencies installed"
    echo ""
fi

# Verify key files exist
echo "Verifying project structure..."
ERRORS=0

if [ ! -f "Makefile" ]; then
    echo "  ✗ Makefile not found"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -d "src/algorithms" ]; then
    echo "  ✗ src/algorithms/ not found"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -d "src/scripts" ]; then
    echo "  ✗ src/scripts/ not found"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -d "src/python" ]; then
    echo "  ✗ src/python/ not found"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
    echo "✗ Project structure verification failed ($ERRORS errors)"
    exit 1
fi

echo "✓ Project structure verified"
echo ""

# Run master script
echo "Starting experiments..."
echo ""
bash src/scripts/run_all.sh

echo ""
echo "======================================================================"
echo "Running Correlation Studies..."
echo "======================================================================"
echo ""
python3 src/python/analysis/correlation_studies.py

echo ""
echo "======================================================================"
echo "Running Comprehensive Algorithm Comparison..."
echo "======================================================================"
echo ""
python3 src/python/analysis/compare_all_algorithms.py

echo ""
echo "======================================================================"
echo "Running Comprehensive Runtime & Memory Analysis..."
echo "======================================================================"
echo ""
python3 src/python/analysis/comprehensive_runtime_memory_analysis.py

echo ""
echo "======================================================================"
echo "✓ All experiments and analyses completed!"
echo "======================================================================"
echo ""
echo "Results Summary:"
echo "  📊 Experiments:        results/synthetic/, results/real_datasets/"
echo "  🎨 Visualizations:     results/node_visualizations/"
echo "  📈 Algorithm Compare:  results/algorithm_comparison/"
echo "  🔗 Correlations:       results/correlation_studies/"
echo "  ⚡ Runtime/Memory:    results/comprehensive_runtime_memory/"
echo ""
echo "Key outputs:"
echo "  1. Correlation heatmaps showing algorithm relationships"
echo "  2. Scatter plots for selected algorithm pairs"
echo "  3. Detailed correlation analysis report"
echo "  4. Recommendations for citation network analysis"
echo ""
echo "Next steps:"
echo "  1. Review correlation_studies/ for algorithm relationships"
echo "  2. Check algorithm_comparison/ for performance metrics"
echo "  3. View node_visualizations/ for ranking comparisons"
echo "  4. See docs/COMPLETE_GUIDE.md for detailed information"
echo ""
