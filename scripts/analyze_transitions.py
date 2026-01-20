#!/usr/bin/env python3
"""
Analyze transition effects.

Analyzes frequency band power around state transitions.
"""

import sys
import os
import argparse

# Add the original code directory to path
original_code_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'code')
if os.path.exists(original_code_dir):
    sys.path.insert(0, original_code_dir)

if __name__ == "__main__":
    from process_transitions.analyze_transition_effects import main
    
    # The original script loads config from its directory
    # We'll update the path to look in configs/
    parser = argparse.ArgumentParser(description="Analyze frequency band power around state transitions")
    parser.add_argument('--config',
                       default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs', 'transitions.yaml'),
                       help='Path to YAML configuration file')
    
    args = parser.parse_args()
    
    import sys as sys_module
    sys_module.argv = ['analyze_transitions.py', '--config', args.config]
    main()
