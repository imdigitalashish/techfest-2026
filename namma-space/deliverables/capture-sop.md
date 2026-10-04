# Namma Space — Capture SOP v1.1 (phone → navigable 3D twin)

**Who:** anyone with a smartphone. **Time:** ~15–20 min for a 2–3 room home (prep 5 min + ~2 min per room + 3 min checks; estimate, not yet measured). **Output:** one or more videos + a filled `capture.json`, which our pipeline turns into a walkable 3D web twin with POIs and paths.

> Status: v1.1, 4 Oct 2026 (v1.1: one lens for all clips; voice/OCR features marked as planned — review findings H7, H8). Rules come from what our pipeline needs: camera posing (COLMAP global SfM), 3D Gaussian Splatting, and floor/obstacle extraction for navigation. Each rule has a *why*. The cross-check against official capture guides is in `research/capture-best-practices.md` (pending); see `research/companies.md` for vendor guidance found so far.

## The 5 rules that matter most
1. **Sharp frames.** Walk slowly (about half your normal pace) and turn slowly (a full turn takes at least 12 s). Blurry frames are the main cause of failed reconstructions.
2. **Move, don't spin.** Never rotate on the spot. Always rotate *while walking sideways or forwards*. Posing needs parallax, and a pure rotation gives none.
3. **Doorways are where twins break.** Pass every doorway at half speed with the door frame in view, and pause 1 s on each side. Never stop recording between rooms.
4. **Show the floor.** Tilt the phone 20–40° down for one loop of every room so that floor–wall edges and furniture legs are visible. Navigation is computed from the floor and from obstacle footprints.
5. **Walk the routes people walk.** Your walking path is recorded and used as proof of walkable space. Walk the real routes (door → sofa → kitchen) and don't climb over furniture.

## 1. Kit (checklist)
- [ ] Phone, charged >60%, with ≥10 GB free. Note the model, and whether it has LiDAR (iPhone 12 Pro or later "Pro" models do).
- [ ] Lens cleaned with a cloth (fingerprints cause haze in every frame).
- [ ] **Scale reference (pick one):**
  - (a) *Best:* print `assets/marker_aruco_4x4_id0_150mm.pdf` at 100% scale on A4 and check that the black square measures 150 mm. Tape it flat on the floor of the main room.
  - (b) *No printer:* measure your **camera height** — hold the phone the way you will film, and measure floor → phone with a tape (e.g. 1.35 m). Write it in `capture.json`.
- [ ] Optional: a second person to open doors and keep people and pets out of frame.

## 2. Phone settings (do once)
| Setting | iPhone | Android | Why |
|---|---|---|---|
| Mode | Camera → **Video** | Camera → Video (Pro/Manual video if available) | Video gives dense overlap automatically |
| Resolution / fps | **4K at 30 fps** (Settings → Camera → Record Video) | 4K 30 fps | More pixels per frame → sharper splats; we extract ~2–4 frames/s |
| HDR video | **Off** (Settings → Camera → Record Video → HDR Video) | HDR off | HDR (HLG/Dolby Vision) frames tone-map inconsistently when extracted |
| Lens | **1× main lens for every clip**; don't zoom or switch lenses, even in small rooms | 1× main | The pipeline assumes **one camera model for the whole capture** (all clips). Mixing 0.5× and 1× breaks the shared intrinsics |
| Stabilisation | Standard (avoid "Action mode" / "Cinematic") | Standard | Action and Cinematic modes crop and warp frames |
| Exposure/focus | Long-press the screen on a mid-brightness wall → **AE/AF LOCK** | Lock AE/AF (Pro mode: shutter ≥1/120 s, ISO auto) | Brightness that changes between frames creates "floaters" and colour seams |
| Orientation | **Landscape**; never rotate the phone mid-clip | Landscape | Constant image size and intrinsics |
| Audio | **On** | On | Voice tags (§4) are recorded now; automatic POIs from them are planned for Round 2 (today POIs are tagged in the viewer) |

*Pro option (best quality):* the free **Blackmagic Camera** app (iOS/Android) can lock shutter (1/120–1/250 s), ISO and white balance. Use it if you are comfortable with it.

## 3. Prepare the space (5 min)
- [ ] **All lights on**; draw curtains halfway if direct sun makes bright patches on the floor. Keep the lighting the same for the whole capture.
- [ ] **Open every interior door fully.** Open doorways become paths in the navigation graph.
- [ ] Clear loose items from the floor; walking lanes should be clear, like on a normal day.
- [ ] People and pets out of the rooms being filmed. Turn TVs and monitors off (dark screens are stable; moving video is not).
- [ ] **Large mirrors and glass doors:** cover big mirrors with a sheet if you can. Otherwise note them in `capture.json`. Mirrors create phantom rooms, which would otherwise look walkable.
- [ ] Privacy: remove documents, photos and screens you don't want in a public 3D model.
- [ ] Place the scale marker (if printed) flat on the floor, in the open, near the main entrance.

