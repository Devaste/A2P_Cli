# Centralized configuration for A2P_Cli 2.0-beta

# Default values for CLI and GUI options
DEFAULT_QB_COLOR = None  # None means no quantization (full color)
DEFAULT_QB_GRAY_COLOR = None
DEFAULT_QB_GRAY = None
DEFAULT_METHOD = 2  # 0=Median Cut, 1=Max Coverage, 2=Fast Octree
DEFAULT_DITHER = 1  # 0=None, 1=Floyd-Steinberg

# Default options dictionary (used for initializing option state)
OPTIONS_DEFAULTS = {
    "input_dir": "",
    "output_dir": "",
    "remove": False,
    "recursive": False,
    "silent": False,
    "qb_color": DEFAULT_QB_COLOR,
    "qb_gray_color": DEFAULT_QB_GRAY_COLOR,
    "qb_gray": DEFAULT_QB_GRAY,
    "method": DEFAULT_METHOD,
    "dither": DEFAULT_DITHER,
}

# Choices and descriptions for options
METHOD_CHOICES = {
    0: 'Median Cut',
    1: 'Max Coverage',
    2: 'Fast Octree',
}
DITHER_CHOICES = {
    0: 'None',
    1: 'Floyd-Steinberg',
}

# Option descriptions for help/menus
OPTION_DESCRIPTIONS = {
    'input_dir': 'Directory containing .avif files (required)',
    'output_dir': 'Directory to save .png files (default: same as input)',
    'remove': 'Remove original .avif files after conversion',
    'recursive': 'Recursively search for .avif files in subdirectories',
    'silent': 'No output to command line, only finishing result',
    'qb_color': 'Quantization bits for color images (1–8, 2–256 colors)',
    'qb_gray_color': 'Quantization bits for grayscale+one images (1–8, 2–256 levels)',
    'qb_gray': 'Quantization bits for grayscale images (1–8, 2–256 levels)',
    'method': 'Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree',
    'dither': 'Dither: 0=None, 1=Floyd-Steinberg',
    'chk_bit': 'Check and display real bit depth (unique color count) for each converted image or single file.',
}

# Validators for each CLI option
OPTION_VALIDATORS = {
    'input_dir': lambda v: isinstance(v, str) and bool(v.strip()),
    'output_dir': lambda v: isinstance(v, str) or v is None,
    'remove': lambda v: v in ['y', 'n', True, False],
    'recursive': lambda v: v in ['y', 'n', True, False],
    'silent': lambda v: v in ['y', 'n', True, False],
    'qb_color': lambda v: (str(v).isdigit() and 1 <= int(v) <= 8) or v == '' or v is None,
    'qb_gray_color': lambda v: (str(v).isdigit() and 1 <= int(v) <= 8) or v == '' or v is None,
    'qb_gray': lambda v: (str(v).isdigit() and 1 <= int(v) <= 8) or v == '' or v is None,
    'method': lambda v: str(v) in ['0','1','2'],
    'dither': lambda v: str(v) in ['0','1'],
    'chk_bit': lambda v: v in [True, False],
}
