# Monogram Vector Extractor

A Python CLI tool that isolates a foreground monogram or logo from a raster showcase image, traces its contours into clean vector paths, and exports production-ready SVGs and multi-resolution favicons.

## Visual Example

| Source Input | Extracted Vector Mask |
| :---: | :---: |
| ![Sample Input](examples/sample_showcase.png) | ![Extraction Comparison](examples/preview_comparison.png) |

## Features

* **Customizable Color Extraction:** Isolates bright or warm foreground artwork (gold, silver, white, or light accents) from darker backgrounds using configurable RGB thresholds.
* **Optional Region Cropping:** Process an entire image or target a specific bounding box via `--crop`.
* **Clean Vector Tracing:** Converts raster masks into smooth, centered `512x512` SVG paths using even-odd fill rules.
* **Complete Brand Asset Suite:** Generates light/dark transparent SVGs, a rounded-square favicon SVG, anti-aliased favicon PNGs (`16px` to `512px`), and UI preview assets.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/seemadri/monogram-vector-extractor.git
   cd monogram-vector-extractor
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   > **Note on CairoSVG:** If `CairoSVG` fails to render on macOS or Linux, install the system Cairo library first (`brew install cairo` on macOS or `sudo apt-get install libcairo2` on Ubuntu/Debian).

## Quick Start

Run the tool on the included sample image:

```bash
python extract_monogram.py examples/sample_showcase.png --crop 56 159 381 451
```

### Common Workflows

**1. Preview mask extraction before generating vectors:**
```bash
python extract_monogram.py showcase.png --crop 56 159 381 451 --preview-only
```

**2. Customize brand colors and output file prefix:**
```bash
python extract_monogram.py showcase.png \
  --fg-color "#D9BE83" \
  --bg-color "#163E2B" \
  --prefix "acme" \
  --output dist/assets
```

**3. Extract a pure white or silver logo (disable warmth filter):**
```bash
python extract_monogram.py white_logo.png --warmth 0 --min-brightness 180
```

## Generated Output

Running the script creates an output folder (default: `brand_assets/`) containing:

* **Vector SVGs:**
  * `<prefix>.svg` — Primary foreground-colored transparent vector
  * `<prefix>-dark.svg` — Foreground-colored vector for dark backgrounds
  * `<prefix>-light.svg` — Background-colored vector for light backgrounds
  * `<prefix>-favicon.svg` — Rounded-square icon (`rx=105`) with solid background
* **Raster Favicons & Previews:**
  * `<prefix>-favicon-{16,32,64,192,512}.png` — Anti-aliased PNG favicons
  * `<prefix>-preview-{dark,light}.png` — `152x152` UI/navbar preview renders
* **Diagnostic Files:**
  * `01_source_crop.png` through `04_tight_mask.png` — Intermediate images to verify extraction accuracy

## CLI Reference

| Flag | Default | Description |
| :--- | :--- | :--- |
| `input` | *(Required)* | Path to the source PNG/JPG image. |
| `-o`, `--output` | `brand_assets` | Directory where generated assets are saved. |
| `-p`, `--prefix` | `monogram` | Filename prefix for all exported SVGs and PNGs. |
| `--crop` | `None` | Optional 4 integers (`LEFT TOP RIGHT BOTTOM`) to crop the input image. |
| `--fg-color` | `#D9BE83` | Hex color for primary/dark-theme artwork and favicon foreground. |
| `--bg-color` | `#163E2B` | Hex color for light-theme artwork and favicon background. |
| `--min-brightness` | `105` | Minimum average RGB brightness (`0–255`) to isolate foreground pixels. |
| `--warmth` | `35` | Minimum `Red - Blue` difference (`0–255`) for warm/gold tones. Set to `0` for neutral/white logos. |
| `--preview-only` | `False` | Save diagnostic crop and mask previews without exporting vectors. |

## License

MIT
