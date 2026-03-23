"""
Dashboard Desembarque Pesquero — Chile 2000-2024
Stack : Dash 4 + Plotly 6 + Dash Bootstrap Components
"""
import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════════════════════
# 1. CARGA Y LIMPIEZA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
print("Cargando datos...")
df = pd.read_csv(os.path.join(BASE_DIR, "csv", "BD_desembarque.csv"), sep=";", encoding="latin-1")
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={df.columns[1]: "ano"})           # año → ano (evita encoding)
df["ano"]       = pd.to_numeric(df["ano"],       errors="coerce")
df["toneladas"] = pd.to_numeric(df["toneladas"], errors="coerce").fillna(0)
df["mes"]       = pd.to_numeric(df["mes"],       errors="coerce")
df["aguas"]     = df["aguas"].str.upper().str.strip()
for col in ["region", "especie", "puerto_desembarque", "tipo_agente"]:
    df[col] = df[col].astype(str).str.strip()
df = df.dropna(subset=["ano"])
df["ano"] = df["ano"].astype(int)
print(f"OK {len(df):,} registros | {df['ano'].min()}-{df['ano'].max()}")

ANOS    = sorted(df["ano"].unique().tolist())
REGIONS = sorted(df["region"].unique().tolist())
TIPOS   = sorted(df["tipo_agente"].unique().tolist())

# ══════════════════════════════════════════════════════════════════════════════
# 2. COORDENADAS DE PUERTOS (54 puertos del CSV)
# ══════════════════════════════════════════════════════════════════════════════
PORT_COORDS = {
    "Arica":           (-18.47, -70.32),
    "Iquique":         (-20.21, -70.14),
    "Tocopilla":       (-22.09, -70.20),
    "Mejillones":      (-23.10, -70.46),
    "Antofagasta":     (-23.65, -70.40),
    "Taltal":          (-25.40, -70.49),
    "Chanaral":        (-26.35, -70.62),
    "Cha\u00f1aral":   (-26.35, -70.62),   # variante con ñ del CSV
    "Caldera":         (-27.07, -70.82),
    "Huasco":          (-28.47, -71.22),
    "Coquimbo":        (-29.96, -71.34),
    "Tongoy":          (-30.25, -71.50),
    "Los Vilos":       (-31.91, -71.51),
    "Quintero":        (-32.78, -71.53),
    "Valparaiso":      (-33.03, -71.63),
    "San Antonio":     (-33.60, -71.62),
    "La Ligua":        (-32.45, -71.24),
    "Pichilemu":       (-34.39, -72.00),
    "Iloca":           (-34.93, -72.18),
    "Pelluhue":        (-35.83, -72.57),
    "Cobquecura":      (-36.13, -72.79),
    "Constitucion":    (-35.33, -72.42),
    "Tome":            (-36.62, -72.96),
    "Talcahuano":      (-36.72, -73.12),
    "San Vicente":     (-36.76, -73.15),
    "Lirquen":         (-36.69, -72.99),
    "Coronel":         (-37.02, -73.15),
    "Lota":            (-37.09, -73.16),
    "Lebu":            (-37.61, -73.65),
    "Queule":          (-39.38, -73.19),
    "Puerto Saavedra": (-38.79, -73.40),
    "Valdivia":        (-39.81, -73.24),
    "Corral":          (-39.88, -73.43),
    "Maullin":         (-41.62, -73.60),
    "Calbuco":         (-41.77, -73.14),
    "Puerto Montt":    (-41.47, -72.94),
    "Ancud":           (-41.87, -73.83),
    "Quemchi":         (-42.13, -73.48),
    "Dalcahue":        (-42.38, -73.64),
    "Castro":          (-42.48, -73.76),
    "Chonchi":         (-42.62, -73.72),
    "Queilen":         (-42.88, -73.55),
    "Quellon":         (-43.12, -73.61),
    "Melinka":         (-43.90, -74.47),
    "Cisnes":          (-44.74, -72.68),
    "Aysen":           (-45.40, -72.70),
    "Chacabuco":       (-45.47, -72.80),
    "Palena":          (-43.62, -72.55),
    "Puerto Aguirre":  (-45.16, -72.59),
    "Guaitecas":       (-43.90, -74.47),
    "Porvenir":        (-53.30, -70.37),
    "Punta Arenas":    (-53.16, -70.91),
    "Puerto Natales":  (-51.73, -72.51),
    "Puerto Williams": (-54.93, -67.61),
    "Metropolitana":   (-33.46, -70.65),
    "Osorno":          (-40.57, -73.13),
}

