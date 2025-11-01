#!/usr/bin/env python3
"""
Compare different barrier models to understand their physical properties.
"""

import sys
sys.path.insert(0, '/home/user/wave_tunnel')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wave_tunnel.barrier_models import (
    RectangularBarrier, EckartBarrier, WoodsSaxonBarrier,
    AsymmetricBarrier, DoubleBarrier
)

# Common parameters
V0 = 320.0
width = 15.0
center = 0.0

# Create spatial grid
x = np.linspace(-30, 30, 3000)

# Current implementation (for comparison)
def current_barrier(x, V0, width, center, transition_width=0.05):
    """Current double-sigmoid implementation."""
    def smooth_step(x, edge, w):
        z = (x - edge) / w
        return 1 / (1 + np.exp(-z))

    barrier_start = center - width / 2
    barrier_end = center + width / 2
    return V0 * (smooth_step(x, barrier_start, transition_width) -
                 smooth_step(x, barrier_end, transition_width))

# Create barriers
barriers = {
    'Current (double sigmoid)': current_barrier(x, V0, width, center, 0.05),
    'Rectangular (textbook)': RectangularBarrier(V0, width, center, smoothing=0.05)(x),
    'Eckart (molecular)': EckartBarrier(V0, width=5, center=center)(x),
    'Woods-Saxon (nuclear)': WoodsSaxonBarrier(V0, radius=width/2,
                                               surface_thickness=0.5,
                                               center=center)(x),
}

# Create figure with multiple subplots
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)

# Plot 1: Overview of all barriers
ax1 = fig.add_subplot(gs[0, :])
colors = ['blue', 'red', 'green', 'purple']
for (name, V), color in zip(barriers.items(), colors):
    ax1.plot(x, V, label=name, linewidth=2, alpha=0.8, color=color)

ax1.axhline(V0, color='k', linestyle='--', alpha=0.3, label=f'V₀ = {V0}')
ax1.axhline(0, color='k', linestyle='-', alpha=0.2)
ax1.axvline(center - width/2, color='orange', linestyle=':', alpha=0.5,
            label='Nominal edges')
ax1.axvline(center + width/2, color='orange', linestyle=':', alpha=0.5)

# Add energy line for tunneling reference
E_kin = 315.8  # From n=4, m=2, kappa=8π
ax1.axhline(E_kin, color='cyan', linestyle='--', alpha=0.6,
            label=f'Wave packet energy E ≈ {E_kin:.1f}')

ax1.set_xlabel('Position x', fontsize=12)
ax1.set_ylabel('Potential V(x)', fontsize=12)
ax1.set_title('Comparison of Barrier Models', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-20, 350)

# Plot 2: Zoom on left transition
ax2 = fig.add_subplot(gs[1, 0])
x_zoom = np.linspace(-10, -5, 1000)
for (name, _), color in zip(barriers.items(), colors):
    if 'Current' in name:
        V_zoom = current_barrier(x_zoom, V0, width, center, 0.05)
    elif 'Rectangular' in name:
        V_zoom = RectangularBarrier(V0, width, center, smoothing=0.05)(x_zoom)
    elif 'Eckart' in name:
        V_zoom = EckartBarrier(V0, width=5, center=center)(x_zoom)
    elif 'Woods' in name:
        V_zoom = WoodsSaxonBarrier(V0, radius=width/2,
                                   surface_thickness=0.5, center=center)(x_zoom)
    ax2.plot(x_zoom, V_zoom, label=name, linewidth=2, alpha=0.8, color=color)

