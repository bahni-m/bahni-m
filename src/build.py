"""Field Notes: render the bahni-m README images (light + dark) with Playwright.

Each image is an HTML page sharing one token set. Doodles are drawn with rough.js after fonts load.
Run: python3 build.py  ->  out/<name>-<light|dark>.png
"""
import base64, pathlib, re
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
SP = HERE.parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

def data(path):
    p = pathlib.Path(path)
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

TOKENS = """
:root{
  --paper:#F7F2EC; --win:#FBF8F4; --ink:#1A1714; --muted:#77706A; --rule:rgba(40,30,20,.16); --rule-strong:rgba(26,23,20,.82);
  --dot:rgba(40,30,20,.17); --marker:#E8511F; --ballpoint:#2420D6; --postit:#F9E27D; --postit-ink:#1b1b1b; --grain:.08;
  --f-display:"Inter Tight","Helvetica Neue",Arial,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --f-hand:"Nanum Pen Script","Comic Sans MS",cursive;
  --f-dot:"Doto","IBM Plex Mono",monospace;
}
:root[data-theme="dark"]{
  --paper:#131312; --win:#1A1A19; --ink:#EEECE6; --muted:#9C9A92; --rule:rgba(238,236,230,.14); --rule-strong:rgba(238,236,230,.75);
  --dot:rgba(238,236,230,.13); --marker:#FF6A38; --ballpoint:#8C89FF; --grain:.10;
}"""

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400&family=IBM+Plex+Mono:wght@400;500&family=Nanum+Pen+Script&family=Doto:wght@800;900&display=block" rel="stylesheet">
<script src="rough.js"></script>
<style>""" + TOKENS + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:transparent}
body{font-family:var(--f-display);color:var(--ink);-webkit-font-smoothing:antialiased}
.frame{background:var(--paper);position:relative;overflow:hidden;border:1px solid var(--rule)}
.grain{position:absolute;inset:0;opacity:var(--grain);pointer-events:none;mix-blend-mode:multiply}
:root[data-theme="dark"] .grain{mix-blend-mode:screen}
.lbl{font:400 13px/1 var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.lbl b{font-weight:500;color:var(--ink)}
.plus{position:absolute;width:13px;height:13px;color:var(--muted)}
.plus::before,.plus::after{content:"";position:absolute;background:currentColor}
.plus::before{left:6px;top:0;width:1px;height:13px}.plus::after{top:6px;left:0;height:1px;width:13px}
.win{border:1px solid var(--rule-strong);background:var(--win);position:relative}
.chrome{height:24px;border-bottom:1px solid var(--rule-strong);display:flex;align-items:center;justify-content:center;font:400 11px/1 var(--f-mono);letter-spacing:.14em;color:var(--muted);position:relative}
.chrome::before{content:">_";position:absolute;left:8px;font-size:11px;letter-spacing:0;color:var(--ink)}
.chrome::after{content:"≡";position:absolute;right:9px;font-size:14px;color:var(--ink)}
.dotgrid{background-image:radial-gradient(var(--dot) 1.1px,transparent 1.3px);background-size:16px 16px}
.hand{font:400 30px/1 var(--f-hand);color:var(--ballpoint);white-space:nowrap;position:absolute}
svg.ink{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}
STYLE
</style></head><body>
<div class="frame" id="frame" style="width:WIDTHpx;height:HEIGHTpx">
<svg class="grain" width="100%" height="100%"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1 0"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
<span class="plus" style="left:12px;top:12px"></span><span class="plus" style="right:12px;top:12px"></span>
<span class="plus" style="left:12px;bottom:12px"></span><span class="plus" style="right:12px;bottom:12px"></span>
BODY
<svg class="ink" id="ink"></svg>
</div>
<script>
const theme = new URLSearchParams(location.search).get('theme') || 'light';
document.documentElement.dataset.theme = theme;
document.querySelectorAll('[data-light]').forEach(i => i.src = i.dataset[theme]);
function ink(){
  const css=getComputedStyle(document.documentElement), v=k=>css.getPropertyValue(k).trim();
  const svg=document.getElementById('ink'), rc=rough.svg(svg), F=document.getElementById('frame').getBoundingClientRect();
  const box=id=>{const r=document.getElementById(id).getBoundingClientRect();return {x:r.left-F.left,y:r.top-F.top,w:r.width,h:r.height}};
  const add=n=>svg.appendChild(n);
  const squiggle=(b,color,seed,dy=2)=>{const y=b.y+b.h+dy;let d=`M ${b.x} ${y}`;for(let x=b.x;x<b.x+b.w;x+=14)d+=` q 7 ${(x-b.x)%28?7:-7} 14 0`;add(rc.path(d,{stroke:color,strokeWidth:2,roughness:.8,seed}))};
  const circle=(b,color,seed,px=30,py=4)=>add(rc.ellipse(b.x+b.w/2+2,b.y+b.h/2+2,b.w+px,b.h+py,{stroke:color,strokeWidth:3,roughness:1.6,bowing:1.3,seed}));
  const arrow=(pts,color,seed,w=1.8)=>{const [a,c,b]=pts;add(rc.path(`M ${a[0]} ${a[1]} Q ${c[0]} ${c[1]} ${b[0]} ${b[1]}`,{stroke:color,strokeWidth:w,roughness:.9,seed}));
    const ang=Math.atan2(b[1]-c[1],b[0]-c[0]),L=12;add(rc.linearPath([[b[0]-L*Math.cos(ang-0.5),b[1]-L*Math.sin(ang-0.5)],[b[0],b[1]],[b[0]-L*Math.cos(ang+0.5),b[1]-L*Math.sin(ang+0.5)]],{stroke:color,strokeWidth:w,roughness:.6,seed:seed+1}))};
  DOODLES
}
document.fonts.ready.then(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))).then(()=>{ink();document.body.dataset.ready=1});
</script></body></html>"""

