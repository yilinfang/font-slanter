# font-slanter

**Font-slanter** is a tool for generating slanted (italic) fonts from regular fonts.
It is particularly useful for CJK (Chinese, Japanese, Korean) fonts that typically do not include built-in italic styles.

## Requirements

- FontForge
- Python 3

_**or**_

- Docker
- Docker Compose (optional but recommended)

## Usage

### Using FontForge and Python

```bash
python3 build.py --input <input_dir> --output <output_dir> [--angle DEGREES] [--width UNITS]
```

Example with a custom slant angle:

```bash
python3 build.py --input ./input --output ./output --angle 12
```

#### Normalizing glyph widths

`--width N` normalizes advance widths so the font sits on a clean grid: narrow glyphs
(Latin letters, half-width forms) are set to `N`, and full-width glyphs (CJK ideographs,
kana, fullwidth symbols) are set to `2 * N`. Each glyph's outline is re-centered within its
new advance box. Narrow vs. full-width is decided by the glyph's Unicode East Asian Width,
so proportional Latin letters are not mistaken for full-width.

```bash
# Latin letters -> 600 units, CJK glyphs -> 1200 units
python3 build.py --input ./input --output ./output --angle 9 --width 600
```

For each input font, a `--width` run produces **two** outputs that share the same width grid —
an upright `…-W600.ttf` and a slanted `…-Italic-W600.ttf`. Each output keeps the source font's
family **and weight**, so a whole family (Thin … Bold) stays intact and every weight gains a
matching italic (Thin → *Thin Italic*, Regular → *Italic*, Bold → *Bold Italic*, …) that pairs
with it in font menus. The `W600` tag stays in the full name, PostScript name, and file name to
keep the normalized fonts distinct from the originals. When `--width` is omitted, only the
italic is generated, advance widths are left unchanged, and no tag is added.

### Using Docker Compose (recommended)

> **Note:** The scripts are copied into the image at build time, so after editing
> `build.py` or `make-italic.py` you must rebuild before the changes take effect:
>
> ```bash
> docker-compose build
> ```

```bash
# Put your fonts in the `input` directory, and the generated fonts will be in the `output` directory.
docker-compose up
```

To use a custom angle, override the command:

```bash
docker-compose run --rm fontforge python3 build.py --input /input --output /output --angle 12
```

To also normalize glyph widths (see above):

```bash
docker-compose run --rm fontforge python3 build.py --input /input --output /output --angle 9 --width 600
```
