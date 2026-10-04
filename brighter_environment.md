# Fish A Human: making the world brighter

**Status (2026-10-05):** 2–6 are applied in Studio (the Lighting service and `WorldBuilder.ApplyLighting`). #1, exposure +0.15, was tried and then reverted at the user's request, so exposure is back to −0.3. The old values are in `ServerStorage.LightingBackup_BeforeSunny`.

Right now the lighting runs a bit dark and blue:
- Exposure is −0.3 and Brightness is 1.6.
- Ambient light is dark blue.
- Color correction tints everything blue.
- The atmosphere adds blue haze.

## What I can change (all reversible: current values get backed up)

| # | Change | Now → Suggested | Effect |
|---|--------|-----------------|--------|
| 1 | Exposure | −0.3 → **+0.15** | Lightens the whole scene. This is the biggest single difference. |
| 2 | Sun brightness and time of day | 1.6 → **2.2**, 14:00 → **12:30** | Stronger, higher sun with shorter shadows |
| 3 | Ambient / outdoor ambient | dark blue → **soft light blue-white** | Lifts the dark spots under the stands and the dome |
| 4 | Shadow softness | 0.2 → **0.5** | Softer, friendlier shadows |
| 5 | Color correction | blue tint → **warm white**, saturation 0.2 → **0.3**, +0.05 brightness | Cheerful, punchy cartoon colors |
| 6 | Atmosphere | density 0.06 → **0.03**, haze 0.2 → **0**, lighter color | Less murky, clearer view across the lobby |
| 7 | Bloom | 0.35 → **0.5**, threshold 1.8 → **1.3** | Glass, neon and gold glow a little |
| 8 | Sun rays | 0.01 → **0.08** | Visible light beams through the dome |
| 9 | Water and dome glass | dark teal → **light turquoise** | The sea reads as tropical, not deep |
| 10 | Lobby colors | → **pastel, more white trim** | Paths and floors pop |
| 11 | A few soft lights at the stands | new | Warm glow at Bait, Nets, Eater and Zoo |
| 12 | Skybox | → **bright cartoon sky** | Happier backdrop (I'd find options for you) |

## My pick
Apply **1–6** together as one "sunny" preset. That's the biggest change for the least risk. Then I'd send before/after screenshots, and we can tune 7–12 from there.

Want me to apply it?
