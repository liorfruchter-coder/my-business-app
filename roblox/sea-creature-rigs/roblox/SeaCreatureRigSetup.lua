--[[
	SeaCreatureRigSetup
	Turns an imported sea creature FBX (fbx/<Creature>.fbx) into a working R15 character.

	1. Put this ModuleScript in ServerStorage.
	2. Home > Import 3D > pick e.g. fbx/Crab.fbx and import it into Workspace.
	3. Command bar:
	       require(game.ServerStorage.SeaCreatureRigSetup).Run(workspace.Crab)

	What it does to the imported model:
	  * scales it so the body is the default 5.2 studs tall (fixes any unit mix-up)
	  * adds a HumanoidRootPart, the R15 rig attachments (at the Joint_* markers,
	    which it then deletes) and the standard accessory / tool attachments
	  * adds a Humanoid (R15) and builds the Motor6Ds with their standard names
	    (Root, Waist, Neck, LeftShoulder ...), so default R15 animations play
	  * welds every creature piece ("<BodyPart>__<Piece>", e.g. Head__Crest) to
	    its body part: no collision, massless. "...Glow" pieces become Neon and
	    "...Glass" pieces see-through
	  * gives the Head a "face" Decal (the classic smile, or opts.Face)
	  * moves it to ReplicatedStorage.SeaCreatureRigs.<Name>

	Options: Run(model, { Name = "Crab", Face = "rbxassetid://...", TextureId = "rbxassetid://...",
	                      Destination = Instance, Keep = false })
	TextureId is only needed if the importer did not carry the texture over (all
	parts of one creature share textures/<Creature>.png).

	CopyFace(fromCharacter, rig) copies a player's face decal onto a rig's head.
	Morph(player, "Shark") swaps a player's character for a rig (server side).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SeaCreatureRigSetup = {}

local BODY_HEIGHT = 5.2 -- soles to the top of the head, in studs
local HRP_ABOVE_GROUND = 3.0 -- centre of the HumanoidRootPart (HipHeight 2)

local BODY_PARTS = {
	"Head", "UpperTorso", "LowerTorso",
	"LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm", "RightLowerArm", "RightHand",
	"LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg", "RightFoot",
}

-- joint name, parent part, child part
local JOINTS = {
	{ "Root", "HumanoidRootPart", "LowerTorso" },
	{ "Waist", "LowerTorso", "UpperTorso" },
	{ "Neck", "UpperTorso", "Head" },
	{ "LeftShoulder", "UpperTorso", "LeftUpperArm" },
	{ "LeftElbow", "LeftUpperArm", "LeftLowerArm" },
	{ "LeftWrist", "LeftLowerArm", "LeftHand" },
	{ "RightShoulder", "UpperTorso", "RightUpperArm" },
	{ "RightElbow", "RightUpperArm", "RightLowerArm" },
	{ "RightWrist", "RightLowerArm", "RightHand" },
	{ "LeftHip", "LowerTorso", "LeftUpperLeg" },
	{ "LeftKnee", "LeftUpperLeg", "LeftLowerLeg" },
	{ "LeftAnkle", "LeftLowerLeg", "LeftFoot" },
	{ "RightHip", "LowerTorso", "RightUpperLeg" },
	{ "RightKnee", "RightUpperLeg", "RightLowerLeg" },
	{ "RightAnkle", "RightLowerLeg", "RightFoot" },
}

local COLLIDES = { Head = true, UpperTorso = true, LowerTorso = true }

local function attach(part, name, worldPos)
	local a = part:FindFirstChild(name)
	if not a then
		a = Instance.new("Attachment")
		a.Name = name
		a.Parent = part
	end
	a.CFrame = part.CFrame:Inverse() * CFrame.new(worldPos)
	return a
end

local function top(part)
	return part.Position.Y + part.Size.Y / 2
end

local function bottom(part)
	return part.Position.Y - part.Size.Y / 2
end

function SeaCreatureRigSetup.Run(root, opts)
	opts = opts or {}
	local name = opts.Name or root.Name

	-- collect the body parts, joint markers and creature pieces
	local parts, markers, pieces = {}, {}, {}
	for _, d in ipairs(root:GetDescendants()) do
		if d:IsA("BasePart") then
			if table.find(BODY_PARTS, d.Name) then
				parts[d.Name] = d
			elseif string.sub(d.Name, 1, 6) == "Joint_" then
				markers[string.sub(d.Name, 7)] = d
			elseif string.find(d.Name, "__", 1, true) then
				table.insert(pieces, d)
			end
		end
	end
	for _, n in ipairs(BODY_PARTS) do
		assert(parts[n], "SeaCreatureRigSetup: missing body part " .. n .. " under " .. root:GetFullName())
	end
	for _, j in ipairs(JOINTS) do
		assert(markers[j[1]], "SeaCreatureRigSetup: missing marker Joint_" .. j[1])
	end

	-- one clean model holding everything
	local rig = Instance.new("Model")
	rig.Name = name
	rig.Parent = root.Parent
	for _, p in pairs(parts) do
		p.Parent = rig
	end
	for _, p in ipairs(pieces) do
		p.Parent = rig
	end
	for _, p in pairs(markers) do
		p.Parent = rig
		p.Anchored = true
	end
	if root ~= workspace then
		root:Destroy()
	end
	for _, p in ipairs(rig:GetChildren()) do
		if p:IsA("BasePart") then
			p.Anchored = true
		end
	end

	-- default R15 height
	local function footY()
		return math.min(bottom(parts.LeftFoot), bottom(parts.RightFoot))
	end
	local height = top(parts.Head) - footY()
	if height > 0 and math.abs(height - BODY_HEIGHT) / BODY_HEIGHT > 0.01 then
		rig:ScaleTo(BODY_HEIGHT / height)
	end
	local ground = footY()

	-- HumanoidRootPart
	local rootPos = markers.Root.Position
	local hrp = Instance.new("Part")
	hrp.Name = "HumanoidRootPart"
	hrp.Size = Vector3.new(2, 2, 1)
	hrp.CFrame = CFrame.new(rootPos.X, ground + HRP_ABOVE_GROUND, rootPos.Z)
	hrp.Transparency = 1
	hrp.CanCollide = false
	hrp.Anchored = true
	hrp.Parent = rig
	parts.HumanoidRootPart = hrp

	-- rig attachments at the markers
	for _, j in ipairs(JOINTS) do
		local pos = markers[j[1]].Position
		attach(parts[j[2]], j[1] .. "RigAttachment", pos)
		attach(parts[j[3]], j[1] .. "RigAttachment", pos)
	end
	for _, m in pairs(markers) do
		m:Destroy()
	end

	-- the usual accessory / tool attachments
	local head, ut, lt = parts.Head, parts.UpperTorso, parts.LowerTorso
	local hp, hs = head.Position, head.Size
	-- hats sit on top of the hood when the creature wears one
	local hood = rig:FindFirstChild("Head__Hood")
	local crown = hood and top(hood) or hp.Y + hs.Y / 2
	attach(head, "HatAttachment", Vector3.new(hp.X, crown, hp.Z))
	attach(head, "HairAttachment", Vector3.new(hp.X, crown, hp.Z))
	attach(head, "FaceFrontAttachment", hp + Vector3.new(0, 0, -hs.Z / 2))
	attach(head, "FaceCenterAttachment", hp)
	local up = ut.Position
	attach(ut, "NeckAttachment", Vector3.new(up.X, top(ut), up.Z))
	attach(ut, "BodyFrontAttachment", up + Vector3.new(0, 0, -0.5))
	attach(ut, "BodyBackAttachment", up + Vector3.new(0, 0, 0.5))
	attach(ut, "LeftCollarAttachment", Vector3.new(up.X + 1, top(ut), up.Z))
	attach(ut, "RightCollarAttachment", Vector3.new(up.X - 1, top(ut), up.Z))
	local lp = lt.Position
	attach(lt, "WaistCenterAttachment", lp)
	attach(lt, "WaistFrontAttachment", lp + Vector3.new(0, 0, -0.5))
	attach(lt, "WaistBackAttachment", lp + Vector3.new(0, 0, 0.5))
	attach(parts.LeftUpperArm, "LeftShoulderAttachment", Vector3.new(parts.LeftUpperArm.Position.X, top(ut), up.Z))
	attach(parts.RightUpperArm, "RightShoulderAttachment", Vector3.new(parts.RightUpperArm.Position.X, top(ut), up.Z))
	for _, side in ipairs({ "Left", "Right" }) do
		local wrist = parts[side .. "Hand"]:FindFirstChild(side .. "WristRigAttachment")
		local wp = parts[side .. "Hand"].CFrame * wrist.CFrame
		attach(parts[side .. "Hand"], side .. "GripAttachment", wp.Position - Vector3.new(0, 0.15, 0))
		local ankle = parts[side .. "Foot"]:FindFirstChild(side .. "AnkleRigAttachment")
		local ap = (parts[side .. "Foot"].CFrame * ankle.CFrame).Position
		attach(parts[side .. "Foot"], side .. "FootAttachment", Vector3.new(ap.X, ground, ap.Z))
	end

	-- body parts + creature pieces
	for _, n in ipairs(BODY_PARTS) do
		local p = parts[n]
		p.CanCollide = COLLIDES[n] == true
		p.Massless = false
		p.CastShadow = true
	end
	for _, piece in ipairs(pieces) do
		local owner = string.match(piece.Name, "^(%w+)__")
		local base = parts[owner]
		if base then
			piece.CanCollide = false
			piece.CanTouch = false
			piece.CanQuery = false
			piece.Massless = true
			if string.find(piece.Name, "Glow", 1, true) then
				piece.Material = Enum.Material.Neon
				piece.CastShadow = false
			elseif string.find(piece.Name, "Glass", 1, true) then
				piece.Material = Enum.Material.Glass
				piece.Transparency = 0.35
				piece.CastShadow = false
			end
			local w = Instance.new("WeldConstraint")
			w.Part0 = base
			w.Part1 = piece
			w.Parent = piece
		else
			warn("SeaCreatureRigSetup: no body part '" .. tostring(owner) .. "' for " .. piece.Name)
		end
	end
	if opts.TextureId then
		for _, d in ipairs(rig:GetDescendants()) do
			if d:IsA("MeshPart") then
				d.TextureID = opts.TextureId
			end
		end
	end

	-- face
	local face = head:FindFirstChild("face") or Instance.new("Decal")
	face.Name = "face"
	face.Face = Enum.NormalId.Front
	face.Texture = opts.Face or "rbxasset://textures/face.png"
	face.Parent = head

	-- humanoid + motors
	local hum = Instance.new("Humanoid")
	hum.RigType = Enum.HumanoidRigType.R15
	hum.HipHeight = (hrp.Position.Y - hrp.Size.Y / 2) - ground
	hum.Parent = rig
	rig.PrimaryPart = hrp
	hum:BuildRigFromAttachments()
	for _, d in ipairs(rig:GetChildren()) do
		if d:IsA("BasePart") then
			d.Anchored = false
		end
	end
	rig:SetAttribute("SeaCreature", name)

	if not opts.Keep then
		local dest = opts.Destination
		if not dest then
			dest = ReplicatedStorage:FindFirstChild("SeaCreatureRigs")
			if not dest then
				dest = Instance.new("Folder")
				dest.Name = "SeaCreatureRigs"
				dest.Parent = ReplicatedStorage
			end
		end
		local old = dest:FindFirstChild(name)
		if old and old ~= rig then
			old:Destroy()
		end
		rig.Parent = dest
	end
	print(string.format("SeaCreatureRigSetup: %s ready (%d creature pieces)", name, #pieces))
	return rig
end

function SeaCreatureRigSetup.CopyFace(fromCharacter, rig)
	local fromHead = fromCharacter:FindFirstChild("Head")
	local toHead = rig:FindFirstChild("Head")
	if not (fromHead and toHead) then
		return
	end
	local src = fromHead:FindFirstChildOfClass("Decal")
	local dst = toHead:FindFirstChild("face")
	if src and dst then
		dst.Texture = src.Texture
	end
end

-- Server: turn a player into one of the rigs in ReplicatedStorage.SeaCreatureRigs.
-- Keeps their face, position and the default Animate / Health scripts.
function SeaCreatureRigSetup.Morph(player, creatureName)
	local folder = ReplicatedStorage:FindFirstChild("SeaCreatureRigs")
	local template = folder and folder:FindFirstChild(creatureName)
	assert(template, "SeaCreatureRigSetup.Morph: no rig named " .. tostring(creatureName))
	local old = player.Character
	local rig = template:Clone()
	rig.Name = player.Name
	if old then
		SeaCreatureRigSetup.CopyFace(old, rig)
		for _, scriptName in ipairs({ "Animate", "Health" }) do
			local s = old:FindFirstChild(scriptName)
			if s then
				s:Clone().Parent = rig
			end
		end
		rig:PivotTo(old:GetPivot())
	end
	player.Character = rig
	rig.Parent = workspace
	if old then
		old:Destroy()
	end
	return rig
end

return SeaCreatureRigSetup
