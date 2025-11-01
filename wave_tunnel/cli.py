#!/usr/bin/env python3
"""
Command-line interface for quantum tunneling simulation.

Usage:
    python -m wave_tunnel.cli --preset stm
    python -m wave_tunnel.cli --config my_config.json
    python -m wave_tunnel.cli --interactive
"""

import argparse
import sys
from pathlib import Path

from wave_tunnel.config import SimulationConfig
from wave_tunnel.presets import PRESETS, list_presets, get_preset


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Quantum Tunneling Simulation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run preset simulation
  %(prog)s --preset stm

  # List all presets
  %(prog)s --list-presets

  # Load from config file
  %(prog)s --config my_config.json

  # Run with custom parameters
  %(prog)s --barrier-type rectangular --V0 300 --width 10

  # Export configuration template
  %(prog)s --export-config template.json

  # Interactive mode
  %(prog)s --interactive

Physical Scenarios:
  stm              - Scanning tunneling microscope (vacuum gap)
  alpha_decay      - Alpha particle decay (Coulomb barrier)
  rtd              - Resonant tunneling diode (double barrier)
  tunnel_junction  - Tunnel junction oxide barrier
  molecular        - Molecular scattering (Eckart barrier)
  heterojunction   - Semiconductor heterojunction
  textbook         - Textbook rectangular barrier
