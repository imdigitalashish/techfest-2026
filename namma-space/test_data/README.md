# Test data

| Set | What | How to get it | Use |
|---|---|---|---|
| `drjohnson` (public) | Deep Blending *drjohnson*: 263 photos (1332×876) of a multi-room house, with a reference COLMAP model | `./test_data/fetch_drjohnson.sh` (≈208 MB, from the Hugging Face mirror `nvs-bench/deepblending`) | End-to-end pipeline test and component metrics. Non-commercial research licence: not redistributed here, and twins built from it are not hosted publicly |
| `sample_home/` (ours) | A downscaled subset of our own home capture (videos → keyframes) + `capture.json` | Added after the capture (owned by the team, so it can be redistributed) | The Round-1 "sample data in a test directory" requirement |

Run the full pipeline on the public scene:
```bash
./setup.sh
./test_data/fetch_drjohnson.sh
./process_capture.sh .data/deepblending/drjohnson/images drjohnson_e2e --reference-colmap .data/deepblending/drjohnson/sparse/0
```
