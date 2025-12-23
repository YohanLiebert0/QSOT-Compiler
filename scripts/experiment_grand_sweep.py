# experiment_grand_sweep.py - Generate Paper Data
# Fully ASCII-safe version for Windows

import numpy as np
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "src"))

def create_superposition():
    rho = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)
    return rho

print("=" * 60)
print("[QSOT] Paper Data Generation - Velocity Sweep")
print("=" * 60)

# 1. Create initial state
print("\n[1/3] Creating superposition state...")
rho0 = create_superposition()
rho0_file = Path("rho0_super.json")
with open(rho0_file, "w") as f:
    json.dump({"re": rho0.real.tolist(), "im": rho0.imag.tolist()}, f)
print("  OK: rho0_super.json created")

# 2. Generate channels
print("\n[2/3] Generating quantum channels...")
channels_file = Path("channels_sweep.json")
try:
    subprocess.run([
        sys.executable,
        str(root / "src/qsot/utils/loader.py"),
        "--fixture", "depolarizing_then_phase_damping",
        "--export-channels", str(channels_file)
    ], check=True, capture_output=True)
    print("  OK: channels_sweep.json created")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# 3. Run sweep
print("\n[3/3] Running velocity sweep...")
velocities = np.linspace(0.0, 0.99, 20)
results = []

sweep_dir = Path("sweep_data")
sweep_dir.mkdir(exist_ok=True)

for i, v in enumerate(velocities):
    print(f"  [{i+1:2d}/20] v={v:.3f}c...", end="", flush=True)
    
    outdir = sweep_dir / f"v_{v:.3f}"
    outdir.mkdir(exist_ok=True)
    
    try:
        subprocess.run([
            sys.executable,
            str(root / "scripts/asdp_run.py"),
            "--rho0", str(rho0_file),
            "--channels", str(channels_file),
            "--velocity", str(v),
            "--outdir", str(outdir)
        ], check=True, capture_output=True, timeout=30)
        
        ent_file = outdir / "entanglement_report.json"
        mem_file = outdir / "memory_report.json"
        
        if ent_file.exists() and mem_file.exists():
            ent_data = json.loads(ent_file.read_text())
            mem_data = json.loads(mem_file.read_text())
            
            q_corr = ent_data.get("final_value", 0.0)
            nm_val = mem_data.get("nm_measure", 0.0)
            
            results.append({
                "velocity": v,
                "quantum_correlation": q_corr,
                "memory_backflow": nm_val
            })
            print(f" OK (Q={q_corr:.4f})")
        else:
            print(" MISSING FILES")
            results.append({"velocity": v, "quantum_correlation": 0.0, "memory_backflow": 0.0})
            
    except Exception as e:
        print(f" ERROR")
        results.append({"velocity": v, "quantum_correlation": 0.0, "memory_backflow": 0.0})

# 4. Save results
print("\n[EXPORT] Saving results...")
import pandas as pd
df = pd.DataFrame(results)
df.to_csv("paper_data_final.csv", index=False)
print(f"  OK: paper_data_final.csv created ({len(df)} points)")

print("\n[SUMMARY]")
print(f"  Q Range: [{df['quantum_correlation'].min():.4f}, {df['quantum_correlation'].max():.4f}]")
print(f"  NM Range: [{df['memory_backflow'].min():.4f}, {df['memory_backflow'].max():.4f}]")

critical = df[df['quantum_correlation'] < 0.1]
if not critical.empty:
    v_c = critical.iloc[0]['velocity']
    print(f"  Critical velocity: v_c = {v_c:.3f}c")

print("\n[DONE] Run 'python scripts/plot_paper_figure.py' next")
