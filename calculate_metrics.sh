#!/bin/bash
# Calculate Additional Performance Metrics: Comparisons and Throughput
# This script computes metrics from existing algorithm results

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "Calculating Additional Performance Metrics"
echo "======================================================================"
echo ""

# Check if venv exists and activate it
if [ -d "venv/bin" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
else
    echo "⚠ Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q pandas numpy matplotlib seaborn
    echo "✓ Virtual environment created"
    echo ""
fi

echo "Running metrics calculation script..."
python3 src/python/analysis/calculate_metrics.py

echo ""
echo "======================================================================"
echo "Metrics calculation complete!"
echo "======================================================================"
echo ""
echo "Results saved to: results/metrics_analysis/"
echo ""

