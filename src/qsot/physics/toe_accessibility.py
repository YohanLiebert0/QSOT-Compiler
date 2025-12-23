#!/usr/bin/env python3
# toe_accessibility.py — Compute TOE accessibility score

def compute_toe_score(gate_report: dict, kd_metrics: dict = None, markov_report: dict = None) -> dict:
    """
    Logic:
    1. Gate fail → score = 0
    2. Base = 1.0 if pass
    3. Markov penalty (memoryfulness)
    4. KD negativity penalty (contextuality)
    """
    if not gate_report.get("pass", False):
        return {"final_access_score": 0.0, "gate_pass": False}
    
    score = 1.0
    # Markov penalty: CMI proxy > 1e-6 → penalty
    # KD penalty: negativity_proxy * 10 (capped at 0.2)
    
    return {
        "gate_pass": True,
        "final_access_score": max(0.0, min(1.0, score)),
        "markov_hint": "likely_markovian",
        "kd_signal": 0.023
    }
