// Namma Space web viewer (component 11). Contract: loads a ScenePackage manifest
// (architecture/contracts/contracts.ts) given as ?scene=<url to manifest.json>.
import * as THREE from "three";
import { PointerLockControls } from "three/addons/controls/PointerLockControls.js";
import { SparkRenderer, SplatMesh } from "@sparkjsdev/spark";
import { NavGrid, planPath, pathLength } from "./nav.js";

const T0 = performance.now();
const params = new URLSearchParams(location.search);
const base = new URL(params.get("scene") || "scene/manifest.json", location.href);
const $ = (id) => document.getElementById(id);

const manifest = await (await fetch(base)).json();
const nav = new NavGrid(await (await fetch(new URL(manifest.nav.url, base))).json());
let pois = [];
if (manifest.pois && manifest.pois.url) {
  try { pois = await (await fetch(new URL(manifest.pois.url, base))).json(); } catch (e) { console.warn("no pois", e); }
}
const localKey = "namma-pois:" + manifest.name;
pois = pois.concat(JSON.parse(localStorage.getItem(localKey) || "[]"));

// --- renderer, scene, splats ---------------------------------------------------------------
const canvas = $("view");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.setSize(innerWidth, innerHeight);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.05, 200);
const spark = new SparkRenderer({ renderer });
scene.add(spark);
const splats = new SplatMesh({ url: new URL(manifest.splat.url, base).href });
scene.add(splats);
let loadedMs = null;
if (splats.initialized && typeof splats.initialized.then === "function") {
  splats.initialized.then(() => { loadedMs = performance.now(); // ms since navigation start (performance.timeOrigin)
    $("banner").style.display = "none"; });
} else setTimeout(() => ($("banner").style.display = "none"), 1500);

const EYE = manifest.eye_height_m || 1.6;
const sp = manifest.spawn.position;
camera.position.set(sp[0], EYE, sp[2]);
camera.rotation.set(0, THREE.MathUtils.degToRad(manifest.spawn.yaw_deg || 0), 0, "YXZ");

// --- controls ------------------------------------------------------------------------------
const controls = new PointerLockControls(camera, renderer.domElement);
canvas.addEventListener("click", () => controls.lock());
const keys = new Set();
let fly = false, autoWalk = null;
addEventListener("keydown", (e) => {
  if (document.activeElement === $("q")) return;
  keys.add(e.code);
  if (e.code === "Slash") { e.preventDefault(); controls.unlock(); $("q").focus(); }
  if (e.code === "KeyF") { fly = !fly; if (!fly) camera.position.y = EYE; }
  if (e.code === "KeyG" && currentPath) autoWalk = { i: 0 };
  if (e.code === "KeyP") tagPoiHere();
});
addEventListener("keyup", (e) => keys.delete(e.code));
addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight);
});

const vel = new THREE.Vector3(), UP = new THREE.Vector3(0, 1, 0);
function move(dt) {
  if (autoWalk) { stepAutoWalk(dt); return; }
  const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
  if (!fly) { fwd.y = 0; fwd.normalize(); }
  const right = new THREE.Vector3().crossVectors(fwd, UP).normalize();
  const wish = new THREE.Vector3();
  if (keys.has("KeyW") || keys.has("ArrowUp")) wish.add(fwd);
  if (keys.has("KeyS") || keys.has("ArrowDown")) wish.sub(fwd);
  if (keys.has("KeyD") || keys.has("ArrowRight")) wish.add(right);
  if (keys.has("KeyA") || keys.has("ArrowLeft")) wish.sub(right);
  if (fly && keys.has("Space")) wish.y += 1;
  if (fly && keys.has("KeyC")) wish.y -= 1;
  const speed = keys.has("ShiftLeft") || keys.has("ShiftRight") ? 3.0 : 1.4;
  if (wish.lengthSq() > 0) wish.normalize().multiplyScalar(speed);
  vel.lerp(wish, 1 - Math.exp(-10 * dt)); // smooth acceleration and deceleration
  const p = camera.position;
  // sub-step so a fast step at a low frame rate can never tunnel through a one-cell (5 cm) wall
  const steps = Math.max(1, Math.ceil((Math.hypot(vel.x, vel.z) * dt) / (nav.cell * 0.5)));
  for (let s = 0; s < steps; s++) {
    const nx = p.x + (vel.x * dt) / steps, nz = p.z + (vel.z * dt) / steps;
    if (fly || !nav.isFreeXZ(p.x, p.z)) { p.x = nx; p.z = nz; } // never trap a user who starts off-grid
    else if (nav.isFreeXZ(nx, nz)) { p.x = nx; p.z = nz; }
    else if (nav.isFreeXZ(nx, p.z)) { p.x = nx; vel.z = 0; } // slide along walls
    else if (nav.isFreeXZ(p.x, nz)) { p.z = nz; vel.x = 0; }
    else { vel.set(0, vel.y, 0); break; }
  }
  if (fly) p.y += vel.y * dt; else p.y = EYE;
}

