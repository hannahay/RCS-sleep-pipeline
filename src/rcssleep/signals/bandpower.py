"""
Frequency band power calculation functions for RCS sleep pipeline.

Provides functions for calculating power spectral density (PSD) and band power
using Welch's method.
"""

import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


def calculate_band_power_from_psd(psd, freqs, fmin, fmax):
    """
    Calculate power in a frequency band by integrating PSD over the frequency range.
    
    Args:
        psd (np.array): Power spectral density values
        freqs (np.array): Frequency values corresponding to PSD
        fmin (float): Minimum frequency in Hz
        fmax (float): Maximum frequency in Hz
        
    Returns:
        tuple: (band_power_linear, band_power_db)
            - band_power_linear: Power in the specified frequency band (in linear units)
            - band_power_db: Power in the specified frequency band (in dB)
    """
    # Find frequency indices within the band
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    
    # Convert PSD (power per Hz) to power spectrum (power)
    # Calculate frequency resolution (bin width)
    if len(freqs) > 1:
        df = freqs[1] - freqs[0]  # Frequency resolution (bin width)
    else:
        df = 1.0  # Fallback if only one frequency point
    
    # Convert PSD to power spectrum: power_spectrum = PSD * df
    power_spectrum = psd * df
    
    # Integrate (sum) power spectrum values in the band
    band_power_linear = np.sum(power_spectrum[freq_mask])
    
    # Convert to dB: 10 * log10(power)
    # Handle zero or very small values to avoid log(0) or negative infinity
    if band_power_linear > 0:
        band_power_db = 10 * np.log10(band_power_linear)
    else:
        # If power is zero or negative, return -infinity or a very small dB value
        band_power_db = -np.inf
    
    return band_power_linear, band_power_db


def calculate_psd_per_epoch(data, state_data, fs, epoch_sec=3.0, target_state=None, 
                            nperseg=None, noverlap=None):
    """
    Calculate PSD for each epoch using Welch's method.
    Epochs containing state transitions are discarded.
    If target_state is specified, only epochs belonging to that state are processed.
    
    Args:
        data (np.array): Time series data
        state_data (np.array): State values corresponding to data (can be numeric or string)
        fs (float): Sampling frequency in Hz
        epoch_sec (float): Length of each epoch in seconds (default: 3.0 sec)
        target_state (optional): If specified, only process epochs belonging to this state
        nperseg (optional): Length of each segment for Welch's method. If None, uses epoch_sec * fs
        noverlap (optional): Number of points to overlap between segments. If None, uses 50% overlap
        
    Returns:
        tuple: (frequencies, list of PSD arrays for each valid epoch)
    """
    epoch_samples = int(epoch_sec * fs)  # Epoch size in samples
    
    if nperseg is None:
        nperseg = epoch_samples  # Window size = epoch size
    if noverlap is None:
        noverlap = nperseg // 2  # 50% overlap
    
    if len(data) < epoch_samples:
        return None, []
    
    # Divide data into non-overlapping epochs
    n_epochs = len(data) // epoch_samples
    psd_list = []
    valid_epoch_indices = []
    
    for i in range(n_epochs):
        epoch_start = i * epoch_samples
        epoch_end = epoch_start + epoch_samples
        
        # Extract epoch data and states
        epoch_data = data[epoch_start:epoch_end]
        epoch_states = state_data[epoch_start:epoch_end]
        
        # Check if epoch contains a state transition (discard if it does)
        unique_states = np.unique(epoch_states)
        if len(unique_states) > 1:
            # Epoch contains state transition - discard
            continue
        
        # If target_state is specified, only process epochs belonging to that state
        if target_state is not None:
            if len(unique_states) == 0 or unique_states[0] != target_state:
                # Epoch does not belong to target state - skip
                continue
        
        # Check for NaN values
        if np.any(np.isnan(epoch_data)):
            continue
        
        # Calculate PSD for this epoch using Welch's method
        try:
            freqs, psd_epoch = signal.welch(
                epoch_data, 
                fs=fs, 
                nperseg=nperseg,
                noverlap=noverlap,
                window='hann'
            )
            psd_list.append(psd_epoch)
            valid_epoch_indices.append(i)
        except Exception as e:
            logger.warning(f"Error calculating PSD for epoch {i}: {e}")
            continue
    
    if len(psd_list) == 0:
        return None, []
    
    # Return frequencies (same for all epochs) and list of PSD arrays
    # Calculate frequencies once (they're the same for all epochs)
    _, freqs = signal.welch(
        np.zeros(epoch_samples),  # Dummy data just to get frequency array
        fs=fs,
        nperseg=nperseg,
        noverlap=noverlap,
        window='hann'
    )
    
    return freqs, psd_list


def calculate_welch_psd(data, fs, nperseg=None, noverlap=None, window='hann'):
    """
    Calculate power spectral density using Welch's method.
    
    Args:
        data (np.array): Time series data
        fs (float): Sampling frequency in Hz
        nperseg (int, optional): Length of each segment. If None, uses min(256, len(data))
        noverlap (int, optional): Number of points to overlap. If None, uses 50% overlap
        window (str or tuple): Window function (default: 'hann')
        
    Returns:
        tuple: (frequencies, PSD values)
    """
    if nperseg is None:
        nperseg = min(256, len(data) // 4)
    if noverlap is None:
        noverlap = nperseg // 2
    
    freqs, psd = signal.welch(
        data,
        fs=fs,
        nperseg=nperseg,
        noverlap=noverlap,
        window=window
    )
    
    return freqs, psd


def calculate_band_power(data, fs, fmin, fmax, nperseg=None, noverlap=None):
    """
    Calculate power in a frequency band directly from time series data.
    
    This is a convenience function that calculates PSD and then integrates over the band.
    
    Args:
        data (np.array): Time series data
        fs (float): Sampling frequency in Hz
        fmin (float): Minimum frequency in Hz
        fmax (float): Maximum frequency in Hz
        nperseg (int, optional): Length of each segment for Welch's method
        noverlap (int, optional): Number of points to overlap
        
    Returns:
        tuple: (band_power_linear, band_power_db)
    """
    freqs, psd = calculate_welch_psd(data, fs, nperseg=nperseg, noverlap=noverlap)
    return calculate_band_power_from_psd(psd, freqs, fmin, fmax)

