import argparse
import pillow_avif  # noqa: F401
from pathlib import Path
from PIL import Image
import numpy as np
import re

def extract_numbers_from_filename(filename):
    """
    Extract all numbers or ranges from filename.
    E.g. '098-099' -> [98, 99], '097' -> [97], '100-102' -> [100, 101, 102]
    """
    name = filename.rsplit('.', 1)[0]
    # Find all number groups or ranges
    matches = re.findall(r'(\d+)(?:-(\d+))?', name)
    numbers = []
    for start, end in matches:
        if end:
            # Range: add all numbers in range
            numbers.extend(list(range(int(start), int(end) + 1)))
        else:
            numbers.append(int(start))
    return numbers

def parse_manga_structure(avif_file):
    """
    Given a Path to an avif_file, extract manga name, volume, chapter.
    Assumes folder structure: manga/volume/chapter/file
    """
    parts = avif_file.parts
    # Expect at least 4 levels: .../<manga>/<volume>/<chapter>/<file>
    if len(parts) < 4:
        return None, None, None
    manga = parts[-4]
    volume = parts[-3]
    chapter = parts[-2]
    return manga, volume, chapter

def is_greyscale(img):
    """Check if a PIL Image is greyscale."""
    if img.mode in ("L", "LA"):
        return True
    if img.mode in ("RGB", "RGBA"):
        rgb = img.convert("RGB")
        bands = rgb.split()
        return all(bands[0].tobytes() == bands[i].tobytes() for i in range(1, 3))
    return False

def is_greyscale_plus_one_color(img, tolerance=5, min_color_pixels=0.01):
    """
    Check if the image is mostly greyscale with a single dominant color (e.g., blue or red highlights).
    Returns (True, color) if so, else (False, None).
    """
    rgb = img.convert("RGB")
    arr = np.array(rgb)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    greyscale_mask = (np.abs(r-g) < tolerance) & (np.abs(r-b) < tolerance) & (np.abs(g-b) < tolerance)
    total_pixels = arr.shape[0] * arr.shape[1]
    color_pixels = total_pixels - np.sum(greyscale_mask)
    if color_pixels / total_pixels < min_color_pixels:
        return False, None  # Nearly all greyscale
    color_arr = arr[~greyscale_mask]
    if len(color_arr) == 0:
        return False, None
    # Find dominant color channel
    color_sums = np.sum(color_arr, axis=0)
    dominant = np.argmax(color_sums)
    color_map = {0: "red", 1: "green", 2: "blue"}
    return True, color_map[dominant]

def quantize_4bit(img):
    """Quantize a greyscale image to 16 levels (4 bits)."""
    grey = img.convert("L")
    return grey.point(lambda x: int(x / 16) * 16)

def quantize_4bit_gui(img):
    """Quantize a greyscale image to 16 colors using PIL's quantize (GUI logic)."""
    return img.convert("L").quantize(colors=16, method=2, dither=0)

def find_avif_files(input_path, recursive):
    """Find all .avif files in a directory, optionally recursively."""
    pattern = '**/*.avif' if recursive else '*.avif'
    return list(input_path.glob(pattern))

def convert_single_image(avif_file, png_file, silent):
    """
    Convert a single AVIF file to PNG.
    - Greyscale images: quantize to 16 levels (GUI logic).
    - Greyscale+one-color: treat as color, print detected color if not silent.
    - Full color: save as PNG.
    """
    try:
        with Image.open(avif_file) as img:
            if is_greyscale(img):
                img_4bit = quantize_4bit_gui(img)
                img_4bit.save(png_file, 'PNG', optimize=True)
                if not silent:
                    print(f"[GREYSCALE 4bit GUI] Converted: {avif_file.name} -> {png_file.name}")
            else:
                is_gs_plus_one, color = is_greyscale_plus_one_color(img)
                if is_gs_plus_one:
                    img.save(png_file, 'PNG', optimize=True)
                    if not silent:
                        print(f"[GREYSCALE+{color.upper()}] Converted: {avif_file.name} -> {png_file.name}")
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
    In recursive mode, outputs are saved to the same folder as their source files.
    Implements automatic renaming based on folder structure and file number or range.
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
    # --- Automatic naming logic with ranges ---
    file_info = []
    for avif_file in avif_files:
        manga, volume, chapter = parse_manga_structure(avif_file)
        numbers = extract_numbers_from_filename(avif_file.stem)
        for num in numbers:
            file_info.append((num, avif_file, manga, volume, chapter))
    # Sort by number (ascending)
    file_info = [f for f in file_info if f[0] is not None]
    file_info.sort(key=lambda x: x[0])
    success = 0
    fail = 0
    for idx, (num, avif_file, manga, volume, chapter) in enumerate(file_info):
        manga_str = manga or "manga"
        volume_str = str(volume).zfill(3) if volume else "000"
        chapter_str = str(chapter).zfill(3) if chapter else "000"
        file_str = str(num).zfill(3)
        new_name = f"{manga_str}-v{volume_str}-ch{chapter_str}-{file_str}.png"
        if recursive:
            png_file = avif_file.parent / new_name
        else:
            png_file = output_path / new_name
        converted = convert_single_image(avif_file, png_file, silent)
        if converted:
            if replace:
                remove_original_file(avif_file)
            success += 1
        else:
            fail += 1
    print_summary(success, fail, silent)

def main():
    """Parse command-line arguments and run the AVIF to PNG conversion."""
    parser = argparse.ArgumentParser(description="Convert all .avif images in a directory to .png format.")
    parser.add_argument('input_dir', help="Directory containing .avif files")
    parser.add_argument('--output_dir', help="Directory to save .png files (default: same as input_dir)")
    parser.add_argument('--replace', action='store_true', help='Remove original .avif files after conversion')
    parser.add_argument('--recursive', action='store_true', help='Recursively search for .avif files in subdirectories')
    parser.add_argument('--silent', action='store_true', help='No output to command line, only finishing result')
    args = parser.parse_args()
    convert_avif_to_png(
        args.input_dir,
        args.output_dir,
        replace=args.replace,
        recursive=args.recursive,
        silent=args.silent
    )

if __name__ == '__main__':
    main()