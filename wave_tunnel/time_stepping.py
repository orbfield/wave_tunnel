"""
Time stepping module for quantum evolution.

Implements physics-based time step calculation for split-operator method
with proper stability and accuracy considerations.

References:
-----------
[1] Press et al., "Numerical Recipes", Ch. 20 (Partial Differential Equations)
[2] Tannor, "Introduction to Quantum Mechanics: A Time-Dependent Perspective", Ch. 7
[3] Feit et al., J. Comp. Phys. 47, 412 (1982) - Split-operator method
"""

import numpy as np
from typing import Optional, Tuple


class TimeStepCalculator:
    """Calculate optimal time step for quantum evolution."""

    def __init__(self, x: np.ndarray, V: np.ndarray, verbose: bool = True):
        """
        Parameters
        ----------
        x : ndarray
            Spatial grid
        V : ndarray
            Potential energy (same shape as x)
        verbose : bool
            Print diagnostic information
        """
        self.x = x
        self.V = V
        self.verbose = verbose

        # Compute spatial parameters
        self.dx = x[1] - x[0]
        self.N = len(x)

        # Compute momentum grid
        self.k = np.fft.fftfreq(self.N, d=self.dx) * 2 * np.pi

    def calculate_optimal_dt(
        self,
        safety_factor: float = 0.2,
        method: str = 'split-operator'
    ) -> Tuple[float, dict]:
        """
        Calculate optimal time step with physics-based justification.

        For the split-operator method:
        ψ(t+dt) = exp(-iT dt/2) exp(-iV dt) exp(-iT dt/2) ψ(t)

        This is 2nd-order accurate in time: local error ~ O(dt³)

        Stability: The split-operator method is unconditionally stable for
        the linear Schrödinger equation (all eigenvalues of evolution
        operator have |λ| = 1).

        Accuracy requirement: For 2nd-order method, phase error is
        ε_phase ~ (ω*dt)³ where ω is the characteristic frequency.

        For good accuracy (ε < 1%), need: ω*dt < 0.2

        The maximum frequency is: ω_max = (T_max + V_max) where
        - T_max = k_max²/2 (maximum kinetic energy)
        - V_max = max(V) (maximum potential energy)

        Parameters
        ----------
        safety_factor : float
            Safety factor for dt calculation (default 0.2)
            Smaller = more accurate but slower
        method : str
            Time-stepping method (currently only 'split-operator')

        Returns
        -------
        dt : float
            Optimal time step
        info : dict
            Diagnostic information about the calculation
        """
        # Maximum kinetic energy
        k_max = np.max(np.abs(self.k))
        T_max = k_max**2 / 2

        # Maximum potential energy
        V_max = np.max(self.V)
        V_min = np.min(self.V)

        # Total maximum energy (characteristic frequency)
        omega_max = T_max + V_max

        # Time step from accuracy requirement: ω*dt < safety_factor
        if omega_max > 0:
            dt = safety_factor / omega_max
        else:
            # Fall back to kinetic-only if potential is zero
            dt = safety_factor / T_max

        # Collect diagnostic information
        info = {
            'dx': self.dx,
            'k_max': k_max,
            'T_max': T_max,
            'V_max': V_max,
            'V_min': V_min,
            'omega_max': omega_max,
            'dt': dt,
            'safety_factor': safety_factor,
            'dt_times_omega': dt * omega_max,
            'method': method
        }

        # CFL-like check: for 2nd order method, want dt*ω < 1
        if dt * omega_max >= 1.0:
            if self.verbose:
                print(f"⚠️  Warning: dt*ω = {dt * omega_max:.3f} >= 1.0")
                print(f"   Time step may be too large for accuracy")

        if self.verbose:
            self._print_diagnostics(info)

        return dt, info

    def _print_diagnostics(self, info: dict):
        """Print diagnostic information about time step calculation."""
        print("\n" + "="*70)
        print("TIME STEP CALCULATION")
        print("="*70)

        print(f"\nSpatial Resolution:")
        print(f"  Grid spacing dx = {info['dx']:.6f}")
        print(f"  Maximum wavenumber k_max = {info['k_max']:.4f}")
        print(f"  (Nyquist: k_nyq = π/dx = {np.pi/info['dx']:.4f})")

        print(f"\nEnergy Scales:")
        print(f"  Maximum kinetic energy T_max = {info['T_max']:.4f}")
        print(f"  Maximum potential V_max = {info['V_max']:.4f}")
        print(f"  Minimum potential V_min = {info['V_min']:.4f}")
        print(f"  Characteristic frequency ω_max = {info['omega_max']:.4f}")

        print(f"\nTime Step:")
        print(f"  Method: {info['method']}")
        print(f"  Safety factor: {info['safety_factor']}")
        print(f"  Calculated dt = {info['dt']:.6f}")
        print(f"  Dimensionless parameter dt*ω = {info['dt_times_omega']:.4f}")

        # Accuracy estimate
        phase_error = (info['dt_times_omega'])**3
        print(f"\nAccuracy Estimate:")
        print(f"  Phase error per step ~ (dt*ω)³ ≈ {phase_error:.2e}")
        if phase_error < 1e-6:
            print(f"  ✓ Excellent accuracy expected")
        elif phase_error < 1e-4:
            print(f"  ✓ Good accuracy expected")
        elif phase_error < 1e-2:
            print(f"  ⚠ Moderate accuracy (acceptable for visualization)")
        else:
            print(f"  ⚠ Low accuracy - consider smaller dt")

        print("="*70 + "\n")

    def estimate_total_steps(self, total_time: float, dt: float) -> int:
        """
        Estimate total number of time steps needed.

        Parameters
        ----------
        total_time : float
            Total simulation time
        dt : float
            Time step

        Returns
        -------
        num_steps : int
            Number of time steps
        """
        return int(np.ceil(total_time / dt))


