#!/usr/bin/env python3
"""
Plot coherence results.

Plots coherence between basal ganglia (TD_key0) and cortex (TD_key2, TD_key3),
and between cortex channels (TD_key2 and TD_key3).
"""

import sys
import os
import argparse

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

# Import the original script's functions
from processing_freq_band.plot_coherence_bg_cortex_results import (
    load_plot_config,
    main as original_main
)

def load_plot_config_updated(config_file=None):
    """Loads plot_config.yaml from configs/ directory."""
    if config_file is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_file = os.path.join(script_dir, 'configs', 'plot_config.yaml')
    return load_plot_config(config_file)


if __name__ == "__main__":
    # Monkey-patch the config loading function to use new path
    import processing_freq_band.plot_coherence_bg_cortex_results as plot_module
    original_load_plot_config = plot_module.load_plot_config
    
    plot_module.load_plot_config = load_plot_config_updated
    
    try:
        original_main()
    finally:
        # Restore original function
        plot_module.load_plot_config = original_load_plot_config
