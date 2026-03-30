import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import time

# =========================================================
# PARAMÈTRES
# =========================================================
FC_BASE = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\FC")

MERGED_CSV = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_connectome\03_dataframe_cognition_connectome.csv"
)

OUTPUT_DIR = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_dFC_three_groups"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ATLAS = "100"         # "100" ou "400"
SESSION = "ses-1"     # "ses-1" ou "ses-2"

TR = 2
WINDOW = round(20 / TR)   # = 10
LAG = 1

MIN_N_WINDOWS = 250
COMMON_N_WINDOWS = 250

MIN_TS_LENGTH = WINDOW + (MIN_N_WINDOWS - 1) * LAG
COMMON_TS_LENGTH = WINDOW + (COMMON_N_WINDOWS - 1) * LAG

DEBUG = False
DEBUG_N_SUBJECTS = 20

PLOT_INDIVIDUAL_EXAMPLE = False
SAVE_SUBJECT_FCD = False


# =========================================================
# FONCTIONS FC / dFC
# =========================================================
def ts_to_fc(TS, format="2D"):
    if format != "1D":
        format = "2D"

    TS = np.asarray(TS, dtype=float)
    n = TS.shape[1]

    FCm = np.corrcoef(TS, rowvar=False)
    FCm = np.nan_to_num(FCm, nan=0.0, posinf=0.0, neginf=0.0)

    il = np.tril_indices(n, k=-1)
    FCv = FCm[il]

    return FCv if format == "1D" else FCm


def ts_to_dfc_stream(TS, W, lag=None, format="2D"):
    if W is None:
        raise ValueError("Provide at least a window size.")
    if lag is None:
        lag = W
    if format is None:
        format = "2D"

    TS = np.asarray(TS, dtype=float)
    t, n = TS.shape
    l = n * (n - 1) // 2

    wstart = 0
    wstop = W
    k = 0
    while wstop <= t:
        k += 1
        wstart += lag
        wstop += lag
    kmax = k

    if format == "3D":
        dFCstream = np.zeros((n, n, kmax), dtype=float)
    else:
        dFCstream = np.zeros((l, kmax), dtype=float)

    wstart = 0
    wstop = W
    k = 0
    while wstop <= t:
        window_ts = TS[wstart:wstop, :]

        if format == "3D":
            dFCstream[:, :, k] = ts_to_fc(window_ts, format="2D")
        else:
            dFCstream[:, k] = ts_to_fc(window_ts, format="1D")

        k += 1
        wstart += lag
        wstop += lag

    return dFCstream


def matrix2vec(dfcstream_3d):
    n, _, F = dfcstream_3d.shape
    il = np.tril_indices(n, k=-1)

    out = np.zeros((len(il[0]), F), dtype=float)
    for k in range(F):
        out[:, k] = dfcstream_3d[:, :, k][il]

    return out


def dfc_stream_to_dfc(dFCstream):
    if dFCstream.ndim == 3:
        dFCstream_2D = matrix2vec(dFCstream)
    elif dFCstream.ndim == 2:
        dFCstream_2D = dFCstream
    else:
        raise ValueError("Provide a valid size dFCstream (2D or 3D).")

    dFC = np.corrcoef(dFCstream_2D, rowvar=False)
    dFC = np.nan_to_num(dFC, nan=0.0, posinf=0.0, neginf=0.0)
    return dFC


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

    if TS.shape[0] < TS.shape[1]:
        TS = TS.T

    return TS, file_path


