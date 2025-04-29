import configparser
import sys
from pathlib import Path

def get_options_path():
    """
    Return the absolute path to the options.ini file for the application.
    Handles both PyInstaller (frozen) and normal script execution.
    """
    # Always resolve relative to the main app location, not this file's location
    if hasattr(sys, 'frozen'):
        # PyInstaller or similar
        base = Path(sys.executable).parent
    else:
        base = Path(sys.argv[0]).parent.resolve()
    return base / 'options.ini'


def parse_value(val):
    """
    Parse a string value from options.ini and convert it to its appropriate type.
    Handles None, booleans, and ints; returns str otherwise.
    """
    if val == "None":
        return None
    if val == "True":
        return True
    if val == "False":
        return False
    try:
        return int(val)
    except ValueError:
        return val


def load_options(section: str) -> dict:
    """
    Load options from the given section ('GUI' or 'CLI') in the options.ini file.
    Returns a dict of options, or empty dict if section not present.
    Converts types: 'None'->None, 'True'->True, 'False'->False, ints, else str.
    """
    config = configparser.ConfigParser()
    options_path = get_options_path()
    if not options_path.exists():
        return {}
    config.read(options_path)
    if section in config:
        return {k: parse_value(v) for k, v in config[section].items()}
    return {}


def save_options(section: str, options: dict):
    """
    Save the given options dict to the specified section ('GUI' or 'CLI') in options.ini.
    Overwrites only that section. Does NOT save input_dir/output_dir/log/version/check_update.
    """
    config = configparser.ConfigParser()
    options_path = get_options_path()
    if options_path.exists():
        config.read(options_path)
    # Exclude input_dir, output_dir, log, version, and check_update from saving
    filtered = {k: str(v) for k, v in options.items() if k not in ('input_dir', 'output_dir', 'log', 'version', 'check_update')}
    config[section] = filtered
    with open(options_path, 'w') as f:
        config.write(f)


def print_options(section: str):
    """
    Print all options for the given section ('GUI' or 'CLI') from options.ini to stdout.
    """
    opts = load_options(section)
    for k, v in opts.items():
        print(f"{k} = {v}")
