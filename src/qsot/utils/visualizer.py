#!/usr/bin/env python3
# visualizer.py - Visualize QSOT Artifacts
import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_kd_heatmap(kd_json_path: Path, out_path: Path):
    """Plot Kirkwood-Dirac Quasiprobability Heatmap"""
    data = json.loads(kd_json_path.read_text(encoding="utf-8"))
    entries = data["entries"]
    max_a = max(e["a"] for e in entries) + 1
    max_b = max(e["b"] for e in entries) + 1
    grid = np.zeros((max_a, max_b))
    for e in entries:
        grid[e["a"], e["b"]] = e["value"]["re"]

    plt.figure(figsize=(6, 5))
    plt.imshow(grid, cmap="RdBu_r", interpolation="nearest")
    plt.colorbar(label="Real(KD Distribution)")
    plt.title("Kirkwood-Dirac Quasi-probability")
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_gate_metrics(report_path: Path, out_path: Path):
    """Plot Gate Axiom Deviations (Log Scale)"""
    rep = json.loads(report_path.read_text(encoding="utf-8"))

    # Extract metrics robustly (handling both old mock and new real formats)
    ax1_val = rep.get("axiom1_report", {}).get(
        "max_deviation",
        rep.get("axiom1_diff", 1e-9),
    )
    ax2_val = rep.get("axiom2_report", {}).get(
        "max_trace_deviation",
        rep.get("axiom2_diff", 1e-12),
    )

    # Avoid log(0)
    ax1_val = max(ax1_val, 1e-16)
    ax2_val = max(ax2_val, 1e-16)

    values = [ax1_val, ax2_val]
    names = ["Linearity", "Trace Pres."]

    plt.figure(figsize=(5, 4))
    plt.bar(names, values, color=["#3498db", "#e74c3c"])

    plt.yscale("log")
    plt.axhline(
        y=1e-8,
        color="k",
        linestyle="--",
        label="Tolerance (1e-8)",
    )
    plt.ylabel("Max Deviation")
    plt.title("Axiom Integrity Check")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_memory_kernel(report_path: Path, out_path: Path):
    """Plot Memory Kernel (Markov vs Non-Markovian Depth)"""
    data = json.loads(report_path.read_text(encoding="utf-8"))
    profile = data.get("profile", [])
    depth = data.get("depth", 0)

    if not profile:
        return

    x = np.arange(len(profile))
    plt.figure(figsize=(6, 4))

    # Bar chart for deviations
    bars = plt.bar(x, profile, color="#444444", label="Markov Deviation")

    # Highlight memory region (Yellow)
    # Assuming depth means the first 'depth' steps are the relevant history
    for i in range(min(len(bars), depth + 1)):
        bars[i].set_color("#F1C40F")  # Yellow

    plt.axvline(
        x=depth + 0.5,
        color="red",
        linestyle="--",
        label=f"Depth {depth}",
    )

    plt.xlabel("Time Lag (tau)")
    plt.ylabel("Norm(K_tau)")
    plt.title("Memory Kernel Profile")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# [v1.2.0 New]
def plot_entanglement_evolution(report_path: Path, out_path: Path):
    """Plot Quantum Correlation (Entanglement/Coherence) Decay"""
    data = json.loads(report_path.read_text(encoding="utf-8"))
    profile = data.get("profile", [])
    metric = data.get("metric", "Quantum Correlation")

    if not profile:
        return

    t = np.arange(len(profile))

    plt.figure(figsize=(6, 4))
    # Plot line
    plt.plot(
        t,
        profile,
        marker="o",
        linestyle="-",
        color="#8e44ad",
        linewidth=2,
        label=metric,
    )
    # Fill area
    plt.fill_between(t, profile, color="#8e44ad", alpha=0.1)

    plt.xlabel("Time Step (t)")
    plt.ylabel("Magnitude")
    plt.title(f"Relativistic Decay: {metric}")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    logger = logging.getLogger(__name__)

    # Use non-interactive backend
    plt.switch_backend("Agg")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        type=Path,
        required=True,
        help="Artifacts directory",
    )
    args = parser.parse_args()

    if not args.dir.exists():
        logger.error("Artifacts directory does not exist: %s", args.dir)
        sys.exit(1)

    logger.info("Visualizing artifacts in %s", args.dir)
    logger.debug("CWD=%s, Target=%s", Path.cwd(), args.dir.resolve())
    if args.dir.exists():
        logger.debug(
            "Contents: %s",
            [p.name for p in args.dir.glob("*")],
        )

    # Plot KD Heatmap
    kd_path = args.dir / "kd_quasiprob.json"
    if kd_path.exists():
        try:
            plot_kd_heatmap(kd_path, args.dir / "viz_kd_heatmap.png")
            logger.info("Generated viz_kd_heatmap.png")
        except Exception as e:
            logger.exception("Failed to plot KD Heatmap: %s", e)

    # Plot Gate Metrics
    gate_path = args.dir / "gate_report.json"
    if gate_path.exists():
        try:
            plot_gate_metrics(gate_path, args.dir / "viz_gate_metrics.png")
            logger.info("Generated viz_gate_metrics.png")
        except Exception as e:
            logger.exception("Failed to plot Gate Metrics: %s", e)

    # Plot Memory Kernel
    mem_path = args.dir / "memory_report.json"
    if mem_path.exists():
        try:
            plot_memory_kernel(
                mem_path,
                args.dir / "viz_memory_kernel.png",
            )
            logger.info("Generated viz_memory_kernel.png (Updated Chart)")
        except Exception as e:
            logger.exception("Failed to plot memory kernel: %s", e)

    # Plot Entanglement Evolution [v1.2.0]
    ent_path = args.dir / "entanglement_report.json"
    if ent_path.exists():
        try:
            plot_entanglement_evolution(
                ent_path,
                args.dir / "viz_entanglement.png",
            )
            logger.info("Generated viz_entanglement.png")
        except Exception as e:
            logger.exception("Failed to plot entanglement: %s", e)
