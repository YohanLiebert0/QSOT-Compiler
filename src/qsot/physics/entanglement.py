#!/usr/bin/env python3
# entanglement.py — Measure Relativistic Quantum Correlations (Entanglement/Coherence)
import numpy as np

def partial_transpose(rho, dim_a, dim_b):
    """
    Compute Partial Transpose (T_B) of a bipartite density matrix rho_{AB}.
    """
    # Reshape to (da, db, da, db)
    rho_reshaped = rho.reshape(dim_a, dim_b, dim_a, dim_b)
    # Transpose the second subsystem (indices 1 and 3)
    rho_pt = rho_reshaped.transpose(0, 3, 2, 1).reshape(dim_a * dim_b, dim_a * dim_b)
    return rho_pt

def logarithmic_negativity(rho):
    """
    Compute Logarithmic Negativity: E_N(rho) = log2 || rho^TB ||_1
    Used for Multipartite systems (dim >= 4).
    """
    dim_total = rho.shape[0]
    dim_a = 2 
    dim_b = dim_total // dim_a
    
    rho_pt = partial_transpose(rho, dim_a, dim_b)
    eigenvalues = np.linalg.eigvalsh(rho_pt)
    
    # Trace Norm = sum(|eigenvalues|)
    trace_norm = np.sum(np.abs(eigenvalues))
    
    # Log Negativity (0 if separable, >0 if entangled)
    return float(np.log2(trace_norm))

def l1_norm_coherence(rho):
    """
    Compute L1-Norm of Coherence: C(rho) = sum_{i!=j} |rho_{ij}|
    Used for Single Qubit systems (dim = 2).
    """
    off_diag_sum = np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho)))
    return float(off_diag_sum)

def compute_correlation_profile(rhos):
    """
    Analyze the trajectory of quantum correlations.
    - If system is multipartite (dim >= 4): Measures Entanglement.
    - If system is single qubit (dim = 2): Measures Coherence (Superposition).
    """
    profile = []
    metric_name = "Unknown"
    
    if not rhos:
        return {"profile": [], "metric": metric_name}

    # Determine metric based on dimension
    dim = rhos[0].shape[0]
    if dim >= 4:
        metric_name = "Logarithmic Negativity (Entanglement)"
        calc_fn = logarithmic_negativity
    else:
        metric_name = "L1 Coherence (Superposition)"
        calc_fn = l1_norm_coherence
        
    for rho in rhos:
        val = calc_fn(rho)
        profile.append(val)
        
    return {
        "profile": profile,
        "metric": metric_name,
        "avg_value": float(np.mean(profile)),
        "max_value": float(np.max(profile)),
        "final_value": float(profile[-1])
    }
