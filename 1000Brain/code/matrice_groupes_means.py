import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# 1. PARAMÈTRES
# =========================================================
base_path = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa")
fc_base = base_path / "FC"
sc_base = base_path / "SC"

# CSV final issu de ton script précédent
merged_csv = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_connectome\03_dataframe_cognition_connectome.csv"
)

output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_group_average_matrices"
)
output_dir.mkdir(parents=True, exist_ok=True)

# Choix atlas
fc_atlas = "Schaefer_100_7NW"
sc_parcels = "100"   # "100" ou "400"

# Pour SC, on prend la version recommandée
use_sift2 = True
use_log = True

# =========================================================
# 2. FONCTIONS
# =========================================================
def load_matrix_auto(file_path: Path):
    """
    Charge automatiquement une matrice depuis différents formats possibles.
    """
    try:
        if file_path.suffix.lower() == ".npy":
            return np.array(np.load(file_path), dtype=float)

        # whitespace
        try:
            mat = np.loadtxt(file_path)
            if mat.ndim == 2:
                return np.array(mat, dtype=float)
        except:
            pass

        # tab
        try:
            mat = pd.read_csv(file_path, sep="\t", header=None).values
            if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
                return np.array(mat, dtype=float)
        except:
            pass

        # semicolon
        try:
            mat = pd.read_csv(file_path, sep=";", header=None).values
            if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
                return np.array(mat, dtype=float)
        except:
            pass

        # comma
        try:
            mat = pd.read_csv(file_path, sep=",", header=None).values
            if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
                return np.array(mat, dtype=float)
        except:
            pass

    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")

    return None


def clean_matrix(mat):
    """
    Nettoyage minimal.
    """
    mat = np.array(mat, dtype=float)
    mat[~np.isfinite(mat)] = np.nan
    mat = np.nan_to_num(mat, nan=0.0, posinf=0.0, neginf=0.0)

    if mat.ndim == 2 and mat.shape[0] == mat.shape[1]:
        np.fill_diagonal(mat, 0)

    return mat


def find_fc_file(subject_id: int, session="ses-1", atlas="Schaefer_100_7NW"):
    sub_str = f"sub-{subject_id:04d}"
    folder = fc_base / sub_str / session / "FC" / atlas

    if not folder.exists():
        return None

    files = [f for f in folder.iterdir() if f.is_file()]
    if len(files) == 0:
        return None

    return files[0]


def find_sc_file(subject_id: int, session="ses-1", parcels="100", use_sift2=True, use_log=True):
    sub_str = f"sub-{subject_id:04d}"
    folder = sc_base / sub_str / session / "SC"

    if not folder.exists():
        return None

    files = [f for f in folder.iterdir() if f.is_file()]
    if len(files) == 0:
        return None

    candidates = []
    for f in files:
        name = f.name
        cond_parcels = f"desc-{parcels}Parcels7Networks" in name
        cond_sift2 = ("sift2" in name) if use_sift2 else True
        cond_log = ("CM_log" in name) if use_log else ("CM" in name)

        if cond_parcels and cond_sift2 and cond_log:
            candidates.append(f)

    if len(candidates) == 0:
        return None

    return candidates[0]


def compute_group_average_matrix(subject_ids, modality="FC"):
    """
    Calcule la matrice moyenne pour une liste de sujets.
    modality = "FC" ou "SC"
    """
    matrices = []
    failed_subjects = []

    for sub in subject_ids:
        try:
            if modality == "FC":
                file_path = find_fc_file(sub, session="ses-1", atlas=fc_atlas)
            elif modality == "SC":
                file_path = find_sc_file(
                    sub,
                    session="ses-1",
                    parcels=sc_parcels,
                    use_sift2=use_sift2,
                    use_log=use_log
                )
            else:
                raise ValueError("modality doit être 'FC' ou 'SC'")

            if file_path is None:
                failed_subjects.append(sub)
                continue

            mat = load_matrix_auto(file_path)
            if mat is None:
                failed_subjects.append(sub)
                continue

            mat = clean_matrix(mat)
            matrices.append(mat)

        except Exception as e:
            print(f"Erreur {modality} sub-{sub:04d}: {e}")
            failed_subjects.append(sub)

    if len(matrices) == 0:
        return None, [], failed_subjects

    stacked = np.stack(matrices, axis=0)
    mean_mat = np.mean(stacked, axis=0)

    return mean_mat, matrices, failed_subjects


