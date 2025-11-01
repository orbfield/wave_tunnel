#!/usr/bin/env python3
"""
Test script for the new simulation engine.

Tests the complete integration of all components.
"""

import sys
sys.path.insert(0, '/home/user/wave_tunnel')

from wave_tunnel.presets import get_preset
from wave_tunnel.simulator import run_simulation

print("\n" + "="*70)
print("TESTING QUANTUM TUNNELING SIMULATION PLATFORM")
print("="*70)

# Test 1: Load a simple preset (use tunnel_junction - the original implementation)
print("\nTest 1: Loading tunnel_junction preset (original implementation)...")
try:
    config = get_preset('tunnel_junction')
    print("✓ Preset loaded successfully")
    print(f"  Barrier type: {config.barrier.type}")
    print(f"  V₀ = {config.barrier.V0}")
    print(f"  E = {config.wave_packet.energy:.2f}")
except Exception as e:
    print(f"❌ Failed to load preset: {e}")
    sys.exit(1)

# Test 2: Modify for quick test
print("\nTest 2: Modifying for quick test run...")
config.time.total_time = 3.0  # Short simulation
config.visualization.num_frames = 30  # Few frames
config.output.filename = "test_output.gif"
config.verbose = True
print(f"  Using {config.spatial.num_points} grid points")

# Test 3: Run simulation
print("\nTest 3: Running simulation...")
try:
    result = run_simulation(config)
    print("✓ Simulation completed successfully")
    print(f"  Frames generated: {len(result.frames)}")
    print(f"  Final probability: {result.probabilities[-1]:.6f}")
    if result.transmission is not None:
        print(f"  Transmission: T = {result.transmission:.4f}")
        print(f"  Reflection: R = {result.reflection:.4f}")
except Exception as e:
    print(f"❌ Simulation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Save output
print("\nTest 4: Saving output...")
try:
    result.save_animation()
    result.plot_probability_evolution("test_probability.png")
    print("✓ Output saved successfully")
except Exception as e:
    print(f"❌ Failed to save output: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("ALL TESTS PASSED ✓")
print("="*70)
print(f"\nGenerated files:")
print(f"  - {config.output.filename}")
print(f"  - test_probability.png")
print("\nThe simulation platform is working correctly!")
print("="*70 + "\n")