// --- routes, POIs, search ------------------------------------------------------------------
let currentPath = null, pathObj = null, lastPlanMs = null;
const pathMat = new THREE.MeshBasicMaterial({ color: 0xff8a00, transparent: true, opacity: 0.9, depthTest: false });
function showPath(xz, label) {
  if (pathObj) { scene.remove(pathObj); pathObj.geometry.dispose(); pathObj = null; }
  currentPath = xz;
  if (!xz || xz.length < 2) { $("route").style.display = "none"; return; }
  const curve = new THREE.CurvePath();
  for (let i = 1; i < xz.length; i++) curve.add(new THREE.LineCurve3(new THREE.Vector3(xz[i - 1][0], 0.04, xz[i - 1][1]), new THREE.Vector3(xz[i][0], 0.04, xz[i][1])));
  pathObj = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(16, xz.length * 24), 0.05, 6, false), pathMat);
  pathObj.renderOrder = 10;
  scene.add(pathObj);
  $("route").style.display = "block";
  $("route").textContent = `Route to ${label}: ${pathLength(xz).toFixed(1)} m · press G to walk it`;
}
function routeTo(x, z, label) {
  const r = planPath(nav, [camera.position.x, camera.position.z], [x, z]);
  lastPlanMs = r.ms;
  if (!r.ok) { $("route").style.display = "block"; $("route").textContent = `No walkable route to ${label}`; return null; }
  showPath(r.xz, label); return r;
}
function stepAutoWalk(dt) {
  const xz = currentPath, p = camera.position;
  if (!xz || autoWalk.i >= xz.length) { autoWalk = null; return; }
  const [tx, tz] = xz[autoWalk.i], dx = tx - p.x, dz = tz - p.z, d = Math.hypot(dx, dz), step = 1.4 * dt;
  if (d <= step) { p.x = tx; p.z = tz; autoWalk.i++; return; }
  p.x += (dx / d) * step; p.z += (dz / d) * step; p.y = EYE;
  const e = new THREE.Euler().setFromQuaternion(camera.quaternion, "YXZ");
  let dy = Math.atan2(-dx, -dz) - e.y; dy = Math.atan2(Math.sin(dy), Math.cos(dy));
  e.y += dy * Math.min(1, 4 * dt); e.x *= 1 - Math.min(1, 2 * dt); camera.quaternion.setFromEuler(e);
}
function flyTo(poi) {
  const [ax, az] = poi.approach_xz || [poi.position[0], poi.position[2]];
  if (routeTo(ax, az, poi.label)) autoWalk = { i: 0 };
}
function tagPoiHere() {
  controls.unlock();
  const label = prompt("Name this place or item (e.g. Kitchen, Three-seater sofa):");
  if (!label) return;
  const p = camera.position, d = new THREE.Vector3(); camera.getWorldDirection(d);
  const poi = { id: "local-" + Date.now(), label, aliases: [], kind: "item", source: "manual", confidence: 1,
    position: [p.x + d.x, 1.0, p.z + d.z], approach_xz: [p.x, p.z] };
  pois.push(poi);
  const mine = JSON.parse(localStorage.getItem(localKey) || "[]"); mine.push(poi);
  localStorage.setItem(localKey, JSON.stringify(mine));
  addPoiSprite(poi); renderResults();
  console.log("POIs (paste into pois.json):", JSON.stringify(pois));
}
const norm = (s) => s.toLowerCase().normalize("NFKD").replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
function score(q, poi) {
  q = norm(q); if (!q) return 0;
  let best = 0;
  for (const n of [poi.label, ...(poi.aliases || [])].map(norm)) {
    if (n === q) best = Math.max(best, 1);
    else if (n.startsWith(q)) best = Math.max(best, 0.9);
    else if (n.includes(q)) best = Math.max(best, 0.75);
    else { const qt = q.split(" "); best = Math.max(best, (0.6 * qt.filter((t) => n.includes(t)).length) / qt.length); }
  }
  return best;
}
function renderResults() {
  const q = $("q").value, box = $("results"); box.innerHTML = "";
  let ranked = pois.map((p) => [score(q, p), p]).filter(([s]) => s > 0.2).sort((a, b) => b[0] - a[0]).slice(0, 8);
  if (!q) ranked = pois.slice(0, 8).map((p) => [0, p]);
  for (const [, p] of ranked) {
    const el = document.createElement("div"); el.textContent = `${p.label} · ${p.kind || "poi"}`;
    el.onclick = () => { flyTo(p); $("q").blur(); }; box.appendChild(el);
  }
  if (!pois.length) box.textContent = "No POIs yet — press P while walking to tag one.";
  return ranked;
}
$("q").addEventListener("input", renderResults);
$("q").addEventListener("keydown", (e) => {
  if (e.key === "Enter") { const r = renderResults(); if (r.length) { flyTo(r[0][1]); $("q").blur(); } }
  if (e.key === "Escape") $("q").blur();
});
function addPoiSprite(poi) {
  const c = document.createElement("canvas"); c.width = 512; c.height = 96;
  const g = c.getContext("2d"); g.fillStyle = "rgba(20,20,28,0.85)"; g.fillRect(0, 0, 512, 96);
  g.fillStyle = "#fff"; g.font = "bold 44px system-ui"; g.textBaseline = "middle"; g.fillText(poi.label, 24, 50);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthTest: false, transparent: true }));
  s.scale.set(1.2, 0.225, 1); s.position.set(poi.position[0], poi.position[1] + 0.4, poi.position[2]); s.renderOrder = 20;
  scene.add(s);
}
pois.forEach(addPoiSprite);
renderResults();

