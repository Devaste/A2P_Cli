from cli.menu_helpers import print_option, get_validated_input
from cli.config import OPTION_DESCRIPTIONS

# For print_option, we will just check it runs without error (visual test)
def test_print_option_runs(capsys):
    print_option(1, 'input_dir', '/some/path')
    print_option(9, 'method', '2 (Fast Octree)')
    out = capsys.readouterr().out
    assert OPTION_DESCRIPTIONS['input_dir'] in out
    assert OPTION_DESCRIPTIONS['method'] in out

# For get_validated_input, we will mock input and test validation
import builtins
import pytest

def test_get_validated_input_accepts_default(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda prompt: '')
    assert get_validated_input('Prompt', default='foo') == 'foo'

def test_get_validated_input_valid(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda prompt: 'bar')
    assert get_validated_input('Prompt', default='foo', validator=lambda v: v == 'bar') == 'bar'

def test_get_validated_input_invalid_then_valid(monkeypatch):
    responses = iter(['bad', 'baz'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(responses))
    # Only 'baz' is valid
    assert get_validated_input('Prompt', default='foo', validator=lambda v: v == 'baz') == 'baz'
