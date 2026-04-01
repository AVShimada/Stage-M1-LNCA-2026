import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# =========================
# 1. PARAMÈTRES
# =========================
input_file = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\Cognition\V1\data\1000Brains_NP_VarOI_V1_Pseudo.xlsx")
output_dir = Path(r"C:\Users\aure6\Downloads\figures_cognition_age")

# Crée le dossier de sortie s'il n'existe pas
output_dir.mkdir(parents=True, exist_ok=True)

# Style général des figures
sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 120

# =========================
# 2. IMPORT DES DONNÉES
# =========================
df = pd.read_excel(input_file, na_values=["NULL"])

# =========================
# 3. NETTOYAGE DE BASE
# =========================
# Supprimer les sujets sans âge
df = df.dropna(subset=["Age"]).copy()

# Groupe d'âge
df["age_group"] = df["Age"].apply(lambda x: "<55" if x < 55 else ">=55")

# Disponibilité AKT avant correction
df["AKT_available_before_cleaning"] = df["AKT_TRW_SelectiveAttention"].notna()

# Correction protocolaire :
# AKT ne doit pas être utilisé pour les sujets <55 ans
df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"] = pd.NA

# Disponibilité AKT après correction
df["AKT_available"] = df["AKT_TRW_SelectiveAttention"].notna()

# Vérifications
print("Nombre de sujets par groupe d'âge :")
print(df["age_group"].value_counts())
print()

print("Nombre de valeurs AKT par groupe d'âge après correction :")
print(df.groupby("age_group")["AKT_TRW_SelectiveAttention"].count())
print()

print("Nombre de valeurs AKT restantes chez les sujets <55 ans :")
print(df.loc[df["Age"] < 55, "AKT_TRW_SelectiveAttention"].notna().sum())
print()

print("Valeurs manquantes par colonne :")
print(df.isna().sum())
print()

# =========================
# 4. LISTE DES VARIABLES À PLOTER
# =========================
exclude_cols = [
    "ID",
    "Visit",
    "Sex",
    "Age",
    "age_group",
    "AKT_available_before_cleaning",
    "AKT_available"
]

test_cols = [col for col in df.columns if col not in exclude_cols]

# =========================
# 5. HISTOGRAMME DE L'ÂGE
# =========================
plt.figure(figsize=(8, 5))
sns.histplot(data=df, x="Age", bins=30, kde=True)
plt.title("Distribution des âges")
plt.xlabel("Âge")
plt.ylabel("Nombre de sujets")
plt.tight_layout()
plt.savefig(output_dir / "00_distribution_age.png", bbox_inches="tight")
plt.show()
plt.close()

# Histogramme par groupe d'âge
plt.figure(figsize=(8, 5))
sns.histplot(data=df, x="Age", hue="age_group", bins=30, multiple="stack")
plt.title("Distribution des âges par groupe")
plt.xlabel("Âge")
plt.ylabel("Nombre de sujets")
plt.tight_layout()
plt.savefig(output_dir / "01_distribution_age_groupes.png", bbox_inches="tight")
plt.show()
plt.close()

# =========================
# 6. FONCTION POUR CRÉER LES SCATTER PLOTS
# =========================
def safe_filename(name: str) -> str:
    """
    Transforme un nom de variable en nom de fichier propre.
    """
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name

def plot_age_vs_test(dataframe: pd.DataFrame, test_col: str, save_dir: Path) -> None:
    """
    Crée et sauvegarde un nuage de points Age vs test_col
    avec droite de tendance.
    """
    plot_df = dataframe[["Age", test_col]].dropna()

    # Évite de créer des figures vides
    if plot_df.empty:
        print(f"Figure ignorée pour {test_col} : aucune donnée disponible.")
        return

    plt.figure(figsize=(7, 5))

    # Nuage de points
    sns.scatterplot(
        data=plot_df,
        x="Age",
        y=test_col,
        alpha=0.6
    )

    # Droite de tendance
    sns.regplot(
        data=plot_df,
        x="Age",
        y=test_col,
        scatter=False,
        ci=95
    )

    plt.title(f"{test_col} en fonction de l'âge")
    plt.xlabel("Âge")
    plt.ylabel(test_col)
    plt.tight_layout()

    filename = safe_filename(test_col) + "_vs_Age.png"
    plt.savefig(save_dir / filename, bbox_inches="tight")
    plt.show()
    plt.close()

# =========================
# 7. FIGURES POUR TOUS LES TESTS
# =========================
for col in test_cols:
    plot_age_vs_test(df, col, output_dir)

print(f"Toutes les figures ont été enregistrées dans : {output_dir}")