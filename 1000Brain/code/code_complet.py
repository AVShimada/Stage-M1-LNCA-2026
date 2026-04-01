import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# =========================================================
# 1. PARAMÈTRES
# =========================================================
input_file = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\Cognition\V1\data\1000Brains_NP_VarOI_V1_Pseudo.xlsx")
output_dir = Path(r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_PCA_cognition")
output_dir.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

# =========================================================
# 2. IMPORT DES DONNÉES
# =========================================================
df = pd.read_excel(input_file, na_values=["NULL"])

# =========================================================
# 3. NETTOYAGE DE BASE
# =========================================================
# On retire les sujets sans âge
df = df.dropna(subset=["Age"]).copy()

# Groupe d'âge
df["age_group"] = df["Age"].apply(lambda x: "<55" if x < 55 else ">=55")

# Disponibilité AKT avant correction
df["AKT_available_before_cleaning"] = df["AKT_TRW_SelectiveAttention"].notna()

# Correction protocolaire :
# AKT réservé aux sujets >=55
df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"] = np.nan

# Disponibilité AKT après correction
df["AKT_available"] = df["AKT_TRW_SelectiveAttention"].notna()

# Encodage du sexe pour quelques figures éventuelles
df["Sex_num"] = df["Sex"].map({"Male": 0, "Female": 1})

print("=== Vérifications après nettoyage ===")
print("\nNombre de sujets :", len(df))
print("\nRépartition par groupe d'âge :")
print(df["age_group"].value_counts())
print("\nAKT par groupe d'âge :")
print(df.groupby("age_group")["AKT_TRW_SelectiveAttention"].count())
print("\nAKT restant chez les sujets <55 :")
print(df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"].notna().sum())
print("\nValeurs manquantes par colonne :")
print(df.isna().sum())

# =========================================================
# 4. VARIABLES POUR LA PCA
# =========================================================
# ISCED_97 est laissé hors PCA par défaut
pca_cols = [
    "LPS_RRW_ProblemSolving",
    "AKT_TRW_SelectiveAttention",
    "Stroop_T3T2_Interference",
    "RWD_5_Punkte_FiguralFluency",
    "TMT_ARW_ProcessingSpeed",
    "TMT_BA_ConceptShifting",
    "BEN_RRW_FiguralMemory",
    "CBT_RVW_VisualSpatialWM_fw",
    "CBT_RRW_VisualSpatialWM_bw",
    "VPT_RW_VisualMemory",
    "ZNS_AVW_digitspan_fw",
    "ZNS_ARW_digitspan_bw",
    "RWT_PB2RW_PhonematicFluency",
    "RWT_SB2RW_SemanticFluency",
    "RWT_PGR2RW_PhonematicFluency_Switch",
    "RWT_SSF2RW_SemanticFluency_Switch",
    "AWST03P_Vocabulary",
    "BKW_1_5_VerbalMemory",
    "BKW_RWfv",
]

# Vérification que toutes les colonnes existent
missing_cols = [col for col in pca_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"Colonnes absentes du fichier : {missing_cols}")

X = df[pca_cols].copy()

# =========================================================
# 5. IMPUTATION DES VALEURS MANQUANTES
# =========================================================
imputer = SimpleImputer(strategy="mean")
X_imputed = pd.DataFrame(
    imputer.fit_transform(X),
    columns=X.columns,
    index=X.index
)

# Sauvegarde de la matrice imputée
X_imputed.to_csv(output_dir / "01_matrice_cognitive_imputee.csv", index=True)

# =========================================================
# 6. STANDARDISATION
# =========================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

X_scaled_df = pd.DataFrame(
    X_scaled,
    columns=X.columns,
    index=X.index
)
X_scaled_df.to_csv(output_dir / "02_matrice_cognitive_standardisee.csv", index=True)

# =========================================================
# 7. PCA
# =========================================================
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

# Scores PCA
scores_pca = pd.DataFrame(
    X_pca,
    columns=[f"PC{i+1}" for i in range(X_pca.shape[1])],
    index=df.index
)

# On ajoute les infos sujet
scores_pca.insert(0, "ID", df["ID"].values)
scores_pca.insert(1, "Age", df["Age"].values)
scores_pca.insert(2, "Sex", df["Sex"].values)
scores_pca.insert(3, "age_group", df["age_group"].values)

scores_pca.to_csv(output_dir / "03_scores_PCA_sujets.csv", index=False)

# =========================================================
# 8. VARIANCE EXPLIQUÉE
# =========================================================
explained_variance_ratio = pca.explained_variance_ratio_
explained_variance_df = pd.DataFrame({
    "Component": [f"PC{i+1}" for i in range(len(explained_variance_ratio))],
    "Explained_Variance_Ratio": explained_variance_ratio,
    "Cumulative_Explained_Variance": np.cumsum(explained_variance_ratio)
})

explained_variance_df.to_csv(output_dir / "04_variance_expliquee.csv", index=False)

print("\n=== Variance expliquée ===")
print(explained_variance_df.head(10))

# Scree plot
plt.figure(figsize=(8, 5))
plt.plot(
    range(1, len(explained_variance_ratio) + 1),
    explained_variance_ratio,
    marker="o"
)
plt.xlabel("Composante principale")
plt.ylabel("Proportion de variance expliquée")
plt.title("Scree plot")
plt.tight_layout()
plt.savefig(output_dir / "05_scree_plot.png", bbox_inches="tight")
plt.show()
plt.close()

# Variance cumulée
plt.figure(figsize=(8, 5))
plt.plot(
    range(1, len(explained_variance_ratio) + 1),
    np.cumsum(explained_variance_ratio),
    marker="o"
)
plt.xlabel("Nombre de composantes")
plt.ylabel("Variance expliquée cumulée")
plt.title("Variance expliquée cumulée")
plt.ylim(0, 1.05)
plt.tight_layout()
plt.savefig(output_dir / "06_variance_cumulee.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================================================
# 9. LOADINGS / CONTRIBUTIONS DES VARIABLES
# =========================================================
loadings = pd.DataFrame(
    pca.components_.T,
    columns=[f"PC{i+1}" for i in range(len(pca_cols))],
    index=pca_cols
)

loadings.to_csv(output_dir / "05_loadings_variables.csv")

print("\n=== Loadings PC1 et PC2 ===")
print(loadings[["PC1", "PC2"]].sort_values(by="PC1", ascending=False))

# Heatmap des loadings pour les 5 premières composantes
n_components_to_plot = 5
plt.figure(figsize=(10, 8))
sns.heatmap(
    loadings.iloc[:, :n_components_to_plot],
    annot=True,
    fmt=".2f",
    center=0,
    cmap="coolwarm"
)
plt.title(f"Loadings des {n_components_to_plot} premières composantes")
plt.tight_layout()
plt.savefig(output_dir / "07_heatmap_loadings_PC1_PC5.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================================================
# 10. PROJECTION DES SUJETS DANS L'ESPACE PCA
# =========================================================
# PC1 vs PC2 coloré par groupe d'âge
plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=scores_pca,
    x="PC1",
    y="PC2",
    hue="age_group",
    alpha=0.7
)
plt.title("Projection des sujets : PC1 vs PC2")
plt.tight_layout()
plt.savefig(output_dir / "08_projection_PC1_PC2_agegroup.png", bbox_inches="tight")
plt.show()
plt.close()

# PC1 vs PC2 coloré par sexe
plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=scores_pca,
    x="PC1",
    y="PC2",
    hue="Sex",
    alpha=0.7
)
plt.title("Projection des sujets : PC1 vs PC2 par sexe")
plt.tight_layout()
plt.savefig(output_dir / "09_projection_PC1_PC2_sex.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================================================
# 11. RELATION ENTRE COMPOSANTES ET ÂGE
# =========================================================
for pc in ["PC1", "PC2", "PC3"]:
    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=scores_pca, x="Age", y=pc, hue="age_group", alpha=0.6)
    sns.regplot(data=scores_pca, x="Age", y=pc, scatter=False, ci=95)
    plt.title(f"{pc} en fonction de l'âge")
    plt.tight_layout()
    plt.savefig(output_dir / f"10_{pc}_vs_Age.png", bbox_inches="tight")
    plt.show()
    plt.close()

# =========================================================
# 12. CERCLE DES CORRÉLATIONS (PC1-PC2)
# =========================================================
# top 10 variables les plus importantes
top_vars = loadings["PC1"].abs().sort_values(ascending=False).head(10).index

plt.figure(figsize=(8,8))

circle = plt.Circle((0, 0), 1, color="gray", fill=False)
plt.gca().add_patch(circle)

for var in top_vars:
    x = loadings.loc[var, "PC1"]
    y = loadings.loc[var, "PC2"]
    
    plt.arrow(0, 0, x, y, head_width=0.03, alpha=0.7)
    plt.text(x*1.15, y*1.15, var, fontsize=10)

plt.axhline(0, color="black")
plt.axvline(0, color="black")
plt.xlim(-1.1, 1.1)
plt.ylim(-1.1, 1.1)
plt.title("Cercle des corrélations (Top variables PC1)")
plt.gca().set_aspect("equal")
plt.show()

# =========================================================
# 13. CONTRIBUTEURS PRINCIPAUX DE PC1 ET PC2
# =========================================================
pc1_sorted = loadings["PC1"].sort_values(key=np.abs, ascending=False)
pc2_sorted = loadings["PC2"].sort_values(key=np.abs, ascending=False)

print("\n=== Variables contribuant le plus à PC1 ===")
print(pc1_sorted.head(10))

print("\n=== Variables contribuant le plus à PC2 ===")
print(pc2_sorted.head(10))

pc1_sorted.head(10).to_csv(output_dir / "12_top10_PC1.csv")
pc2_sorted.head(10).to_csv(output_dir / "13_top10_PC2.csv")

# =========================================================
# 14. CORRÉLATION ENTRE PC ET ÂGE
# =========================================================
pc_age_corr = scores_pca[["Age", "PC1", "PC2", "PC3", "PC4", "PC5"]].corr()
pc_age_corr.to_csv(output_dir / "14_correlations_age_PC.csv")

print("\n=== Corrélations âge / composantes ===")
print(pc_age_corr.loc["Age", ["PC1", "PC2", "PC3", "PC4", "PC5"]])

# =========================================================
# 15. FICHIER FINAL COMPLET
# =========================================================
df_final = pd.concat([df.reset_index(drop=True), scores_pca.reset_index(drop=True)], axis=1)
df_final.to_csv(output_dir / "15_dataframe_complet_avec_scores_PCA.csv", index=False)

print(f"\nTous les résultats ont été enregistrés dans : {output_dir}")

# Renommer ID -> id pour faciliter le merge
df = df.rename(columns={"ID": "id"})

# S'assurer que id est entier
df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")

# =========================
# 2. Charger les données démographiques
# =========================
# Adapte read_csv / sep si besoin selon ton fichier réel
df_demo = pd.read_csv(
    r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\Demographic_data.csv",
    sep=";",
    na_values=["na", "NA", "NULL"]
)

# Nettoyage noms de colonnes
df_demo.columns = df_demo.columns.str.strip()

# Vérification
print("Colonnes df_demo :", df_demo.columns.tolist())
print(df_demo.head())

# =========================
# 3. Convertir id de type sub-0001 -> 1
# =========================
df_demo["id_bids"] = df_demo["id"]                  # garder une copie texte
df_demo["id"] = df_demo["id"].str.replace("sub-", "", regex=False)
df_demo["id"] = pd.to_numeric(df_demo["id"], errors="coerce").astype("Int64")

# =========================
# 4. Vérifier les IDs
# =========================
print(df_demo[["id_bids", "id"]].head())

# =========================
# 5. Merge
# =========================
df_merged = df.merge(df_demo, on="id", how="inner")

print("Taille cognition :", df.shape)
print("Taille demographic :", df_demo.shape)
print("Taille merge :", df_merged.shape)

print(df_merged[["id", "Sex_x", "Sex_y"]].head() if "Sex_x" in df_merged.columns else df_merged.head())

## CODE 2

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


def plot_matrix(ax, mat, title, vmin=None, vmax=None, cmap="turbo"):
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
        cmap="turbo"
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
        cmap="turbo"
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
        cmap="turbo"
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
        cmap="turbo"
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
        cmap="turbo"
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
        cmap="turbo"
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

def plot_sorted_matrix(ax, mat, sorted_idx, sorted_module_labels, title, vmin=None, vmax=None, cmap="turbo"):
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
                       vmin=fc_vmin_sorted, vmax=fc_vmax_sorted, cmap="turbo")
else:
    axes[0, 0].axis("off")

if fc_old_mean is not None:
    plot_sorted_matrix(axes[0, 1], fc_old_mean, sorted_idx, sorted_module_labels,
                       f"FC moyenne - >=55 triée par module (n={len(fc_old_mats)})",
                       vmin=fc_vmin_sorted, vmax=fc_vmax_sorted, cmap="turbo")
else:
    axes[0, 1].axis("off")

if sc_young_mean is not None:
    plot_sorted_matrix(axes[1, 0], sc_young_mean, sorted_idx, sorted_module_labels,
                       f"SC moyenne - <55 triée par module (n={len(sc_young_mats)})",
                       vmin=sc_vmin_sorted, vmax=sc_vmax_sorted, cmap="turbo")
else:
    axes[1, 0].axis("off")

if sc_old_mean is not None:
    plot_sorted_matrix(axes[1, 1], sc_old_mean, sorted_idx, sorted_module_labels,
                       f"SC moyenne - >=55 triée par module (n={len(sc_old_mats)})",
                       vmin=sc_vmin_sorted, vmax=sc_vmax_sorted, cmap="turbo")
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
                       vmin=-vmax_fc_diff, vmax=vmax_fc_diff, cmap="turbo")
