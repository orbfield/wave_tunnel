# Quantum Tunneling Simulation Platform - Architecture

## Overview

This project is being transformed from a single-purpose simulation script into a **comprehensive quantum tunneling simulation platform** for research and education.

## ✅ Completed Components

### 1. Barrier Models (`wave_tunnel/barrier_models.py`)

Implemented physically realistic barrier models:

- **RectangularBarrier**: Textbook quantum tunneling (analytically solvable)
  - Use for: STM, vacuum gaps, theoretical studies
  - Features: Exact transmission coefficient calculation

- **EckartBarrier**: Smooth molecular potentials (Eckart 1930)
  - Use for: Molecular scattering, chemical reactions
  - Features: C^∞ smooth, exponential tails, physically realistic

- **WoodsSaxonBarrier**: Nuclear/surface potentials
  - Use for: Nuclear physics, material surfaces
  - Features: Flat-top with smooth surface transitions

- **AsymmetricBarrier**: Material interfaces
  - Use for: Heterostructures, band offsets
  - Features: Different potentials on each side

- **DoubleBarrier**: Resonant tunneling structures
  - Use for: RTDs, quantum wells
  - Features: Resonant transmission peaks

- **Current Implementation**: Double-sigmoid barrier
  - Use for: Tunnel junctions, oxide layers
  - Features: Two interfaces with bulk region

### 2. Configuration System (`wave_tunnel/config.py`)

Complete hierarchical configuration using dataclasses:

```python
SimulationConfig
├── SpatialConfig        # Grid, domain
├── TimeConfig           # Evolution, timestep
├── WavePacketConfig     # Initial wavefunction
├── BarrierConfig        # Potential barrier
├── BoundaryConfig       # Boundary conditions
├── VisualizationConfig  # Rendering
├── DiagnosticsConfig    # Physics checks
└── OutputConfig         # File output
```

**Features**:
- Automatic validation
- Physics checks (resolution, energy vs barrier)
- Auto-calculation of dependent parameters
- JSON import/export for reproducibility
- Backward compatibility

### 3. Physical Presets (`wave_tunnel/presets.py`)

Seven scientifically accurate scenarios:

1. **STM Vacuum Tunneling** - Scanning tunneling microscope
2. **Alpha Decay** - Gamow's quantum tunneling model
3. **Resonant Tunneling Diode** - Double barrier quantum well
4. **Tunnel Junction** - Oxide barrier (current implementation)
5. **Molecular Scattering** - Eckart barrier
6. **Semiconductor Heterojunction** - Band offset
7. **Textbook Rectangular** - Teaching and validation

Each preset includes:
- Physically realistic parameters
- Appropriate barrier model
- Literature references
- Diagnostic settings

### 4. CLI Interface (`wave_tunnel/cli.py`)

Professional command-line interface:

```bash
# Run preset
python -m wave_tunnel.cli --preset stm

# Interactive mode
python -m wave_tunnel.cli --interactive

# Custom parameters
python -m wave_tunnel.cli --preset textbook --V0 250 --momentum 20

# Export configuration
python -m wave_tunnel.cli --export-config my_config.json

# Load from file
python -m wave_tunnel.cli --config my_config.json
```

**Features**:
- Preset selection
- Interactive wizard
- Parameter overrides
- Configuration file support
- Help system

### 5. Analysis Tools

- `analyze_barrier.py` - Barrier structure analysis
- `compare_barriers.py` - Compare different models
- Visualization of transition regions

## 🚧 Components to Implement

### Priority 1: Core Simulation Engine

**File**: `wave_tunnel/simulator.py`

Refactor main simulation to use new architecture:

```python
def run_simulation(config: SimulationConfig) -> SimulationResult:
    """
    Main simulation engine.

    1. Initialize from config
    2. Create barrier from config.barrier
    3. Setup boundary conditions
    4. Run evolution loop
    5. Collect diagnostics
    6. Generate visualization
    7. Export data
    8. Return results
    """
```

**Status**: To be implemented
**Effort**: Medium (refactor existing code)
**Dependencies**: None

---

