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

def convert_single_image(avif_file, png_file, silent):
    """Convert a single AVIF file to PNG, using GUI-style quantization for greyscale images."""
    try:
        with Image.open(avif_file) as img:
            if is_greyscale(img):
                img_4bit = quantize_4bit_gui(img)
                img_4bit.save(png_file, 'PNG', optimize=True)
                if not silent:
                    print(f"[GREYSCALE 4bit GUI] Converted: {avif_file.name} -> {png_file.name}")
            else:
                img.save(png_file, 'PNG', optimize=True)
                if not silent:
                    print(f"[COLOR] Converted: {avif_file.name} -> {png_file.name}")
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

def convert_avif_to_png(input_dir, output_dir=None, replace=False, recursive=False, silent=False):
    """
    Convert all .avif images in a directory (optionally recursively) to .png format.
    Greyscale images are quantized to 16 levels using GUI-style logic.
    Optionally deletes originals, supports custom output dir and silent mode.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    if not input_path.is_dir():
        if not silent:
            print(f"Input directory '{input_dir}' does not exist.")
        return
    output_path.mkdir(parents=True, exist_ok=True)
    avif_files = find_avif_files(input_path, recursive)
    if not avif_files:
        if not silent:
            print("No .avif files found in the input directory.")
        return
    success = 0
    fail = 0
    for avif_file in avif_files:
        png_file = output_path / (avif_file.stem + '.png')
        converted = convert_single_image(avif_file, png_file, silent)
        if converted:
            if replace:
                remove_original_file(avif_file)
            success += 1
        else:
            fail += 1
    print_summary(success, fail, silent)