#!/usr/bin/env python3
"""Convert the source SVG logos to static, crisp 16×16 pixel sprites.

Requires fonttools only when rebuilding these checked-in assets. The README and
project generator use the generated SVGs without any extra dependencies.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / 'assets' / 'icons'
SIZE = 16


class Pixels:
    def __init__(self):
        self.cells = set()

    def put(self, x, y):
        x, y = round(x), round(y)
        assert 0 <= x < SIZE and 0 <= y < SIZE, (x, y)
        self.cells.add((x, y))

    def line(self, a, b):
        x, y = a
        xx, yy = b
        dx, dy = abs(xx - x), -abs(yy - y)
        sx, sy = (1 if x < xx else -1), (1 if y < yy else -1)
        err = dx + dy
        while True:
            self.put(x, y)
            if (x, y) == (xx, yy):
                return
            twice = err * 2
            if twice >= dy:
                err += dy
                x += sx
            if twice <= dx:
                err += dx
                y += sy

    def polyline(self, points, close=False):
        points = points + points[:1] if close else points
        for a, b in zip(points, points[1:]):
            self.line(a, b)


def brand_pixels(path):
    root = ET.parse(path).getroot()
    vx, vy, width, height = map(float, root.get('viewBox').split())
    records = []
    for node in root:
        if node.tag.rsplit('}', 1)[-1] != 'path':
            continue
        pen = RecordingPen()
        parse_path(node.get('d'), pen)
        # Filled SVG subpaths are implicitly closed.
        pen.value = [('closePath' if name == 'endPath' else name, args)
                     for name, args in pen.value]
        records.append(pen)
    cells = set()
    for y in range(SIZE):
        for x in range(SIZE):
            inside = 0
            for ox, oy in [(.5,.5),(.25,.25),(.75,.25),(.25,.75),(.75,.75)]:
                point = (vx + (x + ox) * width / SIZE, vy + (y + oy) * height / SIZE)
                covered = False
                for record in records:
                    pen = PointInsidePen(None, point)
                    record.replay(pen)
                    covered |= pen.getResult()
                inside += covered
            if inside >= 2:
                cells.add((x, y))
    return cells


def utility_pixels(name):
    p = Pixels()
    if name == 'scanner':
        p.polyline([(1,8),(4,5),(7,4),(9,4),(12,5),(15,8),(12,11),(9,12),(7,12),(4,11)], True)
        p.polyline([(7,6),(9,6),(10,7),(10,9),(9,10),(7,10),(6,9),(6,7)], True)
        p.line((8,0),(8,2));p.line((8,14),(8,15))
    elif name == 'key':
        p.polyline([(3,1),(6,1),(8,3),(8,5),(6,7),(3,7),(1,5),(1,3)],True)
        p.line((7,7),(14,14));p.line((10,10),(12,8));p.line((12,12),(14,10))
    elif name in {'password','terminal','window'}:
        p.polyline([(2,2),(13,2),(14,3),(14,12),(13,13),(2,13),(1,12),(1,3)],True)
        if name == 'password':
            for x in [4,8,12]:
                p.line((x,6),(x,9));p.line((x-1,7),(x+1,7))
        elif name=='terminal':
            p.polyline([(4,5),(6,7),(4,9)]);p.line((8,10),(11,10))
        else:
            p.line((1,5),(14,5));p.line((4,8),(11,8));p.line((4,10),(8,10))
    elif name == 'database':
        p.polyline([(4,1),(11,1),(14,3),(14,12),(11,14),(4,14),(1,12),(1,3)],True)
        p.polyline([(1,3),(4,5),(11,5),(14,3)])
        p.polyline([(1,8),(4,10),(11,10),(14,8)])
    elif name == 'ai':
        p.polyline([(4,3),(11,3),(12,4),(12,11),(11,12),(4,12),(3,11),(3,4)],True)
        for a in [5,10]:
            p.line((a,0),(a,2));p.line((a,13),(a,15))
            p.line((0,a),(2,a));p.line((13,a),(15,a))
        p.polyline([(5,8),(7,10),(10,6)])
    else:
        raise ValueError(name)
    return p.cells


def java_pixels():
    # Keep the steam and cup separate at this small grid size.
    p = Pixels()
    p.polyline([(9,0),(9,2),(6,4),(6,5),(8,6)])
    p.polyline([(11,3),(9,5),(9,6),(10,7)])
    p.polyline([(3,8),(3,11),(5,12),(10,12),(12,10),(12,8)],True)
    p.polyline([(13,8),(14,8),(15,9),(15,10),(13,11)])
    p.polyline([(1,13),(2,14),(12,14),(14,13)])
    return p.cells


def python_pixels():
    # Two separate snakes keep the mark readable at 16×16.
    rows = [
        '.....WWWWWW.....',
        '....WWWWWWWW....',
        '....WW.WWWWW....',
        '....WWWWWWWW....',
        '....WWWWWWWW.BB.',
        'WWWWWWWWWWWW.BBB',
        'WWWWWWWWWWWW.BBB',
        'WWWWWW.......BBB',
        'WWW.......BBBBBB',
        'WWW.BBBBBBBBBBBB',
        'WWW.BBBBBBBBBBBB',
        '.WW.BBBBBBBB....',
        '....BBBBBBBB....',
        '....BBBBB.BB....',
        '....BBBBBBBB....',
        '.....BBBBBB.....',
    ]
    assert all(len(row)==SIZE for row in rows)
    return {color:{(x,y) for y,row in enumerate(rows) for x,c in enumerate(row) if c==symbol}
            for color,symbol in [('#F2F0E8','W'),('#4778FF','B')]}


def blackarch_pixels():
    # Arch silhouette and katana, redrawn from BlackArch's published logo.
    sword=Pixels()
    sword.line((8,0),(8,15));sword.line((7,0),(8,0))
    sword.line((6,4),(10,4))
    arch=Pixels()
    arch.polyline([(8,5),(1,14),(6,12),(6,10),(7,9),(8,9),(9,10),(9,12),(14,14)],True)
    arch.polyline([(5,9),(7,10),(6,8)])
    arch.polyline([(12,11),(11,11),(13,12)])
    return {'#F2F0E8':sword.cells-arch.cells,'#4778FF':arch.cells}


def svg_path(cells):
    commands=[]
    for y in range(SIZE):
        xs=sorted(x for x,yy in cells if yy==y)
        if not xs:
            continue
        first=last=xs[0]
        for x in xs[1:]+[None]:
            if x is not None and x==last+1:
                last=x
                continue
            width=last-first+1
            commands.append(f'M{first} {y}h{width}v1h-{width}z')
            if x is not None:
                first=last=x
    return ''.join(commands)


def main():
    dest=ICONS/'pixel'
    dest.mkdir(exist_ok=True)
    utility={'scanner','key','password','terminal','database','ai','window'}
    for source in sorted(ICONS.glob('*.svg')):
        name=source.stem
        cells=utility_pixels(name) if name in utility else brand_pixels(source)
        if name=='java':
            cells=java_pixels()
        assert cells, name
        layers=python_pixels() if name=='python' else blackarch_pixels() if name=='blackarch' else {'#F2F0E8':cells}
        paths=''.join(f'<path fill="{color}" d="{svg_path(points)}"/>' for color,points in layers.items())
        svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
             f'width="32" height="32" shape-rendering="crispEdges" data-pixel-grid="{SIZE}" '
             f'fill="#F2F0E8">{paths}</svg>')
        (dest/source.name).write_text(svg)
    print(f'Built {len(list(dest.glob("*.svg")))} static 16×16 pixel icons.')


if __name__=='__main__':
    main()
