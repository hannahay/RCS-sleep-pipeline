# Config File Mappings

This document shows which config files each script uses. **This is critical** - each plot script must use the correct config files.

## Analysis Scripts

### `scripts/run_freq_bands.py`
- **Config:** `configs/freq_bands.yaml`
- **Purpose:** Frequency band analysis parameters (sampling rate, epochs, frequency bands, etc.)

### `scripts/run_coherence.py`
- **Config:** None (uses hardcoded parameters or command-line args)
- **Purpose:** Coherence analysis

### `scripts/run_slow_waves.py`
- **Config:** None (uses hardcoded parameters or command-line args)
- **Purpose:** Slow wave detection

### `scripts/run_transitions.py`
- **Config:** `configs/lfp_transition.yaml`
- **Purpose:** LFP transition analysis parameters

### `scripts/analyze_transitions.py`
- **Config:** `configs/transitions.yaml`
- **Purpose:** Transition effects analysis parameters

## Plot Scripts

### `scripts/plot_freq_bands.py`
- **Configs:**
  - `configs/freq_bands.yaml` - Frequency band definitions
  - `configs/plot_config.yaml` - Plot styling (colors, fonts, etc.)
  - `configs/plot_statistics.yaml` - Statistical test configuration (which tests to run, parameters)
- **Purpose:** Plot frequency band power results

### `scripts/plot_slow_waves.py`
- **Configs:**
  - `configs/plot_config.yaml` - Plot styling
- **Purpose:** Plot slow wave detection results
- **Note:** Originally looked in `processing_freq_band/plot_config.yaml`, now uses `configs/plot_config.yaml`

### `scripts/plot_transitions.py`
- **Configs:**
  - `configs/transitions.yaml` - Analysis parameters
  - `configs/plot_config.yaml` - Plot styling
- **Purpose:** Plot transition effects

### `scripts/plot_coherence.py`
- **Configs:**
  - `configs/plot_config.yaml` - Plot styling
- **Purpose:** Plot coherence results

### `scripts/plot_psd.py`
- **Configs:**
  - `configs/plot_config.yaml` - Plot styling
- **Purpose:** Plot power spectral density (PSD) results

## Shared Config Files

### `configs/plot_config.yaml`
Used by ALL plot scripts for consistent styling:
- Colors (state0, state1, continuous, adaptive)
- Font sizes
- Plot styling (alpha, scatter size, etc.)
- State labels

### `configs/plot_statistics.yaml`
Used by plotting scripts to configure statistical tests:
- Enable/disable specific tests (ttest, wilcoxon, unblocked_permutation, within_block_permutation)
- Configure test parameters (n_permutations, random_seed, etc.)
- Set minimum sample size requirements
- Configure display options (p-value format, significance stars, etc.)
- Frequency bands to plot

### `configs/states_labels.yaml`
Used for state label definitions (patient/hemisphere-specific)

## Config File Locations

All config files are in the `configs/` directory:
```
configs/
├── freq_bands.yaml          # Frequency band analysis
├── plot_config.yaml         # Plot styling (shared)
├── states_labels.yaml       # State labels
├── transitions.yaml         # Transition analysis
├── lfp_transition.yaml      # LFP transition analysis
└── sleep_scoring.yaml       # Sleep scoring evaluation
```

## Important Notes

1. **plot_config.yaml is shared** - All plot scripts use the same plot_config.yaml for consistent styling
2. **freq_bands.yaml is used by both** - Both `run_freq_bands.py` (analysis) and `plot_freq_bands.py` (plotting) use this config
3. **transitions.yaml vs lfp_transition.yaml** - These are different:
   - `transitions.yaml` - Used by `analyze_transitions.py` and `plot_transitions.py`
   - `lfp_transition.yaml` - Used by `run_transitions.py` (LFP stage transition analysis)
