import pandas as pd
from pathlib import Path
from nilearn import datasets
from nilearn.plotting import find_parcellation_cut_coords

# =========================================================
# 1. PARAMÈTRES
# =========================================================
output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\atlas_coordinates"
)
output_dir.mkdir(parents=True, exist_ok=True)

# =========================================================
# 2. TÉLÉCHARGER L'ATLAS SCHAEFER 100 / 7 NETWORKS
# =========================================================
atlas = datasets.fetch_atlas_schaefer_2018(
    n_rois=100,
    yeo_networks=7,
    resolution_mm=1
)

# =========================================================
# 3. CALCULER LES COORDONNÉES DES CENTROÏDES
# =========================================================
coords = find_parcellation_cut_coords(labels_img=atlas.maps)

# =========================================================
# 4. RÉCUPÉRER LES LABELS
# =========================================================
labels = [lab.decode("utf-8") if isinstance(lab, bytes) else str(lab) for lab in atlas.labels]

# Souvent le premier label = Background
if len(labels) == len(coords) + 1:
    labels = labels[1:]

if len(labels) != len(coords):
    raise ValueError(
        f"Nombre de labels ({len(labels)}) différent du nombre de coordonnées ({len(coords)})."
    )

# =========================================================
# 5. SAUVEGARDE CSV
# =========================================================
coords_df = pd.DataFrame(coords, columns=["x", "y", "z"])
coords_df.insert(0, "node_index", range(len(coords_df)))
coords_df["label"] = labels

coords_csv = output_dir / "Schaefer_100_7Networks_coordinates.csv"
coords_df.to_csv(coords_csv, index=False)

print("Coordonnées sauvegardées dans :")
print(coords_csv)
print(coords_df.head())