# Mapeo puerto CSV → coordenadas
port_coord_map: dict = {}
for p in df["puerto_desembarque"].unique():
    pn = str(p).strip()
    if pn in PORT_COORDS:
        port_coord_map[pn] = PORT_COORDS[pn]
        continue
    for key, coords in PORT_COORDS.items():
        if key.lower() in pn.lower() or pn.lower() in key.lower():
            port_coord_map[pn] = coords
            break

# ══════════════════════════════════════════════════════════════════════════════
# 3. TEMAS
# ══════════════════════════════════════════════════════════════════════════════
DARK: dict = {
    "name":       "dark",
    "bg":         "#0d0f1a",
    "card":       "#151827",
    "sidebar":    "#0f1220",
    "text":       "#e2e8f0",
    "muted":      "#64748b",
    "border":     "rgba(255,255,255,0.07)",
    "shadow":     "0 4px 24px rgba(0,0,0,0.45)",
    "plot_bg":    "rgba(0,0,0,0)",
    "paper_bg":   "rgba(0,0,0,0)",
    "gridcolor":  "rgba(255,255,255,0.05)",
    "kpi_colors": ["#818cf8", "#34d399", "#f59e0b", "#f87171"],
    "land":       "#1a1d2e",
    "ocean":      "#0a0c14",
    "coast":      "#2d3748",
    "cs":         [[0, "#0d0f1a"], [0.4, "#4f46e5"], [1, "#22d3ee"]],
}
LIGHT: dict = {
    "name":       "light",
    "bg":         "#f0f4f8",
    "card":       "#ffffff",
    "sidebar":    "#ffffff",
    "text":       "#0f172a",
    "muted":      "#64748b",
    "border":     "rgba(0,0,0,0.07)",
    "shadow":     "0 2px 14px rgba(0,0,0,0.07)",
    "plot_bg":    "rgba(0,0,0,0)",
    "paper_bg":   "rgba(0,0,0,0)",
    "gridcolor":  "rgba(0,0,0,0.06)",
    "kpi_colors": ["#6366f1", "#059669", "#d97706", "#dc2626"],
    "land":       "#e8f4f8",
    "ocean":      "#dbeafe",
    "coast":      "#93c5fd",
    "cs":         [[0, "#eff6ff"], [0.4, "#6366f1"], [1, "#0ea5e9"]],
}
THEMES = {"dark": DARK, "light": LIGHT}

TIPO_COLORS = {
    "Artesanal":   "#818cf8",
    "Industrial":  "#34d399",
    "Acuicultura": "#f59e0b",
    "Fabrica":     "#f87171",
}