else:
    axes[0].axis("off")

if sc_diff is not None:
    vmax_sc_diff = np.max(np.abs(sc_diff))
    plot_sorted_matrix(axes[1], sc_diff, sorted_idx, sorted_module_labels,
                       "Différence SC : >=55 - <55 (triée par module)",
                       vmin=-vmax_sc_diff, vmax=vmax_sc_diff, cmap="turbo")
else:
    axes[1].axis("off")

plt.suptitle(f"Différences entre groupes d'âge triées par module (référence : {ref_name})", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_dir / "group_difference_matrices_FC_SC_sorted_by_modules.png", bbox_inches="tight")
plt.show()
plt.close()

## CODE 3
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

## CODE 4
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

## CODE 5
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# FONCTION GÉNÉRALE POUR LE NOUVEAU DATASET
# =========================================================
def generate_sankey_data_2groups(df, col1="<55", col2=">=55"):
    sources = []
    targets = []
    values = []

    # Modules uniques par groupe
    g1_mods = sorted(df[col1].unique())
    g2_mods = sorted(df[col2].unique())

    # IDs uniques pour Plotly
    offset_g2 = len(g1_mods)

    g1_id_map = {mod: i for i, mod in enumerate(g1_mods)}
    g2_id_map = {mod: i + offset_g2 for i, mod in enumerate(g2_mods)}

    # Flux <55 -> >=55
    for m1 in g1_mods:
        for m2 in g2_mods:
            count = len(df[(df[col1] == m1) & (df[col2] == m2)])
            if count > 0:
                sources.append(g1_id_map[m1])
                targets.append(g2_id_map[m2])
                values.append(count)

    # Labels affichés sur les blocs
    labels = [f"{col1} - Mod {m}" for m in g1_mods] + \
             [f"{col2} - Mod {m}" for m in g2_mods]

    return labels, sources, targets, values


