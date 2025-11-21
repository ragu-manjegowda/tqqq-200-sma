"""
Position state management for tracking trading positions.
"""
import os
import json
from datetime import datetime, timezone

from . import config


def load_state():
    """
    Load trading position state from file.
    
    Returns:
        dict: state dictionary with position and last_signal_date
    """
    # default: assume we're out of the market (CASH)
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            # fallback if corrupted
            return {
                "position": "CASH",
                "last_signal_date": None,
                "created": datetime.now(timezone.utc).isoformat()
            }
    else:
        state = {
            "position": "CASH",
            "last_signal_date": None,
            "created": datetime.now(timezone.utc).isoformat()
        }
        save_state(state)
        return state


def save_state(state):
    """
    Save trading position state to file.
    
    Args:
        state: dict containing position and last_signal_date
    """
    with open(config.STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)