ax2.axvline(center - width/2, color='orange', linestyle='--', alpha=0.5)
ax2.axhline(V0/2, color='k', linestyle=':', alpha=0.3, label='V₀/2')
ax2.set_xlabel('Position x', fontsize=11)
ax2.set_ylabel('Potential V(x)', fontsize=11)
ax2.set_title('Left Transition Region (zoomed)', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# Plot 3: Central region
ax3 = fig.add_subplot(gs[1, 1])
x_center = np.linspace(-2, 2, 1000)
for (name, _), color in zip(barriers.items(), colors):
    if 'Current' in name:
        V_center = current_barrier(x_center, V0, width, center, 0.05)
    elif 'Rectangular' in name:
        V_center = RectangularBarrier(V0, width, center, smoothing=0.05)(x_center)
    elif 'Eckart' in name:
        V_center = EckartBarrier(V0, width=5, center=center)(x_center)
    elif 'Woods' in name:
        V_center = WoodsSaxonBarrier(V0, radius=width/2,
                                     surface_thickness=0.5, center=center)(x_center)
    ax3.plot(x_center, V_center, label=name, linewidth=2, alpha=0.8, color=color)

ax3.axhline(V0, color='r', linestyle='--', alpha=0.5)
ax3.set_xlabel('Position x', fontsize=11)
ax3.set_ylabel('Potential V(x)', fontsize=11)
ax3.set_title('Central Barrier Region', fontsize=12, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# Plot 4: Physical interpretation text
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

interpretation = """
PHYSICAL INTERPRETATION OF BARRIER MODELS:

1. CURRENT (Double Sigmoid) - Two separate interfaces:
   • Models: Insulating layer between conductors, oxide barrier, tunnel junction
   • Physics: Wave enters barrier (left interface) → propagates through constant V₀ → exits barrier (right interface)
   • Quantum: Two separate scattering events with bulk propagation between
   • Use for: Material layers, interfaces, realistic devices with finite thickness

2. RECTANGULAR - Canonical quantum tunneling:
   • Models: Idealized thin barrier, STM vacuum gap, textbook problems
   • Physics: Abrupt potential change, pure tunneling through forbidden region
   • Quantum: Single coherent tunneling event, analytically solvable
   • Use for: Theoretical studies, comparison with textbook results, thin barriers

3. ECKART - Smooth molecular barrier:
   • Models: Molecular potentials, chemical reactions, atomic scattering
   • Physics: Smooth potential hill with exponential tails, no discontinuities
   • Quantum: Natural barrier for molecules, all derivatives exist (C^∞ smooth)
   • Use for: Molecular systems, smooth scattering, physically realistic smooth barriers

4. WOODS-SAXON - Finite surface thickness:
   • Models: Nuclear potentials, material surfaces with diffuse interfaces
   • Physics: Flat potential inside with smooth surface transition over finite width
   • Quantum: Combines flat-top (like rectangular) with realistic smooth transitions
   • Use for: Nuclear physics, thick barriers with realistic surfaces

WHICH MODEL FOR YOUR SIMULATION?

Question: What physical scenario are you modeling?

A) Thin vacuum gap (STM, field emission)          → Use RECTANGULAR
B) Thin oxide/insulator layer                     → Use CURRENT (what you have)
C) Molecular barrier (chemical reaction)          → Use ECKART
D) Thick material with smooth interfaces          → Use WOODS-SAXON
E) Single material interface (metal-semiconductor) → Use ASYMMETRIC

Current model is actually CORRECT for scenario B (thin insulating layer)!
The "double barrier" is physically appropriate for a finite-thickness material.

The key question: What is your barrier meant to represent physically?
"""

ax4.text(0.02, 0.98, interpretation, transform=ax4.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.savefig('/home/user/wave_tunnel/barrier_comparison.png', dpi=150,
            bbox_inches='tight')
print("Saved comparison to barrier_comparison.png")

# Print numerical comparison
print("\n" + "="*70)
print("NUMERICAL COMPARISON")
print("="*70)

# Find center values
idx_center = np.argmin(np.abs(x))
print(f"\nPotential at barrier center (x=0):")
for name, V in barriers.items():
    print(f"  {name:30s}: V(0) = {V[idx_center]:.4f}")

# Find transition widths (10-90% rise)
print(f"\n10-90% Transition widths:")
for name, V in barriers.items():
    # Find left transition
    mask_left = (x > -15) & (x < 0)
    if np.any(mask_left):
        V_left = V[mask_left]
        x_left = x[mask_left]

        V_min = np.min(V_left)
        V_max = np.max(V_left)

        if V_max - V_min > 10:  # Significant transition
            V_10 = V_min + 0.1 * (V_max - V_min)
            V_90 = V_min + 0.9 * (V_max - V_min)

            idx_10 = np.argmin(np.abs(V_left - V_10))
            idx_90 = np.argmin(np.abs(V_left - V_90))

            width_trans = x_left[idx_90] - x_left[idx_10]
            print(f"  {name:30s}: {width_trans:.4f} units ({100*width_trans/15:.2f}% of barrier)")

print("\n" + "="*70)
