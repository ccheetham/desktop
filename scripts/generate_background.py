#!/usr/bin/env python3
"""Generate a solid-color desktop background with centered text."""

import argparse
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger("generate_background")


def parse_dimensions(value: str) -> tuple[int, int]:
    width, sep, height = value.partition("x")
    if not sep:
        raise argparse.ArgumentTypeError("dimensions must be WIDTHxHEIGHT, e.g. 2560x1440")
    return int(width), int(height)


def build_font(size: int, italic: bool = False) -> ImageFont.FreeTypeFont:
    # Window Maker's default WindowTitleFont is "Sans:bold" (a bold grotesque
    # sans-serif in the Helvetica/NeXTSTEP lineage); Arial Bold is the closest
    # match readily available on macOS.
    log.debug("building font at size=%d italic=%s", size, italic)
    candidates = (
        ("/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf", "/System/Library/Fonts/Helvetica.ttc")
        if italic
        else ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc")
    )
    for candidate in candidates:
        log.debug("checking font candidate: %s", candidate)
        if Path(candidate).exists():
            log.debug("using font: %s", candidate)
            return ImageFont.truetype(candidate, size)
    log.debug("no candidate fonts found, falling back to PIL default font")
    return ImageFont.load_default()


def generate(dimensions: tuple[int, int], text: str, bg: str, fg: str, output: Path, italic: bool = False) -> None:
    width, height = dimensions
    log.debug("creating %dx%d image with bg=%s", width, height, bg)
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)

    font_size = height // 10
    font = build_font(font_size, italic=italic)

    log.debug("measuring text bbox for text=%r", text)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = ((width - text_width) / 2 - bbox[0], (height - text_height) / 2 - bbox[1])
    log.debug("text size=%s position=%s", (text_width, text_height), position)

    log.debug("drawing text with fg=%s", fg)
    draw.text(position, text, font=font, fill=fg)

    log.debug("ensuring output directory exists: %s", output.parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    log.debug("saving image to %s", output)
    image.save(output)
    log.debug("save complete")
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimensions", required=True, type=parse_dimensions, help="e.g. 2560x1440")
    parser.add_argument("--text", required=True, help="Text to center on the background")
    parser.add_argument("--bg", default="#1e1e2e", help="Background color (name or hex, default #1e1e2e)")
    parser.add_argument("--fg", default="#ffffff", help="Foreground/text color (name or hex, default #ffffff)")
    parser.add_argument("--output", type=Path, default=Path("backgrounds/output.png"), help="Output image path")
    parser.add_argument("--italic", action="store_true", help="Render the text in italic")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging breadcrumbs")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log.debug("parsed args: %s", args)

    generate(args.dimensions, args.text, args.bg, args.fg, args.output, italic=args.italic)
    log.debug("generate() returned")


if __name__ == "__main__":
    main()
