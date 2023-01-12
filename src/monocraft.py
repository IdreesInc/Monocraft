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
from polygonizer import PixelImage, generatePolygons

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

		drawImage(generateImage(character), pen)
		monocraft[character["name"]].width = PIXEL_SIZE * 6
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	monocraft.generate(outputDir + "Monocraft-no-ligatures.ttf")

	for ligature in ligatures:
		lig = monocraft.createChar(-1, ligature["name"])
		pen = monocraft[ligature["name"]].glyphPen()
		drawImage(generateImage(ligature), pen)
		monocraft[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
		lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
	print(f"Generated {len(ligatures)} ligatures")

	monocraft.generate(outputDir + "Monocraft.ttf")
	monocraft.generate(outputDir + "Monocraft.otf")

def generateImage(character):
	image = PixelImage()
	if "pixels" in character:
		arr = character["pixels"]
		x = int(character["leftMargin"]) if "leftMargin" in character else 0
		y = int(-character["descent"]) if "descent" in character else 0
		image = image | imageFromArray(arr, x, y)
	if "reference" in character:
		image = image | generateImage(charactersByCodepoint[character["reference"]])
	if "diacritic" in character:
		diacritic = diacritics[character["diacritic"]]
		arr = diacritic["pixels"]
		x = image.x
		y = findHighestY(image) + 1
		if "diacriticSpace" in character:
			y += int(character["diacriticSpace"])
		image = image | imageFromArray(arr, x, y)
	return image

def findHighestY(image):
	for y in range(image.y_end - 1, image.y, -1):
		for x in range(image.x, image.x_end):
			if image[x, y]:
				return y
	return image.y

def imageFromArray(arr, x=0, y=0):
	return PixelImage(
		x=x,
		y=y,
		width=len(arr[0]),
		height=len(arr),
		data=bytes(x for a in reversed(arr) for x in a),
	)

def drawImage(image, pen):
	for polygon in generatePolygons(image):
		start = True
		for x, y in polygon:
			x *= PIXEL_SIZE
			y *= PIXEL_SIZE
			if start:
				pen.moveTo(x, y)
				start = False
			else:
				pen.lineTo(x, y)
		pen.closePath()

generateFont()
generateExamples(characters, ligatures, charactersByCodepoint)