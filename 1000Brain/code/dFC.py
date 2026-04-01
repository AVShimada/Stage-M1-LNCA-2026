import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import time
import gc
import random

# =========================================================
# PARAMÈTRES
# =========================================================
FC_BASE = Path(r"C:\Users\aure6\Downloads\1000BRAINSconnectomes_Jirsa\FC")

MERGED_CSV = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_connectome\03_dataframe_cognition_connectome.csv"
)

OUTPUT_DIR = Path(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_dFC_random_subjects"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SESSION = "ses-1"

TR = 2
WINDOW = 10
LAG = 1

COMMON_TS_LENGTH = 290

DTYPE = np.float32
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

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

# 3 groupes équilibrés
df["age_group"] = pd.qcut(df["Age"], 3, labels=["Young", "Middle", "Old"])

df = df[df["FC_ses1"] == "YES"]

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

        if TS.shape[0] >= COMMON_TS_LENGTH:
            TS = TS[:COMMON_TS_LENGTH]

            subjects.append({
                "id": sid,
                "age": row["Age"],
                "group": str(row["age_group"]),
                "TS": TS
            })

    except Exception:
        continue

print("Sujets chargés :", len(subjects))

# =========================================================
# SÉLECTION ALÉATOIRE (3 sujets par groupe)
# =========================================================
groups = ["Young", "Middle", "Old"]
N_PER_GROUP = 3

selected_subjects = {}

for g in groups:
    subs = [s for s in subjects if s["group"] == g]

    if len(subs) >= N_PER_GROUP:
        selected_subjects[g] = random.sample(subs, N_PER_GROUP)
    elif len(subs) > 0:
        selected_subjects[g] = subs
    else:
        selected_subjects[g] = []

print("\nSujets sélectionnés :")
for g in groups:
    ids = [f"sub-{s['id']}" for s in selected_subjects[g]]
    print(f"{g} -> {ids}")

# =========================================================
# CALCUL dFC
# =========================================================
results = {g: [] for g in groups}

for g in groups:
    for sub in selected_subjects[g]:
        TS = sub["TS"]

        t0 = time.perf_counter()

        dFCstream = ts_to_dfc_stream(TS, WINDOW, LAG)
        dFC = dfc_stream_to_dfc(dFCstream)

        dt = time.perf_counter() - t0

        print(f"{g} | sub-{sub['id']} | fenêtres={dFC.shape[0]} | temps={dt:.3f}s")

        results[g].append({
            "id": sub["id"],
            "mat": dFC
        })

        del dFCstream
        gc.collect()

# =========================================================
# 3 FIGURES SÉPARÉES
# =========================================================
plt.style.use("dark_background")

for g in groups:
    if len(results[g]) == 0:
        continue

    fig, axes = plt.subplots(1, N_PER_GROUP, figsize=(5 * N_PER_GROUP, 5))

    if N_PER_GROUP == 1:
        axes = [axes]

    last_im = None

    for i in range(N_PER_GROUP):
        ax = axes[i]

        if i < len(results[g]):
            mat = results[g][i]["mat"]
            sid = results[g][i]["id"]

            last_im = ax.imshow(mat, cmap="turbo", vmin=0, vmax=0.5)
            ax.set_title(f"{g}\nsub-{sid}", fontsize=11)
            ax.set_xlabel("Time windows")
            ax.set_ylabel("Time windows")
            ax.set_aspect("equal")
        else:
            ax.axis("off")

    if last_im is not None:
        # créer un axe dédié pour la colorbar à droite
        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # [left, bottom, width, height]

        cbar = fig.colorbar(last_im, cax=cbar_ax)
        cbar.set_label("Correlation")

    plt.suptitle(f"FCD - 3 sujets aléatoires du groupe {g}", fontsize=16)
    plt.subplots_adjust(wspace=0.2, hspace=0.2, top=0.88)

    plt.savefig(OUTPUT_DIR / f"random_3subjects_{g}_FCD.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

print(f"\nFigures enregistrées dans : {OUTPUT_DIR}")
