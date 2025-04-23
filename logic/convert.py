try:
    import pillow_avif  # noqa: F401
except ImportError:
    pillow_avif = None  # For environments without AVIF support

from pathlib import Path
from PIL import Image
import math

def is_greyscale(img):
    """Check if a PIL Image is greyscale."""
    if img.mode in ("L", "LA"):
        return True
    if img.mode in ("RGB", "RGBA"):
        rgb = img.convert("RGB")
        bands = rgb.split()
        return all(bands[0].tobytes() == bands[i].tobytes() for i in range(1, 3))
    return False

def get_real_bit_count(img):
    """Return the number of unique colors (palette or RGB), and bit count."""
    if img.mode == "P":
        colors = img.getcolors(maxcolors=256)
        n_colors = len(colors) if colors else 0
    else:
        colors = img.convert("RGB").getcolors(maxcolors=2**24)
        n_colors = len(colors) if colors else 0
    if n_colors > 0:
        bit_count = math.ceil(math.log2(n_colors))
    else:
        bit_count = 0
    return n_colors, bit_count

def quantize_4bit_gui(img):
    """Quantize a greyscale image to 16 colors using PIL's quantize (GUI logic)."""
    return img.convert("L").quantize(colors=16, method=2, dither=1)

def find_avif_files(input_path, recursive):
    """Find all .avif files in a directory, optionally recursively."""
    pattern = '**/*.avif' if recursive else '*.avif'
    return list(input_path.glob(pattern))

def quantize_and_save(img, png_file, colors: int, mode: str, silent: bool, label: str, **kwargs):
    method = int(kwargs.pop('method', 2))
    dither = int(kwargs.pop('dither', 1))
    if kwargs:
        print(f"Warning: Unexpected keyword arguments received: {', '.join(kwargs.keys())}")
    img_q = img.convert(mode).quantize(colors=int(colors), method=method, dither=dither)
    img_q.save(png_file, 'PNG', optimize=True)
    if not silent:
        print(f"[{label}] Converted: {png_file.name}")

def save_image(img, png_file, silent, label):
    img.save(png_file, 'PNG', optimize=True)
    if not silent:
        print(f"[{label}] Converted: {png_file.name}")


def convert_single_image(avif_file, png_file, silent, chk_bit=False, **kwargs):
    """
    Convert a single AVIF file to PNG, using quantization flags if provided.
    Quantization bitness is limited to 1–8 (2–256 colors/levels) due to PIL's quantize() and PNG palette limitations.
    See PIL.Image.quantize documentation: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize
    """
    qb_color = kwargs.pop('qb_color', None)
    qb_gray_color = kwargs.pop('qb_gray_color', None)
    qb_gray = kwargs.pop('qb_gray', None)
    method = kwargs.pop('method', 2)
    dither = kwargs.pop('dither', 1)

    if kwargs:
        unexpected = ', '.join(kwargs.keys())
        print(f"Warning: Unexpected keyword arguments received: {unexpected}")

    for flag, value in [('qb_color', qb_color), ('qb_gray_color', qb_gray_color), ('qb_gray', qb_gray)]:
        if value is not None and (value < 1 or value > 8):
            print(f"Error: {flag} must be between 1 and 8 (got {value}). This is due to PNG and PIL quantize() limitations.")
            print("See: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize")
            return False

    try:
        with Image.open(avif_file) as img:
            if is_greyscale(img):
                if qb_gray is not None:
                    quantize_and_save(img, png_file, int(2**qb_gray), "L", silent, f"GREYSCALE {2**qb_gray} levels", method=method, dither=dither)
                    if chk_bit:
                        with Image.open(png_file) as out_img:
                            n_colors, bit_count = get_real_bit_count(out_img)
                            print(f"[CHK_BIT] {png_file.name}: {n_colors} colors, ~{bit_count} bits")
                    return True
                if qb_gray_color is not None:
                    quantize_and_save(img, png_file, int(2**qb_gray_color), "L", silent, f"GREYSCALE+ONE {2**qb_gray_color} levels", method=method, dither=dither)
                    if chk_bit:
                        with Image.open(png_file) as out_img:
                            n_colors, bit_count = get_real_bit_count(out_img)
                            print(f"[CHK_BIT] {png_file.name}: {n_colors} colors, ~{bit_count} bits")
                    return True
                img_4bit = quantize_4bit_gui(img)
                img_4bit.save(png_file, 'PNG', optimize=True)
                if not silent:
                    print(f"[GREYSCALE 4bit GUI] Converted: {png_file.name}")
                if chk_bit:
                    with Image.open(png_file) as out_img:
                        n_colors, bit_count = get_real_bit_count(out_img)
                        print(f"[CHK_BIT] {png_file.name}: {n_colors} colors, ~{bit_count} bits")
                return True
            # Color image
            if qb_color is not None:
                quantize_and_save(img, png_file, int(2**qb_color), "RGB", silent, f"COLOR {2**qb_color} colors", method=method, dither=dither)
                if chk_bit:
                    with Image.open(png_file) as out_img:
                        n_colors, bit_count = get_real_bit_count(out_img)
                        print(f"[CHK_BIT] {png_file.name}: {n_colors} colors, ~{bit_count} bits")
                return True
            save_image(img, png_file, silent, "COLOR")
            if chk_bit:
                with Image.open(png_file) as out_img:
                    n_colors, bit_count = get_real_bit_count(out_img)
                    print(f"[CHK_BIT] {png_file.name}: {n_colors} colors, ~{bit_count} bits")
            return True
    except Exception as e:
        if not silent:
            print(f"Failed to convert {avif_file.name}: {e}")
        return False