# =========================================================
# 1. SANKEY FC
# =========================================================
df_fc = pd.read_csv(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_consensus_partition\sankey_data_FC_MEANS.csv"
)

labels, sources, targets, values = generate_sankey_data_2groups(
    df_fc,
    col1="<55",
    col2=">=55"
)

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color="royalblue"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        hovertemplate='Transition: %{value} nœuds<extra></extra>'
    )
)])

fig.update_layout(
    title_text="Évolution de l'allégeance des nœuds FC moyens (<55 -> >=55)",
    font_size=12
)

fig.show()


# =========================================================
# 2. SANKEY SC
# =========================================================
df_sc = pd.read_csv(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_consensus_partition\sankey_data_SC_MEANS.csv"
)

labels, sources, targets, values = generate_sankey_data_2groups(
    df_sc,
    col1="<55",
    col2=">=55"
)

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color="seagreen"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        hovertemplate='Transition: %{value} nœuds<extra></extra>'
    )
)])

fig.update_layout(
    title_text="Évolution de l'allégeance des nœuds SC moyens (<55 -> >=55)",
    font_size=12
)

fig.show()

## CODE 6
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

## CODE 7
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

## CODE 8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import time
import gc

# =========================================================
# PARAMÈTRES
# =========================================================
FC_BASE = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\FC")

