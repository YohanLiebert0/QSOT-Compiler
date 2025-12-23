#!/usr/bin/env python3
# loader.py — Load external rho0 (NPZ/JSON) + Kraus channels (JSON)
# v1.2.0 Verified: Corrects fixture logic for Depolarizing channels

import json
import numpy as np
from pathlib import Path
from typing import List, Any, Tuple

# Robust Import
try:
    from qsot.core.compiler import KrausChannel
except ImportError:
    try:
        from ..core.compiler import KrausChannel
    except ImportError:
        # Fallback definition if run standalone without package structure
        from dataclasses import dataclass
        @dataclass(frozen=True)
        class KrausChannel:
            name: str
            kraus: List[np.ndarray]

def load_rho0(path: str) -> np.ndarray:
    """Load initial density matrix from NPZ or JSON.
    NPZ format: {"rho": array([[...]])}  # complex128
    JSON format: {"re": [[...]], "im": [[...]]}  # real/imag parts
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Initial state file not found: {path}")

    if p.suffix == ".npz":
        return np.load(p)["rho"].astype(np.complex128)
    elif p.suffix == ".json":
        obj = json.loads(p.read_text(encoding="utf-8"))
        return np.array(obj["re"]) + 1j * np.array(obj["im"])
    else:
        raise ValueError(f"Unknown format: {p.suffix}")

def load_channels(path: str) -> List[KrausChannel]:
    """Load Kraus channels from JSON
    Format: [{"name": "...", "kraus": [{"re": ..., "im": ...}, ...]}, ...]
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Channel file not found: {path}")

    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("channels.json must be a list of channel objects")
    
    channels = []
    for ch in data:
        kraus_ops = [np.array(k["re"]) + 1j * np.array(k["im"]) for k in ch["kraus"]]
        channels.append(KrausChannel(ch["name"], kraus_ops))
    return channels

def generate_chaos_channels(length=5, seed=42):
    """Generate a sequence of Random Unitary Channels (Haar Random)."""
    np.random.seed(seed)
    channels = []
    
    for i in range(length):
        # Generate random complex matrix -> QR decomposition -> Unitary
        Z = np.random.randn(2, 2) + 1j * np.random.randn(2, 2)
        Q, R = np.linalg.qr(Z)
        
        # Make diagonal of R real (standard convention)
        d = np.diagonal(R)
        ph = d / np.abs(d)
        U = Q @ np.diag(ph)
        
        # Create Kraus Operator (Noisy Unitary)
        # Mixes unitary evolution (90%) with white noise (10%) to test memory
        k0 = U * np.sqrt(0.9)
        k1 = np.eye(2, dtype=np.complex128) * np.sqrt(0.1) # Noise floor
        
        # Format for JSON export
        k0_dict = {"re": k0.real.tolist(), "im": k0.imag.tolist()}
        k1_dict = {"re": k1.real.tolist(), "im": k1.imag.tolist()}
        
        channels.append({"name": f"Chaos_Step_{i}", "kraus": [k0_dict, k1_dict]})
        
    return channels

def generate_fixture_data(name: str) -> Tuple[np.ndarray, List[dict]]:
    """Generate toy data for testing."""
    
    if name == "quantum_chaos":
        # Chaos Mode: Mixed state + Random Unitaries
        # [FIX] Use Superposition |+> to see dynamics (Maximally mixed state 0.5*I is invariant)
        rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128) 
        channels = generate_chaos_channels(length=10)
        return rho0, channels

    elif name == "correlated_noise_with_ancilla_memory":
        # Non-Markovian Model: Parameter oscillation
        rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128) # |+><+|
        
        channels = []
        # Probability oscillation simulating information backflow
        probs = [0.1, 0.3, 0.5, 0.3, 0.1] 
        
        for i, p in enumerate(probs):
            k0 = np.array([[1, 0], [0, np.sqrt(1-p)]], dtype=np.complex128)
            k1 = np.array([[0, 0], [0, np.sqrt(p)]], dtype=np.complex128)
            
            k0_d = {"re": k0.real.tolist(), "im": k0.imag.tolist()}
            k1_d = {"re": k1.real.tolist(), "im": k1.imag.tolist()}
            
            channels.append({
                "name": f"OscillatingDamping_t{i}", 
                "kraus": [k0_d, k1_d]
            })
            
        return rho0, channels

    elif name == "depolarizing_then_phase_damping":
        # 1. rho0 = |+><+|
        rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)
        
        # 2. Channels
        # [FIX] Channel 1: Depolarizing (p=0.1) instead of Identity
        p_dep = 0.1
        # Kraus operators for single qubit depolarizing
        # K0 = sqrt(1-3p/4) * I
        # K1, K2, K3 = sqrt(p/4) * X, Y, Z
        f0 = np.sqrt(1 - 0.75 * p_dep)
        f1 = np.sqrt(p_dep / 4.0)
        
        k_dep0 = f0 * np.eye(2, dtype=np.complex128)
        k_dep1 = f1 * np.array([[0, 1], [1, 0]], dtype=np.complex128) # X
        k_dep2 = f1 * np.array([[0, -1j], [1j, 0]], dtype=np.complex128) # Y
        k_dep3 = f1 * np.array([[1, 0], [0, -1]], dtype=np.complex128) # Z
        
        k_dep_json = [{"re": k.real.tolist(), "im": k.imag.tolist()} for k in [k_dep0, k_dep1, k_dep2, k_dep3]]

        # Channel 2: Phase Damping (p=0.3)
        p_pd = 0.3
        k_pd0 = np.array([[1, 0], [0, np.sqrt(1-p_pd)]], dtype=np.complex128)
        k_pd1 = np.array([[0, 0], [0, np.sqrt(p_pd)]], dtype=np.complex128)
        
        k_pd_json = [{"re": k.real.tolist(), "im": k.imag.tolist()} for k in [k_pd0, k_pd1]]
        
        channels = [
            {"name": "Depolarizing(p=0.1)", "kraus": k_dep_json},
            {"name": "PhaseDamping(p=0.3)", "kraus": k_pd_json}
        ]
        
        return rho0, channels
    else:
        raise ValueError(f"Unknown fixture: {name}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="QSOT Data Loader & Generator")
    parser.add_argument("--export-rho0", help="Path to save rho0.json")
    parser.add_argument("--export-channels", help="Path to save channels.json")
    parser.add_argument("--fixture", help="Name of the fixture to generate (quantum_chaos | depolarizing_then_phase_damping)")
    args = parser.parse_args()
    
    if args.fixture:
        try:
            print(f"Generating fixture: {args.fixture}")
            rho0, chans = generate_fixture_data(args.fixture)
            
            if args.export_rho0:
                with open(args.export_rho0, "w") as f:
                    json.dump({"re": rho0.real.tolist(), "im": rho0.imag.tolist()}, f)
                print(f"  ✓ Saved rho0 to {args.export_rho0}")
                
            if args.export_channels:
                with open(args.export_channels, "w") as f:
                    json.dump(chans, f, indent=2)
                print(f"  ✓ Saved {len(chans)} channels to {args.export_channels}")
                
        except Exception as e:
            print(f"❌ Error generating fixture: {e}")
            exit(1)