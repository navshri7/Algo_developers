# Bug Fixes - Experiment Scripts

## Issue Found
The experiment scripts were using old filenames and paths:
- Looking for `betweenness_new.cpp` instead of `src/algorithms/betweenness_exact.cpp`
- Looking for `approxbet_new.cpp` instead of `src/algorithms/betweenness_approx.cpp`
- Looking for `katz_centrality.cpp` in root instead of `src/algorithms/katz_centrality.cpp`
- Outputting binaries to root instead of `bin/`

## Fixes Applied

### 1. experiments_betweenness.sh
**Fixed**:
- ✓ Changed `betweenness_new.cpp` → `src/algorithms/betweenness_exact.cpp`
- ✓ Changed `approxbet_new.cpp` → `src/algorithms/betweenness_approx.cpp`
- ✓ Changed output path `betweenness_exact` → `bin/betweenness_exact`
- ✓ Changed output path `betweenness_approx` → `bin/betweenness_approx`
- ✓ Updated all binary references from `./betweenness_*` → `bin/betweenness_*`

### 2. experiments_centrality.sh
**Fixed**:
- ✓ Changed `katz_centrality.cpp` → `src/algorithms/katz_centrality.cpp`
- ✓ Changed `eigenvector_centrality.cpp` → `src/algorithms/eigenvector_centrality.cpp`
- ✓ Changed output path `katz_centrality` → `bin/katz_centrality`
- ✓ Changed output path `eigenvector_centrality` → `bin/eigenvector_centrality`
- ✓ Updated all binary references from `./katz_centrality` → `bin/katz_centrality`
- ✓ Updated all binary references from `./eigenvector_centrality` → `bin/eigenvector_centrality`

### 3. experiments_kcore.sh
**Already correct** - No changes needed

## Verification

✓ All C++ files present in `src/algorithms/`:
- betweenness_approx.cpp
- betweenness_exact.cpp
- eigenvector_centrality.cpp
- katz_centrality.cpp
- kcore.cpp

✓ All experiment scripts have valid bash syntax:
- experiments_kcore.sh
- experiments_betweenness.sh
- experiments_centrality.sh

✓ All paths updated to new structure:
- Source files: `src/algorithms/`
- Binaries: `bin/`
- Data: `data/`
- Results: `results/`

## Testing

To verify fixes work:
```bash
# Test compilation
make build

# Test individual experiments
bash src/scripts/experiments_kcore.sh
bash src/scripts/experiments_betweenness.sh
bash src/scripts/experiments_centrality.sh

# Or run all
bash run.sh
```

## Root Cause
The scripts were created before the refactoring moved files to `src/algorithms/` and binaries to `bin/`. The paths were not updated during the reorganization.

## Prevention
All scripts now:
- Use correct source paths: `src/algorithms/`
- Output binaries to: `bin/`
- Reference data from: `data/`
- Store results in: `results/`

This matches the new organized structure and prevents future path issues.
