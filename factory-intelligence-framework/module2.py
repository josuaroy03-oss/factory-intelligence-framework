"""
module2.py — Supply Chain Flow Analyzer
========================================
LINEAR ALGEBRA CONCEPTS:
  Matrices, Determinants, Eigenvalues, Eigenvectors

The 5x5 flow matrix encodes daily material volumes between stations.
Its determinant measures linear independence of the flow relationships.
Eigenvalue decomposition identifies the dominant flow axis and ranks
stations by their systemic influence score (eigenvector centrality).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for Streamlit
import streamlit as st


# ── Nama Stasiun (harus sama dengan urutan di Modul 1) ────────────────────────
STATION_NAMES = ["Cutting", "Welding", "Assembly", "Painting", "Packaging"]

# ── Matriks aliran default 5x5 (unit/hari) ────────────────────────────────────
#    Baris i → Kolom j  artinya stasiun i mengirimkan volume tersebut ke stasiun j
DEFAULT_FLOW = np.array([
    #  Cut  Weld  Assy  Paint  Pack
    [  0,   30,   20,    0,    0  ],   # Cutting
    [  0,    0,   25,   15,    0  ],   # Welding
    [  0,    0,    0,   40,   35  ],   # Assembly
    [  0,    0,    0,    0,   20  ],   # Painting
    [  0,    0,    0,    0,    0  ],   # Packaging
], dtype=float)

# ── Palet Warna ───────────────────────────────────────────────────────────────
COLORS = ["#f0a500", "#00c9a7", "#e05252", "#7c85ff", "#ff6eb4"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Matematika & Logika Klasifikasi)
# ══════════════════════════════════════════════════════════════════════════════

def compute_determinant(F: np.ndarray) -> float:
    """Return the determinant of the flow matrix, rounded to 4 d.p."""
    return round(float(np.linalg.det(F)), 4)


def interpret_industrial_determinant(det_val: float) -> str:
    """Interpretasi industri dari nilai determinan (Indikator Hubungan Aliran)."""
    if abs(det_val) < 0.01:
        return (
            "**Aliran Sangat Bergantung (Sistem Kaku):** Indikator mendekati nol. "
            "Ini menunjukkan bahwa rute material sangat terikat satu sama lain. Jalur produksi "
            "bergantung pada rute yang spesifik dan berurutan, artinya gangguan di satu "
            "stasiun kemungkinan besar akan memicu efek berantai yang menghentikan stasiun lainnya."
        )
    else:
        return (
            "**Aliran Independen (Sistem Fleksibel):** Indikator bukan nol. "
            "Ini menunjukkan adanya rute-rute alternatif yang beragam dan independen. "
            "Sistem ini memiliki fleksibilitas struktural, sehingga lebih tangguh (resilient) "
            "terhadap gangguan lokal atau kemacetan."
        )


def compute_influence_scores(F: np.ndarray):
    """Dekomposisi nilai eigen dari matriks aliran."""
    raw_vals, raw_vecs = np.linalg.eig(F)
    eigenvalues  = raw_vals.real
    eigenvectors = raw_vecs.real

    dominant_idx = int(np.argmax(np.abs(eigenvalues)))
    dominant_vec = eigenvectors[:, dominant_idx]
    scores = np.abs(dominant_vec)

    if scores.max() > 0:
        scores = scores / scores.max()

    ranking = sorted(zip(STATION_NAMES, scores), key=lambda x: x[1], reverse=True)
    return eigenvalues, dominant_idx, scores, ranking


# ── FUNGSI KLASIFIKASI BARU ───────────────────────────────────────────────────

def classify_system_intensity(total_flow: float) -> tuple:
    """Mengklasifikasikan intensitas sistem berdasarkan total aliran matriks."""
    if total_flow < 100:
        return "Rendah", "Sistem beroperasi di bawah kapasitas optimal atau dalam skala kecil. Risiko kemacetan sangat minim."
    elif total_flow <= 250:
        return "Sedang", "Sistem beroperasi pada tingkat aktivitas standar dan stabil. Aliran material terkelola dengan baik."
    else:
        return "Tinggi", "Sistem produksi sangat aktif! Tingkat aliran ini mengindikasikan beban kerja yang berat dan risiko penumpukan material (bottleneck) yang tinggi."


def classify_relationship(flow_val: float) -> str:
    """Mengklasifikasikan kekuatan hubungan antar dua stasiun."""
    if flow_val == 0:
        return "Tidak Ada Hubungan"
    elif flow_val <= 15:
        return "Lemah"
    elif flow_val <= 30:
        return "Sedang"
    else:
        return "Kuat"


# ══════════════════════════════════════════════════════════════════════════════
# PLOT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def plot_flow_heatmap(F: np.ndarray) -> go.Figure:
    # Buat matriks teks custom yang menyertakan klasifikasi
    custom_text = []
    for i in range(len(STATION_NAMES)):
        row_text = []
        for j in range(len(STATION_NAMES)):
            val = F[i, j]
            cat = classify_relationship(val)
            row_text.append(f"Aliran: {val:.0f}<br>Kategori: {cat}")
        custom_text.append(row_text)

    fig = go.Figure(data=go.Heatmap(
        z=F,
        x=STATION_NAMES,
        y=STATION_NAMES,
        colorscale="Blues",
        text=F.astype(int),
        texttemplate="%{text}",
        textfont=dict(size=13, color="white"),
        customdata=custom_text,
        hovertemplate=(
            "Dari: %{y}<br>Ke: %{x}<br>"
            "%{customdata}<extra></extra>"
        ),
        colorbar=dict(
            title=dict(text="Unit / Hari", font=dict(color="#8b949e")),
            tickfont=dict(color="#8b949e"),
        )),
    )
    fig.update_layout(
        title=dict(text="Peta Panas (Heatmap) Matriks Aliran Material", font=dict(size=22, color="#f0a500")),
        xaxis=dict(title="Ke Stasiun", color="#8b949e", tickfont=dict(color="#e6edf3")),
        yaxis=dict(title="Dari Stasiun", color="#8b949e", tickfont=dict(color="#e6edf3"), autorange="reversed"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        margin=dict(l=40, r=20, t=60, b=40),
        height=420,
    )
    return fig


def plot_influence_scores(ranking: list) -> go.Figure:
    names  = [r[0] for r in ranking]
    scores = [round(r[1], 4) for r in ranking]
    bar_colors = [COLORS[STATION_NAMES.index(n)] for n in names]

    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.15)", width=0.8)),
        text=[f"{s:.4f}" for s in scores],
        textposition="outside",
        textfont=dict(color="#e6edf3", size=12),
        hovertemplate="%{y}: %{x:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Skor Pengaruh Sistem (Vektor Eigen)", font=dict(size=20, color="#f0a500")),
        xaxis=dict(title="Skor Pengaruh yang Dinormalisasi", color="#8b949e", gridcolor="#30363d", range=[0, 1.25]),
        yaxis=dict(color="#e6edf3", autorange="reversed"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        margin=dict(l=100, r=60, t=60, b=40),
        height=380,
    )
    return fig


def plot_eigenvalue_scatter(eigenvalues: np.ndarray, dominant_idx: int) -> go.Figure:
    colors_ev = ["#f0a500" if i == dominant_idx else "#00c9a7" for i in range(len(eigenvalues))]
    sizes = [20 if i == dominant_idx else 10 for i in range(len(eigenvalues))]

    fig = go.Figure()
    fig.add_hline(y=0, line_color="#30363d", line_width=1)

    fig.add_trace(go.Scatter(
        x=list(range(len(eigenvalues))),
        y=eigenvalues,
        mode="markers+text",
        marker=dict(color=colors_ev, size=sizes, line=dict(color="white", width=1.5)),
        text=[f"λ{i+1}={v:.3f}" for i, v in enumerate(eigenvalues)],
        textposition="top center",
        textfont=dict(color="#e6edf3", size=10),
        hovertemplate="λ%{x+1} = %{y:.4f}<extra></extra>",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=[dominant_idx],
        y=[eigenvalues[dominant_idx]],
        mode="markers",
        marker=dict(color="#f0a500", size=22, symbol="star", line=dict(color="white", width=1.5)),
        name=f"λ Dominan = {eigenvalues[dominant_idx]:.3f}",
    ))

    fig.update_layout(
        title=dict(text="Intensitas Sistem (Nilai Eigen)", font=dict(size=20, color="#f0a500")),
        xaxis=dict(
            title="Indeks Nilai Eigen", color="#8b949e", tickmode="array",
            tickvals=list(range(len(eigenvalues))),
            ticktext=[f"λ{i+1}" for i in range(len(eigenvalues))],
            gridcolor="#30363d",
        ),
        yaxis=dict(title="Nilai Eigen (Bagian Real)", color="#8b949e", gridcolor="#30363d"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        legend=dict(bgcolor="#1c2333", bordercolor="#30363d", borderwidth=1),
        margin=dict(l=50, r=20, t=60, b=40),
        height=340,
    )
    return fig


def plot_flow_network(F: np.ndarray, coords: np.ndarray = None) -> go.Figure:
    n = len(STATION_NAMES)
    if coords is None:
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        coords = np.column_stack([np.cos(angles) * 3, np.sin(angles) * 3])

    fig = go.Figure()
    max_flow = F.max() if F.max() > 0 else 1.0

    for i in range(n):
        for j in range(n):
            if F[i, j] > 0:
                width   = 1.0 + 5.0 * (F[i, j] / max_flow)
                opacity = 0.35 + 0.55 * (F[i, j] / max_flow)
                cat = classify_relationship(F[i, j])
                
                fig.add_trace(go.Scatter(
                    x=[coords[i, 0], coords[j, 0]],
                    y=[coords[i, 1], coords[j, 1]],
                    mode="lines",
                    line=dict(color=f"rgba(0,201,167,{opacity:.2f})", width=width),
                    hoverinfo="text",
                    text=(f"<b>{STATION_NAMES[i]} → {STATION_NAMES[j]}</b><br>"
                          f"Volume: {F[i,j]:.0f} unit/hari<br>"
                          f"Kategori Hubungan: {cat}"),
                    showlegend=False,
                ))

    out_flow = F.sum(axis=1)
    for idx in range(n):
        size = 18 + 20 * (out_flow[idx] / (out_flow.max() + 1e-9))
        fig.add_trace(go.Scatter(
            x=[coords[idx, 0]],
            y=[coords[idx, 1]],
            mode="markers+text",
            marker=dict(size=size, color=COLORS[idx], line=dict(color="white", width=2)),
            text=[STATION_NAMES[idx]],
            textposition="top center",
            textfont=dict(size=12, color="white"),
            name=STATION_NAMES[idx],
            hovertemplate=(f"<b>{STATION_NAMES[idx]}</b><br>Total aliran keluar: {out_flow[idx]:.0f} unit/hari<extra></extra>"),
        ))

    fig.update_layout(
        title=dict(text="Diagram Jaringan Aliran Material", font=dict(size=22, color="#f0a500")),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_module2():
    st.markdown("<h2 style='text-align: center;'>Modul 2 — Penganalisis Aliran Rantai Pasok</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'><i>Matriks Aliran · Determinan · Nilai Eigen (Eigenvalues) · Vektor Eigen (Eigenvectors)</i></p>", unsafe_allow_html=True)
    st.divider()

    if "m2_flow" not in st.session_state:
        st.session_state["m2_flow"] = DEFAULT_FLOW.copy()
    if "m2_editor_version" not in st.session_state:
        st.session_state["m2_editor_version"] = 0

    # ── Editable flow matrix panel ─────────────────────────────────────────────
    with st.expander("⚙️  Edit Matriks Aliran (unit / hari)", expanded=True):
        st.caption("Setiap sel [Baris, Kolom] adalah volume harian yang dikirim dari stasiun Baris ke stasiun Kolom.")

        df_editable = pd.DataFrame(st.session_state["m2_flow"], index=STATION_NAMES, columns=STATION_NAMES)
        editor_key = f"m2_flow_editor_v{st.session_state['m2_editor_version']}"
        edited_df = st.data_editor(df_editable, use_container_width=True, key=editor_key, num_rows="fixed")

        col_reset, col_info = st.columns([1, 3])
        with col_reset:
            if st.button("↺  Kembalikan ke Default", key="m2_reset"):
                st.session_state["m2_flow"] = DEFAULT_FLOW.copy()
                st.session_state["m2_editor_version"] += 1
                st.rerun()
        with col_info:
            st.caption("Tips: entri diagonal (stasiun -> dirinya sendiri) harus tetap bernilai 0.")

    F = edited_df.values.astype(float)
    st.session_state["m2_flow"] = F

    # ── Computations & Classifications ─────────────────────────────────────────
    det_val = compute_determinant(F)
    det_interpretation = interpret_industrial_determinant(det_val)
    eigenvalues, dominant_idx, scores, ranking = compute_influence_scores(F)
    dom_eigenvalue = eigenvalues[dominant_idx]

    total_system_flow = int(F.sum())
    intensity_category, intensity_desc = classify_system_intensity(total_system_flow)

    in_flow = F.sum(axis=0)
    out_flow = F.sum(axis=1)
    total_flow_per_station = in_flow + out_flow
    flow_ranking = sorted(zip(STATION_NAMES, total_flow_per_station), key=lambda x: x[1], reverse=True)
    
    top_influencer = ranking[0][0] if ranking[0][1] > 0 else "Tidak Ada"
    highest_flow_station = flow_ranking[0][0] if flow_ranking[0][1] > 0 else "Tidak Ada"

    # ── Plain Language Summary & Insights ──────────────────────────────────────
    st.markdown("### 🏭 Wawasan Produksi Industri")
    
    # Menampilkan Status Intensitas Sistem
    if intensity_category == "Rendah":
        st.success(f"**Intensitas Aliran Sistem: {intensity_category} ({total_system_flow} unit/hari)**\n\n{intensity_desc}")
    elif intensity_category == "Sedang":
        st.info(f"**Intensitas Aliran Sistem: {intensity_category} ({total_system_flow} unit/hari)**\n\n{intensity_desc}")
    else:
        st.error(f"**Intensitas Aliran Sistem: {intensity_category} ({total_system_flow} unit/hari)**\n\n{intensity_desc}")

    col_sum1, col_sum2 = st.columns(2)
    
    with col_sum1:
        st.info(f"**Pengaruh Sistem Tertinggi:**\n\n**{top_influencer}** memiliki Skor Pengaruh Sistem tertinggi. Ini berarti stasiun ini sangat menentukan ritme keseluruhan produksi. Setiap penundaan atau peningkatan efisiensi di stasiun ini akan memberikan efek berantai paling besar ke seluruh lini produksi.")
        
    with col_sum2:
        st.warning(f"**Indikator Potensi Hambatan (Bottleneck):**\n\n**{highest_flow_station}** menangani volume gabungan (material masuk & keluar) terbesar, yaitu **{flow_ranking[0][1]:.0f} unit/hari**. Stasiun ini adalah kandidat utama untuk dipantau secara ketat, karena tingginya sirkulasi material di sini berpotensi menyebabkan penumpukan/kemacetan.")

    st.success(f"{det_interpretation}")
    st.divider()

    # ── Status Kategori Tambahan untuk Metrik ──────────────────────────────────
    # Klasifikasi Determinan
    det_status = "Kaku (Bergantung)" if abs(det_val) < 0.01 else "Fleksibel (Independen)"
    
    # Klasifikasi Nilai Eigen Dominan (Momentum/Sirkulasi)
    if dom_eigenvalue < 10:
        eig_status = "Sirkulasi Rendah"
    elif dom_eigenvalue < 40:
        eig_status = "Sirkulasi Sedang"
    else:
        eig_status = "Sirkulasi Tinggi"

    # ── Key metrics row ────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            label="Indikator Hubungan Aliran", 
            value=f"{det_val:.4f}", 
            delta=f"Status: {det_status}", 
            delta_color="off", 
            help="Berasal dari Determinan Matriks. Mengevaluasi tingkat ketergantungan/kekakuan jalur."
        )
    with m2:
        st.metric(
            label="Intensitas Aliran Matematis", 
            value=f"{dom_eigenvalue:.4f}", 
            delta=f"Kategori: {eig_status}", 
            delta_color="off", 
            help="Berasal dari Nilai Eigen Dominan. Mengukur momentum keseluruhan sistem secara aljabar."
        )
    with m3:
        st.metric(
            label="Total Aliran Harian", 
            value=f"{total_system_flow} unit", 
            delta=f"Kategori: {intensity_category}", 
            delta_color="off"
        )
    with m4:
        st.metric(
            label="Rute Aliran Aktif", 
            value=f"{int(np.count_nonzero(F))}", 
            delta="Dari total 25 rute", 
            delta_color="off"
        )

    st.markdown("---")

    # ── Row: heatmap + network diagram ─────────────────────────────────────────
    col_heat, col_net = st.columns(2)
    with col_heat:
        st.plotly_chart(plot_flow_heatmap(F), use_container_width=True, key="m2_heatmap")
    with col_net:
        st.plotly_chart(plot_flow_network(F), use_container_width=True, key="m2_network")

    # ── Klasifikasi Hubungan Antar-Stasiun (Tabel Baru) ───────────────────────
    with st.expander("📊 Lihat Daftar Kategori Hubungan Antar-Stasiun", expanded=False):
        relationship_data = []
        for i in range(len(STATION_NAMES)):
            for j in range(len(STATION_NAMES)):
                if F[i, j] > 0:
                    val = F[i, j]
                    cat = classify_relationship(val)
                    relationship_data.append({
                        "Dari Stasiun": STATION_NAMES[i],
                        "Ke Stasiun": STATION_NAMES[j],
                        "Volume Aliran": int(val),
                        "Kategori Hubungan": cat
                    })
        
        if relationship_data:
            df_rel = pd.DataFrame(relationship_data).sort_values(by="Volume Aliran", ascending=False)
            st.dataframe(df_rel, use_container_width=True, hide_index=True)
            st.caption("Aturan Klasifikasi: Lemah (1-15), Sedang (16-30), Kuat (>30)")
        else:
            st.write("Tidak ada rute aliran yang aktif saat ini.")

    st.markdown("---")

    # ── Eigenvalue scatter + influence bar chart ───────────────────────────────
    col_eig, col_inf = st.columns(2)
    with col_eig:
        st.plotly_chart(plot_eigenvalue_scatter(eigenvalues, dominant_idx), use_container_width=True, key="m2_eigenvalues")
    with col_inf:
        st.plotly_chart(plot_influence_scores(ranking), use_container_width=True, key="m2_influence")

    # ── Station Influence Leaderboard table ────────────────────────────────────
    st.markdown("#### Papan Peringkat Pengaruh Stasiun")
    st.caption("Diurutkan berdasarkan Skor Pengaruh Sistem (dinormalisasi ke 1.0). Skor yang lebih tinggi menunjukkan bahwa stasiun tersebut memiliki kendali yang lebih besar atas aliran material ke hilir.")

    leaderboard_rows = []
    for rank, (name, score) in enumerate(ranking, start=1):
        bar_fill = int(score * 20)
        bar_str  = "█" * bar_fill + "░" * (20 - bar_fill)
        leaderboard_rows.append({
            "Peringkat": rank,
            "Stasiun": name,
            "Skor Pengaruh": round(score, 4),
            "Visual Dampak": bar_str,
        })

    st.dataframe(pd.DataFrame(leaderboard_rows), use_container_width=True, hide_index=True)

    # ── Full eigenvalue detail table ───────────────────────────────────────────
    with st.expander("📐  Di Balik Layar: Data Aljabar Linear"):
        ev_rows = []
        for i, lam in enumerate(eigenvalues):
            ev_rows.append({
                "Indeks": f"λ{i+1}",
                "Nilai Eigen (Bagian Real)": round(float(lam), 4),
                "|λ| (Nilai Absolut)": round(float(abs(lam)), 4),
                "Dominan?": "★ Ya (Penentu Intensitas)" if i == dominant_idx else "Tidak",
            })
        st.dataframe(pd.DataFrame(ev_rows), use_container_width=True, hide_index=True)
        st.caption("Nilai eigen dominan memiliki nilai absolut terbesar |λ|. Vektor eigen yang terkait dengannya lah yang digunakan untuk menetapkan Skor Pengaruh Sistem.")

    # ── Linear algebra concept box ─────────────────────────────────────────────
    st.info("""
    **Fondasi Matematis:**
    - **Matriks:** Matriks aliran mengkodekan pergerakan volume material harian antar stasiun kerja.
    - **Determinan:** *Indikator Hubungan Aliran* secara komputasi adalah determinan dari matriks tersebut, yang secara aljabar mengukur tingkat kebebasan linear rute-rute.
    - **Nilai Eigen & Vektor Eigen:** Diselesaikan melalui formula $Av = \lambda v$. *Intensitas Aliran Sistem* adalah nilai eigen dominan ($\\lambda$), yang mewakili sumbu aliran paling utama. *Skor Pengaruh Sistem* diturunkan secara langsung dari komponen vektor eigen dominan tersebut ($v$), mencerminkan sentralitas (pengaruh) masing-masing stasiun.
    """)

# Jika dijalankan sebagai script mandiri untuk testing:
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_module2()