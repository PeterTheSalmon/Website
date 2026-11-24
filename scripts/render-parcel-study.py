"""Draw the fictional neighbourhood used in Urbora’s conceptual illustration."""

from pathlib import Path
from PIL import Image, ImageDraw
from random import Random

rng = Random(35)
size = 1600
paper = "#f1f3ee"
im = Image.new("RGB", (size, size), paper)
d = ImageDraw.Draw(im)
for x in range(70, size, 230):
    for y in range(85, size, 253):
        d.rounded_rectangle(
            (x, y, x + 192, y + 207), 12, fill="#e2e6db", outline="#c5cdc0", width=2
        )
        d.line((x + 10, y + 104, x + 182, y + 104), fill="#bcc7b6", width=2)
        for row in range(2):
            start = y + row * 104
            for col in range(2):
                left = x + col * 96
                selected = x == 760 and y == 591 and row == 1 and col == 0
                fill = (
                    "#e4bb90"
                    if selected
                    else rng.choice(["#e6e9de", "#e1e6d9", "#e6e9de"])
                )
                d.rectangle(
                    (left + 8, start + 8, left + 96, start + 101),
                    fill=fill,
                    outline="#bbc5b4",
                    width=2,
                )
                bx = left + rng.randint(19, 30)
                by = start + rng.randint(25, 35)
                bw = rng.randint(35, 49)
                bh = rng.randint(29, 40)
                roof = [
                    (bx, by),
                    (bx + bw, by),
                    (bx + bw, by + bh),
                    (bx + 25, by + bh),
                    (bx + 25, by + bh + 9),
                    (bx + 6, by + bh + 9),
                    (bx + 6, by + bh - 3),
                    (bx, by + bh - 3),
                ]
                d.polygon([(px + 3, py + 4) for px, py in roof], fill="#b6b9aa")
                d.polygon(roof, fill="#ad764d" if selected else "#c7cbba")
                if selected:
                    d.rectangle(
                        (left + 8, start + 8, left + 96, start + 101),
                        outline="#933e23",
                        width=5,
                    )
                else:
                    cx, cy = left + rng.randint(20, 80), start + rng.randint(78, 91)
                    radius = rng.randint(8, 14)
                    d.ellipse(
                        (
                            cx - radius + 3,
                            cy - radius + 3,
                            cx + radius + 3,
                            cy + radius + 3,
                        ),
                        fill="#c4cbbb",
                    )
                    d.ellipse(
                        (cx - radius, cy - radius, cx + radius, cy + radius),
                        fill=rng.choice(["#a3b69b", "#96ac8f", "#a5b394"]),
                    )
rotated = im.rotate(16, resample=Image.Resampling.BICUBIC, fillcolor=paper)
rotated.crop((465, 520, 1135, 995)).resize((1200, 850), Image.Resampling.LANCZOS).save(
    Path(__file__).resolve().parents[1] / "src/assets/atlas/parcel-study.webp",
    quality=89,
    method=6,
)
