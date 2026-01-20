#!/usr/bin/env python3
"""
Main pipeline orchestrator for RCS sleep analysis.

Runs analysis steps and generates plots based on pipeline_main.yaml config.
Substitutes placeholders ({patient_id}, {base_data_dir}, etc.) in config files.

Usage:
    python scripts/run_pipeline.py --config configs/pipeline_main.yaml
    python scripts/run_pipeline.py --all
    python scripts/run_pipeline.py --preprocessing --freq_bands
"""

import sys
import os
import argparse
import subprocess
import yaml
import tempfile
import shutil
from pathlib import Path
from copy import deepcopy

# Get the scripts directory
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent


def get_selected_base_data_dir(main_config):
    """
    Get the selected base data directory based on use_base_data_dir parameter.
    
    Args:
        main_config: Main config dictionary
        
    Returns:
        Selected base data directory path as string, or empty string if not found
    """
    if not main_config:
        return ''
    
    use_base_data_dir = main_config.get('use_base_data_dir', 'base_data_dir')
    
    if use_base_data_dir == 'base_data_dir':
        return main_config.get('base_data_dir', '')
    elif use_base_data_dir == 'base_data_dir_sleep_profiler':
        return main_config.get('base_data_dir_sleep_profiler', '')
    else:
        # Custom path provided
        return use_base_data_dir


def get_default_results_dir(main_config):
    """Returns default results directory: {selected_base_data_dir}/results or PROJECT_ROOT/results."""
    if not main_config:
        return str(PROJECT_ROOT / 'results')
    
    # Determine which base_data_dir to use
    use_base_data_dir = main_config.get('use_base_data_dir', 'base_data_dir')
    
    if use_base_data_dir == 'base_data_dir':
        selected_base_data_dir = main_config.get('base_data_dir', '')
    elif use_base_data_dir == 'base_data_dir_sleep_profiler':
        selected_base_data_dir = main_config.get('base_data_dir_sleep_profiler', '')
    else:
        # Custom path provided
        selected_base_data_dir = use_base_data_dir
    
    if selected_base_data_dir:
        return str(Path(selected_base_data_dir) / 'results')
    else:
        return str(PROJECT_ROOT / 'results')


def auto_detect_plot_input(plot_type, main_config):
    """
    Auto-detect plot input files based on plot type and main_config.
    
    Args:
        plot_type: Type of plot ('freq_bands', 'psd', 'slow_waves', 'coherence')
        main_config: Main config dictionary with patient_id, results_dir, etc.
        
    Returns:
        Path to input file if found, None otherwise
    """
    if not main_config or 'patient_id' not in main_config:
        return None
    
    patient_id = main_config['patient_id']
    results_dir = main_config.get('results_dir', get_default_results_dir(main_config))
    results_base = Path(results_dir)
    patient_results_dir = results_base / patient_id
    
    if plot_type == 'freq_bands':
        # Look for frequency_bands_analysis files in freq_bands directory
        # Prefer CSV files (especially linear) since they don't require fastexcel
        freq_bands_dir = patient_results_dir / 'freq_bands'
        if freq_bands_dir.exists():
            # Try linear CSV first (preferred format)
            csv_linear_file = freq_bands_dir / 'frequency_bands_analysis_linear.csv'
            if csv_linear_file.exists():
                return str(csv_linear_file)
            # Try regular CSV
            csv_file = freq_bands_dir / 'frequency_bands_analysis.csv'
            if csv_file.exists():
                return str(csv_file)
            # Fall back to Excel if CSV not available (requires fastexcel)
            xlsx_file = freq_bands_dir / 'frequency_bands_analysis.xlsx'
            if xlsx_file.exists():
                return str(xlsx_file)
    
    elif plot_type == 'psd':
        # Look for PSD files (*_psd.json or *_psd.csv) in freq_bands directory
        freq_bands_dir = patient_results_dir / 'freq_bands'
        if freq_bands_dir.exists():
            # Try JSON first
            json_files = list(freq_bands_dir.glob('*_psd.json'))
            if json_files:
                # Return most recent
                return str(max(json_files, key=lambda p: p.stat().st_mtime))
            # Try CSV
            csv_files = list(freq_bands_dir.glob('*_psd.csv'))
            if csv_files:
                # Return most recent
                return str(max(csv_files, key=lambda p: p.stat().st_mtime))
            # Also check for psd_data.csv
            psd_file = freq_bands_dir / 'psd_data.csv'
            if psd_file.exists():
                return str(psd_file)
    
    elif plot_type == 'slow_waves':
        # Look for slow wave metrics parquet files
        slow_waves_dir = patient_results_dir / 'slow_waves'
        if slow_waves_dir.exists():
            parquet_files = list(slow_waves_dir.glob('*metrics*.parquet'))
            if parquet_files:
                # Return most recent
                return str(max(parquet_files, key=lambda p: p.stat().st_mtime))
    
    elif plot_type == 'coherence':
        # Look for coherence parquet files
        coherence_dir = patient_results_dir / 'coherence'
        if coherence_dir.exists():
            parquet_files = list(coherence_dir.glob('coherence*.parquet'))
            if parquet_files:
                # Return most recent
                return str(max(parquet_files, key=lambda p: p.stat().st_mtime))
    
    return None


