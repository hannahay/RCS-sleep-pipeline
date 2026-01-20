"""
Signal filtering functions for RCS sleep pipeline.

Provides functions for notch filtering, bandpass filtering, and artifact removal.
"""

import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


def apply_notch_filter(data, fs, notch_freq=60.0, quality_factor=30.0):
    """
    Apply notch filter to remove specific frequency (e.g., 60 Hz line noise).
    
    Args:
        data: Input signal data
        fs: Sampling rate in Hz
        notch_freq: Frequency to notch out (default: 60 Hz)
        quality_factor: Quality factor for notch filter (default: 30.0)
        
    Returns:
        Filtered data
    """
    b_notch, a_notch = signal.iirnotch(notch_freq, quality_factor, fs)
    data_notched = signal.filtfilt(b_notch, a_notch, data)
    return data_notched


def apply_bandpass_filter(data, fs, low_freq, high_freq, order=4):
    """
    Apply Butterworth bandpass filter to data.
    
    Args:
        data: Input signal data
        fs: Sampling rate in Hz
        low_freq: Low cutoff frequency in Hz
        high_freq: High cutoff frequency in Hz
        order: Filter order (default: 4)
        
    Returns:
        Filtered data
    """
    nyquist = fs / 2.0
    low_norm = low_freq / nyquist
    high_norm = high_freq / nyquist
    
    # Check if frequencies are valid
    if low_norm >= 1.0 or high_norm >= 1.0 or low_norm <= 0 or high_norm <= 0:
        logger.warning(f"Invalid frequency range [{low_freq}, {high_freq}] Hz for fs={fs} Hz. Returning original data.")
        return data
    
    try:
        b, a = signal.butter(order, [low_norm, high_norm], btype='band')
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    except Exception as e:
        logger.warning(f"Error applying bandpass filter: {e}. Returning original data.")
        return data


def apply_bandpass_filter_preserve_nan(data, fs, low_freq, high_freq, order=4):
    """
    Apply bandpass filter to data while preserving NaN positions (no interpolation).
    
    This function filters only the valid (non-NaN) segments and preserves NaN positions
    in the output, which is important for maintaining data integrity when NaN values
    represent missing or invalid data.
    
    Args:
        data: Input signal data (may contain NaN)
        fs: Sampling rate in Hz
        low_freq: Low cutoff frequency in Hz
        high_freq: High cutoff frequency in Hz
        order: Filter order (default: 4)
    
    Returns:
        Filtered data with NaN positions preserved
    """
    # Create output array with same shape, preserving NaN positions
    filtered_data = data.copy()
    
    # Find valid (non-NaN) segments
    nan_mask = np.isnan(data)
    
    if nan_mask.all():
        # All data is NaN, return as is
        return filtered_data
    
    # Get valid data segments
    valid_mask = ~nan_mask
    valid_data = data[valid_mask]
    
    if len(valid_data) == 0:
        return filtered_data
    
    # Design filter
    nyquist = fs / 2.0
    low_norm = low_freq / nyquist
    high_norm = high_freq / nyquist
    
    # Check if frequencies are valid
    if low_norm >= 1.0 or high_norm >= 1.0 or low_norm <= 0 or high_norm <= 0:
        # Invalid frequencies, return original data
        logger.warning(f"Invalid frequency range [{low_freq}, {high_freq}] Hz for fs={fs} Hz.")
        return filtered_data
    
    try:
        # Design Butterworth bandpass filter
        b, a = signal.butter(order, [low_norm, high_norm], btype='band')
        
        # Apply filter only to valid data
        filtered_valid = signal.filtfilt(b, a, valid_data)
        
        # Place filtered data back into original positions, preserving NaN
        filtered_data[valid_mask] = filtered_valid
        
        return filtered_data
    except Exception as e:
        # If filtering fails, return original data
        logger.warning(f"Error applying bandpass filter: {e}. Returning original data.")
        return data


def apply_filters(data, fs, notch_freq=60.0, low_freq=0.5, high_freq=120.0, quality_factor=30.0, order=4):
    """
    Apply both notch filter (60 Hz) and bandpass filter (0.5-120 Hz).
    
    This is a convenience function that applies both filters in sequence.
    
    Args:
        data: Input signal data
        fs: Sampling rate in Hz
        notch_freq: Notch frequency (default: 60 Hz)
        low_freq: Low cutoff for bandpass (default: 0.5 Hz)
        high_freq: High cutoff for bandpass (default: 120 Hz)
        quality_factor: Quality factor for notch filter (default: 30.0)
        order: Filter order for bandpass (default: 4)
        
    Returns:
        Filtered data
    """
    # Apply notch filter first
    data_notched = apply_notch_filter(data, fs, notch_freq, quality_factor)
    
    # Then apply bandpass filter
    data_filtered = apply_bandpass_filter(data_notched, fs, low_freq, high_freq, order)
    
    return data_filtered

