"""Render original rounded minimap artwork as 512px, antialiased RGBA TGA files.

No third-party assets or image libraries. Geometry is in native UI units:
198px map frame, inset rounded mask, and a native-style bronze cross-section.
"""
from pathlib import Path
import math
import struct

ROOT = Path(__file__).resolve().parents[1]
SIZE = 512
# UI-space geometry: the 220-unit border extends 11 units past the 198-unit map.
MAP_SIZE = 198
BORDER_SIZE = 220
BORDER_CENTER = BORDER_SIZE / 2
OUTER_INSET = 7
OUTER_RADIUS = 15.2
RIM_WIDTH = 8.2
# Half-length of a straight edge before its rounded corner begins.
STRAIGHT_HALF_EXTENT = 87.8
# The mask overlaps the inner rim by 0.6 units to prevent transparent seams.
MASK_INSET = 3.6
MASK_RADIUS = 7.6
PROFILE = (
    # Depth from outside to inside, derived from the aligned native rim sample.
    # Slight highlight compensation offsets downsampling at the in-game size.
    (0.0, (52, 30, 16)), (1.1, (48, 28, 10)),
    (1.9, (43, 25, 7)), (2.7, (46, 28, 9)),
    (3.5, (86, 67, 41)), (4.3, (160, 137, 98)),
    (5.1, (202, 176, 123)), (5.9, (184, 150, 100)),
    (6.7, (151, 119, 76)), (7.5, (116, 86, 53)),
    (8.3, (61, 45, 28)), (9.1, (18, 20, 18)),
    (10.2, (10, 21, 24)),
)
# The native rim's side faces have a lighter outer bevel and a softer highlight
# than its bottom edge. Blend at the rounded corners using the surface normal.
SIDE_PROFILE = (
    (0.0, (86, 63, 41)), (1.1, (92, 68, 42)),
    (1.9, (95, 70, 43)), (2.7, (100, 75, 47)),
    (3.5, (116, 89, 58)), (4.3, (165, 141, 106)),
    (5.1, (179, 155, 114)), (5.9, (152, 124, 86)),
    (6.7, (120, 91, 59)), (7.5, (102, 73, 44)),
    (8.3, (61, 45, 28)), (9.1, (18, 20, 18)),
    (10.2, (10, 21, 24)),
)
SHADOW = ((0, 1), (0.5, 0.76), (1.3, 0.49), (2.1, 0.25),
          (2.9, 0.10), (3.7, 0.03), (4.5, 0.008), (5.2, 0))


def distance(x, y, size, inset, radius):
    qx = abs(x - size / 2) - (size / 2 - inset - radius)
    qy = abs(y - size / 2) - (size / 2 - inset - radius)
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - radius


def sample(x, y, mask):
    if mask:
        # Slightly overlap the rim to avoid a transparent seam when downsampled.
        return (255, 255, 255, 255 if distance(x, y, MAP_SIZE, MASK_INSET, MASK_RADIUS) <= 0 else 0)
    # Compress the rim by one UI unit on each side of its existing centerline.
    # Outer radius: 16.2 - 1; inner radius: 15.2 - 8.2 = 7 UI units.
    d = distance(x, y, BORDER_SIZE, OUTER_INSET, OUTER_RADIUS)
    qx = abs(x - BORDER_CENTER) - STRAIGHT_HALF_EXTENT
    qy = abs(y - BORDER_CENTER) - STRAIGHT_HALF_EXTENT
    side = qx / math.hypot(qx, qy) if qx > 0 and qy > 0 else float(qx > qy)
    # Carry the lighter bevel around the upper corners, leaving the lower
    # face darker instead of making every edge equally bright or black.
    side = 0.65 + 0.35 * side if y < BORDER_CENTER else 0.10 + 0.90 * side
    if 0 < d < SHADOW[-1][0]:
        for (start, a), (end, b) in zip(SHADOW, SHADOW[1:]):
            if d <= end:
                return (31 + 18 * side, 15 + 18 * side, 2 + 21 * side,
                        255 * (a + (b - a) * (d - start) / (end - start)))
    if not -RIM_WIDTH <= d <= 0:
        return (0, 0, 0, 0)
    # Keep the complete bronze color profile and highlight centered.
    depth = -d * (PROFILE[-1][0] / RIM_WIDTH)
    for index, ((start, a), (end, b)) in enumerate(zip(PROFILE, PROFILE[1:])):
        if depth <= end:
            t = (depth - start) / (end - start)
            side_a, side_b = SIDE_PROFILE[index][1], SIDE_PROFILE[index + 1][1]
            base = [a[i] + (b[i] - a[i]) * t for i in range(3)]
            edge = [side_a[i] + (side_b[i] - side_a[i]) * t for i in range(3)]
            return (*[base[i] + (edge[i] - base[i]) * side for i in range(3)], 255)
    return (*PROFILE[-1][1], 255)


def render(mask):
    scale = (MAP_SIZE if mask else BORDER_SIZE) / SIZE
    pixels = bytearray()
    # Four area samples per output pixel; average premultiplied colors to
    # avoid dark fringes at transparent rounded corners.
    for y in range(SIZE):
        for x in range(SIZE):
            samples = [sample((x + dx) * scale, (y + dy) * scale, mask)
                       for dy in (0.25, 0.75) for dx in (0.25, 0.75)]
            alpha = sum(p[3] for p in samples)
            rgb = [round(sum(p[c] * p[3] for p in samples) / alpha) if alpha else 0
                   for c in range(3)]
            pixels.extend((*rgb, round(alpha / 4)))
    return pixels


def write_tga(path, rgba):
    # Uncompressed true-color TGA, bottom-left origin, 8 bits of alpha.
    header = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, SIZE, SIZE, 32, 8)
    bgra = bytearray()
    for y in reversed(range(SIZE)):
        for x in range(SIZE):
            i = (y * SIZE + x) * 4
            r, g, b, a = rgba[i:i + 4]
            bgra.extend((b, g, r, a))
    path.write_bytes(header + bgra)


def main():
    media = ROOT / 'Media'
    media.mkdir(exist_ok=True)
    for name, mask in (('SquareMinimapBorder5.tga', False), ('SquareMinimapMask3.tga', True)):
        write_tga(media / name, render(mask))
        print(f'Generated Media/{name} ({SIZE}x{SIZE}, RGBA)')


if __name__ == '__main__':
    main()
