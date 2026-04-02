import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, Isomap

# nécessite: pip install umap-learn
import umap

# =========================================================
# 1. PARAMÈTRES
# =========================================================
input_file = Path(
    r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\Cognition\V1\data\1000Brains_NP_VarOI_V1_Pseudo.xlsx"
)

output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_reduction_dimension_cognition"
)
output_dir.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

# =========================================================
# 2. IMPORT DES DONNÉES
# =========================================================
df = pd.read_excel(input_file, na_values=["NULL"]).copy()

# =========================================================
# 3. NETTOYAGE DE BASE
# =========================================================
df = df.dropna(subset=["Age"]).copy()

df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["age_group"] = df["Age"].apply(lambda x: "<55" if x < 55 else ">=55")

df["AKT_available_before_cleaning"] = df["AKT_TRW_SelectiveAttention"].notna()

# AKT réservé aux >=55
df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"] = np.nan

df["AKT_available"] = df["AKT_TRW_SelectiveAttention"].notna()
df["Sex_num"] = df["Sex"].map({"Male": 0, "Female": 1})

print("=== Vérifications après nettoyage ===")
print("\nNombre de sujets :", len(df))
print("\nRépartition par groupe d'âge :")
print(df["age_group"].value_counts())
print("\nAKT par groupe d'âge :")
print(df.groupby("age_group")["AKT_TRW_SelectiveAttention"].count())

# =========================================================
# 4. VARIABLES COGNITIVES
# =========================================================
feature_cols = [
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

missing_cols = [col for col in feature_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"Colonnes absentes : {missing_cols}")

X = df[feature_cols].copy()

# =========================================================
# 5. IMPUTATION + STANDARDISATION
# =========================================================
imputer = SimpleImputer(strategy="mean")
X_imputed = pd.DataFrame(
    imputer.fit_transform(X),
    columns=X.columns,
    index=X.index
)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

X_scaled_df = pd.DataFrame(
    X_scaled,
    columns=X.columns,
    index=X.index
)

X_imputed.to_csv(output_dir / "01_matrice_cognitive_imputee.csv", index=True)
X_scaled_df.to_csv(output_dir / "02_matrice_cognitive_standardisee.csv", index=True)

# =========================================================
# 6. PCA
# =========================================================
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

df_pca = pd.DataFrame(X_pca, columns=["Dim1", "Dim2"], index=df.index)
df_pca["ID"] = df["ID"].values
df_pca["Age"] = df["Age"].values
df_pca["Sex"] = df["Sex"].values
df_pca["age_group"] = df["age_group"].values
df_pca["method"] = "PCA"

# =========================================================
# 7. t-SNE
# =========================================================
tsne = TSNE(
    n_components=2,
    perplexity=30,
    learning_rate="auto",
    init="pca",
    random_state=42
)
X_tsne = tsne.fit_transform(X_scaled)

df_tsne = pd.DataFrame(X_tsne, columns=["Dim1", "Dim2"], index=df.index)
df_tsne["ID"] = df["ID"].values
df_tsne["Age"] = df["Age"].values
df_tsne["Sex"] = df["Sex"].values
df_tsne["age_group"] = df["age_group"].values
df_tsne["method"] = "t-SNE"

# =========================================================
# 8. Isomap
# =========================================================
isomap = Isomap(n_components=2, n_neighbors=15)
X_isomap = isomap.fit_transform(X_scaled)

df_isomap = pd.DataFrame(X_isomap, columns=["Dim1", "Dim2"], index=df.index)
df_isomap["ID"] = df["ID"].values
df_isomap["Age"] = df["Age"].values
df_isomap["Sex"] = df["Sex"].values
df_isomap["age_group"] = df["age_group"].values
df_isomap["method"] = "Isomap"

# =========================================================
# 9. UMAP
# =========================================================
umap_model = umap.UMAP(
    n_components=2,
    n_neighbors=15,
    min_dist=0.1,
    random_state=42
)
X_umap = umap_model.fit_transform(X_scaled)

df_umap = pd.DataFrame(X_umap, columns=["Dim1", "Dim2"], index=df.index)
df_umap["ID"] = df["ID"].values
df_umap["Age"] = df["Age"].values
df_umap["Sex"] = df["Sex"].values
df_umap["age_group"] = df["age_group"].values
df_umap["method"] = "UMAP"

# =========================================================
# 10. SAUVEGARDE DES PROJECTIONS
# =========================================================
df_pca.to_csv(output_dir / "03_projection_PCA.csv", index=False)
df_tsne.to_csv(output_dir / "04_projection_tSNE.csv", index=False)
df_isomap.to_csv(output_dir / "05_projection_Isomap.csv", index=False)
df_umap.to_csv(output_dir / "06_projection_UMAP.csv", index=False)

df_all = pd.concat([df_pca, df_tsne, df_isomap, df_umap], axis=0)
df_all.to_csv(output_dir / "07_projections_toutes_methodes.csv", index=False)

# =========================================================
# 11. FONCTION DE PLOT
# =========================================================
def plot_projection(data, title, hue, save_path):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=data,
        x="Dim1",
        y="Dim2",
        hue=hue,
        alpha=0.75
    )
    plt.title(title)
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.show()
    plt.close()

