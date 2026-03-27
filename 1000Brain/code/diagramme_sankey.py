import pandas as pd
import plotly.graph_objects as go

# =========================================================
# FONCTION GÉNÉRALE POUR LE NOUVEAU DATASET
# =========================================================
def generate_sankey_data_2groups(df, col1="<55", col2=">=55"):
    sources = []
    targets = []
    values = []

    # Modules uniques par groupe
    g1_mods = sorted(df[col1].unique())
    g2_mods = sorted(df[col2].unique())

    # IDs uniques pour Plotly
    offset_g2 = len(g1_mods)

    g1_id_map = {mod: i for i, mod in enumerate(g1_mods)}
    g2_id_map = {mod: i + offset_g2 for i, mod in enumerate(g2_mods)}

    # Flux <55 -> >=55
    for m1 in g1_mods:
        for m2 in g2_mods:
            count = len(df[(df[col1] == m1) & (df[col2] == m2)])
            if count > 0:
                sources.append(g1_id_map[m1])
                targets.append(g2_id_map[m2])
                values.append(count)

    # Labels affichés sur les blocs
    labels = [f"{col1} - Mod {m}" for m in g1_mods] + \
             [f"{col2} - Mod {m}" for m in g2_mods]

    return labels, sources, targets, values


# =========================================================
# 1. SANKEY FC
# =========================================================
df_fc = pd.read_csv(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_consensus_partition\sankey_data_FC_MEANS.csv"
)

labels, sources, targets, values = generate_sankey_data_2groups(
    df_fc,
    col1="<55",
    col2=">=55"
)

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color="royalblue"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        hovertemplate='Transition: %{value} nœuds<extra></extra>'
    )
)])

fig.update_layout(
    title_text="Évolution de l'allégeance des nœuds FC moyens (<55 -> >=55)",
    font_size=12
)

fig.show()


# =========================================================
# 2. SANKEY SC
# =========================================================
df_sc = pd.read_csv(
    r"C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\1000Brain\resultats_consensus_partition\sankey_data_SC_MEANS.csv"
)

labels, sources, targets, values = generate_sankey_data_2groups(
    df_sc,
    col1="<55",
    col2=">=55"
)

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color="seagreen"
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        hovertemplate='Transition: %{value} nœuds<extra></extra>'
    )
)])

fig.update_layout(
    title_text="Évolution de l'allégeance des nœuds SC moyens (<55 -> >=55)",
    font_size=12
)

fig.show()