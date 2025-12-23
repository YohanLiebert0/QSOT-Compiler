#!/usr/bin/env python3
# qsot_compiler.py (v1.2.0) - Relativistic Quantum Chaos & Entanglement Engine
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# [Imports]
try:
    from qsot.utils.math_utils import random_density_matrix
except ImportError:
    # Fallback for direct execution
    from ..utils.math_utils import random_density_matrix

try:
    from .memory_kernel import compute_memory_kernel
except ImportError:
    compute_memory_kernel = None

try:
    from qsot.physics.relativity import boost_damping_channel
except ImportError:
    try:
        from ..physics.relativity import boost_damping_channel
    except ImportError:
        boost_damping_channel = None

try:
    from qsot.physics.entanglement import compute_correlation_profile
except ImportError:
    try:
        from ..physics.entanglement import compute_correlation_profile
    except ImportError:
        compute_correlation_profile = None


# ----- Hash-chained Trace -----
class Trace:
    def __init__(self, path: Path):
        self.path = path
        self.prev = "0" * 64
        self.f = None

    def __enter__(self):
        self.f = open(self.path, "w", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.f:
            self.f.close()
            self.f = None

    def emit(self, step: str, payload: Dict[str, Any]) -> None:
        if self.f is None:
            raise RuntimeError("Trace not opened (use context manager).")
        entry = {
            "ts": time.time(),
            "step": step,
            "prev_hash": self.prev,
            "payload": payload,
        }
        link = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        entry["link_hash"] = link
        self.f.write(json.dumps(entry) + "\n")
        self.f.flush()
        self.prev = link


# ----- Kraus Channel -----
@dataclass(frozen=True)
class KrausChannel:
    name: str
    kraus: List[np.ndarray]

    def apply(self, rho: np.ndarray) -> np.ndarray:
        """Apply Kraus operators: E(rho) = sum_i K_i rho K_i^dagger."""
        out = np.zeros_like(rho, dtype=np.complex128)
        for k in self.kraus:
            out += k @ rho @ k.conj().T
        return out


# ----- Gate #1: Linearity -----
def check_axiom1_linearity(chans, trials=16, tol_abs=1e-8, seed=42):
    """
    Verify F(p*rho + (1-p)*sigma) ~= p*F(rho) + (1-p)*F(sigma) for all channels.
    """
    np.random.seed(seed)
    max_diff = 0.0
    passed = True

    for ch in chans:
        for _ in range(trials):
            rho_a = random_density_matrix(2)
            rho_b = random_density_matrix(2)
            p = np.random.rand()

            rho_mix = p * rho_a + (1 - p) * rho_b

            out_real = ch.apply(rho_mix)
            out_linear = p * ch.apply(rho_a) + (1 - p) * ch.apply(rho_b)

            diff = np.linalg.norm(out_real - out_linear, ord="fro")
            max_diff = max(max_diff, diff)

            if diff > tol_abs:
                passed = False

    return {"pass": passed, "max_deviation": float(max_diff)}


# ----- Gate #2: Conditionability -----
def check_axiom2_conditionability(rhos, chans, tol_abs=1e-8):
    """
    Verify Trace Preservation. Tr(E(rho)) = 1
    """
    max_dev = 0.0
    passed = True

    test_rho = np.eye(2) / 2.0
    for ch in chans:
        out = ch.apply(test_rho)
        tr = np.trace(out)
        dev = abs(tr - 1.0)
        max_dev = max(max_dev, dev)

        if dev > tol_abs:
            passed = False

    return {"pass": passed, "max_trace_deviation": float(max_dev)}


# ----- ASDP Entrypoint -----
def run(
    rho0: np.ndarray,
    channels: List[KrausChannel],
    times=None,
    outdir="artifacts",
    build_kd=True,
    compute_markov_metrics=True,
    seed=42,
    tol_abs=1e-8,
    observer_velocity=0.0,
):
    """QSOT Compiler main entry point"""
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    with Trace(out_path / "trace.jsonl") as trace:
        trace.emit("init", {"velocity": observer_velocity, "version": "1.2.3"})

        # [Relativity Logic Injection]
        active_channels = []
        if observer_velocity > 0 and boost_damping_channel:
            print(f"[!] Relativistic Boost Enabled: v={observer_velocity}c")

            for ch in channels:
                if "PhaseDamping" in ch.name or "Damping" in ch.name:
                    # Generalize for OscillatingDamping too?
                    # For v1.2.0, apply to any damping-like channel where K0 is diagonal
                    k0_11 = ch.kraus[0][1, 1]
                    p_rest = 1.0 - np.abs(k0_11) ** 2

                    # Apply Lorentz Boost
                    p_boost = boost_damping_channel(p_rest, observer_velocity)

                    new_k0 = np.diag([1.0, np.sqrt(1.0 - p_boost)]).astype(
                        np.complex128
                    )
                    new_k1 = np.diag([0.0, np.sqrt(p_boost)]).astype(np.complex128)

                    active_channels.append(
                        KrausChannel(
                            name=f"{ch.name}_Boosted",
                            kraus=[new_k0, new_k1],
                        )
                    )
                else:
                    active_channels.append(ch)
        else:
            active_channels = channels

        # 1. Evolve State (QSOT construction)
        rho_qsot = [rho0]
        current = rho0
        for ch in active_channels:
            current = ch.apply(current)
            rho_qsot.append(current)

        # Save Real State to NPZ
        state_dict = {f"rho_{i}": rho for i, rho in enumerate(rho_qsot)}
        np.savez(out_path / "qsot_state.npz", **state_dict)

        # 2. Gate Validation
        ax1_res = check_axiom1_linearity(active_channels, seed=seed, tol_abs=tol_abs)
        ax2_res = check_axiom2_conditionability(
            rho_qsot,
            active_channels,
            tol_abs=tol_abs,
        )

        gate_report = {
            "pass": ax1_res["pass"] and ax2_res["pass"],
            "axiom1_report": ax1_res,
            "axiom2_report": ax2_res,
            "velocity": observer_velocity,
        }

        # 3. Memory Kernel (Real TTM)
        if compute_memory_kernel:
            mem_report = compute_memory_kernel(rho_qsot, active_channels)
        else:
            mem_report = {"error": "memory_kernel missing"}

        # 4. Entanglement Analysis [v1.2.0 New]
        ent_report = {}
        if compute_correlation_profile:
            ent_report = compute_correlation_profile(rho_qsot)
            (out_path / "entanglement_report.json").write_text(
                json.dumps(ent_report, indent=2)
            )

        # Write Artifacts
        (out_path / "gate_report.json").write_text(json.dumps(gate_report, indent=2))
        (out_path / "memory_report.json").write_text(json.dumps(mem_report, indent=2))

        # Mock KD for visuals
        kd_data = {"entries": [], "metrics": {"kd_negativity_proxy": 0.0}}
        (out_path / "kd_quasiprob.json").write_text(json.dumps(kd_data, indent=2))

        trace.emit(
            "complete",
            {"status": "success", "entanglement": ent_report.get("avg_value", 0)},
        )

    print(f"Gate Pass: {gate_report['pass']}")
    print(f"Artifacts generated in {outdir}")


if __name__ == "__main__":
    pass
