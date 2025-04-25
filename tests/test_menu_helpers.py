from cli.menu_utils import print_option, get_validated_input
from cli.config import OPTION_DESCRIPTIONS
import builtins
import pytest

# For print_option, we will just check it runs without error (visual test)
def test_print_option_runs(capsys):
    print_option(1, 'input_dir', '/some/path')
    print_option(9, 'method', '2 (Fast Octree)')
    out = capsys.readouterr().out
    assert OPTION_DESCRIPTIONS['input_dir'] in out
    assert OPTION_DESCRIPTIONS['method'] in out

# For get_validated_input, we will mock input and test validation
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

def test_get_validated_input_validator_exception(monkeypatch, capsys):
    # Validator will raise an exception on first input, then accept on second
    responses = iter(['fail', 'ok'])
    def bad_validator(val):
        if val == 'fail':
            raise ValueError('fail')
        return val == 'ok'
    monkeypatch.setattr('builtins.input', lambda prompt: next(responses))
    result = get_validated_input('Prompt', default='foo', validator=bad_validator)
    assert result == 'ok'
    out = capsys.readouterr().out
    assert 'Invalid input. Please try again.' in out

def test_get_validated_input_return_val(monkeypatch):
    # Covers the 'else' branch at the end of get_validated_input
    monkeypatch.setattr('builtins.input', lambda prompt: 'direct')
    assert get_validated_input('Prompt', validator=None) == 'direct'
