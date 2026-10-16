"""Animated hero: the doodles draw themselves in. Needs _hero.html from build.py.
Run: python3 gif.py  ->  out/hero-<light|dark>.gif
"""
import pathlib, subprocess, tempfile
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
FPS, LENGTH, SCALE = 20, 8.5, 1.5

# svg.ink children in the order hero doodles add them -> [start, end] seconds
SCHEDULE = [(0.3, 0.9),                          # marker circle "agents"
            (0.9, 1.4),                          # ballpoint squiggle "ship content"
            (2.0, 2.3), (2.3, 2.4),              # RADAR -> DRAFT
            (2.5, 2.8), (2.8, 2.9),              # DRAFT -> post-it
            (3.0, 3.3), (3.3, 3.4),              # post-it -> POSTED
            (4.3, 4.65), (4.65, 4.75),           # note -> post-it
            (4.8, 5.15), (5.15, 5.25),           # note -> FIG. 1
            (1.4, 1.8)]                          # marker star
NOTE = (3.6, 4.2)                                # "that's me, the human gate" written left to right

SETUP = """(sched) => {
  const groups = [...document.getElementById('ink').children];
  window.__parts = groups.map((g, i) => {
    const paths = [...g.querySelectorAll('path')].map(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; return {p, L}; });
    return {paths, total: paths.reduce((s, x) => s + x.L, 0), t: sched[i]};
  });
  window.__note = document.getElementById('n-me');
}"""
SET_T = """([t, note]) => {
  const ease = x => x < 0 ? 0 : x > 1 ? 1 : 1 - Math.pow(1 - x, 2);
  for (const g of window.__parts) {
    let left = ease((t - g.t[0]) / (g.t[1] - g.t[0])) * g.total;
    for (const {p, L} of g.paths) { const d = Math.min(L, Math.max(0, left)); p.style.strokeDashoffset = L - d; left -= L; }
  }
  const k = Math.min(1, Math.max(0, (t - note[0]) / (note[1] - note[0])));
  window.__note.style.clipPath = `inset(-10px ${100 - k * 100}% -10px -10px)`;
}"""

with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
    b = p.chromium.launch()
    for theme in ("light", "dark"):
        pg = b.new_page(viewport={"width": 1200, "height": 580}, device_scale_factor=SCALE)
        pg.goto(f"file://{(HERE / '_hero.html').resolve()}?theme={theme}", wait_until="networkidle")
        pg.wait_for_selector("body[data-ready]")
        pg.evaluate(SETUP, SCHEDULE)
        frames = pathlib.Path(tmp) / theme; frames.mkdir()
        for i in range(int(FPS * LENGTH)):
            pg.evaluate(SET_T, [i / FPS, NOTE])
            pg.locator("#frame").screenshot(path=str(frames / f"{i:04d}.png"))
        pg.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%04d.png"),
                        "-filter_complex", "[0]split[a][b];[a]palettegen=stats_mode=full:max_colors=128[p];[b][p]paletteuse=dither=none:diff_mode=rectangle",
                        str(OUT / f"hero-{theme}.gif")], check=True)
    b.close()
for f in sorted(OUT.glob("hero-*.gif")): print(f.name, f.stat().st_size // 1024, "KB")
