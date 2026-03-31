import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import networkx as nx
import community as community_louvain

# =========================================================
# 1. PARAMÈTRES
# =========================================================
input_matrix_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_group_average_matrices"
)

output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_hubs_connectivite"
)
output_dir.mkdir(parents=True, exist_ok=True)

coords_csv = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\atlas_coordinates\Schaefer_100_7Networks_coordinates.csv"
)

fc_young = np.load(input_matrix_dir / "FC_mean_young_lt55.npy")
fc_old   = np.load(input_matrix_dir / "FC_mean_old_ge55.npy")

sc_young = np.load(input_matrix_dir / "SC_mean_young_lt55.npy")
sc_old   = np.load(input_matrix_dir / "SC_mean_old_ge55.npy")

# paramètres
n_runs = 100
resolution_fc = 1.3
resolution_sc = 1.3
consensus_threshold = 0.5
z_threshold = 1.0
pc_threshold = 0.30
top_n = 10

# =========================================================
# 1bis. CHARGER LES LABELS DE RÉGIONS DEPUIS LE CSV
# =========================================================
coords_df = pd.read_csv(coords_csv)

if "label" not in coords_df.columns:
    raise ValueError(f"Colonne 'label' absente dans {coords_csv}")

region_labels = coords_df["label"].astype(str).tolist()

if len(region_labels) != fc_young.shape[0]:
    raise ValueError(
        f"Nombre de labels ({len(region_labels)}) différent du nombre de nœuds "
        f"dans les matrices ({fc_young.shape[0]})."
    )

# =========================================================
# 2. FONCTIONS CONSENSUS
# =========================================================
def clean_matrix(mat, modality="FC"):
    mat = np.array(mat, dtype=float)
    mat[~np.isfinite(mat)] = 0.0
    np.fill_diagonal(mat, 0.0)

    if modality == "FC":
        mat[mat < 0] = 0.0
    else:
        mat[mat < 0] = 0.0

    return mat


def louvain_one_run(mat, resolution=1.0):
    G = nx.from_numpy_array(mat)
    partition = community_louvain.best_partition(G, weight="weight", resolution=resolution)
    return np.array([partition[i] for i in range(len(mat))])


def run_louvain(mat, n_runs=100, resolution=1.0):
    return np.array([louvain_one_run(mat, resolution) for _ in range(n_runs)])


def agreement_matrix(partitions):
    n_runs, n_nodes = partitions.shape
    A = np.zeros((n_nodes, n_nodes))

    for p in partitions:
        A += (p[:, None] == p[None, :]).astype(float)

    return A / n_runs


def consensus_partition(A, threshold=0.5):
    A = A.copy()
    A[A < threshold] = 0
    np.fill_diagonal(A, 0)

    G = nx.from_numpy_array(A)
    partition = community_louvain.best_partition(G, weight="weight")

    return np.array([partition[i] for i in range(len(A))])


def compute_consensus(mat, modality, resolution):
    mat = clean_matrix(mat, modality)
    partitions = run_louvain(mat, n_runs, resolution)
    A = agreement_matrix(partitions)
    labels = consensus_partition(A, consensus_threshold)
    return mat, labels

# =========================================================
# 3. HUBS
# =========================================================
def compute_strength(mat):
    return np.sum(mat, axis=1)


def zscore(x):
    std = np.std(x)
    if std == 0:
        return np.zeros_like(x)
    return (x - np.mean(x)) / std


def participation_coefficient(mat, labels):
    n = len(mat)
    pc = np.zeros(n)

    for i in range(n):
        ki = np.sum(mat[i])
        if ki == 0:
            continue

        for m in np.unique(labels):
            idx = np.where(labels == m)[0]
            kis = np.sum(mat[i, idx])
            pc[i] += (kis / ki) ** 2

        pc[i] = 1 - pc[i]

    return pc


def compute_hubs(mat, labels, region_labels):
    strength = compute_strength(mat)
    z = zscore(strength)
    pc = participation_coefficient(mat, labels)

    return pd.DataFrame({
        "node_index": np.arange(len(mat)),
        "region_name": region_labels,
        "module_label": labels,
        "strength": strength,
        "strength_z": z,
        "participation_coefficient": pc
    })

