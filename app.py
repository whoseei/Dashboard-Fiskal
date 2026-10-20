import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ------------------------------------------------------------------ CONFIG
st.set_page_config(page_title="Dashboard Fiskal 97 Kota", page_icon="📊", layout="wide")

# ------------------------------------------------------------------ TEMA (ubah warna di sini)
PRIMARY = "#6BAFA6"     # teal lembut
ACCENT = "#9CC5E0"      # biru langit lembut
PALETTE = ["#6BAFA6", "#86AEDB", "#E8A598", "#E8C57E", "#9CC5A1",
           "#E6AD82", "#7FC4C4", "#B5C99A", "#A3B8C8", "#D8A7A0"]
CSCALE = [[0, "#EAF4F2"], [0.5, "#9DCBC4"], [1, "#3F7F78"]]   # skala warna kontinu
TEXT = "#25343A"

tpl = pio.templates["plotly_white"].to_plotly_json()
pio.templates["fiskal"] = go.layout.Template(tpl)
pio.templates["fiskal"].layout.update(
    colorway=PALETTE,
    font=dict(family="Inter, Segoe UI, sans-serif", color="#1F2340"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    title=dict(font=dict(size=17)),
    xaxis=dict(gridcolor="rgba(120,120,160,0.15)", zeroline=False),
    yaxis=dict(gridcolor="rgba(120,120,160,0.15)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=60, l=10, r=10, b=10),
)
pio.templates.default = "fiskal"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .block-container {{ padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1400px; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* ---------- HERO ---------- */
    .hero {{
        background: linear-gradient(120deg, {PRIMARY} 0%, #8E7CF0 55%, {ACCENT} 120%);
        padding: 26px 32px; border-radius: 20px; color: white; margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(108,92,231,0.30);
    }}
    .hero h1 {{ margin: 0; font-size: 2rem; font-weight: 800; color: white; padding: 0; }}
    .hero p  {{ margin: 6px 0 0; opacity: .9; font-size: 0.98rem; }}

    /* ---------- KARTU KPI ---------- */
    div[data-testid="stMetric"] {{
        background: white;
        border: 1px solid rgba(108,92,231,0.12);
        border-left: 5px solid {PRIMARY};
        padding: 14px 16px; border-radius: 14px;
        box-shadow: 0 4px 14px rgba(31,35,64,0.06);
        transition: transform .15s ease, box-shadow .15s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(108,92,231,0.18);
    }}
    div[data-testid="stMetricLabel"] * {{
        white-space: normal !important; overflow: visible !important;
        text-overflow: clip !important; font-weight: 600; opacity: .75;
    }}
    div[data-testid="stMetricValue"] {{ font-weight: 800; color: #1F2340; }}

    /* ---------- TAB ---------- */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: none; }}
    .stTabs [data-baseweb="tab"] {{
        background: rgba(108,92,231,0.08); border-radius: 10px 10px 0 0;
        padding: 10px 18px; font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background: {PRIMARY} !important; color: white !important;
    }}
    .stTabs [aria-selected="true"] p {{ color: white !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #ECEEFA 0%, #DDE0F7 100%);
        border-right: 1px solid rgba(108,92,231,0.15);
    }}

    /* ---------- CHART CARD ---------- */
    div[data-testid="stPlotlyChart"] {{
        background: white; border-radius: 16px; padding: 8px;
        box-shadow: 0 4px 14px rgba(31,35,64,0.06);
        border: 1px solid rgba(108,92,231,0.08);
    }}
    div[data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}
    .stDownloadButton button {{
        background: {PRIMARY}; color: white; border: none; border-radius: 10px; font-weight: 600;
    }}
    .stDownloadButton button:hover {{ background: #5848d6; color: white; }}
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = "dataset_fiskal_97_hipoFull.csv"

TRANSFER = ["DBH_PAJAK", "DBH_SDA", "DBH_Lainnya", "DAU_Grant", "DAU_Earmark", "DAK_Fisik", "DAK_Nonfisik"]
BM = ["bm_pendidikan", "bm_kesehatan", "bm_perumahan", "bm_lingkungan",
      "bm_ekonomi", "bm_infrastruktur", "bm_pariwisata", "bm_perlindungan_sosial"]
OUTCOME = ["KEMISKINAN", "PENGANGGURAN", "KETIMPANGAN", "IPM", "PE"]
LABEL = {
    "KEMISKINAN": "Kemiskinan (%)", "PENGANGGURAN": "Pengangguran (%)",
    "KETIMPANGAN": "Ketimpangan (Gini)", "IPM": "IPM", "PE": "Pertumbuhan Ekonomi (%)",
    "PAD": "PAD", "ICT": "ICT",
}
# indikator di mana nilai LEBIH RENDAH = lebih baik
LOWER_BETTER = {"KEMISKINAN", "PENGANGGURAN", "KETIMPANGAN"}


@st.cache_data
def load(path):
    df = pd.read_csv(path)
    df["Kota"] = df["Kota"].str.replace(r"^Kota\s+", "", regex=True)
    df["Total_Transfer"] = df[TRANSFER].sum(axis=1)
    df["Total_BM"] = df[BM].sum(axis=1)
    return df


def pretty(c):
    return LABEL.get(c, c.replace("bm_", "BM ").replace("_", " ").title())


df = load(DATA_PATH)

# ------------------------------------------------------------------ SIDEBAR
st.sidebar.title("Filter")
y_min, y_max = int(df.Tahun.min()), int(df.Tahun.max())
yr = st.sidebar.slider("Rentang tahun", y_min, y_max, (y_min, y_max))
all_kota = sorted(df.Kota.unique())
sel_kota = st.sidebar.multiselect("Kota (kosong = semua)", all_kota)
sel_out = st.sidebar.selectbox("Indikator outcome utama", OUTCOME, format_func=pretty, index=3)

f = df[df.Tahun.between(*yr)]
if sel_kota:
    f = f[f.Kota.isin(sel_kota)]
if f.empty:
    st.warning("Tidak ada data untuk filter ini.")
    st.stop()

st.sidebar.caption(f"{f.Kota.nunique()} kota · {len(f):,} observasi")

# ------------------------------------------------------------------ HEADER + KPI
st.markdown(
    f"""<div class="hero">
        <h1>Dashboard Fiskal & Pembangunan 97 Kota</h1>
        <p>Periode {yr[0]}–{yr[1]} · transfer, PAD, belanja modal, dan outcome pembangunan</p>
    </div>""",
    unsafe_allow_html=True,
)

first, last = f[f.Tahun == f.Tahun.min()], f[f.Tahun == f.Tahun.max()]


def kpi(col, name, label=None, fmt="{:.2f}"):
    now, before = last[name].mean(), first[name].mean()
    delta = now - before
    good = (delta < 0) if name in LOWER_BETTER else (delta > 0)
    col.metric(label or pretty(name), fmt.format(now), f"{delta:+.2f}",
               delta_color=("normal" if good else "inverse") if name in OUTCOME else "off")


c = st.columns(6)
kpi(c[0], "IPM")
kpi(c[1], "KEMISKINAN")
kpi(c[2], "PENGANGGURAN")
kpi(c[3], "KETIMPANGAN")
kpi(c[4], "PE")
kpi(c[5], "PAD", fmt="{:.0f}")
st.caption("Nilai = rata-rata tahun terakhir; delta = selisih vs tahun pertama pada rentang terpilih.")

# ------------------------------------------------------------------ TABS
t1, t2, t3, t4, t5, t6 = st.tabs(
    ["Tren", "Transfer & PAD", "Belanja Modal", "Hubungan Fiskal–Outcome",
     "Peringkat Kota", "Data"]
)

# ---- Tab 1: Tren
with t1:
    a, b = st.columns(2)
    trend = f.groupby("Tahun")[OUTCOME].mean().reset_index()
    with a:
        fig = px.line(trend, x="Tahun", y=sel_out, markers=True,
                      title=f"Tren rata-rata {pretty(sel_out)}")
        fig.update_layout(yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        z = trend.copy()
        for k in OUTCOME:  # normalisasi 0-100 agar bisa dibandingkan
            z[k] = (z[k] - z[k].min()) / (z[k].max() - z[k].min() + 1e-9) * 100
        zl = z.melt("Tahun", var_name="Indikator", value_name="Skala 0–100")
        zl["Indikator"] = zl["Indikator"].map(pretty)
        fig = px.line(zl, x="Tahun", y="Skala 0–100", color="Indikator", markers=True,
                      title="Semua outcome (dinormalisasi min–max)")
        st.plotly_chart(fig, use_container_width=True)

    if sel_kota:
        lines = f.pivot_table(index="Tahun", columns="Kota", values=sel_out).reset_index()
        fig = px.line(lines.melt("Tahun", var_name="Kota", value_name=sel_out), x="Tahun",
                      y=sel_out, color="Kota", markers=True,
                      title=f"{pretty(sel_out)} per kota terpilih")
        st.plotly_chart(fig, use_container_width=True)

# ---- Tab 2: Transfer & PAD
with t2:
    a, b = st.columns([3, 2])
    comp = f.groupby("Tahun")[TRANSFER].mean().reset_index().melt("Tahun", var_name="Komponen", value_name="Rata-rata")
    with a:
        fig = px.area(comp, x="Tahun", y="Rata-rata", color="Komponen",
                      title="Komposisi transfer ke daerah (rata-rata per kota)")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        tot = f[TRANSFER].mean().reset_index()
        tot.columns = ["Komponen", "Nilai"]
        fig = px.pie(tot, names="Komponen", values="Nilai", hole=0.5,
                     title="Porsi komponen transfer (periode terpilih)")
        st.plotly_chart(fig, use_container_width=True)

    g = f.groupby("Tahun")[["PAD", "Total_Transfer"]].mean().reset_index()
    g["Rasio PAD / Transfer"] = g.PAD / g.Total_Transfer
    fig = go.Figure()
    fig.add_bar(x=g.Tahun, y=g.PAD, name="PAD")
    fig.add_bar(x=g.Tahun, y=g.Total_Transfer, name="Total Transfer")
    fig.add_scatter(x=g.Tahun, y=g["Rasio PAD / Transfer"], name="Rasio PAD/Transfer",
                    yaxis="y2", mode="lines+markers", line=dict(color="#FF7675", width=3))
    fig.update_layout(barmode="group", title="PAD vs Total Transfer (kemandirian fiskal)",
                      yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Rasio"))
    st.plotly_chart(fig, use_container_width=True)

# ---- Tab 3: Belanja Modal
with t3:
    a, b = st.columns(2)
    sec = f[BM].mean().sort_values().reset_index()
    sec.columns = ["Sektor", "Rata-rata"]
    sec["Sektor"] = sec["Sektor"].map(pretty)
    with a:
        fig = px.bar(sec, x="Rata-rata", y="Sektor", orientation="h",
                     title="Rata-rata belanja modal per sektor", color="Rata-rata",
                     color_continuous_scale=CSCALE)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        r = f[BM].mean()
        fig = go.Figure(go.Scatterpolar(r=list(r.values) + [r.values[0]],
                                        theta=[pretty(x) for x in BM] + [pretty(BM[0])],
                                        fill="toself", line=dict(color=PRIMARY), fillcolor="rgba(108,92,231,0.25)"))
        fig.update_layout(title="Profil belanja modal (radar)", polar=dict(radialaxis=dict(visible=True)))
        st.plotly_chart(fig, use_container_width=True)

    hm = f.groupby("Tahun")[BM].mean()
    hm.columns = [pretty(x) for x in hm.columns]
    fig = px.imshow(hm.T, aspect="auto", color_continuous_scale=CSCALE,
                    title="Heatmap belanja modal sektor × tahun")
    st.plotly_chart(fig, use_container_width=True)

# ---- Tab 4: Hubungan
with t4:
    drivers = TRANSFER + ["PAD", "ICT", "Total_Transfer", "Total_BM"] + BM
    a, b, c3 = st.columns(3)
    x = a.selectbox("Variabel fiskal (X)", drivers, index=drivers.index("PAD"), format_func=pretty)
    y = b.selectbox("Outcome (Y)", OUTCOME, index=OUTCOME.index(sel_out), format_func=pretty)
    colr = c3.selectbox("Warna titik", ["Tahun", "Tidak ada"])

    fig = px.scatter(f, x=x, y=y, color=("Tahun" if colr == "Tahun" else None),
                     hover_data=["Kota", "Tahun"], opacity=0.7,
                     title=f"{pretty(y)} vs {pretty(x)}")
    m, k = np.polyfit(f[x], f[y], 1)
    xs = np.linspace(f[x].min(), f[x].max(), 50)
    fig.add_scatter(x=xs, y=m * xs + k, mode="lines", name="Tren linear",
                    line=dict(color="#FF7675", dash="dash"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Korelasi Pearson = **{f[x].corr(f[y]):.3f}** (korelasi ≠ kausalitas).")

    cols = st.multiselect("Variabel untuk matriks korelasi",
                          TRANSFER + ["PAD", "ICT"] + BM + OUTCOME,
                          default=["DAU_Grant", "DAK_Fisik", "PAD", "ICT",
                                   "bm_pendidikan", "bm_kesehatan", "bm_infrastruktur"] + OUTCOME)
    if len(cols) >= 2:
        corr = f[cols].corr()
        fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1,
                        color_continuous_scale="RdBu_r", aspect="auto",
                        title="Matriks korelasi")
        fig.update_layout(height=650)
        st.plotly_chart(fig, use_container_width=True)

# ---- Tab 5: Peringkat
with t5:
    a, b = st.columns([1, 3])
    metric = a.selectbox("Metrik", OUTCOME + ["PAD", "Total_Transfer", "Total_BM", "ICT"],
                         index=OUTCOME.index(sel_out), format_func=pretty)
    topn = a.slider("Jumlah kota", 5, 30, 10)
    asc_default = metric in LOWER_BETTER
    order = a.radio("Urutan", ["Tertinggi", "Terendah"], index=1 if asc_default else 0)
    rk = f.groupby("Kota")[metric].mean().sort_values(ascending=(order == "Terendah")).head(topn)
    rk = rk.sort_values(ascending=(order != "Terendah")).reset_index()
    with b:
        fig = px.bar(rk, x=metric, y="Kota", orientation="h", color=metric,
                     color_continuous_scale=CSCALE,
                     title=f"Top {topn} kota — {order.lower()} {pretty(metric)}")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(height=max(350, 28 * topn))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bandingkan dua kota")
    ca, cb = st.columns(2)
    k1 = ca.selectbox("Kota A", all_kota, index=0)
    k2 = cb.selectbox("Kota B", all_kota, index=1)
    cmp_ = df[df.Kota.isin([k1, k2]) & df.Tahun.between(*yr)]
    cmp_m = cmp_.groupby("Kota")[OUTCOME + ["PAD", "ICT", "Total_Transfer", "Total_BM"]].mean().T
    cmp_m.index = [pretty(i) for i in cmp_m.index]
    st.dataframe(cmp_m.style.format("{:.2f}"), use_container_width=True)

# ---- Tab 6: Data
with t6:
    st.dataframe(f.sort_values(["Kota", "Tahun"]), use_container_width=True, height=450)
    st.download_button("⬇️ Unduh data terfilter (CSV)",
                       f.to_csv(index=False).encode("utf-8"),
                       "data_fiskal_terfilter.csv", "text/csv")
    with st.expander("Statistik deskriptif"):
        st.dataframe(f.drop(columns=["Kota"]).describe().T.style.format("{:.2f}"),
                     use_container_width=True)