def hex_to_rgba(hex_color: str, alpha: float = 0.09) -> str:
    """Convierte #RRGGBB a rgba(r,g,b,alpha) — Plotly 6 no acepta hex de 8 dígitos."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ══════════════════════════════════════════════════════════════════════════════
# 4. HELPERS DE LAYOUT PLOTLY
# ══════════════════════════════════════════════════════════════════════════════
def base_layout(t: dict, title: str = "") -> dict:
    return dict(
        title=dict(
            text=title,
            font=dict(color=t["text"], size=12, family="Inter, sans-serif"),
            x=0.02, y=0.97,
        ),
        paper_bgcolor=t["paper_bg"],
        plot_bgcolor=t["plot_bg"],
        font=dict(color=t["text"], family="Inter, sans-serif", size=11),
        margin=dict(l=8, r=8, t=38, b=8),
        xaxis=dict(
            gridcolor=t["gridcolor"], linecolor="rgba(0,0,0,0)",
            color=t["muted"], zeroline=False,
        ),
        yaxis=dict(
            gridcolor=t["gridcolor"], linecolor="rgba(0,0,0,0)",
            color=t["muted"], zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=t["muted"], size=10),
            orientation="h", y=-0.18,
        ),
        hoverlabel=dict(
            bgcolor=t["card"], font_color=t["text"],
            bordercolor=t["border"], font_size=12,
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 5. FUNCIONES DE GRÁFICOS
# ══════════════════════════════════════════════════════════════════════════════
def chart_timeline(dff: pd.DataFrame, t: dict) -> go.Figure:
    agg = dff.groupby(["ano", "tipo_agente"])["toneladas"].sum().reset_index()
    fig = go.Figure()
    tipos_present = sorted(dff["tipo_agente"].unique())
    for tipo in tipos_present:
        sub = agg[agg["tipo_agente"] == tipo].sort_values("ano")
        color = TIPO_COLORS.get(tipo, "#818cf8")
        fig.add_trace(go.Scatter(
            x=sub["ano"],
            y=sub["toneladas"] / 1_000,
            name=tipo,
            mode="lines+markers",
            line=dict(width=2.5, color=color),
            marker=dict(size=5, color=color),
            # fill="tozeroy" para TODOS: cada trazo llena desde 0 independientemente.
            # fill="tonexty" causa que trazos con menor valor queden sepultados
            # visualmente por el fill del trazo superior.
            fill="tozeroy",
            fillcolor=hex_to_rgba(color, 0.07),
            hovertemplate=f"<b>%{{x}}</b>: %{{y:,.1f}}k t<extra>{tipo}</extra>",
        ))
    layout = base_layout(t, "Desembarque Anual por Tipo de Agente (miles de toneladas)")
    layout["hovermode"] = "x unified"
    layout["xaxis"]["dtick"] = 2
    layout["xaxis"]["tickangle"] = 0
    fig.update_layout(**layout)
    return fig


def chart_treemap(dff: pd.DataFrame, t: dict) -> go.Figure:
    agg = dff.groupby("especie")["toneladas"].sum().nlargest(30).reset_index()
    fig = px.treemap(
        agg, path=["especie"], values="toneladas",
        color="toneladas", color_continuous_scale=t["cs"],
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,.0f} t",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} toneladas<extra></extra>",
        textfont_size=11,
        marker_line_width=2,
        marker_line_color=t["card"],
    )
    layout = base_layout(t, "Top 30 Especies — Treemap")
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    layout["coloraxis_showscale"] = False
    fig.update_layout(**layout)
    return fig


def chart_map(dff: pd.DataFrame, t: dict) -> go.Figure:
    port_agg = dff.groupby("puerto_desembarque")["toneladas"].sum().reset_index()
    port_agg["lat"] = port_agg["puerto_desembarque"].map(
        lambda p: port_coord_map.get(p, (None, None))[0]
    )
    port_agg["lon"] = port_agg["puerto_desembarque"].map(
        lambda p: port_coord_map.get(p, (None, None))[1]
    )
    port_agg = port_agg.dropna(subset=["lat", "lon"])

    if len(port_agg) == 0:
        empty = go.Figure()
        layout = base_layout(t, "Distribución Geográfica — Puertos")
        layout.pop("xaxis", None); layout.pop("yaxis", None)
        empty.update_layout(**layout)
        return empty

    max_t = port_agg["toneladas"].max()
    # Tamaño de burbuja: rango 8–42px proporcional a raíz cuadrada del volumen
    port_agg["size"] = (np.sqrt(port_agg["toneladas"]) / np.sqrt(max_t) * 34 + 8).clip(8, 42)
    port_agg["ton_fmt"] = port_agg["toneladas"].apply(lambda x: f"{x:,.0f}")

    # Tile style según modo: carto-darkmatter (dark) / carto-positron (light)
    map_style = "carto-darkmatter" if t["name"] == "dark" else "carto-positron"
    colorscale  = "Teal"  if t["name"] == "dark" else "Blues"

    fig = go.Figure(go.Scattermap(
        lat=port_agg["lat"],
        lon=port_agg["lon"],
        mode="markers",
        marker=dict(
            size=port_agg["size"],
            color=port_agg["toneladas"],
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                title=dict(text="ton", font=dict(size=10, color=t["muted"])),
                thickness=10,
                len=0.6,
                tickfont=dict(color=t["muted"], size=9),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(0,0,0,0)",
            ),
            opacity=0.9,
        ),
        text=port_agg["puerto_desembarque"],
        customdata=port_agg[["ton_fmt"]].values,
        hovertemplate="<b>%{text}</b><br>%{customdata[0]} toneladas<extra></extra>",
    ))

    layout = base_layout(t, "Distribución Geográfica — Puertos")
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    # Chile: lat -56 a -17, centrado en -37 lon -71, zoom 3.8 muestra todo el país
    layout["map"] = dict(
        style=map_style,
        center=dict(lat=-37, lon=-71),
        zoom=3.8,
    )
    layout["margin"] = dict(l=0, r=0, t=38, b=0)
    fig.update_layout(**layout)
    return fig


def chart_top_especies(dff: pd.DataFrame, t: dict) -> go.Figure:
    top = (
        dff.groupby("especie")["toneladas"]
        .sum().nlargest(10).reset_index()
        .sort_values("toneladas")
    )
    n = len(top)
    palette = t["kpi_colors"]
    colors = [palette[i % len(palette)] for i in range(n)]

    fig = go.Figure(go.Bar(
        x=top["toneladas"] / 1_000,
        y=top["especie"],
        orientation="h",
        marker=dict(color=colors, cornerradius=6),
        text=(top["toneladas"] / 1_000).apply(lambda x: f"{x:,.1f}k"),
        textposition="outside",
        textfont=dict(color=t["muted"], size=10),
        hovertemplate="<b>%{y}</b><br>%{x:,.1f}k toneladas<extra></extra>",
    ))
    layout = base_layout(t, "Top 10 Especies por Toneladas")
    layout["yaxis"]["showgrid"] = False
    layout["xaxis"]["title"] = dict(text="Miles de toneladas", font=dict(size=10))
    layout["margin"] = dict(l=8, r=65, t=38, b=8)
    fig.update_layout(**layout)
    return fig


def chart_donut(dff: pd.DataFrame, t: dict) -> go.Figure:
    agg = dff.groupby("tipo_agente")["toneladas"].sum().reset_index()
    colors = [TIPO_COLORS.get(ta, "#818cf8") for ta in agg["tipo_agente"]]
    total = agg["toneladas"].sum()

    fig = go.Figure(go.Pie(
        labels=agg["tipo_agente"],
        values=agg["toneladas"],
        hole=0.60,
        marker=dict(colors=colors, line=dict(width=3, color=t["card"])),
        texttemplate="%{label}<br><b>%{percent}</b>",
        textfont=dict(size=11, color=t["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} t | %{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{total / 1e6:.1f}M</b><br><span style='font-size:9px'> toneladas</span>",
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=15, color=t["text"]),
    )
    layout = base_layout(t, "Participación por Tipo de Agente")
    layout.pop("xaxis", None)
    layout.pop("yaxis", None)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def chart_region_bar(dff: pd.DataFrame, t: dict) -> go.Figure:
    """Barras horizontales de toneladas por región."""
    agg = (
        dff.groupby("region")["toneladas"]
        .sum().reset_index()
        .sort_values("toneladas", ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=agg["toneladas"] / 1_000,
        y=agg["region"],
        orientation="h",
        marker=dict(
            color=agg["toneladas"],
            colorscale=t["cs"],
            cornerradius=5,
        ),
        hovertemplate="<b>%{y}</b><br>%{x:,.1f}k toneladas<extra></extra>",
    ))
    layout = base_layout(t, "Toneladas por Región")
    layout["yaxis"]["showgrid"] = False
    layout["xaxis"]["title"] = dict(text="Miles de toneladas", font=dict(size=10))
    layout["margin"] = dict(l=8, r=20, t=38, b=8)
    layout["coloraxis_showscale"] = False
    fig.update_layout(**layout)
    return fig


def make_kpi_cards(dff: pd.DataFrame, t: dict) -> dbc.Row:
    total_ton   = dff["toneladas"].sum()
    top_esp     = dff.groupby("especie")["toneladas"].sum().idxmax() if len(dff) > 0 else "—"
    n_puertos   = dff["puerto_desembarque"].nunique()
    ano_min     = int(dff["ano"].min()) if len(dff) > 0 else "—"
    ano_max     = int(dff["ano"].max()) if len(dff) > 0 else "—"

    kpis = [
        {
            "label": "Toneladas Totales",
            "value": f"{total_ton / 1e6:.2f}M t",
            "sub":   "toneladas métricas",
            "icon":  "🐟",
        },
        {
            "label": "Especie Principal",
            "value": top_esp[:20] if isinstance(top_esp, str) else top_esp,
            "sub":   "mayor volumen desembarcado",
            "icon":  "🎣",
        },
        {
            "label": "Puertos Activos",
            "value": str(n_puertos),
            "sub":   "en el período seleccionado",
            "icon":  "⚓",
        },
        {
            "label": "Período",
            "value": f"{ano_min}–{ano_max}",
            "sub":   f"{dff['ano'].nunique()} años de datos",
            "icon":  "📅",
        },
    ]

    cols = []
    for i, k in enumerate(kpis):
        color = t["kpi_colors"][i]
        cols.append(dbc.Col(
            html.Div([
                html.Div([
                    html.Span(k["icon"], style={"fontSize": "1.6rem", "lineHeight": "1"}),
                    html.Div([
                        html.Div(
                            k["value"],
                            style={
                                "fontSize": "1.55rem", "fontWeight": "700",
                                "color": color, "lineHeight": "1.1",
                                "letterSpacing": "-0.02em",
                            },
                        ),
                        html.Div(
                            k["label"],
                            style={
                                "fontSize": "0.65rem", "color": t["muted"],
                                "textTransform": "uppercase",
                                "letterSpacing": "0.08em", "marginTop": "3px",
                            },
                        ),
                    ]),
                ], style={"display": "flex", "alignItems": "center", "gap": "14px"}),
                html.Div(
                    k["sub"],
                    style={
                        "fontSize": "0.7rem", "color": t["muted"],
                        "marginTop": "12px", "paddingTop": "10px",
                        "borderTop": f"1px solid {t['border']}",
                    },
                ),
                html.Div(style={
                    "position": "absolute", "bottom": 0, "left": 0, "right": 0,
                    "height": "3px", "background": color,
                    "borderRadius": "0 0 14px 14px", "opacity": "0.7",
                }),
            ], style={
                "background":    t["card"],
                "borderRadius":  "14px",
                "padding":       "20px 22px 18px",
                "boxShadow":     t["shadow"],
                "border":        f"1px solid {t['border']}",
                "position":      "relative",
                "overflow":      "hidden",
                "height":        "100%",
                "transition":    "transform 0.2s, box-shadow 0.2s",
            }),
            width=3,
        ))
    return dbc.Row(cols, className="g-3 mb-3")


# ══════════════════════════════════════════════════════════════════════════════
# 6. LAYOUT DE LA APP
# ══════════════════════════════════════════════════════════════════════════════
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Dashboard Desembarque Chile"
server = app.server          # expone el servidor Flask para gunicorn


def G(gid: str, height: str = "100%") -> dcc.Graph:
    """Shorthand para crear un dcc.Graph limpio."""
    return dcc.Graph(
        id=gid,
        config={"displayModeBar": False, "responsive": True},
        style={"height": height},
    )


app.layout = html.Div([
    dcc.Store(id="theme-store", data="dark"),

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    html.Div([
        # Marca
        html.Div([
            html.Span("🐟", style={"fontSize": "2rem"}),
            html.Div([
                html.Div("Desembarque",   className="brand-title"),
                html.Div("Pesquero · Chile", className="brand-sub"),
            ]),
        ], className="brand-row"),

        html.Hr(className="sidebar-hr"),

        html.Div("FILTROS GLOBALES", className="section-label"),

        # Año
        html.Div("Rango de Años", className="filter-label"),
        dcc.RangeSlider(
            id="year-range",
            min=ANOS[0], max=ANOS[-1],
            value=[ANOS[0], ANOS[-1]],
            step=1,
            marks={y: str(y) for y in range(ANOS[0], ANOS[-1] + 1, 5)},
            tooltip={"placement": "bottom", "always_visible": False},
            className="mb-4",
        ),

        # Región
        html.Div("Región", className="filter-label"),
        dcc.Dropdown(
            id="region-select",
            options=[{"label": r, "value": r} for r in REGIONS],
            multi=True,
            placeholder="Todas las regiones",
            className="dash-select mb-3",
        ),

        # Tipo agente
        html.Div("Tipo de Agente", className="filter-label"),
        dcc.Checklist(
            id="tipo-select",
            options=[{
                "label": html.Span([
                    html.Span(
                        "●",
                        style={
                            "color": TIPO_COLORS.get(ta, "#818cf8"),
                            "marginRight": "7px", "fontSize": "0.75rem",
                        },
                    ),
                    html.Span(ta),
                ], style={"display": "flex", "alignItems": "center"}),
                "value": ta,
            } for ta in TIPOS],
            value=TIPOS,
            className="tipo-checklist mb-3",
            labelStyle={"display": "flex", "cursor": "pointer", "padding": "4px 0"},
            inputStyle={"marginRight": "8px", "accentColor": "#6366f1"},
        ),

        # Aguas
        html.Div("Tipo de Aguas", className="filter-label"),
        dcc.RadioItems(
            id="aguas-select",
            options=[
                {"label": "Todas",              "value": "ALL"},
                {"label": "Nacionales (NAC)",    "value": "NAC"},
                {"label": "Internacionales (AI)","value": "AI"},
            ],
            value="ALL",
            className="mb-4",
            labelStyle={"display": "flex", "cursor": "pointer", "padding": "4px 0", "fontSize": "0.82rem"},
            inputStyle={"marginRight": "8px", "accentColor": "#6366f1"},
        ),

        html.Hr(className="sidebar-hr"),

        html.Button(
            "↺  Resetear Filtros",
            id="reset-btn",
            n_clicks=0,
            className="reset-btn",
        ),
    ], id="sidebar", className="sidebar dark-mode"),

    # ── CONTENIDO PRINCIPAL ───────────────────────────────────────────────────
    html.Div([

        # Header
        html.Div([
            html.Div([
                html.Span(
                    "Dashboard Desembarque Pesquero",
                    style={"fontWeight": "600", "fontSize": "1rem"},
                ),
                html.Span(" · Chile  ", style={"opacity": "0.35", "fontWeight": "300"}),
                html.Span(
                    "2000 – 2024",
                    style={"fontSize": "0.72rem", "opacity": "0.35", "marginLeft": "6px"},
                ),
            ], style={"display": "flex", "alignItems": "baseline"}),
            html.Button(
                "☀  Modo Claro",
                id="theme-toggle",
                n_clicks=0,
                className="theme-btn",
            ),
        ], id="header", className="header dark-mode"),

        # KPIs
        html.Div(id="kpi-row", className="mb-3"),

        # Timeline — ancho completo
        html.Div([
            G("timeline-fig", "220px"),
            html.Div(
                "\u2190  Arrastra el gr\u00e1fico para desplazarte en el tiempo  \u2192",
                className="chart-drag-hint",
            ),
        ], id="timeline-card", className="chart-card dark-mode mb-3"),

        # Mapa + Treemap
        dbc.Row([
            dbc.Col(
                html.Div(G("map-fig", "440px"), id="map-card", className="chart-card dark-mode"),
                width=6,
            ),
            dbc.Col(
                html.Div(G("treemap-fig", "440px"), id="treemap-card", className="chart-card dark-mode"),
                width=6,
            ),
        ], className="g-3 mb-3"),

        # Top Especies + Donut + Regiones
        dbc.Row([
            dbc.Col(
                html.Div(G("top-especies-fig", "360px"), id="top-card", className="chart-card dark-mode"),
                width=4,
            ),
            dbc.Col(
                html.Div(G("donut-fig", "360px"), id="donut-card", className="chart-card dark-mode"),
                width=4,
            ),
            dbc.Col(
                html.Div(G("region-fig", "360px"), id="region-card", className="chart-card dark-mode"),
                width=4,
            ),
        ], className="g-3 mb-3"),

    ], id="main-content", className="main-content"),

], id="app-root", className="app-root dark-mode")


# ══════════════════════════════════════════════════════════════════════════════
# 7. CALLBACKS
# ══════════════════════════════════════════════════════════════════════════════

# ── Toggle dark / light ──────────────────────────────────────────────────────
@app.callback(
    Output("theme-store",   "data"),
    Output("theme-toggle",  "children"),
    Output("app-root",      "className"),
    Output("sidebar",       "className"),
    Output("header",        "className"),
    Input("theme-toggle",   "n_clicks"),
    State("theme-store",    "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current):
    new   = "light" if current == "dark" else "dark"
    label = "🌙  Modo Oscuro" if new == "light" else "☀  Modo Claro"
    return (
        new,
        label,
        f"app-root {new}-mode",
        f"sidebar {new}-mode",
        f"header {new}-mode",
    )


# ── Resetear filtros ─────────────────────────────────────────────────────────
@app.callback(
    Output("year-range",    "value"),
    Output("region-select", "value"),
    Output("tipo-select",   "value"),
    Output("aguas-select",  "value"),
    Input("reset-btn",      "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return [ANOS[0], ANOS[-1]], None, TIPOS, "ALL"


# ── Dashboard principal ───────────────────────────────────────────────────────
CARD_IDS = ["timeline-card", "map-card", "treemap-card", "top-card", "donut-card", "region-card"]

@app.callback(
    Output("kpi-row",           "children"),
    Output("timeline-fig",      "figure"),
    Output("map-fig",           "figure"),
    Output("treemap-fig",       "figure"),
    Output("top-especies-fig",  "figure"),
    Output("donut-fig",         "figure"),
    Output("region-fig",        "figure"),
    *[Output(cid, "className") for cid in CARD_IDS],
    Input("theme-store",    "data"),
    Input("year-range",     "value"),
    Input("region-select",  "value"),
    Input("tipo-select",    "value"),
    Input("aguas-select",   "value"),
)
def update_dashboard(theme, year_range, regions, tipos, aguas):
    t        = THEMES[theme]
    card_cls = f"chart-card {theme}-mode"

    # Filtrado
    dff = df.copy()
    if year_range:
        dff = dff[(dff["ano"] >= year_range[0]) & (dff["ano"] <= year_range[1])]
    if regions:
        dff = dff[dff["region"].isin(regions)]
    if tipos:
        dff = dff[dff["tipo_agente"].isin(tipos)]
    else:
        dff = dff.iloc[0:0]  # vacío si no hay tipos seleccionados
    if aguas and aguas != "ALL":
        dff = dff[dff["aguas"] == aguas]

    return (
        make_kpi_cards(dff, t),
        chart_timeline(dff, t),
        chart_map(dff, t),
        chart_treemap(dff, t),
        chart_top_especies(dff, t),
        chart_donut(dff, t),
        chart_region_bar(dff, t),
        *([card_cls] * len(CARD_IDS)),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 8. ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)