### Priority 2: Physics Diagnostics Module

**File**: `wave_tunnel/diagnostics.py`

Implement physics measurements:

- ✓ Norm conservation check
- ✓ Energy conservation check
- ✓ Transmission coefficient calculation
- ✓ Reflection coefficient calculation
- ✓ Compare with analytical results (where available)
- ✓ Phase analysis
- ✓ Probability flux

**Status**: Partially designed
**Effort**: Medium
**Dependencies**: Core engine

---

### Priority 3: True PML Implementation

**File**: `wave_tunnel/boundaries/pml.py`

Implement proper Perfectly Matched Layer using complex coordinate stretching:

```python
# Current: Absorbing boundary layer (imaginary potential)
# Target: True PML (complex coordinate transformation)

def create_pml_complex_coordinate(x, pml_params):
    """
    Implement complex coordinate stretching:
    x → x + i ∫σ(x')dx'

    This gives perfectly reflection-less boundaries.
    """
```

**Status**: Research needed
**Effort**: High (requires complex FFT)
**Dependencies**: None
**References**:
- Berenger, J. Comp. Phys. 114, 185 (1994)
- Johnson, arXiv:2108.05348 (PML for quantum mechanics)

---

### Priority 4: Time Step Calculation

**File**: `wave_tunnel/time_stepping.py`

Fix and sophisticate time step calculation:

```python
def calculate_optimal_timestep(spatial_grid, potential, wave_packet,
                                safety_factor=0.2):
    """
    Calculate optimal time step including:
    - Kinetic energy (FFT wavenumbers)
    - Potential energy (barrier height)
    - CFL-like stability condition
    - Accuracy requirements for split-operator method

    Returns dt with physics-based justification.
    """
```

**Current issue**: Uses only kinetic energy, ignores V₀
**Status**: Design complete, needs implementation
**Effort**: Low

---

### Priority 5: Data Export

**File**: `wave_tunnel/io/export.py`

Export data for analysis:

- Wavefunction at all time steps (HDF5)
- Probability density evolution (CSV)
- Diagnostic results (JSON)
- Transmission/reflection vs energy (for parameter scans)

**Status**: To be designed
**Effort**: Low
**Dependencies**: Core engine

---

### Priority 6: Real Experimental Data

**File**: `wave_tunnel/data/`

Add real experimental data for comparison:

- STM tunneling spectra
- RTD I-V curves
- Alpha decay half-lives
- Compare simulation with experiment

**Status**: Research needed
**Effort**: Medium (data collection + fitting)
**Dependencies**: Diagnostics

---

### Priority 7: Web/GUI Interface (Future)

**File**: `wave_tunnel/app/web.py`

Interactive visualization using:
- Flask/FastAPI backend
- Three.js or D3.js frontend
- Real-time parameter adjustment
- Side-by-side comparison

**Status**: Future enhancement
**Effort**: High
**Dependencies**: All above

---

## Code Organization

Current structure:
```
wave_tunnel/
├── wave_tunnel/
│   ├── barrier_models.py    ✅ Complete
│   ├── config.py            ✅ Complete
│   ├── presets.py           ✅ Complete
│   ├── cli.py               ✅ Complete
│   ├── main.py              ⚠️  Legacy (needs refactoring)
│   ├── evolution.py         ⚠️  Legacy (needs integration)
│   ├── pml.py               ⚠️  Absorbing layer (not true PML)
│   ├── potentials.py        ⚠️  Superseded by barrier_models.py
│   ├── visualization.py     ⚠️  Needs integration
│   ├── wavefunctions.py     ⚠️  Needs integration
│   └── utils.py             ✅ OK
├── analyze_barrier.py       ✅ Analysis tool
├── compare_barriers.py      ✅ Analysis tool
└── requirements.txt         ⚠️  Needs update
```

