"""
app.py — Factory Intelligence Framework
Main dashboard entry point.

Run with:
    python -m streamlit run app.py

This file sets up:
- Page layout and sidebar navigation
- Module routing (Module 1, 2, 3 + Summary)
- Global CSS theming for an industrial/technical aesthetic
"""

import streamlit as st

# ── Page config must be the very first Streamlit call ──────────────────────────
st.set_page_config(
    page_title="Factory Intelligence Framework",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import individual module renderers ─────────────────────────────────────────
from module1 import render_module1
from module2 import render_module2
from module3 import render_module3

# ── Global CSS — industrial-utilitarian theme ──────────────────────────────────
st.markdown("""
<style>
/* Import distinctive fonts */
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700&family=Barlow+Condensed:wght@600;700&display=swap');

/* Root palette */
:root {
    --bg-primary:    #0d1117;
    --bg-secondary:  #161b22;
    --bg-card:       #1c2333;
    --accent-amber:  #f0a500;
    --accent-teal:   #00c9a7;
    --accent-red:    #e05252;
    --text-primary:  #e6edf3;
    --text-muted:    #8b949e;
    --border:        #30363d;
}

/* ── Global overrides ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Barlow', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}

/* Sidebar text */
[data-testid="stSidebar"] {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] p, [data-testid="stSidebar"] div {
    font-family: 'Barlow', sans-serif;
}

/* Pengecualian agar ikon panah bawaan Streamlit tidak rusak */
[data-testid="stSidebarCollapseButton"] *, [data-testid="collapsedControl"] *, .stIconMaterial {
    font-family: 'Material Symbols Rounded', sans-serif !important;
}

/* Header branding */
.fif-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: var(--accent-amber);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.fif-subheader {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.6rem;
}

/* Module title */
.module-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-teal);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    border-bottom: 2px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 0.4rem;
}
.module-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    margin-bottom: 1.5rem;
}

/* Info card / concept box */
.concept-box {
    background: var(--bg-card);
    border-left: 4px solid var(--accent-amber);
    border-radius: 4px;
    padding: 1rem 1.2rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: var(--accent-amber);
    margin: 1.2rem 0;
    letter-spacing: 0.03em;
}

/* Summary table styling */
.summary-table th {
    background: var(--bg-card);
    color: var(--accent-amber);
    font-family: 'Barlow Condensed', sans-serif;
    letter-spacing: 0.06em;
}

/* Metric card */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    text-align: center;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.5rem;
    color: var(--accent-teal);
}
.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Streamlit widget label overrides */
label, .stSlider label, .stSelectbox label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent-amber) !important;
    color: var(--accent-amber) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--accent-amber) !important;
    color: var(--bg-primary) !important;
}

/* Dataframe / table */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}

/* Divider */
hr {
    border-color: var(--border) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: 0.06em !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
        <div style='font-family:"Barlow Condensed",sans-serif;font-size:1.3rem;
                    font-weight:700;color:#f0a500;letter-spacing:0.08em;
                    text-transform:uppercase;'>
            🏭 FIF
        </div>
        <div style='font-family:"Share Tech Mono",monospace;font-size:0.65rem;
                    color:#8b949e;letter-spacing:0.1em;'>
            Factory Intelligence Framework
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation selector
    page = st.radio(
        "Navigasi ke:",
        options=[
            "🏠  Ringkasan Utama",
            "📐  Modul 1 — Pemeta Tata Letak",
            "🔗  Modul 2 — Penganalisis Aliran",
            "🧭  Modul 3 — Keselarasan Aliran",
            "📊  Kesimpulan Akhir",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-family:\"Share Tech Mono\",monospace;font-size:0.6rem;"
        "color:#8b949e;line-height:1.8;'>"
        "ALJABAR LINEAR<br>TERAPAN UNTUK<br>TEKNIK INDUSTRI<br><br>"
        "v1.0 · 2026</div>",
        unsafe_allow_html=True,
    )


# ── Page routing ───────────────────────────────────────────────────────────────
if page == "🏠  Ringkasan Utama":
    # ── Hero header ────────────────────────────────────────────────────────────
    st.markdown(
        "<div class='fif-header'>Factory Intelligence Framework</div>"
        "<div class='fif-subheader'>Aljabar Linear Terapan untuk Teknik Industri · Dasbor 3-Modul</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    Selamat datang di **Factory Intelligence Framework** — sebuah dasbor interaktif yang 
    menerapkan konsep inti aljabar linear pada masalah teknik industri dunia nyata. 
    Gunakan menu navigasi di samping untuk berpindah antar modul.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>M1</div>
            <div class='metric-label'>Pemeta Tata Letak Fasilitas</div>
            <div style='font-size:0.72rem;color:#8b949e;margin-top:0.5rem;'>
                Matriks jarak Euclidean · Norma vektor · Vektor posisi 2D
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>M2</div>
            <div class='metric-label'>Penganalisis Aliran Rantai Pasok</div>
            <div style='font-size:0.72rem;color:#8b949e;margin-top:0.5rem;'>
                Matriks aliran · Determinan · Dekomposisi nilai eigen
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>M3</div>
            <div class='metric-label'>Penganalisis Keselarasan Aliran</div>
            <div style='font-size:0.72rem;color:#8b949e;margin-top:0.5rem;'>
                Produk titik (Dot product) · Proyeksi vektor · Ruang hasil kali dalam
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "**Cara menggunakan dasbor ini:** \n"
        "1. Buka setiap modul melalui menu navigasi di samping.  \n"
        "2. Ubah koordinat stasiun kerja dan nilai aliran menggunakan widget interaktif.  \n"
        "3. Semua perhitungan dan grafik akan diperbarui secara otomatis.  \n"
        "4. Gunakan tombol **Kembalikan ke Default** untuk memulihkan data sampel asli.  \n"
        "5. Kunjungi halaman **Kesimpulan Akhir** untuk melihat diagnosis keseluruhan sistem."
    )

elif page == "📐  Modul 1 — Pemeta Tata Letak":
    render_module1()

elif page == "🔗  Modul 2 — Penganalisis Aliran":
    render_module2()

elif page == "🧭  Modul 3 — Keselarasan Aliran":
    render_module3()

elif page == "📊  Kesimpulan Akhir":
    # ── Final Summary Section (Diagnosis Sistem) ───────────────────────────────
    st.markdown(
        "<div class='module-title'>Kesimpulan Eksekutif Sistem Produksi</div>"
        "<div class='module-subtitle'>Diagnosis Kinerja Berbasis Data · Ringkasan Dasbor</div>",
        unsafe_allow_html=True,
    )

    # 1. Pastikan session state tersedia (fallback jika user langsung buka menu ini)
    if "m1_coords" not in st.session_state:
        from module1 import DEFAULT_STATIONS
        st.session_state["m1_coords"] = {k: list(v) for k, v in DEFAULT_STATIONS.items()}
    if "m2_flow" not in st.session_state:
        from module2 import DEFAULT_FLOW
        st.session_state["m2_flow"] = DEFAULT_FLOW.copy()

    # 2. Ambil data dinamis untuk kalkulasi
    coords_dict = st.session_state["m1_coords"]
    F = st.session_state["m2_flow"]
    
    import numpy as np
    from itertools import combinations
    
    # Impor fungsi komputasi dari modul-modul sebelumnya
    from module3 import build_coords_array, compute_alignment
    from module2 import compute_influence_scores
    coords_array = build_coords_array(coords_dict)
    
    # Hitung total jarak fisik (M1)
    total_distance = 0
    for i, j in combinations(range(len(coords_array)), 2):
        total_distance += np.linalg.norm(coords_array[j] - coords_array[i])
        
    # Hitung aliran dan pengaruh (M2)
    total_flow = int(F.sum())
    eigenvalues, dominant_idx, scores, ranking = compute_influence_scores(F)
    top_influencer = ranking[0][0] if ranking[0][1] > 0 else "Tidak Ada"

    # Hitung keselarasan alur (M3)
    dom_axis, results, counts = compute_alignment(coords_array, F)
    well_aligned_routes = counts.get("Sangat Selaras", 0)
    total_active_routes = len(results)

    # 3. Render Kesimpulan Singkat Dinamis
    st.markdown("### 📊 Status Terkini Sistem Produksi")
    st.markdown("Berdasarkan konfigurasi tata letak dan aliran material saat ini, berikut adalah diagnosis sistem produksi Anda:")

    # Metrik Baris Atas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Jarak Perpindahan (M1)", f"{total_distance:.2f} meter")
    c2.metric("Total Aliran Harian (M2)", f"{total_flow} unit")
    c3.metric("Rute Sangat Selaras (M3)", f"{well_aligned_routes} dari {total_active_routes}")

    # Paragraf Deskriptif
    st.info(f"**Diagnosis Keseluruhan:** Pabrik saat ini menangani aliran material harian sebanyak **{total_flow} unit** dengan total jarak perpindahan struktural sejauh **{total_distance:.2f} meter**. Berdasarkan analisis nilai eigen, stasiun **{top_influencer}** memegang kendali paling besar terhadap ritme produksi (Skor Pengaruh tertinggi). Dari segi kesesuaian spasial, terdapat **{well_aligned_routes} rute aktif** yang letaknya sangat selaras dengan arah aliran dominan pabrik.")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # 4. Kesimpulan Singkat 3 Modul (Plain Language)
    st.markdown("<h3 style='font-family: \"Barlow Condensed\", sans-serif; color: var(--accent-amber);'>📌 Intisari Framework</h3>", unsafe_allow_html=True)
    st.markdown("Sebagai pengambil keputusan, ini adalah tiga pilar utama dari efisiensi pabrik yang dianalisis pada dasbor ini:")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.info("**Modul 1: Jarak Fisik**\n\nMengukur jauh-dekatnya posisi antar stasiun kerja. Tata letak yang baik menjaga stasiun agar tetap berdekatan demi meminimalkan waktu dan biaya pergerakan material.")
    with m2:
        st.warning("**Modul 2: Beban Rantai Pasok**\n\nMengevaluasi fleksibilitas rute dan volume material. Membantu menemukan stasiun mana yang memikul beban terberat sehingga rentan menjadi titik kemacetan (bottleneck).")
    with m3:
        st.success("**Modul 3: Keselarasan Alur**\n\nMemastikan posisi stasiun kerja di lantai pabrik searah dengan pergerakan material yang seharusnya, mencegah pekerja harus berjalan bolak-balik (inefisiensi).")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # 5. Exact Closing Statement
    st.markdown("""
    <div class='concept-box'>
    ▸ FRAMEWORK SELESAI<br><br>
    Semua output di atas diturunkan dari operasi aljabar linear yang diterapkan pada data teknik industri.<br><br>
    Modul 1 menggunakan ruang vektor Euclidean dan matriks jarak.<br>
    Modul 2 menggunakan determinan matriks dan dekomposisi nilai eigen.<br>
    Modul 3 menggunakan produk titik (dot product) dan proyeksi vektor untuk mengukur keselarasan fisik dan aliran.
    </div>
    """, unsafe_allow_html=True)