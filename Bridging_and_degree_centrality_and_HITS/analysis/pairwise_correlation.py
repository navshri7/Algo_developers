import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
deg = pd.read_csv("results/degree_results.csv")
brg = pd.read_csv("results/bridging_results.csv")
hits = pd.read_csv("results/hits_results.csv")
df = pd.DataFrame()
df["Node"] = deg["Node"]
df["Degree"] = deg.set_index("Node")["TotalDegree"].reindex(df["Node"]).values
df["Bridging"] = brg.set_index("Node")["BridgingCentrality"].reindex(df["Node"]).values
df["HITS"] = hits.set_index("Node")["Authority"].reindex(df["Node"]).values
df = df.dropna()
pearson_corr = df[["Degree", "Bridging", "HITS"]].corr(method='pearson')
spearman_corr = df[["Degree", "Bridging", "HITS"]].corr(method='spearman')

print("\n===== Pearson Correlation =====")
print(pearson_corr)

print("\n===== Spearman Correlation =====")
print(spearman_corr)

ensure_dir("plots")

plt.figure(figsize=(7, 5))
sns.heatmap(pearson_corr, annot=True, cmap="coolwarm", fmt=".3f")
plt.title("Pearson Correlation — Centrality Algorithms")
plt.tight_layout()
plt.savefig("plots/pairwise_correlation_pearson.png", dpi=300)
plt.close()

plt.figure(figsize=(7, 5))
sns.heatmap(spearman_corr, annot=True, cmap="coolwarm", fmt=".3f")
plt.title("Spearman Correlation — Centrality Algorithms")
plt.tight_layout()
plt.savefig("plots/pairwise_correlation_spearman.png", dpi=300)
plt.close()

print("\nSaved:")
print(" → plots/pairwise_correlation_pearson.png")
print(" → plots/pairwise_correlation_spearman.png")
