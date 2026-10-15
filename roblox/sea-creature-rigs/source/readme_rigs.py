"""Write <out>/README.md from rigs.json.   python3 readme_rigs.py <out_dir>"""
import json
import os
import sys

out = sys.argv[1]
meta = json.load(open(os.path.join(out, "rigs.json")))
ORDER = ["TinyFish", "Pufferfish", "Crab", "Jellyfish", "Octopus", "MorayEel", "Shark", "HammerheadShark", "Orca",
         "GiantSquid", "Clownfish"]

md = ["# Fish a Human: sea creature character rigs", "",
      "Eleven playable sea creature characters on the default blocky R15 rig, built in Blender.",
      "Each one is 5.2 studs tall like the default character and keeps the regular Roblox head, so the player's face shows.",
      "The fish, sharks, eel and orca wear their creature's head as a hood: the player's face looks out through its mouth.",
      "The crab, jellyfish, octopus and squid keep the bare head with eye stalks, a bell or a mantle on it.",
      "Each body is shaped like its animal (round pufferfish, V-shaped shark, soft octopus, armoured crab) while staying a normal R15 humanoid.", "",
      "![Front](previews/Lineup_Front.jpg)", "",
      "![Back](previews/Lineup_Back.jpg)", "",
      "## What's here", "",
      "| Path | What it is |", "|---|---|",
      "| `fbx/<Creature>.fbx` | The rig to import: 15 R15 body parts, the creature pieces and joint markers. The texture is embedded. |",
      "| `textures/<Creature>.png` | The creature's 1024×1024 texture; every part of a creature shares it |",
      "| `roblox/SeaCreatureRigSetup.lua` | ModuleScript: turns an imported FBX into a working R15 character, and morphs players |",
      "| `blend/<Creature>.blend` | Editable Blender scenes (saved from Blender 5.2) |",
      "| `previews/` | `Lineup_Front.jpg`, `Lineup_Back.jpg` and one `<Creature>.jpg` each |",
      "| `source/` | The Python that builds everything. Edit it and re-run to change a creature |",
      "| `rigs.json` | Parts, triangles and size of each rig |", "",
      "## Getting a rig into Roblox Studio", "",
      "1. Put `SeaCreatureRigSetup.lua` in **ServerStorage** as a ModuleScript named `SeaCreatureRigSetup`.",
      "2. **Home → Import 3D** and pick `fbx/Shark.fbx` (or any creature). Import it into Workspace.",
      "3. In the command bar run:",
      "   ```lua",
      "   require(game.ServerStorage.SeaCreatureRigSetup).Run(workspace.Shark)",
      "   ```",
      "   The finished character goes to `ReplicatedStorage.SeaCreatureRigs.Shark`. The script:",
      "   - scales it to 5.2 studs, so the importer's unit setting doesn't matter",
      "   - adds the HumanoidRootPart, a Humanoid (R15) and the standard R15 joints (Root, Waist, Neck, LeftShoulder …), so the default animations play",
      "   - adds the usual accessory attachments (hat, hair, face, shoulders, waist), so hats and tools still fit",
      "   - welds every creature piece to its body part (no collision, massless). Glowing pieces become Neon and the jelly bell becomes glass",
      "   - puts the classic face on the head (`Run(model, { Face = \"rbxassetid://…\" })` for another)",
      "4. If a rig imports without its texture, upload `textures/<Creature>.png` and pass it in: `Run(workspace.Shark, { TextureId = \"rbxassetid://…\" })`.",
      "",
      "## Turning a player into a creature", "",
      "From a server script:",
      "```lua",
      "local Rigs = require(game.ServerStorage.SeaCreatureRigSetup)",
      "Rigs.Morph(player, \"Shark\")   -- keeps the player's face, position and default animations",
      "```",
      "To make a creature the default character instead, copy its rig into **StarterPlayer** and name it `StarterCharacter`.", "",
      "## Conventions", "",
      "- Body parts are named exactly as in R15 (`Head`, `UpperTorso`, `LeftUpperArm` …) and keep the blocky R15 sizes.",
      "- Creature pieces are named `<BodyPart>__<Piece>`, for example `Head__Fin` or `LowerTorso__Tail`. The setup script welds each one to the body part before the `__`.",
      "- `Head__Hood` is the hood on the fish and sharks. It is welded to the head and has an opening for the face.",
      "- Pieces stay clear of the face on the front of the head.",
      "- `Joint_<Name>` cubes mark the R15 joints; the setup script turns them into rig attachments and deletes them.",
      "- Every part is under Roblox's 20,000-triangle limit.", "",
      "## The rigs", "",
      "| # | Creature | Parts | Triangles | Largest part (tris) | Size W × H × D (studs) |",
      "|---:|---|---:|---:|---:|---|"]
for i, n in enumerate(ORDER, 1):
    if n not in meta:
        continue
    m = meta[n]
    w, h, d = m["full_size"]
    md.append(f"| {i} | {m['display']} | {len(m['parts'])} | {m['tris']:,} | {m['max_part_tris']:,} | {w:g} × {h:g} × {d:g} |")
md += ["", "Height is the whole model including fins, bells and mantles. The body itself is 5.2 studs tall on every rig.", ""]
for i, n in enumerate(ORDER, 1):
    if n in meta:
        md += [f"### {i} · {meta[n]['display']}", "", f"![{meta[n]['display']}](previews/{n}.jpg)", ""]
md += ["## Changing or rebuilding a rig", "",
       "`source/char.py` holds the R15 body, fins, materials and texture bake; `source/creatures.py` has one function per creature.",
       "`kit.py` is the shared shape library from the area kit.", "",
       "```bash",
       "python3 -m venv bvenv && ./bvenv/bin/pip install bpy==5.2.2 pillow numpy",
       "./bvenv/bin/python source/build.py . draft only=Shark --no-export   # quick look at one creature",
       "./bvenv/bin/python source/build.py . final                         # rebuild every FBX, texture, .blend and render",
       "./bvenv/bin/python source/lineup.py . && python3 source/readme_rigs.py .",
       "```", ""]
open(os.path.join(out, "README.md"), "w").write("\n".join(md))
print("README written")
