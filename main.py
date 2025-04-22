import argparse
from convert import convert_avif_to_png

def main():
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
