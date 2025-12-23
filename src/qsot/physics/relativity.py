#!/usr/bin/env python3
# relativity.py - Relativistic Channel Boosting [v0.2.0]

import numpy as np


def lorentz_factor(beta: float) -> float:
    """Calculate gamma = 1 / sqrt(1 - beta^2)."""
    if abs(beta) >= 1.0:
        raise ValueError("Velocity beta must be < 1.0")
    return 1.0 / np.sqrt(1.0 - beta**2)


def boost_damping_channel(prob: float, beta: float) -> float:
    """
    Boost phase damping parameter p(t).
    p' = 1 - (1 - p)^gamma
    """
    if beta == 0.0:
        return prob

    gamma = lorentz_factor(beta)
    # Avoid numerical issues if prob is close to 1
    return 1.0 - np.power(1.0 - prob, gamma)


def apply_time_dilation(times: list[float], beta: float) -> list[float]:
    """t' = gamma * t"""
    gamma = lorentz_factor(beta)
    return [t * gamma for t in times]
