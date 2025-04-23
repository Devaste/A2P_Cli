import tempfile
from pathlib import Path
from PIL import Image
import pytest
from logic.convert import is_greyscale, quantize_and_save, save_image, check_and_prepare_dirs, handle_single_conversion, convert_single_image


def test_quantize_and_save_unexpected_kwarg_first(tmp_path, capsys):
    img = Image.new('L', (8, 8), 128)
    png_file = tmp_path / 'unexpected_first.png'
    quantize_and_save(img, png_file, 2, 'L', True, 'LABEL', foo='bar')
    out = capsys.readouterr().out
    assert 'Warning: Unexpected keyword arguments received: foo' in out
    assert png_file.exists()


def test_is_greyscale_modes():
    img_l = Image.new('L', (2, 2), 1)
    img_rgb = Image.new('RGB', (2, 2), (1, 1, 1))
    img_rgba = Image.new('RGBA', (2, 2), (1, 1, 1, 255))
    img_p = Image.new('P', (2, 2))  # Palette mode, should return False
    assert is_greyscale(img_l) is True
    assert is_greyscale(img_rgb) is True
    assert is_greyscale(img_rgba) is True
    assert is_greyscale(img_p) is False

def test_quantize_and_save_warns_unexpected_kwargs(tmp_path, capsys):
    img = Image.new('RGB', (8, 8), (1, 2, 3))
    png_file = tmp_path / 'out.png'
    quantize_and_save(img, png_file, 8, 'RGB', True, 'LABEL', unexpected_kwarg=123)
    out = capsys.readouterr().out
    assert 'Warning: Unexpected keyword arguments received' in out
    assert png_file.exists()

def test_save_image_prints(capsys, tmp_path):
    img = Image.new('RGB', (2, 2), (1, 2, 3))
    png_file = tmp_path / 'out2.png'
    save_image(img, png_file, False, 'LABEL')
    out = capsys.readouterr().out
    assert '[LABEL] Converted' in out
    assert png_file.exists()

def test_handle_single_conversion_replace(tmp_path):
    img = Image.new('RGB', (2, 2), (1, 2, 3))
    avif_file = tmp_path / 'dummy.avif'
    img.save(avif_file, 'PNG')
    output_path = tmp_path
    # Should convert and remove original
    converted = handle_single_conversion(avif_file, output_path, False, True, True, 2, None, None)
    assert converted is True
    assert not avif_file.exists()

def test_handle_single_conversion_no_replace(tmp_path):
    img = Image.new('RGB', (2, 2), (1, 2, 3))
    avif_file = tmp_path / 'dummy2.avif'
    img.save(avif_file, 'PNG')
    output_path = tmp_path
    converted = handle_single_conversion(avif_file, output_path, False, True, False, 2, None, None)
    assert converted is True
    assert avif_file.exists()

def test_check_and_prepare_dirs(tmp_path, capsys):
    input_path = tmp_path / 'in'
    output_path = tmp_path / 'out'
    # input_path does not exist
    result = check_and_prepare_dirs(input_path, output_path)
    out = capsys.readouterr().out
    assert not result
    assert 'does not exist' in out
    # input_path exists
    input_path.mkdir()
    result2 = check_and_prepare_dirs(input_path, output_path)
    assert result2
    assert output_path.exists()

def test_convert_single_image_color_quant(tmp_path):
    img = Image.new('RGB', (8, 8), (10, 20, 30))
    avif_file = tmp_path / 'color.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'color.png'
    result = convert_single_image(avif_file, png_file, True, qb_color=3)
    assert result is True
    assert png_file.exists()

def test_convert_single_image_invalid_bitness(tmp_path, capsys):
    img = Image.new('RGB', (8, 8), (10, 20, 30))
    avif_file = tmp_path / 'bad_bitness.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'bad_bitness.png'
    result = convert_single_image(avif_file, png_file, True, qb_color=0)
    out = capsys.readouterr().out
    assert result is False
    assert 'must be between 1 and 8' in out

def test_convert_single_image_exception(tmp_path, capsys):
    # Pass a text file to cause an exception
    bad_file = tmp_path / 'not_img.avif'
    bad_file.write_text('not an image')
    png_file = tmp_path / 'bad.png'
    result = convert_single_image(bad_file, png_file, False)
    out = capsys.readouterr().out
    assert result is False
    assert 'Failed to convert' in out

def test_quantize_and_save_exit(tmp_path):
    from logic.convert import quantize_and_save
    img = Image.new('RGB', (8, 8), (1, 2, 3))
    png_file = tmp_path / 'exit.png'
    quantize_and_save(img, png_file, 2, 'RGB', True, 'LABEL')
    assert png_file.exists()

def test_convert_single_image_invalid_gray_flags(tmp_path, capsys):
    img = Image.new('L', (8, 8), 128)
    avif_file = tmp_path / 'bad_gray.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'bad_gray.png'
    for flag in ['qb_gray', 'qb_gray_color']:
        kwargs = {flag: 0}
        result = convert_single_image(avif_file, png_file, True, **kwargs)
        out = capsys.readouterr().out
        assert result is False
        assert 'must be between 1 and 8' in out

