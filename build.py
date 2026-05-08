#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate italic versions of TTF fonts"
    )
    parser.add_argument(
        "--input", required=True, help="Directory containing input TTF files"
    )
    parser.add_argument(
        "--output", required=True, help="Directory for generated italic fonts"
    )
    parser.add_argument(
        "--angle", type=float, default=9, help="Slant angle in degrees (default: 9)"
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = Path(__file__).parent / "make-italic.py"
    if not script_path.exists():
        print(f"Error: make-italic.py not found at: {script_path}")
        sys.exit(1)

    ttf_files = sorted(input_dir.glob("*.ttf"))

    if not ttf_files:
        print(f"Warning: No .ttf files found in {input_dir}")
        sys.exit(0)

    print("=" * 60)
    print("Generating Italic Fonts")
    print("=" * 60)
    print(f"Input:  {input_dir.resolve()}")
    print(f"Output: {output_dir.resolve()}")
    print(f"Angle:  {args.angle}°")
    print(f"Found {len(ttf_files)} font(s)")
    print()

    success_count = 0
    fail_count = 0

    for input_file in ttf_files:
        output_filename = input_file.stem + "-Italic.ttf"
        output_file = output_dir / output_filename

        print(f"Processing: {input_file.name}")

        try:
            result = subprocess.run(
                [
                    "fontforge",
                    "-script",
                    str(script_path),
                    "--input",
                    str(input_file),
                    "--output",
                    str(output_file),
                    "--angle",
                    str(args.angle),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print(f"  ✓ Generated: {output_filename}")
                if result.stdout.strip():
                    print(f"    {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"  ✗ Failed: {output_filename}")
                if result.stderr.strip():
                    print(f"    Error: {result.stderr.strip()}")
                fail_count += 1

        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout: {output_filename}")
            fail_count += 1
        except FileNotFoundError:
            print("Error: fontforge command not found. Please install FontForge.")
            sys.exit(1)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            fail_count += 1

        print()

    print("=" * 60)
    print(f"Complete! Success: {success_count}, Failed: {fail_count}")
    print("=" * 60)

    if success_count > 0:
        print("\nGenerated files:")
        for f in sorted(output_dir.glob("*.ttf")):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {f.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
