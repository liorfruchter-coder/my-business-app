"""Write <out>/README.md from assets.json.   python3 readme.py <out_dir>"""
import json
import os
import sys

out = sys.argv[1]
assets = json.load(open(os.path.join(out, "assets.json")))
NICE = {"Beach": "1 · Beach", "TropicalIsland": "2 · Tropical Island", "Volcano": "3 · Volcano", "ThemePark": "4 · Theme Park",
        "RichCity": "5 · Rich City", "CruiseShip": "6 · Cruise Ship Harbor", "SnowyPeaks": "7 · Snowy Peaks",
        "PyramidDesert": "8 · Pyramid Desert", "MoonBase": "9 · Moon Base", "Shared": "Shared border pieces"}
total = sum(len(v) for v in assets.values())

md = [f"# Fish a Human: area building kit", "",
      f"{total} low-poly building and prop models for the nine areas of the shared map, built in Blender.",
      "They add to the existing ZoneKit props (palms, umbrellas, Ferris wheel and the rest) without duplicating any of them.", "",
      "![All areas](previews/AllAreas.jpg)", "",
      "## What's here", "",
      "| Path | What it is |", "|---|---|",
      "| `fbx/<Area>.fbx` | Every asset of an area in one file. Import this one. |",
      "| `fbx/<Area>/<Asset>.fbx` | The same assets, one file each |",
      "| `blend/<Area>.blend` | Editable Blender scenes, opened in Blender 4.2 or later |",
      "| `roblox/AreaKitSetup.lua` | ModuleScript: paints, scales, pivots and files imported models |",
      "| `roblox/AreaKitStyles.lua` | ModuleScript: colour and material for every part style |",
      "| `previews/` | `<Area>.jpg` close-ups, `<Area>_lineup.jpg` everything together |",
      "| `source/` | The Python that builds everything. Edit it and re-run to change a model |",
      "| `assets.json` | Size, triangles and parts for each asset |", "",
      "## Getting them into Roblox Studio", "",
      "1. Put `AreaKitStyles.lua` and `AreaKitSetup.lua` in **ServerStorage** as two ModuleScripts. Name them `AreaKitStyles` and `AreaKitSetup`.",
      "2. **Home → Import 3D** and pick `fbx/Beach.fbx` (or any area). Keep the hierarchy and import into Workspace.",
      "3. In the command bar run:",
      "   ```lua",
      "   require(game.ServerStorage.AreaKitSetup).Run(workspace.Beach)",
      "   ```",
      "   Each asset becomes a Model in `ReplicatedStorage.AreaKit.<Area>`. The script also:",
      "   - paints every part from AreaKitStyles",
      "   - anchors the parts",
      "   - sets the model to its real size in studs, so the importer's unit setting doesn't matter",
      "   - puts the pivot at the bottom centre with the front facing −Z",
      "   - adds a PointLight to each glowing part",
      "4. Place copies with `model:Clone()` and `:PivotTo(CFrame)`, the same way WorldThemeController places ZoneKit props.",
      "",
      "### Conventions",
      "- 1 stud = 1 Blender unit, and the ground is y = 0. A person is about 6 studs tall, and doors are 7–9 studs.",
      "- MeshParts are named `<Asset>_<Style>` (for example `BeachHouse_WoodLight`). The style name picks the colour and material.",
      "- Each style is one MeshPart, so most assets come to 5–20 parts. Every part stays under 9,000 triangles, well within Roblox's 20k limit.",
      "- `Accent` and `Party` parts are meant to be recoloured per copy: `AreaKitSetup.Tint(model, Color3.fromRGB(...))`, or `Run(root, { Accent = ... })`.",
      "  Examples: the beach-house siding, surf-shack awnings and the border pylons' glow strips.",
      "- Glowing parts (lava, fire, windows, neon) use the Neon material.",
      "- **Shared**: `BorderPylon` and `PricePlaque` are for the shadow walls between areas. `PricePlaque` has a black `PricePlaque_Black` face; put a SurfaceGui with the price on it.",
      "",
      "## The assets", ""]

for area, items in assets.items():
    md.append(f"### {NICE.get(area, area)}")
    md.append("")
    md.append(f"![{area}](previews/{area}.jpg)")
    md.append("")
    md.append("| Asset | W × H × D (studs) | Triangles | Parts |")
    md.append("|---|---|---:|---:|")
    for it in items:
        s = it["size_studs"]
        md.append(f"| {it['name']} | {s['x']:g} × {s['y']:g} × {s['z']:g} | {it['tris']:,} | {it['parts']} |")
    md.append("")

md += ["## Changing or rebuilding a model", "",
       "Everything is generated from `source/`: `kit.py` (shapes and styles) and `area_*.py` (one file per area, one function per asset).",
       "", "```bash",
       "python3 -m venv bvenv && ./bvenv/bin/pip install bpy==5.2.2 pillow",
       "./bvenv/bin/python source/run.py area_beach draft solo only=SurfShack   # quick look at one asset",
       "./bvenv/bin/python source/export.py .                                   # rebuild every FBX, .blend and render",
       "python3 source/sheet.py . && python3 source/roblox_lua.py . && python3 source/readme.py .",
       "```", ""]
open(os.path.join(out, "README.md"), "w").write("\n".join(md))
print("README written")
