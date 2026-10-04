# What companies ship today: phone capture → navigable indoor twin (as of 4 Oct 2026)

> **Method and honesty rules.** Every claim below comes from a page I opened on **2026-10-04**, either with a scripted HTTP GET that stripped the page to text and grepped it, or with the web-fetch tool. Each claim has its URL beside it, and every **Src** line means "opened 2026-10-04". Web-search answers were used **only as leads** to find URLs. Anything I could not open is marked **UNVERIFIED**, and "—" means *not found on the pages I opened*. That is absence of evidence, not evidence of absence. Dollar prices are copied as shown on the page that day.
> **Search leads that were wrong or unsupported** (a reminder to verify):
> - (a) A search answer said Meta Hyperscape worlds can be shared with "up to 8 users". Meta's own help page says sharing was **removed on 12 May 2026**.
> - (b) A search answer named Delhi, Bengaluru, Mumbai and Hyderabad airports as "among the first" Indian indoor-wayfinding deployments, with no primary source. **UNVERIFIED.**
> - (c) A search answer said Luma "Flythroughs" was sunset on 1 Jan 2026. Its only source was a third-party blog that I did not open, so this is **UNVERIFIED**.
>
> This file supersedes the UNVERIFIED company table in [`landscape.md`](landscape.md) §3.

## 1. Headlines
1. **No company found ships the whole chain in one product:** phone capture → photoreal twin → automatic walkable map → POI search → obstacle-aware route → AR, all behind a zero-install link. The market splits into two camps that don't meet:
   - **capture/twin vendors** (Matterport, Polycam, Niantic Scaniverse, KIRI, Luma, Varjo Teleport, Zillow) stop at viewing, measuring and floor plans;
   - **wayfinding vendors** (Pointr, Mapsted, Mappedin, IndoorAtlas, MapmyIndia, BootWay) route over 2D maps built from floor plans or surveys, not over a photoreal capture.
2. **Gaussian splats are now standard output from phone capture**:
   - Polycam: photos or video;
   - Scaniverse: on-device, exporting SPZ, PLY and FBX;
   - KIRI: 3DGS, plus 3DGS → mesh;
   - Teleport: cloud, 1M–100M splats;
   - Marble: SPZ or PLY output, but its worlds are *generated*.

   None of the twin pages I opened show navigation on top of the splats.
3. **AR localisation is a separate product category** (VPS SDKs: Niantic Spatial Localize, Immersal, MultiSet, IndoorAtlas AR). Three web-relevant facts:
   - **The hosted 8th Wall platform shut down on 28 Feb 2026.** The open-source engine is MIT-licensed but **excludes SLAM**. SLAM ships only in a binary-licensed build, which has no VPS.
   - **ARKit geotracking works "exclusively outdoors".**
   - Google's Indoor Live View exists only in venues that Google has mapped.
4. **Turnarounds stated by vendors:**
   - Meta Hyperscape: processing takes **up to 8 h** in the cloud.
   - Matterport schematic floor plans: **2 business days**, or 24 h (Fast) / 6 h (Express) on Professional.
   - Polycam: floor plans **on-device in minutes**; LiDAR room scans processed "in a few minutes".
   - Scaniverse: splats processed on-device.
   - Same-day "capture → shareable link with routing": not offered by anyone.
5. **India:** two primary pages verified:
   - MapmyIndia builds indoor maps from floor plans plus on-site surveys;
   - BootWay runs QR-code, no-app hospital/campus/mall wayfinding.

   I verified **no** named Indian airport, mall or metro deployment.

   **Juspay** has no public spatial, 3D or AR work in its site sitemap (411 blog URLs) or in its 378 public GitHub repos. The only public signal is the Techfest brief's job offer.

## 2. Per-company records
Legend for the **Src** lines: every URL was opened on 2026-10-04 (→ shows a redirect).

### 2.1 Capture → twin platforms

