import numpy as np
import pytest

from qsot.core.compiler import (
    check_axiom1_linearity,
    check_axiom2_conditionability,
    run,
)
from qsot.physics.relativity import lorentz_factor
from qsot.utils.math_utils import validate_density_matrix


def test_linearity_axiom(damping_channel):
    res = check_axiom1_linearity([damping_channel], trials=5)
    assert res["pass"] is True
    assert res["max_deviation"] < 1e-8


def test_conditionability_axiom(sample_rho0, damping_channel):
    # Evolve once
    rho1 = damping_channel.apply(sample_rho0)
    res = check_axiom2_conditionability([sample_rho0, rho1], [damping_channel])
    assert res["pass"] is True
    assert res["max_trace_deviation"] < 1e-8


def test_full_run(tmp_path, sample_rho0, damping_channel):
    outdir = tmp_path / "artifacts"
    run(
        rho0=sample_rho0,
        channels=[damping_channel],
        outdir=str(outdir),
        observer_velocity=0.0,
    )

    assert (outdir / "qsot_state.npz").exists()
    assert (outdir / "gate_report.json").exists()
    assert (outdir / "memory_report.json").exists()
    assert (outdir / "trace.jsonl").exists()


def test_relativistic_run(tmp_path, sample_rho0, damping_channel):
    outdir = tmp_path / "artifacts_rel"
    run(
        rho0=sample_rho0,
        channels=[damping_channel],
        outdir=str(outdir),
        observer_velocity=0.5,
    )
    # Check if artifacts created
    assert (outdir / "gate_report.json").exists()

    # Trace logic check
    import json

    with open(outdir / "trace.jsonl") as f:
        lines = f.readlines()
        init_payload = json.loads(lines[0])["payload"]
        assert init_payload["velocity"] == 0.5


def test_density_matrix_validation(sample_rho0):
    """Test that generated states are valid density matrices."""
    is_valid, msg = validate_density_matrix(sample_rho0)
    assert is_valid, f"Invalid density matrix: {msg}"


@pytest.mark.parametrize("velocity", [0.0, 0.3, 0.7, 0.95, 0.99])
def test_parametrized_velocities(
    tmp_path,
    sample_rho0,
    damping_channel,
    velocity,
):
    """Test compilation with different observer velocities."""
    outdir = tmp_path / f"artifacts_v{velocity}"
    run(
        rho0=sample_rho0,
        channels=[damping_channel],
        outdir=str(outdir),
        observer_velocity=velocity,
    )

    assert (outdir / "gate_report.json").exists()

    # Verify trace consistency
    import json

    with open(outdir / "trace.jsonl") as f:
        first_line = json.loads(f.readline())
        assert first_line["payload"]["velocity"] == velocity

    if velocity > 0:
        gamma = lorentz_factor(velocity)
        assert gamma > 1.0
        assert np.isfinite(gamma)
