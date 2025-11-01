"""
Main simulation engine for quantum tunneling.

This module integrates all components:
- Configuration system
- Barrier models
- Wavefunction initialization
- Time evolution
- Boundary conditions
- Visualization
- Diagnostics
"""

import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass, field
from tqdm import tqdm
import matplotlib.pyplot as plt

from wave_tunnel.config import SimulationConfig
from wave_tunnel.barrier_models import create_barrier
from wave_tunnel.time_stepping import calculate_timestep_from_config, estimate_physical_timescales
from wave_tunnel.evolution import evolve_wavefunction
from wave_tunnel.visualization import create_datashader_frame
from wave_tunnel.utils import compute_total_probability


@dataclass
class SimulationResult:
    """Results from a quantum tunneling simulation."""

    config: SimulationConfig
    """Configuration used for this simulation"""

    frames: List = field(default_factory=list)
    """List of visualization frames (PIL images)"""

    times: np.ndarray = field(default_factory=lambda: np.array([]))
    """Array of time points"""

    probabilities: np.ndarray = field(default_factory=lambda: np.array([]))
    """Total probability at each time step"""

    transmission: Optional[float] = None
    """Transmission coefficient (if calculated)"""

    reflection: Optional[float] = None
    """Reflection coefficient (if calculated)"""

    final_wavefunction: Optional[np.ndarray] = None
    """Final wavefunction ψ(x, t_final)"""

    diagnostics: dict = field(default_factory=dict)
    """Additional diagnostic information"""

    def save_animation(self, filename: Optional[str] = None):
        """Save frames as animated GIF."""
        if not self.frames:
            raise ValueError("No frames to save")

        output_file = filename or self.config.output.filename

        print(f"\nSaving animation to {output_file}...")

        # Calculate frame duration
        fps = self.config.visualization.fps
        total_time = self.config.time.total_time
        num_frames = len(self.frames)

        # Duration per frame in milliseconds
        duration = int((total_time / num_frames) * 1000)

        self.frames[0].save(
            output_file,
            save_all=True,
            append_images=self.frames[1:],
            duration=duration,
            loop=0
        )

        print(f"✓ Animation saved: {output_file}")

    def plot_probability_evolution(self, filename: Optional[str] = None):
        """Plot total probability over time."""
        if len(self.probabilities) == 0:
            raise ValueError("No probability data to plot")

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(self.times, self.probabilities, 'b-', linewidth=2)
        ax.axhline(1.0, color='r', linestyle='--', alpha=0.5, label='Perfect conservation')

        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Total Probability', fontsize=12)
        ax.set_title('Probability Conservation', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Show deviation from 1
        deviation = np.abs(self.probabilities - 1.0)
        max_deviation = np.max(deviation)
        ax.text(0.02, 0.98, f'Max deviation: {max_deviation:.2e}',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        output_file = filename or "probability_evolution.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Probability plot saved: {output_file}")

    def print_summary(self):
        """Print simulation summary."""
        print("\n" + "="*70)
        print("SIMULATION RESULTS")
        print("="*70)

        print(f"\nConfiguration: {self.config.name}")
        print(f"Barrier type: {self.config.barrier.type}")
        print(f"Barrier height: V₀ = {self.config.barrier.V0}")
        print(f"Wave packet energy: E = {self.config.wave_packet.energy:.2f}")

        if self.probabilities is not None and len(self.probabilities) > 0:
            initial_prob = self.probabilities[0]
            final_prob = self.probabilities[-1]
            deviation = abs(final_prob - initial_prob)

            print(f"\nProbability Conservation:")
            print(f"  Initial: {initial_prob:.6f}")
            print(f"  Final: {final_prob:.6f}")
            print(f"  Deviation: {deviation:.2e}")

            if deviation < 1e-6:
                print(f"  ✓ Excellent conservation")
            elif deviation < 1e-4:
                print(f"  ✓ Good conservation")
            else:
                print(f"  ⚠ Poor conservation (check time step or boundaries)")

        if self.transmission is not None:
            print(f"\nScattering Coefficients:")
            print(f"  Transmission: T = {self.transmission:.4f}")
            if self.reflection is not None:
                print(f"  Reflection: R = {self.reflection:.4f}")
                print(f"  Sum T+R = {self.transmission + self.reflection:.4f}")

        print(f"\nOutput:")
        print(f"  Animation: {self.config.output.filename}")
        print(f"  Frames: {len(self.frames)}")

        print("="*70 + "\n")


def initialize_wavefunction(config: SimulationConfig, x: np.ndarray) -> np.ndarray:
    """
    Initialize wavefunction from configuration.

    Parameters
    ----------
    config : SimulationConfig
        Simulation configuration
    x : ndarray
        Spatial grid

    Returns
    -------
    psi : ndarray (complex)
        Initial wavefunction
    """
    # Use Gaussian wave packet
    momentum = config.wave_packet.momentum
    x0 = config.wave_packet.x0
    width = config.wave_packet.width

    # Calculate alpha from width: sigma = sqrt(1/alpha) => alpha = 1/sigma^2
    alpha = 1 / (width**2)

    # Construct Gaussian wave packet
    shifted_x = x - x0
    wave = np.exp(1j * momentum * shifted_x)
    gaussian = np.exp(-alpha * shifted_x**2 / 2)
    psi = gaussian * wave

    # Normalize
    dx = x[1] - x[0]
    norm = np.sqrt(np.sum(np.abs(psi)**2) * dx)
    psi = psi / norm

    if config.verbose:
        print("\n" + "="*70)
        print("WAVEFUNCTION INITIALIZATION")
        print("="*70)
        print(f"\nWave Packet Properties:")
        print(f"  Type: Gaussian")
        print(f"  Central momentum: p = {momentum:.4f}")
        print(f"  Kinetic energy: E = {config.wave_packet.energy:.4f}")
        print(f"  Initial position: x₀ = {x0}")
        print(f"  Spatial width: σ = {width:.4f}")
        print(f"  de Broglie wavelength: λ = {config.wave_packet.wavelength:.4f}")
        print(f"  Normalization: ∫|ψ|²dx = {norm:.6f}")
        print("="*70 + "\n")

    return psi


def create_potential_barrier(config: SimulationConfig, x: np.ndarray) -> np.ndarray:
    """
    Create potential barrier from configuration.

    Parameters
    ----------
    config : SimulationConfig
        Simulation configuration
    x : ndarray
        Spatial grid

    Returns
    -------
    V : ndarray
        Potential energy array
    """
    barrier_cfg = config.barrier

    # Handle legacy "current" type (double sigmoid)
    if barrier_cfg.type == 'current':
        # Use original implementation from potentials.py
        from wave_tunnel.potentials import create_potential_barrier
        V = create_potential_barrier(
            x,
            barrier_center=barrier_cfg.center,
            V0=barrier_cfg.V0,
            barrier_width=barrier_cfg.width,
            transition_width=barrier_cfg.transition_width
        )
    else:
        # Use new barrier models
        barrier = create_barrier(
            barrier_cfg.type,
            V0=barrier_cfg.V0,
            width=barrier_cfg.width,
            center=barrier_cfg.center,
            smoothing=barrier_cfg.smoothing,
            # Type-specific parameters
            transition_width=barrier_cfg.transition_width,
            surface_thickness=barrier_cfg.surface_thickness,
            V_left=barrier_cfg.V_left,
            V_right=barrier_cfg.V_right,
            well_width=barrier_cfg.well_width
        )
        V = barrier(x)

    if config.verbose:
        print("="*70)
        print("POTENTIAL BARRIER")
        print("="*70)
        print(f"\nBarrier Type: {barrier_cfg.type}")
        print(f"  Height: V₀ = {barrier_cfg.V0}")
        print(f"  Width: {barrier_cfg.width}")
        print(f"  Center: {barrier_cfg.center}")
        print(f"  Max value: {np.max(V):.4f}")
        print(f"  Min value: {np.min(V):.4f}")

        # Energy comparison
        E = config.wave_packet.energy
        print(f"\nEnergy Analysis:")
        print(f"  Wave packet energy: E = {E:.4f}")
        print(f"  Barrier height: V₀ = {barrier_cfg.V0:.4f}")
        print(f"  Ratio E/V₀ = {E/barrier_cfg.V0:.4f}")

        if E > barrier_cfg.V0:
            print(f"  → Over-barrier transmission (E > V₀)")
        elif E > 0.9 * barrier_cfg.V0:
            print(f"  → Near-barrier regime (mixed behavior)")
        else:
            print(f"  → Tunneling regime (E < V₀)")

        print("="*70 + "\n")

    return V


def create_boundary_potential(config: SimulationConfig, x: np.ndarray) -> Optional[np.ndarray]:
    """
    Create absorbing boundary potential.

    Parameters
    ----------
    config : SimulationConfig
        Simulation configuration
    x : ndarray
        Spatial grid

    Returns
    -------
    W : ndarray or None
        Absorbing potential (None if no boundaries)
    """
    if config.boundary.type == 'periodic':
        return None

    # Use existing PML/absorbing code
    from wave_tunnel.pml import create_pml_absorbing_potential

    boundary_cfg = config.boundary

    # Determine central region
    x_min, x_max = x.min(), x.max()
    width = boundary_cfg.width

    if width is None:
        # Auto: 10% of domain
        domain_width = x_max - x_min
        width = domain_width * 0.1

    central_min = x_min + width
    central_max = x_max - width

    # Create absorbing potential
    W = create_pml_absorbing_potential(
        x,
        pml_width=width,
        pml_strength=boundary_cfg.strength,
        central_region=(central_min, central_max)
    )

    if config.verbose:
        print("="*70)
        print("BOUNDARY CONDITIONS")
        print("="*70)
        print(f"\nType: {boundary_cfg.type}")
        print(f"  Boundary width: {width:.4f}")
        print(f"  Strength parameter: {boundary_cfg.strength}")
        print(f"  Central region: [{central_min:.2f}, {central_max:.2f}]")
        print(f"  Max absorption: {np.max(W):.4f}")
        print("="*70 + "\n")

    return W


def compute_transmission_reflection(
    psi: np.ndarray,
    x: np.ndarray,
    barrier_center: float
) -> Tuple[float, float]:
    """
    Compute transmission and reflection coefficients.

    Parameters
    ----------
    psi : ndarray
        Final wavefunction
    x : ndarray
        Spatial grid
    barrier_center : float
        Center of barrier

    Returns
    -------
    T : float
        Transmission coefficient
    R : float
        Reflection coefficient
    """
    dx = x[1] - x[0]

    # Transmitted: probability to right of barrier
    mask_transmitted = x > barrier_center
    P_transmitted = np.sum(np.abs(psi[mask_transmitted])**2) * dx

    # Reflected: probability to left of barrier
    mask_reflected = x < barrier_center
    P_reflected = np.sum(np.abs(psi[mask_reflected])**2) * dx

    # Normalize
    total = P_transmitted + P_reflected

    if total > 0:
        T = P_transmitted / total
        R = P_reflected / total
    else:
        T = 0.0
        R = 0.0

    return T, R


def run_simulation(config: SimulationConfig) -> SimulationResult:
    """
    Run complete quantum tunneling simulation.

    This is the main entry point that integrates all components.

    Parameters
    ----------
    config : SimulationConfig
        Complete simulation configuration

    Returns
    -------
    result : SimulationResult
        Simulation results including frames, diagnostics, etc.
    """
    # Validate configuration
    config.validate()

    if config.verbose:
        print("\n" + "="*70)
        print(f"STARTING SIMULATION: {config.name}")
        print("="*70 + "\n")

    # Create spatial grid
    x = config.spatial.x
    dx = config.spatial.dx

    # Initialize wavefunction
    psi = initialize_wavefunction(config, x)

    # Create potential barrier
    V = create_potential_barrier(config, x)

    # Create boundary conditions
    W_boundary = create_boundary_potential(config, x)

    # Calculate time step
    if config.time.dt is None:
        dt, dt_info = calculate_timestep_from_config(
            x, V,
            safety_factor=config.time.dt_safety_factor,
            verbose=config.verbose
        )
    else:
        dt = config.time.dt
        if config.verbose:
            print(f"Using manual time step: dt = {dt}")

    # Time array
    num_time_steps = int(config.time.total_time / dt) + 1
    times = np.linspace(0, config.time.total_time, num_time_steps)

    # Frames to capture
    num_frames = config.visualization.num_frames
    frame_indices = np.linspace(0, num_time_steps - 1, num_frames).astype(int)

    # Storage
    frames = []
    probabilities = []

    # Physical time scales (for reference)
    if config.verbose:
        timescales = estimate_physical_timescales(
            config.wave_packet.momentum,
            config.barrier.V0
        )
        print("="*70)
        print("PHYSICAL TIME SCALES")
        print("="*70)
        print(f"\nWave packet:")
        print(f"  de Broglie wavelength: λ = {timescales['wavelength']:.4f}")
        print(f"  Group velocity: v = {timescales['v_group']:.4f}")
        print(f"  Oscillation period: T = {timescales['T_oscillation']:.4f}")
        if timescales['tau_tunnel'] is not None:
            print(f"  Tunneling time estimate: τ ≈ {timescales['tau_tunnel']:.4f}")
        print(f"\nSimulation:")
        print(f"  Total time: {config.time.total_time}")
        print(f"  Time steps: {num_time_steps}")
        print(f"  dt = {dt:.6f}")
        print(f"  Frames: {num_frames}")
        print("="*70 + "\n")

    # Evolution loop
    print(f"Running time evolution...")
    for i in tqdm(range(num_time_steps), disable=not config.verbose):
        # Evolve one time step
        psi = evolve_wavefunction(psi, x, dt, V, W_boundary)

        # Compute diagnostics
        if config.diagnostics.check_norm_conservation:
            total_prob = compute_total_probability(psi, dx)
            probabilities.append(total_prob)

        # Capture frames
        if i in frame_indices:
            vis_settings = {
                'width': config.visualization.width,
                'height': config.visualization.height
            }

            img = create_datashader_frame(
                psi, x, vis_settings,
                barrier_center=config.barrier.center,
                barrier_width=config.barrier.width
            )
            frames.append(img)

    # Final wavefunction
    psi_final = psi.copy()

    # Compute transmission and reflection
    T, R = None, None
    if config.diagnostics.compute_transmission:
        T, R = compute_transmission_reflection(psi_final, x, config.barrier.center)

    # Create result object
    result = SimulationResult(
        config=config,
        frames=frames,
        times=times,
        probabilities=np.array(probabilities),
        transmission=T,
        reflection=R,
        final_wavefunction=psi_final,
        diagnostics={}
    )

    if config.verbose:
        result.print_summary()

    return result
