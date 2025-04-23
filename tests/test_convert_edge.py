import os
import tempfile
from pathlib import Path
import pytest
from logic.convert import convert_avif_to_png
from PIL import Image

def test_no_avif_files(tmp_path):
    # Directory with no .avif files should do nothing (no error, no output)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    convert_avif_to_png(str(tmp_path), str(output_dir), silent=True)
    assert not any(output_dir.iterdir()), "Output dir should be empty if no avif files present"

def test_corrupted_avif_file(tmp_path):
    # Simulate a corrupted .avif (actually just a text file)
    bad_file = tmp_path / "bad.avif"
    bad_file.write_text("not an image")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    # Should not raise, just skip or log error
    convert_avif_to_png(str(tmp_path), str(output_dir), silent=True)
    assert not any(output_dir.iterdir()), "No PNG should be created for corrupted AVIF"

def test_invalid_input_dir():
    # Should raise FileNotFoundError or similar
    with pytest.raises(Exception):
        convert_avif_to_png("nonexistent_dir_xyz", None, silent=True)