AVATAR = (HERE / "avatar.svg").read_text().replace("<svg ", '<svg class="avatar" ', 1)
AB = SP / "ai-builders-id_logo/01-primary"
KS = SP / "konten-studio_logo/01-primary"

# ---------------- hero ----------------
HERO = dict(w=1200, h=580, style="""
.bar{position:absolute;left:40px;right:40px;top:26px;display:flex;justify-content:space-between;padding-bottom:12px;border-bottom:1px solid var(--rule-strong)}
h1{position:absolute;left:40px;top:86px;width:690px;font-weight:300;font-size:74px;line-height:1.0;letter-spacing:-.055em}
h1 span{white-space:nowrap}
.sub{position:absolute;left:40px;top:340px;font:400 15px/1.6 var(--f-mono);color:var(--muted);width:640px}
.sub b{color:var(--ink);font-weight:500}
.fig1{position:absolute;left:800px;top:76px;width:360px;height:300px}
.fig1 .body{position:absolute;inset:24px 0 0 0}
.fig1 svg.avatar{position:absolute;left:50%;top:50%;width:260px;height:260px;transform:translate(-50%,-48%);color:var(--ink)}
.flow{position:absolute;left:40px;right:40px;top:442px;height:104px;display:flex;align-items:center;justify-content:space-between}
.cell{width:220px;height:84px;border:1px solid var(--rule-strong);background:var(--win);display:flex;flex-direction:column;justify-content:center;padding:0 18px;gap:8px}
.cell .d{font:900 30px/1 var(--f-dot);letter-spacing:.02em}
.cell .s{font:400 12px/1 var(--f-mono);color:var(--muted);letter-spacing:.04em}
.post{width:236px;height:100px;background:var(--postit);color:var(--postit-ink);transform:rotate(-3.5deg);box-shadow:0 14px 18px -14px rgba(0,0,0,.55);padding:14px 16px;position:relative}
.post .t{font:400 40px/1 var(--f-hand);white-space:nowrap}
.post .s{font:400 12px/1 var(--f-mono);margin-top:10px;opacity:.7}
.post .tape{position:absolute;top:-11px;left:62px;width:76px;height:22px;background:rgba(255,255,255,.55);transform:rotate(3deg);border:1px solid rgba(0,0,0,.05)}
.gap{flex:1;height:84px}
""", body=f"""
<div class="bar lbl"><span>/ <b>bahni-m</b> &nbsp;·&nbsp; field notes</span><span>Bogor, ID &nbsp;·&nbsp; UTC+7</span></div>
<h1>I build <span id="w-agents">agents</span> that write, design &amp; <span id="w-ship">ship content</span>.</h1>
<p class="sub">Building <b>aibuilders.id</b>. Ex-AI PM, 7 years shipping AI to 5M+ users.</p>
<div class="win fig1" id="win"><div class="chrome">[ FIG. 1 ]</div><div class="body dotgrid"></div>{AVATAR}</div>
<div class="hand" id="n-me" style="left:430px;top:390px">that's me, the human gate</div>
<div class="flow">
  <div class="cell"><div class="d">RADAR</div><div class="s">trends + product notes</div></div><div class="gap" id="g1"></div>
  <div class="cell"><div class="d">DRAFT</div><div class="s">hooks · copy · images</div></div><div class="gap" id="g2"></div>
  <div class="post" id="post"><div class="tape"></div><div class="t">you approve ✓</div><div class="s">one human gate</div></div><div class="gap" id="g3"></div>
  <div class="cell"><div class="d">POSTED</div><div class="s">Threads · IG · WhatsApp</div></div>
</div>""", doodles="""
  const a=box('w-agents'); add(rc.ellipse(a.x+a.w/2+2,a.y+a.h/2+6,a.w+34,a.h+2,{stroke:v('--marker'),strokeWidth:3.2,roughness:1.6,bowing:1.4,seed:7}));
  squiggle(box('w-ship'),v('--ballpoint'),3);
  [['g1',2],['g2',5],['g3',9]].forEach(([id,seed])=>{const g=box(id),cy=g.y+g.h/2;arrow([[g.x+10,cy+4],[g.x+g.w/2,cy-14],[g.x+g.w-12,cy]],v('--ink'),seed)});
  arrow([[728,412],[772,414],[776,440]],v('--ballpoint'),11);
  arrow([[728,400],[800,396],[846,382]],v('--ballpoint'),13);
  add(rc.path('M 742 116 l 10 -22 l 8 24 l 22 -6 l -18 14 l 12 20 l -20 -10 l -14 18 l 2 -22 l -20 -6 z',{stroke:v('--marker'),strokeWidth:2,roughness:1.4,seed:21}));
""")

