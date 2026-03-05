import pandas as pd
import plotly.graph_objects as go

# 1. Charger les données
df = pd.read_csv('C:/Users/aure6/Downloads/STAGE_M1/code/sankey_data_SC_MEANS.csv')

def generate_sankey_data(df):
    sources = []
    targets = []
    values = []
    
    # On identifie les modules uniques par groupe
    g1_mods = sorted(df['G1'].unique())
    g2_mods = sorted(df['G2'].unique())
    g3_mods = sorted(df['G3'].unique())
    
    # Création des IDs uniques pour Plotly (chaque bloc doit avoir un ID unique)
    # G1: 0 à N, G2: N+1 à M, etc.
    offset_g2 = max(g1_mods) + 1
    offset_g3 = offset_g2 + max(g2_mods) + 1
    
    # Flux G1 -> G2
    for m1 in g1_mods:
        for m2 in g2_mods:
            count = len(df[(df['G1'] == m1) & (df['G2'] == m2)])
            if count > 0:
                sources.append(m1)
                targets.append(m2 + offset_g2)
                values.append(count)
                
    # Flux G2 -> G3
    for m2 in g2_mods:
        for m3 in g3_mods:
            count = len(df[(df['G2'] == m2) & (df['G3'] == m3)])
            if count > 0:
                sources.append(m2 + offset_g2)
                targets.append(m3 + offset_g3)
                values.append(count)
                
    # Labels des nœuds (le nom qui s'affiche sur les blocs)
    labels = [f"G1-Mod {m}" for m in g1_mods] + \
             [f"G2-Mod {m}" for m in g2_mods] + \
             [f"G3-Mod {m}" for m in g3_mods]
    
    return labels, sources, targets, values

# 2. Préparer les données pour le tracé
labels, sources, targets, values = generate_sankey_data(df)

# 3. Créer la figure Plotly
fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "royalblue"
    ),
    link = dict(
      source = sources, 
      target = targets,
      value = values,
      hovertemplate = 'Transition: %{value} nœuds<extra></extra>'
  ))])

fig.update_layout(title_text="Évolution de l'allégeance des nœuds (G1 -> G2 -> G3)", font_size=12)
fig.show()