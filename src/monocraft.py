# Monocraft, a monospaced font for developers who like Minecraft a bit too much.
# Copyright (C) 2022 Idrees Hassan
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import fontforge
import json
from generate_diacritics import generateDiacritics
from generate_examples import generateExamples

PIXEL_SIZE = 120

characters = json.load(open("./characters.json"))
diacritics = json.load(open("./diacritics.json"))
ligatures = json.load(open("./ligatures.json"))

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}

def generateFont():
	monocraft = fontforge.font()
	monocraft.fontname = "Monocraft"
	monocraft.familyname = "Monocraft"
	monocraft.fullname = "Monocraft"
	monocraft.copyright = "Idrees Hassan, https://github.com/IdreesInc/Monocraft"
	monocraft.encoding = "UnicodeFull"
	monocraft.version = "2.3"
	monocraft.weight = "Regular"
	monocraft.ascent = PIXEL_SIZE * 8
	monocraft.descent = PIXEL_SIZE
	monocraft.em = PIXEL_SIZE * 9
	monocraft.upos = -PIXEL_SIZE # Underline position
	monocraft.addLookup("ligatures", "gsub_ligature", (), (("liga",(("dflt",("dflt")),)),))
	monocraft.addLookupSubtable("ligatures", "ligatures-subtable")

	for character in characters:
		charactersByCodepoint[character["codepoint"]] = character
		monocraft.createChar(character["codepoint"], character["name"])
		pen = monocraft[character["name"]].glyphPen()
		top = 0
		drawn = character
		if "pixels" in character:
			top = drawCharacter(character, pen)
		elif "reference" in character:
			drawn = charactersByCodepoint[character["reference"]]
			top = drawCharacter(drawn, pen)
		if "diacritic" in character:
			diacritic = diacritics[character["diacritic"]]
			if "diacriticSpace" in character:
				top += PIXEL_SIZE * character["diacriticSpace"]
			drawGlyph(diacritic["pixels"], pen, getLeftMargin(drawn), top)
		monocraft[character["name"]].width = PIXEL_SIZE * 6
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	monocraft.generate(outputDir + "Monocraft-no-ligatures.ttf")

	for ligature in ligatures:
		lig = monocraft.createChar(-1, ligature["name"])
		pen = monocraft[ligature["name"]].glyphPen()
		drawCharacter(ligature, pen)
		monocraft[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
		lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
	print(f"Generated {len(ligatures)} ligatures")

	monocraft.generate(outputDir + "Monocraft.ttf")
	monocraft.generate(outputDir + "Monocraft.otf")

def getLeftMargin(character):
	return PIXEL_SIZE * character["leftMargin"] if "leftMargin" in character else 0

def drawCharacter(character, pen):
	if "reference" in character: return drawCharacter(charactersByCodepoint[character["reference"]],pen)
	leftMargin = getLeftMargin(character)
	floor = -PIXEL_SIZE * character["descent"] if "descent" in character else 0
	return drawGlyph(character["pixels"], pen, leftMargin, floor)

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

generateFont()
generateExamples(characters, ligatures, charactersByCodepoint)