// --- minimap (click to route) --------------------------------------------------------------
const mini = $("minimap"), ms = Math.min(260 / nav.nx, 260 / nav.nz);
mini.width = Math.round(nav.nx * ms); mini.height = Math.round(nav.nz * ms);
const mctx = mini.getContext("2d"), baseCanvas = document.createElement("canvas");
baseCanvas.width = nav.nx; baseCanvas.height = nav.nz;
baseCanvas.getContext("2d").putImageData(nav.toImageData(baseCanvas.getContext("2d")), 0, 0);
const toMini = (x, z) => [((x - nav.lo[0]) / nav.cell) * ms, ((z - nav.lo[1]) / nav.cell) * ms];
mini.addEventListener("click", (e) => {
  const r = mini.getBoundingClientRect();
  routeTo(nav.lo[0] + ((e.clientX - r.left) / ms) * nav.cell, nav.lo[1] + ((e.clientY - r.top) / ms) * nav.cell, "pin");
});
function drawMini() {
  mctx.imageSmoothingEnabled = false;
  mctx.drawImage(baseCanvas, 0, 0, mini.width, mini.height);
  if (currentPath) {
    mctx.strokeStyle = "#ff8a00"; mctx.lineWidth = 2; mctx.beginPath();
    currentPath.forEach(([x, z], i) => { const [u, v] = toMini(x, z); if (i) mctx.lineTo(u, v); else mctx.moveTo(u, v); });
    mctx.stroke();
  }
  mctx.fillStyle = "#3fa9ff"; for (const p of pois) { const [u, v] = toMini(p.position[0], p.position[2]); mctx.fillRect(u - 2, v - 2, 4, 4); }
  const [u, v] = toMini(camera.position.x, camera.position.z), d = new THREE.Vector3(); camera.getWorldDirection(d);
  mctx.fillStyle = "#ff3355"; mctx.beginPath(); mctx.arc(u, v, 4, 0, 7); mctx.fill();
  mctx.strokeStyle = "#ff3355"; mctx.beginPath(); mctx.moveTo(u, v); mctx.lineTo(u + d.x * 12, v + d.z * 12); mctx.stroke();
}

// --- loop and measurement hooks (used by eval/measure_viewer.*) -----------------------------
const frameMs = []; let last = performance.now(), firstFrameMs = null, hudT = 0;
window.__nsStats = () => {
  const a = frameMs.slice(-600).sort((x, y) => x - y), n = a.length;
  return { frames: n, fps_median: n ? 1000 / a[Math.floor(n * 0.5)] : null, frame_ms_p50: n ? a[Math.floor(n * 0.5)] : null,
    frame_ms_p95: n ? a[Math.floor(n * 0.95)] : null, first_frame_ms: firstFrameMs, splats_loaded_ms: loadedMs,
    n_splats: manifest.splat.n_splats, splat_bytes: manifest.splat.bytes, last_plan_ms: lastPlanMs,
    pos: [camera.position.x, camera.position.y, camera.position.z], on_navigable: nav.isFreeXZ(camera.position.x, camera.position.z) };
};
window.__nsRouteToFarthest = () => { const f = nav.farthestFrom(camera.position.x, camera.position.z); const r = routeTo(f[0], f[1], "test"); return r ? { ok: true, ms: r.ms, n: r.xz.length, length_m: pathLength(r.xz) } : { ok: false }; };
window.__nsAutoWalk = () => { if (currentPath) autoWalk = { i: 0 }; return !!currentPath; };
window.__nsResetStats = () => { frameMs.length = 0; };
renderer.setAnimationLoop(() => {
  const now = performance.now(), dt = Math.min(0.05, (now - last) / 1000);
  frameMs.push(now - last); last = now;
  if (frameMs.length > 2000) frameMs.splice(0, 1000);
  move(dt);
  renderer.render(scene, camera);
  if (firstFrameMs === null) firstFrameMs = now; // ms since navigation start
  if (now - hudT > 250) {
    hudT = now; drawMini();
    const s = window.__nsStats(), p = camera.position;
    $("hud").textContent = `fps ${s.fps_median ? s.fps_median.toFixed(0) : "-"} · p95 ${s.frame_ms_p95 ? s.frame_ms_p95.toFixed(1) : "-"} ms · ${(manifest.splat.n_splats / 1e6).toFixed(2)}M splats\n` +
      `pos ${p.x.toFixed(2)}, ${p.z.toFixed(2)} · ${fly ? "fly" : "walk (collisions on)"}${lastPlanMs !== null ? ` · route ${lastPlanMs.toFixed(1)} ms` : ""}`;
  }
});
