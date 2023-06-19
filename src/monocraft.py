# Monocraft, a monospaced font for developers who like Minecraft a bit too much.
# Copyright (C) 2022-2023 Idrees Hassan
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
import math
from generate_diacritics import generateDiacritics
from generate_examples import generateExamples
from polygonizer import PixelImage, generatePolygons
from generate_continuous_ligatures import generate_continuous_ligatures

PIXEL_SIZE = 120

characters = json.load(open("./characters.json"))
diacritics = json.load(open("./diacritics.json"))
ligatures = json.load(open("./ligatures.json"))
ligatures += generate_continuous_ligatures("./continuous_ligatures.json")

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}

def generateFont():
	fontList = [fontforge.font() for _ in range(3)]
	for font in fontList:
		font.fontname = "Monocraft"
		font.familyname = "Monocraft"
		font.fullname = "Monocraft"
		font.copyright = "Idrees Hassan, https://github.com/IdreesInc/Monocraft"
		font.encoding = "UnicodeFull"
		font.version = "3.0"
		font.weight = "Regular"
		font.ascent = PIXEL_SIZE * 8
		font.descent = PIXEL_SIZE
		font.em = PIXEL_SIZE * 9
		font.upos = -PIXEL_SIZE # Underline position
		font.addLookup("ligatures", "gsub_ligature", (), (("liga",(("dflt",("dflt")),("latn",("dflt")))),))
		font.addLookupSubtable("ligatures", "ligatures-subtable")

	font = fontList[0]
	font.os2_stylemap = font.macstyle = 0
	font = fontList[1]
	font.fontname = "Monocraft-Bold"
	font.fullname = "Monocraft Bold"
	font.os2_stylemap = font.macstyle = 1
	font = fontList[2]
	font.fontname = "Monocraft-Italic"
	font.fullname = "Monocraft Italic"
	font.os2_stylemap = font.macstyle = 2
	font.italicangle = -15

	for character in characters:
		charactersByCodepoint[character["codepoint"]] = character
		image, kw = generateImage(character)
		createChar(fontList, character["codepoint"], character["name"], image, **kw)
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	fontList[0].generate(outputDir + "Monocraft-no-ligatures.ttf")
	fontList[1].generate(outputDir + "Monocraft-bold-no-ligatures.ttf")
	fontList[2].generate(outputDir + "Monocraft-italic-no-ligatures.ttf")
	for ligature in ligatures:
		image, kw = generateImage(ligature)
		createChar(fontList, -1, ligature["name"], image, width=PIXEL_SIZE * len(ligature["sequence"]) * 6, **kw)
		for font in fontList:
			font[ligature["name"]].addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
	print(f"Generated {len(ligatures)} ligatures")

	fontList[0].generate(outputDir + "Monocraft.ttf")
	fontList[0].generate(outputDir + "Monocraft.otf")
	fontList[1].generate(outputDir + "Monocraft-bold.ttf")
	fontList[1].generate(outputDir + "Monocraft-bold.otf")
	fontList[2].generate(outputDir + "Monocraft-italic.ttf")
	#fontList[2].generate(outputDir + "Monocraft-italic.otf")

def generateImage(character):
	image = PixelImage()
	kw = {}
	if "pixels" in character:
		arr = character["pixels"]
		leftMargin = character["leftMargin"] if "leftMargin" in character else 0
		x = math.floor(leftMargin)
		kw['dx'] = leftMargin - x
		descent = -character["descent"] if "descent" in character else 0
		y = math.floor(descent)
		kw['dy'] = descent - y
		image = image | imageFromArray(arr, x, y)
	if "reference" in character:
		other = generateImage(charactersByCodepoint[character["reference"]])
		kw.update(other[1])
		image = image | other[0]
	if "diacritic" in character:
		diacritic = diacritics[character["diacritic"]]
		arr = diacritic["pixels"]
		x = image.x
		y = findHighestY(image) + 1
		if "diacriticSpace" in character:
			y += int(character["diacriticSpace"])
		image = image | imageFromArray(arr, x, y)
	return (image, kw)

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

def drawPolygon(poly, pen):
	for polygon in poly:
		start = True
		for x, y in polygon:
			x = int(math.floor(x * PIXEL_SIZE))
			y = int(math.floor(y * PIXEL_SIZE))
			if start:
				pen.moveTo(x, y)
				start = False
			else:
				pen.lineTo(x, y)
		pen.closePath()

BOLD_DIST = 0.2
ITALIC_MAT = (1, 0, math.tan(math.radians(15)), 1, 0, 0)

def createChar(fontList, code, name, image=None, *, width=None, dx=0, dy=0):
	if image is not None:
		poly = [[(x + dx, y + dy) for x, y in p]
				for p in generatePolygons(image)]
	for font in fontList:
		char = font.createChar(code, name)
		if image is None:
			char.width = width if width is not None else PIXEL_SIZE * 6
			continue

		if font.macstyle & 1 != 0:
			def f(p):
				l = len(p)
				for i, (x, y) in enumerate(p):
					x_, y_ = x + dx, y + dy
					px, py = p[i - 1]
					if px < x:
						y_ -= BOLD_DIST
					elif px > x:
						y_ += BOLD_DIST
					elif py < y:
						x_ += BOLD_DIST
					else:
						x_ -= BOLD_DIST
					px, py = p[(i + 1) % l]
					if px < x:
						y_ += BOLD_DIST
					elif px > x:
						y_ -= BOLD_DIST
					elif py < y:
						x_ -= BOLD_DIST
					else:
						x_ += BOLD_DIST
					yield (x_, y_)
			drawPolygon(
				[f(p) for p in generatePolygons(image, join_polygons=True)],
				char.glyphPen(),
			)
		else:
			drawPolygon(poly, char.glyphPen())
		if font.macstyle & 2 != 0:
			char.transform(ITALIC_MAT, ("round", ))
		char.width = width if width is not None else PIXEL_SIZE * 6

generateFont()
generateExamples(characters, ligatures, charactersByCodepoint)
