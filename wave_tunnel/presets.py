"""
Preset configurations for real physical scenarios.

Each preset represents a real quantum tunneling phenomenon with
physically realistic parameters (converted to natural units).

References:
-----------
[1] Binning & Rohrer, "Scanning Tunneling Microscopy", Surf. Sci. 126, 236 (1983)
[2] Esaki & Tsu, "Superlattice and negative differential conductivity", IBM J. 14, 61 (1970)
[3] Gamow, "Quantum theory of atomic nucleus", Z. Phys. 51, 204 (1928)
"""

from wave_tunnel.config import (
    SimulationConfig, SpatialConfig, TimeConfig, WavePacketConfig,
    BarrierConfig, BoundaryConfig, VisualizationConfig,
    DiagnosticsConfig, OutputConfig
)


def stm_vacuum_tunneling() -> SimulationConfig:
    """
    Scanning Tunneling Microscope (STM) - electron tunneling through vacuum gap.

    Physical scenario:
    -----------------
    - Electron tunneling between metal tip and surface
    - Vacuum barrier width: ~5-10 Angstroms
    - Work function: ~4-5 eV
    - Electron energy: ~4 eV (Fermi level)

    Scaled to natural units for simulation.

    Reference: Binning & Rohrer, Nobel Prize in Physics 1986
    """
    return SimulationConfig(
        name="STM Vacuum Tunneling",
        spatial=SpatialConfig(
            x_min=-50.0,
            x_max=50.0,
            num_points=2000
        ),
        time=TimeConfig(
            total_time=10.0,
            dt_safety_factor=0.2
        ),
        wave_packet=WavePacketConfig(
            type='gaussian',
            momentum=20.0,  # E ≈ 200 (just below barrier)
            x0=-30.0,
            width=5.0
        ),
        barrier=BarrierConfig(
            type='rectangular',
            V0=220.0,  # Slightly above electron energy
            width=2.0,  # Thin vacuum gap
            center=0.0,
            smoothing=0.02  # Very sharp transitions
        ),
        boundary=BoundaryConfig(
            type='absorbing',
            target_reflection=0.001
        ),
        visualization=VisualizationConfig(
            width=1280,
            height=640,
            fps=50
        ),
        diagnostics=DiagnosticsConfig(
            compare_analytical=True
        ),
        output=OutputConfig(
            filename="stm_tunneling.gif"
        )
    )


def alpha_decay() -> SimulationConfig:
    """
    Alpha decay - quantum tunneling through Coulomb barrier.

    Physical scenario:
    -----------------
    - Alpha particle escaping atomic nucleus
    - Coulomb barrier + nuclear potential
    - Approximated as Eckart barrier
    - Energy: just below barrier top

    Scaled to natural units for simulation.

    Reference: Gamow (1928), first application of quantum tunneling
    """
    return SimulationConfig(
        name="Alpha Decay (Gamow Model)",
        spatial=SpatialConfig(
            x_min=-100.0,
            x_max=100.0,
            num_points=3000
        ),
        time=TimeConfig(
            total_time=20.0,
            dt_safety_factor=0.15
        ),
        wave_packet=WavePacketConfig(
            type='gaussian',
            momentum=18.0,  # E ≈ 162
            x0=-60.0,
            width=8.0
        ),
        barrier=BarrierConfig(
            type='eckart',
            V0=200.0,
            width=10.0,  # Coulomb barrier width
            center=0.0
        ),
        boundary=BoundaryConfig(
            type='absorbing',
            width=20.0,
            target_reflection=0.01
        ),
        visualization=VisualizationConfig(
            fps=40
        ),
        output=OutputConfig(
            filename="alpha_decay.gif"
        )
    )


def resonant_tunneling_diode() -> SimulationConfig:
    """
    Resonant Tunneling Diode (RTD) - double barrier quantum well.

    Physical scenario:
    -----------------
    - Two thin barriers with quantum well between
    - Resonant transmission at quantized energy levels
    - Shows negative differential resistance
    - AlGaAs/GaAs heterostructure

    Reference: Esaki & Tsu (1970), Chang et al. Appl. Phys. Lett. 24, 593 (1974)
    """
    return SimulationConfig(
        name="Resonant Tunneling Diode",
        spatial=SpatialConfig(
            x_min=-80.0,
            x_max=80.0,
            num_points=2500
        ),
        time=TimeConfig(
            total_time=25.0,
            dt_safety_factor=0.2
        ),
        wave_packet=WavePacketConfig(
            type='gaussian',
            momentum=14.0,  # E ≈ 98 (tuned to well resonance)
            x0=-50.0,
            width=6.0
        ),
        barrier=BarrierConfig(
            type='double',
            V0=150.0,
            width=2.0,  # Thin barriers
            well_width=8.0,  # Quantum well
            center=0.0,
            smoothing=0.05
        ),
        boundary=BoundaryConfig(
            type='absorbing',
            width=15.0
        ),
        visualization=VisualizationConfig(
            fps=60,
            width=1600,
            height=800
        ),
        diagnostics=DiagnosticsConfig(
            compute_transmission=True,
            compare_analytical=False  # No simple analytical form
        ),
        output=OutputConfig(
            filename="rtd_resonant_tunneling.gif",
            export_data=True
        )
    )


