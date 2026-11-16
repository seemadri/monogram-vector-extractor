"""
Monogram Vector Extractor

Extracts foreground monogram artwork from a raster image, traces its contours
into vector paths, and exports scalable SVGs, favicons, and UI previews.
"""

import argparse
import io
from pathlib import Path

import cairosvg
import cv2
import matplotlib
import numpy as np
import svgwrite
from PIL import Image

# Use non-interactive backend for headless terminal execution
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def extract_foreground_mask(
    image: Image.Image,
    min_brightness: int = 105,
    warmth: int = 35,
    min_area: int = 3,
) -> np.ndarray:
    """Isolate bright/warm foreground pixels from a darker background."""
    rgb = np.asarray(image, dtype=np.float32)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    brightness = (r + g + b) / 3.0

    # Brightness is always required. The warmth filter is optional.
    mask_condition = brightness > min_brightness

    if warmth > 0:
        mask_condition &= (r - b) > warmth
        mask_condition &= (r > min_brightness + 10) & (
            g > min_brightness - 10
        )

    raw_mask = mask_condition.astype(np.uint8) * 255

    # Remove isolated pixel noise while preserving fine details
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        raw_mask, connectivity=8
    )
    clean_mask = np.zeros_like(raw_mask)
    for i in range(1, count):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            clean_mask[labels == i] = 255

    return clean_mask


