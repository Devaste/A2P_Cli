import os
from typing import Callable, Optional, Any
from .config import OPTION_DESCRIPTIONS

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_option(index: int, key: str, value: Any, extra: Optional[str] = None) -> None:
    """
    Print a formatted CLI option line with its description and value.
    Args:
        index (int): Option number in the menu.
        key (str): Option key, e.g. 'method'.
        value: Current value of the option.
        extra (str|None): Extra info to display after value (optional).
    """
    desc = OPTION_DESCRIPTIONS.get(key, '')
    extra_str = f" {extra}" if extra else ''
    print(f"{index}. {desc}: {value}{extra_str}")


def get_validated_input(prompt: str, default: Optional[Any] = None, validator: Optional[Callable[[Any], bool]] = None) -> Any:
    """
    Prompt user for input, applying a validator and supporting defaults.
    Args:
        prompt (str): Prompt to display.
        default: Default value if user enters nothing.
        validator (callable|None): Function to validate input. Should return True for valid.
    Returns:
        User input (possibly default), validated.
    """
    while True:
        val = input(f"{prompt} " + (f"[default: {default}] " if default else ""))
        if not val and default is not None:
            return default
        if validator:
            try:
                if validator(val):
                    return val
            except Exception:
                pass
            print("Invalid input. Please try again.")
        else:
            return val
