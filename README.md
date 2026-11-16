# Monogram Vector Extractor

A Python command-line tool that extracts foreground artwork from raster images and converts it into scalable SVG graphics, favicons, and UI-ready image assets.

Provide an image, run the extractor, inspect the resulting foreground mask, and export vector assets. Cropping and extraction thresholds can be adjusted when needed, but are not required for the basic workflow.

## Features

- **Foreground Extraction:** Identifies bright or warm-coloured artwork against a darker background.
- **Configurable Extraction:** Adjust brightness and colour warmth thresholds to suit different images.
- **Automatic Cropping:** Detects the boundaries of the extracted artwork and removes unnecessary surrounding space.
- **Optional Manual Cropping:** Specify a region of interest when the source image contains multiple objects or unwanted elements.
- **Vector Tracing:** Converts the extracted foreground mask into scalable SVG paths.
- **Custom Colours:** Choose foreground and background colours for exported assets.
- **SVG Export:** Generates transparent SVG files for different interface themes.
- **Favicon Generation:** Creates SVG and PNG favicons in multiple resolutions.
- **UI Previews:** Generates preview images for light and dark interfaces.
- **Extraction Diagnostics:** Saves intermediate masks and comparison images to inspect extraction quality.

## Requirements

- Python 3.10 or newer.
- Dependencies listed in `requirements.txt`.

## Installation

Clone the repository:

```bash
git clone https://github.com/seemadri/monogram-vector-extractor.git
cd monogram-vector-extractor
```

Create and activate a virtual environment.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### CairoSVG system dependency

CairoSVG may require the Cairo graphics library to be installed on your system.

**macOS**

```bash
brew install cairo
```

**Ubuntu / Debian**

```bash
sudo apt-get install libcairo2
```

## Quick Start

Place your source image inside the project directory or provide its full or relative path.

For example, using the included sample image:

```bash
python extract_monogram.py examples/sample_showcase.png --preview-only
```

This generates an extraction preview without exporting the final vector assets.

Inspect the comparison image in:

```text
brand_assets/03_extraction_comparison.png
```

If the extracted mask looks satisfactory, run the extractor again without `--preview-only`:

```bash
python extract_monogram.py examples/sample_showcase.png
```

The generated assets are saved in `brand_assets/` by default.

For your own image:

```bash
python extract_monogram.py path/to/your_image.png
```

No crop coordinates are required for the standard workflow.

## Usage

### 1. Extract artwork from an image

```bash
python extract_monogram.py path/to/your_image.png
```

The tool processes the complete image, identifies foreground artwork, automatically crops the detected region, and generates the output assets.

### 2. Preview extraction

```bash
python extract_monogram.py path/to/your_image.png --preview-only
```

This generates diagnostic images so that you can inspect the extraction before exporting SVGs and favicons.

### 3. Adjust extraction thresholds

The extractor uses brightness and colour warmth thresholds to identify foreground pixels.

For gold or warm-coloured artwork:

```bash
python extract_monogram.py path/to/your_image.png \
  --min-brightness 105 \
  --warmth 35
```

For white or neutral-coloured artwork:

```bash
python extract_monogram.py path/to/your_image.png \
  --min-brightness 180 \
  --warmth 0
```

The appropriate values depend on the contrast and colours in the source image.

### 4. Process a specific image region

If the source contains multiple objects or unwanted background elements, specify an optional crop region:

```bash
python extract_monogram.py path/to/your_image.png \
  --crop LEFT TOP RIGHT BOTTOM
```

Coordinates are expressed in pixels, relative to the original image.

### 5. Customise output colours and filenames

```bash
python extract_monogram.py path/to/your_image.png \
  --fg-color "#D9BE83" \
  --bg-color "#163E2B" \
  --prefix "mybrand" \
  --output dist/assets
```

### 6. Generate assets without retaining them in the project directory

You can specify a separate output directory:

```bash
python extract_monogram.py path/to/your_image.png \
  --output /tmp/monogram-assets
```

This is useful when you want to keep generated files separate from the source repository.

## Generated Assets

By default, the extractor creates a `brand_assets/` directory.

For a prefix of `monogram`, the output includes:

### Vector graphics

| File | Description |
|---|---|
| `monogram.svg` | Primary transparent SVG |
| `monogram-dark.svg` | Foreground-coloured SVG |
| `monogram-light.svg` | Alternative-coloured SVG |
| `monogram-favicon.svg` | Rounded-square favicon with a solid background |

### Favicon PNGs

The following resolutions are generated:

- 16 × 16 px
- 32 × 32 px
- 64 × 64 px
- 192 × 192 px
- 512 × 512 px

### UI previews

| File | Description |
|---|---|
| `monogram-preview-dark.png` | Preview for dark-theme interfaces |
| `monogram-preview-light.png` | Preview for light-theme interfaces |

Both previews are generated at 152 × 152 px.

### Diagnostic images

| File | Description |
|---|---|
| `01_source_crop.png` | Cropped source image, generated only when manual cropping is used |
| `02_extraction_mask.png` | Binary foreground extraction mask |
| `03_extraction_comparison.png` | Source image and extracted mask comparison |
| `04_tight_mask.png` | Automatically cropped foreground mask |

Diagnostic images are useful for inspecting extraction quality and adjusting thresholds.

## Command-Line Reference

| Argument | Default | Description |
|---|---|---|
| `input` | Required | Path to the source image |
| `-o`, `--output` | `brand_assets` | Output directory |
| `-p`, `--prefix` | `monogram` | Filename prefix for generated assets |
| `--crop` | None | Optional crop coordinates: LEFT TOP RIGHT BOTTOM |
| `--fg-color` | `#D9BE83` | Foreground colour for primary and dark-theme artwork |
| `--bg-color` | `#163E2B` | Background colour for light-theme artwork and favicon |
| `--min-brightness` | `105` | Minimum average RGB brightness threshold (0–255) |
| `--warmth` | `35` | Minimum red-blue difference for warm-coloured artwork; use 0 to disable |
| `--preview-only` | False | Generate extraction diagnostics without exporting vectors |

## How It Works

The extraction pipeline consists of the following stages:

1. **Image Loading:** Loads the source raster image and optionally crops a specified region.
2. **Foreground Detection:** Identifies pixels using configurable brightness and colour warmth thresholds.
3. **Mask Cleaning:** Removes small isolated foreground components.
4. **Automatic Cropping:** Detects the foreground boundaries and crops the extracted mask.
5. **Contour Tracing:** Identifies and simplifies contours to create SVG paths.
6. **Asset Generation:** Exports SVG graphics, favicons, and UI preview images.

## Limitations

- The current extraction method is threshold-based and works best when the foreground artwork is visually distinct from a darker background.
- Images with complex backgrounds, gradients, shadows, overlapping colours, or low contrast may require manual cropping or threshold adjustment.
- The current implementation is designed for bright or warm-coloured foreground artwork, not arbitrary object segmentation.
- Generated SVGs are vector traces of the extracted raster artwork; they do not reconstruct the original font or design geometry.
- Fine details may be affected by mask cleaning and contour simplification.

## License

MIT License. See [LICENSE](LICENSE) for details.
