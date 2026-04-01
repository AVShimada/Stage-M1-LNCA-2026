import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import zscore, pearsonr
import statsmodels.api as sm

# =========================
# 1. PARAMÈTRES
# =========================
input_file = Path(
    r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\Cognition\V1\data\1000Brains_NP_VarOI_V1_Pseudo.xlsx"
)
output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\figures_cognition_age_education"
)
output_dir.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

# =========================
# 2. IMPORT DES DONNÉES
# =========================
df = pd.read_excel(input_file, na_values=["NULL"]).copy()

# =========================
# 3. NETTOYAGE DE BASE
# =========================
df = df.dropna(subset=["Age"]).copy()

df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["ISCED_97"] = pd.to_numeric(df["ISCED_97"], errors="coerce")

df["age_group"] = df["Age"].apply(lambda x: "<55" if x < 55 else ">=55")

df["AKT_available_before_cleaning"] = df["AKT_TRW_SelectiveAttention"].notna()

# AKT réservé aux >=55
df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"] = np.nan
df["AKT_available"] = df["AKT_TRW_SelectiveAttention"].notna()

print("Nombre de sujets par groupe d'âge :")
print(df["age_group"].value_counts())
print()

print("Nombre de valeurs AKT par groupe d'âge après correction :")
print(df.groupby("age_group")["AKT_TRW_SelectiveAttention"].count())
print()

