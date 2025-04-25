# Global arguments/constants for CLI and TUI usage

# Quantization defaults for CLI and TUI (single source of truth)
DEFAULT_QB_COLOR = 0  # 0 means no quantization (full color)
DEFAULT_QB_GRAY_COLOR = 8  # 256 levels (was 4)
DEFAULT_QB_GRAY = 4        # 16 levels

cli_args = {
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

# Status bar color constants
STATUS_COLORS = {
    "INFO": "yellow",
    "SUCCESS": "green",
    "ERROR": "red",
}
