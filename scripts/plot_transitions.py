#!/usr/bin/env python3
"""
Plot transition effects.

Visualizes frequency band power around state transitions.
"""

import sys
import os
import argparse

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

# Import the original script's functions
from process_transitions.plot_state_transition_effects import (
    load_config,
    load_plot_config,
    main as original_main
)

def load_config_updated(config_path=None):
    """Loads transitions.yaml from configs/ directory."""
    if config_path is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(script_dir, 'configs', 'transitions.yaml')
    return load_config(config_path)


def load_plot_config_updated(config_path=None):
    """Loads plot_config.yaml from configs/ directory."""
    if config_path is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(script_dir, 'configs', 'plot_config.yaml')
    return load_plot_config(config_path)


if __name__ == "__main__":
    # Monkey-patch the config loading functions to use new paths
    import process_transitions.plot_state_transition_effects as plot_module
    original_load_config = plot_module.load_config
    original_load_plot_config = plot_module.load_plot_config
    
    plot_module.load_config = load_config_updated
    plot_module.load_plot_config = load_plot_config_updated
    
    try:
        original_main()
    finally:
        # Restore original functions
        plot_module.load_config = original_load_config
        plot_module.load_plot_config = original_load_plot_config
