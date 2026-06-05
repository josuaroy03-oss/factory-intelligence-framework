"""
module1.py — Facility Layout Mapper
====================================
LINEAR ALGEBRA CONCEPTS:
  Vectors, Euclidean Vector Space, Vector Norms, Distance Matrix

Each workstation is stored as a 2D position vector.
Pairwise Euclidean distances are computed using the vector norm:
  dist(i, j) = sqrt((x2-x1)² + (y2-y1)²)
The full result is stored as a 5x5 numpy distance matrix.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for Streamlit
import streamlit as st
from itertools import combinations

# ── Default sample data ────────────────────────────────────────────────────────
DEFAULT_STATIONS = {
    "Cutting":   (2, 5),
    "Welding":   (8, 3),
    "Assembly":  (5, 9),
    "Painting":  (1, 1),
    "Packaging": (9, 8),
}

STATION_NAMES = list(DEFAULT_STATIONS.keys())

# ── Colour palette ────────────────────────────────────────────────────────────
COLORS = ["#f0a500", "#00c9a7", "#e05252", "#7c85ff", "#ff6eb4"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def build_coords_array(coords_dict: dict) -> np.ndarray:
    """Convert {name: (x,y)} dict → (N,2) numpy array of position vectors."""
    return np.array([coords_dict[s] for s in STATION_NAMES], dtype=float)


def compute_distance_matrix(coords: np.ndarray) -> np.ndarray:
    """
    Compute the full NxN Euclidean distance matrix.
    Formula: dist(i,j) = ||pos_j - pos_i||_2 = sqrt((x2-x1)²+(y2-y1)²)
    """
    n = len(coords)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            diff = coords[j] - coords[i]          # vector subtraction
            D[i, j] = np.linalg.norm(diff)        # Euclidean norm
    return D


def ranked_pairs(D: np.ndarray) -> list:
    """
    Return list of (station_i, station_j, distance) tuples sorted
    from farthest to closest (only upper-triangle, 10 unique pairs).
    """
    pairs = []
    for i, j in combinations(range(len(STATION_NAMES)), 2):
        pairs.append((STATION_NAMES[i], STATION_NAMES[j], D[i, j]))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs


# ══════════════════════════════════════════════════════════════════════════════
# PLOT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def plot_factory_floor(coords: np.ndarray, D: np.ndarray) -> go.Figure:
    """
    Interactive Plotly factory floor map.
    """
    fig = go.Figure()
    n = len(STATION_NAMES)
    max_dist = D.max() if D.max() > 0 else 1.0

    # Draw lines between every pair of stations
    for i, j in combinations(range(n), 2):
        d = D[i, j]
        opacity = 0.25 + 0.65 * (d / max_dist)
        width   = 1.0  + 4.0  * (d / max_dist)

        fig.add_trace(go.Scatter(
            x=[coords[i, 0], coords[j, 0]],
            y=[coords[i, 1], coords[j, 1]],
            mode="lines",
            line=dict(color=f"rgba(200,200,200,{opacity:.2f})", width=width),
            hoverinfo="text",
            text=f"{STATION_NAMES[i]} ↔ {STATION_NAMES[j]}: {d:.2f} meter",
            showlegend=False,
        ))

    # Draw station nodes
    for idx, name in enumerate(STATION_NAMES):
        fig.add_trace(go.Scatter(
            x=[coords[idx, 0]],
            y=[coords[idx, 1]],
            mode="markers+text",
            marker=dict(size=26, color=COLORS[idx],
                        line=dict(color="white", width=3)),
            text=[name],
            textposition="top center",
            textfont=dict(family="Arial", size=16, color="white"),
            name=name,
            hovertemplate=f"<b>{name}</b><br>X: {coords[idx,0]}<br>Y: {coords[idx,1]}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(
            text="Peta Tata Letak Pabrik Interaktif",
            font=dict(size=26, color="#f0a500"), 
            x=0.5, 
            xanchor='center'
        ), 
        xaxis=dict(title=dict(text="Koordinat X (m)", font=dict(size=14)), 
                   gridcolor="#30363d", range=[-1, 16], zeroline=False, color="#8b949e"),
        yaxis=dict(title=dict(text="Koordinat Y (m)", font=dict(size=14)), 
                   gridcolor="#30363d", range=[-1, 16], zeroline=False, color="#8b949e"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        margin=dict(l=60, r=60, t=80, b=60),
        height=650, 
    )
    return fig


def plot_distance_heatmap(D: np.ndarray) -> go.Figure:
    """Interactive Plotly heatmap of the Euclidean distance matrix."""
    fig = go.Figure(data=go.Heatmap(
        z=np.round(D, 2),
        x=STATION_NAMES,
        y=STATION_NAMES,
        colorscale="YlOrRd",
        text=np.round(D, 2),
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=16), 
        hovertemplate="Dari: %{y}<br>Ke: %{x}<br>Jarak: %{z:.2f} meter<extra></extra>",
        colorbar=dict(
            title=dict(text="Jarak (meter)", font=dict(color="#8b949e", size=14)),
            tickfont=dict(color="#8b949e", size=12)
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="Matriks Jarak Euclidean",
            font=dict(size=26, color="#f0a500"), 
            x=0.5, 
            xanchor='center'
        ), 
        xaxis=dict(title=dict(text="Ke Stasiun", font=dict(size=16)), 
                   color="#8b949e", tickfont=dict(color="#e6edf3", size=14)),
        yaxis=dict(title=dict(text="Dari Stasiun", font=dict(size=16)), 
                   color="#8b949e", tickfont=dict(color="#e6edf3", size=14), autorange="reversed"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        margin=dict(l=80, r=60, t=80, b=60),
        height=650, 
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_module1():
    """Render Module 1 — Facility Layout Mapper inside Streamlit."""

    st.markdown("<h2 style='text-align: center;'>Module 1 — Pemeta Tata Letak Pabrik</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'><i>Matriks Jarak Euclidean · Vektor Posisi 2D · Analisis Efisiensi</i></p>", unsafe_allow_html=True)
    st.divider()

    # ── Session-state initialisation ───────────────────────────────────────────
    if "m1_coords" not in st.session_state:
        st.session_state["m1_coords"] = {k: list(v) for k, v in DEFAULT_STATIONS.items()}

    def reset_module1():
        for k, v in DEFAULT_STATIONS.items():
            st.session_state["m1_coords"][k] = list(v)
            st.session_state[f"m1_x_{k}"] = v[0]
            st.session_state[f"m1_y_{k}"] = v[1]

    # ── Interactive Sidebar-style controls ─────────────────────────────────────
    st.markdown("### ⚙️ Sesuaikan Koordinat Stasiun Kerja")
    st.caption("Geser slider untuk memindahkan stasiun. Matriks jarak dan peta akan diperbarui secara instan.")
    
    cols = st.columns(5)
    for idx, name in enumerate(STATION_NAMES):
        with cols[idx]:
            st.markdown(f"<strong style='color:{COLORS[idx]}; font-size: 1.1em;'>{name}</strong>", unsafe_allow_html=True)
            x_val = st.slider(f"X — {name}", 0, 15, int(st.session_state["m1_coords"][name][0]), key=f"m1_x_{name}")
            y_val = st.slider(f"Y — {name}", 0, 15, int(st.session_state["m1_coords"][name][1]), key=f"m1_y_{name}")
            st.session_state["m1_coords"][name] = [x_val, y_val]

    st.button("↺ Kembalikan ke Tata Letak Default", on_click=reset_module1, type="secondary")
    st.divider()

    # ── Compute Core Metrics ───────────────────────────────────────────────────
    coords = build_coords_array(st.session_state["m1_coords"])
    D = compute_distance_matrix(coords)
    pairs = ranked_pairs(D)
    total_efficiency = sum([d for _, _, d in pairs])

    # ── CEK TUMPANG TINDIH (OVERLAP WARNING) ───────────────────────────────────
    overlapping_pairs = [ (a, b) for a, b, d in pairs if d == 0.0 ]
    if overlapping_pairs:
        for p in overlapping_pairs:
            st.warning(f"**PERINGATAN:** Stasiun **{p[0]}** dan **{p[1]}** berada di titik koordinat yang persis sama! Harap geser salah satu stasiun untuk menghindari tumpukan fisik di lantai pabrik.", icon="⚠️")

    # ── Visualizations (Disusun Vertikal dan Besar) ────────────────────────────
    
    # 1. Peta Tata Letak
    st.plotly_chart(plot_factory_floor(coords, D), use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True) # Jarak estetik
    
    # 2. Matriks Jarak
    st.plotly_chart(plot_distance_heatmap(D), use_container_width=True)

    st.divider()

    # ── KESIMPULAN EFISIENSI (EFFICIENCY CONCLUSION) ───────────────────────────
    st.markdown("<h3 style='text-align: center;'>🎯 Kesimpulan Efisiensi Tata Letak</h3>", unsafe_allow_html=True)
    
    # Menampilkan metrik utama di tengah menggunakan HTML/CSS custom agar rata tengah
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1.5rem; background-color: #161b22; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 1.5rem;">
            <div style="color: #8b949e; font-size: 1rem; margin-bottom: 0.5rem;" title="Jumlah dari semua jarak Euclidean antar pasangan stasiun.">
                Total Jarak Tata Letak (Makin rendah makin baik)
            </div>
            <div style="color: #f0a500; font-size: 2.8rem; font-weight: bold; font-family: sans-serif;">
                {total_efficiency:.2f} <span style="font-size: 1.5rem; color: #e6edf3;">meter</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Rentang efisiensi
    if total_efficiency < 60:
        st.success(f"**Status: SANGAT EFISIEN** ✅\n\nTotal perpindahan material berada di angka **{total_efficiency:.2f} meter**. Tata letak saat ini sudah sangat optimal. Stasiun kerja saling berdekatan sehingga meminimalkan biaya logistik internal.")
    elif total_efficiency < 85:
        st.info(f"**Status: CUKUP EFISIEN** ⚠️\n\nTotal perpindahan material adalah **{total_efficiency:.2f} meter**. Tata letak ini dapat diterima, namun masih ada ruang untuk dioptimalkan dengan cara mendekatkan stasiun-stasiun yang letaknya berjauhan.")
    else:
        st.error(f"**Status: TIDAK EFISIEN** ❌\n\nTotal perpindahan material mencapai **{total_efficiency:.2f} meter**! Tata letak ini terlalu menyebar. Sangat disarankan untuk merombak posisi agar stasiun utama lebih berdekatan satu sama lain demi menghemat waktu perakitan.")

    # ── STANDAR ACUAN RENTANG (REVISI DOSEN) ───────────────────────────────────
    st.caption("📋 **Acuan Standar Rentang Efisiensi Total Jarak:**\n"
               "- **< 60 meter:** Sangat Efisien (Aktivitas perpindahan minimal & hemat ruang)\n"
               "- **60 - 85 meter:** Cukup Efisien (Standar operasional wajar, namun masih ada ruang optimasi)\n"
               "- **> 85 meter:** Tidak Efisien (Pemborosan pergerakan material, risiko delay produksi tinggi)")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Dynamic Relocation Insights ────────────────────────────────────────────
    farthest_a, farthest_b, farthest_d = pairs[0]
    closest_a, closest_b, closest_d = pairs[-1]

    col_insight1, col_insight2 = st.columns(2)
    with col_insight1:
        st.error(f"**🚨 Prioritas Relokasi:**\n\n**{farthest_a}** dan **{farthest_b}** adalah yang paling berjauhan pada **{farthest_d:.2f} meter**.")
        st.caption("Pertimbangkan untuk mendekatkan keduanya guna mengurangi jarak tempuh material utama.")
        
    with col_insight2:
        if closest_d == 0.0:
            st.warning(f"**⚠️ Tumpang Tindih:**\n\n**{closest_a}** dan **{closest_b}** bertabrakan (0 meter).")
            st.caption("Segera pisahkan stasiun ini.")
        else:
            st.success(f"**✅ Sinergi Terkuat:**\n\n**{closest_a}** dan **{closest_b}** adalah yang terdekat pada **{closest_d:.2f} meter**.")
            st.caption("Alur kedua stasiun ini sangat efisien. Pertahankan posisi mereka.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Educational Concept Box ────────────────────────────────────────────────
    st.info("""
    **Konsep Aljabar Linear yang Digunakan:**
    - **Vektor:** Setiap stasiun kerja direpresentasikan sebagai vektor posisi $v = [x, y]$ dalam ruang Euclidean 2D.
    - **Norma Euclidean:** Jarak antar stasiun dihitung menggunakan formula norma: $d(i, j) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$.
    - **Matriks Jarak (Distance Matrix):** Semua perbandingan berpasangan dikompilasi menjadi matriks simetris $n \\times n$ dengan nilai nol pada diagonal utama (karena jarak stasiun ke dirinya sendiri adalah 0).
    """)

# If running as a standalone script for testing:
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_module1()