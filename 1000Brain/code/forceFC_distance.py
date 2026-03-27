import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.spatial.distance import pdist, squareform

# =========================================================
# 1. PARAMÈTRES
# =========================================================
input_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_group_average_matrices"
)

output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_fc_distance"
)
output_dir.mkdir(parents=True, exist_ok=True)

# Matrices FC moyennes
fc_young_file = input_dir / "FC_mean_young_lt55.npy"
fc_old_file   = input_dir / "FC_mean_old_ge55.npy"

# Coordonnées des nœuds / ROI
coords_file = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\atlas_coordinates\Schaefer_100_7Networks_coordinates.csv"
)

# Paramètres du binning
n_bins = 8
use_absolute_fc = False   # True si tu veux |FC| au lieu de FC positive seulement

# =========================================================
# 2. FONCTIONS
# =========================================================
def clean_fc_matrix(mat, use_absolute=False):
    mat = np.array(mat, dtype=float).copy()
    mat[~np.isfinite(mat)] = np.nan
    np.fill_diagonal(mat, np.nan)

    if use_absolute:
        mat = np.abs(mat)
    else:
        # on garde seulement les corrélations positives
        mat[mat < 0] = np.nan

    return mat


def load_coordinates(coords_csv):
    df = pd.read_csv(coords_csv)

    required_cols = ["x", "y", "z"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Colonne '{col}' absente dans {coords_csv}")

    coords = df[required_cols].to_numpy(dtype=float)
    return coords


def compute_distance_matrix(coords):
    return squareform(pdist(coords, metric="euclidean"))


def upper_triangle_values(mat):
    iu = np.triu_indices_from(mat, k=1)
    return mat[iu]


def compute_fc_distance_profile(fc_mat, dist_mat, n_bins=8):
    fc_vals = upper_triangle_values(fc_mat)
    dist_vals = upper_triangle_values(dist_mat)

    valid = np.isfinite(fc_vals) & np.isfinite(dist_vals)
    fc_vals = fc_vals[valid]
    dist_vals = dist_vals[valid]

    if len(fc_vals) == 0:
        raise ValueError("Aucune valeur valide après filtrage.")

    bin_edges = np.linspace(dist_vals.min(), dist_vals.max(), n_bins + 1)

    bin_centers = []
    fc_means = []
    fc_stds = []
    fc_sems = []
    counts = []

    for i in range(n_bins):
        left = bin_edges[i]
        right = bin_edges[i + 1]

        if i < n_bins - 1:
            mask = (dist_vals >= left) & (dist_vals < right)
        else:
            mask = (dist_vals >= left) & (dist_vals <= right)

        fc_bin = fc_vals[mask]
        dist_bin = dist_vals[mask]

        if len(fc_bin) == 0:
            bin_centers.append((left + right) / 2)
            fc_means.append(np.nan)
            fc_stds.append(np.nan)
            fc_sems.append(np.nan)
            counts.append(0)
        else:
            bin_centers.append(np.mean(dist_bin))
            fc_means.append(np.mean(fc_bin))
            fc_stds.append(np.std(fc_bin, ddof=1) if len(fc_bin) > 1 else 0.0)
            fc_sems.append(
                (np.std(fc_bin, ddof=1) / np.sqrt(len(fc_bin))) if len(fc_bin) > 1 else 0.0
            )
            counts.append(len(fc_bin))

    return pd.DataFrame({
        "bin_center_mm": bin_centers,
        "fc_mean": fc_means,
        "fc_std": fc_stds,
        "fc_sem": fc_sems,
        "n_edges": counts
    })


def plot_fc_vs_distance(profile_young, profile_old, save_path=None):
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.errorbar(
        profile_young["bin_center_mm"],
        profile_young["fc_mean"],
        yerr=profile_young["fc_sem"],
        fmt="o-",
        linewidth=2.5,
        markersize=8,
        capsize=5,
        label="<55"
    )

    ax.errorbar(
        profile_old["bin_center_mm"],
        profile_old["fc_mean"],
        yerr=profile_old["fc_sem"],
        fmt="o-",
        linewidth=2.5,
        markersize=8,
        capsize=5,
        label=">=55"
    )

    ax.set_title("Décroissance de la FC en fonction de la distance", fontsize=18)
    ax.set_xlabel("Distance Euclidienne (mm)", fontsize=14)
    ax.set_ylabel("Force de Connectivité moyenne (FC)", fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.15)

    plt.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close(fig)

# =========================================================
# 3. CHARGEMENT DES DONNÉES
# =========================================================
if not fc_young_file.exists():
    raise FileNotFoundError(f"Fichier introuvable : {fc_young_file}")

if not fc_old_file.exists():
    raise FileNotFoundError(f"Fichier introuvable : {fc_old_file}")

if not coords_file.exists():
    raise FileNotFoundError(f"Fichier introuvable : {coords_file}")

fc_young = np.load(fc_young_file)
fc_old = np.load(fc_old_file)

coords = load_coordinates(coords_file)

if fc_young.shape[0] != coords.shape[0]:
    raise ValueError(
        f"Nombre de nœuds incohérent : FC young = {fc_young.shape[0]}, coords = {coords.shape[0]}"
    )

if fc_old.shape[0] != coords.shape[0]:
    raise ValueError(
        f"Nombre de nœuds incohérent : FC old = {fc_old.shape[0]}, coords = {coords.shape[0]}"
    )

# =========================================================
# 4. MATRICE DE DISTANCE
# =========================================================
dist_mat = compute_distance_matrix(coords)

# =========================================================
# 5. PROFILS FC ~ DISTANCE
# =========================================================
fc_young_clean = clean_fc_matrix(fc_young, use_absolute=use_absolute_fc)
fc_old_clean = clean_fc_matrix(fc_old, use_absolute=use_absolute_fc)

profile_young = compute_fc_distance_profile(fc_young_clean, dist_mat, n_bins=n_bins)
profile_old = compute_fc_distance_profile(fc_old_clean, dist_mat, n_bins=n_bins)

# Sauvegardes CSV
profile_young.to_csv(output_dir / "FC_distance_profile_young_lt55.csv", index=False)
profile_old.to_csv(output_dir / "FC_distance_profile_old_ge55.csv", index=False)

# =========================================================
# 6. FIGURE
# =========================================================
plot_fc_vs_distance(
    profile_young,
    profile_old,
    save_path=output_dir / "FC_vs_distance_two_age_groups.png"
)

print("\nProfils sauvegardés dans :")
print(output_dir / "FC_distance_profile_young_lt55.csv")
print(output_dir / "FC_distance_profile_old_ge55.csv")
print(output_dir / "FC_vs_distance_two_age_groups.png")