def tunnel_junction_oxide() -> SimulationConfig:
    """
    Tunnel junction - electron tunneling through thin oxide barrier.

    Physical scenario:
    -----------------
    - Aluminum oxide (Al₂O₃) barrier between metal electrodes
    - Barrier thickness: ~1-3 nm
    - Barrier height: ~2 eV
    - Used in: Josephson junctions, magnetic tunnel junctions

    This is what the CURRENT implementation models!
    """
    return SimulationConfig(
        name="Tunnel Junction (Oxide Barrier)",
        spatial=SpatialConfig(
            x_min=-100.0,
            x_max=100.0,
            num_points=2000
        ),
        time=TimeConfig(
            total_time=15.0
        ),
        wave_packet=WavePacketConfig(
            momentum=25.13,  # Original n=4 case
            x0=-50.0,
            width=8.9
        ),
        barrier=BarrierConfig(
            type='current',  # Double-sigmoid barrier
            V0=320.0,
            width=15.0,
            center=0.0,
            transition_width=0.05
        ),
        boundary=BoundaryConfig(
            type='absorbing',
            strength=20.0
        ),
        visualization=VisualizationConfig(
            width=1280,
            height=640,
            fps=50
        ),
        output=OutputConfig(
            filename="tunnel_junction.gif"
        )
    )


def molecular_scattering() -> SimulationConfig:
    """
    Molecular collision - smooth potential barrier.

    Physical scenario:
    -----------------
    - Molecule scattering off potential barrier
    - Eckart barrier (smooth, realistic molecular potential)
    - Mixed reflection/transmission/tunneling

    Reference: Eckart barrier commonly used in molecular dynamics
    """
    return SimulationConfig(
        name="Molecular Scattering (Eckart Barrier)",
        spatial=SpatialConfig(
            x_min=-100.0,
            x_max=100.0,
            num_points=2500
        ),
        time=TimeConfig(
            total_time=18.0
        ),
        wave_packet=WavePacketConfig(
            momentum=22.0,
            x0=-55.0,
            width=7.0
        ),
        barrier=BarrierConfig(
            type='eckart',
            V0=280.0,
            width=6.0,
            center=0.0
        ),
        boundary=BoundaryConfig(
            type='absorbing'
        ),
        visualization=VisualizationConfig(
            fps=45
        ),
        output=OutputConfig(
            filename="molecular_scattering.gif"
        )
    )


def semiconductor_heterojunction() -> SimulationConfig:
    """
    Semiconductor heterojunction - asymmetric barrier.

    Physical scenario:
    -----------------
    - Band offset at material interface (e.g., GaAs/AlGaAs)
    - Different potential on each side
    - Models electron crossing heterostructure

    Used in: LEDs, laser diodes, HEMTs
    """
    return SimulationConfig(
        name="Semiconductor Heterojunction",
        spatial=SpatialConfig(
            x_min=-80.0,
            x_max=80.0,
            num_points=2000
        ),
        time=TimeConfig(
            total_time=12.0
        ),
        wave_packet=WavePacketConfig(
            momentum=20.0,
            x0=-45.0,
            width=6.0
        ),
        barrier=BarrierConfig(
            type='asymmetric',
            V_left=0.0,
            V_right=150.0,  # Band offset
            center=0.0,
            transition_width=0.5  # Interface width
        ),
        boundary=BoundaryConfig(
            type='absorbing'
        ),
        output=OutputConfig(
            filename="heterojunction.gif"
        )
    )


def textbook_rectangular() -> SimulationConfig:
    """
    Textbook quantum tunneling - rectangular barrier.

    Physical scenario:
    -----------------
    - Idealized rectangular barrier (step functions)
    - Classic quantum mechanics problem
    - Analytically solvable
    - Good for teaching and validation

    Reference: Griffiths QM textbook, Chapter 2
    """
    return SimulationConfig(
        name="Textbook Rectangular Barrier",
        spatial=SpatialConfig(
            x_min=-60.0,
            x_max=60.0,
            num_points=2000
        ),
        time=TimeConfig(
            total_time=10.0
        ),
        wave_packet=WavePacketConfig(
            momentum=18.0,  # E = 162
            x0=-35.0,
            width=5.0
        ),
        barrier=BarrierConfig(
            type='rectangular',
            V0=200.0,
            width=10.0,
            center=0.0,
            smoothing=0.01  # Minimal smoothing
        ),
        boundary=BoundaryConfig(
            type='absorbing'
        ),
        diagnostics=DiagnosticsConfig(
            compare_analytical=True  # Can compare with exact solution
        ),
        output=OutputConfig(
            filename="textbook_tunneling.gif"
        )
    )


# Registry of all presets
PRESETS = {
    'stm': stm_vacuum_tunneling,
    'alpha_decay': alpha_decay,
    'rtd': resonant_tunneling_diode,
    'tunnel_junction': tunnel_junction_oxide,
    'molecular': molecular_scattering,
    'heterojunction': semiconductor_heterojunction,
    'textbook': textbook_rectangular,
}


def list_presets() -> None:
    """Print all available presets."""
    print("\n" + "="*70)
    print("AVAILABLE PRESETS")
    print("="*70)

    for name, preset_func in PRESETS.items():
        config = preset_func()
        print(f"\n{name}:")
        print(f"  {config.name}")
        print(f"  Barrier: {config.barrier.type}, V₀={config.barrier.V0}")
        print(f"  Energy: E={config.wave_packet.energy:.2f}")

    print("\n" + "="*70)


def get_preset(name: str) -> SimulationConfig:
    """
    Get a preset configuration by name.

    Parameters
    ----------
    name : str
        Preset name (stm, alpha_decay, rtd, tunnel_junction,
        molecular, heterojunction, textbook)

    Returns
    -------
    config : SimulationConfig
        Configuration object

    Examples
    --------
    >>> config = get_preset('stm')
    >>> config.validate()
    """
    if name not in PRESETS:
        available = ', '.join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")

    return PRESETS[name]()