Target structure:
```
wave_tunnel/
├── wave_tunnel/
│   ├── core/                # Core physics
│   │   ├── evolution.py
│   │   ├── wavefunctions.py
│   │   ├── time_stepping.py     # NEW
│   │   └── diagnostics.py       # NEW
│   ├── barriers/            # Barrier models
│   │   └── models.py        ✅
│   ├── boundaries/          # Boundary conditions
│   │   ├── absorbing.py     # Refactored from pml.py
│   │   └── pml.py           # NEW: True PML
│   ├── config/              # Configuration
│   │   ├── parameters.py    ✅ (config.py)
│   │   └── presets.py       ✅
│   ├── io/                  # Input/output
│   │   ├── export.py        # NEW
│   │   └── visualization.py
│   ├── data/                # Experimental data
│   │   └── ...              # NEW
│   ├── app/                 # User interfaces
│   │   ├── cli.py           ✅
│   │   └── web.py           # Future
│   ├── simulator.py         # NEW: Main engine
│   └── utils/
├── examples/                # Example notebooks/scripts
├── tests/                   # Unit tests
├── docs/                    # Documentation
└── tools/                   # Analysis scripts
    ├── analyze_barrier.py
    └── compare_barriers.py
```

## Next Steps

### Immediate (This Session)

1. **Create main simulator** (`simulator.py`)
   - Integrate configuration system
   - Use barrier models
   - Call existing evolution code
   - Generate output

2. **Fix time step calculation**
   - Include V₀ in calculation
   - Document physics

3. **Basic diagnostics**
   - Norm conservation
   - Transmission coefficient

4. **Test with one preset**
   - Validate end-to-end
   - Debug integration

### Near Term

5. Implement true PML
6. Add all diagnostics
7. Data export
8. Test all presets
9. Documentation
10. Unit tests

### Future

11. Real experimental data
12. Web interface
13. Parameter optimization
14. Machine learning integration

## Physics Priorities Summary

Based on earlier analysis, the critical physics improvements are:

1. ✅ **Barrier models** - DONE (all 6 types implemented)
2. ✅ **Configuration system** - DONE
3. 🚧 **Time step calculation** - HIGH PRIORITY (currently incorrect)
4. 🚧 **PML implementation** - MEDIUM (current is absorbing layer, not PML)
5. 🚧 **Physics validation** - HIGH (need transmission coefficients)
6. 🚧 **Unit system documentation** - HIGH (ℏ=1, m=1 undocumented)

## Design Philosophy

1. **Modularity**: Each component is self-contained and testable
2. **Physics first**: Prioritize physical correctness over performance
3. **Reproducibility**: All simulations fully configurable and saveable
4. **Education**: Clear documentation with physics explanations
5. **Research ready**: Export data, compare with theory/experiment
6. **User friendly**: CLI, presets, validation, helpful errors

## Usage Examples

Once complete, users will be able to:

```bash
# Quick start with preset
python -m wave_tunnel.cli --preset stm --output stm_result.gif

# Custom simulation
python -m wave_tunnel.cli --barrier-type rectangular --V0 200 --width 10 \
    --momentum 18 --export-data

# Interactive exploration
python -m wave_tunnel.cli --interactive

# Batch processing
for preset in stm alpha_decay rtd molecular; do
    python -m wave_tunnel.cli --preset $preset
done

# Research workflow
python -m wave_tunnel.cli --config experiment.json --export-data
python analyze_transmission.py results.h5
```

## References

### Quantum Mechanics
- Griffiths, "Introduction to Quantum Mechanics" (3rd ed.)
- Cohen-Tannoudji et al., "Quantum Mechanics"
- Landau & Lifshitz, "Quantum Mechanics"

### Numerical Methods
- Press et al., "Numerical Recipes"
- Tannor, "Introduction to Quantum Mechanics: A Time-Dependent Perspective"

### PML
- Berenger, J. Comp. Phys. 114, 185 (1994)
- Johnson, arXiv:2108.05348 (2021)

### Experimental
- Binning & Rohrer, Surf. Sci. 126, 236 (1983) - STM
- Esaki & Tsu, IBM J. 14, 61 (1970) - RTD
- Gamow, Z. Phys. 51, 204 (1928) - Alpha decay

---

**Status**: Framework complete, ready for integration
**Next**: Implement `simulator.py` to tie everything together
