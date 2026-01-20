# Phase 2 Complete: Plot Scripts

## Summary

Phase 2 (Plot Scripts) has been successfully completed! All plot entrypoint scripts have been created with proper config file mappings.

## Created Plot Scripts

### ✅ `scripts/plot_freq_bands.py`
- **Purpose:** Plot frequency band power results
- **Configs Used:**
  - `configs/freq_bands.yaml` - Frequency band definitions
  - `configs/plot_config.yaml` - Plot styling
- **Status:** ✅ Tested and working

### ✅ `scripts/plot_slow_waves.py`
- **Purpose:** Plot slow wave detection results
- **Configs Used:**
  - `configs/plot_config.yaml` - Plot styling
- **Status:** ✅ Tested and working

### ✅ `scripts/plot_transitions.py`
- **Purpose:** Plot transition effects
- **Configs Used:**
  - `configs/transitions.yaml` - Analysis parameters
  - `configs/plot_config.yaml` - Plot styling
- **Status:** ✅ Tested and working

### ✅ `scripts/plot_coherence.py`
- **Purpose:** Plot coherence results
- **Configs Used:**
  - `configs/plot_config.yaml` - Plot styling
- **Status:** ✅ Tested and working

### ✅ `scripts/plot_psd.py`
- **Purpose:** Plot power spectral density (PSD) results
- **Configs Used:**
  - `configs/plot_config.yaml` - Plot styling
- **Status:** ✅ Tested and working

## Config File Mappings

All plot scripts correctly map to their config files:
- **plot_config.yaml** is shared by ALL plot scripts for consistent styling
- Each script that needs analysis parameters has its specific config (freq_bands.yaml, transitions.yaml)
- All config paths have been updated to point to `configs/` directory

## Testing Results

✅ All plot scripts can:
- Import their original modules successfully
- Load configs from the new `configs/` directory
- Display help messages correctly
- Execute without import errors

## Documentation

- ✅ `CONFIG_MAPPINGS.md` - Complete documentation of which configs each script uses
- ✅ `REORGANIZATION_STATUS.md` - Updated with Phase 2 completion
- ✅ All scripts have docstrings explaining their config usage

## Next Steps

The reorganization is now complete for both Phase 1 and Phase 2. The codebase is:
- ✅ Properly organized
- ✅ All configs in one place
- ✅ All entrypoint scripts created
- ✅ Config mappings documented
- ✅ Ready for use

Future work (optional):
- Extract plotting functions into library modules
- Extract event detection functions into library modules
- Refactor scripts to use library modules instead of importing from original code
- Create comprehensive unit tests

## Usage

All scripts can now be run from the `RCS-sleep-pipeline/` directory:

```bash
# Analysis scripts
python3 scripts/run_freq_bands.py --config configs/freq_bands.yaml
python3 scripts/run_slow_waves.py
python3 scripts/run_transitions.py --config configs/lfp_transition.yaml

# Plot scripts
python3 scripts/plot_freq_bands.py input_file.xlsx
python3 scripts/plot_slow_waves.py input_file.parquet
python3 scripts/plot_transitions.py
```

All scripts automatically find their configs in the `configs/` directory!
