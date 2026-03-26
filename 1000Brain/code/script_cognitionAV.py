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