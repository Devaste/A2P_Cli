import argparse
from convert import convert_avif_to_png

def main():
    parser = argparse.ArgumentParser(
        usage="%(prog)s input_dir [-h] [--output_dir OUTPUT_DIR] [--replace] [--recursive] [--silent] [--qb_color QB_COLOR] [--qb_gray-color QB_GRAY_COLOR] [--qb_gray QB_GRAY]",
        description="Convert all .avif images in a directory to .png format."
    )
    parser.add_argument('input_dir', help="Directory containing .avif files")
    parser.add_argument('--output_dir', help="Directory to save .png files (default: same as input_dir)")
    parser.add_argument('--replace', action='store_true', help='Remove original .avif files after conversion')
    parser.add_argument('--recursive', action='store_true', help='Recursively search for .avif files in subdirectories')
    parser.add_argument('--silent', action='store_true', help='No output to command line, only finishing result')
    parser.add_argument('--qb_color', type=int, help='Quantize bitness for color images (1–8, i.e., 2–256 colors). Due to PNG and PIL quantize() limitations, only 1–8 are allowed. See: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize')
    parser.add_argument('--qb_gray-color', type=int, help='Quantize bitness for grayscale+one images (1–8, i.e., 2–256 levels). Due to PNG and PIL quantize() limitations, only 1–8 are allowed. See: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize')
    parser.add_argument('--qb_gray', type=int, help='Quantize bitness for grayscale images (1–8, i.e., 2–256 levels). Due to PNG and PIL quantize() limitations, only 1–8 are allowed. See: https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize')
    args = parser.parse_args()
    convert_avif_to_png(
        args.input_dir,
        args.output_dir,
        replace=args.replace,
        recursive=args.recursive,
        silent=args.silent,
        qb_color=args.qb_color,
        qb_gray_color=args.qb_gray_color,
        qb_gray=args.qb_gray
    )

if __name__ == '__main__':
    main()