MERGED_CSV = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_connectome\03_dataframe_cognition_connectome.csv"
)

OUTPUT_DIR = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_dFC_matlab_like"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ATLAS = "100"
SESSION = "ses-1"

TR = 2
WINDOW = 10
LAG = 1

DEBUG = False
DEBUG_N_SUBJECTS = 20

DTYPE = np.float32

# =========================================================
# FONCTIONS
# =========================================================
def ts_to_fc(TS, format="2D"):
    TS = np.asarray(TS, dtype=DTYPE)
    n = TS.shape[1]

    FCm = np.corrcoef(TS, rowvar=False).astype(DTYPE)
    FCm = np.nan_to_num(FCm)

    il = np.tril_indices(n, k=-1)
    FCv = FCm[il]

    return FCv if format == "1D" else FCm


def ts_to_dfc_stream(TS, W, lag):
    TS = np.asarray(TS, dtype=DTYPE)
    t, n = TS.shape
    l = n * (n - 1) // 2

    kmax = ((t - W) // lag) + 1

    dFCstream = np.zeros((l, kmax), dtype=DTYPE)

    wstart = 0
    k = 0
    while (wstart + W) <= t:
        window_ts = TS[wstart:wstart + W, :]
        dFCstream[:, k] = ts_to_fc(window_ts, "1D")

        wstart += lag
        k += 1

    return dFCstream


def dfc_stream_to_dfc(dFCstream):
    dFC = np.corrcoef(dFCstream, rowvar=False).astype(DTYPE)
    dFC = np.nan_to_num(dFC)
    return dFC


# =========================================================
# CHARGEMENT CSV
# =========================================================
df = pd.read_csv(MERGED_CSV)
df.columns = df.columns.str.strip()

df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

df = df.dropna(subset=["id", "Age"])

df["age_group"] = pd.qcut(df["Age"], 3, labels=["Young", "Middle", "Old"])

df = df[df["FC_ses1"] == "YES"]

if DEBUG:
    df = df.head(DEBUG_N_SUBJECTS)

print("Nombre de sujets :", len(df))
print(df["age_group"].value_counts())


# =========================================================
# CHARGEMENT TS
# =========================================================
def find_ts_file(subject_id):
    sub = f"sub-{int(subject_id):04d}"
    folder = FC_BASE / sub / SESSION / "FC" / "Schaefer_100_7NW"

    if not folder.exists():
        return None

    for f in folder.iterdir():
        if "FC_TS_Schaefer_100P_7NW" in f.name and "TSdim" not in f.name:
            return f

    return None


subjects = []

for _, row in df.iterrows():
    sid = int(row["id"])
    file_path = find_ts_file(sid)

    if file_path is None:
        continue

    try:
        TS = np.loadtxt(file_path)
        TS = np.nan_to_num(TS)

        if TS.shape[0] < TS.shape[1]:
            TS = TS.T

        subjects.append({
            "id": sid,
            "age": row["Age"],
            "group": row["age_group"],
            "TS": TS
        })

    except:
        continue

print("Sujets chargés :", len(subjects))

# =========================================================
# FIXER LONGUEUR COMMUNE
# =========================================================
COMMON_TS_LENGTH = 290  # ajuste si besoin

subjects_fixed = []

for sub in subjects:
    if sub["TS"].shape[0] >= COMMON_TS_LENGTH:
        sub["TS"] = sub["TS"][:COMMON_TS_LENGTH, :]
        subjects_fixed.append(sub)

subjects = subjects_fixed

print("Sujets après homogénéisation :", len(subjects))

# =========================================================
# CALCUL dFC
# =========================================================
group_sums = {"Young": None, "Middle": None, "Old": None}
group_counts = {"Young": 0, "Middle": 0, "Old": 0}

times = []

for sub in subjects:
    TS = sub["TS"]

    t0 = time.perf_counter()

    dFCstream = ts_to_dfc_stream(TS, WINDOW, LAG)
    dFC = dfc_stream_to_dfc(dFCstream)

    dt = time.perf_counter() - t0
    times.append(dt)

    g = sub["group"]

    if group_sums[g] is None:
        group_sums[g] = dFC.copy()
    else:
        group_sums[g] += dFC

    group_counts[g] += 1

    print(f"Sujet {sub['id']} | fenêtres={dFC.shape[0]} | temps={dt:.3f}s")

    del dFCstream, dFC
    gc.collect()

print("\nTemps moyen :", np.mean(times))


# =========================================================
# MOYENNES
# =========================================================
results = {}

for g in group_sums:
    if group_counts[g] > 0:
        results[g] = group_sums[g] / group_counts[g]


# =========================================================
# PLOTS
# =========================================================
plt.style.use("dark_background")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, g in zip(axes, ["Young", "Middle", "Old"]):
    if g in results:
        mat = results[g]
        im = ax.imshow(mat, cmap="turbo", vmin=0, vmax=1)
        ax.set_title(f"{g} (n={group_counts[g]})")
        ax.set_aspect("equal")
        plt.colorbar(im, ax=ax)
    else:
        ax.axis("off")

plt.suptitle("FCD (Matlab-like, lag=W)", fontsize=16)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "mean_FCD_matlab_like.png", dpi=300)
plt.show()

