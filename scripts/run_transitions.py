#!/usr/bin/env python3
"""
Sleep stage transition analysis.

Analyzes LFP activity during sleep stage transitions.
"""

import sys
import os
import argparse

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

if __name__ == "__main__":
    from process_transitions.sleepstage_transition.lfp_stage_transition_analysis import main
    
    parser = argparse.ArgumentParser(description="Analyze LFP activity during sleep stage transitions")
    parser.add_argument("--config", 
                       default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs', 'lfp_transition.yaml'),
                       help="Path to YAML configuration file")
    parser.add_argument("--data_folder", help="Folder containing parquet files to analyze")
    parser.add_argument("--data_file", help="Specific parquet file to analyze")
    parser.add_argument("--legacy_patient", help="Legacy mode: Patient ID (e.g., P001)")
    parser.add_argument("--session_number", help="Session number (e.g., 001) - required with --legacy_patient")
    parser.add_argument("--specific_file", help="Specific parquet file name within folder (optional)")
    parser.add_argument("--output_dir", default="transition_analysis_plots", help="Output directory for plots")
    parser.add_argument("--min_prev_duration", type=int, default=300, help="Minimum previous stage duration (seconds)")
    parser.add_argument("--min_next_duration", type=int, default=180, help="Minimum next stage duration (seconds)")
    parser.add_argument("--max_nan_ratio", type=float, default=0.5, help="Maximum ratio of NaN values to accept in segments (0.0-1.0)")
    parser.add_argument("--max_interpolation_duration", type=float, default=2.0, help="Maximum disconnection duration to interpolate (seconds)")
    
    args = parser.parse_args()
    
    import sys as sys_module
    sys_module.argv = ['run_transitions.py'] + [f'--{k}={v}' for k, v in vars(args).items() if v is not None]
    main()
