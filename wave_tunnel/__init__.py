"""
Quantum Tunneling Simulation Platform

A comprehensive platform for simulating quantum tunneling phenomena with
multiple barrier models, physically realistic parameters, and professional
visualization capabilities.

Main Components:
---------------
- simulator: Main simulation engine
- config: Configuration system (dataclasses)
- presets: Physical scenario presets
- barrier_models: Barrier potential models
- cli: Command-line interface

Quick Start:
-----------
>>> from wave_tunnel import presets, simulator
>>> config = presets.get_preset('stm')
>>> result = simulator.run_simulation(config)
>>> result.save_animation()

Or use the CLI:
    python -m wave_tunnel.cli --preset stm
"""

__version__ = "0.2.0"
__author__ = "orbfield"

# Import main components for easy access
from wave_tunnel.config import SimulationConfig
from wave_tunnel.simulator import run_simulation, SimulationResult
from wave_tunnel import presets
from wave_tunnel import barrier_models

__all__ = [
    'SimulationConfig',
    'run_simulation',
    'SimulationResult',
    'presets',
    'barrier_models',
]
