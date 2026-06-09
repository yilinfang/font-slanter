# font-slanter

**Font-slanter** generates a slanted (faux-italic), grid-aligned **CJK companion font**
to pair with your favourite monospace coding font. CJK (Chinese, Japanese, Korean) fonts
rarely ship an italic style, so editors and terminals fall back to an upright CJK face even
when the surrounding code is italic. The idea here is the same as Nerd Fonts or Sarasa
Gothic, but without merging anything: keep using your coding font as the primary, and add a
generated CJK font as the **fallback** so CJK glyphs slant along with your italics and line
up on the coding grid.

Because your primary font already renders all the Latin/ASCII/symbol glyphs (with its own
real italics), this tool only needs to touch the **CJK glyphs** — that is why the non-CJK
glyphs in the source font are either left at their natural proportions or dropped entirely
(see `--non-cjk` below).

## Using it as a fallback font

Set your coding font first and the generated CJK font second. For example, in VS Code:

```jsonc
// settings.json — upright editor uses the regular pair, italics use the italic pair
"editor.fontFamily": "JetBrains Mono, 'IBM Plex Sans SC W600'"
```

Most terminals (Kitty, WezTerm, Alacritty, …) and editors expose the same primary +
fallback list. Use the upright `…-W600.ttf` alongside your font's regular/bold, and the
slanted `…-Italic-W600.ttf` alongside its italics.

## Requirements

- FontForge
- Python 3

_**or**_

- Docker
- Docker Compose (optional but recommended)

## Usage

### Using FontForge and Python

```bash
python3 build.py --input <input_dir> --output <output_dir> [--angle DEGREES] [--width UNITS] [--non-cjk keep|remove]
```

Example with a custom slant angle:

```bash
python3 build.py --input ./input --output ./output --angle 12
```

#### Aligning CJK widths to the coding grid

`--width N` sets `N` to your primary font's character-cell width, so the full-width CJK
glyphs (ideographs, kana, fullwidth symbols) are normalized to `2 * N` and re-centered within
that double cell — two CJK columns line up exactly with two of your coding font's columns.
Only CJK glyphs are touched; **non-CJK glyphs keep their original proportional widths**.
Full-width vs. narrow is decided by the glyph's Unicode East Asian Width, and ambiguous-width
symbols (arrows, math operators, smart quotes, …) keep whichever width the source font drew
them at.

```bash
# CJK glyphs -> 1200 units, matching a 600-unit coding cell
python3 build.py --input ./input --output ./output --angle 9 --width 600
```

For each input font, a `--width` run produces **two** outputs that share the same grid — an
upright `…-W600.ttf` (pair with your coding font's regular/bold) and a slanted
`…-Italic-W600.ttf` (pair with its italics). Each output keeps the source font's family **and
weight**, so a whole family (Thin … Bold) stays intact and every weight gains a matching
italic (Thin → _Thin Italic_, Regular → _Italic_, Bold → _Bold Italic_, …). The `W600` tag
stays in the full name, PostScript name, and file name to keep the normalized fonts distinct
from the originals. When `--width` is omitted, only the italic is generated, CJK widths are
left unchanged, and no tag is added.

#### Choosing what happens to non-CJK glyphs

Source CJK fonts also ship Latin/ASCII/punctuation glyphs, but in a fallback setup your
primary coding font renders those instead. `--non-cjk` controls what to do with them:

- **`keep`** (default) — keep every glyph and slant it (so the italic stays consistent), but
  leave non-CJK widths untouched. The font still works on its own.
- **`remove`** — drop all non-CJK glyphs, leaving a pure CJK supplement: smaller files and no
  chance of stray glyphs shadowing your coding font. Use this when you always rely on
  fallback. (A glyph that only the CJK font had will be missing if your primary font also
  lacks it.)

```bash
python3 build.py --input ./input --output ./output --angle 9 --width 600 --non-cjk remove
```

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

To align CJK widths to the coding grid, and optionally drop non-CJK glyphs (see above):

```bash
docker-compose run --rm fontforge python3 build.py --input /input --output /output --angle 9 --width 600 --non-cjk remove
```
