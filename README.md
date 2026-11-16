# Monogram Vector Extractor

A Python CLI tool that isolates a foreground monogram or logo from a brand showcase image, traces its contours into clean vector paths, and exports production-ready SVGs and multi-resolution favicons.

## Features

* **Customizable Color Extraction:** Isolates bright/warm foreground artwork (like gold, white, or light accents) from darker backgrounds using configurable RGB thresholds.
* **Optional Cropping:** Process an entire image or target a specific region via bounding-box coordinates (`--crop`).
* **Clean Vector Tracing:** Converts raster masks into smooth, centered `512x512` SVG paths with even-odd fill rules.
* **Complete Asset Suite:** Exports light/dark transparent SVGs, a rounded-square favicon SVG, anti-aliased favicon PNGs (`16px` to `512px`), and UI preview assets.

## Setup

1. **Clone the repository and install dependencies:**
   ```bash
   pip install -r requirements.txt
