import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import networkx as nx
import community as community_louvain

# =========================================================
# 1. PARAMÈTRES
# =========================================================
input_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_group_average_matrices"
)

output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_consensus_partition"
)
output_dir.mkdir(parents=True, exist_ok=True)

# Fichiers des matrices moyennes
fc_young_file = input_dir / "FC_mean_young_lt55.npy"
fc_old_file   = input_dir / "FC_mean_old_ge55.npy"

sc_young_file = input_dir / "SC_mean_young_lt55.npy"
sc_old_file   = input_dir / "SC_mean_old_ge55.npy"

# Paramètres Louvain / consensus
n_runs = 100
resolution_fc = 1.3
resolution_sc = 1.3
consensus_threshold = 0.5
random_state_consensus = 42

# Colormaps
cmap_matrix = "turbo"
cmap_agreement = "viridis"

# =========================================================
# 2. FONCTIONS
# =========================================================
def clean_matrix(mat, zero_diag=True):
    mat = np.array(mat, dtype=float)
    mat[~np.isfinite(mat)] = 0.0
    if zero_diag and mat.ndim == 2 and mat.shape[0] == mat.shape[1]:
        np.fill_diagonal(mat, 0.0)
    return mat


def prepare_matrix_for_louvain(mat, modality="FC"):
    mat = np.array(mat, dtype=float).copy()
    mat[~np.isfinite(mat)] = 0.0
    np.fill_diagonal(mat, 0.0)

    if modality.upper() == "FC":
        mat[mat < 0] = 0.0
    elif modality.upper() == "SC":
        mat[mat < 0] = 0.0
    else:
        raise ValueError("modality doit être 'FC' ou 'SC'")

    return mat


def louvain_one_run(mat, resolution=1.0, random_state=None):
    G = nx.from_numpy_array(mat)

    partition = community_louvain.best_partition(
        G,
        weight="weight",
        resolution=resolution,
        random_state=random_state
    )

    n_nodes = mat.shape[0]
    labels = np.array([partition[i] for i in range(n_nodes)], dtype=int)
    return labels


def relabel_consecutive(labels):
    unique_vals = np.unique(labels)
    mapping = {old: new for new, old in enumerate(unique_vals)}
    return np.array([mapping[x] for x in labels], dtype=int)


def run_louvain_multiple_times(mat, n_runs=100, resolution=1.0):
    partitions = []
    for _ in range(n_runs):
        labels = louvain_one_run(mat, resolution=resolution, random_state=None)
        labels = relabel_consecutive(labels)
        partitions.append(labels)

    return np.array(partitions)


def agreement_matrix_from_partitions(partitions):
    partitions = np.asarray(partitions)
    n_runs, n_nodes = partitions.shape
    agreement = np.zeros((n_nodes, n_nodes), dtype=float)

    for r in range(n_runs):
        labels = partitions[r]
        same_module = (labels[:, None] == labels[None, :]).astype(float)
        agreement += same_module

    agreement /= n_runs
    return agreement


def consensus_partition_from_agreement(agreement, threshold=0.5, random_state=42):
    agreement_thr = agreement.copy()
    agreement_thr[agreement_thr < threshold] = 0.0
    np.fill_diagonal(agreement_thr, 0.0)

    G = nx.from_numpy_array(agreement_thr)

    partition = community_louvain.best_partition(
        G,
        weight="weight",
        resolution=1.0,
        random_state=random_state
    )

    n_nodes = agreement_thr.shape[0]
    labels = np.array([partition[i] for i in range(n_nodes)], dtype=int)
    labels = relabel_consecutive(labels)

    return labels, agreement_thr


def consensus_partition_from_agreement_no_threshold(agreement, random_state=42):
    agreement_full = agreement.copy()
    np.fill_diagonal(agreement_full, 0.0)

    G = nx.from_numpy_array(agreement_full)

    partition = community_louvain.best_partition(
        G,
        weight="weight",
        resolution=1.0,
        random_state=random_state
    )

    n_nodes = agreement_full.shape[0]
    labels = np.array([partition[i] for i in range(n_nodes)], dtype=int)
    labels = relabel_consecutive(labels)

    return labels, agreement_full


