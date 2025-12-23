#!/usr/bin/env python3
# memory_kernel.py — Real Transfer Tensor Method (TTM) implementation

import numpy as np
from typing import List, Dict, Any

def trace_dist(A: np.ndarray, B: np.ndarray) -> float:
    """Compute Trace Distance: 0.5 * sum(|eigenvalues(A-B)|)"""
    diff = A - B
    # Ensure Hermitian for stability
    diff = (diff + diff.conj().T) / 2.0
    vals = np.linalg.eigvalsh(diff)
    return 0.5 * float(np.sum(np.abs(vals)))

def compute_memory_kernel(rhos: List[np.ndarray], channels: List) -> Dict[str, Any]:
    """
    Compute Non-Markovianity by comparing actual state vs Markovian prediction.
    Deviation[t] = || rho(t+1) - Channel(t)[ rho(t) ] ||_tr
    """
    deviations = []
    accumulated_nm = 0.0
    
    # We compare prediction vs reality for each step
    # Note: rhos has length N+1 (t0...tN), channels has length N
    steps = min(len(rhos)-1, len(channels))
    
    for t in range(steps):
        rho_curr = rhos[t]
        rho_real_next = rhos[t+1]
        
        # 1. Predict next state assuming Markovianity (Memoryless)
        # channel must have .apply() method
        rho_pred_next = channels[t].apply(rho_curr)
        
        # 2. Calculate deviation (Information Backflow / Kernel Norm proxy)
        dev = trace_dist(rho_real_next, rho_pred_next)
        
        deviations.append(dev)
        accumulated_nm += dev

    # Determine Memory Depth (consecutive significant deviations)
    threshold = 1e-6
    depth = 0
    current_streak = 0
    for d in deviations:
        if d > threshold:
            current_streak += 1
            depth = max(depth, current_streak)
        else:
            current_streak = 0
            
    return {
        "nm_measure": accumulated_nm,
        "depth": depth,
        "profile": deviations  # This list will replace the mock profile
    }
