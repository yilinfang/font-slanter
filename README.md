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
python3 build.py <input_dir> <output_dir>
```

### Using Docker Compose (recommended)

```bash
# Put your fonts in the `input` directory, and the generated fonts will be in the `output` directory.
docker-compose up
```
