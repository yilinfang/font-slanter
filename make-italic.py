#!/usr/bin/env fontforge
import argparse
import math
import unicodedata

import fontforge
import psMat

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
    help="Snap CJK glyphs onto a mono grid: full-width advances become 2*N, half-width forms become N; non-CJK glyphs are left unchanged",
)
parser.add_argument(
    "--no-slant",
    action="store_true",
    help="Skip slanting and emit an upright font (only useful with --width)",
)
parser.add_argument(
    "--non-cjk",
    choices=["keep", "remove"],
    default="keep",
    help="keep: slant non-CJK glyphs but leave their widths alone; remove: drop them for a pure CJK fallback (default: keep)",
)
args = parser.parse_args()


def is_wide(glyph, narrow_width):
    """Full-width (CJK) glyphs get the doubled advance; everything else stays narrow.

    East-Asian *Ambiguous* glyphs (arrows, math symbols, §, smart quotes, …) are drawn
    full-width in many CJK fonts but half-width elsewhere, so we trust the source advance
    for them rather than forcing them narrow and overflowing the box.
    """
    cp = glyph.unicode
    if cp is not None and cp >= 0:
        try:
            eaw = unicodedata.east_asian_width(chr(cp))
        except ValueError:
            eaw = None
        if eaw in ("W", "F"):
            return True
        if eaw != "A":  # Na / H / N: definitively narrow
            return False
        # "A" (ambiguous): fall through to the source-advance heuristic below.
    # No usable codepoint, or ambiguous width: fall back to current advance.
    return glyph.width >= 1.5 * narrow_width


def is_cjk(glyph, narrow_width):
    """Glyphs that should snap to the half/full grid.

    Extends is_wide() (full-width CJK) with the half-width East-Asian forms
    (e.g. half-width katakana, East-Asian-width "H") so they land on the half
    cell. Latin and other proportional glyphs are left alone.
    """
    if is_wide(glyph, narrow_width):
        return True
    cp = glyph.unicode
    if cp is not None and cp >= 0:
        try:
            return unicodedata.east_asian_width(chr(cp)) == "H"
        except ValueError:
            pass
    return False


def strip_non_cjk(font, narrow_width):
    """Drop every non-full-width glyph, keeping CJK + the components they reference."""
    keep = {g.glyphname for g in font.glyphs() if is_wide(g, narrow_width)}
    keep.add(".notdef")
    pending = [n for n in keep if n in font]
    while pending:
        for ref in font[pending.pop()].references:
            if ref[0] not in keep:
                keep.add(ref[0])
                pending.append(ref[0])
    for glyph in list(font.glyphs()):
        if glyph.glyphname not in keep:
            font.removeGlyph(glyph)


def normalize_cjk_widths(font, narrow_width):
    """Snap CJK glyphs onto the half (N) / full (2N) grid, PlemolJP-style.

    Mirrors PlemolJP's set_width_600_or_1000: a CJK glyph narrower than the half
    cell is centered and grown to narrow_width, a full-width one is centered and
    grown to 2*narrow_width. Non-CJK glyphs keep their proportional advance.
    """
    wide_width = narrow_width * 2
    # Glyphs used as references must not be moved, or their composites would drift.
    referenced = {ref[0] for glyph in font.glyphs() for ref in glyph.references}
    for glyph in font.glyphs():
        if not is_cjk(glyph, narrow_width):
            continue
        if 0 < glyph.width < narrow_width:
            target = narrow_width
        elif narrow_width < glyph.width < wide_width:
            target = wide_width
        else:
            continue  # already sits on the grid (or wider) — leave it alone
        # Pad both sides equally so the glyph keeps the placement the source
        # designed. Centering the *ink* instead would shove intentionally
        # off-center glyphs (brackets/punctuation like 【】, 。) into the middle
        # of the cell and break their spacing.
        if glyph.glyphname not in referenced:
            glyph.transform(psMat.translate((target - glyph.width) / 2, 0))
        glyph.width = target


def set_names(font, family, subfamily, pref_family, pref_styles, fullname, psname):
    """Write one face's name table, preserving the source family + weight grouping.

    Clears the stale entries (every language) for the IDs we manage, then sets the
    English ones. `pref_family` (the typographic family, e.g. "IBM Plex Sans SC") is
    kept so the face groups with the other weights; `pref_styles` (e.g. "Thin Italic")
    is the style shown in font menus. The font's weight is left untouched.
    """
    managed = {
        "Family",
        "SubFamily",
        "UniqueID",
        "Fullname",
        "PostScriptName",
        "Preferred Family",
        "Preferred Styles",
        "Compatible Full",
        "WWS Family",
        "WWS Subfamily",
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

# is_wide() needs a narrow baseline for ambiguous / unencoded glyphs; when --width
# is omitted, a full-width CJK advance is ~em, so em//2 is a sound narrow reference.
narrow_ref = args.width if args.width is not None else font.em // 2

if args.non_cjk == "remove":
    strip_non_cjk(font, narrow_ref)

slant = not args.no_slant

if slant:
    slant_degrees = args.angle
    slant_radians = math.radians(slant_degrees)
    slant_factor = math.tan(slant_radians)

    font.selection.all()
    font.transform((1, 0, slant_factor, 1, 0, 0))

if args.width is not None:
    normalize_cjk_widths(font, args.width)

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
    f", CJK widths snapped to {args.width}/{args.width * 2} grid"
    if args.width is not None
    else ""
)
non_cjk_note = ", non-CJK glyphs removed" if args.non_cjk == "remove" else ""
print(
    f"Generated {'italic' if slant else 'upright'} font with {detail}{width_note}{non_cjk_note}"
)
font.close()