# ---------------- brand cards ----------------
CARD_STYLE = """
.card{position:absolute;inset:22px}
.card .body{position:absolute;inset:24px 0 0 0;padding:30px 30px 0}
.logo{height:56px;display:flex;align-items:center}
.tag{margin-top:22px;font:300 34px/1.05 var(--f-display);letter-spacing:-.04em;display:inline-block}
.desc{margin-top:14px;font:400 14px/1.6 var(--f-mono);color:var(--muted);max-width:400px}
.url{position:absolute;left:30px;bottom:22px;font:500 13px/1 var(--f-mono);letter-spacing:.04em;color:var(--ink)}
"""
def card(fig, logo_light, logo_dark, logo_h, tag_html, desc, url, note, doodles):
    return dict(w=600, h=340, style=CARD_STYLE, body=f"""
<div class="win card"><div class="chrome">[ FIG. {fig} ]</div><div class="body dotgrid">
  <div class="logo"><img data-light="{data(logo_light)}" data-dark="{data(logo_dark)}" style="height:{logo_h}px;width:auto" alt=""></div>
  <div class="tag">{tag_html}</div>
  <p class="desc">{desc}</p>
  <div class="url">{url} ↗</div>
</div></div>
<div class="hand" id="note" style="{note[1]}">{note[0]}</div>""", doodles=doodles)

CARD_AB = card(2, AB / "aibuilders-logo-horizontal.png", AB / "aibuilders-logo-horizontal-dark-bg.png", 56,
    'Learn · Build · <span id="hl">Get built</span>',
    "Where 1,700+ Indonesian builders learn to ship and sell AI products. Events, courses and the platform, on Nuxt + Cloudflare.",
    "aibuilders.id", ("where I build in public", "right:44px;top:70px"), """
  squiggle(box('hl'),v('--marker'),31,0);
  const n=box('note'); arrow([[n.x+n.w*0.35,n.y+n.h+4],[n.x+n.w*0.2,n.y+n.h+40],[n.x-34,n.y+n.h+48]],v('--ballpoint'),33);
""")
CARD_KS = card(3, KS / "konten-studio-lockup-trim.png", KS / "konten-studio-lockup-dark-trim.png", 36,
    'Growth on <span id="hl">Threads</span>',
    "Done-for-you, monthly. Strategy, posts and replies that turn followers into signups for SaaS and tech brands.",
    "kontenstudio.agency", ("on purpose.", "left:372px;top:138px"), """
  const t=box('hl'); add(rc.ellipse(t.x+t.w/2,t.y+t.h/2+3,t.w+26,t.h+8,{stroke:v('--marker'),strokeWidth:3,roughness:1.5,bowing:1.3,seed:41}));
  const n=box('note'); arrow([[n.x+20,n.y+n.h+2],[n.x+4,n.y+n.h+26],[t.x+t.w+20,t.y+t.h/2+4]],v('--ballpoint'),43);
""")

# ---------------- stack ----------------
STACK = [("claude", "Claude Code"), ("cloudflare", "Workers · D1"), ("nuxt", "Nuxt"), ("vuedotjs", "Vue"),
         ("typescript", "TypeScript"), ("python", "Python"), ("playwright", "Playwright"), ("git", "git + cron")]
