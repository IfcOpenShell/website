#!/usr/bin/env python3
"""Generates the Bonsai feature-chip icons (bx-chip-ico) as standalone SVGs.

Follows the visual language of assets/images/downloads/*.svg: a 32x32 grid,
3 unit ribbon strokes, a green to lime gradient, and one orange to yellow accent.

Usage: python3 generate.py   (writes *.svg next to this file)
"""
import os

GREEN = ("#079444", "#b8db30")
ORANGE = ("#f1592a", "#f5c132")

# Shorthand attribute sets. G = green, O = orange accent; s = stroked, f = filled.
def stroke(grad, width=3, cap="round"):
    return f'fill="none" stroke="url(#{grad})" stroke-width="{width}" stroke-linecap="{cap}" stroke-linejoin="round"'


def gs(width=3, cap="round"):
    return stroke("g", width, cap)


def os_(width=3, cap="round"):
    return stroke("o", width, cap)


Gs = gs()
Os = os_()
Gf = 'fill="url(#g)"'
Of = 'fill="url(#o)"'

# name: (orange gradient vector x1 y1 x2 y2, body)
ICONS = {
    # ---- Home ------------------------------------------------------------
    "free-forever": ((17, 22, 29, 10), f"""
        <path {Gs} d="M16 16c-2.6-3.6-4.6-5.5-7.5-5.5a5.5 5.5 0 0 0 0 11c2.9 0 4.9-1.9 7.5-5.500"/>
        <path {Os} d="M16 16c2.600 3.600 4.600 5.500 7.500 5.500a5.500 5.500 0 0 0 0-11c-2.900 0-4.900 1.900-7.500 5.500"/>"""),
    "native-ifc": ((5, 12, 27, 3), f"""
        <path {Of} stroke="url(#o)" stroke-width="1.6" stroke-linejoin="round" d="M16 3.800 25.800 9.300 16 14.800 6.200 9.300z"/>
        <path {Gf} stroke="url(#g)" stroke-width="1.6" stroke-linejoin="round" d="M4.800 12.200 14.600 17.700v10.800L4.800 23z"/>
        <path {Gf} stroke="url(#g)" stroke-width="1.6" stroke-linejoin="round" opacity=".72" d="M27.200 12.200 17.400 17.700v10.800L27.200 23z"/>"""),
    "no-lock-in": ((18, 14, 30, 2), f"""
        <path {Os} d="M19.500 13.500V9a5 5 0 0 1 9.600-1.900"/>
        <path {Gf} fill-rule="evenodd" d="M6 13.500h15a3 3 0 0 1 3 3V26a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-9.500a3 3 0 0 1 3-3zm7.500 4.300a2.400 2.400 0 0 0-1.300 4.400v2.600h2.600v-2.600a2.400 2.400 0 0 0-1.300-4.400z"/>"""),

    # ---- Studio ----------------------------------------------------------
    "audit-analyse": ((3, 14, 29, 3), f"""
        <path {gs(4)} d="M6 28v-6M13 28V17M20 28v-8M27 28V14"/>
        <path {os_(2.6)} d="M4.500 13.500 12.500 7l7 4 8-7"/>
        <path {os_(2.6)} d="M22.500 3.800h5.200V9"/>"""),
    "structural-analysis": ((16, 13, 16, 2), f"""
        <path {gs(4)} d="M3.500 16.500h25"/>
        <path {gs(2.6)} d="M7.500 20.500 4 27h7zM24.500 20.500 21 27h7z"/>
        <path {Os} d="M16 3v7.500"/>
        <path {Os} d="M12 7.500l4 4 4-4"/>"""),
    "mep-systems": ((4, 28, 28, 4), f"""
        <path {gs(6, "butt")} d="M2.500 11h12a7 7 0 0 1 7 7v11.500"/>
        <path {os_(3.4)} d="M9 5v12M15.500 23h12"/>"""),
    "costing-scheduling": ((9, 19, 25, 13), f"""
        <path {gs(2.6)} d="M4 3.500v25"/>
        <path {gs(4.5)} d="M9.500 8h9"/>
        <path {os_(4.5)} d="M13.500 16h11.500"/>
        <path {gs(4.5)} d="M20 24h7.500"/>"""),
    "facility-management": ((17, 22, 30, 12), f"""
        <circle {Gs} cx="9.500" cy="16" r="5.500"/>
        <path {Gs} d="M15 16h13.500"/>
        <path {Os} d="M22 16.500v5.500M27.500 16.500v4"/>"""),
    "fully-scriptable": ((12, 27, 20, 5), f"""
        <path {Gs} d="M10 9 3.500 16 10 23M22 9l6.500 7L22 23"/>
        <path {Os} d="M18.500 5.500 13.500 26.500"/>"""),

    # ---- Viewer ----------------------------------------------------------
    "saved-views": ((11, 23, 21, 9), f"""
        <path {Gs} d="M3.500 10V6.500a3 3 0 0 1 3-3H10M22 3.500h3.500a3 3 0 0 1 3 3V10M28.500 22v3.500a3 3 0 0 1-3 3H22M10 28.500H6.500a3 3 0 0 1-3-3V22"/>
        <path {Of} stroke="url(#o)" stroke-width="2" stroke-linejoin="round" d="M11.500 9.500h9v13L16 18.800l-4.500 3.700z"/>"""),
    "search": ((19, 29, 29, 19), f"""
        <circle {Gs} cx="13" cy="13" r="8.500"/>
        <path {os_(4)} d="M20.500 20.500 28 28"/>"""),
    "filter-colour-code": ((11, 29, 21, 17), f"""
        <path {Gf} stroke="url(#g)" stroke-width="2.400" stroke-linejoin="round" d="M4.500 5h23l-8.300 10.500h-6.400z"/>
        <path {Of} stroke="url(#o)" stroke-width="2.400" stroke-linejoin="round" d="M12.800 19.500h6.400v5.300l-6.400 3z"/>"""),
    "bulk-edit-spreadsheets": ((12, 21, 21, 14), f"""
        <path {Gf} d="M6.500 4h19A3.500 3.500 0 0 1 29 7.500V11H3V7.500A3.500 3.500 0 0 1 6.500 4z"/>
        <path {gs(2.6)} d="M4.300 11v13.500a3 3 0 0 0 3 3h17.400a3 3 0 0 0 3-3V11M4.300 19.500h23.400M12 11v16.500M20.500 11v16.500"/>
        <rect {Of} x="12" y="12.300" width="8.500" height="7.200"/>"""),
    "audit-ids": ((10, 24, 23, 12), f"""
        <path {Gs} d="M11.500 6H8.500a3 3 0 0 0-3 3v16.500a3 3 0 0 0 3 3h15a3 3 0 0 0 3-3V9a3 3 0 0 0-3-3h-3"/>
        <rect {Gf} x="11" y="2.500" width="10" height="6" rx="2"/>
        <path {Os} d="M10.500 18.500l4 4 7.500-8.500"/>"""),
    "clash-detection": ((12, 20, 20, 12), f"""
        <rect {Gs} x="3.500" y="3.500" width="16.500" height="16.500" rx="3"/>
        <rect {Gs} x="12" y="12" width="16.500" height="16.500" rx="3"/>
        <rect {Of} x="13.500" y="13.500" width="5" height="5" rx=".8"/>"""),
    "bcf-issues": ((16, 20, 16, 7), f"""
        <path {Gs} d="M6.500 4.500h19a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H16l-7 6v-6H6.500a3 3 0 0 1-3-3v-12a3 3 0 0 1 3-3z"/>
        <path {Os} d="M16 8.500v5"/>
        <circle {Of} cx="16" cy="18" r="1.700"/>"""),
    "model-federation": ((5, 14, 27, 3), f"""
        <path {Of} stroke="url(#o)" stroke-width="2" stroke-linejoin="round" d="M16 4 27.500 10 16 16 4.500 10z"/>
        <path {Gs} d="M4.500 16 16 22l11.500-6M4.500 22 16 28l11.500-6"/>"""),
    "cloud-sync": ((11, 24, 21, 12), f"""
        <path {Gs} d="M9.500 25.500a6 6 0 0 1-.9-11.900 7.500 7.500 0 0 1 14.600-1.300A6.600 6.600 0 0 1 22.500 25.500"/>
        <path {Os} d="M16 28V17.500M11.800 21.200 16 17l4.200 4.200"/>"""),

    # ---- Web -------------------------------------------------------------
    "nothing-to-install": ((5, 9, 14, 5), f"""
        <rect {Gs} x="3.500" y="4.500" width="25" height="23" rx="3"/>
        <path {gs(2.6)} d="M3.500 11.500h25"/>
        <circle {Of} cx="7.800" cy="8" r="1.300"/>
        <circle {Of} cx="11.800" cy="8" r="1.300"/>
        <path {os_(2.6)} d="M17.500 14.500 13 20h6l-4.500 5.500" transform="translate(0 -.3)"/>"""),
    "share-anywhere": ((2, 22, 14, 10), f"""
        <path {gs(2.6)} d="M9 16 23.500 7.500M9 16l14.500 8.500"/>
        <circle {Gf} cx="23.500" cy="7.500" r="4.500"/>
        <circle {Gf} cx="23.500" cy="24.500" r="4.500"/>
        <circle {Of} cx="8.500" cy="16" r="5"/>"""),
    "private-by-default": ((12, 23, 20, 11), f"""
        <path {Gs} d="M16 3.500 27 7.500v7.500c0 6.800-4.700 11-11 13.500C9.700 26 5 21.800 5 15V7.500z"/>
        <path {Of} d="M16 11a3 3 0 0 0-1.600 5.500V21h3.200v-4.500A3 3 0 0 0 16 11z"/>"""),
}

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="32mm" height="32mm" viewBox="0 0 32 32">
<defs>
<linearGradient id="g" x1="4" y1="28" x2="28" y2="4" gradientUnits="userSpaceOnUse"><stop stop-color="{g0}" offset="0"/><stop stop-color="{g1}" offset="1"/></linearGradient>
<linearGradient id="o" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="userSpaceOnUse"><stop stop-color="{o0}" offset="0"/><stop stop-color="{o1}" offset="1"/></linearGradient>
</defs>{body}
</svg>
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for name, ((x1, y1, x2, y2), body) in ICONS.items():
        body = "\n".join(line.strip() for line in body.splitlines())
        svg = TEMPLATE.format(g0=GREEN[0], g1=GREEN[1], o0=ORANGE[0], o1=ORANGE[1], x1=x1, y1=y1, x2=x2, y2=y2, body=body)
        with open(os.path.join(here, name + ".svg"), "w") as f:
            f.write(svg)
    print(f"Wrote {len(ICONS)} icons to {here}")
