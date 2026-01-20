"""
Data loading utilities for RCS sleep pipeline.

Provides memory-efficient functions for loading parquet files and CSV data.
"""

import os
import logging
import pandas as pd
import polars as pl

logger = logging.getLogger(__name__)


def read_parquet_fast(file_path, columns=None, use_polars=True):
    """
    Read parquet file efficiently, with option to use Polars for large files.
    
    For large files, Polars is more memory-efficient than pandas.
    For smaller files, pandas with PyArrow is sufficient.
    
    Args:
        file_path (str): Path to parquet file
        columns (list): Optional list of columns to read (recommended for large files)
        use_polars (bool): If True, use Polars for memory efficiency. If False, use pandas.
        
    Returns:
        pd.DataFrame: DataFrame with parquet data (always returns pandas DataFrame)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.info(f"Reading parquet file: {os.path.basename(file_path)} (columns: {len(columns) if columns else 'all'})...")
    
    if use_polars:
        try:
            # Use Polars for memory-efficient reading
            if columns:
                df_pl = pl.read_parquet(file_path, columns=columns)
            else:
                df_pl = pl.read_parquet(file_path)
            logger.info(f"Read completed: {len(df_pl):,} rows (using Polars)")
            # Convert to pandas for compatibility with rest of code
            return df_pl.to_pandas()
        except Exception as e:
            logger.warning(f"Error reading with Polars, falling back to pandas: {e}")
            # Fall through to pandas
    
    # Use pandas with PyArrow engine
    try:
        df = pd.read_parquet(file_path, columns=columns, engine='pyarrow')
    except Exception:
        df = pd.read_parquet(file_path, columns=columns, engine='auto')
    logger.info(f"Read completed: {len(df):,} rows (using pandas)")
    return df


def load_lfp_data(file_path, channels=['TD_key0', 'TD_key2', 'TD_key3']):
    """
    Load LFP channel data from parquet file using Polars (memory-efficient).
    
    Args:
        file_path: Path to parquet file
        channels: List of channel names to load
        
    Returns:
        pl.DataFrame: Polars DataFrame with DerivedTime and channel data, or None if error
    """
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return None
    
    try:
        # First, check schema to see which channels are available (memory-efficient)
        try:
            df_schema = pl.scan_parquet(file_path)
            available_columns = df_schema.columns
        except Exception:
            # Fallback: read a small sample to check columns
            df_sample = pl.read_parquet(file_path, n_rows=1)
            available_columns = df_sample.columns
            del df_sample
        
        # Check if channels exist
        available_channels = [ch for ch in channels if ch in available_columns]
        if not available_channels:
            logger.warning(f"None of the requested channels {channels} found in {file_path}")
            return None
        
        # Select DerivedTime and available channels during read (memory-efficient)
        cols_to_select = ['DerivedTime'] + available_channels
        df_selected = pl.read_parquet(file_path, columns=cols_to_select)
        
        # Remove rows with NaN in DerivedTime or any channel
        df_selected = df_selected.filter(
            pl.col('DerivedTime').is_not_null()
        )
        
        for ch in available_channels:
            df_selected = df_selected.filter(pl.col(ch).is_not_null())
        
        # Sort by DerivedTime
        df_selected = df_selected.sort('DerivedTime')
        
        return df_selected
        
    except Exception as e:
        logger.error(f"Error loading LFP data from {file_path}: {e}")
        return None


def read_parquet_with_polars(file_path):
    """
    Read parquet file using Polars and return as Polars DataFrame.
    
    Args:
        file_path: Path to parquet file
        
    Returns:
        pl.DataFrame: Polars DataFrame
    """
    if not os.path.exists(file_path):
        raise IOError(f"File not found: {file_path}")
    
    try:
        df = pl.read_parquet(file_path)
        return df
    except Exception as e:
        raise IOError(f"Error reading parquet file {file_path}: {str(e)}")

