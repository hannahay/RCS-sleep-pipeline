#!/usr/bin/env python3
"""
Frequency band power analysis.

Calculates power in delta, theta, beta, gamma, tuned-gamma bands
for state0 and state1 using Welch's method.
"""

import sys
import os
import argparse

# Add original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

# Import the main function from the original script
from processing_freq_band.calculate_frequency_bands import main as original_main, load_config

def load_config_updated(config_path=None):
    """Loads config from configs/ directory."""
    if config_path is None:
        # Look for config in the new configs/ directory
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(script_dir, 'configs', 'freq_bands.yaml')
    
    # Use the original load_config function
    return load_config(config_path)


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(
        description='Calculate frequency band power (delta, theta, beta, gamma, tuned-gamma) for state0 and state1'
    )
    parser.add_argument('--config',
                       default=None,
                       help='Path to YAML configuration file (default: configs/freq_bands.yaml)')
    parser.add_argument('--session_reports_dir',
                       default=None,
                       help='Directory containing session_reports folder with parquet files (overrides config)')
    parser.add_argument('--output_file', 
                       default=None,
                       help='Output Excel file path (overrides config)')
    parser.add_argument('--fs',
                       type=float,
                       default=None,
                       help='Sampling frequency in Hz (overrides config)')
    parser.add_argument('--epoch_sec',
                       type=float,
                       default=None,
                       help='Length of each epoch in seconds (overrides config)')
    
    args = parser.parse_args()
    
    # Set default config path if not provided
    if args.config is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        args.config = os.path.join(script_dir, 'configs', 'freq_bands.yaml')
    
    # Temporarily monkey-patch load_config to use our updated version
    import processing_freq_band.calculate_frequency_bands as calc_module
    original_load_config = calc_module.load_config
    calc_module.load_config = load_config_updated
    
    try:
        # Call the original main function
        original_main()
    finally:
        # Restore original function
        calc_module.load_config = original_load_config


if __name__ == "__main__":
    main()
