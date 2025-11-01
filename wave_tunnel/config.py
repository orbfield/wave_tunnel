"""
Configuration system for quantum tunneling simulation.

This module provides dataclasses for all simulation parameters,
validation, and preset physical scenarios.
"""

from dataclasses import dataclass, field, asdict
from typing import Literal, Optional, Dict, Any
import numpy as np
import json


@dataclass
class SpatialConfig:
    """Spatial grid configuration."""

    x_min: float = -100.0
    """Minimum spatial coordinate (length units)"""

    x_max: float = 100.0
    """Maximum spatial coordinate (length units)"""

    num_points: int = 2000
    """Number of spatial grid points"""

    def __post_init__(self):
        if self.x_min >= self.x_max:
            raise ValueError(f"x_min ({self.x_min}) must be < x_max ({self.x_max})")
        if self.num_points < 100:
            raise ValueError(f"num_points must be >= 100, got {self.num_points}")

    @property
    def dx(self) -> float:
        """Grid spacing."""
        return (self.x_max - self.x_min) / self.num_points

    @property
    def x(self) -> np.ndarray:
        """Spatial grid array."""
        return np.linspace(self.x_min, self.x_max, self.num_points)


@dataclass
class TimeConfig:
    """Time evolution configuration."""

    total_time: float = 15.0
    """Total simulation time (time units)"""

    dt: Optional[float] = None
    """Time step (auto-calculated if None)"""

    dt_safety_factor: float = 0.2
    """Safety factor for automatic dt calculation"""

    adaptive_dt: bool = False
    """Use adaptive time stepping (future feature)"""

    def __post_init__(self):
        if self.total_time <= 0:
            raise ValueError(f"total_time must be positive, got {self.total_time}")
        if self.dt is not None and self.dt <= 0:
            raise ValueError(f"dt must be positive, got {self.dt}")
        if not 0 < self.dt_safety_factor <= 1.0:
            raise ValueError(f"dt_safety_factor must be in (0, 1], got {self.dt_safety_factor}")


@dataclass
class WavePacketConfig:
    """Initial wave packet configuration."""

    type: Literal['gaussian', 'cosine'] = 'gaussian'
    """Type of wave packet"""

    momentum: float = 25.13
    """Central momentum (ℏk₀ in natural units)"""

    x0: float = -50.0
    """Initial center position"""

    width: float = 8.9
    """Spatial width σ (standard deviation)"""

    # Legacy parameters for backwards compatibility
    n: Optional[int] = None
    """Legacy: n = m² for kappa = π m³ formula"""

    def __post_init__(self):
        # Handle legacy n parameter
        if self.n is not None:
            m = int(np.sqrt(self.n))
            if m**2 != self.n:
                raise ValueError(f"n must be perfect square, got {self.n}")
            self.momentum = np.pi * (m ** 3)
            # Auto-set width if using legacy mode
            if self.width == 8.9:  # default value
                alpha = 0.0126
                self.width = np.sqrt(1 / alpha)

    @property
    def energy(self) -> float:
        """Kinetic energy of wave packet (in natural units where m=1)."""
        return self.momentum**2 / 2

    @property
    def wavelength(self) -> float:
        """de Broglie wavelength."""
        return 2 * np.pi / self.momentum

    def validate_resolution(self, dx: float, min_points_per_wavelength: int = 10):
        """Validate spatial resolution is adequate."""
        points_per_wavelength = self.wavelength / dx

        if points_per_wavelength < min_points_per_wavelength:
            raise ValueError(
                f"Insufficient resolution: {points_per_wavelength:.1f} points/wavelength. "
                f"Need at least {min_points_per_wavelength}. "
                f"Either increase num_points or decrease momentum."
            )


