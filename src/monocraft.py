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
print(characters[0]["codepoint"])

for character in characters:
	monocraft.createChar(character["codepoint"], character["name"])
	pen = monocraft[character["name"]].glyphPen()
	for rowIndex in range(len(character["pixels"])):
		row = character["pixels"][-(rowIndex + 1)]
		for columnIndex in range(len(row)):
			if row[columnIndex] == 0:
				continue
			pen.moveTo((columnIndex * PIXEL_SIZE, rowIndex * PIXEL_SIZE)) # Bottom left
			pen.lineTo((columnIndex * PIXEL_SIZE, (rowIndex + 1) * PIXEL_SIZE))
			pen.lineTo(((columnIndex + 1) * PIXEL_SIZE, (rowIndex + 1) * PIXEL_SIZE))
			pen.lineTo(((columnIndex + 1) * PIXEL_SIZE, rowIndex * PIXEL_SIZE))
			pen.closePath()
	monocraft[character["name"]].width = PIXEL_SIZE * 6

monocraft.generate("generated.ttf")