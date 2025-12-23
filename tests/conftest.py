import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to sys.path for tests
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
sys.path.insert(0, str(src_dir))

from qsot.core.compiler import KrausChannel

@pytest.fixture
def sample_rho0():
    # |+><+| state
    return np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)

@pytest.fixture
def identity_channel():
    k0 = np.eye(2, dtype=np.complex128)
    return KrausChannel(name="Identity", kraus=[k0])

@pytest.fixture
def damping_channel():
    # Phase Damping p=0.3
    p = 0.3
    k0 = np.array([[1, 0], [0, np.sqrt(1-p)]], dtype=np.complex128)
    k1 = np.array([[0, 0], [0, np.sqrt(p)]], dtype=np.complex128)
    return KrausChannel(name="PhaseDamping(0.3)", kraus=[k0, k1])