def save_matrix_outputs(mat, base_name):
    """
    Sauvegarde matrice en .npy et .csv
    """
    np.save(output_dir / f"{base_name}.npy", mat)
    pd.DataFrame(mat).to_csv(output_dir / f"{base_name}.csv", index=False, header=False)


def plot_matrix(ax, mat, title, vmin=None, vmax=None, cmap="viridis"):
    im = ax.imshow(mat, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Nœuds")
    ax.set_ylabel("Nœuds")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


# =========================================================
# 3. CHARGER LE DATAFRAME FINAL
# =========================================================
df = pd.read_csv(merged_csv, na_values=["#NV", "na", "NA", "NULL", ""])
df.columns = df.columns.str.strip()

# Harmoniser types
if "id" in df.columns:
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")

if "Age" in df.columns:
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

if "Age_ses-1" in df.columns:
    df["Age_ses-1"] = pd.to_numeric(df["Age_ses-1"], errors="coerce")

# reconstruire age_group si absent
if "age_group" not in df.columns:
    if "Age" in df.columns:
        df["age_group"] = df["Age"].apply(lambda x: "<55" if x < 55 else ">=55")
    elif "Age_ses-1" in df.columns:
        df["age_group"] = df["Age_ses-1"].apply(lambda x: "<55" if x < 55 else ">=55")

print("Taille dataframe :", df.shape)
print(df["age_group"].value_counts(dropna=False))

# =========================================================
# 4. LISTES DE SUJETS PAR GROUPE
# =========================================================
young_fc = df.loc[
    (df["age_group"] == "<55") & (df["FC_ses1"] == "YES"),
    "id"
].dropna().astype(int).tolist()

old_fc = df.loc[
    (df["age_group"] == ">=55") & (df["FC_ses1"] == "YES"),
    "id"
].dropna().astype(int).tolist()

young_sc = df.loc[
    (df["age_group"] == "<55") & (df["SC_ses_1"] == "YES"),
    "id"
].dropna().astype(int).tolist()

old_sc = df.loc[
    (df["age_group"] == ">=55") & (df["SC_ses_1"] == "YES"),
    "id"
].dropna().astype(int).tolist()

print(f"Sujets FC <55 : {len(young_fc)}")
print(f"Sujets FC >=55 : {len(old_fc)}")
print(f"Sujets SC <55 : {len(young_sc)}")
print(f"Sujets SC >=55 : {len(old_sc)}")

# =========================================================
# 5. CALCUL DES MATRICES MOYENNES
# =========================================================
fc_young_mean, fc_young_mats, fc_young_failed = compute_group_average_matrix(young_fc, modality="FC")
fc_old_mean, fc_old_mats, fc_old_failed = compute_group_average_matrix(old_fc, modality="FC")

sc_young_mean, sc_young_mats, sc_young_failed = compute_group_average_matrix(young_sc, modality="SC")
sc_old_mean, sc_old_mats, sc_old_failed = compute_group_average_matrix(old_sc, modality="SC")

# =========================================================
# 6. SAUVEGARDE DES MATRICES
# =========================================================
if fc_young_mean is not None:
    save_matrix_outputs(fc_young_mean, "FC_mean_young_lt55")
if fc_old_mean is not None:
    save_matrix_outputs(fc_old_mean, "FC_mean_old_ge55")
if sc_young_mean is not None:
    save_matrix_outputs(sc_young_mean, "SC_mean_young_lt55")
if sc_old_mean is not None:
    save_matrix_outputs(sc_old_mean, "SC_mean_old_ge55")

# différences
if fc_young_mean is not None and fc_old_mean is not None:
    fc_diff = fc_old_mean - fc_young_mean
    save_matrix_outputs(fc_diff, "FC_difference_old_minus_young")

if sc_young_mean is not None and sc_old_mean is not None:
    sc_diff = sc_old_mean - sc_young_mean
    save_matrix_outputs(sc_diff, "SC_difference_old_minus_young")

# =========================================================
# 7. FIGURE PRINCIPALE 2x2
# =========================================================
# échelles communes par modalité
fc_all = [m for m in [fc_young_mean, fc_old_mean] if m is not None]
sc_all = [m for m in [sc_young_mean, sc_old_mean] if m is not None]

fc_vmin = min(np.min(m) for m in fc_all) if fc_all else None
fc_vmax = max(np.max(m) for m in fc_all) if fc_all else None

sc_vmin = min(np.min(m) for m in sc_all) if sc_all else None
sc_vmax = max(np.max(m) for m in sc_all) if sc_all else None

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

if fc_young_mean is not None:
    plot_matrix(
        axes[0, 0],
        fc_young_mean,
        f"FC moyenne - <55 (n={len(fc_young_mats)})",
        vmin=fc_vmin,
        vmax=fc_vmax,
        cmap="coolwarm"
    )
else:
    axes[0, 0].set_title("FC moyenne - <55 indisponible")
    axes[0, 0].axis("off")

if fc_old_mean is not None:
    plot_matrix(
        axes[0, 1],
        fc_old_mean,
        f"FC moyenne - >=55 (n={len(fc_old_mats)})",
        vmin=fc_vmin,
        vmax=fc_vmax,
        cmap="coolwarm"
    )
else:
    axes[0, 1].set_title("FC moyenne - >=55 indisponible")
    axes[0, 1].axis("off")

if sc_young_mean is not None:
    plot_matrix(
        axes[1, 0],
        sc_young_mean,
        f"SC moyenne - <55 (n={len(sc_young_mats)})",
        vmin=sc_vmin,
        vmax=sc_vmax,
        cmap="viridis"
    )
else:
    axes[1, 0].set_title("SC moyenne - <55 indisponible")
    axes[1, 0].axis("off")

if sc_old_mean is not None:
    plot_matrix(
        axes[1, 1],
        sc_old_mean,
        f"SC moyenne - >=55 (n={len(sc_old_mats)})",
        vmin=sc_vmin,
        vmax=sc_vmax,
        cmap="viridis"
    )
else:
    axes[1, 1].set_title("SC moyenne - >=55 indisponible")
    axes[1, 1].axis("off")

plt.suptitle("Matrices moyennes FC et SC par groupe d'âge", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(output_dir / "group_average_matrices_FC_SC.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================================================
# 8. FIGURE DES DIFFÉRENCES
# =========================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

if fc_young_mean is not None and fc_old_mean is not None:
    fc_diff = fc_old_mean - fc_young_mean
    vmax_fc_diff = np.max(np.abs(fc_diff))
    plot_matrix(
        axes[0],
        fc_diff,
        "Différence FC : >=55 - <55",
        vmin=-vmax_fc_diff,
        vmax=vmax_fc_diff,
        cmap="bwr"
    )
else:
    axes[0].set_title("Différence FC indisponible")
    axes[0].axis("off")

if sc_young_mean is not None and sc_old_mean is not None:
    sc_diff = sc_old_mean - sc_young_mean
    vmax_sc_diff = np.max(np.abs(sc_diff))
    plot_matrix(
        axes[1],
        sc_diff,
        "Différence SC : >=55 - <55",
        vmin=-vmax_sc_diff,
        vmax=vmax_sc_diff,
        cmap="bwr"
    )
else:
    axes[1].set_title("Différence SC indisponible")
    axes[1].axis("off")

plt.suptitle("Différences entre groupes d'âge", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_dir / "group_difference_matrices_FC_SC.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================================================
# 9. RÉSUMÉ
# =========================================================
summary = pd.DataFrame([{
    "n_young_fc_requested": len(young_fc),
    "n_old_fc_requested": len(old_fc),
    "n_young_sc_requested": len(young_sc),
    "n_old_sc_requested": len(old_sc),
    "n_young_fc_loaded": len(fc_young_mats) if fc_young_mean is not None else 0,
    "n_old_fc_loaded": len(fc_old_mats) if fc_old_mean is not None else 0,
    "n_young_sc_loaded": len(sc_young_mats) if sc_young_mean is not None else 0,
    "n_old_sc_loaded": len(sc_old_mats) if sc_old_mean is not None else 0,
    "n_young_fc_failed": len(fc_young_failed),
    "n_old_fc_failed": len(fc_old_failed),
    "n_young_sc_failed": len(sc_young_failed),
    "n_old_sc_failed": len(sc_old_failed),
}])

summary.to_csv(output_dir / "summary_group_average_matrices.csv", index=False)

print("\nRésumé :")
print(summary.T)

print(f"\nTous les résultats ont été enregistrés dans : {output_dir}")

import networkx as nx
import community as community_louvain

def get_module_boundaries(sorted_module_labels):
    boundaries = []
    for i in range(1, len(sorted_module_labels)):
        if sorted_module_labels[i] != sorted_module_labels[i - 1]:
            boundaries.append(i - 0.5)
    return boundaries

def plot_sorted_matrix(ax, mat, sorted_idx, sorted_module_labels, title, vmin=None, vmax=None, cmap="viridis"):
    mat_sorted = mat[np.ix_(sorted_idx, sorted_idx)]

    im = ax.imshow(mat_sorted, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Nœuds triés par module")
    ax.set_ylabel("Nœuds triés par module")

    boundaries = get_module_boundaries(sorted_module_labels)
    for b in boundaries:
        ax.axhline(b, color="white", linestyle=":", linewidth=1)
        ax.axvline(b, color="white", linestyle=":", linewidth=1)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

def louvain_labels_from_matrix(mat, modality="FC", resolution=1.3):
    mat = np.array(mat, dtype=float).copy()
    np.fill_diagonal(mat, 0)

    if modality == "FC":
        mat[mat < 0] = 0

    mat[~np.isfinite(mat)] = 0
    G = nx.from_numpy_array(mat)

    part = community_louvain.best_partition(
        G,
        weight="weight",
        resolution=resolution,
        random_state=None
    )

    n_nodes = mat.shape[0]
    return np.array([part[i] for i in range(n_nodes)], dtype=int)

def agreement_matrix_from_partitions(partitions):
    partitions = np.asarray(partitions)
    n_runs, n_nodes = partitions.shape
    agreement = np.zeros((n_nodes, n_nodes), dtype=float)

    for r in range(n_runs):
        labels = partitions[r]
        same_module = labels[:, None] == labels[None, :]
        agreement += same_module.astype(float)

    agreement /= n_runs
    return agreement

def relabel_consecutive(labels):
    unique_vals = np.unique(labels)
    mapping = {old: new for new, old in enumerate(unique_vals)}
    return np.array([mapping[x] for x in labels], dtype=int)

def consensus_louvain(mat, modality="FC", resolution=1.3, n_runs=200, threshold=0.5):
    mat = np.array(mat, dtype=float).copy()
    np.fill_diagonal(mat, 0)

    if modality == "FC":
        mat[mat < 0] = 0

    mat[~np.isfinite(mat)] = 0
    n_nodes = mat.shape[0]

    partitions = []
    for _ in range(n_runs):
        labels = louvain_labels_from_matrix(mat, modality=modality, resolution=resolution)
        partitions.append(labels)
    partitions = np.array(partitions)

    agreement = agreement_matrix_from_partitions(partitions)

    agreement_thr = agreement.copy()
    agreement_thr[agreement_thr < threshold] = 0
    np.fill_diagonal(agreement_thr, 0)

    G_consensus = nx.from_numpy_array(agreement_thr)
    final_part = community_louvain.best_partition(
        G_consensus,
        weight="weight",
        resolution=1.0,
        random_state=42
    )

    final_labels = np.array([final_part[i] for i in range(n_nodes)], dtype=int)
    final_labels = relabel_consecutive(final_labels)

    sorted_idx = np.argsort(final_labels)
    sorted_labels = final_labels[sorted_idx]
    partition_dict = {i: int(final_labels[i]) for i in range(n_nodes)}

    return partition_dict, sorted_idx, sorted_labels, agreement, agreement_thr, partitions

# Référence pour le tri modulaire
if fc_young_mean is not None:
    ref_mat = fc_young_mean
    ref_modality = "FC"
    ref_name = "FC <55"
elif fc_old_mean is not None:
    ref_mat = fc_old_mean
    ref_modality = "FC"
    ref_name = "FC >=55"
elif sc_young_mean is not None:
    ref_mat = sc_young_mean
    ref_modality = "SC"
    ref_name = "SC <55"
elif sc_old_mean is not None:
    ref_mat = sc_old_mean
    ref_modality = "SC"
    ref_name = "SC >=55"
else:
    raise ValueError("Aucune matrice disponible pour la détection modulaire.")

partition_dict, sorted_idx, sorted_module_labels, agreement, agreement_thr, partitions = consensus_louvain(
    ref_mat,
    modality=ref_modality,
    resolution=1.3,
    n_runs=200,
    threshold=0.5
)

n_modules = len(np.unique(sorted_module_labels))
print(f"\nRéférence modulaire utilisée : {ref_name}")
print(f"Nombre de modules détectés : {n_modules}")

# Sauvegardes
np.save(output_dir / "agreement_matrix.npy", agreement)
pd.DataFrame(agreement).to_csv(output_dir / "agreement_matrix.csv", index=False, header=False)

np.save(output_dir / "agreement_thresholded.npy", agreement_thr)
pd.DataFrame(agreement_thr).to_csv(output_dir / "agreement_thresholded.csv", index=False, header=False)

pd.DataFrame(partitions).to_csv(output_dir / "partitions_all_runs.csv", index=False)

module_order_sorted_df = pd.DataFrame({
    "sorted_position": np.arange(len(sorted_idx)),
    "original_node_index": sorted_idx,
    "module": sorted_module_labels
})
module_order_sorted_df.to_csv(output_dir / "module_order_sorted.csv", index=False)

# Figures triées
fc_all_sorted = [m for m in [fc_young_mean, fc_old_mean] if m is not None]
sc_all_sorted = [m for m in [sc_young_mean, sc_old_mean] if m is not None]

fc_vmin_sorted = min(np.min(m) for m in fc_all_sorted) if fc_all_sorted else None
fc_vmax_sorted = max(np.max(m) for m in fc_all_sorted) if fc_all_sorted else None

sc_vmin_sorted = min(np.min(m) for m in sc_all_sorted) if sc_all_sorted else None
sc_vmax_sorted = max(np.max(m) for m in sc_all_sorted) if sc_all_sorted else None

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

if fc_young_mean is not None:
    plot_sorted_matrix(axes[0, 0], fc_young_mean, sorted_idx, sorted_module_labels,
                       f"FC moyenne - <55 triée par module (n={len(fc_young_mats)})",
                       vmin=fc_vmin_sorted, vmax=fc_vmax_sorted, cmap="coolwarm")
else:
    axes[0, 0].axis("off")

if fc_old_mean is not None:
    plot_sorted_matrix(axes[0, 1], fc_old_mean, sorted_idx, sorted_module_labels,
                       f"FC moyenne - >=55 triée par module (n={len(fc_old_mats)})",
                       vmin=fc_vmin_sorted, vmax=fc_vmax_sorted, cmap="coolwarm")
else:
    axes[0, 1].axis("off")

if sc_young_mean is not None:
    plot_sorted_matrix(axes[1, 0], sc_young_mean, sorted_idx, sorted_module_labels,
                       f"SC moyenne - <55 triée par module (n={len(sc_young_mats)})",
                       vmin=sc_vmin_sorted, vmax=sc_vmax_sorted, cmap="viridis")
else:
    axes[1, 0].axis("off")

if sc_old_mean is not None:
    plot_sorted_matrix(axes[1, 1], sc_old_mean, sorted_idx, sorted_module_labels,
                       f"SC moyenne - >=55 triée par module (n={len(sc_old_mats)})",
                       vmin=sc_vmin_sorted, vmax=sc_vmax_sorted, cmap="viridis")
else:
    axes[1, 1].axis("off")

plt.suptitle(f"Matrices moyennes FC et SC triées par module (référence : {ref_name})", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(output_dir / "group_average_matrices_FC_SC_sorted_by_modules.png", bbox_inches="tight")
plt.show()
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

if fc_diff is not None:
    vmax_fc_diff = np.max(np.abs(fc_diff))
    plot_sorted_matrix(axes[0], fc_diff, sorted_idx, sorted_module_labels,
                       "Différence FC : >=55 - <55 (triée par module)",
                       vmin=-vmax_fc_diff, vmax=vmax_fc_diff, cmap="bwr")
else:
    axes[0].axis("off")

if sc_diff is not None:
    vmax_sc_diff = np.max(np.abs(sc_diff))
    plot_sorted_matrix(axes[1], sc_diff, sorted_idx, sorted_module_labels,
                       "Différence SC : >=55 - <55 (triée par module)",
                       vmin=-vmax_sc_diff, vmax=vmax_sc_diff, cmap="bwr")
else:
    axes[1].axis("off")

plt.suptitle(f"Différences entre groupes d'âge triées par module (référence : {ref_name})", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_dir / "group_difference_matrices_FC_SC_sorted_by_modules.png", bbox_inches="tight")
plt.show()
plt.close()