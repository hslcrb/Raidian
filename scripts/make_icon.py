"""Generate a multi-resolution Windows icon without embedding proprietary fonts.

Uses Pillow only during packaging, not at runtime. A pixel-drawn brand mark
keeps the packaged icon crisp without relying on unavailable SVG renderers.
"""
from __future__ import annotations

from pathlib import Path
import sys


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    output = Path(argv[0]) if argv else Path("build/raidian.ico")
    try:
        from PIL import Image, ImageDraw
    except ImportError as error:
        raise SystemExit("아이콘을 생성하려면 pip install Pillow 가 필요합니다.") from error

    scale = 4
    size = 256 * scale
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def rect(coords, radius, color):
        draw.rounded_rectangle(tuple(v * scale for v in coords), radius=radius * scale, fill=color)

    def circle(x, y, r, color):
        draw.ellipse(((x-r)*scale, (y-r)*scale, (x+r)*scale, (y+r)*scale), fill=color)

    def line(points, color, width):
        draw.line([(x*scale, y*scale) for x,y in points], fill=color, width=width*scale, joint="curve")

    rect((0,0,256,256),74,"#551128")
    rect((18,18,238,238),62,"#FCECEF")
    # Branch stems. Round caps are explicit so they survive downscaling.
    line([(89,75),(89,173),(118,202),(162,202)],"#A72146",13)
    line([(89,129),(129,121),(151,90),(165,57)],"#A72146",13)
    for x,y in [(89,75),(165,57),(162,202)]:
        circle(x,y,20,"#FFFFFF")
        circle(x,y,16,"#C42B54")
    for x,y in [(114,131),(148,131)]:
        circle(x,y,5,"#551128")
    line([(120,148),(126,153),(135,153),(142,148)],"#551128",4)
    circle(104,145,6,"#EDB0C3")
    circle(160,145,6,"#EDB0C3")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.resize((256,256),Image.Resampling.LANCZOS).save(output, format="ICO",
        sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    print(output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
