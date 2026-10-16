#!/usr/bin/env python3
"""Generate bespoke pixel-art cover art for every Pixel Sprout original."""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "assets" / "originals.json"
PALETTES = [
 ((12,25,54),(38,70,104),(110,205,172),(250,215,119)),
 ((22,31,66),(72,60,112),(244,130,164),(255,223,142)),
 ((11,44,47),(28,94,81),(121,184,129),(243,206,125)),
 ((16,49,73),(40,116,145),(123,226,212),(255,222,145)),
 ((21,37,73),(55,75,133),(104,191,218),(246,181,119)),
 ((49,28,76),(105,51,111),(238,126,184),(255,219,151)),
 ((20,54,60),(31,115,98),(128,210,145),(255,212,111)),
 ((25,37,63),(67,73,117),(185,141,130),(255,214,153)),
 ((40,30,48),(105,52,61),(241,117,75),(255,207,115)),
 ((20,34,71),(54,72,133),(255,184,102),(255,230,165)),
 ((17,48,62),(39,104,99),(134,194,140),(239,216,145)),
 ((22,37,71),(64,84,133),(126,198,225),(255,207,123)),
 ((43,27,46),(123,49,47),(255,111,65),(255,203,111)),
 ((12,45,64),(24,103,115),(113,207,192),(244,212,142)),
 ((20,26,68),(57,60,127),(183,139,228),(255,211,152)),
 ((24,34,61),(59,76,103),(165,195,212),(248,219,160)),
 ((33,28,64),(87,54,116),(191,131,227),(255,219,148)),
]
GAMES = [
 ("lumenstack","LUMENSTACK","tower","Arcade"),("petalstack","PETALSTACK","flower","Arcade"),
 ("mossgate","MOSSGATE","gate","Arcade"),("dewdash","DEWDASH","bolt","Arcade"),
 ("dewrack","DEWRACK","gems","Arcade"),("petalrack","PETALRACK","petalgems","Puzzle"),
 ("nectarjar","NECTARJAR","jar","Puzzle"),("cairnfall","CAIRNFALL","stones","Arcade"),
 ("kilnstack","KILNSTACK","kiln","Arcade"),("lanternspire","LANTERNSPIRE","lantern","Arcade"),
 ("reedline","REEDLINE","reeds","Arcade"),("galehook","GALEHOOK","hook","Arcade"),
 ("cinderwell","CINDERWELL","ember","Arcade"),("riverstone","RIVERSTONE","river","Puzzle"),
 ("moonbloom","MOONBLOOM","moonflower","Puzzle"),("cold-read","COLD READ","eye-book","Original"),
 ("guess-it-box","GUESS IT BOX","giftbox","Original")
]
def font(size, bold=True):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def mix(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def icon(d, kind, cx, cy, s, a, h):
    ink=(10,18,31); d.ellipse((cx-s*.8,cy-s*.8,cx+s*.8,cy+s*.8),fill=tuple(v//3 for v in a))
    def rect(box,c,outline=ink,w=5): d.rectangle(box,fill=c,outline=outline,width=w)
    def poly(points,c): d.polygon(points,fill=c,outline=ink)
    if kind in ("tower","flower","lantern","kiln"):
        w=s*.9; ht=s*1.3
        rect((cx-w/2,cy-ht/2,cx+w/2,cy+ht/2),a)
        for y in range(int(cy-ht/2+12),int(cy+ht/2),22): d.rectangle((cx-w/2+9,y,cx+w/2-9,y+5),fill=h)
        for x in (cx-w*.25,cx,cx+w*.25): rect((x-7,cy-13,x+7,cy+12),ink,ink,1)
        rect((cx-17,cy+30,cx+17,cy+ht/2),h)
        if kind=="flower":
            for dx,dy in [(0,-s*.75),(-s*.22,-s*.58),(s*.22,-s*.58),(0,-s*.48)]: d.ellipse((cx+dx-17,cy+dy-17,cx+dx+17,cy+dy+17),fill=h,outline=ink,width=4)
        if kind=="lantern": rect((cx-24,cy-s*.7,cx+24,cy-s*.36),h)
        if kind=="kiln": rect((cx-24,cy+10,cx+24,cy+48),(255,100,48))
    elif kind in ("gems","petalgems","bolt"):
        if kind=="bolt": poly([(cx+10,cy-s*.65),(cx-s*.38,cy+4),(cx-2,cy+4),(cx-s*.15,cy+s*.58),(cx+s*.4,cy-s*.1),(cx+s*.12,cy-s*.1)],h)
        else:
            for i in range(6 if kind=="petalgems" else 3):
                x=cx+math.cos(i*math.pi/3)*s*.32; y=cy+math.sin(i*math.pi/3)*s*.32
                d.polygon([(x, y-s*.25),(x+s*.19,y),(x,y+s*.25),(x-s*.19,y)],fill=h if i%2 else a,outline=ink)
            d.ellipse((cx-s*.17,cy-s*.17,cx+s*.17,cy+s*.17),fill=h,outline=ink,width=4)
    elif kind in ("gate","stones","river"):
        if kind=="gate":
            rect((cx-s*.58,cy-s*.42,cx-s*.3,cy+s*.46),a); rect((cx+s*.3,cy-s*.42,cx+s*.58,cy+s*.46),a); rect((cx-s*.58,cy-s*.5,cx+s*.58,cy-s*.22),h)
            d.rectangle((cx-20,cy+10,cx+20,cy+s*.46),fill=ink)
        else:
            for i,(dx,dy,ww,hh) in enumerate([(-.36,.2,.42,.28),(.1,.02,.44,.3),(-.02,-.34,.36,.25),(.37,.35,.3,.2)]):
                poly([(cx+(dx-ww/2)*s,cy+(dy-hh/2)*s),(cx+(dx+ww/2)*s,cy+(dy-hh/2)*s),(cx+(dx+ww/2)*s,cy+(dy+hh/2)*s),(cx+(dx-ww/2)*s,cy+(dy+hh/2)*s)],a if i%2==0 else h)
    elif kind in ("jar","giftbox"):
        if kind=="jar":
            rect((cx-s*.38,cy-s*.35,cx+s*.38,cy+s*.44),a); rect((cx-s*.23,cy-s*.55,cx+s*.23,cy-s*.35),h)
            d.ellipse((cx-s*.28,cy-s*.1,cx+s*.28,cy+s*.26),fill=h,outline=ink,width=4)
            d.ellipse((cx-s*.1,cy-s*.04,cx+s*.1,cy+s*.16),fill=a)
        else:
            poly([(cx-s*.5,cy-s*.18),(cx,cy-s*.48),(cx+s*.5,cy-s*.18),(cx+s*.5,cy+s*.34),(cx,cy+s*.55),(cx-s*.5,cy+s*.34)],a)
            poly([(cx-s*.5,cy-s*.18),(cx,cy+.03),(cx+s*.5,cy-s*.18),(cx,cy-s*.48)],h)
            rect((cx-10,cy-12,cx+10,cy+15),h)
    elif kind in ("reeds","hook"):
        for i in range(5):
            x=cx+(i-2)*s*.16; d.line((x,cy+s*.5,x+(i-2)*5,cy-s*.45),fill=a,width=10)
            poly([(x,cy-s*.12),(x-20,cy-s*.32),(x-4,cy+s*.02)],h)
        if kind=="hook":
            d.arc((cx-s*.45,cy-s*.5,cx+s*.45,cy+s*.35),180,350,fill=h,width=13)
            d.line((cx+s*.38,cy-s*.02,cx+s*.52,cy+s*.34),fill=h,width=11)
    elif kind=="ember":
        d.ellipse((cx-s*.52,cy-s*.36,cx+s*.52,cy+s*.52),fill=a,outline=ink,width=6)
        d.ellipse((cx-s*.34,cy-s*.2,cx+s*.34,cy+s*.3),fill=ink,outline=h,width=4)
        poly([(cx,cy+s*.25),(cx-s*.18,cy-s*.12),(cx-s*.05,cy-s*.45),(cx+s*.18,cy-s*.08),(cx+s*.08,cy+s*.22)],(255,112,49))
    elif kind=="moonflower":
        for ang in range(0,360,45):
            x=cx+math.cos(math.radians(ang))*s*.27; y=cy+math.sin(math.radians(ang))*s*.27
            d.ellipse((x-25,y-25,x+25,y+25),fill=a,outline=ink,width=4)
        d.ellipse((cx-17,cy-17,cx+17,cy+17),fill=h,outline=ink,width=3)
        d.arc((cx-s*.65,cy-s*.65,cx+s*.65,cy+s*.65),205,335,fill=h,width=8)
    elif kind=="eye-book":
        poly([(cx-s*.6,cy-s*.35),(cx,cy-s*.18),(cx,cy+s*.45),(cx-s*.6,cy+s*.28)],a)
        poly([(cx+s*.6,cy-s*.35),(cx,cy-s*.18),(cx,cy+s*.45),(cx+s*.6,cy+s*.28)],h)
        d.ellipse((cx-24,cy-15,cx+24,cy+15),fill=ink,outline=h,width=4); d.ellipse((cx-8,cy-8,cx+8,cy+8),fill=h)
def draw(slug,title,kind,category,idx,path):
    top,bottom,a,h=PALETTES[idx]; W=640
    im=Image.new("RGB",(W,W)); px=im.load()
    for y in range(W):
        base=mix(top,bottom,y/(W-1))
        for x in range(W):
            v=max(0,1-math.sqrt(((x-320)/420)**2+((y-270)/440)**2))
            px[x,y]=tuple(min(255,int(c+v*18)) for c in base)
    d=ImageDraw.Draw(im); rng=random.Random(1234+idx)
    for _ in range(150):
        x=rng.randrange(15,625); y=rng.randrange(12,410); z=rng.choice([2,3,4,6])
        c=h if rng.random()<.3 else tuple(int(v*.7) for v in a)
        d.rectangle((x,y,x+z,y+z),fill=c)
        if z>3 and rng.random()<.2: d.line((x-5,y+z//2,x+z+5,y+z//2),fill=h,width=1)
    # layered far hills and pixel forest
    for base,col in [(385,tuple(v//2 for v in a)),(425,tuple(int(v*.36) for v in a))]:
        pts=[(0,base)]; x=0
        while x<640:
            x+=rng.randrange(22,58); pts.append((min(x,640),base-rng.randrange(12,68)))
        pts.extend([(640,640),(0,640)]); d.polygon(pts,fill=col)
    # lush pixel vines framing the hero
    for side in (0,1):
        for j in range(9):
            x=18+j*15 if side==0 else 622-j*15; y=150+j*24
            d.rectangle((x,y,x+7,y+28),fill=tuple(int(v*.45) for v in a))
            d.polygon([(x,y+7),(x-15 if side==0 else x+22,y-5),(x+5,y+17)],fill=a)
            if j%2==0: d.rectangle((x+(10 if side else -9),y+12,x+(18 if side else -1),y+20),fill=h)
    # luminous stepping-stone stage
    d.polygon([(70,430),(160,400),(480,400),(570,432),(500,474),(140,474)],fill=(15,25,38))
    d.polygon([(70,430),(160,400),(480,400),(570,432),(500,449),(140,449)],fill=a)
    for x in range(105,550,22): d.rectangle((x,451,x+8,460),fill=tuple(int(v*.62) for v in a))
    icon(d,kind,320,267,118,a,h)
    d.rectangle((8,8,631,631),outline=tuple(int(v*.72) for v in h),width=3)
    for x,y in [(18,18),(622,18),(18,622),(622,622)]: d.rectangle((x-4,y-4,x+4,y+4),fill=h)
    d.rounded_rectangle((34,492,606,582),radius=21,fill=(9,16,30),outline=h,width=4)
    for x in range(48,594,22): d.rectangle((x,500,x+5,505),fill=a)
    size=42 if len(title)<=9 else (37 if len(title)<=10 else 31)
    f=font(size); bbox=d.textbbox((0,0),title,font=f,stroke_width=2)
    while bbox[2]-bbox[0]>530 and size>25:
        size-=2; f=font(size); bbox=d.textbbox((0,0),title,font=f,stroke_width=2)
    d.text(((W-(bbox[2]-bbox[0]))//2,516),title,font=f,fill=h,stroke_width=4,stroke_fill=(4,9,19))
    sf=font(15,False); d.text((320,605),f"PIXELSPROUT  •  {category.upper()}",font=sf,fill=(225,236,226),anchor="mm",stroke_width=1,stroke_fill=(7,13,25))
    path.parent.mkdir(parents=True,exist_ok=True); im.save(path,"JPEG",quality=91,optimize=True,progressive=True,subsampling=0)
def main():
    games=json.loads(CATALOG.read_text(encoding="utf-8"))
    index={g[0]:i for i,g in enumerate(GAMES)}
    byslug={g[0]:g for g in GAMES}
    wrote=[]
    for game in games:
        slug=game.get("slug","")
        if slug not in byslug: continue
        _,title,kind,cat=byslug[slug]; idx=index[slug]
        thumb=game.get("thumbnail","")
        if slug=="cold-read": path=ROOT/"assets"/"cold-read-logo.jpg"
        elif slug=="guess-it-box": path=ROOT/"assets"/"gift-file-logo.jpg"
        else: path=ROOT/"assets"/"originals"/slug/"cover.jpg"
        draw(slug,title,kind,cat,idx,path); wrote.append(str(path.relative_to(ROOT)))
    print(f"Generated {len(wrote)} original game logos:")
    for p in wrote: print(p)
if __name__=="__main__": main()
