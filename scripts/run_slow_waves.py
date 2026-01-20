#!/usr/bin/env python3
"""
Slow wave detection and analysis.

Detects and analyzes slow waves (delta waves) and beta bursts in overnight recordings.
"""

import sys
import os
import argparse

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

if __name__ == "__main__":
    from processing_SW.process_overnight_waves_Hanna import main
    # The original script has its own argument parsing
    main()
