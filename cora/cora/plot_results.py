#!/usr/bin/env python3
"""
plot_results.py

Reads `eigenc_output.csv` and `katz_output.csv`, joins by node id, and
produces a scatter plot comparing Eigenvector vs Katz centrality. Saves
`centrality_scatter.png` and prints basic statistics.

Usage (PowerShell):
python .\plot_results.py

Requires: matplotlib, pandas (install with `pip install matplotlib pandas`)
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

e = pd.read_csv('eigenc_output.csv')
k = pd.read_csv('katz_output.csv')
df = pd.merge(e, k, on='node_id', suffixes=('_eig','_katz'))

eig = df['eigen_centrality'].values
katz = df['katz_centrality'].values

corr = np.corrcoef(eig, katz)[0,1]
print(f'Nodes joined: {len(df)}, Pearson correlation: {corr:.4f}')

plt.figure(figsize=(6,6))
plt.scatter(eig, katz, s=6, alpha=0.6)
plt.xlabel('Eigenvector centrality (norm max=1)')
plt.ylabel('Katz centrality (norm max=1)')
plt.title(f'Eigen vs Katz centrality (corr={corr:.3f})')
plt.grid(True)
plt.tight_layout()
plt.savefig('centrality_scatter.png', dpi=200)
print("Saved 'centrality_scatter.png'.")

# Print top-10 lists and overlap
top_eig = df.nlargest(20, 'eigen_centrality')['node_id'].astype(str).tolist()
top_katz = df.nlargest(20, 'katz_centrality')['node_id'].astype(str).tolist()
print('Top 20 Eigenvector IDs:', ','.join(top_eig[:10]))
print('Top 20 Katz IDs:', ','.join(top_katz[:10]))
overlap = set(top_eig).intersection(top_katz)
print(f'Top-20 overlap count: {len(overlap)}')
