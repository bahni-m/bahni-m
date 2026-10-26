"""Field Notes: render the "results on Threads" strip from results.json (light + dark).

results.json is the kontenstudio.agency proof snapshot (Repliz -> Threads Insights), refreshed
every 2 days by a cron on Bahni's VPS (~/scripts/github-results/run.sh), which then commits.
Run: python3 results.py  ->  ../assets/results-<light|dark>.png
"""
import json
from build import HERE, render

R = json.loads((HERE / "results.json").read_text())
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

def date(d, year=True):
    return f"{int(d[8:10])} {MONTHS[int(d[5:7]) - 1]}" + (f" {d[:4]}" if year else "")

def compact(n):  # same rules as compact() in kontenstudio-landing/site/src/proof.mjs
    if n >= 1e6: return f"{n / 1e6:.{0 if n >= 1e7 else 1}f}".removesuffix(".0") + "M"
    if n >= 1e4: return f"{round(n / 1e3)}K"
    if n >= 1e3: return f"{n / 1e3:.1f}".removesuffix(".0") + "K"
    return str(n)

h = R["headline"]
since = f"since the first post on {date(h['firstPost'], False)}" if h["firstPost"] else f"last {R['windowDays']} days"
brand_cells = "".join(f"""<div class="br">
  <div class="bh"><b>@{b['handle']}</b><span>{b['blurb']}</span></div>
  <div class="mini">{''.join(f'<div><b>{compact(b[k])}</b><span>{l}</span></div>' for k, l in
      (("views", "views"), ("engagement", "engagements"), ("followers", "followers"), ("clicks", "link clicks")))}</div>
</div>""" for b in R["brands"])

RESULTS = dict(w=1200, h=372, style="""
.bar{position:absolute;left:40px;right:40px;top:26px;display:flex;justify-content:space-between;padding-bottom:12px;border-bottom:1px solid var(--rule-strong)}
.row{position:absolute;left:40px;right:40px;top:78px;display:grid;grid-template-columns:1.15fr repeat(BRANDS,1fr);border:1px solid var(--rule-strong);background:var(--win)}
.hl{height:218px;padding:28px 26px;border-right:1px dashed var(--rule-strong)}
.hl b{display:inline-block;font:900 64px/1 var(--f-dot);letter-spacing:.01em}
.hl .u{font:900 30px/1 var(--f-dot);margin-left:8px}
.hl p{margin-top:18px;font:400 14px/1.5 var(--f-mono);color:var(--muted)}
.hl p em{font-style:normal;color:var(--ink)}
.br{height:218px;padding:22px 24px;border-right:1px dashed var(--rule-strong)}
.br:last-child{border-right:none}
.bh b{font:500 15px/1 var(--f-mono);color:var(--ink)}
.bh span{display:block;margin-top:6px;font:400 12px/1 var(--f-mono);color:var(--muted)}
.mini{margin-top:20px;display:grid;grid-template-columns:1fr 1fr;row-gap:16px}
.mini b{display:block;font:900 30px/1 var(--f-dot)}
.mini span{display:block;margin-top:6px;font:400 12px/1 var(--f-mono);color:var(--muted)}
""".replace("BRANDS", str(len(R["brands"]))), body=f"""
<div class="bar lbl"><span>/ <b>results on threads</b> &nbsp;·&nbsp; [ fig. 6 ]</span><span>Threads Insights &nbsp;·&nbsp; updated {date(R['asOf'])}</span></div>
<div class="row" id="row">
  <div class="hl"><b id="big">{compact(h['views'])}</b><span class="u">views</span>
    <p><em>@{h['handle']}</em>, {h['posts']} posts in {h['days']} days,<br>{since}.</p></div>
  {brand_cells}
</div>
<div class="hand" id="note" style="left:470px;top:318px">grown by Konten Studio, refreshed every 2 days</div>""", doodles="""
  const s=box('big'); add(rc.ellipse(s.x+s.w/2+2,s.y+s.h/2+2,s.w+30,s.h+20,{stroke:v('--marker'),strokeWidth:3,roughness:1.5,bowing:1.2,seed:71}));
  const n=box('note'), r=box('row'); arrow([[n.x-8,n.y+n.h/2],[s.x+s.w/2+60,n.y+n.h/2+4],[s.x+s.w/2+30,r.y+r.h+6]],v('--ballpoint'),73);
""")

if __name__ == "__main__":
    render({"results": RESULTS}, HERE.parent / "assets")
    print("ok results", R["asOf"])
