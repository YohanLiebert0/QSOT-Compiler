
import numpy as np
from scipy import linalg

def validate_density_matrix(rho: np.ndarray, tol: float = 1e-8) -> tuple[bool, str]:
    """
    Validate if rho is a proper density matrix.
    
    Requirements:
    1. Hermitian: rho = rho†
    2. Trace = 1
    3. Positive semi-definite: eigenvalues >= 0
    
    Returns:
        (is_valid, error_message)
    """
    # Check Hermitian
    if not np.allclose(rho, rho.conj().T, atol=tol):
        return False, "Matrix is not Hermitian"
    
    # Check trace
    trace = np.trace(rho)
    if not np.isclose(trace, 1.0, atol=tol):
        return False, f"Trace is {trace:.6e}, expected 1.0"
    
    # Check positive semi-definite
    eigenvalues = np.linalg.eigvalsh(rho)
    min_eigenval = np.min(eigenvalues)
    if min_eigenval < -tol:
        return False, f"Negative eigenvalue detected: {min_eigenval:.6e}"
    
    return True, "Valid density matrix"

def random_density_matrix(dim: int, seed: int = None) -> np.ndarray:
    """
    Generate a valid random density matrix of dimension `dim`.
    Uses the Ginibre ensemble method: rho = G @ G.H / Tr(G @ G.H)
    """
    if seed is not None:
        np.random.seed(seed)
        
    # Generate random complex matrix (Ginibre ensemble)
    G = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
    
    # Make it positive semidefinite
    rho = G @ G.conj().T
    
    # Normalize trace to 1
    rho /= np.trace(rho)
    
    # Validate (sanity check)
    is_valid, msg = validate_density_matrix(rho)
    if not is_valid:
        raise ValueError(f"Generated invalid density matrix: {msg}")
    
    return rho

def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    """
    Compute trace distance: D(rho, sigma) = 0.5 * Tr|rho - sigma|
    where |A| = sqrt(A†A)
    """
    diff = rho - sigma
    # Compute eigenvalues of sqrt(diff† @ diff) which corresponds to singular values of diff
    # Trace norm is sum of singular values.
    # faster: sum(linalg.svdvals(diff))
    
    return 0.5 * np.sum(linalg.svdvals(diff))

def frobenius_norm(A: np.ndarray) -> float:
    """Compute Frobenius norm (Euclidean norm of flattened matrix)."""
    return np.linalg.norm(A, ord='fro')