# =========================================================
# 4. FIGURES HUBS
# =========================================================
def plot_top_hubs(df1, df2, metric, title, color, save_path):
    def top(df):
        return df.sort_values(metric, ascending=False).head(top_n).iloc[::-1]

    d1 = top(df1)
    d2 = top(df2)

    plt.style.use("dark_background")
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    axes[0].barh(d1["region_name"], d1[metric], color=color)
    axes[0].set_title("<55")
    axes[0].set_xlabel(metric)
    axes[0].tick_params(axis="y", labelsize=8)

    axes[1].barh(d2["region_name"], d2[metric], color=color)
    axes[1].set_title(">=55")
    axes[1].set_xlabel(metric)
    axes[1].tick_params(axis="y", labelsize=8)

    fig.suptitle(title, fontsize=16)
    plt.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

# =========================================================
# 5. CALCUL CONSENSUS
# =========================================================
fc_young_mat, fc_young_labels = compute_consensus(fc_young, "FC", resolution_fc)
fc_old_mat, fc_old_labels = compute_consensus(fc_old, "FC", resolution_fc)

sc_young_mat, sc_young_labels = compute_consensus(sc_young, "SC", resolution_sc)
sc_old_mat, sc_old_labels = compute_consensus(sc_old, "SC", resolution_sc)

# =========================================================
# 6. CALCUL HUBS
# =========================================================
fc_young_df = compute_hubs(fc_young_mat, fc_young_labels, region_labels)
fc_old_df   = compute_hubs(fc_old_mat, fc_old_labels, region_labels)

sc_young_df = compute_hubs(sc_young_mat, sc_young_labels, region_labels)
sc_old_df   = compute_hubs(sc_old_mat, sc_old_labels, region_labels)

# sauvegarde complète
fc_young_df.to_csv(output_dir / "fc_young_hubs_with_labels.csv", index=False)
fc_old_df.to_csv(output_dir / "fc_old_hubs_with_labels.csv", index=False)
sc_young_df.to_csv(output_dir / "sc_young_hubs_with_labels.csv", index=False)
sc_old_df.to_csv(output_dir / "sc_old_hubs_with_labels.csv", index=False)

# top 10 sauvegardés
fc_young_df.sort_values("strength", ascending=False).head(top_n).to_csv(
    output_dir / "fc_young_top10_strength.csv", index=False
)
fc_old_df.sort_values("strength", ascending=False).head(top_n).to_csv(
    output_dir / "fc_old_top10_strength.csv", index=False
)
fc_young_df.sort_values("participation_coefficient", ascending=False).head(top_n).to_csv(
    output_dir / "fc_young_top10_pc.csv", index=False
)
fc_old_df.sort_values("participation_coefficient", ascending=False).head(top_n).to_csv(
    output_dir / "fc_old_top10_pc.csv", index=False
)

sc_young_df.sort_values("strength", ascending=False).head(top_n).to_csv(
    output_dir / "sc_young_top10_strength.csv", index=False
)
sc_old_df.sort_values("strength", ascending=False).head(top_n).to_csv(
    output_dir / "sc_old_top10_strength.csv", index=False
)
sc_young_df.sort_values("participation_coefficient", ascending=False).head(top_n).to_csv(
    output_dir / "sc_young_top10_pc.csv", index=False
)
sc_old_df.sort_values("participation_coefficient", ascending=False).head(top_n).to_csv(
    output_dir / "sc_old_top10_pc.csv", index=False
)

# =========================================================
# 7. FIGURES
# =========================================================

# FC strength
plot_top_hubs(
    fc_young_df,
    fc_old_df,
    metric="strength",
    title="Hubs de connectivité (Strength) FC",
    color="#30b7d4",
    save_path=output_dir / "FC_strength.png"
)

# FC PC
plot_top_hubs(
    fc_young_df,
    fc_old_df,
    metric="participation_coefficient",
    title="Hubs d'intégration (Participation Coefficient) FC",
    color="#f27a1a",
    save_path=output_dir / "FC_pc.png"
)

# SC strength
plot_top_hubs(
    sc_young_df,
    sc_old_df,
    metric="strength",
    title="Hubs de connectivité (Strength) SC",
    color="#30b7d4",
    save_path=output_dir / "SC_strength.png"
)

# SC PC
plot_top_hubs(
    sc_young_df,
    sc_old_df,
    metric="participation_coefficient",
    title="Hubs d'intégration (Participation Coefficient) SC",
    color="#f27a1a",
    save_path=output_dir / "SC_pc.png"
)

print("Terminé : figures et tableaux de hubs générés avec les noms de régions depuis le CSV.")