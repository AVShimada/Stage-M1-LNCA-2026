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