"""
    )

    # Preset or config file
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '--preset', '-p',
        choices=list(PRESETS.keys()),
        help='Use preset configuration'
    )
    input_group.add_argument(
        '--config', '-c',
        type=Path,
        help='Load configuration from JSON file'
    )

    # Output
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output filename (default: from config)'
    )

    # Utility commands
    parser.add_argument(
        '--list-presets', '-l',
        action='store_true',
        help='List all available presets'
    )
    parser.add_argument(
        '--export-config',
        type=Path,
        metavar='FILE',
        help='Export configuration template to JSON file'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive configuration mode'
    )

    # Barrier parameters
    barrier_group = parser.add_argument_group('Barrier Parameters')
    barrier_group.add_argument('--barrier-type', choices=['rectangular', 'eckart', 'woods-saxon', 'asymmetric', 'double', 'current'])
    barrier_group.add_argument('--V0', type=float, help='Barrier height')
    barrier_group.add_argument('--width', type=float, help='Barrier width')
    barrier_group.add_argument('--center', type=float, help='Barrier center position')

    # Wave packet parameters
    wave_group = parser.add_argument_group('Wave Packet Parameters')
    wave_group.add_argument('--momentum', type=float, help='Wave packet momentum')
    wave_group.add_argument('--x0', type=float, help='Initial position')
    wave_group.add_argument('--packet-width', type=float, help='Wave packet width (sigma)')

    # Spatial parameters
    spatial_group = parser.add_argument_group('Spatial Domain')
    spatial_group.add_argument('--x-min', type=float, help='Minimum x coordinate')
    spatial_group.add_argument('--x-max', type=float, help='Maximum x coordinate')
    spatial_group.add_argument('--num-points', type=int, help='Number of spatial grid points')

    # Time parameters
    time_group = parser.add_argument_group('Time Evolution')
    time_group.add_argument('--total-time', type=float, help='Total simulation time')
    time_group.add_argument('--dt', type=float, help='Time step (default: auto)')

    # Visualization
    vis_group = parser.add_argument_group('Visualization')
    vis_group.add_argument('--fps', type=int, help='Frames per second')
    vis_group.add_argument('--resolution', type=str, metavar='WxH', help='Frame resolution (e.g., 1920x1080)')

    # Diagnostics
    parser.add_argument(
        '--no-diagnostics',
        action='store_true',
        help='Disable physics diagnostics'
    )
    parser.add_argument(
        '--export-data',
        action='store_true',
        help='Export wavefunction data'
    )

    # Verbosity
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    return parser


def apply_cli_overrides(config: SimulationConfig, args: argparse.Namespace) -> SimulationConfig:
    """Apply command-line parameter overrides to configuration."""

    # Barrier parameters
    if args.barrier_type is not None:
        config.barrier.type = args.barrier_type
    if args.V0 is not None:
        config.barrier.V0 = args.V0
    if args.width is not None:
        config.barrier.width = args.width
    if args.center is not None:
        config.barrier.center = args.center

    # Wave packet
    if args.momentum is not None:
        config.wave_packet.momentum = args.momentum
    if args.x0 is not None:
        config.wave_packet.x0 = args.x0
    if args.packet_width is not None:
        config.wave_packet.width = args.packet_width

    # Spatial
    if args.x_min is not None:
        config.spatial.x_min = args.x_min
    if args.x_max is not None:
        config.spatial.x_max = args.x_max
    if args.num_points is not None:
        config.spatial.num_points = args.num_points

    # Time
    if args.total_time is not None:
        config.time.total_time = args.total_time
    if args.dt is not None:
        config.time.dt = args.dt

    # Visualization
    if args.fps is not None:
        config.visualization.fps = args.fps
    if args.resolution is not None:
        try:
            w, h = map(int, args.resolution.lower().split('x'))
            config.visualization.width = w
            config.visualization.height = h
        except ValueError:
            print(f"⚠️  Invalid resolution format: {args.resolution}. Use WIDTHxHEIGHT (e.g., 1920x1080)")

    # Output
    if args.output is not None:
        config.output.filename = args.output

    # Diagnostics
    if args.no_diagnostics:
        config.diagnostics.check_norm_conservation = False
        config.diagnostics.check_energy_conservation = False
        config.diagnostics.compute_transmission = False

    if args.export_data:
        config.output.export_data = True

    # Verbosity
    if args.quiet:
        config.verbose = False
    if args.verbose:
        config.verbose = True

    return config


def interactive_mode() -> SimulationConfig:
    """Interactive configuration wizard."""
    print("\n" + "="*70)
    print("QUANTUM TUNNELING SIMULATION - Interactive Setup")
    print("="*70)

    # Choose preset or custom
    print("\n1. Start from preset or create custom configuration?")
    print("   Presets available:")
    for i, (name, preset_func) in enumerate(PRESETS.items(), 1):
        config = preset_func()
        print(f"   {i}. {name:20s} - {config.name}")

    print(f"   {len(PRESETS) + 1}. Custom configuration")

    choice = input(f"\nChoice [1-{len(PRESETS) + 1}]: ").strip()

    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(PRESETS):
            preset_name = list(PRESETS.keys())[choice_num - 1]
            config = get_preset(preset_name)
            print(f"\n✓ Loaded preset: {config.name}")
        else:
            config = SimulationConfig()
            print("\n✓ Starting with default configuration")
    except ValueError:
        config = SimulationConfig()
        print("\n✓ Starting with default configuration")

    # Ask if user wants to modify
    modify = input("\nModify parameters? [y/N]: ").strip().lower()
    if modify == 'y':
        # Barrier type
        print(f"\nBarrier type (current: {config.barrier.type})")
        print("  Options: rectangular, eckart, woods-saxon, asymmetric, double, current")
        barrier_type = input("  [press Enter to keep current]: ").strip()
        if barrier_type:
            config.barrier.type = barrier_type

        # Barrier height
        V0 = input(f"Barrier height V₀ (current: {config.barrier.V0}): ").strip()
        if V0:
            config.barrier.V0 = float(V0)

        # Wave packet momentum
        momentum = input(f"Wave packet momentum (current: {config.wave_packet.momentum:.2f}): ").strip()
        if momentum:
            config.wave_packet.momentum = float(momentum)

        print("\n✓ Configuration updated")

    return config


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Utility commands
    if args.list_presets:
        list_presets()
        return 0

    if args.export_config:
        config = SimulationConfig()
        config.to_json(str(args.export_config))
        print(f"✓ Exported configuration template to {args.export_config}")
        return 0

    # Interactive mode
    if args.interactive:
        config = interactive_mode()
    # Load from preset
    elif args.preset:
        config = get_preset(args.preset)
        print(f"\n✓ Loaded preset: {config.name}")
    # Load from config file
    elif args.config:
        if not args.config.exists():
            print(f"❌ Configuration file not found: {args.config}", file=sys.stderr)
            return 1
        config = SimulationConfig.from_json(str(args.config))
        print(f"\n✓ Loaded configuration from {args.config}")
    else:
        # No input specified - use default
        print("\nNo preset or config specified. Use --help for options.")
        print("Using default configuration...\n")
        config = SimulationConfig()

    # Apply CLI overrides
    config = apply_cli_overrides(config, args)

    # Validate
    try:
        config.validate()
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}", file=sys.stderr)
        return 1

    # Print configuration
    if config.verbose:
        print(config)

    # Save config if requested
    save_config = input("\nSave this configuration to file? [y/N]: ").strip().lower()
    if save_config == 'y':
        filename = input("Filename [simulation_config.json]: ").strip() or "simulation_config.json"
        config.to_json(filename)
        print(f"✓ Saved configuration to {filename}")

    # Run simulation
    print("\n" + "="*70)
    print("RUNNING SIMULATION")
    print("="*70 + "\n")

    try:
        # Import here to avoid circular dependency
        from wave_tunnel.simulator import run_simulation

        run_simulation(config)

        print(f"\n✓ Simulation complete!")
        print(f"✓ Output saved to: {config.output.filename}")

        return 0

    except ImportError:
        print("\n⚠️  Simulation engine not yet implemented.")
        print("Configuration is ready. Next step: implement simulator.py")
        return 0
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
