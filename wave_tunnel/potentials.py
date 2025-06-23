# potentials.py

import numpy as np
from pml import create_pml_absorbing_potential

def create_potential_barrier(x, barrier_center=0.0, V0=20.0, barrier_width=1.0, transition_width=0.05):
    """
    Create a potential barrier with smooth transitions.
    """
    V = np.zeros_like(x)
    barrier_start = barrier_center - barrier_width / 2
    barrier_end = barrier_center + barrier_width / 2

    def smooth_step(x, edge, width):
        z = (x - edge) / width
        return 1 / (1 + np.exp(-z))

    V += V0 * (smooth_step(x, barrier_start, transition_width) - smooth_step(x, barrier_end, transition_width))
    return V

def create_total_potential(x, barrier_center=0.0, V0=20.0, barrier_width=1.0, transition_width=0.05):
    """
    Create the total potential including the stationary physical barrier.
    """
    return create_potential_barrier(x, barrier_center, V0, barrier_width, transition_width)

def create_total_potential_with_pml(x, barrier_center=0.0, V0=20.0, barrier_width=1.0, 
                                   transition_width=0.05, pml_params=None):
    """
    Create the total potential including the stationary physical barrier and PML.
    
    Returns:
    - V_total: Physical potential
    - W_pml: PML absorbing potential (None if no PML)
    """
    V_total = create_potential_barrier(x, barrier_center, V0, barrier_width, transition_width)
    
    W_pml = None
    if pml_params is not None:
        W_pml = create_pml_absorbing_potential(
            x, 
            pml_width=pml_params['pml_width'],
            pml_strength=pml_params['pml_strength'],
            central_region=pml_params['central_region']
        )
    
    return V_total, W_pml
