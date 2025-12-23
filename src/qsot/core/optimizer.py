#!/usr/bin/env python3
# optimizer.py - FPE (PyTorch) based Quantum Observable Optimization
# Finds optimal measurement basis angles to maximize KD Negativity.

import argparse
import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_OPTIMIZER_PATIENCE = 20

# Optional Torch Import
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:

    class QuantumOptimizer(torch.nn.Module):
        def __init__(self, rho_np):
            super().__init__()
            self.rho = torch.tensor(rho_np, dtype=torch.complex128)
            self.theta_a = torch.nn.Parameter(
                (torch.rand(1) * np.pi).to(dtype=torch.float64)
            )
            self.phi_a = torch.nn.Parameter(
                (torch.rand(1) * 2 * np.pi).to(dtype=torch.float64)
            )
            self.theta_b = torch.nn.Parameter(
                (torch.rand(1) * np.pi).to(dtype=torch.float64)
            )
            self.phi_b = torch.nn.Parameter(
                (torch.rand(1) * 2 * np.pi).to(dtype=torch.float64)
            )

        def get_projector(self, theta, phi):
            c = torch.cos(theta / 2)
            s = torch.sin(theta / 2)
            phase = torch.exp(1j * phi)
            psi = torch.stack([c, phase * s]).squeeze()
            if psi.dim() == 0:
                psi = psi.unsqueeze(0)
            P = torch.outer(psi, psi.conj())
            return P

        def forward(self):
            Pa = self.get_projector(self.theta_a, self.phi_a)
            Pb = self.get_projector(self.theta_b, self.phi_b)
            term = torch.trace(Pb @ Pa @ self.rho)
            return term.real


def run_kd_optimization(
    state_path: str,
    out_path: str,
    steps=200,
    lr=0.1,
    patience=DEFAULT_OPTIMIZER_PATIENCE,
    min_delta=1e-6,
):
    """
    Core logic for AI-driven Kirkwood-Dirac optimization with early stopping.

    Args:
        state_path: Path to NPZ file containing quantum states
        out_path: Output JSON path
        steps: Maximum optimization steps
        lr: Learning rate
        patience: Early stopping patience (steps without improvement)
        min_delta: Minimum change to be considered improvement
    """
    print(f"[>] Starting AI Optimization for: {state_path}")

    if not TORCH_AVAILABLE:
        print("[!] PyTorch not found. Optimization skipped.")
        Path(out_path).write_text(
            json.dumps({"optimized_value": 0.0, "error": "torch_missing"}, indent=2)
        )
        return

    # Load State
    try:
        data = np.load(state_path)
        keys = [k for k in data.keys() if k.startswith("rho_")]
        if not keys:
            raise ValueError(f"No rho states found in {state_path}")
        last_key = sorted(keys)[-1]
        rho = data[last_key]
    except (FileNotFoundError, KeyError, OSError, ValueError) as e:
        logger.error("Failed to load state: %s", e)
        Path(out_path).write_text(
            json.dumps({"optimized_value": 0.0, "error": str(e)}, indent=2)
        )
        return

    model = QuantumOptimizer(rho)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    # Early stopping variables
    best_loss = float("inf")
    no_improve_count = 0
    best_state = None

    for i in range(steps):
        opt.zero_grad()
        val = model()
        # Loss: minimize Re(Tr(Pb Pa rho)) to find negative values
        loss = val
        loss.backward()

        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        opt.step()

        current_loss = loss.item()

        # Early stopping check
        if current_loss < best_loss - min_delta:
            best_loss = current_loss
            no_improve_count = 0
            # Save best state
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve_count += 1

        if i % 50 == 0:
            print(
                f"  Step {i:03d}: KD Value = {val.item():.6f} | Best = {best_loss:.6f}"
            )

        # Early stopping
        if no_improve_count >= patience:
            print(
                f"[+] Early stopping at step {i} (no improvement for {patience} steps)"
            )
            # Restore best model
            if best_state is not None:
                model.load_state_dict(best_state)
            break

    final_val = model().item()
    res = {
        "optimized_value": final_val,
        "is_negative": final_val < 0,
        "is_contextual": final_val < -1e-6,  # Significant negativity
        "convergence": {
            "converged": no_improve_count >= patience,
            "final_step": i + 1,
            "total_steps": steps,
        },
        "angles": {
            "basis_a": {
                "theta": float(model.theta_a.item()),
                "phi": float(model.phi_a.item()),
            },
            "basis_b": {
                "theta": float(model.theta_b.item()),
                "phi": float(model.phi_b.item()),
            },
        },
        "target_state_index": last_key,
    }

    Path(out_path).write_text(json.dumps(res, indent=2))
    print(f"[+] Optimization Complete. Best Value: {final_val:.6f}")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--state",
        required=True,
        help="Path to qsot_state.npz",
    )
    ap.add_argument("--out", default="optimization_result.json")
    args = ap.parse_args()

    run_kd_optimization(args.state, args.out)
