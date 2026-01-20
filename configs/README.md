# Configuration Files

This directory contains all YAML configuration files for the RCS sleep pipeline.

## Main Configuration

### `pipeline_main.yaml`
**This is the main configuration file** that controls which analyses to run and sets global parameters like `patient_id`.

Key features:
- **patient_id**: Patient identifier (e.g., "RCS16L") that will be automatically substituted in other config files
- **analyses**: Toggle which analyses to run (true/false)
- **plots**: Toggle which plots to generate (true/false)
- **config_overrides**: Override specific values in other config files

Usage:
```bash
python scripts/run_pipeline.py --config configs/pipeline_main.yaml
```

## Analysis-Specific Configs

### `freq_bands.yaml`
Configuration for frequency band power analysis.
- Used by: `run_freq_bands.py`, `plot_freq_bands.py`
- Contains: Sampling rate, epoch size, frequency bands, paths

### `transitions.yaml`
Configuration for transition effects analysis.
- Used by: `analyze_transitions.py`, `plot_transitions.py`
- Contains: Time windows, frequency bands, channels

### `lfp_transition.yaml`
Configuration for LFP stage transition analysis.
- Used by: `run_transitions.py`
- Contains: Data paths, analysis parameters, transition types

### `sleep_scoring.yaml`
Configuration for sleep scoring evaluation.
- Used by: Sleep scoring scripts
- Contains: NREM/REM stage mappings

## Plot Configuration

### `plot_config.yaml`
**Shared by all plot scripts** for consistent styling.
- Colors, fonts, plot styling
- Frequency bands to plot
- **States to plot** - Controls which states are included in plots (see below)
- **References `states_labels.yaml`** for patient-specific state labels
- Contains minimal fallback state labels (used only if `states_labels.yaml` cannot be loaded)

#### States to Plot Configuration

The `states_to_plot` section controls which states are included in plots:

```yaml
states_to_plot:
  # Options: 'all', 'basic_only', 'combined_only', or list of specific states
  mode: 'all'  # Default: plot everything
  
  # Optional: Explicit list of states to include (overrides mode if specified)
  include: null  # null = use mode, or specify list like ['state0', 'state1', 'NREM_State0']
  
  # Optional: List of states to exclude (applied after include/mode)
  exclude: []  # e.g., ['Unknown_State0', 'Unknown_State1'] to skip unknown states
```

**Mode options:**
- `'all'`: Plot both basic states (state0/state1) and combined states (NREM_State0, REM_State1, etc.) when available
- `'basic_only'`: Only plot state0 and state1 (ignore combined states)
- `'combined_only'`: Only plot combined states (NREM_State0, REM_State1, etc.), skip basic states

**Note**: Combined states (e.g., `NREM_State0`, `REM_State1`) are only available when the `SleepStage` column exists in the data. Analysis scripts automatically calculate both basic states and combined states when sleep stage data is present.

**Important**: Plotting scripts should:
1. Load `plot_config.yaml` for styling (colors, fonts, etc.)
2. Load `states_labels.yaml` for patient-specific state labels
3. Look up `patient_id` in `states_labels.yaml['patients']`
4. Use those labels for plot legends and titles

### `states_labels.yaml`
**Patient-specific state label definitions.**
- Maps each patient_id to their state meanings (state0 and state1 labels)
- Used by plotting scripts (via `plot_config.yaml`) to generate appropriate labels
- Referenced by `plot_config.yaml` - plotting scripts should load both files
- Contains patient-specific definitions and default fallback labels

Example:
```yaml
patients:
  RCS16L:
    state0: 'NREM-like'
    state1: 'wake+REM'
  RCS16R:
    state0: 'wake+REM'
    state1: 'NREM-like'
default:
  state0: 'State 0'
  state1: 'State 1'
```

**Usage in plotting scripts:**
```python
# Load both configs
plot_config = yaml.safe_load(open('configs/plot_config.yaml'))
states_labels = yaml.safe_load(open('configs/states_labels.yaml'))

# Get patient_id from pipeline_main.yaml or command line
patient_id = "RCS16L"

# Look up state labels for this patient
if patient_id in states_labels['patients']:
    state0_label = states_labels['patients'][patient_id]['state0']
    state1_label = states_labels['patients'][patient_id]['state1']
else:
    # Use defaults
    state0_label = states_labels['default']['state0']
    state1_label = states_labels['default']['state1']
```

