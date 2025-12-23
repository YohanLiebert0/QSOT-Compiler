#!/usr/bin/env python3
# asdp_run.py — ASDP runtime wrapper
import sys
from pathlib import Path

# Ensure 'src' is in python path
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import argparse
from typing import Dict, Any, List

# Imports after path fix
try:
    from qsot.core.compiler import run
    from qsot.utils.loader import load_rho0, load_channels
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

def run_asdp(rho0_path: str, channels_path: str, velocity: float, outdir: str = "artifacts"):
    rho0 = load_rho0(rho0_path)
    channels = load_channels(channels_path)
    
    print(f"✓ Loaded rho0: shape={rho0.shape}")
    print(f"✓ Loaded {len(channels)} channels")
    
    return run(rho0=rho0, channels=channels, outdir=outdir, observer_velocity=velocity)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASDP Runner for QSOT Compiler")
    parser.add_argument("--rho0", required=True, help="Path to initial state JSON/NPZ")
    parser.add_argument("--channels", required=True, help="Path to channels JSON")
    parser.add_argument("--velocity", type=float, default=0.0, help="Observer velocity (c)")
    parser.add_argument("--outdir", default="artifacts", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        run_asdp(args.rho0, args.channels, args.velocity, args.outdir)
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)