def calculate_timestep_from_config(
    x: np.ndarray,
    V: np.ndarray,
    safety_factor: float = 0.2,
    verbose: bool = True
) -> Tuple[float, dict]:
    """
    Convenience function to calculate time step.

    Parameters
    ----------
    x : ndarray
        Spatial grid
    V : ndarray
        Potential energy
    safety_factor : float
        Safety factor for dt calculation
    verbose : bool
        Print diagnostics

    Returns
    -------
    dt : float
        Optimal time step
    info : dict
        Diagnostic information
    """
    calculator = TimeStepCalculator(x, V, verbose=verbose)
    return calculator.calculate_optimal_dt(safety_factor=safety_factor)


def validate_timestep(dt: float, dx: float, V_max: float, verbose: bool = True) -> bool:
    """
    Validate that time step satisfies stability and accuracy requirements.

    Parameters
    ----------
    dt : float
        Time step to validate
    dx : float
        Spatial grid spacing
    V_max : float
        Maximum potential energy
    verbose : bool
        Print validation results

    Returns
    -------
    valid : bool
        True if time step is acceptable
    """
    # Maximum wavenumber
    k_max = np.pi / dx
    T_max = k_max**2 / 2

    # Characteristic frequency
    omega_max = T_max + V_max

    # Check dimensionless parameter
    dt_omega = dt * omega_max

    if verbose:
        print(f"\nTime Step Validation:")
        print(f"  dt = {dt:.6f}")
        print(f"  dt*ω = {dt_omega:.4f}")

        if dt_omega < 0.1:
            print(f"  ✓ Excellent (high accuracy)")
            valid = True
        elif dt_omega < 0.5:
            print(f"  ✓ Good (adequate accuracy)")
            valid = True
        elif dt_omega < 1.0:
            print(f"  ⚠ Marginal (acceptable for visualization)")
            valid = True
        else:
            print(f"  ❌ Too large (accuracy concerns)")
            valid = False

        if not valid:
            suggested_dt = 0.2 / omega_max
            print(f"  Suggested dt < {suggested_dt:.6f}")

    return valid


# Physical time scales for reference
def estimate_physical_timescales(momentum: float, barrier_height: float) -> dict:
    """
    Estimate relevant physical time scales for quantum tunneling.

    Parameters
    ----------
    momentum : float
        Wave packet momentum (ℏk in natural units)
    barrier_height : float
        Barrier height V₀

    Returns
    -------
    timescales : dict
        Dictionary of characteristic time scales
    """
    # de Broglie wavelength
    wavelength = 2 * np.pi / momentum

    # Group velocity (in natural units where m=1)
    v_group = momentum  # v = p/m = p for m=1

    # Classical traversal time (if above barrier)
    E = momentum**2 / 2
    if E > barrier_height:
        # Above barrier - classical motion
        v_classical = np.sqrt(2 * (E - barrier_height))
    else:
        v_classical = None

    # Quantum oscillation period at momentum k
    T_oscillation = 2 * np.pi / E

    # Tunneling time estimate (controversial, but useful order of magnitude)
    # Büttiker-Landauer time: τ ~ ℏ/(E(1-E/V₀))
    if E < barrier_height and E > 0:
        tau_tunnel = 1.0 / (E * (1 - E / barrier_height))
    else:
        tau_tunnel = None

    return {
        'wavelength': wavelength,
        'v_group': v_group,
        'v_classical': v_classical,
        'T_oscillation': T_oscillation,
        'tau_tunnel': tau_tunnel,
        'energy': E,
        'barrier_height': barrier_height
    }
