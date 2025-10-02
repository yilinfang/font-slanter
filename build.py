#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 build.py <input_dir> <output_dir>")
        print("Example: python3 build.py ./static ./static/italic")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find make-italic.py script
    script_path = Path(__file__).parent / "make-italic.py"
    if not script_path.exists():
        print(f"Error: make-italic.py not found at: {script_path}")
        sys.exit(1)

    # Find all TTF files
    ttf_files = sorted(input_dir.glob("*.ttf"))

    if not ttf_files:
        print(f"Warning: No .ttf files found in {input_dir}")
        sys.exit(0)

    print("=" * 60)
    print("Generating Italic Fonts")
    print("=" * 60)
    print(f"Input:  {input_dir.resolve()}")
    print(f"Output: {output_dir.resolve()}")
    print(f"Found {len(ttf_files)} font(s)")
    print()

    success_count = 0
    fail_count = 0

    for input_file in ttf_files:
        # Generate output filename
        output_filename = input_file.stem + "-Italic.ttf"
        output_file = output_dir / output_filename

        print(f"Processing: {input_file.name}")

        # Run fontforge with make-italic.py
        try:
            result = subprocess.run(
                [
                    "fontforge",
                    "-script",
                    str(script_path),
                    str(input_file),
                    str(output_file),
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
