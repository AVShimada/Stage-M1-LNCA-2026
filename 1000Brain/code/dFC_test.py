import numpy as np
import pandas as pd
from pathlib import Path

# =========================================================
# PARAMÈTRES
# =========================================================
FC_BASE = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\FC")

MERGED_CSV = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_connectome\03_dataframe_cognition_connectome.csv"
)

ATLAS = "100"          # "100" ou "400"
SESSION = "ses-1"      # "ses-1" ou "ses-2"

# pour éviter de tout charger si tu veux tester vite
DEBUG = False
DEBUG_N_SUBJECTS = 50


# =========================================================
# FONCTIONS CHARGEMENT DES TS
# =========================================================
def get_atlas_folder_name(atlas="100"):
    if str(atlas) == "100":
        return "Schaefer_100_7NW"
    elif str(atlas) == "400":
        return "Schaefer_400_7NW"
    raise ValueError("ATLAS doit être '100' ou '400'")


def get_ts_token(atlas="100"):
    if str(atlas) == "100":
        return "FC_TS_Schaefer_100P_7NW"
    elif str(atlas) == "400":
        return "FC_TS_Schaefer_400P_7NW"
    raise ValueError("ATLAS doit être '100' ou '400'")


def find_ts_file(subject_id, session="ses-1", atlas="100"):
    sub_str = f"sub-{int(subject_id):04d}"
    atlas_folder = get_atlas_folder_name(atlas)
    ts_token = get_ts_token(atlas)

    folder = FC_BASE / sub_str / session / "FC" / atlas_folder
    if not folder.exists():
        return None

    candidates = []
    for f in folder.iterdir():
        if not f.is_file():
            continue

        name = f.name
        cond_ts = ts_token in name
        cond_exclude = (
            "connectivitymatrix" in name
            or "TSdim" in name
            or "VolPercRemAfterCens" in name
        )

        if cond_ts and not cond_exclude:
            candidates.append(f)

    if len(candidates) == 0:
        return None

    candidates = sorted(
        candidates,
        key=lambda x: ("V2" in x.name, "V1" in x.name, x.name),
        reverse=True
    )
    return candidates[0]


def load_matrix_auto(file_path: Path):
    suffix = file_path.suffix.lower()

    if suffix == ".npy":
        return np.array(np.load(file_path), dtype=float)

    try:
        mat = np.loadtxt(file_path)
        if mat.ndim == 2:
            return np.array(mat, dtype=float)
    except Exception:
        pass

    try:
        mat = pd.read_csv(file_path, sep="\t", header=None).values
        if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
            return np.array(mat, dtype=float)
    except Exception:
        pass

    try:
        mat = pd.read_csv(file_path, sep=",", header=None).values
        if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
            return np.array(mat, dtype=float)
    except Exception:
        pass

    try:
        mat = pd.read_csv(file_path, sep=";", header=None).values
        if mat.ndim == 2 and mat.shape[0] > 1 and mat.shape[1] > 1:
            return np.array(mat, dtype=float)
    except Exception:
        pass

    raise ValueError(f"Impossible de lire le fichier : {file_path}")


def load_subject_ts(subject_id, session="ses-1", atlas="100"):
    file_path = find_ts_file(subject_id, session=session, atlas=atlas)
    if file_path is None:
        return None, None

    TS = load_matrix_auto(file_path)
    TS = np.nan_to_num(TS, nan=0.0, posinf=0.0, neginf=0.0)

    # on force format (temps, régions)
    if TS.shape[0] < TS.shape[1]:
        TS = TS.T

    return TS, file_path