## CODE 9
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import time
import gc

# =========================================================
# PARAMÈTRES
# =========================================================
BASE_PATH = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa")
FC_BASE = BASE_PATH / "FC"
DEMOGRAPHY_CSV = BASE_PATH / "Demographic_data.csv"

OUTPUT_DIR = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_MC_refined_dataset_matlab_like"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SESSION = "ses-1"
ATLAS_FOLDER = "Schaefer_100_7NW"
TS_SUFFIX = "_ses-1_FC_TS_Schaefer_100P_7NW_V1.txt"

TR = 2
WINDOW = round(20 / TR)   # = 10
LAG = 1

EXPECTED_TS_LENGTH = 296

DEBUG = False
DEBUG_N_SUBJECTS = 30

PLOT_EXAMPLE_SUBJECT = False
SAVE_SUBJECT_MC = False

DTYPE = np.float32


# =========================================================
# FONCTIONS
# =========================================================
def ts_to_fc(TS, format="2D"):
    """
    Équivalent TS2FC Matlab.
    TS : [temps x régions]
    """
    if format != "1D":
        format = "2D"

    TS = np.asarray(TS, dtype=DTYPE)
    n = TS.shape[1]

    FCm = np.corrcoef(TS, rowvar=False).astype(DTYPE, copy=False)
    FCm = np.nan_to_num(FCm, nan=0.0, posinf=0.0, neginf=0.0)

    il = np.tril_indices(n, k=-1)
    FCv = FCm[il]

    return FCv if format == "1D" else FCm


