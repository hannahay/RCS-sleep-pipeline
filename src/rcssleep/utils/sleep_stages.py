"""
Sleep stage mappings and utilities.
"""

# Standard sleep stage mappings
SLEEP_STAGE_MAP = {
    2: "N3",
    3: "N2",
    4: "N1",
    5: "REM",
    6: "Wake"
}

# Alternative mapping (used in some contexts)
SLEEP_STAGE_MAP_ALT = {
    0: "Wake",
    1: "N1",
    2: "N2",
    3: "N3",
    4: "N2",  # Sometimes N2 is mapped to 4
    5: "REM",
    6: "Wake"
}


def map_sleep_stage(stage_value, mapping=None):
    """
    Map numeric sleep stage value to string label.
    
    Args:
        stage_value: Numeric sleep stage value
        mapping: Dictionary mapping, defaults to SLEEP_STAGE_MAP
        
    Returns:
        str: Sleep stage label or None if not found
    """
    if mapping is None:
        mapping = SLEEP_STAGE_MAP
    
    return mapping.get(stage_value, None)


def is_nrem_stage(stage_value, mapping=None):
    """Check if stage value corresponds to NREM sleep (N2 or N3)."""
    stage_label = map_sleep_stage(stage_value, mapping)
    return stage_label in ["N2", "N3"]


def is_rem_stage(stage_value, mapping=None):
    """Check if stage value corresponds to REM sleep."""
    stage_label = map_sleep_stage(stage_value, mapping)
    return stage_label == "REM"


def is_wake_stage(stage_value, mapping=None):
    """Check if stage value corresponds to wake."""
    stage_label = map_sleep_stage(stage_value, mapping)
    return stage_label == "Wake"

