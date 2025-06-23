# utils.py

import numpy as np

def compute_total_probability(psi, dx):
    """
    Compute the total probability density of the wavefunction.
    """
    return np.sum(np.abs(psi)**2) * dx