def compute_n_windows(ts_length, window, lag):
    if ts_length < window:
        return 0
    return ((ts_length - window) // lag) + 1


# =========================================================
# CHARGER LA COHORTE
# =========================================================
df = pd.read_csv(MERGED_CSV, na_values=["#NV", "na", "NA", "NULL", ""])
df.columns = df.columns.str.strip()

df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

df = df.dropna(subset=["id", "Age"]).copy()

if "age_group" not in df.columns:
    df["age_group"] = df["Age"].apply(lambda x: "<55" if x < 55 else ">=55")

if SESSION == "ses-1":
    fc_col = "FC_ses1"
elif SESSION == "ses-2":
    fc_col = "FC_ses-2"
else:
    raise ValueError("SESSION doit être 'ses-1' ou 'ses-2'")

if fc_col not in df.columns:
    raise ValueError(f"Colonne absente dans le CSV : {fc_col}")

df = df[df[fc_col].astype(str).str.upper() == "YES"].copy()

if DEBUG:
    df = df.head(DEBUG_N_SUBJECTS).copy()

print("Nombre de sujets après filtrage cohorte :", len(df))
print(df["age_group"].value_counts(dropna=False))


# =========================================================
# CHARGEMENT DES SUJETS
# =========================================================
subjects = []
missing_files = []
failed_loading = []

for _, row in df.iterrows():
    sid = int(row["id"])
    TS, file_path = load_subject_ts(sid, session=SESSION, atlas=ATLAS)

    if TS is None:
        missing_files.append(sid)
        continue

    try:
        subjects.append({
            "id": sid,
            "age": float(row["Age"]),
            "age_group": row["age_group"],
            "TS": TS,
            "file_path": str(file_path)
        })
    except Exception:
        failed_loading.append(sid)

print("\n=== Résumé chargement ===")
print("Sujets attendus après filtre cohorte :", len(df))
print("Sujets réellement chargés           :", len(subjects))
print("Fichiers TS manquants               :", len(missing_files))
print("Sujets en échec de chargement       :", len(failed_loading))

if len(subjects) == 0:
    raise ValueError("Aucun sujet valide chargé.")

print("\nExemple sujet chargé :")
print(subjects[0]["id"], subjects[0]["file_path"], subjects[0]["TS"].shape)


# =========================================================
# DISTRIBUTION DES LONGUEURS TS
# =========================================================
lengths = [sub["TS"].shape[0] for sub in subjects]

print("\n=== Distribution des longueurs TS ===")
print("Min :", min(lengths))
print("Max :", max(lengths))
print("Valeurs uniques (20 premières) :", sorted(set(lengths))[:20])

length_counts = pd.Series(lengths).value_counts().sort_index()
print("\nEffectifs par longueur (20 premières lignes) :")
print(length_counts.head(20))

print("\n=== Durées estimées selon différents TR ===")
for tr_candidate in [0.8, 1.0, 1.5, 2.0, 2.2, 2.5, 3.0]:
    durations_min = [L * tr_candidate / 60 for L in lengths]
    print(
        f"TR={tr_candidate:.1f}s -> durée min={min(durations_min):.2f} min, "
        f"max={max(durations_min):.2f} min"
    )


# =========================================================
# NOMBRE DE FENÊTRES POSSIBLES
# =========================================================
print("\n=== Nombre de fenêtres possibles selon WINDOW ===")
for window in [10, 20, 30, 40, 50]:
    n_windows_all = [compute_n_windows(L, window, 1) for L in lengths]
    print(
        f"WINDOW={window:2d} -> "
        f"min windows={min(n_windows_all)}, "
        f"max windows={max(n_windows_all)}"
    )


# =========================================================
# TESTS DE SEUILS
# =========================================================
print("\n=== Combien de sujets passent différents seuils ? ===")
for min_windows in [100, 150, 200, 250, 280, 300, 400, 500, 600]:
    if 10 > 0:
        min_ts_length = 10 + (min_windows - 1) * 1
    else:
        min_ts_length = None

    n_kept = sum(L >= min_ts_length for L in lengths)
    print(
        f"Seuil {min_windows:3d} fenêtres "
        f"(TS >= {min_ts_length}) -> {n_kept} sujets gardés"
    )


# =========================================================
# EXPORT RÉSUMÉ
# =========================================================
summary_df = pd.DataFrame({
    "id": [sub["id"] for sub in subjects],
    "age": [sub["age"] for sub in subjects],
    "age_group": [sub["age_group"] for sub in subjects],
    "ts_length": [sub["TS"].shape[0] for sub in subjects],
    "file_path": [sub["file_path"] for sub in subjects],
})

print("\nAperçu du résumé :")
print(summary_df.head())

# optionnel : sauvegarde pour inspection
output_summary = MERGED_CSV.parent / f"summary_TS_lengths_{SESSION}_atlas{ATLAS}.csv"
summary_df.to_csv(output_summary, index=False)

print("\nRésumé sauvegardé dans :")
print(output_summary)