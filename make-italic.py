#!/usr/bin/env fontforge
import argparse
import math

import fontforge

parser = argparse.ArgumentParser(description="Generate an italic version of a TTF font")
parser.add_argument("--input", required=True, help="Input TTF file")
parser.add_argument("--output", required=True, help="Output TTF file")
parser.add_argument(
    "--angle", type=float, default=9, help="Slant angle in degrees (default: 9)"
)
args = parser.parse_args()

font = fontforge.open(args.input)

slant_degrees = args.angle
slant_radians = math.radians(slant_degrees)
slant_factor = math.tan(slant_radians)

font.selection.all()
font.transform((1, 0, slant_factor, 1, 0, 0))

font.fontname = font.fontname + "-Italic"
font.familyname = font.familyname
font.fullname = font.fullname + " Italic"

font.italicangle = -slant_degrees

font.os2_stylemap |= 0x01

font.generate(args.output)
print(f"Generated italic font with {slant_degrees}° slant (factor: {slant_factor:.4f})")
font.close()