def ts_to_dfc_stream(TS, W, lag=None, format="2D"):
    """
    Équivalent TS2dFCstream Matlab.
    Format 2D : [n_links x n_windows]
    """
    if W is None:
        raise ValueError("Provide at least a window size.")
    if lag is None:
        lag = W
    if format is None:
        format = "2D"

    TS = np.asarray(TS, dtype=DTYPE)
    t, n = TS.shape
    l = n * (n - 1) // 2

    kmax = ((t - W) // lag) + 1

    if format == "3D":
        dFCstream = np.zeros((n, n, kmax), dtype=DTYPE)
    else:
        dFCstream = np.zeros((l, kmax), dtype=DTYPE)

    wstart = 0
    k = 0
    while (wstart + W) <= t:
        window_ts = TS[wstart:wstart + W, :]

        if format == "3D":
            dFCstream[:, :, k] = ts_to_fc(window_ts, format="2D")
        else:
            dFCstream[:, k] = ts_to_fc(window_ts, format="1D")

        wstart += lag
        k += 1

    return dFCstream


def matrix2vec_lower_tri(dfcstream_3d):
    """
    Convertit [n, n, F] -> [M, F] avec triangle inférieur.
    """
    n, _, F = dfcstream_3d.shape
    il = np.tril_indices(n, k=-1)
    out = np.zeros((len(il[0]), F), dtype=DTYPE)
    for k in range(F):
        out[:, k] = dfcstream_3d[:, :, k][il]
    return out


def build_stream_index_map(nregions):
    """
    Mappe chaque lien non orienté (i, j) avec i < j
    vers son index dans le stream.
    """
    pairs = []
    for i in range(1, nregions):
        for j in range(i):
            pairs.append((j, i))  # j < i
    stream_map = {pair: idx for idx, pair in enumerate(pairs)}
    return stream_map, pairs


def build_redundant_link_index_vector(nregions, stream_map):
    """
    Construit l'indexation des liens orientés (i,j), i != j,
    vers les liens non orientés du stream.
    Taille finale = nregions * (nregions - 1)
    """
    ordered_pairs = []
    for i in range(nregions):
        for j in range(nregions):
            if i != j:
                ordered_pairs.append((i, j))

    link_idx = np.array(
        [stream_map[(min(i, j), max(i, j))] for i, j in ordered_pairs],
        dtype=np.int32
    )
    return link_idx, ordered_pairs


def dfc_stream_to_mc_matlab_like(dFCstream, redundant=True, dtype=DTYPE):
    """
    Reproduction fidèle de dFCstream2MC.m

    Parameters
    ----------
    dFCstream : ndarray
        [M, F] ou [n, n, F]
    redundant : bool
        True  -> renvoie MC redondante [n(n-1), n(n-1)]
        False -> renvoie MCsmall [M, M]
    dtype : dtype
        np.float32 conseillé

    Returns
    -------
    MC : ndarray
    """
    if dFCstream.ndim == 3:
        FCstr = matrix2vec_lower_tri(dFCstream)
    elif dFCstream.ndim == 2:
        FCstr = np.asarray(dFCstream, dtype=dtype)
    else:
        raise ValueError("dFCstream doit être 2D ou 3D")

    M = FCstr.shape[0]

    nregions = int((1 + np.sqrt(1 + 8 * M)) / 2)
    if nregions * (nregions - 1) // 2 != M:
        raise ValueError("Impossible de déduire correctement le nombre de régions.")

    # MCsmall = corr(FCstr')
    MCsmall = np.corrcoef(FCstr).astype(dtype, copy=False)
    MCsmall = np.nan_to_num(MCsmall, nan=0.0, posinf=0.0, neginf=0.0)
    np.fill_diagonal(MCsmall, 1.0)

    if not redundant:
        return MCsmall

    # redistribution redondante Matlab-like
    stream_map, _ = build_stream_index_map(nregions)
    link_idx, _ = build_redundant_link_index_vector(nregions, stream_map)

    MC = MCsmall[np.ix_(link_idx, link_idx)].astype(dtype, copy=False)
    np.fill_diagonal(MC, 1.0)

    return MC


def compute_n_windows(ts_length, window, lag):
    if ts_length < window:
        return 0
    return ((ts_length - window) // lag) + 1


def load_matrix_auto(file_path: Path):
    suffix = file_path.suffix.lower()

    if suffix == ".npy":
        return np.array(np.load(file_path), dtype=DTYPE)

    try:
        mat = np.loadtxt(file_path)
        if mat.ndim == 2:
            return np.array(mat, dtype=DTYPE)
    except Exception:
        pass

    try:
        mat = pd.read_csv(file_path, sep="\t", header=None).values
        if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
            return np.array(mat, dtype=DTYPE)
    except Exception:
        pass

    try:
        mat = pd.read_csv(file_path, sep=",", header=None).values
        if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
            return np.array(mat, dtype=DTYPE)
    except Exception:
        pass

    try:
        mat = pd.read_csv(file_path, sep=";", header=None).values
        if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
            return np.array(mat, dtype=DTYPE)
    except Exception:
        pass

    raise ValueError(f"Impossible de lire le fichier : {file_path}")


def load_demography_refined():
    dem = pd.read_csv(DEMOGRAPHY_CSV, delimiter=";")
    demred = dem[["id", "Sex", "Age_ses-1", "ISCED_ses-1"]].copy()
    demog = demred.dropna().copy()
    demog["subject_id"] = demog["id"].apply(lambda s: int(str(s).split("-")[1]))
    demog = demog.drop_duplicates(subset="subject_id", keep="first").copy()
    return demog


def load_timeseries_refined():
    subjects = []

    for subj in range(1, 1315):
        sbj = str(subj).zfill(4)
        filepath = FC_BASE / f"sub-{sbj}" / SESSION / "FC" / ATLAS_FOLDER / f"sub-{sbj}{TS_SUFFIX}"

        if not filepath.exists():
            continue

        try:
            tseries = load_matrix_auto(filepath)
            tseries = np.nan_to_num(tseries, nan=0.0, posinf=0.0, neginf=0.0)

            if tseries.shape[0] < tseries.shape[1]:
                tseries = tseries.T

            if tseries.shape[0] == EXPECTED_TS_LENGTH:
                subjects.append({
                    "id": subj,
                    "TS": tseries,
                    "file_path": str(filepath),
                })

        except Exception as e:
            print(f"Erreur lecture sub-{sbj}: {e}")

    return subjects


# =========================================================
# CHARGEMENT DU DATASET RAFFINÉ
# =========================================================
demog = load_demography_refined()
ts_subjects = load_timeseries_refined()

df_ts = pd.DataFrame({
    "id": [s["id"] for s in ts_subjects],
    "TS": [s["TS"] for s in ts_subjects],
    "file_path": [s["file_path"] for s in ts_subjects],
})

print("Sujets avec TS V1 de longueur 296 :", len(df_ts))
print("Sujets démographie valides        :", len(demog))

df = demog.merge(df_ts, left_on="subject_id", right_on="id", how="inner").copy()

df["Age"] = pd.to_numeric(df["Age_ses-1"], errors="coerce")
df = df.dropna(subset=["Age"]).copy()

age_q = df["Age"].quantile([0, 1/3, 2/3, 1]).values

def assign_age_tertile(age, q):
    if age <= q[1]:
        return "Young"
    elif age <= q[2]:
        return "Middle Age"
    else:
        return "Old"

df["age_group_3"] = df["Age"].apply(lambda x: assign_age_tertile(x, age_q))

if DEBUG:
    df = df.head(DEBUG_N_SUBJECTS).copy()

print("\n=== Cohorte raffinée finale ===")
print("Nombre de sujets :", len(df))
print("Quantiles âge    :", age_q)
print(df["age_group_3"].value_counts(dropna=False))

if len(df) == 0:
    raise ValueError("Aucun sujet disponible après intersection démographie + TS.")


# =========================================================
# CONSTRUIRE LA LISTE DES SUJETS
# =========================================================
subjects = []
for _, row in df.iterrows():
    TS = row["TS"]
    subjects.append({
        "id": int(row["subject_id"]),
        "age": float(row["Age"]),
        "sex": row["Sex"],
        "edu": row["ISCED_ses-1"],
        "age_group": row["age_group_3"],
        "TS": TS,
        "file_path": row["file_path"],
        "ts_length": TS.shape[0],
        "n_windows": compute_n_windows(TS.shape[0], WINDOW, LAG),
    })

print("\nExemple sujet :")
print(subjects[0]["id"], subjects[0]["file_path"], subjects[0]["TS"].shape)

unique_lengths = sorted(set(sub["ts_length"] for sub in subjects))
print("Longueurs TS uniques :", unique_lengths)

COMMON_TS_LENGTH = EXPECTED_TS_LENGTH
COMMON_N_WINDOWS = compute_n_windows(COMMON_TS_LENGTH, WINDOW, LAG)
print("COMMON_TS_LENGTH :", COMMON_TS_LENGTH)
print("COMMON_N_WINDOWS :", COMMON_N_WINDOWS)

# taille attendue pour diagnostic
n_rois = subjects[0]["TS"].shape[1]
n_links = n_rois * (n_rois - 1) // 2
mc_small_size = (n_links, n_links)
mc_full_size = (n_rois * (n_rois - 1), n_rois * (n_rois - 1))
print("MCsmall attendue :", mc_small_size)
print("MC redondante attendue :", mc_full_size)


# =========================================================
# MOYENNES INCRÉMENTALES PAR GROUPE
# =========================================================
group_sums = {
    "Young": None,
    "Middle Age": None,
    "Old": None,
}
group_counts = {
    "Young": 0,
    "Middle Age": 0,
    "Old": 0,
}

times = []
example_MC = None
example_id = None

for sub in subjects:
    TS = sub["TS"]

    t0 = time.perf_counter()

    dFCstream = ts_to_dfc_stream(TS, W=WINDOW, lag=LAG, format="2D")
    MC = dfc_stream_to_mc_matlab_like(dFCstream, redundant=True, dtype=DTYPE)

    dt = time.perf_counter() - t0
    times.append(dt)

    g = sub["age_group"]

    if group_sums[g] is None:
        group_sums[g] = MC.copy()
    else:
        group_sums[g] += MC

    group_counts[g] += 1

    if PLOT_EXAMPLE_SUBJECT and example_MC is None:
        example_MC = MC.copy()
        example_id = sub["id"]

    print(f"\nSujet {sub['id']}")
    print("  âge            :", sub["age"])
    print("  groupe         :", g)
    print("  TS             :", TS.shape)
    print("  dFCstream      :", dFCstream.shape)
    print("  MC             :", MC.shape)
    print(f"  temps          : {dt:.3f} s")

    if SAVE_SUBJECT_MC:
        np.save(OUTPUT_DIR / f"sub-{sub['id']:04d}_MC.npy", MC)

    del dFCstream, MC
    gc.collect()

print(f"\nTemps moyen / sujet : {np.mean(times):.3f} s")
print(f"Temps total calcul  : {np.sum(times):.3f} s")


# =========================================================
# MATRICES MOYENNES FINALES
# =========================================================
young_mean_MC = None
middle_mean_MC = None
old_mean_MC = None

if group_counts["Young"] > 0:
    young_mean_MC = group_sums["Young"] / group_counts["Young"]
    np.save(OUTPUT_DIR / "MC_mean_young.npy", young_mean_MC)

if group_counts["Middle Age"] > 0:
    middle_mean_MC = group_sums["Middle Age"] / group_counts["Middle Age"]
    np.save(OUTPUT_DIR / "MC_mean_middle.npy", middle_mean_MC)

if group_counts["Old"] > 0:
    old_mean_MC = group_sums["Old"] / group_counts["Old"]
    np.save(OUTPUT_DIR / "MC_mean_old.npy", old_mean_MC)

print("\n=== Répartition finale ===")
print("Young       :", group_counts["Young"])
print("Middle Age  :", group_counts["Middle Age"])
print("Old         :", group_counts["Old"])


# =========================================================
# RÉSUMÉ
# =========================================================
summary = pd.DataFrame([{
    "session": SESSION,
    "atlas_folder": ATLAS_FOLDER,
    "ts_suffix": TS_SUFFIX,
    "TR": TR,
    "window": WINDOW,
    "lag": LAG,
    "expected_ts_length": EXPECTED_TS_LENGTH,
    "common_n_windows_used": COMMON_N_WINDOWS,
    "n_subjects_total": len(subjects),
    "n_subjects_young": group_counts["Young"],
    "n_subjects_middle": group_counts["Middle Age"],
    "n_subjects_old": group_counts["Old"],
    "age_q0": age_q[0],
    "age_q1_3": age_q[1],
    "age_q2_3": age_q[2],
    "age_q1": age_q[3],
    "mean_compute_time_per_subject_sec": float(np.mean(times)),
    "total_compute_time_sec": float(np.sum(times)),
    "n_rois": n_rois,
    "n_links_unique": n_links,
    "mc_small_dim": mc_small_size[0],
    "mc_full_dim": mc_full_size[0],
}])

summary.to_csv(OUTPUT_DIR / "summary_MC_refined_three_groups.csv", index=False)


# =========================================================
# FIGURE EXEMPLE INDIVIDUELLE
# =========================================================
plt.style.use("dark_background")

if PLOT_EXAMPLE_SUBJECT and example_MC is not None:
    vmax = np.nanpercentile(example_MC, 99)

    plt.figure(figsize=(7, 6))
    plt.imshow(example_MC, cmap="turbo", vmin=0, vmax=vmax)
    plt.colorbar()
    plt.gca().set_aspect("equal")
    plt.xlabel("Connections")
    plt.ylabel("Connections")
    plt.title(f"Example subject MC - sub-{example_id:04d}")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"example_subject_sub-{example_id:04d}_MC.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()


# =========================================================
# FIGURES PAR GROUPE
# =========================================================
group_mats = [
    ("Young", young_mean_MC, group_counts["Young"]),
    ("Middle Age", middle_mean_MC, group_counts["Middle Age"]),
    ("Old", old_mean_MC, group_counts["Old"]),
]

for title, mat, n_sub in group_mats:
    if mat is not None:
        vmax = np.nanpercentile(mat, 99)

        plt.figure(figsize=(7, 6))
        plt.imshow(mat, cmap="turbo", vmin=0, vmax=vmax)
        plt.colorbar()
        plt.gca().set_aspect("equal")
        plt.xlabel("Connections")
        plt.ylabel("Connections")
        plt.title(f"Mean meta-connectivity - {title} (n={n_sub})")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"mean_MC_{title.replace(' ', '_').lower()}.png", dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()


# =========================================================
# FIGURE COMPARATIVE 1x3
# =========================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, (title, mat, n_sub) in zip(axes, group_mats):
    if mat is not None:
        vmax = np.nanpercentile(mat, 99)
        im = ax.imshow(mat, cmap="turbo", vmin=0, vmax=vmax)
        ax.set_title(f"{title} (n={n_sub})")
        ax.set_xlabel("Connections")
        ax.set_ylabel("Connections")
        ax.set_aspect("equal")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    else:
        ax.set_title(f"{title} indisponible")
        ax.axis("off")

plt.suptitle("Mean meta-connectivity by age tertiles (refined cohort, Matlab-like MC)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUTPUT_DIR / "mean_MC_three_age_groups_refined_matlab_like.png", dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print(f"\nTous les résultats ont été enregistrés dans : {OUTPUT_DIR}")