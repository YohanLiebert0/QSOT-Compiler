#!/usr/bin/env python3
"""
generate_paper_data.py — Grand Sweep for Academic Paper Generation

This script performs a systematic velocity sweep (0.0 - 0.99c) to generate
data for the Physics Paper (Paper B: Causal Horizon).

Output:
    - paper_data/v_*/entanglement_report.json
    - paper_data/v_*/memory_report.json
    - Fig_Relativistic_Decay.png (Publication-ready figure)
"""

import subprocess
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Add src to path for imports
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

def main():
    print("=" * 60)
    print("🧪 QSOT Paper Data Generation: Velocity Sweep")
    print("=" * 60)
    
    # Configuration
    velocities = np.linspace(0.0, 0.99, 20)  # 20 velocity points
    fixture = "quantum_chaos"  # Use chaos mode for memory backflow
    output_base = root_dir / "paper_data"
    output_base.mkdir(exist_ok=True)
    
    # Data storage
    entanglements = []
    memory_measures = []
    
    # Sweep
    for i, v in enumerate(velocities):
        print(f"\n[{i+1}/20] Running simulation at v={v:.3f}c...")
        
        # Create velocity-specific output directory
        outdir = output_base / f"v_{v:.3f}"
        outdir.mkdir(exist_ok=True)
        
        # Prepare temporary files
        rho0_file = outdir / "rho0_tmp.json"
        chans_file = outdir / "chans_tmp.json"
        
        try:
            # 1. Generate initial state and channels
            subprocess.run([
                sys.executable, 
                str(root_dir / "src/qsot/utils/loader.py"),
                "--export-rho0", str(rho0_file),
                "--export-channels", str(chans_file),
                "--fixture", fixture
            ], check=True, capture_output=True)
            
            # 2. Run compiler
            subprocess.run([
                sys.executable,
                str(root_dir / "scripts/asdp_run.py"),
                "--rho0", str(rho0_file),
                "--channels", str(chans_file),
                "--velocity", str(v),
                "--outdir", str(outdir)
            ], check=True, capture_output=True)
            
            # 3. Harvest data
            ent_file = outdir / "entanglement_report.json"
            mem_file = outdir / "memory_report.json"
            
            if ent_file.exists() and mem_file.exists():
                ent_data = json.loads(ent_file.read_text())
                mem_data = json.loads(mem_file.read_text())
                
                entanglements.append(ent_data.get("avg_value", 0.0))
                memory_measures.append(mem_data.get("nm_measure", 0.0))
                print(f"   ✓ Entanglement: {entanglements[-1]:.4f}")
                print(f"   ✓ Memory (NM): {memory_measures[-1]:.4f}")
            else:
                print(f"   ⚠ Missing output files, using 0.0")
                entanglements.append(0.0)
                memory_measures.append(0.0)
                
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Simulation failed: {e}")
            entanglements.append(0.0)
            memory_measures.append(0.0)
    
    # Generate publication figure
    print("\n" + "=" * 60)
    print("📊 Generating Publication Figure...")
    print("=" * 60)
    
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Entanglement axis
    color = 'tab:blue'
    ax1.set_xlabel('Observer Velocity (β = v/c)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Entanglement (Logarithmic Negativity)', color=color, fontsize=12)
    ax1.plot(velocities, entanglements, 'o-', color=color, linewidth=2, markersize=6, label='Entanglement')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    # Memory axis
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Non-Markovianity Measure', color=color, fontsize=12)
    ax2.plot(velocities, memory_measures, 's--', color=color, linewidth=2, markersize=6, label='Memory Backflow')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Title and legend
    plt.title('Relativistic Quantum Decay & Memory Dynamics\n(QSOT Compiler v1.2.3)', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    
    # Save figure
    fig_path = output_base / "Fig_Relativistic_Decay.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved: {fig_path}")
    
    # Save raw data as CSV
    csv_path = output_base / "raw_data.csv"
    with open(csv_path, 'w') as f:
        f.write("velocity,entanglement,non_markovianity\n")
        for v, e, m in zip(velocities, entanglements, memory_measures):
            f.write(f"{v:.4f},{e:.6f},{m:.6f}\n")
    print(f"✅ Raw data saved: {csv_path}")
    
    print("\n" + "=" * 60)
    print("🎉 Data Generation Complete!")
    print("=" * 60)
    print(f"\nNext Steps:")
    print(f"1. Review figure: {fig_path}")
    print(f"2. Analyze critical velocity (sudden death point)")
    print(f"3. Begin Paper B draft with this data")

if __name__ == "__main__":
    main()
