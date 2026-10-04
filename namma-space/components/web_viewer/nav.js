// NavGrid decoding + in-browser path planner (JS port of components/path_planner/planner.py).
// Grid layout: row-major (i, k); cell (i,k) centre = (lo_x + (i+0.5)*cell, lo_z + (k+0.5)*cell).
export class NavGrid {
  constructor(j) {
    this.nx = j.nx; this.nz = j.nz; this.cell = j.cell_m; this.lo = j.lo_xz;
    this.radius = (j.params && j.params.agent_radius) || 0.25;
    this.nav = decodeBits(j.navigable_b64, this.nx * this.nz);
    this.obst = decodeBits(j.obstacle_b64, this.nx * this.nz);
    this.dist = chamfer(this.nav, this.nx, this.nz, this.cell); // metres to nearest non-navigable cell
  }
  idx(i, k) { return i * this.nz + k; }
  toIJ(x, z) { return [Math.floor((x - this.lo[0]) / this.cell), Math.floor((z - this.lo[1]) / this.cell)]; }
  toXZ(i, k) { return [this.lo[0] + (i + 0.5) * this.cell, this.lo[1] + (k + 0.5) * this.cell]; }
  inside(i, k) { return i >= 0 && k >= 0 && i < this.nx && k < this.nz; }
  free(i, k) { return this.inside(i, k) && this.nav[this.idx(i, k)] === 1; }
  isFreeXZ(x, z) { const [i, k] = this.toIJ(x, z); return this.free(i, k); }
  snap(i, k) { // exact Euclidean-nearest navigable cell (matches planner.py's EDT snap)
    i = Math.min(this.nx - 1, Math.max(0, i)); k = Math.min(this.nz - 1, Math.max(0, k));
    if (this.free(i, k)) return [i, k];
    let best = null, bd = Infinity;
    const test = (a, b) => { if (this.free(a, b)) { const d = (a - i) ** 2 + (b - k) ** 2; if (d < bd) { bd = d; best = [a, b]; } } };
    for (let r = 1; r < Math.max(this.nx, this.nz); r++) {
      if (best && r > Math.sqrt(bd)) break; // cells on ring r are at least r away
      for (let a = i - r; a <= i + r; a++) { test(a, k - r); test(a, k + r); }
      for (let b = k - r + 1; b <= k + r - 1; b++) { test(i - r, b); test(i + r, b); }
    }
    return best;
  }
  farthestFrom(x, z) {
    let best = null, bd = -1;
    for (let i = 0; i < this.nx; i += 2) for (let k = 0; k < this.nz; k += 2) if (this.free(i, k)) {
      const [cx, cz] = this.toXZ(i, k), d = Math.hypot(cx - x, cz - z); if (d > bd) { bd = d; best = [cx, cz]; }
    }
    return best;
  }
  toImageData(ctx) {
    const img = ctx.createImageData(this.nx, this.nz);
    for (let i = 0; i < this.nx; i++) for (let k = 0; k < this.nz; k++) {
      const o = (k * this.nx + i) * 4, id = this.idx(i, k);
      const c = this.nav[id] ? [200, 235, 200] : this.obst[id] ? [25, 25, 25] : [90, 90, 96];
      img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2]; img.data[o + 3] = 255;
    }
    return img;
  }
}

function decodeBits(b64, n) {
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)), out = new Uint8Array(n);
  for (let b = 0; b < n; b++) out[b] = (bytes[b >> 3] >> (7 - (b & 7))) & 1;
  return out;
}

function chamfer(nav, nx, nz, cell) { // 3-4 chamfer distance (~Euclidean) to non-navigable cells
  const INF = 1e9, d = new Float32Array(nx * nz);
  for (let p = 0; p < d.length; p++) d[p] = nav[p] ? INF : 0;
  const at = (i, k) => (i < 0 || k < 0 || i >= nx || k >= nz ? 0 : d[i * nz + k]);
  for (let i = 0; i < nx; i++) for (let k = 0; k < nz; k++) { const p = i * nz + k; if (!d[p]) continue;
    d[p] = Math.min(d[p], at(i - 1, k) + 3, at(i, k - 1) + 3, at(i - 1, k - 1) + 4, at(i - 1, k + 1) + 4); }
  for (let i = nx - 1; i >= 0; i--) for (let k = nz - 1; k >= 0; k--) { const p = i * nz + k; if (!d[p]) continue;
    d[p] = Math.min(d[p], at(i + 1, k) + 3, at(i, k + 1) + 3, at(i + 1, k + 1) + 4, at(i + 1, k - 1) + 4); }
  for (let p = 0; p < d.length; p++) d[p] = (d[p] / 3) * cell;
  return d;
}

