#!/usr/bin/env python3
# dashboard.py — QSOT Interactive Control Center (v1.2.3)
import streamlit as st
import json
import subprocess
import time
import os
import sys
from pathlib import Path

# Add root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))

# Config
ARTIFACTS_DIR = Path("artifacts_dashboard")
RHO0_FILE = "rho0_tmp.json"
CHANS_FILE = "chans_tmp.json"

st.set_page_config(page_title="QSOT Compiler v1.2.3", layout="wide", page_icon="🌌")

# CSS: Prism 'Voidwalker' Theme [Drift-Free]
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max_width: 90%;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    section[data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    div.stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def get_file_content(filename):
    p = ARTIFACTS_DIR / filename
    return p.read_bytes() if p.exists() else None

def load_json(name):
    p = ARTIFACTS_DIR / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

# --- [SECTION 1] Sidebar Layout ---
with st.sidebar:
    st.markdown("## 🚀 Simulation Engine")
    
    # Controls
    if st.button("RUN SIMULATION", type="primary", width='stretch'):
        st.session_state['run_triggered'] = True
    
    st.markdown("---")
    
    # Parameters
    st.markdown("### ⚙️ Configuration")
    velocity = st.slider("Observer Velocity (β = v/c)", 0.0, 0.99, 0.5, 0.01, help="Simulates time dilation.")
    fixture = st.selectbox("Quantum Channel Model", 
        ["depolarizing_then_phase_damping", "quantum_chaos", "correlated_noise_with_ancilla_memory"],
        help="Select environmental noise model.")
        
    st.markdown("---")
    
    # Artifacts Download
    st.markdown("### 📥 Artifacts")
    if ARTIFACTS_DIR.exists():
        if (ARTIFACTS_DIR/"LAB_PROTOCOL.txt").exists():
            st.download_button("📜 Lab Protocol", get_file_content("LAB_PROTOCOL.txt"), "protocol.txt", width='stretch')
        if (ARTIFACTS_DIR/"qsot_state.npz").exists():
            st.download_button("💾 Raw State (NPZ)", get_file_content("qsot_state.npz"), "state.npz", width='stretch')
        if (ARTIFACTS_DIR/"trace.jsonl").exists():
            st.download_button("⛓️ Execution Trace", get_file_content("trace.jsonl"), "trace.jsonl", width='stretch')
        
        st.caption("Visualizations:")
        if (ARTIFACTS_DIR/"viz_kd_heatmap.png").exists():
            st.download_button("🖼️ KD Heatmap (PNG)", get_file_content("viz_kd_heatmap.png"), "kd_heatmap.png", mime="image/png", width='stretch')
        if (ARTIFACTS_DIR/"viz_entanglement.png").exists():
            st.download_button("🖼️ Entanglement Plot (PNG)", get_file_content("viz_entanglement.png"), "entanglement.png", mime="image/png", width='stretch')
        if (ARTIFACTS_DIR/"viz_gate_metrics.png").exists():
            st.download_button("🖼️ Gate Metrics (PNG)", get_file_content("viz_gate_metrics.png"), "gate_metrics.png", mime="image/png", width='stretch')
        if (ARTIFACTS_DIR/"viz_memory_kernel.png").exists():
            st.download_button("🖼️ Memory Kernel (PNG)", get_file_content("viz_memory_kernel.png"), "memory_kernel.png", mime="image/png", width='stretch')
    else:
        st.caption("No artifacts available yet.")


# --- [SECTION 2] Logic Execution (Triggered by Sidebar Button) ---
if st.session_state.get('run_triggered', False):
    st.info("🚀 Starting Simulation Pipeline...", icon="⚙️")
    with st.spinner(f"Compiling Quantum States (v={velocity}c)..."):
        try:
            # Determine path to scripts (relative to dashboard.py root)
            scripts_dir = root_dir / "scripts"
            
            env = os.environ.copy()
            env["PYTHONPATH"] = str(root_dir / "src") + os.pathsep + env.get("PYTHONPATH", "")
            
            # 1. Loader
            subprocess.run([sys.executable, str(root_dir / "src/qsot/utils/loader.py"), 
                            "--export-rho0", RHO0_FILE, 
                            "--export-channels", CHANS_FILE, "--fixture", fixture], check=True, env=env)
            
            # 2. Compiler
            subprocess.run([sys.executable, str(scripts_dir / "asdp_run.py"), 
                            "--rho0", RHO0_FILE, 
                            "--channels", CHANS_FILE, "--velocity", str(velocity), 
                            "--outdir", str(ARTIFACTS_DIR)], check=True, env=env)
            
            # 3. Visualizer
            subprocess.run([sys.executable, str(root_dir / "src/qsot/utils/visualizer.py"), 
                            "--dir", str(ARTIFACTS_DIR)], check=True, env=env)
            
            # 4. Optimizer
            subprocess.run([sys.executable, str(root_dir / "src/qsot/core/optimizer.py"), 
                            "--state", str(ARTIFACTS_DIR/"qsot_state.npz"),
                            "--out", str(ARTIFACTS_DIR/"optimization_result.json")], check=True, env=env)
            
            # 5. Protocol
            subprocess.run([sys.executable, str(root_dir / "src/qsot/core/protocol_gen.py"), 
                            "--opt-result", str(ARTIFACTS_DIR/"optimization_result.json"),
                            "--out", str(ARTIFACTS_DIR/"LAB_PROTOCOL.txt")], check=True, env=env)
            
            st.success("Compilation & Optimization Complete!")
            st.session_state['run_triggered'] = False # Reset trigger
            st.rerun()
            
        except Exception as e:
            st.error(f"Pipeline Failed: {e}")
            st.session_state['run_triggered'] = False

# --- [SECTION 3] Main View (Display) ---
st.title("⚛️ Flamehaven QSOT Compiler")
st.markdown("### v1.2.3: Causal Horizon Module (Relativistic Entanglement)")

if ARTIFACTS_DIR.exists():
    mem_rep = load_json("memory_report.json")
    opt_res = load_json("optimization_result.json")
    gate_rep = load_json("gate_report.json")
    ent_rep = load_json("entanglement_report.json")
    
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    if gate_rep: kpi1.metric("Axiom Integrity", "PASS" if gate_rep["pass"] else "FAIL")
    if mem_rep: kpi2.metric("Memory Depth", f"{mem_rep.get('depth', 0)} steps")
    if ent_rep:
        # Shorten metric name for display
        raw_metric = ent_rep.get('metric', 'Unknown')
        short_metric = raw_metric.split('(')[0].strip() # "L1 Coherence" or "Logarithmic Negativity"
        
        kpi3.metric("Avg Coherence", f"{ent_rep.get('avg_value', 0):.3f}")
        kpi4.metric("Metric Type", short_metric, help=raw_metric)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualizations", "🕸️ Entanglement", "🧠 Memory Kernel", "🔬 Lab Protocol"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            if (ARTIFACTS_DIR/"viz_kd_heatmap.png").exists(): 
                st.image(str(ARTIFACTS_DIR/"viz_kd_heatmap.png"), caption="Kirkwood-Dirac Q-Prob")
        with c2:
            if (ARTIFACTS_DIR/"viz_gate_metrics.png").exists():
                 st.image(str(ARTIFACTS_DIR/"viz_gate_metrics.png"), caption="Axiom Gate Metrics")
    
    with tab2:
        # Entanglement Stability & Metrics
        ec1, ec2 = st.columns([1, 3])
        with ec1:
            final_val = ent_rep.get("final_value", 0.0) if ent_rep else 0.0
            st.metric("Final Entanglement", f"{final_val:.4f}")
            
            stability = "Stable" if final_val > 1e-3 else "Collapsed"
            st.metric("State Stability", stability, 
                     delta="-Critical" if stability == "Collapsed" else "Healthy",
                     delta_color="normal" if stability == "Stable" else "inverse")
            
        with ec2:
            st.markdown(f"**Relativistic Entanglement Decay (Velocity: {velocity}c)**")
            if (ARTIFACTS_DIR/"viz_entanglement.png").exists(): 
                st.image(str(ARTIFACTS_DIR/"viz_entanglement.png"), width='stretch')

    with tab3:
        if (ARTIFACTS_DIR/"viz_memory_kernel.png").exists(): 
            st.image(str(ARTIFACTS_DIR/"viz_memory_kernel.png"), caption="Non-Markovian Memory Depth")
            
    with tab4:
        # Optimization Metrics
        p1, p2 = st.columns(2)
        optimized_val = opt_res.get("optimized_value", 0.0) if opt_res else 0.0
        p1.metric("Optimized KD Value", f"{optimized_val:.6f}")
        p2.metric("Non-Classicality", 
                  "Confirmed" if optimized_val < 0 else "Classical Bound",
                  delta="Quantum" if optimized_val < 0 else " Classical",
                  delta_color="normal" if optimized_val < 0 else "off")
                  
        st.markdown("### 🧬 Experimental Setup (Waveplate Angles)")
        if (ARTIFACTS_DIR/"LAB_PROTOCOL.txt").exists():
            st.code((ARTIFACTS_DIR/"LAB_PROTOCOL.txt").read_text(encoding="utf-8"))
            
        st.markdown("---")
        with st.expander("🔍 View Raw Optimization Result (JSON)"):
            if opt_res:
                st.json(opt_res)
            else:
                st.info("No optimization result found.")

else:
    st.info("👈 Use the **Simulation Engine** in the Sidebar to start.")