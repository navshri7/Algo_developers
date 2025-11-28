#!/usr/bin/env python3
"""
analyze_centralities.py

Reads `eigenc_output.csv` and `katz_output.csv`, computes ranking comparisons,
labels nodes as 'foundational' and 'frontier' by simple operational rules,
and saves `classification.csv` plus diagnostic plots.

Usage:
  python analyze_centralities.py

Outputs:
  - classification.csv
  - topk_overlap.png
  - centrality_histograms.png

Definitions used (configurable in script):
  - Foundational: node is in top 5% by in-degree (highly cited)
  - Frontier: node is in top 5% by Katz or Eigen but NOT in top 25% by in-degree

These are heuristic labels for exploring differences between centralities.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

e = pd.read_csv('eigenc_output.csv')
k = pd.read_csv('katz_output.csv')
df = pd.merge(e, k, on='node_id', suffixes=('_eig','_katz'))

# After merge, degree columns will be suffixed (e.g. 'in_degree_eig').
# Pick the available in-degree column and normalize name to 'in_degree'.
possible_indeg = [c for c in df.columns if 'in' in c and 'deg' in c]
if len(possible_indeg) == 0:
  raise RuntimeError('Could not find an in-degree column in merged CSVs')
indeg_col = possible_indeg[0]
if indeg_col != 'in_degree':
  df['in_degree'] = df[indeg_col]

# Pick the available out-degree column and normalize name to 'out_degree'.
possible_outdeg = [c for c in df.columns if 'out' in c and 'deg' in c]
if len(possible_outdeg) == 0:
  # try a more relaxed match
  possible_outdeg = [c for c in df.columns if 'degree' in c and c != indeg_col]
if len(possible_outdeg) == 0:
  # if still not found, create a zero column to avoid failures downstream
  df['out_degree'] = 0
else:
  outdeg_col = possible_outdeg[0]
  if outdeg_col != 'out_degree':
    df['out_degree'] = df[outdeg_col]

N = len(df)
print(f'N nodes = {N}')

# compute ranks (1 = highest)
# Use positional ranks (method='first') so ranks run from 1..N rather than dense
# which only counts distinct values (dense was causing the frontier test to fail).
df['rank_indeg_pos'] = df['in_degree'].rank(method='first', ascending=False).astype(int)
df['rank_eig_pos'] = df['eigen_centrality'].rank(method='first', ascending=False).astype(int)
df['rank_katz_pos'] = df['katz_centrality'].rank(method='first', ascending=False).astype(int)

# Provide canonical rank column names expected by downstream code/CSV
df['rank_indeg'] = df['rank_indeg_pos']
df['rank_eig'] = df['rank_eig_pos']
df['rank_katz'] = df['rank_katz_pos']

# thresholds
pct_found = 0.05
pct_front_indeg_max = 0.25
th_found = max(1, int(np.ceil(N * pct_found)))
th_front_indeg = int(np.ceil(N * pct_front_indeg_max))
print(f'top {pct_found*100:.1f}% -> {th_found} nodes considered foundational')


# label foundational: top th_found by in_degree (positional)
df = df.sort_values('in_degree', ascending=False).reset_index(drop=True)
df['foundational'] = False
top_indeg_ids = set(df.head(th_found)['node_id'])
df.loc[df['node_id'].isin(top_indeg_ids), 'foundational'] = True

# label frontier: in top 5% by Katz or Eigen but NOT in top 25% by indeg
# pick top by sorting centrality directly (robust to ties)
th_top5 = th_found
top_katz = set(df.sort_values('katz_centrality', ascending=False).head(th_top5)['node_id'])
top_eig = set(df.sort_values('eigen_centrality', ascending=False).head(th_top5)['node_id'])
candidate_front = top_katz.union(top_eig)
df['frontier'] = False
for nid in candidate_front:
  # use positional indeg rank for threshold test
  pos = int(df.loc[df['node_id'] == nid].index[0]) + 1
  if pos > th_front_indeg:
    df.loc[df['node_id'] == nid, 'frontier'] = True

# Save classification
cols = ['node_id','eigen_centrality','katz_centrality','in_degree','out_degree','foundational','frontier','rank_indeg','rank_eig','rank_katz']
df[cols].to_csv('classification.csv', index=False)
print('Wrote classification.csv')

# Top-k overlap curve between indeg and centralities
ks = list(range(5, min(500, N), 5))
overlap_katz = []
overlap_eig = []
for k_ in ks:
    top_ind = set(df.nsmallest(k_, 'rank_indeg')['node_id'])
    top_k = set(df.nsmallest(k_, 'rank_katz')['node_id'])
    top_e = set(df.nsmallest(k_, 'rank_eig')['node_id'])
    overlap_katz.append(len(top_ind & top_k) / k_)
    overlap_eig.append(len(top_ind & top_e) / k_)

plt.figure(figsize=(6,4))
plt.plot(ks, overlap_katz, label='Indeg ∩ Katz')
plt.plot(ks, overlap_eig, label='Indeg ∩ Eigen')
plt.xlabel('k (top-k)')
plt.ylabel('Fraction overlap')
plt.title('Top-k overlap with in-degree')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('topk_overlap.png', dpi=200)
print('Saved topk_overlap.png')

# Histograms
plt.figure(figsize=(8,4))
plt.subplot(1,2,1)
plt.hist(df['eigen_centrality'], bins=40)
plt.title('Eigenvector centrality (normed)')
plt.subplot(1,2,2)
plt.hist(df['katz_centrality'], bins=40)
plt.title('Katz centrality (normed)')
plt.tight_layout()
plt.savefig('centrality_histograms.png', dpi=200)
print('Saved centrality_histograms.png')

# Print sample lists
print('\nSample Foundational (top by indeg):')
print(df[df['foundational']].sort_values('in_degree', ascending=False).head(20)[['node_id','in_degree']].to_string(index=False))

print('\nSample Frontier (high centrality but low indeg):')
print(df[df['frontier']].sort_values(['katz_centrality','eigen_centrality'], ascending=False).head(20)[['node_id','katz_centrality','eigen_centrality','in_degree']].to_string(index=False))

print('\nCounts: foundational=', df['foundational'].sum(), ' frontier=', df['frontier'].sum())