print("Nombre de valeurs AKT restantes chez les sujets <55 ans :")
print(df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"].notna().sum())
print()

# =========================
# 4. VARIABLES COGNITIVES
# =========================
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

missing_cols = [col for col in pca_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"Colonnes absentes du fichier : {missing_cols}")

for col in pca_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 5. DIRECTION DES TESTS
# =========================
# +1 = plus grand = meilleur
# -1 = plus grand = moins bon
#
# À vérifier selon ta convention exacte des scores.
direction_map = {
    "LPS_RRW_ProblemSolving": 1,
    "AKT_TRW_SelectiveAttention": 1,
    "Stroop_T3T2_Interference": -1,
    "RWD_5_Punkte_FiguralFluency": 1,
    "TMT_ARW_ProcessingSpeed": -1,
    "TMT_BA_ConceptShifting": -1,
    "BEN_RRW_FiguralMemory": 1,
    "CBT_RVW_VisualSpatialWM_fw": 1,
    "CBT_RRW_VisualSpatialWM_bw": 1,
    "VPT_RW_VisualMemory": 1,
    "ZNS_AVW_digitspan_fw": 1,
    "ZNS_ARW_digitspan_bw": 1,
    "RWT_PB2RW_PhonematicFluency": 1,
    "RWT_SB2RW_SemanticFluency": 1,
    "RWT_PGR2RW_PhonematicFluency_Switch": 1,
    "RWT_SSF2RW_SemanticFluency_Switch": 1,
    "AWST03P_Vocabulary": 1,
    "BKW_1_5_VerbalMemory": 1,
    "BKW_RWfv": 1,
}

# =========================
# 6. STANDARDISATION + SCORE GLOBAL
# =========================
z_cols = []

for col in pca_cols:
    z_col = f"{col}_z"
    vals = df[col]

    # z-score colonne par colonne
    z = (vals - vals.mean()) / vals.std(ddof=0)

    # aligne la direction
    z = z * direction_map[col]

    df[z_col] = z
    z_cols.append(z_col)

# score global = moyenne des z-scores disponibles
df["global_cognition_score"] = df[z_cols].mean(axis=1, skipna=True)

# nombre de tests disponibles par sujet
df["n_tests_used_global_score"] = df[z_cols].notna().sum(axis=1)

print("Résumé score global :")
print(df["global_cognition_score"].describe())
print()

# sauvegarde
df.to_csv(output_dir / "01_dataframe_with_global_cognition_score.csv", index=False)

# =========================
# 7. HISTOGRAMME DU SCORE GLOBAL
# =========================
plt.figure(figsize=(8, 5))
sns.histplot(df["global_cognition_score"].dropna(), bins=30, kde=True)
plt.title("Distribution du score global de cognition")
plt.xlabel("Score global de cognition")
plt.ylabel("Nombre de sujets")
plt.tight_layout()
plt.savefig(output_dir / "02_distribution_global_cognition_score.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================
# 8. SCORE GLOBAL EN FONCTION DE L'ÂGE
# =========================
plot_df = df[["Age", "global_cognition_score", "age_group"]].dropna()

plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=plot_df,
    x="Age",
    y="global_cognition_score",
    hue="age_group",
    alpha=0.65
)
sns.regplot(
    data=plot_df,
    x="Age",
    y="global_cognition_score",
    scatter=False,
    ci=95,
    color="black"
)
plt.title("Score global de cognition en fonction de l'âge")
plt.xlabel("Âge")
plt.ylabel("Score global de cognition")
plt.tight_layout()
plt.savefig(output_dir / "03_global_cognition_vs_age.png", bbox_inches="tight")
plt.show()
plt.close()

r_age, p_age = pearsonr(plot_df["Age"], plot_df["global_cognition_score"])
print(f"Corrélation âge / score global : r = {r_age:.3f}, p = {p_age:.3e}")

# =========================
# 9. IMPACT BRUT DE L'ÉDUCATION
# =========================
edu_df = df[["ISCED_97", "global_cognition_score"]].dropna().copy()

plt.figure(figsize=(8, 6))
sns.boxplot(data=edu_df, x="ISCED_97", y="global_cognition_score")
sns.stripplot(data=edu_df, x="ISCED_97", y="global_cognition_score", alpha=0.25, color="black")
plt.title("Score global de cognition selon le niveau d'éducation (ISCED_97)")
plt.xlabel("ISCED_97")
plt.ylabel("Score global de cognition")
plt.tight_layout()
plt.savefig(output_dir / "04_global_cognition_by_education_boxplot.png", bbox_inches="tight")
plt.show()
plt.close()

plt.figure(figsize=(8, 6))
sns.regplot(
    data=edu_df,
    x="ISCED_97",
    y="global_cognition_score",
    ci=95
)
plt.title("Score global de cognition en fonction de l'éducation")
plt.xlabel("ISCED_97")
plt.ylabel("Score global de cognition")
plt.tight_layout()
plt.savefig(output_dir / "05_global_cognition_vs_education_regplot.png", bbox_inches="tight")
plt.show()
plt.close()

r_edu, p_edu = pearsonr(edu_df["ISCED_97"], edu_df["global_cognition_score"])
print(f"Corrélation éducation / score global : r = {r_edu:.3f}, p = {p_edu:.3e}")

# =========================
# 10. IMPACT DE L'ÉDUCATION EN CONTRÔLANT L'ÂGE
# =========================
reg_df = df[["global_cognition_score", "ISCED_97", "Age"]].dropna().copy()

X = reg_df[["ISCED_97", "Age"]]
X = sm.add_constant(X)
y = reg_df["global_cognition_score"]

model = sm.OLS(y, X).fit()

with open(output_dir / "06_regression_global_cognition_education_age.txt", "w", encoding="utf-8") as f:
    f.write(model.summary().as_text())

print("\nRégression linéaire : score global ~ éducation + âge")
print(model.summary())

# =========================
# 11. FIGURE ÉDUCATION vs SCORE GLOBAL COLORÉE PAR ÂGE
# =========================
plot_df = df[["ISCED_97", "Age", "global_cognition_score"]].dropna().copy()

plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=plot_df,
    x="ISCED_97",
    y="global_cognition_score",
    hue="Age",
    alpha=0.7
)
sns.regplot(
    data=plot_df,
    x="ISCED_97",
    y="global_cognition_score",
    scatter=False,
    ci=95,
    color="black"
)
plt.title("Score global de cognition vs éducation")
plt.xlabel("ISCED_97")
plt.ylabel("Score global de cognition")
plt.tight_layout()
plt.savefig(output_dir / "07_global_cognition_vs_education_colored_by_age.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================
# 12. GROUPES D'ÉDUCATION SIMPLIFIÉS
# =========================
def isced_group(x):
    if pd.isna(x):
        return np.nan
    if x <= 5:
        return "Faible"
    elif x <= 8:
        return "Moyen"
    else:
        return "Élevé"

df["education_group"] = df["ISCED_97"].apply(isced_group)

plot_df = df[["education_group", "global_cognition_score"]].dropna()

plt.figure(figsize=(8, 6))
sns.boxplot(data=plot_df, x="education_group", y="global_cognition_score", order=["Faible", "Moyen", "Élevé"])
sns.stripplot(data=plot_df, x="education_group", y="global_cognition_score", order=["Faible", "Moyen", "Élevé"],
              alpha=0.25, color="black")
plt.title("Score global de cognition selon le niveau d'éducation")
plt.xlabel("Groupe d'éducation")
plt.ylabel("Score global de cognition")
plt.tight_layout()
plt.savefig(output_dir / "08_global_cognition_by_education_group.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================
# 13. TABLEAUX RÉCAPITULATIFS
# =========================
summary_edu = df.groupby("education_group")["global_cognition_score"].agg(["count", "mean", "std", "median"])
summary_edu.to_csv(output_dir / "09_summary_global_cognition_by_education_group.csv")

summary_isced = df.groupby("ISCED_97")["global_cognition_score"].agg(["count", "mean", "std", "median"])
summary_isced.to_csv(output_dir / "10_summary_global_cognition_by_ISCED.csv")

print("\nRésumé par groupe d'éducation :")
print(summary_edu)

print(f"\nTous les résultats ont été enregistrés dans : {output_dir}")