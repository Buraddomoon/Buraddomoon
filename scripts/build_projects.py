#!/usr/bin/env python3
"""Build the profile's project gallery from projects.json. Python stdlib only."""
from html import escape
import json
from math import cos, pi, sin
from pathlib import Path
import re
from technology_icons import technology_row

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "projects"
COLORS = {"ink": "#101216", "white": "#F2F0E8", "gray": "#7B8494", "blue": "#4778FF"}
FRAMES = 96


class Pixels:
    def __init__(self):
        self.cells = {}

    def put(self, x, y, color):
        x, y = round(x), round(y)
        assert 0 <= x < 64 and 0 <= y < 56, (x, y)
        self.cells[x, y] = color

    def block(self, x, y, width, height, color):
        for row in range(round(y), round(y) + height):
            for col in range(round(x), round(x) + width):
                self.put(col, row, color)

    def line(self, start, end, color):
        x, y = map(round, start)
        xx, yy = map(round, end)
        dx, dy = abs(xx - x), -abs(yy - y)
        sx, sy = (1 if x < xx else -1), (1 if y < yy else -1)
        err = dx + dy
        while True:
            self.put(x, y, color)
            if (x, y) == (xx, yy):
                break
            twice = 2 * err
            if twice >= dy:
                err += dy
                x += sx
            if twice <= dx:
                err += dx
                y += sy

    def polyline(self, points, color, close=False):
        pairs = points + points[:1] if close else points
        for start, end in zip(pairs, pairs[1:]):
            self.line(start, end, color)

    def circle(self, cx, cy, radius, color, start=0, end=2 * pi):
        for n in range(181):
            a = start + (end - start) * n / 180
            self.put(cx + radius * cos(a), cy + radius * sin(a), color)

    def polygon(self, points, color):
        for y in range(min(p[1] for p in points),max(p[1] for p in points)+1):
            for x in range(min(p[0] for p in points),max(p[0] for p in points)+1):
                inside=False
                for (ax,ay),(bx,by) in zip(points,points[1:]+points[:1]):
                    if (ay>y+.5)!=(by>y+.5) and x+.5<(bx-ax)*(y+.5-ay)/(by-ay)+ax:
                        inside=not inside
                if inside:self.put(x,y,color)
        self.polyline(points,color,True)

    def path(self, color):
        out = []
        for y in range(56):
            xs = [x for x in range(64) if self.cells.get((x, y)) == color]
            if not xs:
                continue
            first = last = xs[0]
            for x in xs[1:] + [None]:
                if x is not None and x == last + 1:
                    last = x
                    continue
                width = (last - first + 1) * 4
                out.append(f"M{first*4} {y*4}h{width}v4h-{width}z")
                if x is not None:
                    first = last = x
        return "".join(out)

    def svg(self):
        return "".join(f'<path fill="{COLORS[color]}" d="{self.path(color)}"/>'
                       for color in ["gray", "blue", "white", "ink"] if color in self.cells.values())


def check(p, x, y, color="white", progress=1):
    points = [(x, y + 3), (x + 3, y + 6), (x + 10, y - 1)]
    if progress <= 0:
        return
    if progress < .3:
        p.line(points[0], (x + 3 * progress / .3, y + 3 + 3 * progress / .3), color)
    else:
        p.line(points[0], points[1], color)
        q = min(1, (progress - .3) / .7)
        p.line(points[1], (x + 3 + 7 * q, y + 6 - 7 * q), color)


