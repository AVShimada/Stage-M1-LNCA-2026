import numpy as np
import scipy.io as sio
from nilearn import plotting
import matplotlib.pyplot as plt

# 1. CHARGEMENT DES DONNÉES .MAT
# Remplace le chemin par l'endroit où se trouve ton fichier
file_path = 'C:/Users/aure6/Downloads/Stage_M1_Github/Stage-M1-LNCA-2026/Aging_Data/data/AgingDATA_for_learning.mat'
data = sio.loadmat(file_path, squeeze_me=True, struct_as_record=False)

# 2. COORDONNÉES DES 68 RÉGIONS (Atlas Desikan-Killiany)
coords = np.array([
    [-51, -43, 8], [-4, 25, 24], [-34, 19, 44], [-7, -78, 20], [-24, -14, -36], [-30, -38, -19],
    [-42, -67, 34], [-48, -25, -28], [-8, -48, 16], [-40, -82, 11], [-31, 26, -14], [-15, -67, -4],
    [-5, 41, -15], [-54, -20, -14], [-22, -30, -15], [-7, -32, 57], [-44, 15, 22], [-40, 31, -11],
    [-46, 26, 9], [-10, -83, 3], [-43, -18, 48], [-7, -27, 40], [-41, -11, 46], [-8, -55, 52],
    [-4, 39, 4], [-31, 46, 17], [-17, 33, 46], [-22, -60, 58], [-53, -22, 6], [-51, -34, 30],
    [-7, 54, -9], [-29, 13, -34], [-43, -16, 7], [-35, 3, 3], # Gauche
    [51, -43, 8], [4, 25, 24], [34, 19, 44], [7, -78, 20], [24, -14, -36], [30, -38, -19],
    [42, -67, 34], [48, -25, -28], [8, -48, 16], [40, -82, 11], [31, 26, -14], [15, -67, -4],
    [5, 41, -15], [54, -20, -14], [22, -30, -15], [7, -32, 57], [44, 15, 22], [40, 31, -11],
    [46, 26, 9], [10, -83, 3], [43, -18, 48], [7, -27, 40], [41, -11, 46], [8, -55, 52],
    [4, 39, 4], [31, 46, 17], [17, 33, 46], [22, -60, 58], [53, -22, 6], [51, -34, 30],
    [7, 54, -9], [29, 13, -34], [43, -16, 7], [35, 3, 3] # Droite
])

# 3. EXTRACTION ET CALCUL DE LA FC
N_subjects = 49
all_fc = []
all_ages = []

for i in range(1, N_subjects + 1):
    sub_key = f'SUBJECT_{i}'
    subject = data[sub_key]
    
    # Calcul de la corrélation (FC) à partir des Time Series (TS)
    ts = subject.TS # Shape attendu (N_timepoints, 68)
    fc = np.corrcoef(ts.T)
    np.fill_diagonal(fc, 0) # Nettoyage diagonale
    
    all_fc.append(fc)
    all_ages.append(subject.age)

all_fc = np.array(all_fc)
all_ages = np.array(all_ages)

# 4. CRÉATION DES GROUPES (Tertiles d'âge)
q1, q2 = np.quantile(all_ages, [0.333, 0.666])
groups = np.zeros(N_subjects)
groups[all_ages <= q1] = 1
groups[(all_ages > q1) & (all_ages <= q2)] = 2
groups[all_ages > q2] = 3

group_names = ['Jeunes (G1)', 'Moyens (G2)', 'Âgés (G3)']

# 5. GÉNÉRATION DES GLASS BRAINS
for k in range(1, 4):
    # Moyenne de la FC pour le groupe k
    mean_fc_group = np.mean(all_fc[groups == k], axis=0)
    
    # Affichage
    plotting.plot_connectome(
        mean_fc_group, 
        coords,
        edge_threshold="95%", # Garde les 5% des liens les plus forts
        title=f'Glass Brain : {group_names[k-1]}',
        display_mode='ortho',
        node_size=20,
        edge_cmap='RdYlBu_r'
    )

plotting.show()