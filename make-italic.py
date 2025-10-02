#!/usr/bin/env fontforge
import fontforge
import sys
import math

if len(sys.argv) < 3:
    print("Usage: fontforge -script make-italic.py input.ttf output.ttf")
    sys.exit(1)

font = fontforge.open(sys.argv[1])

# Calculate slant for 9 degrees
# tan(9°) for the shear transformation
slant_degrees = 9
slant_radians = math.radians(slant_degrees)
slant_factor = math.tan(slant_radians)

# Apply italic transformation
# Transform matrix: (1, 0, slant_factor, 1, 0, 0)
# This applies a horizontal shear
font.selection.all()
font.transform((1, 0, slant_factor, 1, 0, 0))

# Update font names
font.fontname = font.fontname + "-Italic"
font.familyname = font.familyname
font.fullname = font.fullname + " Italic"

# Set italic angle (negative by convention)
font.italicangle = -slant_degrees

# Set OS/2 italic bit
font.os2_stylemap |= 0x01

# Generate the font
font.generate(sys.argv[2])
print(f"Generated italic font with {slant_degrees}° slant (factor: {slant_factor:.4f})")
font.close()