def frame(emblem, t):
    p = Pixels()
    if emblem == "defense-test":
        # A defense target is tested from three directions. Each impact launches
        # a wave along the rim and compresses the reticle; no status/check icon.
        outline=[(31,4),(48,10),(48,28),(45,36),(39,43),
                 (31,49),(23,43),(17,36),(14,28),(14,10)]
        edge=Pixels();edge.polyline(outline,"white",True)
        rim=list(edge.cells)
        for x,y in rim:p.put(x,y,"white")
        t%=1
        impacts=[(1/6,(14,22),(-1,0)),(1/2,(44,9),(0,-1)),(5/6,(48,25),(1,0))]
        response=0
        for hit,(hx,hy),(dx,dy) in impacts:
            flight=((t-hit+.15)%1)/.15
            if 0<=flight<1:
                # Keep the incoming probe visible throughout its approach.
                available=hx-1 if dx<0 else 62-hx if dx>0 else hy-1
                distance=round(min(15,available)*(1-flight))
                x=hx+dx*distance;y=hy+dy*distance
                if 0<=x<63 and 0<=y<55:p.block(x,y,2,2,"white")
                for tail in [3,6]:
                    xx=x+dx*tail;yy=y+dy*tail
                    if 0<=xx<64 and 0<=yy<56:p.put(xx,yy,"blue")
            age=((t-hit)%1)/.17
            if 0<=age<1:
                strength=sin(pi*age)
                response=max(response,strength)
                origin=min(range(len(rim)),key=lambda i:(rim[i][0]-hx)**2+(rim[i][1]-hy)**2)
                spread=round(age*len(rim)/2)
                for direction in [-1,1]:
                    for width in range(-3,4):
                        x,y=rim[(origin+direction*spread+width)%len(rim)]
                        p.put(x,y,"blue")
                if age<.36:
                    # Small impact fragments remain attached to the shield edge.
                    for side in [-1,1]:
                        xx=hx+dx*3-dy*side*3;yy=hy+dy*3+dx*side*3
                        if 0<=xx<64 and 0<=yy<56:p.put(xx,yy,"blue")
        focus=round(response*2)
        ring_color="white" if response>.88 else "blue"
        p.circle(31,25,10-focus,ring_color)
        p.block(30,24,3,3,"blue")
        p.line((31,13+focus),(31,19+focus),"white")
        p.line((31,31-focus),(31,37-focus),"white")
        p.line((19+focus,25),(25+focus,25),"white")
        p.line((37-focus,25),(43-focus,25),"white")
    elif emblem == "reticle":
        # One compact mark: a targeting reticle and a simulated-attack bolt.
        # The silhouette stays fixed; only a narrow highlight crosses the bolt.
        corners=[[(24,8),(19,8),(12,15),(12,22)],
                 [(39,8),(44,8),(51,15),(51,22)],
                 [(51,33),(51,40),(44,47),(39,47)],
                 [(24,47),(19,47),(12,40),(12,33)]]
        for points in corners:
            edge=Pixels();edge.polyline(points,"white")
            for x,y in edge.cells:p.block(x,y,2,2,"white")
        bolt=Pixels()
        bolt.polygon([(35,12),(22,30),(31,30),(26,44),(44,24),(35,24),(41,12)],"blue")
        for y in range(12,45):
            xs=[x for x,yy in bolt.cells if yy==y]
            if xs:bolt.line((min(xs),y),(max(xs),y),"blue")
        for x,y in bolt.cells:p.put(x,y,"blue")
        if .12<t<.88:
            sweep=12+32*(t-.12)/.76
            for x,y in bolt.cells:
                if abs(y-sweep)<1:p.put(x,y,"white")
    elif emblem == "cyberlab":
        # A simulated probe hits a defensive wall on a lab machine. A status
        # check follows the impact; this is a conceptual mark, not a live test.
        p.polygon([(16,8),(54,8),(57,11),(57,38),(54,41),(16,41),(13,38),(13,11)],"white")
        p.block(16,12,38,24,"ink")
        p.line((18,10),(52,10),"gray")
        p.block(33,42,5,5,"white")
        p.polygon([(27,47),(44,47),(48,50),(23,50)],"gray")
        p.line((24,51),(47,51),"blue")
        for x in [19,23,27]:p.block(x,38,2,1,"gray")
        p.circle(46,23,4,"gray")
        p.line((40,23),(52,23),"white")
        p.line((46,17),(46,29),"white")
        p.block(45,22,3,3,"ink")
        wall_color="white" if .46<t<.64 else "blue"
        for x,y,w,h in [(29,16,4,4),(34,16,5,4),(27,21,5,4),
                        (33,21,6,4),(29,26,4,5),(34,26,5,5)]:
            p.block(x,y,w,h,wall_color)
        bolt=Pixels()
        bolt.polygon([(3,18),(18,18),(13,22),(25,22),(10,33),(14,26),(2,26),(7,22)],"blue")
        for x,y in bolt.cells:p.put(x,y,"blue")
        if .08<t<.46:
            sweep=3+22*(t-.08)/.38
            for x,y in bolt.cells:
                if abs(x-sweep)<1.4:p.put(x,y,"white")
        if .46<t<.65:
            p.block(26,22,2,3,"white")
            for x,y in [(25,18),(23,20),(24,28),(27,30)]:p.put(x,y,"blue")
        if .7<t<.98:
            p.block(40,16,14,16,"ink")
            check(p,41,22,"white",min(1,(t-.7)/.12))
            p.block(49,38,3,1,"blue")
    elif emblem == "helmet":
        # A compact guardian emblem: Greek helmet, blue crest and a visor glint.
        p.polygon([(17,13),(17,9),(21,5),(27,2),(36,2),(42,5),(46,9),(46,13),
                   (41,10),(36,8),(27,8),(22,10)],"blue")
        for x,y in [(22,5),(27,3),(35,3),(41,6)]:p.line((x,y),(x,y+2),"ink")
        p.polygon([(24,11),(39,11),(45,17),(47,23),(46,37),(42,46),(36,51),
                   (27,51),(21,46),(17,37),(16,23),(19,17)],"white")
        p.polyline([(21,19),(26,14),(37,14),(42,19)],"gray")
        p.polygon([(18,29),(22,32),(25,43),(27,47),(27,51),(21,46),(17,37)],"gray")
        p.polygon([(45,29),(41,32),(38,43),(36,47),(36,51),(42,46),(46,37)],"gray")
        p.polygon([(31,33),(35,38),(35,53),(28,53),(28,38)],"ink")
        p.polygon([(19,23),(29,26),(28,30),(20,27)],"ink")
        p.polygon([(34,26),(44,23),(43,27),(35,30)],"ink")
        p.line((30,25),(30,34),"white");p.line((33,25),(33,34),"white")
        p.line((31,34),(32,35),"white")
        visor=[]
        for a,b in [((21,25),(27,27)),((36,27),(42,25))]:
            temp=Pixels();temp.line(a,b,"blue");visor.extend(temp.cells)
        for x,y in visor:p.put(x,y,"blue")
        if .12<t<.86:
            sweep=20+24*(t-.12)/.74
            for x,y in visor:
                if abs(x-sweep)<1.6:p.put(x,y,"white")
    elif emblem == "correlation":
        # Event sources converge on a correlation core, producing an evidence
        # record. Open circuitry replaces the enclosing shield silhouette.
        inputs=[[(5,11),(12,11),(15,14),(15,21),(12,24),(5,24),(2,21),(2,14)],
                [(51,11),(58,11),(61,14),(61,21),(58,24),(51,24),(48,21),(48,14)]]
        for outline in inputs:p.polyline(outline,"white",True)
        p.polyline([(28,1),(34,1),(37,4),(37,8),(34,11),(28,11),(25,8),(25,4)],"gray",True)
        p.block(29,4,5,4,"blue")
        p.polyline([(5,18),(7,18),(8,15),(10,21),(11,17),(13,17)],"blue")
        p.polyline([(51,18),(53,18),(54,15),(56,21),(57,17),(59,17)],"blue")
        p.polyline([(15,17),(20,17),(26,23)],"gray")
        p.polyline([(48,17),(43,17),(37,23)],"gray")
        p.line((31,12),(31,22),"gray")
        for corner in [[(22,27),(22,22),(27,22)],[(36,22),(41,22),(41,27)],
                       [(22,32),(22,37),(27,37)],[(36,37),(41,37),(41,32)]]:
            p.polyline(corner,"white")
        p.polyline([(26,27),(31,30),(37,27)],"blue")
        p.line((31,25),(31,30),"blue")
        p.block(29,29,5,4,"blue")
        p.line((31,34),(31,43),"gray")
        p.polyline([(26,43),(35,43),(39,47),(39,53),(26,53)],"blue",True)
        p.polyline([(35,43),(35,47),(39,47)],"blue")
        if .08<t<.43:
            u=(t-.08)/.35
            for x,y in [(15+12*u,17+9*u),(48-12*u,17+9*u),(31,12+13*u)]:
                p.block(round(x),round(y),2,2,"white")
        if .43<=t<.72:
            p.block(26,25,12,10,"ink")
            check(p,27,27,"white",min(1,(t-.43)/.12))
        if .64<t<.81:
            p.block(31,round(35+10*(t-.64)/.17),2,2,"white")
        if .79<t<.98:
            for i,y in enumerate([47,49,51]):
                if t>.79+i*.045:p.line((29,y),(33 if i==0 else 36,y),"white")
            p.block(29,4,5,4,"white")
    elif emblem == "shield":
        p.polyline([(31,3),(49,9),(49,28),(46,36),(39,44),(31,50),(23,44),(16,36),(13,28),(13,9)], "white", True)
        p.polyline([(31,7),(45,12),(45,27),(42,34),(37,40),(31,45),(25,40),(20,34),(17,27),(17,12)], "blue", True)
        for x in [6,56]:
            p.line((x,18),(x,34),"gray")
            p.line((x,26),(11 if x==6 else 51,26),"gray")
            p.block(x-1,15,3,3,"blue")
            p.block(x-1,35,3,3,"blue")
        for x,y in [(23,19),(35,19),(23,27),(35,27)]:
            p.block(x,y,5,5,"gray")
        if t < .55:
            scan=round(15+21*t/.55)
            for y in range(15,min(scan,34)):
                for x in range(22,41):
                    if p.cells.get((x,y))=="gray":p.put(x,y,"blue")
            p.line((21,scan),(41,scan),"white")
        else:
            p.block(22,18,19,18,"ink")
            check(p,26,22,progress=min(1,(t-.55)/.16))
        p.line((21,52),(41,52),"gray")
        p.block(28,51,7,3,"blue" if t<.7 else "white")
    elif emblem == "rewind":
        p.circle(31,26,22,"gray",-.18*pi,1.55*pi)
        p.circle(31,26,18,"blue",.10*pi,1.65*pi)
        p.polyline([(15,6),(10,6),(10,11)],"white")
        p.polyline([(47,46),(52,46),(52,41)],"white")
        # Opposing timeline states are restored in reverse order.
        cycle=1-abs(2*t-1)
        for shift in [0,12]:
            for row in range(-7,8):
                width=7-abs(row)
                p.line((28+shift-width,26+row),(28+shift,26+row),"white" if shift==0 else "blue")
        p.line((18,52),(44,52),"gray")
        for i,x in enumerate([18,31,44]):p.block(x-1,51,3,3,"white" if i==round(cycle*2) else "gray")
        a=2*pi*(1-t)-pi/2
        p.block(round(31+22*cos(a))-1,round(26+22*sin(a))-1,3,3,"white")
    elif emblem == "review":
        p.polyline([(31,3),(51,14),(51,39),(31,51),(11,39),(11,14)],"blue",True)
        p.polyline([(31,7),(47,16),(47,37),(31,47),(15,37),(15,16)],"gray",True)
        p.polyline([(21,15),(35,15),(41,21),(41,39),(21,39)],"white",True)
        p.polyline([(35,15),(35,21),(41,21)],"white")
        p.polyline([(27,23),(24,26),(27,29)],"blue")
        p.polyline([(34,23),(37,26),(34,29)],"blue")
        for y,width in [(33,7),(36,10)]:p.line((25,y),(25+width,y),"gray")
        if t<.58:
            scan=round(19+19*t/.58)
            p.line((18,scan),(44,scan),"blue")
            p.block(17,scan-1,2,3,"white");p.block(44,scan-1,2,3,"white")
        else:
            p.block(27,23,17,14,"ink")
            check(p,29,26,progress=min(1,(t-.58)/.16))
        p.block(30,2,3,3,"white");p.block(30,50,3,3,"white")
    elif emblem == "forms":
        p.polyline([(18,4),(44,4),(52,12),(52,43),(44,51),(18,51),(10,43),(10,12)],"gray",True)
        # A desktop form sends a book record to the database, then confirms it.
        p.polyline([(17,12),(42,12),(44,14),(44,38),(17,38)],"white",True)
        p.line((17,18),(44,18),"gray")
        for x in [20,23,26]:p.put(x,15,"blue")
        p.polyline([(21,22),(25,21),(29,22),(33,21),(36,22),(36,30),(32,29),(29,30),(25,29),(21,30)],"white",True)
        p.line((29,22),(29,29),"blue")
        p.block(23,33,12,2,"blue")
        p.block(36,30,15,15,"ink")
        p.polyline([(37,33),(40,31),(47,31),(50,33),(47,35),(40,35)],"blue",True)
        p.polyline([(37,33),(37,42),(40,44),(47,44),(50,42),(50,33)],"blue")
        p.polyline([(37,38),(40,40),(47,40),(50,38)],"gray")
        if .15<t<.64:
            u=(t-.15)/.49
            x=round(31+12*u);y=round(35+4*sin(pi*u))
            p.block(x,y,2,2,"white")
        if .68<t<.94:
            p.block(20,22,17,9,"ink")
            check(p,24,23,"white",min(1,(t-.68)/.12))
        p.line((23,53),(41,53),"blue")
    elif emblem == "checkpoint":
        p.polyline([(16,6),(47,6),(53,12),(53,43),(47,49),(16,49),(10,43),(10,12)],"gray",True)
        p.line((15,44),(48,44),"blue")
        for x,y in [(17,35),(29,29),(41,22)]:
            p.line((x,y),(x+7,y),"white");p.line((x+1,y+1),(x+6,y+1),"blue")
        p.line((45,10),(45,21),"white")
        p.block(46,10,7,5,"blue")
        p.block(49,10,2,2,"white");p.block(47,12,2,2,"white")
        # A run crosses three platforms before resetting at the start.
        q=min(t/.78,1)*2
        section=min(1,int(q));u=q-section
        if q>=2:section=1;u=1
        x=20+12*(section+u);y=32-6*(section+u)-round(7*sin(pi*u))
        p.block(round(x)-1,round(y)-4,3,3,"white")
        p.block(round(x)-2,round(y)-1,5,3,"blue")
        p.line((round(x)-1,round(y)+2),(round(x)-1,round(y)+3),"white")
        p.line((round(x)+1,round(y)+2),(round(x)+1,round(y)+3),"white")
        if t>.8:check(p,27,8,"blue",min(1,(t-.8)/.1))
    elif emblem == "platformer":
        p.polyline([(31,3),(54,26),(31,49),(8,26)],"blue",True)
        p.polyline([(31,7),(50,26),(31,45),(12,26)],"gray",True)
        p.line((17,36),(45,36),"white")
        p.line((19,38),(43,38),"gray")
        p.line((22,40),(40,40),"blue")
        q=min(t/.75,1)
        jump=round(12*sin(pi*q))
        x=round(23+16*q);y=32-jump
        p.block(x-1,y-5,4,4,"white");p.block(x-2,y-1,6,4,"blue")
        p.block(x-2,y+3,2,1,"white");p.block(x+2,y+3,2,1,"white")
        if t<.4:
            p.polyline([(32,13),(35,16),(32,20),(29,16)],"white",True)
            p.line((31,15),(33,15),"blue")
        elif t<.65:
            radius=round(2+10*(t-.4)/.25)
            for dx,dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:p.block(32+dx*radius,16+dy*radius,1,1,"blue")
    elif emblem == "tasks":
        p.polyline([(18,5),(45,5),(52,12),(52,42),(45,49),(18,49),(11,42),(11,12)],"gray",True)
        p.polyline([(22,12),(40,12),(44,16),(44,41),(19,41),(19,16)],"white",True)
        p.block(27,10,9,4,"blue")
        for i,y in enumerate([20,27,34]):
            p.polyline([(23,y),(26,y),(26,y+3),(23,y+3)],"gray",True)
            p.line((30,y+1),(39,y+1),"gray")
            if t>.12+i*.20:
                p.polyline([(23,y+1),(24,y+2),(27,y-1)],"blue")
                p.line((30,y+1),(39,y+1),"white")
        p.polyline([(6,21),(2,25),(6,29)],"blue")
        p.polyline([(57,21),(61,25),(57,29)],"blue")
        packet=round(7+10*min(t/.25,1))
        if t<.25:p.block(packet,25,2,2,"white")
        if t>.75:p.block(round(46+10*(t-.75)/.25),25,2,2,"white")
    else:
        raise ValueError(f"Unknown emblem: {emblem}")
    return p


