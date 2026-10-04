/**
 * Namma Space — typed contracts between components (v1, 4 Oct 2026).
 * Frames: "colmap" = arbitrary SfM frame; "aligned" = y-up, floor at y = 0, metres (approximate if
 * Alignment.scale_source starts with "ASSUMED"). Arrays are row-major. All files are JSON unless noted.
 * Python implementations emit exactly these shapes (see components/*).
 */

export type Vec3 = [number, number, number];
export type Mat4RowMajor = [Vec3 | number[], number[], number[], number[]];

/** 1 capture → 2 ingest: written by the person capturing (deliverables/capture-sop.md §8). */
export interface CaptureJson {
  space_name: string;
  date: string;                       // ISO date
  phone_model: string;
  has_lidar: boolean;
  lens: "1x" | "0.5x" | string;
  resolution_fps: string;             // e.g. "3840x2160@30"
  hdr_video: boolean;
  app?: string;
  camera_height_m?: number;           // scale fallback when there is no marker
  marker?: { type: "aruco_4x4_50"; id: number; size_mm: number; placed_in?: string };
  rooms?: string[];
  pois_to_tag?: string[];
  mirrors_or_glass?: string[];
  clips: string[];                    // file names, in capture order
  notes?: string;
}

/** 2 ingest → 3 posing / 8 poi-extraction. */
export interface FrameSet {
  frames: { name: string; clip: string; t_s: number; sharpness: number }[];
  voice_tags: { text: string; clip: string; t_start_s: number; t_end_s: number; confidence: number }[];
  intrinsics_hint?: { fx: number; fy: number; cx: number; cy: number; width: number; height: number };
}

/** 3 posing → 4, 5, 6, 8: a COLMAP binary model directory (cameras.bin, images.bin, points3D.bin). */
export interface PosedFrames {
  colmap_dir: string;
  n_registered: number;
  n_frames: number;
  mean_reprojection_error_px: number;
}

/** 4 splat-training → 10: INRIA-style 3DGS PLY (opacity = logit, scale = log, rot = wxyz quaternion). */
export interface SplatModel {
  ply_path: string;
  frame: "colmap";
  n_splats: number;
  train_seconds: number;
  heldout?: { psnr: number; ssim: number; lpips?: number; split: string };
}

/** 5 scene-alignment → 6, 8, 10, 12 (alignment.json). x_aligned = T · [x_colmap, 1]. */
export interface Alignment {
  T_aligned_from_colmap: Mat4RowMajor;  // similarity: s·R | t
  scale: number;
  scale_source: string;                 // "marker" | "capture.json camera_height_m" | "ASSUMED ..."
  up_colmap: Vec3;
  up_camera_consistency: number;        // |mean camera up|, 1 = all upright
  up_refinement_deg: number;
  camera_height_median_m: number;
  floor_inlier_frac: number;
  points_below_floor_frac: number;
  runtime_s: number;
}

/** 6 walkable-space → 7, 10, 11, 12 (nav.json). Bitmasks: np.packbits(row-major (i,k)), base64. */
export interface NavGrid {
  frame: string;
  lo_xz: [number, number];              // cell (i,k) centre = (lo_x + (i+0.5)·cell, lo_z + (k+0.5)·cell)
  cell_m: number;
  nx: number;
  nz: number;
  navigable_b64: string;                // already eroded by agent_radius
  obstacle_b64: string;
  params: {
    cell: number; voxel: number; agent_radius: number; agent_height: number; step_height: number;
    floor_tol: number; floor_dilate_m: number; min_occ_points: number; carve_beta: number;
    traj_radius: number; close_m: number;
  };
}

/** 7 path-planner (Python and the in-browser JS port share this). */
export interface PathRequest { start_xz: [number, number]; goal_xz: [number, number]; goal_poi_id?: string }
export interface PathResult {
  ok: boolean;
  polyline_xz?: [number, number][];     // aligned metres, on the floor (y = 0)
  length_m?: number;
  ms: number;
  snapped_start_m?: number;             // how far start/goal had to move to reach navigable space
  snapped_goal_m?: number;
}

/** 8 poi-extraction → 9, 10, 11, 12 (pois.json). */
export interface POI {
  id: string;
  label: string;                        // "Meeting Room 4", "Three-seater sofa"
  aliases: string[];
  kind: "room" | "zone" | "item" | "landmark";
  position: Vec3;                       // aligned; the anchor shown in the viewer
  approach_xz?: [number, number];       // navigable point in front of it (path goal)
  region_xz?: [number, number][];       // polygon on the floor for rooms/zones (click target)
  source: "manual" | "voice_tag" | "ocr" | "detector" | "vlm";
  confidence: number;
  evidence?: { frame: string; t_s?: number }[];
}

/** 9 search. */
export interface SearchQuery { text: string; near_xz?: [number, number]; k?: number }
export interface SearchResult { poi_id: string; score: number; matched: "exact" | "alias" | "fuzzy" | "semantic" }

/** 10 scene-packager → 11, 12 (manifest.json, the only file the viewer is pointed at). */
export interface ScenePackage {
  schema: "namma-space/scene@1";
  name: string;
  splat: { url: string; format: "splat" | "spz" | "ply" | "sog"; n_splats: number; bytes: number; frame: "aligned" };
  nav: { url: string };                 // NavGrid
  pois: { url: string };                // POI[]
  spawn: { position: Vec3; yaw_deg: number };
  eye_height_m: number;                 // default 1.6
  credits: string[];                    // licences of data and tools used
}

/** 12 ar-navigation: one relocalisation fix from the server. */
export interface ARPoseFix {
  t_ms: number;
  T_aligned_from_device: Mat4RowMajor;  // maps the AR session frame into the twin frame
  inliers: number;
  error_estimate_m: number;
}
