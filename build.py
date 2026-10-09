#!/usr/bin/env python3
"""
Build an InkyPinky GTK 3/4 (and gnome-shell) theme from the Catppuccin-GnomeTheme base.

Every colour the base theme carries -- the Catppuccin core palette, the ad-hoc
surface shades the original author sprinkled through the stylesheet, the
libadwaita `blue_1..dark_5` tonal ramps, the Tango/XFCE `STRAWBERRY_100..` ramp
constants, the 14 `avatar.colorN` gradients and the hex stops inside the SVG
assets -- is remapped onto the Omarchy InkyPinky palette.

    ~/.config/omarchy/themes/inkypinky/colors.toml
        background = #13131D   foreground = #c8c8c8   accent = #7c7ca8

    python3 build.py [--src BASE] [--dst OUT] [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# The InkyPinky palette
# ---------------------------------------------------------------------------
# Surfaces form a five-step ramp on the ink background. Two steps (#191923 and
# #2B2B35) are taken verbatim from the theme's own vencord/shell definitions;
# the deepest (#0B0B12) stands in for Catppuccin's crust.
INK      = "#13131d"   # background / color0
INK_1    = "#0f0f17"   # mantle
INK_0    = "#0b0b12"   # crust
SURF_1   = "#191923"   # vencord base01
SURF_2   = "#2b2b35"   # vencord base02
SURF_3   = "#434353"   # color8 / bright_black
FG       = "#c8c8c8"   # foreground
DIM      = "#a1a2a7"   # color7
ACCENT   = "#7c7ca8"   # color4 / accent
MAGENTA  = "#9f859f"   # color5
CYAN     = "#919ab7"   # color6
GREEN    = "#a6b2c7"   # color2
B_GREEN  = "#d1d9e4"   # color10
RED      = "#ea90a8"   # color1
B_RED    = "#f6bfce"   # color9
YELLOW   = "#d18ba2"   # color3
B_YELLOW = "#e3aebf"   # color11
B_BLUE   = "#bcbcd4"   # color12
B_MAGENT = "#bfadbf"   # color13
B_CYAN   = "#d2d7e3"   # color14
BRIGHT   = "#fafafa"   # shell.toml bar/launcher text
ACCENT_DIM = "#5e5c8a"
ON_INK   = INK.lstrip("#")   # the text colour that sits on top of the accent

# ---------------------------------------------------------------------------
# 1. Core Catppuccin palette
# ---------------------------------------------------------------------------
CORE = {
    # surfaces
    "#1e1e2e": INK, "#181825": INK_1, "#11111b": INK_0, "#313244": SURF_1,
    "#393947": SURF_2, "#484856": SURF_2, "#282938": SURF_1, "#333342": SURF_2,
    "#242434": SURF_1, "#35353d": SURF_1, "#4d4d54": SURF_3, "#3d3e4c": SURF_2,
    "#444556": SURF_3, "#34343f": INK_1, "#292936": INK_1, "#222234": INK_1,
    "#0a0a0f": INK_0, "#14141f": INK_1, "#060609": INK_0, "#292c3c": SURF_1,
    "#393b50": SURF_2, "#2b2c3b": SURF_1, "#3e3e5f": SURF_2, "#5d5d6a": SURF_3,
    "#16191a": SURF_1, "#2b3133": SURF_2, "#515151": SURF_3, "#292929": SURF_1,
    "#424242": SURF_3, "#202020": INK_1, "#1e1e1e": INK_1, "#191919": INK_1,
    "#605955": SURF_3, "#6e6d71": SURF_3,

    # text
    "#eff1f5": FG, "#a6adc8": DIM, "#b0b2b9": DIM, "#c0bfbc": DIM,
    "#9a9996": DIM, "#77767b": DIM, "#d8d7d3": DIM, "#e5d6ca": FG,

    # accent (Catppuccin maroon occupies the accent slot)
    "#eba0ac": ACCENT, "#875e69": ACCENT_DIM, "#ce8cd7": MAGENTA,
    "#2861c6": ACCENT, "#eb5ec3": MAGENTA, "#6d53e0": ACCENT, "#393484": INK,
    "#ef4e9b": MAGENTA, "#f77466": RED, "#5e5c64": ACCENT_DIM,

    # status colours
    "#f38ba8": RED, "#f9e2af": YELLOW, "#f9e2a7": B_YELLOW, "#a6e3a1": GREEN,
    "#fab387": B_YELLOW, "#89b4fa": B_BLUE, "#cba6f7": MAGENTA, "#89dceb": CYAN,
    "#c01c28": RED,

    # lighter/darker siblings of the status colours
    "#f4cad1": B_RED, "#e78b9a": B_RED, "#f2a5bb": B_RED, "#f0b9c2": B_RED,
    "#f17497": RED, "#efb5be": B_RED, "#ecacb7": B_RED, "#f7e6c1": B_RED,
    "#f7d997": YELLOW, "#f5cd76": B_YELLOW, "#ed547e": YELLOW,
    "#b8e7b6": B_GREEN, "#79d572": GREEN, "#6ed166": GREEN, "#f4c868": B_YELLOW,
    "#ec4674": RED, "#f5d180": B_YELLOW, "#ae7b03": YELLOW, "#cd9309": YELLOW,
    "#d61f2d": RED, "#a11722": RED,

    # libadwaita blues
    "#337fdc": B_BLUE, "#1c71d8": ACCENT, "#0b2e52": INK_1, "#1862af": ACCENT,
    "#0f9ac8": CYAN, "#29ae74": GREEN,

    # avatar ramp stops
    "#cfe1f5": B_CYAN, "#83b6ec": B_BLUE, "#caeaf2": B_CYAN, "#7ad9f1": CYAN,
    "#cef8d8": B_GREEN, "#8de6b1": GREEN, "#e6f9d7": B_GREEN, "#b5e98a": B_GREEN,
    "#6ab85b": CYAN, "#f8e359": B_RED, "#d29d09": YELLOW, "#ffcb62": B_RED,
    "#d68400": YELLOW, "#ffa95a": B_RED, "#ed5b00": RED, "#f78773": B_RED,
    "#e62d42": RED, "#e973ab": RED, "#e33b6a": RED, "#cb78d4": MAGENTA,
    "#9945b5": ACCENT, "#9e91e8": ACCENT, "#7a59ca": ACCENT, "#e3cf9c": B_YELLOW,
    "#b08952": MAGENTA, "#be916d": MAGENTA, "#785336": SURF_3,
    "#f9f4e1": B_RED, "#ffead1": B_RED, "#ffe5c5": B_RED, "#f8d2ce": B_RED,
    "#fac7de": B_RED, "#e7c2e8": B_MAGENT, "#d5d2f5": B_BLUE, "#f2eade": B_RED,
    "#29ae74": GREEN, "#27a66c": GREEN, "#333": SURF_3,

    # The one light card in the whole theme: gnome-software's "work" tile, which
    # is a sheet of graph paper. A warm off-white keeps it reading as paper
    # against the ink surfaces instead of becoming just another dark tile.
    "#fdf8d7": "#f3ece9",
    "#fefcef": "#f8f2f0",
    "#fcf4bf": "#f6e8e4",
}

# ---------------------------------------------------------------------------
# 2. rgb()/rgba() triplets
# ---------------------------------------------------------------------------
RGB = {
    "239,241,245": FG.lstrip("#"),
    "17,17,27":    ON_INK,
    "235,160,172": ACCENT.lstrip("#"),
    "221,151,163": ACCENT.lstrip("#"),
    "181,125,136": ACCENT.lstrip("#"),
    "187,109,133": ACCENT.lstrip("#"),
    "243,139,168": RED.lstrip("#"),
    "249,226,175": YELLOW.lstrip("#"),
    "166,227,161": GREEN.lstrip("#"),
    "137,180,250": B_BLUE.lstrip("#"),
    "250,179,135": B_YELLOW.lstrip("#"),
    "225,229,233": FG.lstrip("#"),
    "178,191,203": FG.lstrip("#"),
    "201,216,232": FG.lstrip("#"),
    "21,22,24":    ON_INK,
    "30,30,46":    ON_INK,
    "49,50,68":    SURF_1.lstrip("#"),
    "33,35,37":    SURF_1.lstrip("#"),
    "33,33,50":    SURF_1.lstrip("#"),
    "48,48,48":    SURF_2.lstrip("#"),
    "35,38,40":    SURF_1.lstrip("#"),
    "47,51,54":    SURF_2.lstrip("#"),
    "57,63,70":    SURF_3.lstrip("#"),
    "56,63,71":    SURF_3.lstrip("#"),
    "78,89,99":    SURF_3.lstrip("#"),
    "60,60,66":    SURF_3.lstrip("#"),
    "38,66,94":    SURF_3.lstrip("#"),
    "163,209,254": B_CYAN.lstrip("#"),
    "140,191,242": B_CYAN.lstrip("#"),
    "111,173,235": B_BLUE.lstrip("#"),
    "65,140,214":  ACCENT.lstrip("#"),
    "7,25,43":     INK_1.lstrip("#"),
    "19,56,93":    SURF_1.lstrip("#"),
    "205,147,9":   YELLOW.lstrip("#"),
    "192,28,40":   RED.lstrip("#"),
    "163,178,193": FG.lstrip("#"),
    "233,242,250": FG.lstrip("#"),
    "35,50,66":    SURF_1.lstrip("#"),
    "11,11,18":    INK_0.lstrip("#"),
    # `0,0,0`, `255,255,255` and `255,0,0` are absolute shadows and the error
    # red, and are deliberately left alone.
}

# ---------------------------------------------------------------------------
# 3. Tonal ramps (`blue_1..blue_5`, `STRAWBERRY_100..`, `light_1..`, ...)
# ---------------------------------------------------------------------------
# Each family gets a two-anchor InkyPinky ramp. Stops are reassigned in the
# original luminance order, so a ramp that went light->dark still does.
FAMILY = {
    "red":    ("#a1768c", "#f9c8d3"),
    "orange": ("#a98f8c", "#f9d5c9"),
    "yellow": ("#b2909f", "#f9e0d4"),
    "green":  ("#8f96a8", "#d8dde6"),
    "blue":   ("#7c7ca8", "#bcbcd4"),
    "purple": ("#8d84a8", "#c9bed9"),
    "brown":  ("#8f8290", "#cdc0bd"),
    "silver": ("#2b2b35", "#a1a2a7"),
    "slate":  ("#13131d", "#5a5a62"),
    "light":  ("#434353", "#ffffff"),
    # `dark` stops well short of the light end: gnome-software's category tiles
    # print white text on `dark_2`.
    "dark":   ("#13131d", "#5a5a62"),
}

RAMPS = {
    "STRAWBERRY": "red", "ORANGE": "orange", "BANANA": "yellow", "LIME": "green",
    "BLUEBERRY": "blue", "GRAPE": "purple", "COCOA": "brown",
    "SILVER": "silver", "SLATE": "slate", "BLACK": "dark",
    "blue": "blue", "green": "green", "yellow": "yellow", "orange": "orange",
    "red": "red", "purple": "purple", "brown": "brown",
    "light": "light", "dark": "dark",
}

# Colours that are metadata or a deliberately absolute black, kept as-is.
# `#ffffff` and `#000000` are *not* in here: they are `light_1` and `dark_5`
# in the tonal ramps, so they have to move with their ramp rather than stay.
KEEP = {"#000"}


# ---------------------------------------------------------------------------
# 4. The 14 libadwaita `avatar.colorN` gradients
# ---------------------------------------------------------------------------
AVATARS = [
    (B_CYAN,   CYAN,    INK),
    (B_BLUE,   ACCENT,  INK),
    (B_GREEN,  GREEN,   INK),
    (B_CYAN,   CYAN,    INK),
    (B_RED,    RED,     INK),
    (B_RED,    YELLOW,  INK),
    (B_YELLOW, MAGENTA, INK),
    (B_RED,    RED,     INK),
    (RED,      YELLOW,  INK),
    (B_RED,    MAGENTA, INK),
    (B_BLUE,   ACCENT,  INK),
    (B_MAGENT, MAGENTA, INK),
    (DIM,      SURF_3,  BRIGHT),
    (ACCENT,   SURF_3,  BRIGHT),
]


# ---------------------------------------------------------------------------
# colour helpers
# ---------------------------------------------------------------------------
def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def lum(rgb: tuple[int, int, int]) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def tint(dark: str, light: str, t: float) -> str:
    d, l = hex2rgb(dark), hex2rgb(light)
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, round(d[i] + (l[i] - d[i]) * t))) for i in range(3)
    )


# ---------------------------------------------------------------------------
# map builders
# ---------------------------------------------------------------------------
def core_map() -> dict[str, str]:
    return {k.lower(): v.lower() for k, v in CORE.items()}


def ramp_map(root: Path) -> dict[str, str]:
    """Find every concrete colour a legacy ramp family declares, then reassign."""
    found: dict[str, set[str]] = {n: set() for n in RAMPS}
    pat = re.compile(
        r"@define-color\s+(" + "|".join(sorted(RAMPS)) + r")_([0-9]+)\s+(#[0-9a-fA-F]{3,8})\b"
    )
    for path in root.rglob("*.css"):
        for m in pat.finditer(path.read_text()):
            found[m.group(1)].add(m.group(3).lower())

    out: dict[str, str] = {}
    for family, colors in found.items():
        if not colors:
            continue
        dark, light = FAMILY[RAMPS[family]]
        lums = {c: lum(hex2rgb(c)) for c in colors}
        lo, hi = min(lums.values()), max(lums.values())
        ordered = sorted(colors, key=lambda c: lums[c])   # dark -> light
        n = len(ordered)
        for i, color in enumerate(ordered):
            out[color] = light if i == n - 1 else tint(dark, light, i / (n - 1))
    return out


AVATAR_DECL = re.compile(
    r"avatar\.color\d+\s*\{\s*background-image:\s*linear-gradient\(\s*"
    r"(#[0-9a-fA-F]{3,8})\s*,\s*(#[0-9a-fA-F]{3,8})\s*\)\s*;"
    r"\s*color:\s*(#[0-9a-fA-F]{3,8})\s*;",
    re.S,
)


def avatar_map(root: Path) -> dict[str, str]:
    text = "\n".join(p.read_text() for p in sorted(root.rglob("*.css")))
    seen: dict[tuple[str, str, str], None] = {}
    for m in AVATAR_DECL.finditer(text):
        seen.setdefault(tuple(c.lower() for c in m.groups()), None)
    decls = list(seen)
    if len(decls) != len(AVATARS):
        raise SystemExit(f"expected {len(AVATARS)} avatar rules, found {len(decls)}")
    out: dict[str, str] = {}
    for (a, b, c), (light, dark, fg) in zip(decls, AVATARS):
        out[a.lower()] = light
        out[b.lower()] = dark
        out[c.lower()] = fg
    return out


# ---------------------------------------------------------------------------
# rewriting
# ---------------------------------------------------------------------------
# A CSS hex colour needs a delimiter before the '#'. `colorswatch#add-color-button`
# is an ID selector, and without this lookbehind the regex happily eats `#add`.
HEX_RE = re.compile(r"(?<![A-Za-z0-9_\-])#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(
    r"rgba?\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)((?:\s*,\s*[0-9.]+)?)\s*\)"
)


def rewrite(text: str, hexmap: dict[str, str], *, svg: bool) -> str:
    def _rgb(m: re.Match) -> str:
        key = f"{m.group(1)},{m.group(2)},{m.group(3)}"
        new = RGB.get(key)
        if new is None:
            return m.group(0)
        alpha = (m.group(4) or "").replace(" ", "")
        if not alpha:
            return f"#{new}"
        # GTK's `rgba()` only takes three numbers -- a hex literal inside it is a
        # parse error. `alpha(colour, factor)` is the GTK idiom and keeps the
        # palette reference readable.
        return f"alpha(#{new},{alpha.lstrip(',')})"

    text = RGB_RE.sub(_rgb, text)

    def _hex(m: re.Match) -> str:
        original = m.group(0)
        low = original.lower()
        if low in KEEP:
            return original
        new = hexmap.get(low)
        if new is None:
            return original
        return new if original.islower() else new.upper()

    return HEX_RE.sub(_hex, text)


INDEX_THEME = """Type=X-GNOME-Metatheme
[Desktop Entry]
Name=InkyPinky
Comment=GTK theme matching the Omarchy InkyPinky palette
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=InkyPinky
MetacityTheme=InkyPinky
IconTheme=Papirus-Dark
CursorTheme=default
ButtonLayout=close,minimize,maximize:menu
"""


def ship_thpm(dst: Path, omarchy: Path) -> None:
    """
    The base theme's gtk-4.0/gtk.css opens with

        @import url("thpm-theme.css");

    which never resolves, because the file it is looking for lives in
    ~/.config/gtk-4.0/ -- not in the theme directory GTK resolves the URL
    against. It has been logging a parse warning and doing nothing ever since.

    Shipping the Omarchy palette there fixes it and, as a side effect, gives GTK 4
    the named colours (`background`, `accent_bg_color`, ...) that GTK 3 already
    gets from ~/.config/gtk-3.0/gtk.css. The theme's own @define-color block sits
    *after* the import, so it still wins on every overlapping name.
    """
    src = omarchy / "gtk.css"
    if not src.is_file():
        print(f"note: no omarchy gtk.css at {src}; import left unresolved")
        return
    shutil.copyfile(src, dst / "gtk-4.0" / "thpm-theme.css")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="~/.themes/Catppuccin-GnomeTheme")
    ap.add_argument("--dst", default="~/.themes/InkyPinky")
    ap.add_argument("--omarchy", default="~/.config/omarchy/themes/inkypinky",
                    help="theme dir supplying the Omarchy named-colour palette")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src, dst = Path(args.src).expanduser(), Path(args.dst).expanduser()
    if not src.is_dir():
        print(f"error: {src} not found", file=sys.stderr)
        return 1

    hexmap = core_map()
    hexmap.update(ramp_map(src))
    hexmap.update(avatar_map(src))

    if args.dry_run:
        for k in sorted(hexmap):
            print(f"{k:>9} -> {hexmap[k]}")
        return 0

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    for path in sorted(dst.rglob("*")):
        if not path.is_file():
            continue
        try:
            body = path.read_text()
        except UnicodeDecodeError:
            continue                      # real binary asset: leave it alone
        # `thumbnail.png` is misleadingly named -- it is an inline SVG preview of
        # the theme's titlebar and accent, so it gets recoloured like any other.
        is_svg = path.suffix == ".svg" or body.lstrip()[:5] in ("<svg", "<?xml")
        after = rewrite(body, hexmap, svg=is_svg)
        if after != body:
            path.write_text(after)

    (dst / "index.theme").write_text(INDEX_THEME)
    ship_thpm(dst, Path(args.omarchy).expanduser())
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