# =========================================================
# 12. FIGURES INDIVIDUELLES
# =========================================================
plot_projection(
    df_pca,
    "PCA - projection des sujets par groupe d'âge",
    "age_group",
    output_dir / "08_PCA_age_group.png"
)

plot_projection(
    df_tsne,
    "t-SNE - projection des sujets par groupe d'âge",
    "age_group",
    output_dir / "09_tSNE_age_group.png"
)

plot_projection(
    df_isomap,
    "Isomap - projection des sujets par groupe d'âge",
    "age_group",
    output_dir / "10_Isomap_age_group.png"
)

plot_projection(
    df_umap,
    "UMAP - projection des sujets par groupe d'âge",
    "age_group",
    output_dir / "11_UMAP_age_group.png"
)

plot_projection(
    df_pca,
    "PCA - projection des sujets par âge",
    "Age",
    output_dir / "12_PCA_age_continu.png"
)

plot_projection(
    df_tsne,
    "t-SNE - projection des sujets par âge",
    "Age",
    output_dir / "13_tSNE_age_continu.png"
)

plot_projection(
    df_isomap,
    "Isomap - projection des sujets par âge",
    "Age",
    output_dir / "14_Isomap_age_continu.png"
)

plot_projection(
    df_umap,
    "UMAP - projection des sujets par âge",
    "Age",
    output_dir / "15_UMAP_age_continu.png"
)

# =========================================================
# 13. FIGURE COMPARATIVE 2x2
# =========================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

methods = [
    ("PCA", df_pca),
    ("t-SNE", df_tsne),
    ("Isomap", df_isomap),
    ("UMAP", df_umap),
]

for ax, (name, df_proj) in zip(axes.ravel(), methods):
    sns.scatterplot(
        data=df_proj,
        x="Dim1",
        y="Dim2",
        hue="age_group",
        alpha=0.75,
        ax=ax
    )
    ax.set_title(name)
    ax.set_xlabel("Dimension 1")
    ax.set_ylabel("Dimension 2")

handles, labels = axes[0, 0].get_legend_handles_labels()

for ax in axes.ravel():
    legend = ax.get_legend()
    if legend is not None:
        legend.remove()

fig.legend(handles, labels, loc="upper right")
plt.suptitle("Comparaison PCA / t-SNE / Isomap / UMAP", fontsize=16)
plt.tight_layout(rect=[0, 0, 0.95, 0.97])
plt.savefig(output_dir / "16_comparaison_methodes_age_group.png", bbox_inches="tight")
plt.show()
plt.close()

print(f"\nTous les résultats ont été enregistrés dans : {output_dir}")