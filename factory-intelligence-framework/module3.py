"""
module3.py — Material Flow Alignment Analyzer
==============================================
LINEAR ALGEBRA CONCEPTS:
  Dot Product, Vector Projection, Inner Product Space

This module evaluates how well the physical factory layout aligns with
the dominant material flow direction using vector operations.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Konfigurasi Default (Jika Modul 1 & 2 belum dijalankan) ───────────────────
STATION_NAMES = ["Cutting", "Welding", "Assembly", "Painting", "Packaging"]

DEFAULT_STATIONS = {
    "Cutting":   (2, 5),
    "Welding":   (8, 3),
    "Assembly":  (5, 9),
    "Painting":  (1, 1),
    "Packaging": (9, 8),
}

DEFAULT_FLOW = np.array([
    [  0,   30,   20,    0,    0  ],
    [  0,    0,   25,   15,    0  ],
    [  0,    0,    0,   40,   35  ],
    [  0,    0,    0,    0,   20  ],
    [  0,    0,    0,    0,    0  ],
], dtype=float)

COLORS = ["#f0a500", "#00c9a7", "#e05252", "#7c85ff", "#ff6eb4"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Matematika Vektor)
# ══════════════════════════════════════════════════════════════════════════════

def build_coords_array(coords_dict: dict) -> np.ndarray:
    """Mengubah dictionary koordinat menjadi array numpy (N, 2)."""
    return np.array([coords_dict[s] for s in STATION_NAMES], dtype=float)

def compute_alignment(coords: np.ndarray, F: np.ndarray):
    """
    Menghitung vektor arah, sumbu dominan, dot product, dan status keselarasan.
    """
    n = len(STATION_NAMES)
    
    # 1. Menghitung vektor arah yang dinormalisasi & Sumbu Aliran Dominan
    dom_vector_sum = np.array([0.0, 0.0])
    active_paths = []
    
    for i in range(n):
        for j in range(n):
            if F[i, j] > 0:
                # Vektor arah fisik dari i ke j
                v_ij = coords[j] - coords[i]
                magnitude = np.linalg.norm(v_ij)
                
                if magnitude > 0:
                    v_norm = v_ij / magnitude
                else:
                    v_norm = np.array([0.0, 0.0])
                
                # Bobot vektor berdasarkan volume aliran
                dom_vector_sum += F[i, j] * v_norm
                
                active_paths.append({
                    "from_idx": i,
                    "to_idx": j,
                    "from_name": STATION_NAMES[i],
                    "to_name": STATION_NAMES[j],
                    "flow_vol": F[i, j],
                    "v_norm": v_norm,
                    "v_ij": v_ij
                })
    
    # Sumbu Dominan yang dinormalisasi
    dom_mag = np.linalg.norm(dom_vector_sum)
    dom_axis = dom_vector_sum / dom_mag if dom_mag > 0 else np.array([1.0, 0.0])
    
    # 2. Menghitung Dot Product dan Proyeksi untuk setiap rute aktif
    results = []
    counts = {"Sangat Selaras": 0, "Selaras Parsial": 0, "Tidak Selaras": 0}
    
    for path in active_paths:
        v_norm = path["v_norm"]
        # Dot product (cos theta)
        cos_theta = np.dot(v_norm, dom_axis)
        
        # Klasifikasi Keselarasan
        if cos_theta > 0.7:
            status = "Sangat Selaras (Alur Mendukung)"
            counts["Sangat Selaras"] += 1
            color = "#00c9a7" # Hijau
        elif 0 <= cos_theta <= 0.7:
            status = "Selaras Parsial (Ada Inefisiensi)"
            counts["Selaras Parsial"] += 1
            color = "#f0a500" # Oranye
        else:
            status = "Tidak Selaras (Pekerja Harus Berbalik)"
            counts["Tidak Selaras"] += 1
            color = "#e05252" # Merah
            
        # Magnitude Proyeksi = (v · axis / |axis|^2) * |axis| = cos_theta (karena |axis| = 1)
        proj_mag = cos_theta 
        
        results.append({
            "Rute Aliran": f"{path['from_name']} → {path['to_name']}",
            "Vektor Arah": f"[{v_norm[0]:.2f}, {v_norm[1]:.2f}]",
            "cos(θ)": round(cos_theta, 4),
            "Status Keselarasan": status,
            "Besaran Proyeksi": round(proj_mag, 4),
            "color": color,
            "from_idx": path["from_idx"],
            "to_idx": path["to_idx"],
        })
        
    return dom_axis, results, counts


# ══════════════════════════════════════════════════════════════════════════════
# PLOT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def plot_alignment_map(coords: np.ndarray, dom_axis: np.ndarray, results: list) -> go.Figure:
    """
    Membuat peta pabrik 2D interaktif dengan Plotly. 
    Menampilkan tanda panah untuk rute aliran (diwarnai berdasarkan keselarasan)
    dan panah besar untuk Sumbu Aliran Dominan.
    """
    fig = go.Figure()
    
    # Titik Pusat (Centroid) Pabrik
    centroid = np.mean(coords, axis=0)

    # 1. Menggambar Panah Rute Aliran
    for res in results:
        start = coords[res["from_idx"]]
        end = coords[res["to_idx"]]
        
        # Gunakan add_annotation untuk membuat panah di Plotly
        fig.add_annotation(
            x=end[0], y=end[1],
            ax=start[0], ay=start[1],
            xref="x", yref="y",
            axref="x", ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=res["color"],
            opacity=0.7,
            hovertext=f"{res['Rute Aliran']}<br>cos(θ): {res['cos(θ)']}<br>{res['Status Keselarasan']}"
        )

    # 2. Menggambar Sumbu Aliran Dominan (Panah Besar dari Centroid)
    # Skala panah dominan agar terlihat jelas di peta (dikali 3 unit)
    dom_end = centroid + (dom_axis * 3)
    
    fig.add_annotation(
        x=dom_end[0], y=dom_end[1],
        ax=centroid[0], ay=centroid[1],
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=2,
        arrowwidth=5,
        arrowcolor="#7c85ff", # Warna ungu menonjol
        text="<b>SUMBU DOMINAN</b>",
        font=dict(color="#7c85ff", size=14)
    )

    # 3. Menggambar Titik Stasiun Kerja
    for idx, name in enumerate(STATION_NAMES):
        fig.add_trace(go.Scatter(
            x=[coords[idx, 0]],
            y=[coords[idx, 1]],
            mode="markers+text",
            marker=dict(size=22, color=COLORS[idx], line=dict(color="white", width=2)),
            text=[name],
            textposition="top center",
            textfont=dict(size=14, color="white"),
            name=name,
            hovertemplate=f"<b>{name}</b><br>X: {coords[idx,0]}<br>Y: {coords[idx,1]}<extra></extra>",
            showlegend=False
        ))

    # Kustomisasi Layout
    fig.update_layout(
        title=dict(text="Peta Keselarasan Aliran Material (Alignment Map)", font=dict(size=22, color="#f0a500"), x=0.5, xanchor='center'),
        xaxis=dict(title=dict(text="Koordinat X (m)", font=dict(size=14)), gridcolor="#30363d", range=[-2, 17], zeroline=False, color="#8b949e"),
        yaxis=dict(title=dict(text="Koordinat Y (m)", font=dict(size=14)), gridcolor="#30363d", range=[-2, 17], zeroline=False, color="#8b949e"),
        plot_bgcolor="#161b22",
        paper_bgcolor="#0d1117",
        font=dict(color="#e6edf3"),
        margin=dict(l=60, r=60, t=80, b=60),
        height=650,
    )
    
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_module3():
    st.markdown("<h2 style='text-align: center;'>Modul 3 — Penganalisis Keselarasan Aliran Fisik</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'><i>Produk Titik (Dot Product) · Proyeksi Vektor · Ruang Hasil Kali Dalam (Inner Product Space)</i></p>", unsafe_allow_html=True)
    st.divider()

    # ── Mengambil Data dari Session State (Modul 1 & 2) ────────────────────────
    # Jika state belum ada (user langsung buka modul 3), gunakan default
    if "m1_coords" not in st.session_state:
        st.session_state["m1_coords"] = {k: list(v) for k, v in DEFAULT_STATIONS.items()}
    if "m2_flow" not in st.session_state:
        st.session_state["m2_flow"] = DEFAULT_FLOW.copy()

    coords = build_coords_array(st.session_state["m1_coords"])
    F = st.session_state["m2_flow"]

    # ── Komputasi Vektor ───────────────────────────────────────────────────────
    dom_axis, results, counts = compute_alignment(coords, F)

    # ── Ringkasan Dasbor (KPI) ─────────────────────────────────────────────────
    st.markdown("### 🎯 Ringkasan Status Keselarasan Tata Letak")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; background-color: rgba(0, 201, 167, 0.1); border-radius: 8px; border: 1px solid #00c9a7;">
                <div style="color: #00c9a7; font-size: 1.2rem; font-weight: bold;">Sangat Selaras</div>
                <div style="color: #e6edf3; font-size: 2.5rem; font-weight: bold;">{counts['Sangat Selaras']} <span style="font-size: 1rem;">Rute</span></div>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; background-color: rgba(240, 165, 0, 0.1); border-radius: 8px; border: 1px solid #f0a500;">
                <div style="color: #f0a500; font-size: 1.2rem; font-weight: bold;">Selaras Parsial</div>
                <div style="color: #e6edf3; font-size: 2.5rem; font-weight: bold;">{counts['Selaras Parsial']} <span style="font-size: 1rem;">Rute</span></div>
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; background-color: rgba(224, 82, 82, 0.1); border-radius: 8px; border: 1px solid #e05252;">
                <div style="color: #e05252; font-size: 1.2rem; font-weight: bold;">Tidak Selaras</div>
                <div style="color: #e6edf3; font-size: 2.5rem; font-weight: bold;">{counts['Tidak Selaras']} <span style="font-size: 1rem;">Rute</span></div>
            </div>
            """, unsafe_allow_html=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Peta Keselarasan ───────────────────────────────────────────────────────
    st.plotly_chart(plot_alignment_map(coords, dom_axis, results), use_container_width=True)

    # Legenda Peta (Manual HTML)
    st.markdown(
        """
        <div style="display: flex; justify-content: center; gap: 20px; font-size: 14px; color: #8b949e;">
            <div><span style="color: #00c9a7;">🟢 ➔</span> Sangat Selaras (Mendukung Alur)</div>
            <div><span style="color: #f0a500;">🟠 ➔</span> Selaras Parsial (Ada Inefisiensi)</div>
            <div><span style="color: #e05252;">🔴 ➔</span> Tidak Selaras (Berbalik Arah)</div>
            <div><span style="color: #7c85ff;">🟣 ➔</span> <b>Sumbu Aliran Dominan</b></div>
        </div>
        """, unsafe_allow_html=True
    )
    
    st.divider()

    # ── Tabel Hasil Analisis Vektor ────────────────────────────────────────────
    st.markdown("### 📐 Data Analisis Produk Titik & Proyeksi")
    st.caption("Menunjukkan kalkulasi sudut (cos θ) antara vektor pergerakan antar-stasiun terhadap Sumbu Aliran Dominan pabrik.")
    
    # Filter dictionary keys to only match required columns
    table_data = [
        {
            "Rute Aliran": r["Rute Aliran"],
            "Vektor Arah": r["Vektor Arah"],
            "cos(θ)": r["cos(θ)"],
            "Status Keselarasan": r["Status Keselarasan"],
            "Besaran Proyeksi": r["Besaran Proyeksi"]
        } for r in results
    ]
    
    df_results = pd.DataFrame(table_data)
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    # ── Educational Concept Box ────────────────────────────────────────────────
    st.info("""
    **LINEAR ALGEBRA CONCEPT USED:** *Dot Product, Vector Projection, Inner Product Space*
    
    The dot product $\\vec{a} \\cdot \\vec{b} = \\|\\vec{a}\\|\\|\\vec{b}\\|\\cos(\\theta)$ quantifies directional alignment between the physical layout and the material flow. A dot product near 1 means the layout efficiently supports the flow direction. Vector projection measures how much each flow path follows the factory's dominant movement axis.
    """)

# Jika dijalankan sebagai script mandiri untuk testing:
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    render_module3()