def text(content, x, y, size, color="white", tracking=0, weight=400):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" letter-spacing="{tracking}" fill="{COLORS[color]}">{escape(content)}</text>'


def badge(project):
    slug=project["slug"]
    duration=project.get("animation_seconds",4)
    title=escape(project["name"])
    desc=escape(project["description"])
    out=f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="376" viewBox="0 0 320 376" role="img" aria-labelledby="title desc"><title id="title">{title}</title><desc id="desc">{desc}</desc>'
    out+=f'<style>.frames{{animation:advance {duration}s steps({FRAMES},end) infinite;will-change:transform}}@keyframes advance{{to{{transform:translateX(-{FRAMES*256}px)}}}}@media(prefers-reduced-motion:reduce){{.frames{{animation:none;transform:none}}}}</style>'
    out+=f'<path fill="{COLORS["ink"]}" d="M0 0h320v376H0z"/>'
    out+=f'<g transform="translate(32 18)" shape-rendering="crispEdges"><defs><clipPath id="sprite"><path d="M0 0h256v224H0z"/></clipPath></defs><g clip-path="url(#sprite)"><g class="frames">'
    for i in range(FRAMES):
        out+=f'<g data-frame="{i}" transform="translate({i*256} 0)">{frame(project["emblem"],i/FRAMES).svg()}</g>'
    out+='</g></g></g>'
    out+=text(project["category"],160,263,10,"blue",1.25)
    out+=text(project["name"],160,296,29,weight=600)
    out+=text(project["summary"],160,323,13,"white")
    out+=technology_row(project["stack"])
    out+=f'<path d="M32 366H288" stroke="{COLORS["gray"]}" stroke-width=".5"/>'
    return out+'</svg>'


