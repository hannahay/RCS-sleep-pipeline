# Preprocessing Analysis

## Overview

The `preprocessing` analysis step runs `pre_processing_forSleepProfiler.py`, which performs **data merging and organization** (not signal filtering).

## What It Does

### 1. Data Merging
- **Merges two parquet files:**
  - `raw_data.parquet` - Contains neural signals (TD_key0, TD_key2, TD_key3) and timestamps
  - `sleep_data.parquet` - Contains sleep stage annotations (SleepStage) and other metadata

- **From raw_data.parquet, it extracts:**
  - `localTime` - Local timestamp
  - `DerivedTime` - Derived timestamp
  - `TD_key0`, `TD_key2`, `TD_key3` - Neural signal channels
  - `Adaptive_CurrentAdaptiveState` - Adaptive DBS state
  - `SessionIdentity` or `SessionNumber` - Session identifier

- **From sleep_data.parquet, it includes:**
  - ALL columns (including `SleepStage` and any other metadata)

### 2. Data Validation
- Validates that required columns are present
- Checks for empty TD_key columns
- Warns if SleepStage is missing

### 3. Length Matching
- Compares lengths of raw_data and sleep_data
- Truncates the longer file to match the shorter one
- Warns if length difference is significant (>10 minutes)

### 4. Visualization
- Creates sleep stage plots showing:
  - Sleep stages over time (local time axis)
  - Sleep stages over time (derived time axis)
- Saves plots to `plots/{patient_name}/` directory

### 5. Data Organization
- Saves merged data as: `raw_data_withSleepStage_session{number}.parquet`
- Organizes by patient in `preprocessing/{patient_name}/` directory

## Important Notes

### ⚠️ NO Signal Processing
- **No filtering is applied** (no notch filter, no bandpass filter)
- **No downsampling** is applied
- Data is saved **as-is** after merging

### When to Use Preprocessing

Use preprocessing when:
- You have separate `raw_data.parquet` and `sleep_data.parquet` files that need to be merged
- You need to combine neural signals with sleep stage annotations
- You want to validate data integrity before analysis

### When NOT to Use Preprocessing

Skip preprocessing if:
- Your data is already merged (single parquet file with both signals and sleep stages)
- You need signal filtering (use other preprocessing scripts for that)
- Your data is already in the format needed for analysis

## Output

The preprocessing step saves:
- **Merged parquet files**: `preprocessing/{patient_name}/raw_data_withSleepStage_session{number}.parquet`
- **Sleep stage plots**: `plots/{patient_name}/sleep_stages_*.png`

## Configuration

The preprocessing script uses hardcoded paths in the script itself:
- Base folder: `/media/longterm_hdd/hannac/Sleep_aDBS/data/sleep_profiler/`
- Looks for files in: `{base_folder}/{patient}/session_reports/`
- Expects: `raw_data.parquet` and `sleep_data.parquet` in session folders

**Note**: The preprocessing script is not yet integrated with the main config system. It uses its own hardcoded paths.

## Alternative Preprocessing Scripts

There are other preprocessing scripts in the codebase that do apply signal filtering:
- `pre_processing.py` - Applies 60Hz notch filter and 0.1-120Hz bandpass filter
- `pre_processing_nofilter_nothreshold.py` - Minimal preprocessing without filters
- `remove_DBS_artifact.py` - Removes DBS artifacts
- `clean_bursts_one_segment.py` - Cleans burst artifacts

These are not currently integrated into the pipeline but could be added if needed.
