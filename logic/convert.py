try:
    import pillow_avif  # noqa: F401
except ImportError:
    pillow_avif = None  # For environments without AVIF support

from pathlib import Path
from PIL import Image
import math
import logging
import traceback
import numpy as np
from logic.logging_config import log_call
from logic.config import DEFAULT_MAX_WORKERS
import concurrent.futures
import os
import time

GREYSCALE_ONE_LABEL = "GREYSCALE+ONE"
FULL_COLOR_LABEL = "FULL COLOR"

@log_call
def batch_files_by_size(avif_files, target_batch_size_bytes):
    batches = []
    current_batch = []
    current_size = 0
    for f in avif_files:
        size = os.path.getsize(f)
        if current_size + size > target_batch_size_bytes and current_batch:
            batches.append(list(current_batch))
            current_batch = []
            current_size = 0
        current_batch.append(f)
        current_size += size
    if current_batch:
        batches.append(current_batch)
    return batches

@log_call
def is_greyscale(img):
    """Check if a PIL Image is greyscale."""
    if img.mode in ("L", "LA"):
        return True
    if img.mode in ("RGB", "RGBA"):
        rgb = img.convert("RGB")
        bands = rgb.split()
        return all(bands[0].tobytes() == bands[i].tobytes() for i in range(1, 3))
    return False

@log_call
def get_real_bit_count(img):
    """Return the number of unique colors (palette or RGB), and "bit" count."""
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

@log_call
def quantize_4bit(img):
    """Quantize a greyscale image to 16 colors using PIL's quantize (4-bit)."""
    return img.convert("L").quantize(colors=16, method=2, dither=1)

@log_call
def find_avif_files(input_path, recursive):
    """Find all .avif files in a directory, optionally recursively."""
    pattern = '**/*.avif' if recursive else '*.avif'
    return list(input_path.glob(pattern))

@log_call
def quantize_and_save(img, png_file, colors: int, mode: str, silent: bool, label: str, progress_printer=None, **kwargs):
    method = int(kwargs.pop('method', 2))
    dither = int(kwargs.pop('dither', 1))
    if kwargs:
        logging.warning(f"Unexpected keyword arguments received: {', '.join(kwargs.keys())}")
    img_q = img.convert(mode).quantize(colors=int(colors), method=method, dither=dither)
    img_q.save(png_file, 'PNG', optimize=True)
    if not silent and progress_printer:
        progress_printer(f"[{label}] Converted: {png_file.name}")

@log_call
def save_image(img, png_file, silent, label, progress_printer=None):
    img.save(png_file, 'PNG', optimize=True)
    if not silent and progress_printer:
        progress_printer(f"[{label}] Converted: {png_file.name}")

@log_call
def classify_image_type(img):
    """Classify image as 'grayscale', 'grayscale+one', or 'color' using numpy."""
    arr = np.array(img.convert('RGBA'))
    r, g, b, _ = arr[...,0], arr[...,1], arr[...,2], arr[...,3]
    # Grayscale: all RGB channels are equal everywhere
    if np.all((r == g) & (g == b)):
        # Grayscale+one: check for a single unique color (besides gray)
        unique_colors = np.unique(arr[...,:3].reshape(-1, 3), axis=0)
        if unique_colors.shape[0] == 2:
            return 'grayscale+one'
        return 'grayscale'
    return 'color'

@log_call
def _quantize_if_requested(img, png_file, qb_val, mode, silent, label, progress_printer, method, dither):
    """Helper: quantize image if qb_val is valid, else save as-is."""
    if qb_val is not None and str(qb_val).strip() != "":
        try:
            bits = int(qb_val)
        except ValueError:
            bits = None
        if bits is not None and 1 <= bits <= 8:
            quant_colors = 2 ** bits
            quantize_and_save(img, png_file, quant_colors, mode, silent, label, progress_printer, method=method, dither=dither)
            return
    save_image(img, png_file, silent, label, progress_printer)

@log_call
def _print_chk_bit(png_file, progress_printer):
    try:
        with Image.open(png_file) as out_img:
            n_colors, bit_count = get_real_bit_count(out_img)
            chk_msg = f"[CHK_BIT] {png_file.name}: {n_colors} colors, ~{bit_count} bits"
            if progress_printer == print:
                print(chk_msg)
            else:
                logging.info(chk_msg)
    except (OSError, ValueError) as e:
        logging.error(f"CHK_BIT failed for {png_file}: {e}")