def test_convert_single_image_greyscale_4bit(tmp_path, capsys):
    img = Image.new('L', (8, 8), 128)
    avif_file = tmp_path / 'gray4bit.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'gray4bit.png'
    result = convert_single_image(avif_file, png_file, False)
    out = capsys.readouterr().out
    assert result is True
    assert "[GREYSCALE 4bit GUI] Converted" in out
    assert png_file.exists()

def test_convert_single_image_exception_silent(tmp_path):
    bad_file = tmp_path / 'not_img2.avif'
    bad_file.write_text('not an image')
    png_file = tmp_path / 'bad2.png'
    result = convert_single_image(bad_file, png_file, True)
    assert result is False

def test_convert_single_image_invalid_qb_gray(tmp_path, capsys):
    img = Image.new('L', (8, 8), 128)
    avif_file = tmp_path / 'bad_gray2.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'bad_gray2.png'
    result = convert_single_image(avif_file, png_file, True, qb_gray=0)
    out = capsys.readouterr().out
    assert result is False
    assert 'must be between 1 and 8' in out

def test_convert_single_image_invalid_qb_gray_color(tmp_path, capsys):
    img = Image.new('L', (8, 8), 128)
    avif_file = tmp_path / 'bad_gray_color2.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'bad_gray_color2.png'
    result = convert_single_image(avif_file, png_file, True, qb_gray_color=0)
    out = capsys.readouterr().out
    assert result is False
    assert 'must be between 1 and 8' in out

def test_convert_single_image_exception_only_return(tmp_path):
    # Covers the except block with silent=True (no print, just return False)
    bad_file = tmp_path / 'not_img3.avif'
    bad_file.write_text('not an image')
    png_file = tmp_path / 'bad3.png'
    result = convert_single_image(bad_file, png_file, True)
    assert result is False

def test_quantize_and_save_exit_coverage(tmp_path):
    # This ensures the function exit at line 37 is covered.
    img = Image.new('RGB', (8, 8), (1, 2, 3))
    png_file = tmp_path / 'exit2.png'
    quantize_and_save(img, png_file, 2, 'RGB', True, 'LABEL')
    assert png_file.exists()

def test_convert_single_image_invalid_bitness_upper(tmp_path, capsys):
    img = Image.new('RGB', (8, 8), (10, 20, 30))
    avif_file = tmp_path / 'bad_bitness2.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'bad_bitness2.png'
    # Test for qb_color, qb_gray, qb_gray_color all > 8
    for flag in ['qb_color', 'qb_gray', 'qb_gray_color']:
        kwargs = {flag: 9}
        result = convert_single_image(avif_file, png_file, True, **kwargs)
        out = capsys.readouterr().out
        assert result is False
        assert 'must be between 1 and 8' in out
        assert 'https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize' in out

def test_convert_single_image_exception_print(tmp_path, capsys):
    # Triggers the exception handler with silent=False (should print)
    bad_file = tmp_path / 'not_img4.avif'
    bad_file.write_text('not an image')
    png_file = tmp_path / 'bad4.png'
    result = convert_single_image(bad_file, png_file, False)
    out = capsys.readouterr().out
    assert result is False
    assert 'Failed to convert' in out

def test_quantize_and_save_print_and_unexpected(tmp_path, capsys):
    img = Image.new('RGB', (8, 8), (1, 2, 3))
    png_file = tmp_path / 'print.png'
    quantize_and_save(img, png_file, 2, 'RGB', False, 'LABEL', foo='bar')
    out = capsys.readouterr().out
    assert 'Converted: print.png' in out
    assert 'Warning: Unexpected keyword arguments received: foo' in out
    assert png_file.exists()

def test_convert_single_image_color_save_image(tmp_path, capsys):
    img = Image.new('RGB', (8, 8), (10, 20, 30))
    avif_file = tmp_path / 'color2.avif'
    img.save(avif_file, 'PNG')
    png_file = tmp_path / 'color2.png'
    # Test silent=False
    result = convert_single_image(avif_file, png_file, False)
    out = capsys.readouterr().out
    assert result is True
    assert '[COLOR] Converted' in out
    assert png_file.exists()
    # Test silent=True
    png_file2 = tmp_path / 'color3.png'
    result2 = convert_single_image(avif_file, png_file2, True)
    assert result2 is True
    assert png_file2.exists()

def test_quantize_and_save_unexpected_kwarg_branch(tmp_path, capsys):
    img = Image.new('L', (8, 8), 128)  # Greyscale image, mode 'L'
    png_file = tmp_path / 'unexpected.png'
    # Use mode 'L' and colors=2 to ensure quantize works and no Pillow error
    quantize_and_save(img, png_file, 2, 'L', True, 'LABEL', foo='bar')
    out = capsys.readouterr().out
    assert 'Warning: Unexpected keyword arguments received: foo' in out
    assert png_file.exists()