def compute_n_windows(ts_length, window, lag):
    return ((ts_length - window) // lag) + 1 if ts_length >= window else 0


# =========================================================
# CHARGER ET FILTRER LA COHORTE
# =========================================================
df = pd.read_csv(MERGED_CSV, na_values=["#NV", "na", "NA", "NULL", ""])
df.columns = df.columns.str.strip()

df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df = df.dropna(subset=["id", "Age"]).copy()

if SESSION == "ses-1":
    fc_col = "FC_ses1"
elif SESSION == "ses-2":
    fc_col = "FC_ses-2"
else:
    raise ValueError("SESSION doit être 'ses-1' ou 'ses-2'")

if fc_col not in df.columns:
    raise ValueError(f"Colonne absente dans le CSV : {fc_col}")

df = df[df[fc_col].astype(str).str.upper() == "YES"].copy()

# Groupes d'âge équilibrés par tertiles
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

print("Nombre de sujets après filtrage cohorte :", len(df))
print("\nQuantiles d'âge :", age_q)
print("\nRépartition tertiles d'âge :")
print(df["age_group_3"].value_counts(dropna=False))


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
            "age_group": row["age_group_3"],
            "TS": TS,
            "file_path": str(file_path),
            "ts_length": TS.shape[0],
            "n_windows": compute_n_windows(TS.shape[0], WINDOW, LAG),
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
# FILTRE NOMBRE DE FENÊTRES
# =========================================================
subjects_before_window_filter = len(subjects)
subjects = [sub for sub in subjects if sub["n_windows"] >= MIN_N_WINDOWS]

print("\n=== Filtre nombre de fenêtres ===")
print("TR                    :", TR)
print("WINDOW                :", WINDOW)
print("LAG                   :", LAG)
print("MIN_N_WINDOWS         :", MIN_N_WINDOWS)
print("MIN_TS_LENGTH         :", MIN_TS_LENGTH)
print("Sujets avant filtre   :", subjects_before_window_filter)
print("Sujets après filtre   :", len(subjects))

if len(subjects) == 0:
    raise ValueError(f"Aucun sujet ne possède au moins {MIN_N_WINDOWS} fenêtres.")

lengths = [sub["ts_length"] for sub in subjects]
print("Longueurs TS retenues :", sorted(set(lengths))[:20], "...")
print("Longueur min retenue  :", min(lengths))
print("Longueur max retenue  :", max(lengths))

subjects = [sub for sub in subjects if sub["ts_length"] >= COMMON_TS_LENGTH]

for sub in subjects:
    sub["TS_truncated"] = sub["TS"][:COMMON_TS_LENGTH, :]

print("COMMON_TS_LENGTH utilisé :", COMMON_TS_LENGTH)
print("COMMON_N_WINDOWS         :", COMMON_N_WINDOWS)


# =========================================================
# CALCUL dFC / FCD PAR SUJET
# =========================================================
times = []

for sub in subjects:
    TS = sub["TS_truncated"]

    assert TS.ndim == 2, f"TS non 2D pour sujet {sub['id']}"
    assert WINDOW <= TS.shape[0], f"WINDOW trop grand pour sujet {sub['id']}"
    assert np.isfinite(TS).all(), f"NaN/Inf dans TS sujet {sub['id']}"

    t0 = time.perf_counter()

    dFCstream = ts_to_dfc_stream(TS, W=WINDOW, lag=LAG, format="2D")
    dFC = dfc_stream_to_dfc(dFCstream)

    dt = time.perf_counter() - t0
    times.append(dt)

    sub["dFCstream"] = dFCstream
    sub["dFC"] = dFC

    print(f"\nSujet {sub['id']}")
    print("  âge            :", sub["age"])
    print("  groupe         :", sub["age_group"])
    print("  TS tronquée    :", TS.shape)
    print("  n_windows      :", dFC.shape[0])
    print("  dFCstream      :", dFCstream.shape)
    print("  dFC            :", dFC.shape)
    print(f"  temps          : {dt:.3f} s")

    if SAVE_SUBJECT_FCD:
        np.save(OUTPUT_DIR / f"sub-{sub['id']:04d}_dFC.npy", dFC)

print(f"\nTemps moyen / sujet : {np.mean(times):.3f} s")
print(f"Temps total calcul  : {np.sum(times):.3f} s")


# =========================================================
# MOYENNES PAR GROUPE
# =========================================================
young_subjects = [sub for sub in subjects if sub["age_group"] == "Young"]
middle_subjects = [sub for sub in subjects if sub["age_group"] == "Middle Age"]
old_subjects = [sub for sub in subjects if sub["age_group"] == "Old"]

print("\n=== Répartition finale ===")
print("Young       :", len(young_subjects))
print("Middle Age  :", len(middle_subjects))
print("Old         :", len(old_subjects))

young_mean_dFC = None
middle_mean_dFC = None
old_mean_dFC = None

if len(young_subjects) > 0:
    young_stack = np.stack([sub["dFC"] for sub in young_subjects], axis=0)
    young_mean_dFC = np.mean(young_stack, axis=0)
    np.save(OUTPUT_DIR / "dFC_mean_young.npy", young_mean_dFC)
    pd.DataFrame(young_mean_dFC).to_csv(OUTPUT_DIR / "dFC_mean_young.csv", index=False, header=False)

if len(middle_subjects) > 0:
    middle_stack = np.stack([sub["dFC"] for sub in middle_subjects], axis=0)
    middle_mean_dFC = np.mean(middle_stack, axis=0)
    np.save(OUTPUT_DIR / "dFC_mean_middle.npy", middle_mean_dFC)
    pd.DataFrame(middle_mean_dFC).to_csv(OUTPUT_DIR / "dFC_mean_middle.csv", index=False, header=False)

if len(old_subjects) > 0:
    old_stack = np.stack([sub["dFC"] for sub in old_subjects], axis=0)
    old_mean_dFC = np.mean(old_stack, axis=0)
    np.save(OUTPUT_DIR / "dFC_mean_old.npy", old_mean_dFC)
    pd.DataFrame(old_mean_dFC).to_csv(OUTPUT_DIR / "dFC_mean_old.csv", index=False, header=False)


# =========================================================
# RÉSUMÉ
# =========================================================
summary = pd.DataFrame([{
    "session": SESSION,
    "atlas": ATLAS,
    "TR": TR,
    "window": WINDOW,
    "lag": LAG,
    "min_n_windows_required": MIN_N_WINDOWS,
    "common_n_windows_used": COMMON_N_WINDOWS,
    "common_ts_length_used": COMMON_TS_LENGTH,
    "n_subjects_total_after_filter": len(subjects),
    "n_subjects_young": len(young_subjects),
    "n_subjects_middle": len(middle_subjects),
    "n_subjects_old": len(old_subjects),
    "age_q0": age_q[0],
    "age_q1_3": age_q[1],
    "age_q2_3": age_q[2],
    "age_q1": age_q[3],
    "mean_compute_time_per_subject_sec": float(np.mean(times)),
    "total_compute_time_sec": float(np.sum(times)),
}])

summary.to_csv(OUTPUT_DIR / "summary_dFC_three_groups.csv", index=False)


# =========================================================
# FIGURE EXEMPLE INDIVIDUELLE
# =========================================================
plt.style.use("dark_background")

if PLOT_INDIVIDUAL_EXAMPLE and len(subjects) > 0:
    dFC_example = subjects[0]["dFC"]

    plt.figure(figsize=(7, 6))
    plt.imshow(dFC_example, cmap="turbo", vmin=0, vmax=1)
    plt.colorbar()
    plt.gca().set_aspect("equal")
    plt.xlabel("Time window")
    plt.ylabel("Time window")
    plt.title(f"Example subject FCD - sub-{subjects[0]['id']:04d}")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"example_subject_sub-{subjects[0]['id']:04d}_FCD.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()


# =========================================================
# FIGURES PAR GROUPE
# =========================================================
group_mats = [
    ("Young", young_mean_dFC, len(young_subjects)),
    ("Middle Age", middle_mean_dFC, len(middle_subjects)),
    ("Old", old_mean_dFC, len(old_subjects)),
]

for title, mat, n_sub in group_mats:
    if mat is not None:
        plt.figure(figsize=(7, 6))
        plt.imshow(mat, cmap="turbo", vmin=0, vmax=1)
        plt.colorbar()
        plt.gca().set_aspect("equal")
        plt.xlabel("Time window")
        plt.ylabel("Time window")
        plt.title(f"Mean FCD recurrence matrix - {title} (n={n_sub})")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"mean_FCD_{title.replace(' ', '_').lower()}.png", dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()


# =========================================================
# FIGURE COMPARATIVE 1x3
# =========================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, (title, mat, n_sub) in zip(axes, group_mats):
    if mat is not None:
        im = ax.imshow(mat, cmap="turbo", vmin=0, vmax=1)
        ax.set_title(f"{title} (n={n_sub})")
        ax.set_xlabel("Time window")
        ax.set_ylabel("Time window")
        ax.set_aspect("equal")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    else:
        ax.set_title(f"{title} indisponible")
        ax.axis("off")

plt.suptitle("Mean FCD recurrence matrices by age tertiles", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUTPUT_DIR / "mean_FCD_three_age_groups.png", dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print(f"\nTous les résultats ont été enregistrés dans : {OUTPUT_DIR}")