@log_call
def convert_single_image(avif_file, png_file, silent, chk_bit=False, progress_printer=None, **kwargs):
    try:
        qb_color = kwargs.pop('qb_color', None)
        qb_gray_color = kwargs.pop('qb_gray_color', None)
        qb_gray = kwargs.pop('qb_gray', None)
        method = kwargs.pop('method', 2)
        dither = kwargs.pop('dither', 1)

        if kwargs:
            unexpected = ', '.join(kwargs.keys())
            logging.warning(f"Unexpected keyword arguments: {unexpected}")

        with Image.open(avif_file) as img:
            img_type = classify_image_type(img)
            if img_type == 'grayscale+one':
                _quantize_if_requested(img, png_file, qb_gray_color, "P", silent, GREYSCALE_ONE_LABEL, progress_printer, method, dither)
            elif img_type == 'grayscale':
                _quantize_if_requested(img, png_file, qb_gray, "L", silent, "GREYSCALE", progress_printer, method, dither)
            else:  # color
                _quantize_if_requested(img, png_file, qb_color, "P", silent, FULL_COLOR_LABEL, progress_printer, method, dither)

            if chk_bit:
                _print_chk_bit(png_file, progress_printer)
            return True
    except Exception as e:
        logging.error(f"Exception in convert_single_image for {avif_file}: {e}\n{traceback.format_exc()}")
        return False

@log_call
def handle_single_conversion(avif_file, output_path, recursive, silent, remove, qb_color, qb_gray_color, qb_gray, progress_printer=None):
    png_file = (avif_file.parent if recursive else output_path) / (avif_file.stem + '.png')
    converted = convert_single_image(avif_file, png_file, silent, qb_color=qb_color, qb_gray_color=qb_gray_color, qb_gray=qb_gray, progress_printer=progress_printer)
    if converted and remove:
        try:
            remove_original_file(avif_file)
        except Exception as e:
            print(f"[WARN] Failed to remove {avif_file}: {e}")
    return converted

@log_call
def _resolve_png_file(avif_file, input_path, output_path, output_dir, recursive):
    if recursive and output_dir:
        rel_path = avif_file.parent.relative_to(input_path)
        target_folder = output_path / rel_path
        target_folder.mkdir(parents=True, exist_ok=True)
        return target_folder / (avif_file.stem + '.png')
    if recursive:
        return avif_file.parent / (avif_file.stem + '.png')
    if output_dir:
        return output_path / (avif_file.stem + '.png')
    return avif_file.parent / (avif_file.stem + '.png')

@log_call
def _remove_original_if_requested(avif_file, remove):
    if not remove:
        return
    try:
        remove_original_file(avif_file)
    except OSError as e:
        print(f"[WARN] Failed to remove {avif_file}: {e}")

@log_call
def convert_avif_to_png(input_dir, output_dir=None, remove=False, recursive=False, silent=False, qb_color=None, qb_gray_color=None, qb_gray=None, progress_callback=None, progress_printer=None, max_workers=DEFAULT_MAX_WORKERS, **kwargs):
    input_path = Path(input_dir)
    if not input_path.exists():
        logging.error(f"Input directory '{input_dir}' does not exist.")
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist.")
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)
    avif_files = find_avif_files(input_path, recursive)
    if not avif_files:
        logging.warning(f"No AVIF files found in '{input_dir}'.")
        return {"success": 0, "fail": 0}
    total = len(avif_files)
    results = [None] * total

    # Set batch size to 5 MB
    target_batch_size_bytes = 5 * 1024 * 1024

    # Sort files by size (largest first)
    avif_files = sorted(avif_files, key=lambda f: os.path.getsize(f), reverse=True)
    batches = batch_files_by_size(avif_files, target_batch_size_bytes)
    total = len(avif_files)
    progress_counter = [0]  # Mutable counter for progress reporting

    def convert_batch(batch):
        results = []
        for avif_file in batch:
            start = time.time()
            png_file = _resolve_png_file(avif_file, input_path, output_path, output_dir, recursive)
            converted = convert_single_image(
                avif_file, png_file, silent, progress_printer=progress_printer,
                qb_color=qb_color, qb_gray_color=qb_gray_color, qb_gray=qb_gray, **kwargs
            )
            if converted:
                _remove_original_if_requested(avif_file, remove)
            duration = time.time() - start
            logging.debug(f"Converted {avif_file} in {duration:.2f}s")
            if progress_callback:
                progress_counter[0] += 1
                progress_callback(progress_counter[0], total)
            results.append(converted)
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        batch_futures = [executor.submit(convert_batch, batch) for batch in batches]
        for future in concurrent.futures.as_completed(batch_futures):
            try:
                batch_results = future.result()
                # Fill the main results list in order
                # Option 1: If order doesn't matter, just extend
                # results.extend(batch_results)
                # Option 2: If you want to keep the original file order, you'll need to track which files were in each batch
                # For now, just extend:
                results.extend(batch_results)
            except Exception as exc:
                logging.error(f"Exception during batch conversion: {exc}\n{traceback.format_exc()}")

    success = sum(1 for r in results if r)
    fail = total - success
    return {"success": success, "fail": fail}

@log_call
def print_summary(success, fail, silent):
    """Print a summary of the conversion results."""
    msg = f"Done: {success} converted, {fail} failed." if silent else f"Conversion finished. Success: {success}, Failed: {fail}"
    print(msg)

@log_call
def remove_original_file(avif_file):
    """Remove the original AVIF file after conversion."""
    avif_file.unlink()

@log_call
def check_and_prepare_dirs(input_path, output_path):
    if not input_path.is_dir():
        logging.error(f"Input directory '{input_path}' does not exist.")
        return False
    output_path.mkdir(parents=True, exist_ok=True)
    return True
