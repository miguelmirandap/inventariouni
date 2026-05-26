from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIZE = 64
OUT_DIR = Path(__file__).resolve().parent
ICO_PATH = OUT_DIR / "icon_taza_check.ico"
PNG_PATH = OUT_DIR / "icon_taza_check.png"


def rgba(r: int, g: int, b: int, a: int = 255) -> tuple[int, int, int, int]:
    return (r, g, b, a)


def clamp(v: int) -> int:
    return max(0, min(255, v))


def put(px: list[list[tuple[int, int, int, int]]], x: int, y: int, color: tuple[int, int, int, int]) -> None:
    if 0 <= x < SIZE and 0 <= y < SIZE:
        px[y][x] = color


def fill_rect(px, x0: int, y0: int, x1: int, y1: int, color) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(px, x, y, color)


def fill_circle(px, cx: int, cy: int, r: int, color) -> None:
    r2 = r * r
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                put(px, x, y, color)


def draw_line(px, x0: int, y0: int, x1: int, y1: int, color, thickness: int = 1) -> None:
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        for oy in range(-thickness // 2, thickness // 2 + 1):
            for ox in range(-thickness // 2, thickness // 2 + 1):
                put(px, x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def rounded_panel(px) -> None:
    bg = rgba(245, 236, 220)
    shadow = rgba(223, 204, 171)

    fill_rect(px, 7, 7, 57, 57, shadow)
    fill_rect(px, 6, 6, 56, 56, bg)
    for (cx, cy) in [(6, 6), (55, 6), (6, 55), (55, 55)]:
        fill_circle(px, cx, cy, 6, bg)


def draw_cup(px) -> None:
    cup = rgba(112, 77, 48)
    cup_light = rgba(156, 113, 74)
    white = rgba(255, 250, 240)

    # Saucer and cup body
    fill_rect(px, 16, 43, 47, 47, cup)
    fill_rect(px, 16, 28, 45, 43, cup_light)
    fill_rect(px, 18, 30, 43, 41, white)

    # Cup handle
    for r in range(0, 5):
        fill_circle(px, 46, 35, 7 - r, cup)
    fill_circle(px, 46, 35, 3, rgba(245, 236, 220))

    # Steam lines
    steam = rgba(171, 143, 111)
    draw_line(px, 24, 24, 22, 16, steam, 2)
    draw_line(px, 31, 24, 30, 14, steam, 2)
    draw_line(px, 38, 24, 40, 16, steam, 2)


def draw_check(px) -> None:
    green = rgba(13, 128, 96)
    green_dark = rgba(7, 101, 75)

    fill_circle(px, 46, 46, 12, green)
    draw_line(px, 39, 46, 45, 52, rgba(232, 255, 245), 3)
    draw_line(px, 45, 52, 54, 40, rgba(232, 255, 245), 3)

    # subtle border
    for t in range(1, 3):
        draw_line(px, 39, 46 - t, 45, 52 - t, green_dark, 1)
        draw_line(px, 45, 52 - t, 54, 40 - t, green_dark, 1)


def to_png_bytes(px) -> bytes:
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)  # no filter
        for x in range(SIZE):
            raw.extend(px[y][x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=9)

    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def save_ico_with_png(png_data: bytes) -> None:
    # ICO header: reserved(0), type(1), count(1)
    header = struct.pack("<HHH", 0, 1, 1)

    # Directory entry for 64x64 PNG.
    # width=64, height=64, colors=0, reserved=0, planes=1, bpp=32
    image_offset = 6 + 16
    entry = struct.pack("<BBBBHHII", 64, 64, 0, 0, 1, 32, len(png_data), image_offset)

    ICO_PATH.write_bytes(header + entry + png_data)


def main() -> None:
    px = [[rgba(0, 0, 0, 0) for _ in range(SIZE)] for _ in range(SIZE)]
    rounded_panel(px)
    draw_cup(px)
    draw_check(px)

    png_data = to_png_bytes(px)
    PNG_PATH.write_bytes(png_data)
    save_ico_with_png(png_data)

    print(f"Icono PNG: {PNG_PATH}")
    print(f"Icono ICO: {ICO_PATH}")


if __name__ == "__main__":
    main()
