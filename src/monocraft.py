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

PIXEL_SIZE = 80

characters = json.load(open("./characters.json"))
diacritics = json.load(open("./diacritics.json"))
ligatures = json.load(open("./ligatures.json"))
ligatures += generate_continuous_ligatures("./continuous_ligatures.json")

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}

def generateFont():
	monocraft = fontforge.font()
	monocraft.fontname = "Monocraft"
	monocraft.familyname = "Monocraft"
	monocraft.fullname = "Monocraft"
	monocraft.copyright = "Idrees Hassan, https://github.com/IdreesInc/Monocraft"
	monocraft.encoding = "UnicodeFull"
	monocraft.version = "3.0"
	monocraft.weight = "Regular"
	monocraft.ascent = PIXEL_SIZE * 12
	monocraft.descent = PIXEL_SIZE * 2
	monocraft.em = PIXEL_SIZE * 13
	monocraft.upos = -PIXEL_SIZE * 2 # Underline position
	monocraft.addLookup("ligatures", "gsub_ligature", (), (("liga",(("dflt",("dflt")),("latn",("dflt")))),))
	monocraft.addLookupSubtable("ligatures", "ligatures-subtable")

	for character in characters:
		charactersByCodepoint[character["codepoint"]] = character
		monocraft.createChar(character["codepoint"], character["name"])
		pen = monocraft[character["name"]].glyphPen()
		top = 0
		drawn = character

		image, kw = generateImage(character)
		drawImage(image, pen, **kw)
		monocraft[character["name"]].width = PIXEL_SIZE * 6
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	monocraft.generate(outputDir + "Monocraft-no-ligatures.ttf")
	for ligature in ligatures:
		lig = monocraft.createChar(-1, ligature["name"])
		pen = monocraft[ligature["name"]].glyphPen()
		image, kw = generateImage(ligature)
		drawImage(image, pen, **kw)
		monocraft[ligature["name"]].width = PIXEL_SIZE * len(ligature["sequence"]) * 6
		lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
	print(f"Generated {len(ligatures)} ligatures")

	monocraft.generate(outputDir + "Monocraft.ttf")
	monocraft.generate(outputDir + "Monocraft.otf")

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
		image = addDiacritic(image, diacritics[character["diacritic"]], character["diacriticSpace"])
	elif "diacritics" in character:
		for diacritic in character["diacritics"]:
			image = addDiacritic(image, diacritics[diacritic], character["diacriticSpace"])
	return (image, kw)

def addDiacritic(image, diacritic, spacing):
	arr = diacritic["pixels"]
	direction = [0, 1]
	if "placement" in diacritic:
		if "above" in diacritic["placement"]:
			direction[1] = 1
		elif "below" in diacritic["placement"]:
			direction[1] = -1
		if "left" in diacritic["placement"]:
			direction[0] = -1
		elif "right" in diacritic["placement"]:
			direction[0] = 1
	x, y = findBoundsInDirection(image, direction)
	x += direction[0]
	y += direction[1]
	if "offsetX" in diacritic:
	    x += diacritic["offsetX"]
	if "offsetY" in diacritic:
	    y += diacritic["offsetY"]
	if spacing is not None:
		x += int(spacing) * direction[0]
		y += int(spacing) * direction[1]
	return image | imageFromArray(arr, x, y)

def findBoundsInDirection(image, direction):
	if   direction[0] == 0: x = image.x
	elif direction[0] >  0: x = findHighestX(image)
	elif direction[0] <  0: x = findLowestX(image)

	if   direction[1] == 0: y = image.y
	elif direction[1] >  0: y = findHighestY(image)
	elif direction[1] <  0: y = findLowestY(image)

	return x, y

def findHighestX(image):
	for x in range(image.x_end - 1, image.x, -1):
		for y in range(image.y, image.y_end):
			if image[x, y]:
				return x
	return image.x
def findLowestX(image):
	for x in range(image.x, image.x_end):
		for y in range(image.y, image.y_end):
			if image[x, y]:
				return x
	return image.x_end
def findHighestY(image):
	for y in range(image.y_end - 1, image.y, -1):
		for x in range(image.x, image.x_end):
			if image[x, y]:
				return y
	return image.y
def findLowestY(image):
	for y in range(image.y, image.y_end):
		for x in range(image.x, image.x_end):
			if image[x, y]:
				return y
	return image.y_end

def imageFromArray(arr, x=0, y=0):
	return PixelImage(
		x=x,
		y=y,
		width=len(arr[0]),
		height=len(arr),
		data=bytes(x for a in reversed(arr) for x in a),
	)

def drawImage(image, pen, *, dx=0, dy=0):
	for polygon in generatePolygons(image):
		start = True
		for x, y in polygon:
			x = (x + dx) * PIXEL_SIZE
			y = (y + dy) * PIXEL_SIZE
			if start:
				pen.moveTo(x, y)
				start = False
			else:
				pen.lineTo(x, y)
		pen.closePath()

generateFont()
generateExamples(characters, ligatures, charactersByCodepoint)
