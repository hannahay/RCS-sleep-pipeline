"""
Logging utilities for RCS sleep pipeline.
"""

import logging
import os


def setup_logging(log_file=None, level=logging.INFO, format_string=None):
    """
    Set up logging configuration.
    
    Args:
        log_file: Optional path to log file. If None, only logs to console.
        level: Logging level (default: INFO)
        format_string: Custom format string. If None, uses default format.
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

