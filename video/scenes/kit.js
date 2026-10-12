const Q = new URLSearchParams(location.search);
const T0 = parseFloat(Q.get("t0") || 0);
let START = null;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
function at(t, fn) { setTimeout(fn, t * 1000); }
function on(sel, t, cls = "on") { at(t, () => $$(sel).forEach((e) => e.classList.add(cls))); }
function off(sel, t, cls = "on") { at(t, () => $$(sel).forEach((e) => e.classList.remove(cls))); }
function hide(sel, t) { at(t, () => $$(sel).forEach((e) => { e.classList.add("out", "off"); })); }
function show(sel, t) { at(t, () => $$(sel).forEach((e) => { e.classList.remove("off"); })); }
function count(sel, t, dur, from, to, fmt) {
  at(t, () => {
    const e = $(sel); const s = performance.now();
    (function f() {
      const p = Math.min(1, (performance.now() - s) / (dur * 1000));
      const k = 1 - Math.pow(1 - p, 3);
      if (e) e.textContent = fmt(from + (to - from) * k);
      if (p < 1) requestAnimationFrame(f);
    })();
  });
}
function hud(sec, num) {
  $(".scene").insertAdjacentHTML("beforeend",
    `<div class="hud tl">// purser · ${num} · ${sec}</div><div class="hud tr">PURSER_DEMO.MP4 <span id="tc">00:00:00:00</span></div><div class="hud bl">neatHack 2026 · exactly-once refund operations agent</div><div class="hud br">github.com/0xkinno/purser</div>`);
}
function tick() {
  if (START !== null) {
    const t = T0 + (performance.now() - START) / 1000;
    const f = Math.floor((t % 1) * 30), s = Math.floor(t) % 60, m = Math.floor(t / 60) % 60, h = Math.floor(t / 3600);
    const p = (n) => String(n).padStart(2, "0");
    const e = $("#tc"); if (e) e.textContent = `${p(h)}:${p(m)}:${p(s)}:${p(f)}`;
  }
  requestAnimationFrame(tick);
}
tick();
function zoom(sel, t, scale, x, y) { at(t, () => { const e = $(sel); if (e) e.style.transform = `scale(${scale}) translate(${-x}px,${-y}px)`; }); }
window.go = function () {
  START = performance.now();
  const sc = $(".scene");
  if (sc) sc.classList.add("go");
  $$("video").forEach((v) => { v.muted = true; v.currentTime = parseFloat(v.dataset.ss || 0); v.play().catch(()=>{}); });
  if (window.run) window.run();
  const w = $(".wipe-a");
  if (w) { w.style.transition = "transform .8s cubic-bezier(.65,0,.35,1)"; requestAnimationFrame(() => { w.style.transform = "translateX(105%)"; }); }
  const end = parseFloat(Q.get("dur") || 0);
  if (end) at(end - 0.7, () => { const e = $(".wipe-b"); if (e) { e.style.transition = "transform .7s cubic-bezier(.65,0,.35,1)"; e.style.transform = "translateX(0)"; } });
};
document.addEventListener("DOMContentLoaded", () => {
  const c1 = window.WIPE || "#2B44FF";
  const sc = $(".scene");
  if (sc) {
    sc.insertAdjacentHTML("beforeend",
      `<div class="wipe"><div class="wipe-a" style="position:absolute;inset:0;background:${c1};transform:translateX(0)"></div><div class="wipe-b" style="position:absolute;inset:0;background:${window.WIPE2 || c1};transform:translateX(-105%)"></div></div>`);
  }
});

function mark(s = 100, c = "#A8792E") {
  return `<svg width="${s}" height="${s}" viewBox="0 0 200 200" fill="none">
    <circle cx="100" cy="100" r="92" stroke="${c}" stroke-width="2.5" />
    <circle cx="100" cy="100" r="82" stroke="${c}" stroke-width="1" stroke-dasharray="3 3" />
    <circle cx="100" cy="100" r="68" stroke="${c}" stroke-width="1" />
    <polygon points="100,20 106,85 100,95 94,85" fill="${c}" />
    <polygon points="100,180 106,115 100,105 94,115" fill="${c}" opacity="0.8" />
    <polygon points="20,100 85,106 95,100 85,94" fill="${c}" />
    <polygon points="180,100 115,106 105,100 115,94" fill="${c}" opacity="0.8" />
    <polygon points="43,43 88,92 92,88" fill="${c}" opacity="0.6" />
    <polygon points="157,43 112,88 108,92" fill="${c}" opacity="0.6" />
    <polygon points="43,157 88,108 92,112" fill="${c}" opacity="0.6" />
    <polygon points="157,157 112,112 108,108" fill="${c}" opacity="0.6" />
    <circle cx="100" cy="100" r="10" fill="${c}" />
  </svg>`;
}

const ICONS = {
  check: '<path d="M5 13l4 4L19 7"/>', x: '<path d="M6 6l12 12M18 6L6 18"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>'
};
function ico(name, s = 24, c = "currentColor") {
  return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]||""}</svg>`;
}
