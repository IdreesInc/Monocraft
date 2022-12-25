import fontforge
import json

print("hi")

PIXEL_SIZE = 120

monocraft = fontforge.font()
monocraft.fontname = "Monocraft"
monocraft.weight = "Medium"
monocraft.ascent = PIXEL_SIZE * 8
monocraft.descent = PIXEL_SIZE
monocraft.em = PIXEL_SIZE * 9
monocraft.upos = -PIXEL_SIZE # Underline position

characters = json.load(open("./characters.json"))
diacritics = json.load(open("./diacritics.json"))
charactersByCodepoint = {}
print(len(characters))

def drawGlyph(pixels, pen, startingY):
	top = 0 # The highest point of the character
	for rowIndex in range(len(pixels)):
		row = pixels[-(rowIndex + 1)]
		for columnIndex in range(len(row)):
			if row[columnIndex] == 0:
				continue
			pen.moveTo((columnIndex * PIXEL_SIZE, rowIndex * PIXEL_SIZE + startingY)) # Bottom left
			pen.lineTo((columnIndex * PIXEL_SIZE, (rowIndex + 1) * PIXEL_SIZE + startingY))
			pen.lineTo(((columnIndex + 1) * PIXEL_SIZE, (rowIndex + 1) * PIXEL_SIZE + startingY))
			pen.lineTo(((columnIndex + 1) * PIXEL_SIZE, rowIndex * PIXEL_SIZE + startingY))
			pen.closePath()
			top = (rowIndex + 1) * PIXEL_SIZE + startingY
	return top

def drawCharacter(character, pen):
	floor = -PIXEL_SIZE * character["descent"] if "descent" in character else 0
	return drawGlyph(character["pixels"], pen, floor)

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
		drawGlyph(diacritic["pixels"], pen, top)

	monocraft[character["name"]].width = PIXEL_SIZE * 6

monocraft.generate("generated.ttf")