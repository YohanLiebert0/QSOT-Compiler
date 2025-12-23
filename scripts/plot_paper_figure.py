# plot_paper_figure.py - Simple matplotlib version
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

csv_file = Path("paper_data_final.csv")
if not csv_file.exists():
    print("ERROR: paper_data_final.csv not found")
    exit(1)

print("Loading data...")
df = pd.read_csv(csv_file)

# Academic style
plt.rcParams.update(
    {
        "font.size": 12,
        "axes.labelsize": 14,
        "legend.fontsize": 10,
    }
)

# Create figure
fig, ax1 = plt.subplots(figsize=(8, 5.5))

# Quantum Correlation (colorblind-friendly)
color1 = "#0072B2"
ax1.set_xlabel(
    "Observer Velocity (beta = v/c)",
    fontsize=14,
    fontweight="bold",
)
ax1.set_ylabel("Quantum Correlation", color=color1, fontsize=13)
ax1.plot(
    df["velocity"],
    df["quantum_correlation"],
    "o-",
    color=color1,
    linewidth=2.5,
    markersize=7,
    label="Quantum Coherence",
    markerfacecolor="white",
    markeredgewidth=1.5,
)
ax1.tick_params(axis="y", labelcolor=color1)
ax1.set_ylim(0, 1.1)
ax1.grid(True, alpha=0.3)

# Memory Backflow (colorblind-friendly)
ax2 = ax1.twinx()
color2 = "#D55E00"
ax2.set_ylabel("Non-Markovianity", color=color2, fontsize=13)
ax2.plot(
    df["velocity"],
    df["memory_backflow"],
    "x--",
    color=color2,
    linewidth=2,
    markersize=8,
    label="Memory Backflow",
    markeredgewidth=2,
)
ax2.tick_params(axis="y", labelcolor=color2)
ax2.set_ylim(0, df["memory_backflow"].max() * 1.3)

# Title
plt.title(
    "Relativistic Degradation of Quantum Resources\n(QSOT Compiler v1.2.3)",
    fontsize=14,
    fontweight="bold",
    pad=15,
)

# Critical zone
critical = df[df["quantum_correlation"] < 0.1]
if not critical.empty:
    v_c = critical.iloc[0]["velocity"]
    ax1.axvspan(v_c - 0.05, 1.0, color="gray", alpha=0.15)
    ax1.text(
        v_c + 0.08,
        0.9,
        "Causal\nHorizon",
        fontsize=10,
        color="dimgray",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
    )
    print(f"Critical velocity: v_c = {v_c:.3f}c")

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="upper right",
    framealpha=0.95,
)

# Save
fig.tight_layout()
output = Path("Fig_Relativistic_Decay_FINAL.png")
plt.savefig(output, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Figure saved: {output}")
q_min = df["quantum_correlation"].min()
q_max = df["quantum_correlation"].max()
print(f"Q range: [{q_min:.4f}, {q_max:.4f}]")
print("DONE - Ready for Paper B")