class Heap { // binary min-heap of [f, id]
  constructor() { this.a = []; }
  push(f, id) { const a = this.a; a.push([f, id]); let i = a.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (a[p][0] <= a[i][0]) break; [a[p], a[i]] = [a[i], a[p]]; i = p; } }
  pop() { const a = this.a, top = a[0], last = a.pop(); if (a.length) { a[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < a.length && a[l][0] < a[m][0]) m = l; if (r < a.length && a[r][0] < a[m][0]) m = r; if (m === i) break; [a[m], a[i]] = [a[i], a[m]]; i = m; } } return top; }
  get size() { return this.a.length; }
}

const NB = [[-1, 0, 1], [1, 0, 1], [0, -1, 1], [0, 1, 1], [-1, -1, Math.SQRT2], [-1, 1, Math.SQRT2], [1, -1, Math.SQRT2], [1, 1, Math.SQRT2]];

export function planPath(g, startXZ, goalXZ, wClear = 2.0, cPref = 0.6) {
  const t0 = performance.now();
  const s = g.snap(...g.toIJ(...startXZ)), e = g.snap(...g.toIJ(...goalXZ));
  if (!s || !e) return { ok: false, ms: performance.now() - t0 };
  const pen = (id) => 1 + wClear * Math.min(1, Math.max(0, (cPref - (g.dist[id] + g.radius)) / cPref));
  const n = g.nx * g.nz, best = new Float64Array(n).fill(Infinity), came = new Int32Array(n).fill(-1), closed = new Uint8Array(n);
  const sid = g.idx(...s), gid = g.idx(...e), h = (i, k) => Math.hypot(i - e[0], k - e[1]);
  const heap = new Heap(); best[sid] = 0; heap.push(h(...s), sid);
  while (heap.size) {
    const [, u] = heap.pop(); if (closed[u]) continue; if (u === gid) break; closed[u] = 1;
    const i = Math.floor(u / g.nz), k = u % g.nz;
    for (const [di, dk, w] of NB) {
      const a = i + di, b = k + dk; if (!g.free(a, b)) continue;
      if (di && dk && !(g.free(a, k) && g.free(i, b))) continue;
      const v = g.idx(a, b), nd = best[u] + w * 0.5 * (pen(u) + pen(v));
      if (nd < best[v]) { best[v] = nd; came[v] = u; heap.push(nd + h(a, b), v); }
    }
  }
  if (sid !== gid && came[gid] < 0) return { ok: false, ms: performance.now() - t0 };
  const cells = [gid]; while (cells[cells.length - 1] !== sid) cells.push(came[cells[cells.length - 1]]);
  cells.reverse();
  const ij = cells.map((c) => [Math.floor(c / g.nz), c % g.nz]);
  const xz = smooth(g, ij).map(([i, k]) => g.toXZ(i, k));
  return { ok: true, xz, ms: performance.now() - t0, raw_cells: cells.length };
}

function los(g, a, b, eps = 0.05) { // conservative supercover (same rule as planner.py)
  const n = Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])) * 10 + 2;
  for (let s = 0; s <= n; s++) {
    const t = s / n, ui = a[0] + 0.5 + t * (b[0] - a[0]), uk = a[1] + 0.5 + t * (b[1] - a[1]);
    for (const di of [-eps, eps]) for (const dk of [-eps, eps]) if (!g.free(Math.floor(ui + di), Math.floor(uk + dk))) return false;
  }
  return true;
}
function smooth(g, p) {
  if (p.length < 3) return p.slice();
  const out = [p[0]]; let anchor = 0;
  for (let j = 2; j < p.length; j++) if (!los(g, p[anchor], p[j])) { anchor = j - 1; out.push(p[anchor]); }
  out.push(p[p.length - 1]); return out;
}
export function pathLength(xz) { let L = 0; for (let i = 1; i < xz.length; i++) L += Math.hypot(xz[i][0] - xz[i - 1][0], xz[i][1] - xz[i - 1][1]); return L; }
