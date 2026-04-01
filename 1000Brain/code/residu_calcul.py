import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# =========================
# PARAMÈTRES
# =========================
input_file = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\figures_cognition_age_education\01_dataframe_with_global_cognition_score.csv"
)

output_dir = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\figures_cognition_residual"
)
output_dir.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

# =========================
# 1. LOAD DATA
# =========================
df = pd.read_csv(input_file)

# =========================
# 2. SÉLECTION DES VARIABLES
# =========================
reg_df = df[[
    "global_cognition_score",
    "Age",
    "ISCED_97"
]].dropna().copy()

print("Nombre de sujets utilisés :", len(reg_df))

# =========================
# 3. RÉGRESSION
# =========================
X = reg_df[["Age", "ISCED_97"]]
X = sm.add_constant(X)

y = reg_df["global_cognition_score"]

model = sm.OLS(y, X).fit()

print("\n=== Résultats régression ===")
print(model.summary())

# =========================
# 4. RÉSIDU
# =========================
reg_df["cognition_residual"] = model.resid

# =========================
# 5. SAUVEGARDE
# =========================
reg_df.to_csv(
    output_dir / "cognition_residuals.csv",
    index=False
)

# =========================
# 6. VISUALISATIONS
# =========================

# Histogramme
plt.figure(figsize=(7,5))
sns.histplot(reg_df["cognition_residual"], kde=True)
plt.title("Distribution du résidu de cognition")
plt.xlabel("Résidu cognition")
plt.tight_layout()
plt.savefig(output_dir / "residual_distribution.png", dpi=300)
plt.show()
plt.close()

# Résidu vs âge (doit être plat !)
plt.figure(figsize=(7,5))
sns.scatterplot(
    data=reg_df,
    x="Age",
    y="cognition_residual",
    alpha=0.6
)
sns.regplot(
    data=reg_df,
    x="Age",
    y="cognition_residual",
    scatter=False,
    color="red"
)
plt.title("Résidu vs âge (doit être ~0 pente)")
plt.tight_layout()
plt.savefig(output_dir / "residual_vs_age.png", dpi=300)
plt.show()
plt.close()

# Résidu vs éducation
plt.figure(figsize=(7,5))
sns.scatterplot(
    data=reg_df,
    x="ISCED_97",
    y="cognition_residual",
    alpha=0.6
)
sns.regplot(
    data=reg_df,
    x="ISCED_97",
    y="cognition_residual",
    scatter=False,
    color="red"
)
plt.title("Résidu vs éducation (doit être ~0 pente)")
plt.tight_layout()
plt.savefig(output_dir / "residual_vs_education.png", dpi=300)
plt.show()
plt.close()

print("\nRésidus calculés et sauvegardés dans :", output_dir)