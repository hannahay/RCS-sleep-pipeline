#!/usr/bin/env python3
"""
Forward-fill state preprocessing.

Adds Adaptive_CurrentAdaptiveState_filled column to raw_data.parquet files.
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Forward-fill Adaptive_CurrentAdaptiveState for all sessions'
    )
    parser.add_argument('--config', type=str, default=None,
                       help='Path to pipeline_main.yaml config file (default: configs/pipeline_main.yaml)')
    parser.add_argument('--base_folder', type=str, default=None,
                       help='Base folder path (overrides config)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without modifying files')
    parser.add_argument('--sfreq', type=float, default=500.0,
                       help='Sampling frequency in Hz (default: 500.0)')
    parser.add_argument('--general-limit', type=float, default=15.0,
                       help='General forward fill limit in seconds (default: 15.0)')
    parser.add_argument('--transition-limit', type=float, default=21.0,
                       help='Forward fill limit at transitions in seconds (default: 21.0)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of sessions to process (for testing)')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Directory to save metrics CSV file')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing even if already processed')
    
    args = parser.parse_args()
    
    # Load config if provided
    main_config = None
    base_folder = args.base_folder
    
    if args.config or base_folder is None:
        config_path = args.config if args.config else None
        main_config = load_main_config(config_path)
        
        if main_config and base_folder is None:
            # Use selected base_data_dir for forward-fill
            use_base_data_dir = main_config.get('use_base_data_dir', 'base_data_dir')
            if use_base_data_dir == 'base_data_dir':
                base_folder = main_config.get('base_data_dir', '')
            elif use_base_data_dir == 'base_data_dir_sleep_profiler':
                base_folder = main_config.get('base_data_dir_sleep_profiler', '')
            else:
                base_folder = use_base_data_dir
            
            if base_folder:
                # Forward-fill expects path to session_reports directory
                patient_id = main_config.get('patient_id', '')
                if patient_id:
                    base_folder = os.path.join(base_folder, patient_id, 'session_reports')
                print(f"Using base folder from config: {base_folder}")
            else:
                print("base_data_dir not found in config")
        elif base_folder is None:
            print("Config file not found and no base_folder provided")
    
    # Import and call main function
    from preprocess_forward_fill_states import main
    
    # Build sys.argv for the original script
    import sys as sys_module
    script_args = []
    
    if base_folder:
        script_args.append(base_folder)
    
    if args.dry_run:
        script_args.append('--dry-run')
    if args.sfreq != 500.0:
        script_args.extend(['--sfreq', str(args.sfreq)])
    if args.general_limit != 15.0:
        script_args.extend(['--general-limit', str(args.general_limit)])
    if args.transition_limit != 21.0:
        script_args.extend(['--transition-limit', str(args.transition_limit)])
    if args.limit:
        script_args.extend(['--limit', str(args.limit)])
    if args.output_dir:
        script_args.extend(['--output-dir', args.output_dir])
    if args.force:
        script_args.append('--force')
    
    # Set sys.argv for the original script
    sys_module.argv = ['run_forward_fill.py'] + script_args
    main()
