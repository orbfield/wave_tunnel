# pml.py

import numpy as np

def create_pml_absorbing_potential(x, pml_width=5.0, pml_strength=10.0, central_region=None):
    """
    Create a Perfectly Matched Layer (PML) absorbing potential.
    
    Parameters:
    - x: Spatial grid points.
    - pml_width: Width of the PML regions.
    - pml_strength: Maximum strength of the absorbing potential.
    - central_region: Tuple defining the central simulation region (min, max).
                     If None, automatically determined from domain.
    
    Returns:
    - W_pml: Absorbing potential array (positive real numbers).
    """
    W_pml = np.zeros_like(x)
    x_min, x_max = x.min(), x.max()
    
    if central_region is None:
        # Define central region as middle portion of domain
        domain_width = x_max - x_min
        central_min = x_min + pml_width
        central_max = x_max - pml_width
    else:
        central_min, central_max = central_region

    # Left PML (between x_min and central_min)
    mask_left = (x >= x_min) & (x <= central_min)
    if np.any(mask_left):
        # Distance from left boundary of PML region
        distance_from_boundary = central_min - x[mask_left]
        normalized_distance = distance_from_boundary / pml_width
        # Ensure we don't exceed pml_width
        normalized_distance = np.clip(normalized_distance, 0, 1)
        W_pml[mask_left] = pml_strength * normalized_distance**2

    # Right PML (between central_max and x_max)
    mask_right = (x >= central_max) & (x <= x_max)
    if np.any(mask_right):
        # Distance from right boundary of PML region
        distance_from_boundary = x[mask_right] - central_max
        normalized_distance = distance_from_boundary / pml_width
        # Ensure we don't exceed pml_width
        normalized_distance = np.clip(normalized_distance, 0, 1)
        W_pml[mask_right] = pml_strength * normalized_distance**2

    return W_pml

def apply_pml_damping(psi, W_pml, dt):
    """
    Apply PML damping to the wavefunction.
    
    Parameters:
    - psi: Current wavefunction.
    - W_pml: PML absorbing potential.
    - dt: Time step.
    
    Returns:
    - psi_damped: Wavefunction after PML damping.
    """
    # Apply exponential damping where PML is active

    damping_factor = np.exp(-W_pml * dt * 2.0)
    return psi * damping_factor

def get_pml_parameters(spatial_range):
    """
    Get default PML parameters based on spatial range.
    
    Parameters:
    - spatial_range: Tuple (x_min, x_max) of the spatial domain.
    
    Returns:
    - Dictionary with PML parameters.
    """
    x_min, x_max = spatial_range
    domain_width = x_max - x_min
    
    pml_width = domain_width * 0.1
    
    central_min = x_min + pml_width
    central_max = x_max - pml_width
    
    pml_strength = 20.0
    
    return {
        'pml_width': pml_width,
        'pml_strength': pml_strength,
        'central_region': (central_min, central_max),
    }
