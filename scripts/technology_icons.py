"""Embed static pixel-art technology icons directly in the profile's SVG assets."""
from functools import lru_cache
from html import escape
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "icons"
ET.register_namespace("", "http://www.w3.org/2000/svg")
ALIASES = {
    "Python": "python", "Python subset": "python", "Java": "java",
    "TypeScript": "typescript", "C#": "csharp", "Claude Code": "claudecode",
    "Codex": "codex", "Unity": "unity", "Unreal Engine 5": "unrealengine",
    "Nmap": "scanner", "Metasploit": "metasploit", "Hydra": "key",
    "John the Ripper": "password", "Kali Linux": "kalilinux", "BlackArch": "blackarch",
    "React": "react", "FastAPI": "fastapi", "Roblox": "roblox", "Luau": "luau",
    "Spring Boot": "spring", "JPA": "database", "OpenAI API": "ai",
    "Swing": "window", "Firebase": "firebase",
}


@lru_cache(maxsize=None)
def source(name):
    root = ET.parse(ASSETS / "pixel" / (ALIASES[name] + ".svg")).getroot()
    children = "".join(ET.tostring(e, encoding="unicode") for e in root
                       if e.tag.rsplit("}", 1)[-1] not in {"title", "desc"})
    return root.get("viewBox"), children, {key: value for key, value in root.attrib.items()
                                         if key in {"fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"}}


def icon(name, x, y, size=28):
    viewbox, children, style = source(name)
    attributes = " ".join(f'{key}="{value}"' for key, value in style.items())
    return (f'<svg x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" '
            f'viewBox="{viewbox}" {attributes} shape-rendering="crispEdges" data-pixel-grid="16" aria-hidden="true" '
            f'data-technology="{escape(name, quote=True)}">{children}</svg>')


def technology_row(stack, center=160, baseline=347, size=10.5):
    metrics = json.loads((ASSETS / "text-metrics.json").read_text())
    names = stack.split(" · ")
    widths = [sum(metrics.get(char, .56) for char in name) * size for name in names]
    icon_size, gap, between = 12, 4, 13
    width = sum(widths) + len(names) * (icon_size + gap) + (len(names) - 1) * between
    assert width <= 280, (stack, width)
    x = center - width / 2
    out = '<g data-technology-row="true">'
    for name, text_width in zip(names, widths):
        out += icon(name, x, baseline - 10, icon_size)
        x += icon_size + gap
        out += (f'<text x="{x:g}" y="{baseline:g}" font-family="Arial,Helvetica,sans-serif" '
                f'font-size="{size:g}" fill="#7B8494">{escape(name)}</text>')
        x += text_width + between
    return out + '</g>'