def save_comparison_plot(
    source_image: Image.Image, clean_mask: np.ndarray, output_path: Path
) -> None:
    """Save a side-by-side diagnostic image of the crop and extracted mask."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].imshow(source_image)
    axes[0].set_title("Source Region")
    axes[0].axis("off")

    axes[1].imshow(clean_mask, cmap="gray")
    axes[1].set_title("Extracted Artwork Mask")
    axes[1].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close(fig)


def trace_svg_paths(mask: np.ndarray, simplify_factor: float = 0.0005) -> str:
    """Convert a binary mask into an SVG path data string."""
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    if hierarchy is None:
        raise RuntimeError("No contours found in mask.")

    paths = []
    for contour in contours:
        if cv2.contourArea(contour) < 2:
            continue
        perimeter = cv2.arcLength(contour, True)
        epsilon = simplify_factor * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        points = approx.reshape(-1, 2)

        if len(points) < 3:
            continue

        commands = [f"M {points[0][0]} {points[0][1]}"]
        commands.extend(f"L {x} {y}" for x, y in points[1:])
        commands.append("Z")
        paths.append(" ".join(commands))

    path_data = " ".join(paths)
    if not path_data:
        raise RuntimeError("No valid SVG paths generated.")

    return path_data


def create_svg(
    filepath: Path,
    path_data: str,
    width: int,
    height: int,
    color: str,
    background: str | None = None,
) -> None:
    """Write a centered 512x512 SVG file from traced path data."""
    dwg = svgwrite.Drawing(
        str(filepath), size=("512px", "512px"), viewBox="0 0 512 512"
    )
    if background is not None:
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(512, 512),
                rx=105,
                ry=105,
                fill=background,
            )
        )

    scale = min(385 / width, 385 / height)
    dx = (512 - width * scale) / 2
    dy = (512 - height * scale) / 2
    group = dwg.g(
        transform=f"translate({dx:.5f},{dy:.5f}) scale({scale:.7f})"
    )
    group.add(dwg.path(d=path_data, fill=color, fill_rule="evenodd"))

    dwg.add(group)
    dwg.save()
    print(f"Created: {filepath.name}")


def generate_assets(
    input_path: Path,
    output_dir: Path,
    prefix: str = "monogram",
    crop_box: tuple[int, int, int, int] | None = None,
    fg_color: str = "#D9BE83",
    bg_color: str = "#163E2B",
    min_brightness: int = 105,
    warmth: int = 35,
    preview_only: bool = False,
) -> None:
    """Run the full extraction and vector export pipeline."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path.resolve()}")

    output_dir.mkdir(parents=True, exist_ok=True)
    image = Image.open(input_path).convert("RGB")
    print(f"Loaded image: {input_path.name} ({image.size[0]}x{image.size[1]})")

    if crop_box is not None:
        working_image = image.crop(crop_box)
        if working_image.width == 0 or working_image.height == 0:
            raise ValueError(
                "Crop region is empty. Check LEFT TOP RIGHT BOTTOM coordinates."
            )
        working_image.save(output_dir / "01_source_crop.png")
    else:
        working_image = image

    clean_mask = extract_foreground_mask(
        working_image, min_brightness=min_brightness, warmth=warmth
    )
    Image.fromarray(clean_mask).save(output_dir / "02_extraction_mask.png")

    save_comparison_plot(
        working_image, clean_mask, output_dir / "03_extraction_comparison.png"
    )

    if preview_only:
        print(
            "\nExtraction preview saved.\n"
            f"Inspect {output_dir / '03_extraction_comparison.png'} "
            "and run without --preview-only to export."
        )
        return

    # Tightly crop around detected foreground pixels
    ys, xs = np.where(clean_mask > 0)
    if len(xs) == 0:
        raise RuntimeError(
            "No foreground pixels detected. Try lowering --min-brightness "
            "or adjusting --warmth."
        )

    padding = 6
    left = max(0, xs.min() - padding)
    right = min(clean_mask.shape[1], xs.max() + padding + 1)
    top = max(0, ys.min() - padding)
    bottom = min(clean_mask.shape[0], ys.max() + padding + 1)

    tight_mask = clean_mask[top:bottom, left:right]
    height, width = tight_mask.shape
    Image.fromarray(tight_mask).save(output_dir / "04_tight_mask.png")

    # Trace and export SVGs
    path_data = trace_svg_paths(tight_mask)
    dark_svg = output_dir / f"{prefix}-dark.svg"
    light_svg = output_dir / f"{prefix}-light.svg"
    master_svg = output_dir / f"{prefix}.svg"
    favicon_svg = output_dir / f"{prefix}-favicon.svg"

    create_svg(dark_svg, path_data, width, height, fg_color)
    create_svg(light_svg, path_data, width, height, bg_color)
    create_svg(master_svg, path_data, width, height, fg_color)
    create_svg(
        favicon_svg, path_data, width, height, fg_color, background=bg_color
    )

    # Export multi-resolution favicon PNGs
    png_bytes = cairosvg.svg2png(
        url=str(favicon_svg), output_width=2048, output_height=2048
    )
    large_favicon = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    for size in (16, 32, 64, 192, 512):
        resized = large_favicon.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(output_dir / f"{prefix}-favicon-{size}.png")

    # Export UI preview PNGs
    for theme, svg_file in (("dark", dark_svg), ("light", light_svg)):
        png_bytes = cairosvg.svg2png(
            url=str(svg_file), output_width=152, output_height=152
        )
        preview = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        preview.save(output_dir / f"{prefix}-preview-{theme}.png")

    print("\nAll assets generated successfully!")
    print(f"Output folder: {output_dir.resolve()}")
    for file in sorted(output_dir.iterdir()):
        print(f" - {file.name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a monogram from an image and generate scalable "
            "vector and favicon assets."
        )
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the source image file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("brand_assets"),
        help="Directory where generated assets will be saved "
        "(default: brand_assets).",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        type=str,
        default="monogram",
        help="Filename prefix for exported assets (default: monogram).",
    )
    parser.add_argument(
        "--crop",
        type=int,
        nargs=4,
        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
        default=None,
        help="Optional crop box coordinates (left top right bottom).",
    )
    parser.add_argument(
        "--fg-color",
        type=str,
        default="#D9BE83",
        help="Hex color for primary/dark-theme artwork (default: #D9BE83).",
    )
    parser.add_argument(
        "--bg-color",
        type=str,
        default="#163E2B",
        help="Hex color for light-theme artwork and favicon background "
        "(default: #163E2B).",
    )
    parser.add_argument(
        "--min-brightness",
        type=int,
        default=105,
        help="Minimum RGB brightness threshold 0-255 (default: 105).",
    )
    parser.add_argument(
        "--warmth",
        type=int,
        default=35,
        help="Minimum Red-Blue difference 0-255 for warm/gold tones; "
        "use 0 for white (default: 35).",
    )
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Only generate diagnostic extraction previews without "
        "exporting vectors.",
    )

    args = parser.parse_args()
    crop_tuple = tuple(args.crop) if args.crop is not None else None

    generate_assets(
        input_path=args.input,
        output_dir=args.output,
        prefix=args.prefix,
        crop_box=crop_tuple,
        fg_color=args.fg_color,
        bg_color=args.bg_color,
        min_brightness=args.min_brightness,
        warmth=args.warmth,
        preview_only=args.preview_only,
    )


if __name__ == "__main__":
    main()