def main():
    projects=json.loads((ROOT/"projects.json").read_text())
    slugs=[p["slug"] for p in projects]
    assert len(slugs)==len(set(slugs)), "Duplicate project slug"
    ASSETS.mkdir(parents=True,exist_ok=True)
    heading=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="142" viewBox="0 0 1200 142" role="img" aria-labelledby="title desc"><title id="title">Project insignias</title><desc id="desc">Clickable project insignias: security automation, developer tools, backend and game experiments.</desc><path d="M0 0h1200v142H0z" fill="{COLORS["ink"]}"/><path d="M48 16H1152" stroke="{COLORS["gray"]}" stroke-width=".6"/><text x="44" y="87" fill="{COLORS["white"]}" font-family="Arial,Helvetica,sans-serif" font-size="55" letter-spacing="-2">Project insignias</text><text x="48" y="125" fill="{COLORS["gray"]}" font-family="Arial,Helvetica,sans-serif" font-size="21">Security / Developer tools / Backend / Game experiments</text><text x="1152" y="81" text-anchor="end" fill="{COLORS["blue"]}" font-family="Arial,Helvetica,sans-serif" font-size="14" letter-spacing="2">EXPLORE THE PROJECTS ↗</text></svg>'
    (ASSETS/'heading.svg').write_text(heading)
    links=[]
    for project in projects:
        assert re.fullmatch(r"[a-z0-9-]+",project["slug"])
        assert re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",project["repository"])
        (ASSETS/f'{project["slug"]}.svg').write_text(badge(project))
        url='https://github.com/'+project['repository']
        alt=f'{project["name"]} — {project["summary"]}. {project["category"].capitalize()}. Open repository.'
        links.append(f'  <a href="{url}"><img src="./assets/projects/{project["slug"]}.svg" width="30%" alt="{escape(alt,quote=True)}" /></a>')
    rows=['<p align="center">\n'+'\n'.join(links[i:i+3])+'\n</p>' for i in range(0,len(links),3)]
    block='<!-- PROJECTS:START -->\n'+'\n\n'.join(rows)+'\n\n<p align="center"><a href="https://github.com/Buraddomoon?tab=repositories">Explore all repositories ↗</a></p>\n\n<details>\n<summary>Project index &amp; technical notes</summary>\n\n'
    for project in projects:
        block+=f'- [**{project["name"]}**](https://github.com/{project["repository"]}) — {project["description"]}\n'
    block+='\n[ÆGIS architecture](https://github.com/Buraddomoon/AEGIS/blob/main/docs/architecture/overview.md) · [Rewind architecture](https://github.com/Buraddomoon/reversible-debugger/blob/main/docs/architecture.md)\n\n</details>\n<!-- PROJECTS:END -->'
    readme=ROOT/'README.md'
    source=readme.read_text()
    assert source.count('<!-- PROJECTS:START -->')==source.count('<!-- PROJECTS:END -->')==1, 'README needs one gallery marker pair'
    readme.write_text(re.sub(r'<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->',lambda _:block,source,flags=re.S))
    print(f'Built {len(projects)} project insignias and updated the README gallery.')


if __name__=='__main__':
    main()