**Matterport (a CoStar Group company)**
| Field | What the opened page says |
|---|---|
| Ownership | CoStar Group completed the acquisition of Matterport on **28 Feb 2025** — [matterport.com/news/costar-group-completes-acquisition…](https://matterport.com/news/costar-group-completes-acquisition-of-matterport-ushering-in-a-new-era-of-3d) |
| Capture | "Matterport for Mobile… capture any space in immersive 3D, from the phone in your pocket", on Android and iPhone. The same page has setup guides for Pro3, Pro2, Insta360 and Ricoh cameras — [matterport.com/3d-camera-app](https://matterport.com/3d-camera-app). The Free plan: "Create immersive 3D experiences with a phone, tablet or 360 camera" — [matterport.com/plans](https://matterport.com/plans) |
| Processing | Scans are uploaded "to the cloud for processing" — [3d-camera-app](https://matterport.com/3d-camera-app). Floor plans and technical files: Fast (24 h) and Express (6 h) on Professional — [plans](https://matterport.com/plans). Schematic floor plans "within 2 business days" — [digital-twin-features](https://matterport.com/digital-twin-features). Turnaround for the 3D model itself: not stated |
| Outputs | Schematic floor plans as PNG, PDF and SVG. The MatterPak bundle has a point cloud, OBJ, floor plan and reflected-ceiling-plan views for 3ds Max, ReCap, Revit and AutoCAD — [digital-twin-features](https://matterport.com/digital-twin-features). CAD, BIM, E57, Sketch and TruePlan files can be bought on Professional — [plans](https://matterport.com/plans) |
| Web viewer | Starter and above: "Share & embed anywhere" — [plans](https://matterport.com/plans). Viewer modes: "scan navigation, highlight reels, dollhouse and floor plan views, floor selection, and measurement mode" — [digital-twin-features](https://matterport.com/digital-twin-features). Movement is between scan positions; no free WASD found |
| POI / search | Tags "to draw your viewer's attention to important points of interest". Tags can carry keywords "to improve navigation", and guided tours exist — [digital-twin-features](https://matterport.com/digital-twin-features). Property Intelligence generates room dimensions and labels automatically — [features/property-intelligence](https://matterport.com/features/property-intelligence). A search UI over tags: — |
| Routing / AR | — / — |
| Pricing | Tiers are Free (1 active space), Starter (5–20), Professional (20–150), Business (100–300) and Enterprise (contact sales) — [matterport.com/plans](https://matterport.com/plans). The "Starting at" dollar figures render client-side and were **not captured**. matterport.com/pricing returned **404** even though the sitemap lists it |

**Polycam**
| Field | What the opened page says |
|---|---|
| Capture | Gaussian splats from "your own photos or videos": 20–200 PNG/JPG images or an MP4 video — [poly.cam/tools/gaussian-splatting](https://poly.cam/tools/gaussian-splatting). Room scans use LiDAR: "accurate to within a 0.5 inch tolerance… Furniture and appliances are automatically detected, as well as wall color, windows, and cabinetry" — [poly.cam/tools/3d-room-scanner](https://poly.cam/tools/3d-room-scanner) |
| Processing | Floor plans: "processes on-device in minutes. No cloud uploads" — [poly.cam/floor-plans](https://poly.cam/floor-plans). Room scans: "we'll process the capture in a few minutes" — [3d-room-scanner](https://poly.cam/tools/3d-room-scanner). Where splats are processed: not stated |
| Outputs | Floor plans as PDF, DXF, PNG and SVG — [floor-plans](https://poly.cam/floor-plans). Splat export formats: — |
| Web viewer | "Private link sharing" is in the Basic plan — [poly.cam/pricing](https://poly.cam/pricing) |
| POI / routing / AR | Furniture auto-detection in room scans (see Capture). Search, routing and AR: — |
| Pricing | Free. **Basic** $150/yr (≈$12.50/mo) or $30/mo billed monthly, with "Unlimited object captures and Gaussian splats". **Business** $400/yr per user, with 2D & 3D floor plans. **Enterprise** $1200/yr per user — [poly.cam/pricing](https://poly.cam/pricing) |

**Niantic Spatial: Scaniverse, SPZ, VPS (Localize), 8th Wall**
| Field | What the opened page says |
|---|---|
| Capture | scaniverse.com → [nianticspatial.com/products/capture](https://www.nianticspatial.com/products/capture): "Capture detailed 3D scans from iOS and Android devices today plus data from 360° cameras and drones". BYOD covers LiDAR and drone imagery. "Try Scaniverse on Web" |
| Processing | "Generate Gaussian Splats and meshes processed efficiently on-device" — [products/capture](https://www.nianticspatial.com/products/capture). The pricing page lists "On-device reconstruction (legacy version)" on Free, and monthly credits pay for processing: Free gives 20,000 credits, enough to "Process ~10 min of mobile capture". Where credit-based processing runs is not stated — [nianticspatial.com/pricing](https://www.nianticspatial.com/pricing) |
| Outputs | "including our open-source SPZ format, reducing file size by 90%" — [products/capture](https://www.nianticspatial.com/products/capture). Exports FBX, SPZ and PLY; USDZ and 360° splats on Plus — [pricing](https://www.nianticspatial.com/pricing). The SPZ repo `nianticlabs/spz` is MIT-licensed: "About 10x smaller than the PLY equivalent" (GitHub API, see [`sources_verified_2026-10-04.tsv`](sources_verified_2026-10-04.tsv)) |
| VPS / AR | "Vision-based localization that works outdoors, mapped indoor locations, and GPS-denied environments… Bring your own data to map private indoor and outdoor spaces" — [products/localize](https://www.nianticspatial.com/products/localize). Blog post dated 4/7/2026: the original VPS gives "6DoF localization with near centimeter-level precision. It works indoors…" but a space "had to be pre-scanned and mapped". VPS 2.0 integrates with Scaniverse and adds 3DoF without prior scanning — [blog/vps2](https://www.nianticspatial.com/blog/vps2) |
| 8th Wall status | 8thwall.com → [8thwall.org](https://8thwall.org/): "8th Wall is now open source". Per [blog/8th-wall-open-source](https://8thwall.org/blog/8th-wall-open-source) (2 Mar 2026):<br>• "As of February 28, 2026, that transition is complete": "the hosted 8th Wall platform — login, the cloud editor, and web-based Studio — is no longer available".<br>• A "Distributed Engine Binary… includes SLAM… binary-only license… VPS, Maps, and Hand Tracking are not included".<br>• An "MIT-licensed open source version of the engine framework that does not include SLAM".<br>Separately, Agog has given a grant for community stewardship — [blog/agog-supports-8th-wall](https://8thwall.org/blog/agog-supports-8th-wall) |
| Floor plan / POI / routing | — |
| Pricing | Free: 20k credits, ~1,500 VPS queries. **Plus** $20/mo or $200/yr: 40k credits. **Pro** $50/mo or $500/yr: 105k credits, commercial rights. Enterprise: custom, on-prem. "Classic Scaniverse" keeps free on-device processing — [nianticspatial.com/pricing](https://www.nianticspatial.com/pricing) |

**Luma AI**
| Field | What the opened page says |
|---|---|
| Company focus | Homepage title "Luma \| AI Agents for Creative Work". Meta description: "creative AI platform for video generation and image creation… Ray and Uni". No 3D-capture text was found on the homepage — [lumalabs.ai](https://lumalabs.ai/) |
| Capture app | The **Luma 3D Capture** app is still listed on the App Store ("Only for iPhone"): "No Lidar or fancy capture equipment necessary, all you need to create is an iPhone 11 or newer". It also says "share anywhere on the web" and "embed them on your website". Last-update date: not captured — [apps.apple.com/…/id1615849914](https://apps.apple.com/us/app/luma-3d-capture/id1615849914) |
| Viewer | captures.lumalabs.ai → [lumalabs.ai/featured](https://lumalabs.ai/featured), titled "Featured Captures", still shows "Interactive Scenes" |
| Formats / processing / POI / routing / AR / pricing | — (the 3D product is not mentioned on [lumalabs.ai/pricing](https://lumalabs.ai/pricing)) |

**World Labs: Marble and Spark**
| Field | What the opened page says |
|---|---|
| What it is | Marble is "powered by our multimodal world models that can reconstruct, generate, and simulate 3D worlds… from a single text prompt, single or multiple image, video, and coarse 3D structures". Panorama input gives "the most accurate spatial representation" — [docs.worldlabs.ai](https://docs.worldlabs.ai/). The output is a generated world, not a metric survey of the space |
| Plans | Four tiers — [account-billing](https://docs.worldlabs.ai/marble/support/account-billing):<br>• **Free**: text, single image or 360 panorama; up to 4 world generations.<br>• **Standard**: "Generation from multiple images, videos, or 3D layouts"; exporting; up to 12.<br>• **Pro**: high-quality textured-mesh export, commercial rights; up to 25.<br>• **Max**: "high-volume production".<br>Dollar prices are not on that page |
| Outputs | SPZ (~2M splats), low-res SPZ (~500k), PLY (~2M), low-res PLY (~500k), and a "Collider Mesh (GLB)… coarse mesh optimized for simple physics" — [marble/export/specs](https://docs.worldlabs.ai/marble/export/specs) |
| Web renderer | Spark: "An advanced 3D Gaussian Splatting renderer for THREE.js… wide format support (ply, sogs, spz, splat, ksplat)" — [sparkjs.dev](https://sparkjs.dev/). MIT licence per the GitHub API (`sparkjsdev/spark`, [`sources_verified_2026-10-04.tsv`](sources_verified_2026-10-04.tsv)) |
| POI / routing / AR | — (the collider mesh supports physics, not pathfinding) |

**Meta: Horizon Hyperscape Capture (beta)**
| Field | What the opened page says (all from [meta.com/help/quest/1088536553019177](https://www.meta.com/help/quest/1088536553019177/) → en-gb) |
|---|---|
| Capture | **Meta Quest 3 and 3S only**, users 18+. Three guided steps:<br>1. walk the room edge from one corner to the next, stopping to look around;<br>2. capture details up close;<br>3. look up to capture the ceiling.<br>Rooms should be at least ~3×3 m, well lit and static |
| Processing | Captures upload to Meta's servers, and processing "can take up to 8 hours, depending on the size of your spaces" |
| Viewer / sharing | Rendering happens on-device in the Hyperscape Capture app. **"As of 12 May 2026, these features [sharing, inviting] are no longer available… only accessible as 'view only'"** on Quest 3/3S |
| Outputs / POI / routing / AR / pricing | — (no export described) |

**Varjo Teleport**
| Field | What the opened page says |
|---|---|
| Ships | teleport.varjo.com → [get.teleport.varjo.com](https://get.teleport.varjo.com/), "Cloud platform for real world 3D reconstructions":<br>• "Process thousands of captures from rooms to neighborhoods automatically in the cloud, with a developer API";<br>• "Export the models, or embed our renderer into your product";<br>• "3D Gaussian splatting reconstructs your space in the cloud, from 1M to 100M splats" |
| Capture device / pricing / POI / routing / AR | — (the capture device is **UNVERIFIED** on the page I opened) |

**KIRI Engine**
| Field | What the opened page says ([kiriengine.app](https://www.kiriengine.app/)) |
|---|---|
| Ships | "3D Scanner App for iPhone, Android, and Web". Modes: Photogrammetry, Featureless Object Scan, 3D Gaussian Splatting, 3DGS To Mesh, and LiDAR. LiDAR mode on iOS can "3D scan models, create floor plans, and generate quick scene visualizations". 3DGS can be exported "as physical meshes". Free to download |
| Processing / pricing / POI / routing / AR | — |

**Epic Games: RealityScan**
| Field | What the opened page says |
|---|---|
| Ships | "RealityScan Mobile 1.9 is now available", described as a "free mobile application" to "capture, process, and share high-fidelity scans… from your mobile device". Desktop RealityScan builds models "from images and laser scans". The RealityCapture legacy licensing server "will close down on August 3" — [realityscan.com](https://www.realityscan.com/) |
| Pricing | "Free for students, educators, and companies earning under $1 million USD in annual gross revenue". Above that, paid seats — [realityscan.com/license](https://www.realityscan.com/license) |
| Splats / POI / routing / AR | — |

**Jawset Postshot**
| Field | What the opened page says ([jawset.com](https://www.jawset.com/)) |
|---|---|
| Ships | Desktop radiance-field / 3D scene training: "3D scenes and objects with any camera in minutes… from regular RGB images". Unlimited image count; image masking. Integrates with Unreal Engine and After Effects. "Download for free" |
| Processing | "Postshot runs all processing and machine learning steps on devices only you have access to". Requires Windows 10 or later and an NVIDIA GPU with compute capability 7.5+ (e.g. RTX 2060) |
| Pricing tiers / web viewer / POI / routing / AR | — |

**Zillow 3D Home**
| Field | What the opened page says ([zillow.com/z/3d-home](https://www.zillow.com/z/3d-home/) → /3d-home/) |
|---|---|
| Ships | Free Zillow 3D Home app for iOS and Android. "Use a supported iPhone®, Android smartphone or 360-degree camera to capture panoramas, and then let the app do the rest". Produces 3D Home tours and **Interactive Floor Plans** on Zillow listings; Ricoh Theta is supported |
| Splats / POI / routing / AR | — (panorama tours) |

**NavVis**
| Field | What the opened page says |
|---|---|
| Ships | Laser-scanning hardware — MLX, VLX 3 and "VLX 4 NEW" — plus the IVION platform — [navvis.com](https://www.navvis.com/). IVION "pairs millimeter-accurate scan data with an intuitive browser-based platform". Users can explore as-is conditions, overlay design models and collaborate remotely; it handles point clouds and panoramas — [navvis.com/ivion](https://www.navvis.com/ivion) |
| Phone capture / splats / POI / routing / AR | — (these are dedicated scanners, not phone capture) |

### 2.2 Platform SDKs (Apple, Google)

**Apple: RoomPlan, Object Capture, ARKit**
| Field | What the opened page says |
|---|---|
| RoomPlan | "Utilizes the camera and LiDAR Scanner on iPhone and iPad to create a 3D floor plan of a room, including… dimensions and types of furniture". Outputs USD/USDZ with "dimensions of each component recognized… as well as the type of furniture detected". Includes a coaching UI — [developer.apple.com/augmented-reality/roomplan](https://developer.apple.com/augmented-reality/roomplan/). `StructureBuilder` (iOS 17) "combines multiple scan sessions into a single captured result" — [docs JSON](https://developer.apple.com/tutorials/data/documentation/roomplan/structurebuilder.json) |
| Object Capture | "Create 3D objects from a series of photographs using photogrammetry" — [augmented-reality/object-capture](https://developer.apple.com/augmented-reality/object-capture/) → RealityKit docs |
| ARKit, relevant to AR navigation | `ARGeoTrackingConfiguration` (iOS 14): **"Geotracking occurs exclusively outdoors"** — [docs JSON](https://developer.apple.com/tutorials/data/documentation/arkit/argeotrackingconfiguration.json). `ARWorldMap` (iOS 12) can be saved and restored so content returns to "the same positions" — [docs JSON](https://developer.apple.com/tutorials/data/documentation/arkit/arworldmap.json) |
| Web | — (native SDKs) |

**Google: Indoor Live View (Maps), ARCore Geospatial**
| Field | What the opened page says |
|---|---|
| Indoor Live View | Blog post of 30 Mar 2021: "Indoor Live View is live now on Android and iOS in a number of malls in Chicago, Long Island, Los Angeles, Newark, San Francisco, San Jose, and Seattle". It was then rolling out to "select airports, malls, and transit stations in Tokyo and Zurich". Arrows and directions lead to gates, elevators, check-in, restrooms and ATMs. It runs on "global localization" built from Street View imagery — [blog.google/…/redefining-what-map-can-be…](https://blog.google/products-and-platforms/products/maps/redefining-what-map-can-be-new-information-and-ai/). Later expansion (venue counts, Tokyo 2025): **UNVERIFIED** — kotsu.metro.tokyo.jp returned a 212-byte stub, and support.google.com/maps/answer/11618113 returned 404 |
| ARCore Geospatial | "Remotely attach content to any area covered by Google Street View". Its VPS uses "a global 3D point cloud derived from Google Street View images" — [developers.google.com/ar/develop/geospatial](https://developers.google.com/ar/develop/geospatial) |
| User capture → twin | — (no user-capture product; Google maps the venues itself) |

### 2.3 Indoor positioning / wayfinding / VPS

| Company | What the opened page says | Src (opened 2026-10-04) |
|---|---|---|
| **Pointr** | "AI Mapping, Wayfinding, & Positioning". "Map generation through AI-powered MapScale®". "Building digitization through AI with MapScale® and Building X". "Powering product wayfinding at The Home Depot". Runs on "Mobile (Native and Hybrid), Web and Kiosk", with SDKs for iOS, Android and Web. AR, capture input, pricing: — | [pointr.tech](https://www.pointr.tech/) |
| **Mapsted** | Positioning with "No Beacons, No Wi-Fi… without any beacons, Wi-Fi or on-site hardware", covering "4+ billion sq ft". Products include Interactive Map, Intelligent Search, Indoor Navigation, Wayfinding, Accessibility and Outdoor-Indoor Navigation. AR, pricing: — | [mapsted.com](https://mapsted.com/) |
| **IndoorAtlas** | Positioning SDK using "patented multi-layer sensor fusion". Wayfinding for "airports, hospitals, shopping malls, and offices", with offline support and "optional augmented reality extensions" (IndoorAtlas AR). SDK 3.8.1 | [indooratlas.com/solutions/indooratlas-wayfinding](https://www.indooratlas.com/solutions/indooratlas-wayfinding/) |
| **Immersal** (Part of Hexagon) | SDK for wayfinding "in complex indoor and outdoor environments", with WebAR. Case study: "an indoor navigation web-based application for the Mall of Tripla… more than 85,000 m2 in Helsinki" using VPS. Also a city-scale toolkit. "© 2026 Immersal - Part of Hexagon" | [immersal.com](https://immersal.com/) |
| **MultiSet AI** | "Independent VPS infrastructure… Scan-agnostic": inputs are "LiDAR, E57, Gaussian Splats, 360 videos, textured meshes, iPhone scans, drone captures". "≤5 cm accuracy… instant 6-DoF relocalization". Cloud, on-prem or "on-device/offline". "SDKs for Unity, iOS, Android, WebXR, Quest" | [multiset.ai](https://www.multiset.ai/) |
| **Mappedin** | "Create indoor maps using AI-powered tools and share them anywhere". "Transform floor plans to full-featured maps… Map venues in minutes, not weeks or months". Indoor wayfinding software | [mappedin.com](https://www.mappedin.com/) |
| **ARway** | "Indoor Mapping, Navigation & AR Experiences": "Static & branded 2D Maps of venues", wayfinding, Apple Vision Pro. Capture method: — | [arway.ai](https://www.arway.ai/) |
| **Treedis** | "Treedis Connected Worker": digital twins, IoT, AR and industrial AI. Its menu lists "Matterport", "AR on-site" and "2D Web App". Routing: — | [treedis.com](https://www.treedis.com/) |

### 2.4 India deployments and Juspay
| Item | Finding | Src (opened 2026-10-04) |
|---|---|---|
| **MapmyIndia** indoor mapping | "Interactive, searchable, and even navigable!", for "Malls, airports, stadiums, offices". Maps are built "by using floor plans, onsite surveys with sophisticated equipments". The page claims "hundreds of these location referenced positions along with defined routes" across airports, malls, museums and offices. **It names no Indian venue** | [mapmyindia.com/indoor-mapping](https://www.mapmyindia.com/indoor-mapping/) |
| **BootWay** | "India's First iNaaS Provider" (indoor navigation as a service). "Visitors scan a QR code and follow a clear path… No app, no beacons, no signage rework". Users can "search by department, doctor, or room number, and set the starting point from a nearby landmark". Targets hospitals, campuses, malls and workplaces | [bootway.in](https://www.bootway.in/) |
| Named Indian airport / mall / metro deployments | **None verified.** The search lead (Delhi, Bengaluru, Mumbai and Hyderabad airports; Phoenix Marketcity; metro stations) gave no primary sources. Varlecon and GlobalLogic, also named in the lead, were **not opened: UNVERIFIED** | — |
| **Juspay**: spatial / 3D | **Nothing public found.** [juspay.io/sitemap-0.xml](https://juspay.io/sitemap-0.xml) (411 blog URLs) has no URL matching 3d, spatial, augment, indoor, vision, camera, metaverse, navigation, techfest or namma. The only hits are "3DS" (3-D Secure payments) posts and an `/ar/` (Arabic) locale page. The GitHub API listing of `orgs/juspay/repos` (378 public repos) has no 3D, AR, indoor-navigation or splat repos. The only public signal is the brief: teams that finish the full pipeline including AR "will earn the opportunity to be considered for a full time job opportunity at Juspay" ([`_briefs/namma-space.txt`](../../_briefs/namma-space.txt)). A Juspay ↔ Namma Yatri link is **UNVERIFIED** today: the `nammayatri/nammayatri` repo description ("A Direct-to-Driver open mobility platform…") does not mention Juspay | as listed |

## 3. Capability × company matrix
✅ = verified on the page I opened · ◐ = partial or conditional (see §2) · ❌ = the page says no, or the product structurally can't · — = not found on the pages I opened. The last row is **our target design, not a verified claim**.

| Company / product | Phone capture | Photoreal (splat/radiance) | Floor plan | POI / search | Routing | AR | Zero-install web viewer |
|---|---|---|---|---|---|---|---|
| Matterport | ✅ phone/tablet/360 | — | ✅ schematic, paid add-on | ◐ tags + keywords, auto room labels | — | — | ✅ share & embed |
| Polycam | ✅ photos/video; LiDAR rooms | ✅ splats | ✅ on-device AI | ◐ auto-detected furniture | — | — | ◐ private link sharing |
| Niantic Spatial (Scaniverse + VPS) | ✅ iOS/Android/360/drone | ✅ on-device; SPZ | — | — | — | ✅ VPS 6DoF in pre-scanned indoor spaces (SDK) | ◐ Scaniverse on Web; hosted 8th Wall ended |
| Luma 3D Capture | ✅ iPhone 11+ | ✅ (format not stated) | — | — | — | — | ✅ share/embed |
| World Labs Marble + Spark | ◐ images/video → *generated* world | ✅ SPZ/PLY | — | — | ◐ collider mesh only | — | ✅ Spark (MIT) |
| Meta Hyperscape | ❌ Quest 3/3S only | ✅ (format undisclosed) | — | — | — | — | ❌ view-only in Quest app |
| Varjo Teleport | — | ✅ cloud, 1M–100M splats | — | — | — | — | ◐ embeddable renderer / API |
| KIRI Engine | ✅ iPhone/Android/web | ✅ 3DGS (+ mesh) | ✅ LiDAR iOS | — | — | — | — |
| Epic RealityScan | ✅ Mobile 1.9 | — | — | — | — | — | — |
| Jawset Postshot | ◐ any camera; desktop processing | ✅ radiance field | — | — | — | — | — |
| Zillow 3D Home | ✅ iPhone/Android/360 | — (panoramas) | ✅ interactive | — | — | — | ✅ on listings |
| NavVis (MLX/VLX + IVION) | ❌ laser scanners | — | — | — | — | — | ✅ IVION in browser |
| Apple (RoomPlan / Object Capture / ARKit) | ✅ LiDAR iPhone/iPad | — | ✅ parametric USDZ, multi-room | ◐ furniture types | — | ✅ ARKit; ARWorldMap; geotracking outdoors only | ❌ native SDK |
| Google (Indoor Live View / Geospatial) | ❌ Google-mapped venues | — | — | ✅ gates, stores, restrooms | ✅ | ✅ select venues | ❌ Maps app |
| Pointr | — | — | ✅ AI MapScale | ✅ product wayfinding | ✅ | — | ✅ Web SDK / kiosk |
| Mapsted | — | — | ✅ interactive map | ✅ intelligent search | ✅ | — | — |
| IndoorAtlas | — | — | — | — | ✅ | ✅ AR extension | — |
| Immersal (Hexagon) | — | — | — | — | ✅ | ✅ VPS | ✅ WebAR (Mall of Tripla) |
| MultiSet AI | ◐ ingests iPhone scans / 360 video | ◐ ingests splats | — | — | — | ✅ VPS ≤5 cm | ◐ WebXR SDK |
| Mappedin | — | — | ✅ AI floor plan → map | — | ✅ | — | ◐ "share them anywhere" |
| ARway | — | — | ✅ 2D maps | — | ✅ | ✅ | — |
| Treedis | ◐ via Matterport | — | — | — | — | ✅ AR on-site | ✅ 2D web app |
| MapmyIndia indoor | ❌ floor plans + surveys | — | ✅ | ✅ "searchable" | ✅ "navigable" | — | — |
| BootWay (India) | — | — | — | ✅ dept / doctor / room | ✅ step-by-step | — | ✅ QR, no app |
| **Namma Space (target)** | ✅ phone video + SOP | ✅ 3DGS | ✅ derived NavGrid | ✅ click + search | ✅ obstacle-aware A* | ◐ bonus (WebXR + relocalisation) | ✅ one link, WASD |

## 4. Gaps none of them close
1. **Routing over the captured geometry.** Every routing product I opened (Pointr, Mapsted, Mappedin, MapmyIndia, BootWay, IndoorAtlas, Immersal, Google) routes over operator-made maps: floor plans, CAD, surveys or Google's own venue mapping. No capture product (Matterport, Polycam, Scaniverse, KIRI, Luma, Teleport, Hyperscape, Zillow) shows a path planned around *captured* obstacles such as a sofa or a display stand.
2. **Free first-person walking in a photoreal twin from a web link.** The pages I opened show:
   - Matterport: scan-position navigation and dollhouse views, not free WASD;
   - Hyperscape: Quest-only and view-only;
   - Marble: worlds are generated, not faithful;
   - Splat apps: share links, with no navigation layer.
3. **Item-level, searchable POIs taken from the capture itself** (e.g. "3-seater sofas"). Closest matches:
   - RoomPlan detects furniture types, but only natively, per room, with LiDAR;
   - Polycam detects furniture in LiDAR room scans;
   - Matterport auto-labels rooms and adds tag keywords.

   None of them puts open-vocabulary item search into a web twin.
4. **Phone AR localised against the same capture that built the twin, without an app install.**
   - VPS products need pre-scanning and SDK/app integration (Niantic, Immersal, MultiSet), though MultiSet lists a WebXR SDK and Immersal shipped a WebAR mall case study.
   - Hosted 8th Wall is gone, and the MIT engine has no SLAM.
   - ARKit geotracking is outdoors-only.
   - Google's Indoor Live View covers only venues that Google has mapped.
5. **Capture → live link the same day.** Stated turnarounds:
   - Hyperscape: up to 8 h;
   - Matterport floor plans: 2 business days (6 h Express);
   - Polycam floor plans and Scaniverse splats: on-device.

   Nobody I opened states a single-session "capture → hosted twin with search and routing" time. This is the Round-3 Day-1 test.
6. **Openness and hardware.** NavVis and Matterport Pro3 need dedicated scanners; Hyperscape needs a headset; most twins are closed SaaS. The open pieces I verified are SPZ (MIT), Spark (MIT) and the 8th Wall engine (MIT, without SLAM).

## 5. Where Namma Space can borrow from or beat them
**Borrow (credit in the abstract):**
- **Delivery format and renderer.** Use SPZ (MIT; Niantic quotes ~90% / ~10× smaller than PLY) with Spark (MIT; reads ply, sogs, spz, splat and ksplat). Marble's two-tier export (~2M and ~500k splats) is a good model for a low-res first load.
- **Capture SOP wording.** Meta's three steps (walk the edge corner to corner while looking inward → close-up detail → ceiling; static scene, good light, ≥3×3 m) and Polycam's capture rules (20–200 images; avoid motion blur and shallow depth of field, which generate "floaters"). Add both to `deliverables/capture-sop.md` as cross-checks.
- **Viewer UX conventions.** From Matterport: dollhouse and floor-plan views, floor selection, measurement mode, tags with keywords, guided tours. From Google Indoor Live View: arrows plus written directions, and floor changes ("what floor a store is on").
- **LiDAR iPhones as a semantic prior.** RoomPlan furniture types, with StructureBuilder for multi-room capture. ARWorldMap save/restore is the iOS relocalisation path for the AR bonus.
- **A cheap AR start pose.** BootWay sets the starting point from a QR code or nearby landmark. A printed marker at the entrance (we already ship an ArUco marker in the SOP) gives an initial pose without a VPS.
- **Proof that web-based VPS indoor navigation works.** Immersal's Mall of Tripla WebAR app (85,000 m²). MultiSet accepts Gaussian splats and iPhone scans as map sources, which suggests localising against our own capture.

**Beat:**
- **One link that does it all:** WASD walk, POI click and search, and an obstacle-aware floor path in the photoreal twin. No verified product combines these (§3).
- **Routing around furniture**, computed from our own capture rather than a floor plan (the wayfinding camp's input). This needs the honest R2 path-safety numbers from `eval/nav_eval_v3.py`.
- **Phone-only, zero-install, open source.** No Pro3, NavVis scanner or Quest headset; no paid seat (Polycam Business, Niantic Plus/Pro, Matterport plans).
- **Turnaround with on-site QA**, as in spike D′, against the stated vendor turnarounds: Hyperscape ≤8 h, Matterport floor plans 2 business days or 6 h Express.
- **Item-level search from capture-time voice tags and VLM labels**, versus room labels (Matterport) or native-only furniture categories (RoomPlan).

## 6. What I could not verify (follow-ups)
- Luma Flythroughs sunset date; the Luma 3D Capture app's last-update date.
- Matterport and World Labs dollar prices (rendered client-side or absent); Polycam's splat export formats; KIRI and Postshot pricing.
- Google Indoor Live View's current venue count and coverage (the 2021 post is the latest primary source I opened).
- Varjo Teleport's capture device(s).
- Named Indian airport, mall and metro indoor-navigation deployments; Varlecon and GlobalLogic pages.
- The Juspay ↔ Namma Yatri relationship.