### `config_states.yaml` (Alternative)
Alternative state label configuration file. Currently, `states_labels.yaml` is the primary file used by `plot_config.yaml`.

### `plot_statistics.yaml`
**Statistical test configuration for plotting scripts.**

Controls which statistical tests are performed and their parameters:
- **Enable/disable tests**: Toggle t-test, Wilcoxon, unblocked permutation, and within-block permutation tests
- **Test parameters**: Configure number of permutations, random seeds, progress display
- **Minimum sample sizes**: Set requirements for each test type
- **Display options**: Control how p-values and statistics are shown on plots

**Usage**: Automatically loaded by plotting scripts. No manual configuration needed unless you want to change test settings.

**Example configuration**:
```yaml
tests:
  ttest:
    enabled: true
  wilcoxon:
    enabled: true
  unblocked_permutation:
    enabled: true
    n_permutations: 1000
    random_seed: 42
  within_block_permutation:
    enabled: true
    n_permutations: 1000

min_samples:
  ttest: 2
  wilcoxon: 2
  unblocked_permutation: 2
  within_block_permutation: 1
```

## Patient ID, Hemisphere, and Results Directory Substitution

When using `pipeline_main.yaml`, placeholders are automatically substituted in other config files:

- `{patient_id}` - Replaced with the patient_id from main config
- `{hemisphere}` - Replaced with the hemisphere from main config ('left' or 'right')
- `{base_data_dir}` - Replaced with the **selected** base directory (see `use_base_data_dir` below)
- `{base_data_dir_sleep_profiler}` - Replaced with sleep_profiler base directory (always available)
- `{results_dir}` - Replaced with results directory (defaults to `{selected_base_data_dir}/results`)

### Selecting Base Data Directory

The `use_base_data_dir` parameter controls which directory is used when substituting `{base_data_dir}` in config files:

- `'base_data_dir'` (default): Uses `base_data_dir` from config
- `'base_data_dir_sleep_profiler'`: Uses `base_data_dir_sleep_profiler` from config
- Custom absolute path: Specify any path (e.g., `"/path/to/custom/data"`)

**Note**: 
- Preprocessing always uses `base_data_dir_sleep_profiler` (unless overridden via command line)
- LFP transitions can explicitly use `base_data_dir_sleep_profiler` via `config_overrides`
- All other analyses use the selected `base_data_dir` based on `use_base_data_dir`

### Hemisphere Parameter

The `hemisphere` parameter in `pipeline_main.yaml` determines:
- Which state meanings to use from `states_labels.yaml`
- How state labels are interpreted in plots
- Default state definitions when patient is not found in `states_labels.yaml`

Example:
```yaml
# In pipeline_main.yaml
patient_id: "RCS16L"
hemisphere: "left"

# The pipeline will look up RCS16L in states_labels.yaml
# and use the state definitions for that patient
```

Example:
```yaml
# In pipeline_main.yaml
patient_id: "RCS16L"
base_data_dir: "/media/longterm_hdd/hannac/Sleep_aDBS/data/adaptive/stage_3_pilot"
results_dir: null  # Will default to "results" in project root

# In freq_bands.yaml (after substitution via config_overrides)
session_reports_dir: "/media/longterm_hdd/hannac/Sleep_aDBS/data/adaptive/stage_3_pilot/RCS16L/session_reports"
output_file: "results/RCS16L/freq_bands/frequency_bands_analysis.xlsx"
```

## Results Directory Structure

All outputs are automatically saved to `results/{patient_id}/` with subdirectories for each analysis type:
- `results/{patient_id}/freq_bands/` - Frequency band analysis results
- `results/{patient_id}/plots/` - All plot outputs
- `results/{patient_id}/transitions/` - Transition analysis results
- etc.

See `RESULTS_STRUCTURE.md` for complete details.

## Overriding Patient ID

You can override the patient_id from the command line:

```bash
python scripts/run_pipeline.py --config configs/pipeline_main.yaml --patient_id RCS12L
```

This will use RCS12L instead of the value in the config file.
