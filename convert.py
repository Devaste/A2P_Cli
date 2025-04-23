import pillow_avif  # noqa: F401
from pathlib import Path
from PIL import Image

def is_greyscale(img):
    """Check if a PIL Image is greyscale."""
    if img.mode in ("L", "LA"):
        return True
    if img.mode in ("RGB", "RGBA"):
        rgb = img.convert("RGB")
        bands = rgb.split()
        return all(bands[0].tobytes() == bands[i].tobytes() for i in range(1, 3))
    return False

def quantize_4bit_gui(img):
    """Quantize a greyscale image to 16 colors using PIL's quantize (GUI logic)."""
    return img.convert("L").quantize(colors=16, method=2, dither=0)

def find_avif_files(input_path, recursive):
    """Find all .avif files in a directory, optionally recursively."""
    pattern = '**/*.avif' if recursive else '*.avif'
    return list(input_path.glob(pattern))

def quantize_and_save(img, png_file, colors, mode, silent, label):
    img_q = img.convert(mode).quantize(colors=colors, method=2, dither=0)
    img_q.save(png_file, 'PNG', optimize=True)
    if not silent:
        print(f"[{label}] Converted: {png_file.name}")

def save_image(img, png_file, silent, label):
    img.save(png_file, 'PNG', optimize=True)
    if not silent:
        print(f"[{label}] Converted: {png_file.name}")


def convert_single_image(avif_file, png_file, silent, qb_color=None, qb_gray_color=None, qb_gray=None):
    """Convert a single AVIF file to PNG, using quantization flags if provided."""
    try:
        with Image.open(avif_file) as img:
            if is_greyscale(img):
                if qb_gray is not None:
                    quantize_and_save(img, png_file, 2**qb_gray, "L", silent, f"GREYSCALE {2**qb_gray} levels")
                    return True
                if qb_gray_color is not None:
                    quantize_and_save(img, png_file, 2**qb_gray_color, "L", silent, f"GREYSCALE+ONE {2**qb_gray_color} levels")
                    return True
                img_4bit = quantize_4bit_gui(img)
                img_4bit.save(png_file, 'PNG', optimize=True)
                if not silent:
                    print(f"[GREYSCALE 4bit GUI] Converted: {png_file.name}")
                return True
            # Color image
            if qb_color is not None:
                quantize_and_save(img, png_file, 2**qb_color, "RGB", silent, f"COLOR {2**qb_color} colors")
                return True
            save_image(img, png_file, silent, "COLOR")
            return True
    except Exception as e:
        if not silent:
            print(f"Failed to convert {avif_file.name}: {e}")
        return False

def print_summary(success, fail, silent):
    """Print a summary of the conversion results."""
    msg = f"Done: {success} converted, {fail} failed." if silent else f"Conversion finished. Success: {success}, Failed: {fail}"
    print(msg)

def remove_original_file(avif_file):
    """Remove the original AVIF file after conversion."""
    avif_file.unlink()

def convert_avif_to_png(input_dir, output_dir=None, replace=False, recursive=False, silent=False, qb_color=None, qb_gray_color=None, qb_gray=None):
    """
    Convert all .avif images in a directory (optionally recursively) to .png format.
    Greyscale images are quantized to 16 levels using GUI-style logic by default.
    Supports custom quantization via CLI flags.
    Optionally deletes originals, supports custom output dir and silent mode.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    if not input_path.is_dir():
        print(f"Input directory '{input_dir}' does not exist.")
        return
    output_path.mkdir(parents=True, exist_ok=True)
    avif_files = find_avif_files(input_path, recursive)
    if not avif_files:
        print("No .avif files found in the input directory.")
        return
    success = 0
    fail = 0
    for avif_file in avif_files:
        if recursive:
            png_file = avif_file.parent / (avif_file.stem + '.png')
        else:
            png_file = output_path / (avif_file.stem + '.png')
        converted = convert_single_image(avif_file, png_file, silent, qb_color=qb_color, qb_gray_color=qb_gray_color, qb_gray=qb_gray)
        if converted:
            if replace:
                remove_original_file(avif_file)
            success += 1
        else:
            fail += 1
    print_summary(success, fail, silent)