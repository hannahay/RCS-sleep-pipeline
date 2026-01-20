#!/usr/bin/env python3
"""
Data preprocessing.

Merges raw_data.parquet with sleep_data.parquet (no signal filtering).
"""

import sys
import os
import argparse
import yaml
from pathlib import Path

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

# Get the scripts directory
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent


def load_main_config(config_path=None):
    """Loads pipeline_main.yaml config."""
    if config_path is None:
        config_path = PROJECT_ROOT / 'configs' / 'pipeline_main.yaml'
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return None


# Import and run the original script's main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Preprocess sleep study data by merging raw_data.parquet with sleep_data.parquet'
    )
    parser.add_argument('--config', type=str, default=None,
                       help='Path to pipeline_main.yaml config file (default: configs/pipeline_main.yaml)')
    parser.add_argument('--base_folder', type=str, default=None,
                       help='Base folder path (overrides config, default: uses config or hardcoded default)')
    parser.add_argument('--patient', nargs='+', required=False,
                       help='Process only these patient(s) (e.g., --patient RCS16L RCS16R)')
    
    args = parser.parse_args()
    
    # Load config if provided
    main_config = None
    base_folder = args.base_folder
    
    if args.config or base_folder is None:
        # Try to load config to get base_data_dir_sleep_profiler
        config_path = args.config if args.config else None
        main_config = load_main_config(config_path)
        
        if main_config and base_folder is None:
            # Get base_data_dir_sleep_profiler from config
            base_folder = main_config.get('base_data_dir_sleep_profiler')
            if base_folder:
                print(f"Using base_data_dir_sleep_profiler from config: {base_folder}")
            else:
                print(f"base_data_dir_sleep_profiler not found in config, using default")
        elif base_folder is None:
            print(f"Config file not found, using default base folder")
    
    from pre_processing.pre_processing_forSleepProfiler import main
    
    if args.patient:
        if len(args.patient) == 1:
            main(patient_filter=args.patient[0], base_folder=base_folder)
        else:
            main(patient_filter=args.patient, base_folder=base_folder)
    else:
        main(base_folder=base_folder)
