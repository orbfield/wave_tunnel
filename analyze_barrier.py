#!/usr/bin/env python3
"""Analyze the current barrier structure to identify the double-barrier issue."""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def smooth_step(x, edge, width):
    """Current sigmoid transition."""
    z = (x - edge) / width
    return 1 / (1 + np.exp(-z))

def current_barrier(x, barrier_center=0.0, V0=20.0, barrier_width=1.0, transition_width=0.05):
    """Current implementation - creates double barrier."""
    V = np.zeros_like(x)
    barrier_start = barrier_center - barrier_width / 2
    barrier_end = barrier_center + barrier_width / 2

    V += V0 * (smooth_step(x, barrier_start, transition_width) -
               smooth_step(x, barrier_end, transition_width))
    return V

# Create detailed view
x = np.linspace(-5, 5, 2000)

# Current parameters from main.py
barrier_width = 15.0
V0 = 320.0
transition_width = 0.05

V_current = current_barrier(x, barrier_center=0, V0=V0,
                            barrier_width=barrier_width,
                            transition_width=transition_width)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Full view
ax = axes[0]
ax.plot(x, V_current, 'b-', linewidth=2, label='Current barrier')
ax.axhline(V0, color='r', linestyle='--', alpha=0.5, label=f'V₀ = {V0}')
ax.axhline(0, color='k', linestyle='-', alpha=0.3)
ax.axvline(-barrier_width/2, color='orange', linestyle='--', alpha=0.5, label='Barrier edges')
ax.axvline(+barrier_width/2, color='orange', linestyle='--', alpha=0.5)
ax.set_xlabel('Position x', fontsize=12)
ax.set_ylabel('Potential V(x)', fontsize=12)
ax.set_title('Current Barrier Structure - Full View', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

# Zoomed view on transition
ax = axes[1]
x_zoom = np.linspace(-barrier_width/2 - 0.5, -barrier_width/2 + 0.5, 1000)
V_zoom = current_barrier(x_zoom, barrier_center=0, V0=V0,
                         barrier_width=barrier_width,
                         transition_width=transition_width)

ax.plot(x_zoom, V_zoom, 'b-', linewidth=2, label='Left transition')
ax.axvline(-barrier_width/2, color='orange', linestyle='--', alpha=0.5, label='Nominal edge')
ax.axhline(V0, color='r', linestyle='--', alpha=0.5)
ax.axhline(0, color='k', linestyle='-', alpha=0.3)

# Mark 10-90% rise points
V_10 = 0.1 * V0
V_90 = 0.9 * V0
idx_10 = np.argmin(np.abs(V_zoom - V_10))
idx_90 = np.argmin(np.abs(V_zoom - V_90))
transition_distance = x_zoom[idx_90] - x_zoom[idx_10]

ax.plot([x_zoom[idx_10], x_zoom[idx_90]], [V_10, V_90], 'ro-', markersize=8,
        label=f'10-90% rise: {transition_distance:.4f} units')

ax.set_xlabel('Position x', fontsize=12)
ax.set_ylabel('Potential V(x)', fontsize=12)
ax.set_title(f'Transition Region (width parameter = {transition_width})', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig('/home/user/wave_tunnel/barrier_analysis.png', dpi=150, bbox_inches='tight')
print("Saved barrier analysis to barrier_analysis.png")

# Analyze the structure
print("\n" + "="*70)
print("BARRIER STRUCTURE ANALYSIS")
print("="*70)
print(f"\nBarrier width: {barrier_width} units")
print(f"Transition width parameter: {transition_width}")
print(f"10-90% transition distance: {transition_distance:.6f} units")
print(f"Ratio: {transition_distance/barrier_width:.2%} of barrier width")

print(f"\nPotential values:")
print(f"  Far from barrier: V = {V_current[0]:.6f}")
print(f"  Center of barrier: V = {V_current[len(V_current)//2]:.6f}")
print(f"  Expected V₀: {V0}")

print("\n" + "="*70)
print("THE DOUBLE-BARRIER PROBLEM")
print("="*70)
print("""
Current structure creates TWO distinct transitions:

1. LEFT TRANSITION (rising):  0 → V₀  at x ≈ -7.5
2. MIDDLE REGION (flat):      V = V₀  for |x| < 7.5
3. RIGHT TRANSITION (falling): V₀ → 0  at x ≈ +7.5

This is physically like:
  - Entering a potential well/barrier (left interface)
  - Propagating through constant potential (bulk material)
  - Exiting the barrier (right interface)

For a SOLID BARRIER in reality:
  - Thin barriers (like STM vacuum gap): nearly rectangular, abrupt transitions
  - Material interfaces: sharp on atomic scale (~angstroms)
  - The "transition width" should be << barrier_width

Physical interpretation:
  - Current model: Two separate interfaces with bulk material between
  - Realistic tunneling: Usually rectangular barrier or single interface
""")

print("\n" + "="*70)
print("WHAT DOES 'SOLID BARRIER' MEAN PHYSICALLY?")
print("="*70)
print("""
Different physical scenarios:

1. RECTANGULAR BARRIER (textbook model):
   - Step function: V=0 for |x|>L/2, V=V₀ for |x|<L/2
   - Models: STM vacuum gap, thin insulating layer
   - Transition width → 0 (instantaneous)

2. FINITE INTERFACE WIDTH (realistic):
   - Atomic-scale smoothing (~angstroms = 10⁻¹⁰ m)
   - In simulation units: transition_width ~ 0.001 - 0.01
   - Still much sharper than current 0.05

3. ECKART BARRIER (smooth, realistic):
   - V(x) = V₀/cosh²(x/a)
   - Models molecular potentials, scattering problems
   - Physically motivated smooth function

4. WOODS-SAXON POTENTIAL (nuclear physics):
   - V(x) = V₀/(1 + exp((|x|-R)/a))
   - Models nuclear surface, has finite thickness

Current implementation is actually closest to #4 (Woods-Saxon),
but with TWO interfaces creating a well/barrier region.
""")

print("\nRecommendation: Implement multiple barrier models and let user choose")
