# main.py

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from wavefunctions import initialize_wavefunction_custom
from potentials import create_total_potential_with_pml
from evolution import evolve_wavefunction
from visualization import create_datashader_frame
from utils import compute_total_probability
from pml import get_pml_parameters

def create_tunneling_animation_with_stationary_barrier_custom(
    output_filename='quantum_tunneling_with_stationary_barrier_custom.gif',
    num_frames=120,
    spatial_points=2000,
    spatial_range=(-100, 100),
    total_time=6.0,
    barrier_width=1.0,
    V0=20.0,
    transition_width=0.05,
    vis_settings={'width': 2000, 'height': 1000},
    n=1,
    x0=-100.0,
    barrier_center_init=0.0,
    use_pml=True
):
    """
    Create an animation of a wave packet tunneling through a stationary potential barrier.
    Now includes PML boundary conditions.
    """
    # Create spatial grid
    x = np.linspace(spatial_range[0], spatial_range[1], spatial_points)
    dx = x[1] - x[0]

    # Initialize wavefunction
    psi = initialize_wavefunction_custom(x, n, x0)

    # Setup PML parameters
    pml_params = None
    if use_pml:
        pml_params = get_pml_parameters(spatial_range)
        print(f"PML parameters: {pml_params}")

    # Define total potential with PML
    V_total, W_pml = create_total_potential_with_pml(
        x, barrier_center_init, V0, barrier_width, transition_width, pml_params
    )

    # Time step calculation
    max_k = np.max(np.abs(2 * np.pi * np.fft.fftfreq(spatial_points, d=dx)))
    dt = 0.05 / (max_k**2 / 2)

    # Time steps
    num_time_steps = int(total_time / dt) + 1
    times = np.linspace(0, total_time, num_time_steps)

    # Frames to capture
    frame_indices = np.linspace(0, num_time_steps - 1, num_frames).astype(int)

    frames = []
    probabilities = []

    pml_status = "with PML" if use_pml else "without PML"
    print(f"Generating frames with numerical evolution and stationary barrier {pml_status}...")
    for i in tqdm(range(num_time_steps)):
        psi = evolve_wavefunction(psi, x, dt, V_total, W_pml)
        total_prob = compute_total_probability(psi, dx)
        probabilities.append(total_prob)

        if i in frame_indices:
            img = create_datashader_frame(
                psi, x, vis_settings,
                barrier_center=barrier_center_init,
                barrier_width=barrier_width
            )
            frames.append(img)

    # Plot total probability over time
    plt.figure(figsize=(10, 6))
    plt.plot(times, probabilities)
    plt.xlabel('Time')
    plt.ylabel('Total Probability')
    plt.title(f'Total Probability Over Time with Stationary Barrier ({pml_status})')
    plt.grid(True)
    plt.savefig("probability_over_time_with_stationary_barrier_custom.png")
    plt.close()

    if not frames:
        print("No frames were generated. Please check the simulation parameters.")
        return

    # Save the animation
    print(f"Saving animation to {output_filename}...")
    frames[0].save(
        output_filename,
        save_all=True,
        append_images=frames[1:],
        duration=int(total_time / num_frames * 1000),
        loop=0
    )
    print("Animation complete!")
    return output_filename

if __name__ == "__main__":
    n_value = 4  # (n = m^2)
    spatial_range = (-100, 100)
    x0_position = -50.0
    barrier_initial_position = 0
    
    # Fps
    total_time = 15
    fps = 50
    num_frames = int(total_time * fps)
    
    output_file = create_tunneling_animation_with_stationary_barrier_custom(
        output_filename="tunneling.gif",
        num_frames=num_frames,
        spatial_points=2000,
        spatial_range=spatial_range,
        total_time=total_time,
        barrier_width=15.0,
        V0=320.0,
        transition_width=0.05,
        vis_settings={'width': 1280, 'height': 640},
        n=n_value,
        x0=x0_position,
        barrier_center_init=barrier_initial_position,
        use_pml=True
    )
    print(f"Animation saved to: {output_file}")
