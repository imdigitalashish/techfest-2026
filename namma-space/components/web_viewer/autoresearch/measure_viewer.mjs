// FROZEN evaluator for spike E (fidelity-constrained first-person delivery). The ratchet must not edit it.
// S_V = max(T_visible / 5000 ms, F95 / 20 ms)  — lower is better; 1.0 = exactly on budget.
//   T_visible : ms from navigation start until the splat scene reports loaded (SplatMesh.initialized)
//   F95       : p95 rAF frame time during a scripted walk (route to the farthest navigable cell, auto-walk 8 s)
// Protocol: installed Google Chrome via playwright-core, fresh context (cold cache), 1280x800, DPR 1,
// network throttled to 40 Mbit/s down, 10 Mbit/s up, 40 ms RTT (CDP). Fidelity is constrained separately
// (held-out PSNR from the packager variant, <= 1 dB loss).
// Usage: node measure_viewer.mjs <site_url> [out.json] [--no-throttle]
import { chromium } from "playwright-core";
import fs from "node:fs";

const url = process.argv[2];
const out = process.argv[3] && !process.argv[3].startsWith("--") ? process.argv[3] : null;
const throttle = !process.argv.includes("--no-throttle");
const browser = await chromium.launch({ channel: "chrome", headless: false, args: ["--window-size=1280,860"] });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
const cdp = await ctx.newCDPSession(page);
if (throttle) {
  await cdp.send("Network.enable");
  await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 40,
    downloadThroughput: (40e6 / 8), uploadThroughput: (10e6 / 8) });
}
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
const t0 = Date.now();
await page.goto(url, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => window.__nsStats && window.__nsStats().splats_loaded_ms !== null, null, { timeout: 180000 });
const loaded = await page.evaluate(() => window.__nsStats());
await page.waitForTimeout(1500);
await page.evaluate(() => window.__nsResetStats());
await page.waitForTimeout(3000);
const idle = await page.evaluate(() => window.__nsStats());
const route = await page.evaluate(() => window.__nsRouteToFarthest());
await page.evaluate(() => { window.__nsResetStats(); window.__nsAutoWalk(); });
await page.waitForTimeout(8000);
const walk = await page.evaluate(() => window.__nsStats());
const res = {
  url, when: new Date().toISOString(), throttle: throttle ? "40/10 Mbit/s, 40 ms" : "none",
  chrome: browser.version(), viewport: "1280x800@1x",
  T_visible_ms: loaded.splats_loaded_ms, first_frame_ms: loaded.first_frame_ms, wall_ms_to_loaded: Date.now() - t0,
  idle: { fps_median: idle.fps_median, frame_ms_p95: idle.frame_ms_p95, frames: idle.frames },
  walk: { fps_median: walk.fps_median, frame_ms_p95: walk.frame_ms_p95, frames: walk.frames, on_navigable: walk.on_navigable },
  route, n_splats: loaded.n_splats, splat_bytes: loaded.splat_bytes, page_errors: errors,
};
res.S_V = Math.max(res.T_visible_ms / 5000, res.walk.frame_ms_p95 / 20);
console.log(`score ${res.S_V.toFixed(3)}`);
console.log(JSON.stringify(res));
if (out) fs.writeFileSync(out, JSON.stringify(res, null, 1));
await browser.close();
