# Global arguments/constants for CLI and TUI usage

# Quantization bits defaults: None means 'off' (full color), 1-8 are valid
DEFAULT_QB_COLOR = None  # None means no quantization (full color)
DEFAULT_QB_GRAY_COLOR = None
DEFAULT_QB_GRAY = None

options_dict = {
    "input_dir": "",
    "output_dir": "",
    "remove": False,
    "recursive": False,
    "silent": False,
    "qb_color": DEFAULT_QB_COLOR,
    "qb_gray_color": DEFAULT_QB_GRAY_COLOR,
    "qb_gray": DEFAULT_QB_GRAY,
    "method": 1,  # default method is 1
    "dither": 0,  # default dither is 0
}

# Status bar color constants (moved to tui_mode.py)