def sort_nodes_by_partition(labels):
    sorted_idx = np.argsort(labels)
    sorted_labels = labels[sorted_idx]
    return sorted_idx, sorted_labels


def get_module_boundaries(sorted_labels):
    boundaries = []
    for i in range(1, len(sorted_labels)):
        if sorted_labels[i] != sorted_labels[i - 1]:
            boundaries.append(i - 0.5)
    return boundaries


def plot_matrix(ax, mat, title, cmap="viridis", vmin=None, vmax=None, show_colorbar=True):
    im = ax.imshow(mat, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Nœuds")
    ax.set_ylabel("Nœuds")
    if show_colorbar:
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return im


def plot_sorted_matrix(ax, mat, sorted_idx, sorted_labels, title,
                       cmap="viridis", vmin=None, vmax=None, line_color="white"):
    mat_sorted = mat[np.ix_(sorted_idx, sorted_idx)]
    im = ax.imshow(mat_sorted, cmap=cmap, vmin=vmin, vmax=vmax)

    ax.set_title(title)
    ax.set_xlabel("Nœuds triés par communauté")
    ax.set_ylabel("Nœuds triés par communauté")

    boundaries = get_module_boundaries(sorted_labels)
    for b in boundaries:
        ax.axhline(b, color=line_color, linestyle=":", linewidth=1)
        ax.axvline(b, color=line_color, linestyle=":", linewidth=1)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return im


def plot_partition_figure_like_example(partitions, consensus_labels, title_prefix="FC", save_path=None):
    partitions = np.asarray(partitions)
    consensus_labels = np.asarray(consensus_labels)

    vmin = min(np.min(partitions), np.min(consensus_labels))
    vmax = max(np.max(partitions), np.max(consensus_labels))

    plt.style.use("dark_background")

    fig, axes = plt.subplots(
        2, 1,
        figsize=(18, 9),
        gridspec_kw={"height_ratios": [4, 1]}
    )

    im1 = axes[0].imshow(
        partitions,
        aspect="auto",
        interpolation="nearest",
        cmap="turbo",
        vmin=vmin,
        vmax=vmax
    )
    axes[0].set_title(f"{title_prefix} - Partitions de tous les runs", fontsize=16)
    axes[0].set_ylabel("Runs", fontsize=13)
    axes[0].set_xticks([])
    fig.colorbar(im1, ax=axes[0], fraction=0.02, pad=0.01)

    im2 = axes[1].imshow(
        consensus_labels[np.newaxis, :],
        aspect="auto",
        interpolation="nearest",
        cmap="turbo",
        vmin=vmin,
        vmax=vmax
    )
    axes[1].set_title(f"{title_prefix} - Partition Consensus", fontsize=16)
    axes[1].set_xlabel("Nœuds", fontsize=13)
    axes[1].set_yticks([])
    fig.colorbar(im2, ax=axes[1], fraction=0.02, pad=0.01)

    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close(fig)


def save_partition_outputs(prefix, mat, partitions, agreement, agreement_thr,
                           consensus_labels, sorted_idx,
                           agreement_no_thr=None, consensus_labels_no_thr=None, sorted_idx_no_thr=None):
    np.save(output_dir / f"{prefix}_input_matrix.npy", mat)
    pd.DataFrame(mat).to_csv(output_dir / f"{prefix}_input_matrix.csv", index=False, header=False)

    np.save(output_dir / f"{prefix}_all_partitions.npy", partitions)
    pd.DataFrame(partitions).to_csv(output_dir / f"{prefix}_all_partitions.csv", index=False)

    np.save(output_dir / f"{prefix}_agreement_matrix.npy", agreement)
    pd.DataFrame(agreement).to_csv(output_dir / f"{prefix}_agreement_matrix.csv", index=False, header=False)

    np.save(output_dir / f"{prefix}_agreement_thresholded.npy", agreement_thr)
    pd.DataFrame(agreement_thr).to_csv(output_dir / f"{prefix}_agreement_thresholded.csv", index=False, header=False)

    consensus_df = pd.DataFrame({
        "node_index": np.arange(len(consensus_labels)),
        "consensus_module": consensus_labels
    })
    consensus_df.to_csv(output_dir / f"{prefix}_consensus_labels.csv", index=False)

    sorted_df = pd.DataFrame({
        "sorted_position": np.arange(len(sorted_idx)),
        "original_node_index": sorted_idx,
        "consensus_module": consensus_labels[sorted_idx]
    })
    sorted_df.to_csv(output_dir / f"{prefix}_sorted_nodes_by_consensus.csv", index=False)

    if agreement_no_thr is not None:
        np.save(output_dir / f"{prefix}_agreement_no_threshold.npy", agreement_no_thr)
        pd.DataFrame(agreement_no_thr).to_csv(
            output_dir / f"{prefix}_agreement_no_threshold.csv",
            index=False,
            header=False
        )

    if consensus_labels_no_thr is not None:
        consensus_no_thr_df = pd.DataFrame({
            "node_index": np.arange(len(consensus_labels_no_thr)),
            "consensus_module_no_threshold": consensus_labels_no_thr
        })
        consensus_no_thr_df.to_csv(
            output_dir / f"{prefix}_consensus_labels_no_threshold.csv",
            index=False
        )

    if sorted_idx_no_thr is not None and consensus_labels_no_thr is not None:
        sorted_no_thr_df = pd.DataFrame({
            "sorted_position": np.arange(len(sorted_idx_no_thr)),
            "original_node_index": sorted_idx_no_thr,
            "consensus_module_no_threshold": consensus_labels_no_thr[sorted_idx_no_thr]
        })
        sorted_no_thr_df.to_csv(
            output_dir / f"{prefix}_sorted_nodes_by_consensus_no_threshold.csv",
            index=False
        )


def process_modality(mat, modality="FC", n_runs=100, resolution=1.3, threshold=0.5):
    mat_clean = clean_matrix(mat, zero_diag=True)
    mat_ready = prepare_matrix_for_louvain(mat_clean, modality=modality)

    partitions = run_louvain_multiple_times(
        mat_ready,
        n_runs=n_runs,
        resolution=resolution
    )

    agreement = agreement_matrix_from_partitions(partitions)

    consensus_labels_thr, agreement_thr = consensus_partition_from_agreement(
        agreement,
        threshold=threshold,
        random_state=random_state_consensus
    )

    sorted_idx_thr, sorted_labels_thr = sort_nodes_by_partition(consensus_labels_thr)

    consensus_labels_no_thr, agreement_full = consensus_partition_from_agreement_no_threshold(
        agreement,
        random_state=random_state_consensus
    )

    sorted_idx_no_thr, sorted_labels_no_thr = sort_nodes_by_partition(consensus_labels_no_thr)

    return {
        "mat_clean": mat_clean,
        "mat_ready": mat_ready,
        "partitions": partitions,
        "agreement": agreement,
        "agreement_thr": agreement_thr,
        "consensus_labels": consensus_labels_thr,
        "sorted_idx": sorted_idx_thr,
        "sorted_labels": sorted_labels_thr,
        "n_modules": len(np.unique(consensus_labels_thr)),
        "agreement_no_thr": agreement_full,
        "consensus_labels_no_thr": consensus_labels_no_thr,
        "sorted_idx_no_thr": sorted_idx_no_thr,
        "sorted_labels_no_thr": sorted_labels_no_thr,
        "n_modules_no_thr": len(np.unique(consensus_labels_no_thr))
    }


# =========================================================
# 3. CHARGEMENT DES 4 MATRICES
# =========================================================
matrices = {
    "FC_young": (fc_young_file, "FC", resolution_fc),
    "FC_old":   (fc_old_file,   "FC", resolution_fc),
    "SC_young": (sc_young_file, "SC", resolution_sc),
    "SC_old":   (sc_old_file,   "SC", resolution_sc),
}

results = {}

for name, (file_path, modality, resolution) in matrices.items():
    if not file_path.exists():
        print(f"[absent] {file_path}")
        continue

    mat = np.load(file_path)
    print(f"{name} chargé : {file_path}")

    res = process_modality(
        mat,
        modality=modality,
        n_runs=n_runs,
        resolution=resolution,
        threshold=consensus_threshold
    )
    results[name] = res

    save_partition_outputs(
        prefix=name,
        mat=res["mat_clean"],
        partitions=res["partitions"],
        agreement=res["agreement"],
        agreement_thr=res["agreement_thr"],
        consensus_labels=res["consensus_labels"],
        sorted_idx=res["sorted_idx"],
        agreement_no_thr=res["agreement_no_thr"],
        consensus_labels_no_thr=res["consensus_labels_no_thr"],
        sorted_idx_no_thr=res["sorted_idx_no_thr"]
    )

    print(f"{name} : {res['n_modules']} communautés consensus détectées avec threshold")
    print(f"{name} : {res['n_modules_no_thr']} communautés consensus détectées sans threshold")


# =========================================================
# 4. FIGURES INDIVIDUELLES
# =========================================================
titles = {
    "FC_young": "FC <55",
    "FC_old": "FC >=55",
    "SC_young": "SC <55",
    "SC_old": "SC >=55",
}

for name, res in results.items():
    modality_title = titles[name]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    plot_matrix(
        axes[0],
        res["mat_clean"],
        f"{modality_title} moyenne",
        cmap=cmap_matrix
    )

    plot_matrix(
        axes[1],
        res["agreement"],
        f"{modality_title} matrice d'accord ({n_runs} runs)",
        cmap=cmap_agreement,
        vmin=0,
        vmax=1
    )

    plot_sorted_matrix(
        axes[2],
        res["mat_clean"],
        res["sorted_idx"],
        res["sorted_labels"],
        f"{modality_title} triée par partition consensus\n({res['n_modules']} communautés)",
        cmap=cmap_matrix
    )

    fig.suptitle(f"Partition consensus - {modality_title}", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output_dir / f"{name}_consensus_partition_summary.png", bbox_inches="tight")
    plt.show()
    plt.close(fig)


# =========================================================
# 5. FIGURES PARTITIONS + CONSENSUS
# =========================================================
for name, res in results.items():
    modality_title = titles[name]

    plot_partition_figure_like_example(
        partitions=res["partitions"],
        consensus_labels=res["consensus_labels"],
        title_prefix=modality_title,
        save_path=output_dir / f"{name}_partitions_consensus.png"
    )

    plot_partition_figure_like_example(
        partitions=res["partitions"],
        consensus_labels=res["consensus_labels_no_thr"],
        title_prefix=f"{modality_title} sans threshold",
        save_path=output_dir / f"{name}_partitions_consensus_no_threshold.png"
    )


# =========================================================
# 6. CSV SANKEY
# =========================================================
if "FC_young" in results and "FC_old" in results:
    pd.DataFrame({
        "<55": results["FC_young"]["consensus_labels"],
        ">=55": results["FC_old"]["consensus_labels"]
    }).to_csv(output_dir / "sankey_data_FC_MEANS.csv", index=False)

if "SC_young" in results and "SC_old" in results:
    pd.DataFrame({
        "<55": results["SC_young"]["consensus_labels"],
        ">=55": results["SC_old"]["consensus_labels"]
    }).to_csv(output_dir / "sankey_data_SC_MEANS.csv", index=False)

print("\nCSV Sankey créés si les deux groupes étaient disponibles.")


# =========================================================
# 7. RÉSUMÉ
# =========================================================
summary_rows = []
for name, res in results.items():
    summary_rows.append({
        "dataset": name,
        "n_nodes": res["mat_clean"].shape[0],
        "n_runs": n_runs,
        "resolution": resolution_fc if "FC" in name else resolution_sc,
        "consensus_threshold": consensus_threshold,
        "n_consensus_modules_threshold": res["n_modules"],
        "n_consensus_modules_no_threshold": res["n_modules_no_thr"]
    })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(output_dir / "summary_consensus_partition.csv", index=False)

print("\nRésumé :")
print(summary_df)

print(f"\nTous les résultats ont été enregistrés dans : {output_dir}")