cells = "".join(f'<div class="sc" id="s-{k}"><i style="-webkit-mask-image:url({data(HERE/"icons"/(k+".svg"))});mask-image:url({data(HERE/"icons"/(k+".svg"))})"></i><span>{l}</span></div>' for k, l in STACK)
STACKIMG = dict(w=1200, h=270, style="""
.bar{position:absolute;left:40px;right:40px;top:26px;display:flex;justify-content:space-between;padding-bottom:12px;border-bottom:1px solid var(--rule-strong)}
.row{position:absolute;left:40px;right:40px;top:78px;display:grid;grid-template-columns:repeat(8,1fr);border:1px solid var(--rule-strong);background:var(--win)}
.sc{height:128px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;border-right:1px solid var(--rule)}
.sc:last-child{border-right:none}
.sc i{width:44px;height:44px;background:var(--ink);-webkit-mask-size:contain;mask-size:contain;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:center;mask-position:center}
.sc span{font:400 14px/1 var(--f-mono);color:var(--muted)}
""", body=f"""
<div class="bar lbl"><span>/ <b>stack</b> &nbsp;·&nbsp; [ fig. 4 ]</span><span>what I reach for daily</span></div>
<div class="row">{cells}</div>
<div class="hand" id="note" style="right:150px;top:222px">cron + git = my job queue</div>""", doodles="""
  const g=box('s-git'), n=box('note');
  arrow([[n.x+n.w+6,n.y+n.h/2],[g.x+g.w/2+30,n.y+n.h/2],[g.x+g.w/2+10,g.y+g.h-6]],v('--ballpoint'),51);
  const c=box('s-claude'); add(rc.ellipse(c.x+c.w/2,c.y+49,66,64,{stroke:v('--marker'),strokeWidth:2.6,roughness:1.6,seed:53}));
""")

# ---------------- stats ----------------
STATS = [("~7y", "shipping AI products", "st1"), ("5M+", "users reached", "st2"), ("1M+", "assets classified", "st3"),
         ("-90%", "account hijacking", "st4"), ("$150K", "saved per year", "st5")]
stat_cells = "".join(f'<div class="st"><b id="{i}">{n}</b><span>{l}</span></div>' for n, l, i in STATS)
STATSIMG = dict(w=1200, h=290, style="""
.bar{position:absolute;left:40px;right:40px;top:26px;display:flex;justify-content:space-between;padding-bottom:12px;border-bottom:1px solid var(--rule-strong)}
.row{position:absolute;left:40px;right:40px;top:78px;display:grid;grid-template-columns:repeat(5,1fr);border:1px solid var(--rule-strong);background:var(--win)}
.st{height:140px;padding:28px 24px;border-right:1px dashed var(--rule-strong)}
.st:last-child{border-right:none}
.st b{display:inline-block;font:900 52px/1 var(--f-dot);letter-spacing:.01em}
.st span{display:block;margin-top:16px;font:400 14px/1.3 var(--f-mono);color:var(--muted)}
""", body=f"""
<div class="bar lbl"><span>/ <b>before this</b> &nbsp;·&nbsp; [ fig. 5 ]</span><span>Enterprise · MarTech · GovTech · Travel · Mobility</span></div>
<div class="row">{stat_cells}</div>
<div class="hand" id="note" style="left:330px;top:238px">AI PM, before agents were cool</div>""", doodles="""
  const s=box('st2'); add(rc.ellipse(s.x+s.w/2,s.y+s.h/2+2,s.w+36,s.h+22,{stroke:v('--marker'),strokeWidth:3,roughness:1.5,bowing:1.2,seed:61}));
  const n=box('note'); arrow([[n.x-6,n.y+n.h/2],[s.x+s.w/2-10,n.y+n.h/2+4],[s.x+s.w/2-4,s.y+s.h+40]],v('--ballpoint'),63);
""")

JOBS = {"hero": HERO, "card-aibuilders": CARD_AB, "card-kontenstudio": CARD_KS, "stack": STACKIMG, "stats": STATSIMG}

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, j in JOBS.items():
        html = (HEAD.replace("WIDTH", str(j["w"])).replace("HEIGHT", str(j["h"]))
                .replace("STYLE", j["style"]).replace("DOODLES", j["doodles"]).replace("BODY", j["body"]))
        f = HERE / f"_{name}.html"; f.write_text(html)
        for theme in ("light", "dark"):
            pg = b.new_page(viewport={"width": j["w"], "height": j["h"]}, device_scale_factor=2)
            pg.goto(f"file://{f.resolve()}?theme={theme}", wait_until="networkidle")
            pg.wait_for_selector("body[data-ready]"); pg.wait_for_timeout(250)
            pg.locator("#frame").screenshot(path=str(OUT / f"{name}-{theme}.png"))
            pg.close()
    b.close()
print("ok", sorted(x.name for x in OUT.iterdir()))