@dataclass
class BarrierConfig:
    """Potential barrier configuration."""

    type: Literal['rectangular', 'eckart', 'woods-saxon', 'asymmetric',
                  'double', 'current'] = 'rectangular'
    """Barrier model type"""

    V0: float = 320.0
    """Barrier height (energy units)"""

    width: float = 15.0
    """Barrier width (length units)"""

    center: float = 0.0
    """Barrier center position"""

    # Type-specific parameters
    smoothing: float = 0.05
    """Smoothing width for rectangular barrier"""

    transition_width: float = 0.05
    """Transition width for current/sigmoid barrier"""

    surface_thickness: float = 0.5
    """Surface thickness for Woods-Saxon barrier"""

    V_left: Optional[float] = None
    """Left potential for asymmetric barrier"""

    V_right: Optional[float] = None
    """Right potential for asymmetric barrier"""

    well_width: Optional[float] = None
    """Well width for double barrier"""

    def __post_init__(self):
        if self.V0 < 0:
            raise ValueError(f"V0 must be non-negative, got {self.V0}")
        if self.width <= 0:
            raise ValueError(f"width must be positive, got {self.width}")


@dataclass
class BoundaryConfig:
    """Boundary condition configuration."""

    type: Literal['periodic', 'absorbing', 'pml'] = 'absorbing'
    """Boundary condition type"""

    width: Optional[float] = None
    """Boundary layer width (auto: 10% of domain if None)"""

    strength: float = 20.0
    """Absorption/PML strength parameter"""

    target_reflection: float = 0.01
    """Target reflection coefficient"""

    pml_order: int = 2
    """PML polynomial order (for true PML)"""

    auto_tune: bool = True
    """Automatically tune strength for target reflection"""


@dataclass
class VisualizationConfig:
    """Visualization configuration."""

    width: int = 1280
    """Frame width in pixels"""

    height: int = 640
    """Frame height in pixels"""

    fps: int = 50
    """Frames per second"""

    num_frames: Optional[int] = None
    """Number of frames (auto-calculated from fps if None)"""

    colormap_real: str = 'red'
    """Colormap for real part"""

    colormap_imag: str = 'blue'
    """Colormap for imaginary part"""

    colormap_prob: str = 'grey'
    """Colormap for probability density"""

    show_barrier: bool = True
    """Display barrier in visualization"""

    def __post_init__(self):
        if self.width < 100 or self.height < 100:
            raise ValueError(f"Frame dimensions too small: {self.width}x{self.height}")
        if self.fps <= 0:
            raise ValueError(f"fps must be positive, got {self.fps}")


@dataclass
class DiagnosticsConfig:
    """Physics diagnostics configuration."""

    check_norm_conservation: bool = True
    """Monitor probability conservation"""

    check_energy_conservation: bool = True
    """Monitor energy conservation"""

    compute_transmission: bool = True
    """Compute transmission coefficient"""

    compute_reflection: bool = True
    """Compute reflection coefficient"""

    compare_analytical: bool = True
    """Compare with analytical results if available"""

    save_diagnostics: bool = True
    """Save diagnostic data to file"""

    tolerance_norm: float = 1e-6
    """Tolerance for norm conservation check"""

    tolerance_energy: float = 1e-4
    """Tolerance for energy conservation check"""


@dataclass
class OutputConfig:
    """Output configuration."""

    filename: str = "quantum_tunneling.gif"
    """Output animation filename"""

    format: Literal['gif', 'mp4', 'frames'] = 'gif'
    """Output format"""

    save_frames: bool = False
    """Save individual frames as PNGs"""

    export_data: bool = False
    """Export wavefunction data"""

    data_format: Literal['csv', 'hdf5', 'npz'] = 'npz'
    """Data export format"""

    overwrite: bool = True
    """Overwrite existing files"""


