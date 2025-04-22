import os
import shutil
import tempfile
from pathlib import Path
from convert import convert_avif_to_png
from PIL import Image
import pytest

def create_dummy_avif(path, mode="RGB", color=(128, 128, 128)):
    img = Image.new(mode, (32, 32), color)
    img.save(path, "PNG")  # Use PNG for test, as Pillow may not write AVIF
    # Rename to .avif for simulation
    avif_path = Path(str(path).replace('.png', '.avif'))
    os.rename(path, avif_path)
    return avif_path

def test_basic_conversion():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        output_dir = Path(tmpdir) / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        avif_file = create_dummy_avif(input_dir / "test001.avif")
        convert_avif_to_png(str(input_dir), str(output_dir), replace=False, recursive=False, silent=True)
        png_file = output_dir / "test001.png"
        assert png_file.exists(), "PNG file was not created"

def test_replace_original():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir)
        avif_file = create_dummy_avif(input_dir / "replace001.avif")
        convert_avif_to_png(str(input_dir), None, replace=True, recursive=False, silent=True)
        png_file = input_dir / "replace001.png"
        assert png_file.exists(), "PNG file was not created"
        assert not (input_dir / "replace001.avif").exists(), "Original AVIF file was not deleted"

def test_recursive():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub = root / "subdir"
        sub.mkdir()
        avif_file = create_dummy_avif(sub / "rec001.avif")
        convert_avif_to_png(str(root), None, replace=False, recursive=True, silent=True)
        png_file = sub / "rec001.png"
        assert png_file.exists(), "PNG file in subdir was not created"
