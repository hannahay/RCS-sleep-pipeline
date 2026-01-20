#!/usr/bin/env python3
"""
Plot frequency band power results.

Creates plots comparing continuous vs adaptive sessions for State0 and State1.
Uses configs/freq_bands.yaml, configs/plot_config.yaml, and configs/plot_statistics.yaml.
"""

import sys
import os
import argparse
import yaml

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

# Import the original script's functions
from processing_freq_band.plot_frequency_bands_results import (
    load_frequency_bands_config,
    load_plot_config,
    main as original_main
)

def load_frequency_bands_config_updated(config_file=None):
    """Loads freq_bands.yaml from configs/ directory."""
    if config_file is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_file = os.path.join(script_dir, 'configs', 'freq_bands.yaml')
    return load_frequency_bands_config(config_file)


def load_plot_config_updated(config_file=None):
    """
    Load plot config with updated path to configs/ directory.
    """
    if config_file is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_file = os.path.join(script_dir, 'configs', 'plot_config.yaml')
    return load_plot_config(config_file)


def load_stats_config(config_file=None):
    """Loads plot_statistics.yaml from configs/ directory."""
    if config_file is None:
        script_dir = os.path.dirname(os.path.dirname(__file__))
        config_file = os.path.join(script_dir, 'configs', 'plot_statistics.yaml')
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print(f"Loaded statistics configuration from: {config_file}")
        return config
    else:
        print(f"WARNING: Statistics config file not found: {config_file}")
        print("Using default statistics configuration")
        # Return default config
        return {
            'tests': {
                'ttest': {'enabled': True},
                'wilcoxon': {'enabled': True},
                'unblocked_permutation': {'enabled': True, 'n_permutations': 1000, 'random_seed': 42, 'show_progress': False},
                'within_block_permutation': {'enabled': True, 'n_permutations': 1000, 'show_progress': False}
            },
            'min_samples': {
                'ttest': 2,
                'wilcoxon': 2,
                'unblocked_permutation': 2,
                'within_block_permutation': 1
            },
            'significance_threshold': 0.05,
            'display': {
                'show_pvalues': True,
                'show_test_statistics': False,
                'show_effect_sizes': False,
                'pvalue_format': 'scientific',
                'pvalue_decimals': 3,
                'show_significance_stars': True
            }
        }


if __name__ == "__main__":
    # Monkey-patch the config loading functions to use new paths
    import processing_freq_band.plot_frequency_bands_results as plot_module
    original_load_freq_config = plot_module.load_frequency_bands_config
    original_load_plot_config = plot_module.load_plot_config
    
    # Add load_stats_config function if it doesn't exist
    if not hasattr(plot_module, 'load_stats_config'):
        plot_module.load_stats_config = load_stats_config
    
    plot_module.load_frequency_bands_config = load_frequency_bands_config_updated
    plot_module.load_plot_config = load_plot_config_updated
    
    try:
        original_main()
    finally:
        # Restore original functions
        plot_module.load_frequency_bands_config = original_load_freq_config
        plot_module.load_plot_config = original_load_plot_config
        if hasattr(plot_module, 'load_stats_config'):
            delattr(plot_module, 'load_stats_config')
