# Public demo scene — source and licence (verified 2026-10-04)

**Purpose:** a hostable demo of the viewer, and a real-video test of the pipeline's video path (ffmpeg extraction, 60 fps, Theora/Ogg). It is **not our capture** and does **not** replace the Round-1 link, which must be our own space (brief: "map their own home (or a similarly accessible indoor space)").

## Primary demo: Deichman library (Oslo) walkthrough video
| Field | Value (from the Wikimedia Commons file record, opened via the Commons API on 2026-10-04) |
|---|---|
| File page | https://commons.wikimedia.org/wiki/File:Deichmanske_library_Oslo_walkthrough.ogg |
| Author | Asav ("Own work") |
| Licence | **CC BY-SA 4.0** — https://creativecommons.org/licenses/by-sa/4.0 (attribution required) |
| Description | "A March 2021 video tour of the new Deichmanske library building in Oslo, Norway. Music by the Czech National Symphony Orchestra." |
| Media | Ogg/Theora 1920×1080, 59.94 fps, 126.4 s, 255.2 MB (uploaded 2022-07-27) |
| What we use | First 90 s, **video stream only** (the music track is dropped, so it's not in any derivative). Local copy: 180.3 MB, 90.0 s |

**Obligations for anything we derive from it** (keyframes, splats, the hosted twin, screenshots):
- Credit: "Deichman library walkthrough by Asav, CC BY-SA 4.0, via Wikimedia Commons", with the file-page link.
- Indicate changes ("reconstructed into a 3D Gaussian-splat model").
- License the derived 3D model under **CC BY-SA 4.0** (ShareAlike).
- The viewer's manifest `credits` field carries this.

Fetch (reproducible): `ffmpeg -i "https://upload.wikimedia.org/wikipedia/commons/d/da/Deichmanske_library_Oslo_walkthrough.ogg" -t 90 -map 0:v:0 -c copy .data/public_demo/deichman/deichman_walkthrough_90s.ogv`

## Alternative (photo rig, MIT): Eyeful Tower (Meta Reality Labs)
- https://github.com/facebookresearch/EyefulTower — README "License: MIT License, as found in the LICENSE file". Changelog, 11 Mar 2026: "Relicensed all content under the MIT license" (both read 2026-10-04).
- LICENSE begins "MIT License — Copyright (c) Meta Platforms, Inc. and affiliates".
- Multi-camera rig captures. The smallest per-scene download is ≈0.2 GB (`office1a`). v3 scenes include `meeting_room`.
- Caveat: the rig uses several cameras, so it needs per-camera intrinsics in posing (our pipeline assumes one camera). Use it only if the video route fails.

## Not hostable (do not deploy derived twins)
Deep Blending *drjohnson* (non-commercial research licence) · ScanNet/ScanNet++ · Matterport3D/HM3D · Tanks & Temples (contradictory licence page) · Mip-NeRF 360 (licence UNVERIFIED) — see `research/datasets.md`.
