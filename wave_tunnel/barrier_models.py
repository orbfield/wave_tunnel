"""
Physically realistic potential barrier models for quantum tunneling.

This module implements various barrier geometries based on real quantum
mechanics scenarios. All models use natural units (ℏ=1, m=1).

References:
-----------
[1] Griffiths, "Introduction to Quantum Mechanics" (3rd ed.), Ch. 2
[2] Cohen-Tannoudji et al., "Quantum Mechanics" Vol. 1, Ch. III
[3] Landau & Lifshitz, "Quantum Mechanics", §25
[4] Eckart, Phys. Rev. 35, 1303 (1930)
"""

import numpy as np
from typing import Tuple, Optional, Literal


class BarrierModel:
    """Base class for potential barrier models."""

    def __init__(self, V0: float, width: float, center: float = 0.0):
        """
        Parameters
        ----------
        V0 : float
            Barrier height (energy units)
        width : float
            Characteristic width (length units)
        center : float
            Center position of barrier
        """
        self.V0 = V0
        self.width = width
        self.center = center

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Evaluate potential at positions x."""
        raise NotImplementedError("Subclass must implement __call__")

    def analytical_transmission(self, energy: float) -> Optional[float]:
        """
        Analytical transmission coefficient T(E) if known.

        Returns None if no closed-form solution exists.
        """
        return None


class RectangularBarrier(BarrierModel):
    """
    Rectangular (square) potential barrier - the canonical tunneling problem.

    V(x) = { V₀  for |x - x₀| < L/2
           { 0   otherwise

    This is the textbook model for:
    - STM vacuum tunneling gap
    - Thin insulating barrier
    - Alpha decay (simplified)

    Physical properties:
    -------------------
    - Discontinuous (unphysical but useful approximation)
    - Analytically solvable
    - Transmission coefficient:
        T(E) = [1 + (V₀²sinh²(κL))/(4E(V₀-E))]⁻¹  for E < V₀
        where κ = √(2m(V₀-E))/ℏ = √(V₀-E) in natural units
    """

    def __init__(self, V0: float, width: float, center: float = 0.0,
                 smoothing: float = 0.0):
        """
        Parameters
        ----------
        smoothing : float, optional
            If > 0, smooth the step function over this length scale.
            Use smoothing ~ dx (grid spacing) to avoid numerical issues.
        """
        super().__init__(V0, width, center)
        self.smoothing = smoothing

    def __call__(self, x: np.ndarray) -> np.ndarray:
        if self.smoothing == 0:
            # True step function
            return np.where(np.abs(x - self.center) < self.width / 2,
                          self.V0, 0.0)
        else:
            # Smoothed step using tanh transitions
            # tanh transitions are C^∞ smooth
            x_left = self.center - self.width / 2
            x_right = self.center + self.width / 2

            # Left edge: 0 → V₀
            edge_left = 0.5 * (1 + np.tanh((x - x_left) / self.smoothing))
            # Right edge: V₀ → 0
            edge_right = 0.5 * (1 + np.tanh((x_right - x) / self.smoothing))

            return self.V0 * edge_left * edge_right

    def analytical_transmission(self, energy: float) -> float:
        """
        Exact transmission coefficient for rectangular barrier.

        References: Griffiths QM (3rd ed.), Problem 2.33
        """
        if energy >= self.V0:
            # Above barrier - free particle oscillations
            k = np.sqrt(energy)
            k0 = np.sqrt(energy - self.V0)

            # Transmission for E > V₀
            T = 1 / (1 + (self.V0**2 * np.sin(k0 * self.width)**2) /
                     (4 * energy * (energy - self.V0)))
        else:
            # Tunneling regime E < V₀
            kappa = np.sqrt(self.V0 - energy)
            k = np.sqrt(energy)

            # Avoid overflow for very thick barriers
            sinh_term = np.sinh(kappa * self.width)

            if sinh_term > 1e100:
                # Asymptotic form: T ~ 16(E/V₀)(1-E/V₀) exp(-2κL)
                T = 16 * (energy / self.V0) * (1 - energy / self.V0) * \
                    np.exp(-2 * kappa * self.width)
            else:
                T = 1 / (1 + (self.V0**2 * sinh_term**2) /
                         (4 * energy * (self.V0 - energy)))

        return T


class EckartBarrier(BarrierModel):
    """
    Eckart potential barrier - smooth, physically realistic, analytically solvable.

    V(x) = V₀ / cosh²((x - x₀)/a)

    Named after Carl Eckart (1930), this barrier models:
    - Molecular scattering potentials
    - Smooth barrier with exponential tails
    - Chemical reaction barriers

    Physical properties:
    -------------------
    - C^∞ smooth (all derivatives exist)
    - Analytically solvable (confluent hypergeometric functions)
    - Maximum at x = x₀
    - Exponential decay: V(x) ~ 4V₀e^(-2|x|/a) for |x| >> a
    - More realistic than rectangular for atomic/molecular systems

    Reference: Eckart, Phys. Rev. 35, 1303 (1930)
    """

    def __init__(self, V0: float, width: float, center: float = 0.0):
        """
        Parameters
        ----------
        width : float
            Scale parameter 'a'. Full width at half maximum ≈ 2.63a
        """
        super().__init__(V0, width, center)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        xi = (x - self.center) / self.width
        return self.V0 / np.cosh(xi)**2

    def analytical_transmission(self, energy: float) -> float:
        """
        Transmission coefficient for Eckart barrier.

        Uses the reflection coefficient from quantum scattering theory.
        See: Landau & Lifshitz, Quantum Mechanics §25
        """
        # Dimensionless parameters
        lambda_param = self.width * np.sqrt(2 * energy)  # k*a in natural units
        s = self.width * np.sqrt(2 * self.V0)

        # Reflection coefficient (simplified for symmetric Eckart)
        # R = |Γ(iλ + 1 - s)|² |Γ(iλ + s)|² / [|Γ(iλ)|² |Γ(iλ + 1)|²]
        # For practical purposes, numerical evaluation needed

        # Asymptotic approximations:
        if energy >> self.V0:
            # High energy: T ≈ 1
            return 1.0
        elif energy << self.V0:
            # Low energy tunneling: WKB approximation
            kappa_eff = np.sqrt(2 * self.V0) * (np.pi / 2)  # Effective barrier
            T = np.exp(-2 * kappa_eff * self.width)
            return min(T, 1.0)
        else:
            # Intermediate regime: return None (needs numerical calculation)
            return None


class WoodsSaxonBarrier(BarrierModel):
    """
    Woods-Saxon potential - models finite surface thickness.

    V(x) = V₀ / [1 + exp((|x - x₀| - R)/a)]

    Originally developed for nuclear potentials, this models:
    - Nuclear surface (finite-range force)
    - Material interfaces with finite transition width
    - Realistic surface potentials

    Physical properties:
    -------------------
    - Smooth sigmoid transitions
    - Surface thickness ~ 4a (10-90% transition)
    - Reduces to step function as a → 0
    - Flat top for |x| < R (constant potential inside)

    This is similar to the current implementation but more physically motivated.

    Reference: Woods & Saxon, Phys. Rev. 95, 577 (1954)
    """

    def __init__(self, V0: float, radius: float, surface_thickness: float,
                 center: float = 0.0):
        """
        Parameters
        ----------
        radius : float
            Radius R where potential is V₀/2
        surface_thickness : float
            Surface thickness parameter 'a'
            10-90% transition width ≈ 4.39a
        """
        super().__init__(V0, width=radius, center=center)
        self.radius = radius
        self.surface_thickness = surface_thickness

    def __call__(self, x: np.ndarray) -> np.ndarray:
        r = np.abs(x - self.center)
        exponent = (r - self.radius) / self.surface_thickness

        # Prevent overflow for large negative exponents
        exponent = np.clip(exponent, -50, 50)

        return self.V0 / (1.0 + np.exp(exponent))


class AsymmetricBarrier(BarrierModel):
    """
    Asymmetric barrier with different potentials on each side.

    Models a material interface where potential changes from V_left to V_right:

    V(x) = { V_left   for x < x₀ - w/2
           { V_trans  smooth transition
           { V_right  for x > x₀ + w/2

    Physical scenarios:
    ------------------
    - Metal-semiconductor junction
    - Heterojunction interfaces
    - Band bending in semiconductors
    - Work function differences
    """

    def __init__(self, V_left: float, V_right: float, center: float = 0.0,
                 transition_width: float = 0.1):
        """
        Parameters
        ----------
        V_left : float
            Potential on left side (x < center)
        V_right : float
            Potential on right side (x > center)
        transition_width : float
            Width of transition region
        """
        V0 = abs(V_right - V_left)
        super().__init__(V0, transition_width, center)
        self.V_left = V_left
        self.V_right = V_right

    def __call__(self, x: np.ndarray) -> np.ndarray:
        # Smooth transition using tanh
        transition = 0.5 * (1 + np.tanh((x - self.center) / self.width))
        return self.V_left + (self.V_right - self.V_left) * transition


class DoubleBarrier(BarrierModel):
    """
    Double barrier with quantum well between - resonant tunneling structure.

    V(x) has two barriers separated by a well, creating:
    - Resonant transmission peaks at E_n (quantized well states)
    - Models quantum well resonant tunneling diodes (RTD)
    - Important in semiconductor nanodevices

    The transmission shows sharp peaks when E aligns with well states.
    """

    def __init__(self, V0: float, barrier_width: float, well_width: float,
                 center: float = 0.0, smoothing: float = 0.01):
        """
        Parameters
        ----------
        barrier_width : float
            Width of each barrier
        well_width : float
            Width of quantum well between barriers
        smoothing : float
            Transition smoothness
        """
        super().__init__(V0, barrier_width, center)
        self.well_width = well_width
        self.smoothing = smoothing

    def __call__(self, x: np.ndarray) -> np.ndarray:
        # Left barrier
        x_left = self.center - self.well_width/2 - self.width/2
        # Right barrier
        x_right = self.center + self.well_width/2 + self.width/2

        # Create two rectangular barriers
        barrier1 = RectangularBarrier(self.V0, self.width, x_left,
                                     self.smoothing)
        barrier2 = RectangularBarrier(self.V0, self.width, x_right,
                                     self.smoothing)

        return barrier1(x) + barrier2(x)


def create_barrier(
    barrier_type: Literal['rectangular', 'eckart', 'woods-saxon',
                          'asymmetric', 'double'],
    **kwargs
) -> BarrierModel:
    """
    Factory function to create barrier models.

    Parameters
    ----------
    barrier_type : str
        Type of barrier: 'rectangular', 'eckart', 'woods-saxon',
                        'asymmetric', 'double'
    **kwargs
        Barrier-specific parameters

    Returns
    -------
    barrier : BarrierModel
        Barrier model instance

    Examples
    --------
    >>> # Rectangular barrier for STM tunneling
    >>> barrier = create_barrier('rectangular', V0=320, width=15, smoothing=0.01)

    >>> # Eckart barrier for molecular scattering
    >>> barrier = create_barrier('eckart', V0=100, width=5, center=0)

    >>> # Material interface
    >>> barrier = create_barrier('asymmetric', V_left=0, V_right=200,
    ...                          center=0, transition_width=0.5)
    """
    models = {
        'rectangular': RectangularBarrier,
        'eckart': EckartBarrier,
        'woods-saxon': WoodsSaxonBarrier,
        'asymmetric': AsymmetricBarrier,
        'double': DoubleBarrier,
    }

    if barrier_type not in models:
        raise ValueError(f"Unknown barrier type: {barrier_type}. "
                        f"Available: {list(models.keys())}")

    return models[barrier_type](**kwargs)
