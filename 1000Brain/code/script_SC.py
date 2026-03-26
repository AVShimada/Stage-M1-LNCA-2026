import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# =========================================================
# 1. PARAMÈTRES
# =========================================================
base_path = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa")
fc_base = base_path / "FC"
sc_base = base_path / "SC"

# CSV issu de ton script PCA
pca_csv = Path(r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_PCA_cognition\15_dataframe_complet_avec_scores_PCA.csv")

# Fichier démographique
demo_csv = base_path / "demographic_data.csv"   # adapte le nom exact si besoin

# Dossier de sortie
output_dir = Path(r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_connectome")
output_dir.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

# =========================================================
# 2. FONCTIONS UTILES
# =========================================================
def load_matrix_auto(file_path: Path):
    """
    Essaie de charger automatiquement une matrice à partir d'un fichier.
    Compatible avec .txt, .csv, .tsv, fichiers sans extension, et .npy
    """
    try:
        if file_path.suffix.lower() == ".npy":
            mat = np.load(file_path)
            return np.array(mat, dtype=float)

        # Essai 1 : séparateur whitespace
        try:
            mat = np.loadtxt(file_path)
            if mat.ndim == 2:
                return np.array(mat, dtype=float)
        except:
            pass

        # Essai 2 : tabulation
        try:
            mat = pd.read_csv(file_path, sep="\t", header=None).values
            if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
                return np.array(mat, dtype=float)
        except:
            pass

        # Essai 3 : point-virgule
        try:
            mat = pd.read_csv(file_path, sep=";", header=None).values
            if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
                return np.array(mat, dtype=float)
        except:
            pass

        # Essai 4 : virgule
        try:
            mat = pd.read_csv(file_path, sep=",", header=None).values
            if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
                return np.array(mat, dtype=float)
        except:
            pass

    except Exception as e:
        print(f"Impossible de charger {file_path}: {e}")

    return None


def clean_connectome_matrix(mat):
    """
    Nettoyage minimal d'une matrice de connectivité.
    """
    mat = np.array(mat, dtype=float)

    # Remplace NaN/inf
    mat[~np.isfinite(mat)] = np.nan
    mat = np.nan_to_num(mat, nan=0.0, posinf=0.0, neginf=0.0)

    # Si matrice carrée, on met la diagonale à 0
    if mat.ndim == 2 and mat.shape[0] == mat.shape[1]:
        np.fill_diagonal(mat, 0)

    return mat


def compute_connectome_metrics(mat, prefix="FC"):
    """
    Calcule des métriques simples sur une matrice de connectivité.
    """
    mat = clean_connectome_matrix(mat)

    # Utilise le triangle supérieur pour éviter de doubler les connexions
    if mat.shape[0] == mat.shape[1]:
        upper = mat[np.triu_indices_from(mat, k=1)]
    else:
        upper = mat.flatten()

    upper = upper[np.isfinite(upper)]

    if len(upper) == 0:
        return {
            f"{prefix}_mean": np.nan,
            f"{prefix}_std": np.nan,
            f"{prefix}_median": np.nan,
            f"{prefix}_sum": np.nan,
            f"{prefix}_abs_mean": np.nan,
            f"{prefix}_nonzero_fraction": np.nan,
        }

    metrics = {
        f"{prefix}_mean": float(np.mean(upper)),
        f"{prefix}_std": float(np.std(upper)),
        f"{prefix}_median": float(np.median(upper)),
        f"{prefix}_sum": float(np.sum(upper)),
        f"{prefix}_abs_mean": float(np.mean(np.abs(upper))),
        f"{prefix}_nonzero_fraction": float(np.mean(upper != 0)),
    }

    # Degree / strength moyen
    if mat.shape[0] == mat.shape[1]:
        strength = mat.sum(axis=1)
        metrics[f"{prefix}_mean_strength"] = float(np.mean(strength))
        metrics[f"{prefix}_std_strength"] = float(np.std(strength))
    else:
        metrics[f"{prefix}_mean_strength"] = np.nan
        metrics[f"{prefix}_std_strength"] = np.nan

    return metrics


def find_fc_file(subject_id: int, session="ses-1", atlas="Schaefer_100_7NW"):
    """
    Cherche le fichier FC pour un sujet/session/atlas.
    """
    sub_str = f"sub-{subject_id:04d}"
    folder = fc_base / sub_str / session / "FC" / atlas

    if not folder.exists():
        return None

    files = [f for f in folder.iterdir() if f.is_file()]
    if len(files) == 0:
        return None

    # Priorité aux fichiers les plus plausibles
    preferred = sorted(files, key=lambda x: (x.suffix == "", x.suffix))
    return preferred[0]


def find_sc_file(subject_id: int, session="ses-1", parcels="100", use_sift2=True, use_log=True):
    """
    Cherche le fichier SC le plus pertinent.
    Par défaut : 100 parcels + sift2 + CM_log
    """
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


def plot_and_save_regression(df, x, y, save_path, hue=None, title=None):
    """
    Scatter + droite de tendance
    Force x et y en numérique pour éviter les erreurs de type.
    """
    cols = [x, y] + ([hue] if hue else [])
    plot_df = df[cols].copy()

    # conversion explicite en numérique
    plot_df[x] = pd.to_numeric(plot_df[x], errors="coerce")
    plot_df[y] = pd.to_numeric(plot_df[y], errors="coerce")

    # suppression des lignes invalides
    plot_df = plot_df.dropna(subset=[x, y])

    if plot_df.empty:
        print(f"Figure ignorée pour {x} vs {y} : aucune donnée exploitable.")
        return

    print(f"{x} dtype ->", plot_df[x].dtype)
    print(f"{y} dtype ->", plot_df[y].dtype)

    plt.figure(figsize=(7, 5))

    if hue:
        sns.scatterplot(data=plot_df, x=x, y=y, hue=hue, alpha=0.7)
    else:
        sns.scatterplot(data=plot_df, x=x, y=y, alpha=0.7)

    sns.regplot(data=plot_df, x=x, y=y, scatter=False, ci=95)

    plt.title(title if title else f"{y} en fonction de {x}")
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.show()
    plt.close()

# =========================================================
# 3. CHARGER LE CSV PCA
# =========================================================
df = pd.read_csv(pca_csv)
df.columns = df.columns.str.strip()

print("Colonnes PCA :", df.columns.tolist()[:20], "...")
print("Taille df PCA :", df.shape)

# Harmoniser id
if "ID" in df.columns and "id" not in df.columns:
    df = df.rename(columns={"ID": "id"})

df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")

# =========================================================
# 4. CHARGER LE FICHIER DÉMOGRAPHIQUE
# =========================================================
df_demo = pd.read_csv(demo_csv, sep=";", na_values=["na", "NA", "NULL"])
df_demo.columns = df_demo.columns.str.strip()

print("Colonnes df_demo :", df_demo.columns.tolist())
print(df_demo.head())

# Convertir sub-0001 -> 1
df_demo["id_bids"] = df_demo["id"]
df_demo["id"] = df_demo["id"].str.replace("sub-", "", regex=False)
df_demo["id"] = pd.to_numeric(df_demo["id"], errors="coerce").astype("Int64")

# =========================================================
# 5. MERGE PCA + DÉMOGRAPHIE
# =========================================================
df_merged = df.merge(df_demo, on="id", how="inner")

print("Taille après merge :", df_merged.shape)

# Nettoyage du sexe si doublons
if "Sex_x" in df_merged.columns and "Sex_y" in df_merged.columns:
    print("Concordance Sex_x / Sex_y :")
    print((df_merged["Sex_x"] == df_merged["Sex_y"]).value_counts(dropna=False))
    df_merged = df_merged.drop(columns=["Sex_y"]).rename(columns={"Sex_x": "Sex"})
elif "Sex_x" in df_merged.columns:
    df_merged = df_merged.rename(columns={"Sex_x": "Sex"})
elif "Sex_y" in df_merged.columns:
    df_merged = df_merged.rename(columns={"Sex_y": "Sex"})

# =========================================================
# 6. EXTRACTION DES MÉTRIQUES FC
# =========================================================
fc_results = []

subjects_fc = df_merged.loc[df_merged["FC_ses1"] == "YES", "id"].dropna().astype(int).tolist()
print("Nombre de sujets avec FC ses-1 :", len(subjects_fc))

for sub in subjects_fc:
    fc_file = find_fc_file(sub, session="ses-1", atlas="Schaefer_100_7NW")

    if fc_file is None:
        print(f"FC non trouvé pour sub-{sub:04d}")
        continue

    mat = load_matrix_auto(fc_file)
    if mat is None:
        print(f"FC illisible pour sub-{sub:04d} : {fc_file}")
        continue

    metrics = compute_connectome_metrics(mat, prefix="FC")
    metrics["id"] = sub
    metrics["FC_file"] = str(fc_file)
    fc_results.append(metrics)

df_fc = pd.DataFrame(fc_results)
df_fc.to_csv(output_dir / "01_fc_metrics.csv", index=False)

print("Taille df_fc :", df_fc.shape)

# =========================================================
# 7. EXTRACTION DES MÉTRIQUES SC
# =========================================================
sc_results = []

subjects_sc = df_merged.loc[df_merged["SC_ses_1"] == "YES", "id"].dropna().astype(int).tolist()
print("Nombre de sujets avec SC ses-1 :", len(subjects_sc))

for sub in subjects_sc:
    sc_file = find_sc_file(sub, session="ses-1", parcels="100", use_sift2=True, use_log=True)

    if sc_file is None:
        print(f"SC non trouvé pour sub-{sub:04d}")
        continue

    mat = load_matrix_auto(sc_file)
    if mat is None:
        print(f"SC illisible pour sub-{sub:04d} : {sc_file}")
        continue

    metrics = compute_connectome_metrics(mat, prefix="SC")
    metrics["id"] = sub
    metrics["SC_file"] = str(sc_file)
    sc_results.append(metrics)

df_sc = pd.DataFrame(sc_results)
df_sc.to_csv(output_dir / "02_sc_metrics.csv", index=False)

print("Taille df_sc :", df_sc.shape)

# =========================================================
# 8. MERGE FINAL
# =========================================================
df_final = df_merged.merge(df_fc, on="id", how="left")
df_final = df_final.merge(df_sc, on="id", how="left")

df_final.to_csv(output_dir / "03_dataframe_cognition_connectome.csv", index=False)

# Remplacer les marqueurs texte de valeurs manquantes
df_final = df_final.replace(["#NV", "na", "NA", "NULL", ""], np.nan)

# Colonnes à convertir en numérique
numeric_candidates = [
    "PC1", "PC2", "PC3",
    "FC_mean", "FC_std", "FC_median", "FC_sum", "FC_abs_mean",
    "FC_nonzero_fraction", "FC_mean_strength", "FC_std_strength",
    "SC_mean", "SC_std", "SC_median", "SC_sum", "SC_abs_mean",
    "SC_nonzero_fraction", "SC_mean_strength", "SC_std_strength",
    "Age", "Age_ses-1", "Age_ses-2",
    "ISCED_97", "ISCED_ses-1"
]

for col in numeric_candidates:
    if col in df_final.columns:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce")
        
# =========================================================
# 9. FIGURES PRINCIPALES
# =========================================================
# PC1 vs FC
plot_and_save_regression(
    df_final,
    x="PC1",
    y="FC_mean",
    hue="age_group" if "age_group" in df_final.columns else None,
    title="FC_mean en fonction de PC1",
    save_path=output_dir / "04_PC1_vs_FC_mean.png"
)

# PC1 vs SC
plot_and_save_regression(
    df_final,
    x="PC1",
    y="SC_mean",
    hue="age_group" if "age_group" in df_final.columns else None,
    title="SC_mean en fonction de PC1",
    save_path=output_dir / "05_PC1_vs_SC_mean.png"
)

# Age vs FC
age_col = "Age_ses-1" if "Age_ses-1" in df_final.columns else "Age"
plot_and_save_regression(
    df_final,
    x=age_col,
    y="FC_mean",
    hue="Sex" if "Sex" in df_final.columns else None,
    title="FC_mean en fonction de l'âge",
    save_path=output_dir / "06_Age_vs_FC_mean.png"
)

# Age vs SC
plot_and_save_regression(
    df_final,
    x=age_col,
    y="SC_mean",
    hue="Sex" if "Sex" in df_final.columns else None,
    title="SC_mean en fonction de l'âge",
    save_path=output_dir / "07_Age_vs_SC_mean.png"
)

# FC vs SC
plot_and_save_regression(
    df_final,
    x="FC_mean",
    y="SC_mean",
    hue="age_group" if "age_group" in df_final.columns else None,
    title="SC_mean en fonction de FC_mean",
    save_path=output_dir / "08_FC_mean_vs_SC_mean.png"
)

# =========================================================
# 10. CORRÉLATIONS NUMÉRIQUES
# =========================================================
numeric_cols_for_corr = [
    col for col in [
        "PC1", "PC2", "PC3",
        "FC_mean", "FC_std", "FC_abs_mean", "FC_mean_strength",
        "SC_mean", "SC_std", "SC_abs_mean", "SC_mean_strength",
        "Age", "Age_ses-1", "ISCED_97", "ISCED_ses-1"
    ]
    if col in df_final.columns
]

corr_input = df_final[numeric_cols_for_corr].apply(pd.to_numeric, errors="coerce")
corr_df = corr_input.corr()

corr_df.to_csv(output_dir / "09_correlations.csv")

plt.figure(figsize=(10, 8))
sns.heatmap(corr_df, cmap="coolwarm", center=0, annot=True, fmt=".2f")
plt.title("Corrélations cognition / connectome / âge / éducation")
plt.tight_layout()
plt.savefig(output_dir / "10_heatmap_correlations.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================================================
# 11. TABLEAU RÉSUMÉ
# =========================================================
summary = {
    "n_total_merge": len(df_merged),
    "n_fc_available_demo": len(subjects_fc),
    "n_sc_available_demo": len(subjects_sc),
    "n_fc_loaded": len(df_fc),
    "n_sc_loaded": len(df_sc),
    "n_final_with_any_connectome": len(df_final[(df_final["FC_mean"].notna()) | (df_final["SC_mean"].notna())]),
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv(output_dir / "11_summary_counts.csv", index=False)

print("\nRésumé :")
print(summary_df.T)

print(f"\nTous les résultats ont été enregistrés dans : {output_dir}")