import pytest
from logic.convert import get_real_bit_count
from PIL import Image
import numpy as np
import tempfile

@pytest.mark.parametrize("mode,colors,expected_bits", [
    ("RGB", 2, 1),
    ("RGB", 16, 4),
    ("RGB", 128, 7),
    ("RGB", 256, 8),
    ("L", 8, 3),
])
def test_get_real_bit_count(mode, colors, expected_bits):
    arr = np.linspace(0, 255, colors, dtype=np.uint8)
    if mode == "RGB":
        arr = np.stack([arr, arr, arr], axis=-1)
        arr = np.tile(arr, (16, 1, 1))
    else:
        arr = np.tile(arr, (16, 1))
    img = Image.fromarray(arr, mode)
    n_colors, bit_count = get_real_bit_count(img)
    assert n_colors == colors
    assert bit_count == expected_bits


def test_chk_bit_on_palette(tmp_path):
    # Create a palette PNG with 4 colors
    img = Image.new("P", (10, 10))
    img.putpalette([0,0,0, 64,64,64, 128,128,128, 255,255,255] + [0]*252*3)
    for i in range(4):
        img.paste(i, (i*2, 0, (i+1)*2, 10))
    file = tmp_path / "pal.png"
    img.save(file)
    with Image.open(file) as im:
        n_colors, bit_count = get_real_bit_count(im)
        assert n_colors == 4
        assert bit_count == 2
