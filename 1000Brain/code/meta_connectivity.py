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
        im = ax.imshow(mat, cmap="turbo", vmin=0, vmax=0.1)
        ax.set_title(f"{title} (n={n_sub})")
        ax.set_xlabel("Connections")
        ax.set_ylabel("Connections")
        ax.set_aspect("equal")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    else:
        ax.set_title(f"{title} indisponible")
        ax.axis("off")

plt.suptitle("Mean meta-connectivity by age tertiles (vmax=0.1)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUTPUT_DIR / "mean_MC_three_age_groups_refined_matlab_like.png", dpi=300, bbox_inches="tight")
plt.show()
plt.close()

print(f"\nTous les résultats ont été enregistrés dans : {OUTPUT_DIR}")