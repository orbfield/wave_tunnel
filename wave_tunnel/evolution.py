# evolution.py

import numpy as np
from wave_tunnel.pml import apply_pml_damping

def evolve_wavefunction(psi, x, dt, V_total, W_pml=None):
    """
    Evolve the wavefunction psi by a time step dt using the split-operator method.
    Optionally applies PML boundary conditions.
    """
    dx = x[1] - x[0]
    N = len(x)
    k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
    T = (k**2) / 2  # Kinetic energy operator
    exp_T = np.exp(-1j * T * dt / 2)
    exp_V = np.exp(-1j * V_total * dt)

    # Half step in momentum space
    psi_k = np.fft.fft(psi)
    psi_k *= exp_T
    psi = np.fft.ifft(psi_k)

    # Full step in position space
    psi *= exp_V

    # Another half step in momentum space
    psi_k = np.fft.fft(psi)
    psi_k *= exp_T
    psi = np.fft.ifft(psi_k)

    # Apply PML damping if provided
    if W_pml is not None:
        psi = apply_pml_damping(psi, W_pml, dt)

    return psi
