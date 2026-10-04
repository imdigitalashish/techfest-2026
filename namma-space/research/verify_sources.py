#!/usr/bin/env python3
"""Verify landscape sources against primary endpoints; write sources_verified_<date>.tsv.

repos  : GitHub REST API via `gh api repos/<o>/<r>` (stars, last push, licence, description)
papers : arXiv API title-phrase search (id, first-version date, title) — a match is accepted only if
         the returned title equals the query title after normalisation (else MISMATCH)
pages  : HTTP GET of official product pages (<title>, og:description)
Usage: python research/verify_sources.py  (network; ~2-5 min)
"""
import concurrent.futures as cf
import datetime as dt
import html
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request

REPOS = ["colmap/colmap", "colmap/glomap", "ArthurBrussee/brush", "pierotofy/OpenSplat", "nerfstudio-project/gsplat",
         "graphdeco-inria/gaussian-splatting", "facebookresearch/vggt", "facebookresearch/map-anything",
         "naver/mast3r", "naver/dust3r", "ByteDance-Seed/Depth-Anything-3", "yyfz/Pi3", "sparkjsdev/spark",
         "playcanvas/supersplat", "playcanvas/engine", "mkkellogg/GaussianSplats3D", "nianticlabs/spz",
         "isaac-mason/recast-navigation-js", "recastnavigation/recastnavigation", "facebookresearch/habitat-sim",
         "cvg/Hierarchical-Localization", "minghanqin/LangSplat", "lkeab/gaussian-grouping", "facebookresearch/sam2",
         "facebookresearch/sam3", "IDEA-Research/GroundingDINO", "concept-graphs/concept-graphs",
         "rmurai0610/MASt3R-SLAM", "nianticlabs/ace", "hbb1/2d-gaussian-splatting", "zju3dv/PGSR",
         "autonomousvision/gaussian-opacity-fields", "openai/whisper", "ml-explore/mlx"]
PAPERS = ["3D Gaussian Splatting for Real-Time Radiance Field Rendering",
          "2D Gaussian Splatting for Geometrically Accurate Radiance Fields",
          "VGGT: Visual Geometry Grounded Transformer", "Grounding Image Matching in 3D with MASt3R",
          "DUSt3R: Geometric 3D Vision Made Easy", "Global Structure-from-Motion Revisited",
          "MapAnything: Universal Feed-Forward Metric 3D Reconstruction",
          "Depth Anything 3: Recovering the Visual Space from Any Views",
          "LangSplat: 3D Language Gaussian Splatting", "Gaussian Grouping: Segment and Edit Anything in 3D Scenes",
          "Splat-Nav: Safe Real-Time Robot Navigation in Gaussian Splatting Maps",
          "SAM 2: Segment Anything in Images and Videos",
          "ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning",
          "MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors",
          "Gaussian Opacity Fields: Efficient Adaptive Surface Reconstruction in Unbounded Scenes",
          "AnySplat: Feed-forward 3D Gaussian Splatting from Unconstrained Views",
          "Fast3R: Towards 3D Reconstruction of 1000+ Images in One Forward Pass",
          "Accelerated Coordinate Encoding: Learning to Relocalize in Minutes using RGB and Poses",
          "Hierarchical 3D Gaussian Representation for Real-Time Rendering of Very Large Datasets",
          "SAM 3: Segment Anything with Concepts", "Taming 3DGS: High-Quality Radiance Fields with Limited Resources",
          "3D Gaussian Splatting as Markov Chain Monte Carlo",
          "ScanNet++: A High-Fidelity Dataset of 3D Indoor Scenes",
          "ARKitScenes: A Diverse Real-World Dataset For 3D Indoor Scene Understanding Using Mobile RGB-D Data",
          "Robust Speech Recognition via Large-Scale Weak Supervision"]
PAGES = ["https://matterport.com/", "https://poly.cam/", "https://scaniverse.com/", "https://www.nianticspatial.com/",
         "https://lumalabs.ai/", "https://www.worldlabs.ai/", "https://sparkjs.dev/", "https://superspl.at/",
         "https://developer.apple.com/augmented-reality/roomplan/", "https://www.kiriengine.app/",
         "https://www.navvis.com/", "https://www.pointr.tech/", "https://mapsted.com/", "https://www.indooratlas.com/",
         "https://immersal.com/", "https://www.multiset.ai/", "https://www.realityscan.com/", "https://www.jawset.com/",
         "https://developers.google.com/ar", "https://immersive-web.github.io/webxr-ar-module/"]
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154 Safari/537.36"}
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def repo(r):
    try:
        out = subprocess.run(["gh", "api", f"repos/{r}"], capture_output=True, text=True, timeout=60)
        if out.returncode:
            return ["repo", r, "NOT_FOUND", "", "", out.stderr.strip()[:80]]
        j = json.loads(out.stdout)
        return ["repo", j["full_name"], "OK", f"stars={j['stargazers_count']} pushed={j['pushed_at'][:10]}",
                (j.get("license") or {}).get("spdx_id") or "none", (j.get("description") or "")[:120]]
    except Exception as e:
        return ["repo", r, "ERROR", "", "", str(e)[:80]]


def paper(t):
    q = urllib.parse.quote('ti:"%s"' % re.sub(r"[:,+]", " ", t))
    url = f"http://export.arxiv.org/api/query?search_query={q}&max_results=3"
    for attempt in range(3):
        try:
            x = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode()
            for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
                title = " ".join(html.unescape(re.search(r"<title>(.*?)</title>", e, re.S).group(1)).split())
                aid = re.search(r"<id>http://arxiv.org/abs/(.*?)</id>", e).group(1)
                pub = re.search(r"<published>(.*?)</published>", e).group(1)[:10]
                if norm(title) == norm(t):
                    return ["paper", f"arXiv:{aid}", "OK", f"v1={pub}", "", title]
            return ["paper", t[:60], "MISMATCH_OR_NONE", "", "", ""]
        except Exception as e:
            err = str(e)[:80]
            time.sleep(4 * (attempt + 1))
    return ["paper", t[:60], "ERROR", "", "", err]


def page(u):
    try:
        x = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read(400000).decode("utf-8", "ignore")
        t = re.search(r"<title[^>]*>(.*?)</title>", x, re.S | re.I)
        d = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:description|description)["\'][^>]+content=["\'](.*?)["\']', x, re.S | re.I)
        return ["page", u, "OK", "", "", (" ".join(html.unescape(t.group(1)).split()) if t else "") + " | " +
                (" ".join(html.unescape(d.group(1)).split())[:160] if d else "")]
    except Exception as e:
        return ["page", u, "ERROR", "", "", str(e)[:80]]


def main():
    rows = []
    with cf.ThreadPoolExecutor(8) as ex:
        rows += list(ex.map(repo, REPOS))
        rows += list(ex.map(page, PAGES))
    with cf.ThreadPoolExecutor(2) as ex:
        rows += list(ex.map(paper, PAPERS))
    day = dt.date.today().isoformat()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"sources_verified_{day}.tsv")
    with open(path, "w") as f:
        f.write("kind\tid\tstatus\tmeta\tlicence\ttitle_or_description\n")
        for r in rows:
            f.write("\t".join(x.replace("\t", " ").replace("\n", " ") for x in r) + "\n")
    ok = sum(r[2] == "OK" for r in rows)
    print(f"{ok}/{len(rows)} verified -> {path}")


if __name__ == "__main__":
    main()
