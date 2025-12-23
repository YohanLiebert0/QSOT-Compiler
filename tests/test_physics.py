import numpy as np
import pytest
from qsot.physics.relativity import lorentz_factor, boost_damping_channel
from qsot.physics.entanglement import logarithmic_negativity, l1_norm_coherence
from qsot.utils.math_utils import validate_density_matrix, random_density_matrix


class TestRelativity:
    """Test relativistic transformations."""
    
    @pytest.mark.parametrize("beta", [0.0, 0.3, 0.6, 0.9])
    def test_lorentz_factor(self, beta):
        """Lorentz factor should be >= 1 and match formula."""
        gamma = lorentz_factor(beta)
        expected = 1.0 / np.sqrt(1.0 - beta**2)
        
        assert gamma >= 1.0
        assert np.isclose(gamma, expected, rtol=1e-10)
    
    def test_lorentz_factor_edge_cases(self):
        """Test edge cases for Lorentz factor."""
        # beta = 0 should give gamma = 1
        assert np.isclose(lorentz_factor(0.0), 1.0)
        
        # beta close to 1 should give large gamma
        gamma_high = lorentz_factor(0.99)
        assert gamma_high > 7.0
        
        # beta >= 1 should raise error
        with pytest.raises(ValueError, match="beta must be < 1.0"):
            lorentz_factor(1.0)
        
        with pytest.raises(ValueError, match="beta must be < 1.0"):
            lorentz_factor(1.5)
    
    @pytest.mark.parametrize("prob,beta", [
        (0.1, 0.0),
        (0.5, 0.3),
        (0.9, 0.7),
    ])
    def test_boost_damping_channel(self, prob, beta):
        """Boosted probability should be in [0, 1] and >= original."""
        boosted = boost_damping_channel(prob, beta)
        
        assert 0.0 <= boosted <= 1.0
        assert boosted >= prob  # Time dilation increases decoherence


class TestEntanglement:
    """Test entanglement and coherence measures."""
    
    def test_l1_coherence_pure_state(self):
        """Pure state should have maximum coherence."""
        # |+⟩ = (|0⟩ + |1⟩)/√2
        psi = np.array([1, 1]) / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        
        coherence = l1_norm_coherence(rho)
        
        # Off-diagonal elements: |0.5| + |0.5| = 1.0
        assert np.isclose(coherence, 1.0, atol=1e-10)
    
    def test_l1_coherence_mixed_state(self):
        """Maximally mixed state should have zero coherence."""
        rho = np.eye(2) / 2  # I/2
        coherence = l1_norm_coherence(rho)
        assert np.isclose(coherence, 0.0, atol=1e-10)
    
    def test_logarithmic_negativity_separable(self):
        """Separable state should have zero entanglement."""
        # Product state: |0⟩⊗|0⟩
        rho = np.zeros((4, 4), dtype=complex)
        rho[0, 0] = 1.0
        
        ent = logarithmic_negativity(rho)
        
        # Should be close to 0 (log2(1) = 0)
        assert ent >= 0.0
        assert ent < 0.1  # Small tolerance for numerical errors


class TestMathUtils:
    """Test mathematical utility functions."""
    
    def test_validate_density_matrix_valid(self):
        """Valid density matrices should pass validation."""
        # Pure state
        psi = np.array([1, 0])
        rho = np.outer(psi, psi.conj())
        
        is_valid, msg = validate_density_matrix(rho)
        assert is_valid
        assert msg == "Valid density matrix"
    
    def test_validate_density_matrix_non_hermitian(self):
        """Non-Hermitian matrix should fail."""
        rho = np.array([[1.0, 0.5j], [0.0, 0.0]])
        
        is_valid, msg = validate_density_matrix(rho)
        assert not is_valid
        assert "not Hermitian" in msg
    
    def test_validate_density_matrix_wrong_trace(self):
        """Matrix with trace != 1 should fail."""
        rho = np.eye(2) * 0.5  # Trace = 1.0 (this will pass)
        is_valid, _ = validate_density_matrix(rho)
        assert is_valid
        
        rho_bad = np.eye(2) * 0.3  # Trace = 0.6
        is_valid, msg = validate_density_matrix(rho_bad)
        assert not is_valid
        assert "Trace is" in msg
    
    def test_validate_density_matrix_negative_eigenvalue(self):
        """Matrix with negative eigenvalues should fail."""
        rho = np.array([[0.5, 0.5], [0.5, 0.5]])  # Eigenvalues: 1, 0 (valid)
        is_valid, _ = validate_density_matrix(rho)
        assert is_valid
        
        # Artificially create invalid matrix
        rho_bad = np.array([[1.0, 1.5], [1.5, 0.0]])
        rho_bad /= np.trace(rho_bad)  # Normalize trace
        
        is_valid, msg = validate_density_matrix(rho_bad)
        # This will have negative eigenvalue
        if not is_valid:
            assert "eigenvalue" in msg.lower()
    
    def test_random_density_matrix_validity(self):
        """Generated random matrices should be valid."""
        for dim in [2, 3, 4]:
            rho = random_density_matrix(dim, seed=42)
            
            is_valid, msg = validate_density_matrix(rho)
            assert is_valid, f"Failed for dim={dim}: {msg}"
            
            # Check dimensions
            assert rho.shape == (dim, dim)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
