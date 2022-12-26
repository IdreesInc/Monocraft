import fontforge
import json

PIXEL_SIZE = 120

monocraft = fontforge.font()
monocraft.fontname = "Monocraft"
monocraft.familyname = "Monocraft"
monocraft.fullname = "Monocraft"
monocraft.encoding = "UnicodeFull"
monocraft.version = "2.0"
monocraft.weight = "Medium"
monocraft.ascent = PIXEL_SIZE * 8
monocraft.descent = PIXEL_SIZE
monocraft.em = PIXEL_SIZE * 9
monocraft.upos = -PIXEL_SIZE # Underline position
monocraft.addLookup("ligatures", "gsub_ligature", (), (("liga",(("dflt",("dflt")),)),))
monocraft.addLookupSubtable("ligatures", "ligatures-subtable")

characters = json.load(open("./characters.json"))
diacritics = json.load(open("./diacritics.json"))
ligatures = json.load(open("./ligatures.json"))
charactersByCodepoint = {}

def drawGlyph(pixels, pen, startingX, startingY):
	top = 0 # The highest point of the character
	for rowIndex in range(len(pixels)):
		row = pixels[-(rowIndex + 1)]
		for columnIndex in range(len(row)):
			if row[columnIndex] == 0:
				continue
			pen.moveTo((columnIndex * PIXEL_SIZE + startingX, rowIndex * PIXEL_SIZE + startingY)) # Bottom left
			pen.lineTo((columnIndex * PIXEL_SIZE + startingX, (rowIndex + 1) * PIXEL_SIZE + startingY))
			pen.lineTo(((columnIndex + 1) * PIXEL_SIZE + startingX, (rowIndex + 1) * PIXEL_SIZE + startingY))
			pen.lineTo(((columnIndex + 1) * PIXEL_SIZE + startingX, rowIndex * PIXEL_SIZE + startingY))
			pen.closePath()
			top = (rowIndex + 1) * PIXEL_SIZE + startingY
	return top

def drawCharacter(character, pen):
	leftMargin = PIXEL_SIZE * character["leftMargin"] if "leftMargin" in character else 0
	floor = -PIXEL_SIZE * character["descent"] if "descent" in character else 0
	return drawGlyph(character["pixels"], pen, leftMargin, floor)

for character in characters:
	charactersByCodepoint[character["codepoint"]] = character
	monocraft.createChar(character["codepoint"], character["name"])
	pen = monocraft[character["name"]].glyphPen()
	top = 0
	if "pixels" in character:
		top = drawCharacter(character, pen)
	elif "reference" in character:
		top = drawCharacter(charactersByCodepoint[character["reference"]], pen)
	if "diacritic" in character:
		diacritic = diacritics[character["diacritic"]]
		if "diacriticSpace" in character:
			top += PIXEL_SIZE * character["diacriticSpace"]
		drawGlyph(diacritic["pixels"], pen, 0, top)
	monocraft[character["name"]].width = PIXEL_SIZE * 6

print(f"Generated {len(characters)} characters")

for ligature in ligatures:
	lig = monocraft.createChar(-1, ligature["name"])
	pen = monocraft[ligature["name"]].glyphPen()
	drawCharacter(ligature, pen)
	monocraft[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
	lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))

print(f"Generated {len(ligatures)} ligatures")

monocraft.generate("../Monocraft.ttf")