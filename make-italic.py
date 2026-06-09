#!/usr/bin/env fontforge
import argparse
import math
import unicodedata

import fontforge

parser = argparse.ArgumentParser(description="Generate an italic version of a TTF font")
parser.add_argument("--input", required=True, help="Input TTF file")
parser.add_argument("--output", required=True, help="Output TTF file")
parser.add_argument(
    "--angle", type=float, default=9, help="Slant angle in degrees (default: 9)"
)
parser.add_argument(
    "--width",
    type=int,
    default=None,
    help="Normalize advance widths: narrow glyphs to N, full-width (CJK) glyphs to 2*N",
)
parser.add_argument(
    "--no-slant",
    action="store_true",
    help="Skip slanting and emit an upright font (only useful with --width)",
)
args = parser.parse_args()


def is_wide(glyph, narrow_width):
    """Full-width (CJK) glyphs get the doubled advance; everything else stays narrow."""
    cp = glyph.unicode
    if cp is not None and cp >= 0:
        try:
            return unicodedata.east_asian_width(chr(cp)) in ("W", "F")
        except ValueError:
            pass
    # No usable codepoint (e.g. vertical/alternate forms): fall back to current advance.
    return glyph.width >= 1.5 * narrow_width


def normalize_widths(font, narrow_width):
    """Set narrow glyphs to narrow_width and full-width glyphs to 2x, re-centering ink."""
    wide_width = narrow_width * 2
    # Glyphs used as references must not be moved, or their composites would drift.
    referenced = {ref[0] for glyph in font.glyphs() for ref in glyph.references}
    for glyph in font.glyphs():
        target = wide_width if is_wide(glyph, narrow_width) else narrow_width
        if glyph.glyphname not in referenced:
            xmin, ymin, xmax, ymax = glyph.boundingBox()
            ink = xmax - xmin
            if ink > 0:
                dx = round((target - ink) / 2 - xmin)
                if dx:
                    glyph.transform((1, 0, 0, 1, dx, 0))
        glyph.width = target


def set_names(font, family, subfamily, pref_family, pref_styles, fullname, psname):
    """Write one face's name table, preserving the source family + weight grouping.

    Clears the stale entries (every language) for the IDs we manage, then sets the
    English ones. `pref_family` (the typographic family, e.g. "IBM Plex Sans SC") is
    kept so the face groups with the other weights; `pref_styles` (e.g. "Thin Italic")
    is the style shown in font menus. The font's weight is left untouched.
    """
    managed = {
        "Family", "SubFamily", "UniqueID", "Fullname", "PostScriptName",
        "Preferred Family", "Preferred Styles", "Compatible Full",
        "WWS Family", "WWS Subfamily",
    }
    lang = "English (US)"
    names = [n for n in font.sfnt_names if n[1] not in managed]
    names += [
        (lang, "Family", family),
        (lang, "SubFamily", subfamily),
        (lang, "Fullname", fullname),
        (lang, "Preferred Family", pref_family),
        (lang, "Preferred Styles", pref_styles),
    ]
    font.sfnt_names = tuple(names)
    font.familyname = family
    font.fullname = fullname
    font.fontname = psname


font = fontforge.open(args.input)

slant = not args.no_slant

if slant:
    slant_degrees = args.angle
    slant_radians = math.radians(slant_degrees)
    slant_factor = math.tan(slant_radians)

    font.selection.all()
    font.transform((1, 0, slant_factor, 1, 0, 0))

if args.width is not None:
    normalize_widths(font, args.width)

# Preserve the source family + weight grouping; only add the italic style for the
# slanted variant. The width tag stays in the full/PostScript names (and file name)
# so the normalized fonts are distinct from the originals.
orig = {sid: val for lang, sid, val in font.sfnt_names if lang == "English (US)"}
pref_family = orig.get("Preferred Family") or font.familyname
pref_style = orig.get("Preferred Styles") or font.weight or "Regular"
legacy_family = orig.get("Family") or font.familyname
legacy_sub = orig.get("SubFamily") or "Regular"

tag = f" W{args.width}" if args.width is not None else ""
if slant:
    pref_styles = "Italic" if pref_style == "Regular" else f"{pref_style} Italic"
    subfamily = "Bold Italic" if legacy_sub == "Bold" else "Italic"
else:
    pref_styles = pref_style
    subfamily = legacy_sub

fullname = f"{pref_family} {pref_styles}{tag}"
psname = f"{pref_family}{tag}-{pref_styles}".replace(" ", "")

set_names(font, legacy_family, subfamily, pref_family, pref_styles, fullname, psname)

if slant:
    font.italicangle = -slant_degrees
    # set italic, clear the mutually-exclusive regular bit, keep bold for bold weights
    font.os2_stylemap = (font.os2_stylemap & ~0x40) | 0x01

font.generate(args.output)
detail = f"{slant_degrees}° slant (factor: {slant_factor:.4f})" if slant else "no slant"
width_note = (
    f", widths normalized to {args.width}/{args.width * 2}"
    if args.width is not None
    else ""
)
print(f"Generated {'italic' if slant else 'upright'} font with {detail}{width_note}")
font.close()