def substitute_placeholders(text, substitutions):
    """
    Substitute placeholders in text with actual values.
    
    Args:
        text: String that may contain placeholders like {patient_id}
        substitutions: Dictionary of placeholder -> value mappings
        
    Returns:
        String with placeholders replaced
    """
    if isinstance(text, str):
        for key, value in substitutions.items():
            text = text.replace(f"{{{key}}}", str(value))
    return text


def substitute_in_dict(data, substitutions):
    """Recursively replaces placeholders in dict/list structures."""
    if isinstance(data, dict):
        return {k: substitute_in_dict(v, substitutions) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_in_dict(item, substitutions) for item in data]
    elif isinstance(data, str):
        return substitute_placeholders(data, substitutions)
    else:
        return data


def load_and_substitute_config(config_path, main_config):
    """Loads config file and replaces placeholders ({patient_id}, {base_data_dir}, etc.) with values from main_config."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Determine which base_data_dir to use based on use_base_data_dir parameter
    use_base_data_dir = main_config.get('use_base_data_dir', 'base_data_dir')
    
    if use_base_data_dir == 'base_data_dir':
        selected_base_data_dir = main_config.get('base_data_dir', '')
    elif use_base_data_dir == 'base_data_dir_sleep_profiler':
        selected_base_data_dir = main_config.get('base_data_dir_sleep_profiler', '')
    else:
        # Custom path provided
        selected_base_data_dir = use_base_data_dir
    
    # Create substitutions dictionary
    substitutions = {
        'patient_id': main_config.get('patient_id', ''),
        'hemisphere': main_config.get('hemisphere', ''),
        'base_data_dir': selected_base_data_dir,  # Use selected base directory
        'base_data_dir_sleep_profiler': main_config.get('base_data_dir_sleep_profiler', ''),
        'results_dir': main_config.get('results_dir', get_default_results_dir(main_config)),
        'model_base_dir': main_config.get('model_base_dir', ''),
        'model_subdir_pattern': main_config.get('model_subdir_pattern', ''),
    }
    
    # Auto-construct model_path if not set
    # Model path is optional - only needed for sleep scoring analyses
    if not main_config.get('model_path'):
        model_base = main_config.get('model_base_dir', '')
        model_subdir = main_config.get('model_subdir_pattern', '')
        patient_id = main_config.get('patient_id', '')
        if model_base and model_subdir and patient_id:
            # Try to find the model directory
            model_dir = Path(model_base) / model_subdir / patient_id
            if model_dir.exists():
                # Look for ClusterClassificationModel directories
                model_dirs = list(model_dir.glob('ClusterClassificationModel_*'))
                if model_dirs:
                    # Use the most recent one (by modification time)
                    latest_model = max(model_dirs, key=lambda p: p.stat().st_mtime)
                    main_config['model_path'] = str(latest_model)
                    print(f"   Auto-detected model path: {main_config['model_path']}")
                # Don't warn if model directory exists but no models found - it's optional
            # Don't warn if model directory doesn't exist - it's optional for most analyses
    
    # Add model_path to substitutions if it exists
    if main_config.get('model_path'):
        substitutions['model_path'] = main_config['model_path']
    
    # Apply substitutions
    config = substitute_in_dict(config, substitutions)
    
    # Apply overrides from main_config if they exist
    config_name = config_path.stem
    if 'config_overrides' in main_config and config_name in main_config['config_overrides']:
        overrides = main_config['config_overrides'][config_name]
        # Skip if overrides is None or empty
        if overrides is not None:
            # Recursively update config with overrides
            for key, value in overrides.items():
                if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                    config[key].update(value)
                else:
                    config[key] = substitute_in_dict(value, substitutions)
    
    return config


def write_temp_config(config_dict, original_config_path):
    """
    Write a config dictionary to a temporary file.
    
    Args:
        config_dict: Config dictionary to write
        original_config_path: Original config path (for naming)
        
    Returns:
        Path to temporary config file
    """
    temp_dir = PROJECT_ROOT / 'temp_configs'
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / f"{original_config_path.stem}_temp.yaml"
    
    with open(temp_file, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    return temp_file


def run_script(script_name, args=None, use_temp_config=False):
    """Runs a script from scripts/ directory. Returns True if successful."""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    if args:
        print(f"Args: {' '.join(str(a) for a in args)}")
    print(f"{'='*60}\n")
    
    try:
        # Use Popen for real-time output streaming
        # Set unbuffered mode for real-time output
        import os
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        process = subprocess.Popen(cmd, cwd=PROJECT_ROOT, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,  # Combine stderr with stdout
                                 text=True, bufsize=1,
                                 env=env)
        
        # Stream output in real-time line by line
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output, end='')
        
        # Get return code
        returncode = process.poll()
        success = returncode == 0
        
        if success:
            print(f"\n✅ {script_name} completed successfully")
        else:
            print(f"\n❌ {script_name} failed with exit code {returncode}")
        
        # Clean up temp configs if requested
        if use_temp_config:
            temp_dir = PROJECT_ROOT / 'temp_configs'
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        
        return success
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='RCS Sleep Pipeline Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use main config file (recommended)
  python scripts/run_pipeline.py --config configs/pipeline_main.yaml

  # Run full pipeline (all analyses)
  python scripts/run_pipeline.py --all

  # Run specific steps
  python scripts/run_pipeline.py --preprocessing --freq_bands --slow_waves

  # Override patient_id from command line
  python scripts/run_pipeline.py --config configs/pipeline_main.yaml --patient_id RCS12L
        """
    )
    
    # Config file
    parser.add_argument('--config', type=str,
                       help='Path to main pipeline config file (pipeline_main.yaml)')
    parser.add_argument('--patient_id', type=str,
                       help='Override patient_id from config file (e.g., RCS16L)')
    
    # Analysis steps
    parser.add_argument('--forward_fill', action='store_true',
                       help='Forward-fill Adaptive_CurrentAdaptiveState')
    parser.add_argument('--preprocessing', action='store_true',
                       help='Run data preprocessing')
    parser.add_argument('--freq_bands', action='store_true',
                       help='Run frequency band analysis')
    parser.add_argument('--coherence', action='store_true',
                       help='Run coherence analysis')
    parser.add_argument('--slow_waves', action='store_true',
                       help='Run slow wave detection')
    parser.add_argument('--transitions', action='store_true',
                       help='Run transition analysis')
    parser.add_argument('--analyze_transitions', action='store_true',
                       help='Run transition effects analysis')
    
    # Plot steps
    parser.add_argument('--plot_freq_bands', action='store_true',
                       help='Plot frequency band results')
    parser.add_argument('--plot_slow_waves', action='store_true',
                       help='Plot slow wave results')
    parser.add_argument('--plot_transitions', action='store_true',
                       help='Plot transition effects')
    parser.add_argument('--plot_coherence', action='store_true',
                       help='Plot coherence results')
    parser.add_argument('--plot_psd', action='store_true',
                       help='Plot PSD results')
    
    # Convenience flags
    parser.add_argument('--all', action='store_true',
                       help='Run all analysis steps')
    parser.add_argument('--all_plots', action='store_true',
                       help='Run all plot steps')
    
    # Additional arguments
    parser.add_argument('--input_file', type=str,
                       help='Input file for plot scripts')
    parser.add_argument('--output_dir', type=str,
                       help='Output directory for plots')
    
    args = parser.parse_args()
    
    # Load main config if provided
    main_config = {}
    if args.config:
        config_path = PROJECT_ROOT / args.config if not Path(args.config).is_absolute() else Path(args.config)
        if config_path.exists():
            with open(config_path, 'r') as f:
                main_config = yaml.safe_load(f)
            print(f"✅ Loaded main config from: {config_path}")
            
            # Override patient_id if provided via command line
            if args.patient_id:
                main_config['patient_id'] = args.patient_id
                print(f"   Using patient_id: {args.patient_id} (from command line)")
            elif 'patient_id' in main_config:
                print(f"   Using patient_id: {main_config['patient_id']} (from config)")
            
            # Set up results directory - default to selected base_data_dir/results
            if 'results_dir' not in main_config or main_config['results_dir'] is None:
                main_config['results_dir'] = get_default_results_dir(main_config)
            else:
                # Make sure it's an absolute path
                results_dir = Path(main_config['results_dir'])
                if not results_dir.is_absolute():
                    # If relative path, resolve relative to selected base_data_dir if available
                    selected_base_data_dir = get_selected_base_data_dir(main_config)
                    
                    if selected_base_data_dir:
                        results_dir = Path(selected_base_data_dir) / results_dir
                    else:
                        results_dir = PROJECT_ROOT / results_dir
                main_config['results_dir'] = str(results_dir)
            
            # Create results directory structure: results/{patient_id}/
            if 'patient_id' in main_config:
                patient_id = main_config['patient_id']
                results_base = Path(main_config['results_dir'])
                patient_results_dir = results_base / patient_id
                
                # Create directory structure
                patient_results_dir.mkdir(parents=True, exist_ok=True)
                
                # Create subdirectories for different analysis types (CSV/results)
                (patient_results_dir / 'freq_bands').mkdir(exist_ok=True)
                (patient_results_dir / 'coherence').mkdir(exist_ok=True)
                (patient_results_dir / 'slow_waves').mkdir(exist_ok=True)
                (patient_results_dir / 'transitions').mkdir(exist_ok=True)
                (patient_results_dir / 'lfp_transitions').mkdir(exist_ok=True)
                
                # Create organized plot subdirectories
                plots_dir = patient_results_dir / 'plots'
                plots_dir.mkdir(exist_ok=True)
                (plots_dir / 'freq_bands').mkdir(exist_ok=True)
                (plots_dir / 'psd').mkdir(exist_ok=True)
                (plots_dir / 'coherence').mkdir(exist_ok=True)
                (plots_dir / 'slow_waves').mkdir(exist_ok=True)
                (plots_dir / 'transitions').mkdir(exist_ok=True)
                
                print(f"   Results will be saved to: {patient_results_dir}")
                print(f"   CSV files: {patient_results_dir}/<analysis_type>/")
                print(f"   Plots: {patient_results_dir}/plots/<plot_type>/")
                
                # Set plot_output_dir if not specified (base plots directory)
                if not main_config.get('plot_output_dir'):
                    main_config['plot_output_dir'] = str(plots_dir)
                
                # Auto-construct model_path if not set
                # Only show warnings if model is actually needed (e.g., for sleep scoring)
                # For freq_bands analysis, model_path is optional
                if not main_config.get('model_path'):
                    model_base = main_config.get('model_base_dir', '')
                    model_subdir = main_config.get('model_subdir_pattern', '')
                    if model_base and model_subdir and patient_id:
                        # Try to find the model directory
                        model_dir = Path(model_base) / model_subdir / patient_id
                        if model_dir.exists():
                            # Look for ClusterClassificationModel directories
                            model_dirs = list(model_dir.glob('ClusterClassificationModel_*'))
                            if model_dirs:
                                # Use the most recent one (by modification time)
                                latest_model = max(model_dirs, key=lambda p: p.stat().st_mtime)
                                main_config['model_path'] = str(latest_model)
                                print(f"   Auto-detected model path: {main_config['model_path']}")
                            # Don't warn if model directory exists but no models found - it's optional
                        # Don't warn if model directory doesn't exist - it's optional for most analyses
        else:
            print(f"⚠️  Config file not found: {config_path}")
            print("   Continuing without main config...")
    
    # If main config specifies which analyses to run, use those
    if main_config:
        if main_config.get('run_all_analyses', False):
            args.all = True
        if main_config.get('run_all_plots', False):
            args.all_plots = True
        
        # Override individual flags from config
        if 'analyses' in main_config:
            analyses = main_config['analyses']
            if not any([args.forward_fill, args.preprocessing, args.freq_bands, args.coherence, 
                       args.slow_waves, args.transitions, args.analyze_transitions, args.all]):
                # Only override if no command-line flags were set
                args.forward_fill = analyses.get('forward_fill', False)
                args.preprocessing = analyses.get('preprocessing', False)
                args.freq_bands = analyses.get('freq_bands', False)
                args.coherence = analyses.get('coherence', False)
                args.slow_waves = analyses.get('slow_waves', False)
                args.transitions = analyses.get('transitions', False)
                args.analyze_transitions = analyses.get('analyze_transitions', False)
        
        if 'plots' in main_config:
            plots = main_config['plots']
            if not any([args.plot_freq_bands, args.plot_slow_waves, args.plot_transitions,
                       args.plot_coherence, args.plot_psd, args.all_plots]):
                args.plot_freq_bands = plots.get('plot_freq_bands', False)
                args.plot_slow_waves = plots.get('plot_slow_waves', False)
                args.plot_transitions = plots.get('plot_transitions', False)
                args.plot_coherence = plots.get('plot_coherence', False)
                args.plot_psd = plots.get('plot_psd', False)
        
        # Get plot input files from config if not provided
        if 'plot_inputs' in main_config and not args.input_file:
            plot_inputs = main_config['plot_inputs']
            # Will be used when running plot scripts
    
    # If --all is specified, run all analysis steps
    if args.all:
        args.forward_fill = True
        args.preprocessing = True
        args.freq_bands = True
        args.coherence = True
        args.slow_waves = True
        args.transitions = True
        args.analyze_transitions = True
    
    # If --all_plots is specified, run all plot steps
    if args.all_plots:
        args.plot_freq_bands = True
        args.plot_slow_waves = True
        args.plot_transitions = True
        args.plot_coherence = True
        args.plot_psd = True
    
    # Check if any step is specified
    steps = [
        args.preprocessing, args.freq_bands, args.coherence, args.slow_waves,
        args.transitions, args.analyze_transitions,
        args.plot_freq_bands, args.plot_slow_waves, args.plot_transitions,
        args.plot_coherence, args.plot_psd
    ]
    
    if not any(steps):
        parser.print_help()
        print("\n⚠️  No steps specified. Use --config, --all, or specify individual steps.")
        return
    
    results = {}
    temp_configs = []  # Track temp config files for cleanup
    
    # Run analysis steps (forward_fill should run before preprocessing)
    if args.forward_fill:
        script_args = []
        # Pass config path to forward_fill script if available
        if main_config and args.config:
            script_args.extend(['--config', args.config])
        elif main_config:
            # Use default config path
            default_config = PROJECT_ROOT / 'configs' / 'pipeline_main.yaml'
            if default_config.exists():
                script_args.extend(['--config', str(default_config)])
        results['forward_fill'] = run_script('run_forward_fill.py', script_args)
    
    if args.preprocessing:
        script_args = []
        # Pass config path to preprocessing script if available
        if main_config and args.config:
            script_args.extend(['--config', args.config])
        elif main_config:
            # Use default config path
            default_config = PROJECT_ROOT / 'configs' / 'pipeline_main.yaml'
            if default_config.exists():
                script_args.extend(['--config', str(default_config)])
        results['preprocessing'] = run_script('run_preprocessing.py', script_args)
    
    if args.freq_bands:
        script_args = []
        config_path = PROJECT_ROOT / 'configs' / 'freq_bands.yaml'
        
        # Apply substitutions if main_config is available
        if main_config and config_path.exists():
            config = load_and_substitute_config(config_path, main_config)
            temp_config = write_temp_config(config, config_path)
            temp_configs.append(temp_config)
            script_args.extend(['--config', str(temp_config)])
        elif not args.config:
            # Use default config
            script_args.extend(['--config', str(config_path)])
        
        results['freq_bands'] = run_script('run_freq_bands.py', script_args)
        
        # After freq_bands analysis completes, copy session_types_analysis.csv to results directory
        # so it's available for plotting
        if results['freq_bands'] and main_config:
            patient_id = main_config.get('patient_id', '')
            # Use selected base_data_dir
            use_base_data_dir = main_config.get('use_base_data_dir', 'base_data_dir')
            if use_base_data_dir == 'base_data_dir':
                selected_base_data_dir = main_config.get('base_data_dir', '')
            elif use_base_data_dir == 'base_data_dir_sleep_profiler':
                selected_base_data_dir = main_config.get('base_data_dir_sleep_profiler', '')
            else:
                selected_base_data_dir = use_base_data_dir
            results_dir = main_config.get('results_dir', get_default_results_dir(main_config))
            
            if patient_id and selected_base_data_dir:
                # Source: selected_base_data_dir/{patient_id} directory
                patient_dir = Path(selected_base_data_dir) / patient_id
                source_file = patient_dir / 'session_types_analysis.csv'
                
                # Destination: results/freq_bands directory
                results_base = Path(results_dir)
                dest_dir = results_base / patient_id / 'freq_bands'
                dest_file = dest_dir / 'session_types_analysis.csv'
                
                if source_file.exists() and not dest_file.exists():
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    print(f"   ✅ Copied session_types_analysis.csv to: {dest_file}")
                elif source_file.exists() and dest_file.exists():
                    # Check if source is newer and update if needed
                    if source_file.stat().st_mtime > dest_file.stat().st_mtime:
                        shutil.copy2(source_file, dest_file)
                        print(f"   ✅ Updated session_types_analysis.csv in: {dest_file}")
                    else:
                        print(f"   ℹ️  session_types_analysis.csv already exists and is up-to-date: {dest_file}")
                elif not source_file.exists():
                    print(f"   ⚠️  session_types_analysis.csv not found at: {source_file}")
                    print(f"      Searched in: {patient_dir}")
                    print(f"      Plots will not be able to distinguish continuous vs adaptive sessions")
                    print(f"      To fix: Run analyze_session_types.py to generate this file")
    
    if args.coherence:
        results['coherence'] = run_script('run_coherence.py')
    
    if args.slow_waves:
        results['slow_waves'] = run_script('run_slow_waves.py')
    
    if args.transitions:
        script_args = []
        config_path = PROJECT_ROOT / 'configs' / 'lfp_transition.yaml'
        
        if main_config and config_path.exists():
            config = load_and_substitute_config(config_path, main_config)
            temp_config = write_temp_config(config, config_path)
            temp_configs.append(temp_config)
            script_args.extend(['--config', str(temp_config)])
        elif not args.config:
            script_args.extend(['--config', str(config_path)])
        
        results['transitions'] = run_script('run_transitions.py', script_args)
    
    if args.analyze_transitions:
        script_args = []
        config_path = PROJECT_ROOT / 'configs' / 'transitions.yaml'
        
        if main_config and config_path.exists():
            config = load_and_substitute_config(config_path, main_config)
            temp_config = write_temp_config(config, config_path)
            temp_configs.append(temp_config)
            script_args.extend(['--config', str(temp_config)])
        elif not args.config:
            script_args.extend(['--config', str(config_path)])
        
        results['analyze_transitions'] = run_script('analyze_transitions.py', script_args)
    
    # Run plot steps
    if args.plot_freq_bands:
        input_file = args.input_file
        if not input_file and main_config and 'plot_inputs' in main_config:
            input_file = main_config['plot_inputs'].get('freq_bands')
        
        # Auto-detect if still not found and config is available
        if not input_file and main_config:
            input_file = auto_detect_plot_input('freq_bands', main_config)
            if input_file:
                print(f"   Auto-detected freq_bands input file: {input_file}")
        
        if not input_file:
            print("⚠️  --plot_freq_bands requires --input_file or plot_inputs.freq_bands in config")
            if main_config and 'patient_id' in main_config:
                results_dir = main_config.get('results_dir', get_default_results_dir(main_config))
                patient_id = main_config['patient_id']
                expected_path = f"{results_dir}/{patient_id}/freq_bands/frequency_bands_analysis_linear.csv"
                print(f"   Expected location: {expected_path}")
        else:
            script_args = [input_file]
            
            # Auto-detect session_types_file if not provided
            if main_config:
                # Try in same directory as input file first
                input_dir = Path(input_file).parent
                session_types_in_dir = input_dir / 'session_types_analysis.csv'
                if session_types_in_dir.exists():
                    script_args.extend(['--session_types_file', str(session_types_in_dir)])
                else:
                    # Try in selected base_data_dir/{patient_id} directory
                    selected_base_data_dir = get_selected_base_data_dir(main_config)
                    patient_id = main_config.get('patient_id', '')
                    if selected_base_data_dir and patient_id:
                        patient_dir = Path(selected_base_data_dir) / patient_id
                        session_types_file = patient_dir / 'session_types_analysis.csv'
                        if session_types_file.exists():
                            script_args.extend(['--session_types_file', str(session_types_file)])
            
            if args.output_dir or (main_config and main_config.get('plot_output_dir')):
                base_plots_dir = args.output_dir or main_config.get('plot_output_dir')
                # Use plots/freq_bands subdirectory
                output_dir = str(Path(base_plots_dir) / 'freq_bands')
                script_args.extend(['--output_dir', output_dir])
            results['plot_freq_bands'] = run_script('plot_freq_bands.py', script_args)
    
    if args.plot_slow_waves:
        input_file = args.input_file
        if not input_file and main_config and 'plot_inputs' in main_config:
            input_file = main_config['plot_inputs'].get('slow_waves')
        
        # Auto-detect if still not found and config is available
        if not input_file and main_config:
            input_file = auto_detect_plot_input('slow_waves', main_config)
            if input_file:
                print(f"   Auto-detected slow_waves input file: {input_file}")
        
        if not input_file:
            print("⚠️  --plot_slow_waves requires --input_file or plot_inputs.slow_waves in config")
            if main_config and 'patient_id' in main_config:
                results_dir = main_config.get('results_dir', get_default_results_dir(main_config))
                patient_id = main_config['patient_id']
                expected_path = f"{results_dir}/{patient_id}/slow_waves/*metrics*.parquet"
                print(f"   Expected location: {expected_path}")
        else:
            script_args = [input_file]
            if args.output_dir or (main_config and main_config.get('plot_output_dir')):
                output_dir = args.output_dir or main_config.get('plot_output_dir')
                script_args.extend(['--output_dir', output_dir])
            results['plot_slow_waves'] = run_script('plot_slow_waves.py', script_args)
    
    if args.plot_transitions:
        script_args = []
        if args.output_dir or (main_config and main_config.get('plot_output_dir')):
            base_plots_dir = args.output_dir or main_config.get('plot_output_dir')
            # Use plots/transitions subdirectory
            output_dir = str(Path(base_plots_dir) / 'transitions')
            script_args.extend(['--output_dir', output_dir])
        results['plot_transitions'] = run_script('plot_transitions.py', script_args)
    
    if args.plot_coherence:
        input_file = args.input_file
        if not input_file and main_config and 'plot_inputs' in main_config:
            input_file = main_config['plot_inputs'].get('coherence')
        
        # Auto-detect if still not found and config is available
        if not input_file and main_config:
            input_file = auto_detect_plot_input('coherence', main_config)
            if input_file:
                print(f"   Auto-detected coherence input file: {input_file}")
        
        if not input_file:
            print("⚠️  --plot_coherence requires --input_file or plot_inputs.coherence in config")
            print("   Expected location: {results_dir}/{patient_id}/coherence/coherence*.parquet")
        else:
            script_args = [input_file]
            if args.output_dir or (main_config and main_config.get('plot_output_dir')):
                base_plots_dir = args.output_dir or main_config.get('plot_output_dir')
                # Use plots/coherence subdirectory
                output_dir = str(Path(base_plots_dir) / 'coherence')
                script_args.extend(['--output_dir', output_dir])
            results['plot_coherence'] = run_script('plot_coherence.py', script_args)
    
    if args.plot_psd:
        input_file = args.input_file
        if not input_file and main_config and 'plot_inputs' in main_config:
            input_file = main_config['plot_inputs'].get('psd')
        
        # Auto-detect if still not found and config is available
        if not input_file and main_config:
            input_file = auto_detect_plot_input('psd', main_config)
            if input_file:
                print(f"   Auto-detected PSD input file: {input_file}")
        
        if not input_file:
            print("⚠️  --plot_psd requires --input_file or plot_inputs.psd in config")
            if main_config and 'patient_id' in main_config:
                results_dir = main_config.get('results_dir', get_default_results_dir(main_config))
                patient_id = main_config['patient_id']
                expected_path = f"{results_dir}/{patient_id}/freq_bands/*_psd.json or *_psd.csv"
                print(f"   Expected location: {expected_path}")
        else:
            script_args = ['--psd_file', input_file]
            if args.output_dir or (main_config and main_config.get('plot_output_dir')):
                base_plots_dir = args.output_dir or main_config.get('plot_output_dir')
                # Use plots/psd subdirectory
                output_dir = str(Path(base_plots_dir) / 'psd')
                script_args.extend(['--output_dir', output_dir])
            results['plot_psd'] = run_script('plot_psd.py', script_args)
    
    # Clean up temp configs
    if temp_configs:
        temp_dir = PROJECT_ROOT / 'temp_configs'
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary config files")
    
    # Print summary
    print(f"\n{'='*60}")
    print("Pipeline Summary")
    print(f"{'='*60}")
    
    successful = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    
    if successful:
        print(f"\n✅ Successful steps ({len(successful)}):")
        for step in successful:
            print(f"   - {step}")
    
    if failed:
        print(f"\n❌ Failed steps ({len(failed)}):")
        for step in failed:
            print(f"   - {step}")
    
    if not results:
        print("\n⚠️  No steps were executed.")
    
    print()


if __name__ == "__main__":
    main()