## 4. Capture (one continuous video per floor)
Hold the phone at chest height in landscape. Keep it upright (don't roll it sideways).

**A. Start — marker anchor (15 s).** Start recording standing 1.5 m from the marker. Walk a slow half-circle around it with the phone pointing at it, so it appears in many frames. If there is no marker, film the floor and a room corner from 2 m for 10 s.

**B. Each room — three passes (~2 min per room):**
1. **Enter:** walk through the doorway at half speed, pause 1 s, and say the room name aloud: *"Living room"* (voice tag).
2. **Loop 1 — inward:** walk around the room about 1 m from the walls, pointing the phone at the centre of the room. Do a full loop.
3. **Loop 2 — outward and down:** walk the loop again (opposite direction is fine), now pointing at the walls and furniture and **tilted 20–40° down**, so that floor edges, furniture legs, the bottoms of door frames and the floor around obstacles are visible.
4. **Corners and features:** at each corner and each important object, slow down and sweep across it while still moving sideways. Say what it is: *"Fridge"*, *"Three-seater sofa"*, *"Study table"* (recorded for automatic POI extraction, planned for Round 2).
5. **Route pass:** walk the main routes through the room (door → each seat/bed/table → next door) with the phone tilted ~30° down. These walks tell the planner where people actually walk.
6. **Exit:** walk out through the doorway at half speed, pause 1 s on the other side, and say the next room's name.

**C. Corridors / hallways:** walk down the middle facing forwards, then come back facing the other way. Pause at each door and say its label (*"Bedroom 2"*, *"Meeting Room 4"*). Point at any door sign or room number for 2 s (sign reading by OCR is planned for Round 2).

**D. End:** finish back at the marker (or the starting corner) and film it for 5 s. Closing the loop lets the reconstruction correct drift.

**If you must stop** (battery, a phone call): start the next clip by re-filming the last 5 seconds of the previous clip's view (same spot, same direction), so the clips overlap.

**Speeds:** walking ≈0.5 m/s; turning ≤30°/s. If the on-screen image smears when you pause the video, you are going too fast.

**Avoid:** zooming · switching lenses · running · fast pans · filming a blank wall from closer than 1 m (always keep some edges or furniture in view) · your own reflection or shadow · turning lights on or off mid-capture · stepping on the marker.

## 5. Photo mode (only if video is impossible)
Same paths as §4. Take one photo every half step (~30–40 cm), with each photo sharing ~70% of its view with the previous one. Expect 40–80 photos per room. Lock exposure the same way.

## 6. Check before you leave (3 min)
- [ ] Play the video back at 1×. Pause at 5 random moments: is the frame sharp? If more than one in five is blurry, re-shoot that room.
- [ ] Every doorway crossed slowly, with a pause on both sides? Every room has both loops?
- [ ] The marker (or the start corner) appears at the start **and** the end.
- [ ] The voice tags are audible.
- [ ] If you have a laptop: `python namma-space/components/ingest/check_capture.py <video>` prints a blur and coverage report. *(Planned tool, not yet built.)*

## 7. Hand-off (without recompression)
- **Never send via WhatsApp/Telegram/Instagram**: they recompress the video and destroy detail.
- iPhone → Mac: AirDrop (in Options, enable "All Photos Data" if offered) or a USB cable. Android: USB cable, or upload the original file to Google Drive.
- Put the videos and `capture.json` in one folder: `capture_<space>_<YYYYMMDD>/`.

## 8. `capture.json` (fill in; template below)
```json
{
  "space_name": "Ashish home",
  "date": "2026-10-04",
  "phone_model": "iPhone 15 Pro",
  "has_lidar": true,
  "lens": "1x",
  "resolution_fps": "3840x2160@30",
  "hdr_video": false,
  "app": "Camera",
  "camera_height_m": 1.35,
  "marker": {"type": "aruco_4x4_50", "id": 0, "size_mm": 150, "placed_in": "living room"},
  "rooms": ["Living room", "Kitchen", "Bedroom 1", "Bathroom"],
  "pois_to_tag": ["Three-seater sofa", "Fridge", "Study table"],
  "mirrors_or_glass": ["Bathroom mirror (covered)"],
  "clips": ["IMG_0412.MOV"],
  "notes": "Kitchen light flickers"
}
```

## 9. Large-venue mode (finals: a new campus venue, e.g. a lecture hall complex, under time pressure)
- **Two people:** a *camera operator* (follows §4) and a *navigator* (plans the route on a sketch, keeps people out of frame, notes room numbers).
- **Spine first:** capture the corridors as one continuous "spine" clip, with voice tags at every door. Then capture each room as its own clip that **starts and ends in the corridor** (re-film the doorway on the way in and out). That overlap is what joins the rooms automatically.
- **Prioritise:** the rooms named in the task first, then corridors and landmarks (stairs, lifts, washrooms, exits), then everything else.
- **Upload while capturing:** after each clip, the navigator starts the upload, so reconstruction runs in parallel with capture.
- **Budget (estimate, to be measured in rehearsal):** ~1 min of video per 10 m of corridor, ~2 min per classroom, ~4 min per large hall.

## 10. Why each rule exists (for judges and teammates)
| Rule | Pipeline reason |
|---|---|
| Slow motion, locked exposure | Feature matching and splat optimisation assume sharp, photometrically consistent images; blur and brightness changes become floaters |
| Translate, don't spin | Two views of a point give its depth only if the camera centres differ (parallax) |
| Slow doorways, overlap between clips | Rooms connect through a few shared features; a fast doorway pass splits the model into disconnected pieces |
| Floor visible, tilted pass | The floor plane, gravity alignment and obstacle footprints for the navmesh all come from floor observations |
| Walk real routes | The camera trajectory is evidence of free, walkable space (used by our walkable-space component) |
| Marker or camera height | Reconstructions from images alone have unknown scale; navigation needs metres (agent radius, eye height, walking speed) |
| Voice tags and sign close-ups | Planned (Round 2): speech/OCR timestamps → camera pose at that moment → automatic POI names and positions. Recorded now so the same capture can be reprocessed |
| Doors open, mirrors covered | Closed doors read as walls; mirrors read as fake rooms |
