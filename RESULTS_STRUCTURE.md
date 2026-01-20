# Results Directory Structure

## Overview

All analysis results, plots, and outputs are organized in a structured `results/` directory, with subdirectories organized by patient ID.

## Directory Structure

```
results/
└── {patient_id}/              # e.g., RCS16L/, RCS12R/
    ├── freq_bands/            # Frequency band analysis outputs
    │   ├── frequency_bands_analysis.xlsx
    │   ├── frequency_bands_analysis_linear.csv
    │   ├── frequency_bands_analysis_db.csv
    │   └── psd_data.csv (if generated)
    │
    ├── coherence/              # Coherence analysis outputs
    │   ├── coherence_bg_cortex_{patient_id}.parquet
    │   ├── coherence_bg_cortex_{patient_id}.xlsx
    │   └── coherence_summary_{patient_id}.parquet
    │
    ├── slow_waves/             # Slow wave detection outputs
    │   ├── overnight_delta_negative_wave_metrics_{patient_id}.parquet
    │   ├── overnight_delta_positive_wave_metrics_{patient_id}.parquet
    │   └── overnight_beta_burst_metrics_all.csv
    │
    ├── transitions/            # Transition effects analysis outputs
    │   ├── transition_power_analysis.csv
    │   └── transition_plots/
    │
    ├── lfp_transitions/        # LFP transition analysis outputs
    │   ├── session_001/
    │   │   ├── amplitude_time_series/
    │   │   ├── power_analysis/
    │   │   └── raw_data_examples/
    │   └── all_sessions_combined/
    │
    └── plots/                  # All plot outputs (organized by plot type)
        ├── freq_bands/          # Frequency band plots
        │   └── figures/         # Actual plot files (PNG) and CSVs (block assignments, statistics)
        ├── slow_waves/         # Slow wave plots
        ├── transitions/        # Transition plots
        ├── coherence/          # Coherence plots
        └── psd/                # PSD plots
```

## Configuration

The results directory is configured in `configs/pipeline_main.yaml`:

```yaml
# Results directory - all outputs will be saved here
# If null, defaults to "{base_data_dir}/results" (saves alongside your data)
results_dir: null  # null = use "{base_data_dir}/results", or specify absolute path

# Base data directory
base_data_dir: "/media/longterm_hdd/hannac/Sleep_aDBS/data/adaptive/stage_3"

# Patient ID determines the subdirectory
patient_id: "RCS16L"
```

**Note**: By default, results are saved to `{base_data_dir}/results/{patient_id}/`, keeping all outputs alongside your data files.

## Automatic Directory Creation

When you run the pipeline with `--config configs/pipeline_main.yaml`, the script automatically:
1. Creates `{base_data_dir}/results/` directory (or uses the specified `results_dir`)
2. Creates `{base_data_dir}/results/{patient_id}/` subdirectory (or `{results_dir}/{patient_id}/` if results_dir is explicitly set)
3. Creates analysis-specific subdirectories for CSV/results:
   - `freq_bands/` (CSV files)
   - `coherence/` (parquet/CSV files)
   - `slow_waves/` (parquet/CSV files)
   - `transitions/` (CSV files)
   - `lfp_transitions/` (analysis outputs)
4. Creates organized plot subdirectories:
   - `plots/freq_bands/` (frequency band plots)
   - `plots/psd/` (PSD plots)
   - `plots/coherence/` (coherence plots)
   - `plots/slow_waves/` (slow wave plots)
   - `plots/transitions/` (transition plots)

## Output File Locations

### Frequency Band Analysis
- **CSV files**: `results/{patient_id}/freq_bands/frequency_bands_analysis_linear.csv` (and `_db.csv`)
- **Plots**: `results/{patient_id}/plots/freq_bands/figures/` (PNG files, block assignments CSV, statistics CSV)

### Coherence Analysis
- **Results files**: `results/{patient_id}/coherence/` (parquet/CSV files)
- **Plots**: `results/{patient_id}/plots/coherence/` (PNG files, block assignments CSV, statistics CSV)

### Slow Wave Detection
- **Metrics files**: `results/{patient_id}/slow_waves/` (parquet/CSV files)
- **Plots**: `results/{patient_id}/plots/slow_waves/` (PNG files)

### Transition Analysis
- **Analysis results**: `results/{patient_id}/transitions/` (CSV files)
- **Plots**: `results/{patient_id}/plots/transitions/` (PNG files)

### PSD Analysis
- **Input files**: `results/{patient_id}/freq_bands/*_psd.json` or `*_psd.csv`
- **Plots**: `results/{patient_id}/plots/psd/` organized into subfolders:
  - `psd_individual_sessions/` - Individual session plots
  - `psd_continuous_vs_adaptive/` - Comparison plots (continuous vs adaptive)
  - `psd_channel_with_individuals/` - Channel plots with individual traces
  - `psd_all_conditions/` - All four conditions plots (continuous state0, continuous state1, adaptive state0, adaptive state1)

### LFP Transitions
- **Session outputs**: `results/{patient_id}/lfp_transitions/session_XXX/`
- **Combined analysis**: `results/{patient_id}/lfp_transitions/all_sessions_combined/`

## Benefits

1. **Organized by Patient**: Easy to find all results for a specific patient
2. **Separated by Analysis Type**: Clear organization of different analysis outputs
3. **Centralized Location**: All outputs in one place, not scattered in input directories
4. **Easy to Share**: Can easily share `results/{patient_id}/` folder
5. **Version Control Friendly**: Results directory is gitignored, keeping repo clean

## Git Ignore

The `results/` directory is automatically gitignored (see `.gitignore`), so:
- Results won't be committed to version control
- Each user can have their own results
- Keeps the repository clean and focused on code
