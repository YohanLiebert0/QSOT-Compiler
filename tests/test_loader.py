import json
import numpy as np
import pytest
from qsot.utils.loader import load_rho0, load_channels, generate_fixture_data

def test_load_rho0_json(tmp_path):
    rho = np.eye(2, dtype=np.complex128)
    data = {"re": rho.real.tolist(), "im": rho.imag.tolist()}
    
    p = tmp_path / "rho0.json"
    p.write_text(json.dumps(data))
    
    loaded = load_rho0(str(p))
    assert np.allclose(loaded, rho)

def test_generate_fixture():
    rho, chans = generate_fixture_data("depolarizing_then_phase_damping")
    assert rho.shape == (2, 2)
    assert len(chans) == 2
    assert chans[0]["name"] == "Depolarizing(p=0.1)"
