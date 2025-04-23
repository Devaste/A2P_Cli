import pytest
from unittest.mock import patch, mock_open
from logic import update_check

def test_no_update(monkeypatch, capsys):
    monkeypatch.setattr(update_check, "get_local_version", lambda: "1.0")
    monkeypatch.setattr(update_check, "get_latest_version", lambda: "1.0")
    update_check.check_for_update()
    out = capsys.readouterr().out
    assert out == ""

def test_update_available(monkeypatch, capsys):
    monkeypatch.setattr(update_check, "get_local_version", lambda: "1.0")
    monkeypatch.setattr(update_check, "get_latest_version", lambda: "1.1")
    update_check.check_for_update()
    out = capsys.readouterr().out
    assert "Update available: 1.1" in out
    assert "You have 1.0" in out

def test_update_check_fails(monkeypatch, capsys):
    monkeypatch.setattr(update_check, "get_local_version", lambda: None)
    monkeypatch.setattr(update_check, "get_latest_version", lambda: None)
    update_check.check_for_update()
    out = capsys.readouterr().out
    assert out == ""

def test_get_local_version_reads_file():
    with patch("builtins.open", mock_open(read_data="1.2\n")):
        assert update_check.get_local_version() == "1.2"

def test_get_local_version_exception(monkeypatch):
    def raise_ioerror(*a, **kw):
        raise IOError("fail")
    monkeypatch.setattr("builtins.open", raise_ioerror)
    assert update_check.get_local_version() is None

def test_get_latest_version_reads_response(monkeypatch):
    class FakeResp:
        ok = True
        text = "2.0\n"
    monkeypatch.setattr(update_check.requests, "get", lambda *a, **kw: FakeResp())
    assert update_check.get_latest_version() == "2.0"

def test_get_latest_version_exception(monkeypatch):
    def raise_exc(*a, **kw):
        raise Exception("fail")
    monkeypatch.setattr(update_check.requests, "get", raise_exc)
    assert update_check.get_latest_version() is None

def test_get_latest_version_non_ok(monkeypatch):
    class FakeResp:
        ok = False
        text = ""
    monkeypatch.setattr(update_check.requests, "get", lambda *a, **kw: FakeResp())
    assert update_check.get_latest_version() is None
