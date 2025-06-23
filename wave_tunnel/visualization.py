# visualization.py

import numpy as np
import pandas as pd
import dask.dataframe as dd
import datashader as ds
import datashader.transfer_functions as tf

def create_datashader_frame(wave_function, x, vis_settings, barrier_center=0.0, barrier_width=1.0):
    """
    Create a visualization frame showing the probability density and stationary potential barrier.
    """
    # Calculate wave function components
    psi_real = np.real(wave_function)
    psi_imag = np.imag(wave_function)
    prob_density = np.abs(wave_function)**2

    # Normalize components for visualization
    max_density = np.max(prob_density)
    eps = 1e-10  # Prevent division by zero
    normalized_density = prob_density / (max_density + eps)

    # Apply gentle smoothing to probability density
    window_size = 10
    kernel = np.ones(window_size) / window_size
    smoothed_density = np.convolve(normalized_density, kernel, mode='same')

    # Adaptive scaling for probability density
    base_scale = 0.7
    scale_factor = base_scale

    # Prepare DataFrames for datashader
    df_wave = pd.DataFrame({
        'x': x,
        'psi_real': psi_real,
        'psi_imag': psi_imag,
        'psi_abs': scale_factor * smoothed_density
    })

    # Barrier visualization as two vertical lines
    barrier_x_left = [barrier_center - barrier_width / 2, barrier_center - barrier_width / 2]
    barrier_y_left = [-1, 1]
    df_barrier_left = pd.DataFrame({
        'x': barrier_x_left,
        'y': barrier_y_left
    })

    barrier_x_right = [barrier_center + barrier_width / 2, barrier_center + barrier_width / 2]
    barrier_y_right = [-1, 1]
    df_barrier_right = pd.DataFrame({
        'x': barrier_x_right,
        'y': barrier_y_right
    })

    # Canvas settings
    cvs = ds.Canvas(plot_width=vis_settings['width'],
                    plot_height=vis_settings['height'],
                    x_range=(x.min(), x.max()),
                    y_range=(-1, 1))

    # Convert to dask dataframes
    ddf_wave = dd.from_pandas(df_wave, npartitions=8)
    ddf_barrier_left = dd.from_pandas(df_barrier_left, npartitions=1)
    ddf_barrier_right = dd.from_pandas(df_barrier_right, npartitions=1)

    # Aggregate wavefunction components
    agg_real = cvs.line(ddf_wave, 'x', 'psi_real')
    agg_imag = cvs.line(ddf_wave, 'x', 'psi_imag')
    agg_abs = cvs.line(ddf_wave, 'x', 'psi_abs')
    agg_barrier_left = cvs.line(ddf_barrier_left, 'x', 'y')
    agg_barrier_right = cvs.line(ddf_barrier_right, 'x', 'y')

    # Shade components with distinct color maps
    img_real = tf.shade(agg_real, cmap=['red'], how='linear')
    img_imag = tf.shade(agg_imag, cmap=['blue'], how='linear')
    img_abs = tf.shade(agg_abs, cmap=['grey'], how='linear')
    img_barrier_left = tf.shade(agg_barrier_left, cmap=['orange'], how='linear')
    img_barrier_right = tf.shade(agg_barrier_right, cmap=['orange'], how='linear')

    # Combine all components
    img = tf.stack(img_real, img_imag, img_abs, img_barrier_left, img_barrier_right)
    img = tf.set_background(img, 'black')

    return img.to_pil()
