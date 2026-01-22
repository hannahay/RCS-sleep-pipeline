# RCS-Sleep-Pipeline

Pipeline for analyzing sleep data from Medtronic (RCS) devices.

## Overview

This pipeline processes neural recordings from sleep studies to:
- Calculate frequency band power (delta, theta, beta, gamma, etc.)
- Detect slow waves and spindles
- Analyze sleep stage transitions
- Generate visualizations and statistical summaries

## Installation

```bash
pip install -e .
```

## Project Structure

```
RCS-sleep-pipeline/
├── configs/              # YAML configuration files
├── src/rcssleep/         # Reusable library code
│   ├── io/              # Data loading utilities
│   ├── signals/         # Signal processing (filtering, bandpower, coherence)
│   ├── events/          # Event detection (slow waves, spindles)
│   ├── plots/           # Plotting utilities
│   ├── stats/           # Statistical analysis
│   └── utils/            # Utilities (logging, sleep stages)
├── scripts/             # Entrypoint scripts
├── tests/               # Unit tests
└── notebooks/            # Jupyter notebooks
```

## Usage

### Main Pipeline (Recommended)

Use the main config file to define which analyses to run and set patient_id:

```bash
# Run analyses defined in pipeline_main.yaml
python scripts/run_pipeline.py --config configs/pipeline_main.yaml

# Override patient_id from command line
python scripts/run_pipeline.py --config configs/pipeline_main.yaml --patient_id RCS12L

# Run all analysis steps
python scripts/run_pipeline.py --all

# Run specific steps
python scripts/run_pipeline.py --preprocessing --freq_bands --slow_waves

# Run analysis and then plots
python scripts/run_pipeline.py --freq_bands --plot_freq_bands --input_file results.xlsx
```

The main config file (`pipeline_main.yaml`) allows you to:
- Set `patient_id` once - it will be automatically substituted in all other config files
- Define which analyses to run (toggle on/off)
- Override paths in other config files using placeholders like `{patient_id}` and `{base_data_dir}`

### Individual Scripts

#### Preprocessing

```bash
python scripts/run_preprocessing.py
```

**Note**: Preprocessing merges `raw_data.parquet` with `sleep_data.parquet` to combine neural signals with sleep stage annotations. **No signal filtering is applied** - it's purely data merging and organization. See `PREPROCESSING_INFO.md` for details.

#### Frequency Band Analysis

```bash
python scripts/run_freq_bands.py --config configs/freq_bands.yaml
```

#### Slow Wave Detection

```bash
python scripts/run_slow_waves.py
```

#### Transition Analysis

```bash
python scripts/run_transitions.py --config configs/lfp_transition.yaml
```

#### Plotting

```bash
# Plot frequency band results
python scripts/plot_freq_bands.py input_file.xlsx

# Plot slow wave results
python scripts/plot_slow_waves.py input_file.parquet

# Plot transition effects
python scripts/plot_transitions.py
```

## Configuration

### Main Config File

The main configuration file `configs/pipeline_main.yaml` controls:
- **patient_id**: Patient identifier (e.g., "RCS16L") - automatically substituted in all configs
- **analyses**: Toggle which analyses to run
- **plots**: Toggle which plots to generate
- **results_dir**: Where to save all outputs (defaults to `results/` in project root)

### Results Directory Structure

All outputs are organized in a structured results directory:

```
results/
└── {patient_id}/           # e.g., RCS16L/
    ├── freq_bands/         # Frequency band analysis results
    ├── coherence/          # Coherence analysis results
    ├── slow_waves/         # Slow wave detection results
    ├── transitions/        # Transition analysis results
    ├── lfp_transitions/    # LFP transition analysis results
    └── plots/              # All plot outputs
```

### Analysis-Specific Configs

Individual analysis parameters are configured via YAML files in the `configs/` directory:
- `freq_bands.yaml` - Frequency band analysis parameters
- `plot_config.yaml` - Plotting style and colors (shared by all plots)
- `transitions.yaml` - Transition analysis parameters
- `lfp_transition.yaml` - LFP transition analysis parameters
- `sleep_scoring.yaml` - Sleep scoring evaluation parameters

## Dependencies

- numpy
- pandas
- polars (for memory-efficient parquet reading)
- scipy
- matplotlib
- pyyaml
