#!/usr/bin/env python3
"""
Coherence analysis.

Calculates coherence between basal ganglia (TD_key0) and cortex (TD_key2, TD_key3).
"""

import sys
import os

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

# Import and run the original script's main function
if __name__ == "__main__":
    from processing_freq_band.calculate_coherence_bg_cortex import main
    main()
