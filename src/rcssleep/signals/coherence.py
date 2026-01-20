"""
Coherence calculation functions for RCS sleep pipeline.

Provides functions for calculating spectral coherence between signals.
"""

import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


def calculate_coherence(x, y, fs, nperseg=2048, noverlap=None):
    """
    Calculate spectral coherence between two signals using Welch's method.
    
    Coherence measures the linear relationship between two signals in the frequency domain.
    Values range from 0 to 1, where 1 indicates perfect linear relationship.
    
    Args:
        x: First signal
        y: Second signal
        fs: Sampling frequency in Hz
        nperseg: Length of each segment for Welch's method (default: 2048)
        noverlap: Number of points to overlap between segments. If None, uses 50% overlap.
        
    Returns:
        tuple: (frequencies, coherence values)
    """
    if noverlap is None:
        noverlap = nperseg // 2
    
    freqs, coh = signal.coherence(x, y, fs=fs, nperseg=nperseg, noverlap=noverlap)
    
    return freqs, coh


def calculate_band_averaged_coherence(x, y, fs, fmin, fmax, nperseg=2048, noverlap=None):
    """
    Calculate coherence averaged over a frequency band.
    
    Args:
        x: First signal
        y: Second signal
        fs: Sampling frequency in Hz
        fmin: Minimum frequency in Hz
        fmax: Maximum frequency in Hz
        nperseg: Length of each segment for Welch's method
        noverlap: Number of points to overlap between segments
        
    Returns:
        float: Average coherence in the specified frequency band
    """
    freqs, coh = calculate_coherence(x, y, fs, nperseg=nperseg, noverlap=noverlap)
    
    # Find frequency indices within the band
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    
    if not np.any(freq_mask):
        logger.warning(f"No frequencies found in range [{fmin}, {fmax}] Hz")
        return 0.0
    
    # Calculate average coherence in the band
    band_coh = np.mean(coh[freq_mask])
    
    return band_coh
