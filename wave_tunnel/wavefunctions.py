# wavefunctions.py

import numpy as np

def calculate_kappa_n(n):
    """Calculate κₙ using m³ structure where n = m²."""
    m = int(np.sqrt(n))
    if m**2 != n:
        raise ValueError(f"n must be a perfect square. Received n={n}")
    return np.pi * (m ** 3)

def wavefunction_1d(x, n, x0=0.0):
    """
    Calculate the 1D wavefunction as a plane wave modulated by a Gaussian envelope centered at x0.
    """
    kappa = calculate_kappa_n(n)
    alpha = 0.0126  # Gaussian width parameter
    shifted_x = x - x0
    wave = np.exp(1j * kappa * shifted_x)
    gaussian = np.exp(-alpha * shifted_x**2 / 2)
    psi = gaussian * wave
    dx = x[1] - x[0]
    norm = np.sqrt(np.sum(np.abs(psi)**2) * dx)
    return psi / norm

def initialize_wavefunction_custom(x, n, x0=-100.0):
    """
    Initialize a custom Gaussian-modulated wave packet centered at x0.
    """
    return wavefunction_1d(x, n, x0)