def handle_single_conversion(avif_file, output_path, recursive, silent, replace, qb_color, qb_gray_color, qb_gray):
    png_file = (avif_file.parent if recursive else output_path) / (avif_file.stem + '.png')
    converted = convert_single_image(avif_file, png_file, silent, qb_color=qb_color, qb_gray_color=qb_gray_color, qb_gray=qb_gray)
    if converted and replace:
        remove_original_file(avif_file)
    return converted


def convert_avif_to_png(input_dir, output_dir=None, replace=False, recursive=False, silent=False, qb_color=None, qb_gray_color=None, qb_gray=None, **kwargs):
    """
    Convert all .avif images in a directory (optionally recursively) to .png format.
    Greyscale images are quantized to 16 levels by default.
    Supports custom quantization via CLI flags.
    Optionally deletes originals, supports custom output dir and silent mode.
    Accepts extra kwargs (e.g., method, dither) for advanced options.
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist.")
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)
    avif_files = find_avif_files(input_path, recursive)
    if not avif_files:
        print("No .avif files found in the input directory.")
        return
    success = 0
    fail = 0
    for avif_file in avif_files:
        if recursive:
            rel_path = avif_file.parent.relative_to(input_path)
            target_dir = output_path / rel_path
            target_dir.mkdir(parents=True, exist_ok=True)
            png_file = target_dir / (avif_file.stem + '.png')
        else:
            png_file = output_path / (avif_file.stem + '.png')
        converted = convert_single_image(avif_file, png_file, silent, qb_color=qb_color, qb_gray_color=qb_gray_color, qb_gray=qb_gray, **kwargs)
        if converted:
            if replace:
                remove_original_file(avif_file)
            success += 1
        else:
            fail += 1
    print_summary(success, fail, silent)

def print_summary(success, fail, silent):
    """Print a summary of the conversion results."""
    msg = f"Done: {success} converted, {fail} failed." if silent else f"Conversion finished. Success: {success}, Failed: {fail}"
    print(msg)

def remove_original_file(avif_file):
    """Remove the original AVIF file after conversion."""
    avif_file.unlink()

def check_and_prepare_dirs(input_path, output_path):
    if not input_path.is_dir():
        print(f"Input directory '{input_path}' does not exist.")
        return False
    output_path.mkdir(parents=True, exist_ok=True)
    return True
