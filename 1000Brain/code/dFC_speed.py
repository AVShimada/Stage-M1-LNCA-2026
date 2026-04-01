import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.fft import fft, ifft
from scipy.stats import gaussian_kde, ks_2samp
import time

# =========================================================
# PARAMÈTRES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
FC_BASE = BASE_DIR / "FC"
MERGED_CSV = BASE_DIR / "03_dataframe_cognition_connectome.csv"

TR = 2.0
LAG = 1
COMMON_TS_LENGTH = 290

win_ranges = [
    (60, 210),
    (15, 60)
]

range_names = ["Long", "Mid"]

# =========================================================
# FONCTIONS MATLAB-LIKE
# =========================================================
def ts_to_fc_vec(TS):
    FC = np.corrcoef(TS, rowvar=False)
    FC = np.nan_to_num(FC)
    return FC[np.tril_indices(FC.shape[0], -1)]


def TS2dFCstream(TS, W, lag=1):
    t = TS.shape[0]
    kmax = ((t - W) // lag) + 1
    n_links = TS.shape[1] * (TS.shape[1] - 1) // 2

    stream = np.zeros((n_links, kmax))

    k = 0
    for start in range(0, t - W + 1, lag):
        stream[:, k] = ts_to_fc_vec(TS[start:start+W])
        k += 1

    return stream


def dFC_Speeds(dFCstream):
    speeds = []

    for t in range(dFCstream.shape[1] - 1):
        c = np.corrcoef(dFCstream[:, t], dFCstream[:, t+1])[0, 1]
        speeds.append(1 - c)

    speeds = np.nan_to_num(speeds)
    return np.median(speeds), np.array(speeds)


# =========================================================
# PHASE RANDOMIZATION (CORRECT)
# =========================================================
def phase_randomize(TS):
    TS_pr = np.zeros_like(TS)

    for i in range(TS.shape[1]):
        x = TS[:, i]
        Xf = fft(x)

        amp = np.abs(Xf)
        phase = np.angle(Xf)

        rand_phase = np.random.uniform(0, 2*np.pi, len(phase))

        Xf_new = amp * np.exp(1j * rand_phase)
        TS_pr[:, i] = np.real(ifft(Xf_new))

    return TS_pr


# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(MERGED_CSV)
df["id"] = pd.to_numeric(df["id"], errors="coerce")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

df = df.dropna(subset=["id", "Age"])
df = df[df["FC_ses1"] == "YES"]

# =========================================================
# LOAD TS
# =========================================================
def find_ts_file(sid):
    sub = f"sub-{int(sid):04d}"
    folder = FC_BASE / sub / "ses-1" / "FC" / "Schaefer_100_7NW"

    if not folder.exists():
        return None

    for f in folder.iterdir():
        if "FC_TS_Schaefer_100P_7NW" in f.name and "TSdim" not in f.name:
            return f
    return None


subjects = []

for _, row in df.iterrows():
    sid = int(row["id"])
    f = find_ts_file(sid)

    if f is None:
        continue

    TS = np.loadtxt(f)
    TS = np.nan_to_num(TS)

    if TS.shape[0] < TS.shape[1]:
        TS = TS.T

    if TS.shape[0] >= COMMON_TS_LENGTH:
        TS = TS[:COMMON_TS_LENGTH]

        subjects.append(TS)

print("Nombre de sujets :", len(subjects))

## Test si data en entry sont bien présentes et accessibles
print("FC_BASE      :", FC_BASE)
print("MERGED_CSV   :", MERGED_CSV)
print("FC exists    :", FC_BASE.exists())
print("CSV exists   :", MERGED_CSV.exists())

# =========================================================
# CALCUL Vtyp (FIDÈLE MATLAB)
# =========================================================
N = len(subjects)
Vtyp_results = [np.zeros((N, 3)) for _ in range(2)]

print("\nCalcul des Vtyp...")

for s, TS_emp in enumerate(subjects):

    TS_pr = phase_randomize(TS_emp)

    for r, (w_min_s, w_max_s) in enumerate(win_ranges):

        w_min = int(w_min_s / TR)
        w_max = int(w_max_s / TR)

        tmp_e, tmp_p, tmp_s = [], [], []

        for w in range(w_min, w_max, 10):

            s_emp = TS2dFCstream(TS_emp, w, LAG)
            s_pr  = TS2dFCstream(TS_pr,  w, LAG)

            # shuffled
            idx = np.random.permutation(s_emp.shape[1])
            s_sh = s_emp[:, idx]

            _, v_e = dFC_Speeds(s_emp)
            _, v_p = dFC_Speeds(s_pr)
            _, v_s = dFC_Speeds(s_sh)

            tmp_e.extend(v_e)
            tmp_p.extend(v_p)
            tmp_s.extend(v_s)

        Vtyp_results[r][s, 0] = np.median(tmp_e)
        Vtyp_results[r][s, 1] = np.median(tmp_p)
        Vtyp_results[r][s, 2] = np.median(tmp_s)

    if s % 50 == 0:
        print(f"Sujet {s}/{N}")


# =========================================================
# KDE + KS TEST (MATLAB FIGURE 4D)
# =========================================================
plt.style.use("dark_background")
fig, axes = plt.subplots(2, 1, figsize=(8, 10))

for r in range(2):
    ax = axes[r]
    data = Vtyp_results[r]

    kde1 = gaussian_kde(data[:,0])
    kde2 = gaussian_kde(data[:,1])
    kde3 = gaussian_kde(data[:,2])

    x = np.linspace(0, 1.2, 200)

    ax.plot(x, kde1(x), color=(0.1,0.1,0.5), lw=3, label="Empirical")
    ax.plot(x, kde2(x), "g--", lw=2, label="Phase rand")
    ax.plot(x, kde3(x), "r:", lw=2, label="Shuffled")

    # KS test
    p_pr = ks_2samp(data[:,0], data[:,1]).pvalue
    p_sh = ks_2samp(data[:,0], data[:,2]).pvalue

    if p_pr < 0.01:
        ax.text(0.6, max(kde1(x)), "**", color="green", fontsize=15)

    if p_sh < 0.01:
        ax.text(0.7, max(kde1(x)), "**", color="red", fontsize=15)

    ax.set_title(range_names[r])
    ax.set_xlabel("Vtyp")
    ax.set_ylabel("Density")
    ax.legend()
    ax.set_xlim([0, 1.2])

plt.tight_layout()
plt.show()