@dataclass
class SimulationConfig:
    """Complete simulation configuration."""

    spatial: SpatialConfig = field(default_factory=SpatialConfig)
    time: TimeConfig = field(default_factory=TimeConfig)
    wave_packet: WavePacketConfig = field(default_factory=WavePacketConfig)
    barrier: BarrierConfig = field(default_factory=BarrierConfig)
    boundary: BoundaryConfig = field(default_factory=BoundaryConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    name: str = "Quantum Tunneling Simulation"
    """Simulation name/description"""

    verbose: bool = True
    """Print detailed progress information"""

    def validate(self):
        """Validate configuration and cross-check parameters."""
        # Check wave packet energy vs barrier height
        E = self.wave_packet.energy
        V0 = self.barrier.V0

        if self.verbose:
            if E > V0:
                print(f"⚠️  Wave packet energy ({E:.2f}) > barrier ({V0:.2f}): over-barrier transmission")
            elif E > 0.9 * V0:
                print(f"ℹ️  Wave packet energy ({E:.2f}) near barrier ({V0:.2f}): mixed tunneling/transmission")
            else:
                print(f"✓ Wave packet energy ({E:.2f}) < barrier ({V0:.2f}): tunneling regime")

        # Check spatial resolution
        dx = self.spatial.dx
        self.wave_packet.validate_resolution(dx)

        # Auto-calculate num_frames if needed
        if self.visualization.num_frames is None:
            self.visualization.num_frames = int(self.time.total_time * self.visualization.fps)

        # Auto-calculate boundary width if needed
        if self.boundary.width is None:
            domain_width = self.spatial.x_max - self.spatial.x_min
            self.boundary.width = domain_width * 0.1

        if self.verbose:
            print(f"✓ Configuration validated successfully")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, filename: str):
        """Save configuration to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, filename: str) -> 'SimulationConfig':
        """Load configuration from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        # Reconstruct nested dataclasses
        return cls(
            spatial=SpatialConfig(**data.get('spatial', {})),
            time=TimeConfig(**data.get('time', {})),
            wave_packet=WavePacketConfig(**data.get('wave_packet', {})),
            barrier=BarrierConfig(**data.get('barrier', {})),
            boundary=BoundaryConfig(**data.get('boundary', {})),
            visualization=VisualizationConfig(**data.get('visualization', {})),
            diagnostics=DiagnosticsConfig(**data.get('diagnostics', {})),
            output=OutputConfig(**data.get('output', {})),
            name=data.get('name', 'Quantum Tunneling Simulation'),
            verbose=data.get('verbose', True)
        )

    def __str__(self) -> str:
        """Human-readable summary."""
        lines = [
            f"\n{'='*70}",
            f"{self.name}",
            f"{'='*70}",
            f"\nSpatial Domain:",
            f"  Range: [{self.spatial.x_min}, {self.spatial.x_max}]",
            f"  Grid points: {self.spatial.num_points} (dx = {self.spatial.dx:.4f})",
            f"\nTime Evolution:",
            f"  Total time: {self.time.total_time}",
            f"  Time step: {'auto' if self.time.dt is None else self.time.dt}",
            f"\nWave Packet:",
            f"  Type: {self.wave_packet.type}",
            f"  Momentum: {self.wave_packet.momentum:.4f}",
            f"  Energy: {self.wave_packet.energy:.4f}",
            f"  Position: x₀ = {self.wave_packet.x0}",
            f"  Width: σ = {self.wave_packet.width:.4f}",
            f"  Wavelength: λ = {self.wave_packet.wavelength:.4f}",
            f"\nBarrier:",
            f"  Type: {self.barrier.type}",
            f"  Height: V₀ = {self.barrier.V0}",
            f"  Width: {self.barrier.width}",
            f"  Center: {self.barrier.center}",
            f"\nBoundary Conditions:",
            f"  Type: {self.boundary.type}",
            f"  Width: {self.boundary.width}",
            f"\nVisualization:",
            f"  Resolution: {self.visualization.width}x{self.visualization.height}",
            f"  FPS: {self.visualization.fps}",
            f"  Frames: {self.visualization.num_frames}",
            f"\nOutput:",
            f"  File: {self.output.filename}",
            f"  Format: {self.output.format}",
            f"{'='*70}\n"
        ]
        return '\n'.join(lines)
