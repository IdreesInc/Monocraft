# Monocraft, a monospaced font for developers who like Minecraft a bit too much.
# Copyright (C) 2022-2024 Idrees Hassan
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
import argparse
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

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--output-ttc",
		action="store_true",
		dest="output_ttc",
	)
	parser.add_argument(
		"-a",
		"--all",
		action="store_true",
		dest="all",
	)
	parser.add_argument(
		"-O",
		"--black",
		action="store_true",
		dest="black",
	)
	parser.add_argument(
		"-B",
		"--bold",
		action="store_true",
		dest="bold",
	)
	parser.add_argument(
		"-b",
		"--semibold",
		action="store_true",
		dest="semibold",
	)
	parser.add_argument(
		"-l",
		"--light",
		action="store_true",
		dest="light",
	)
	parser.add_argument(
		"-L",
		"--extralight",
		action="store_true",
		dest="extralight",
	)
	parser.add_argument(
		"-i",
		"--italic",
		action="store_true",
		dest="italic",
	)
	ret = parser.parse_args()
	if ret.all:
		ret.black = ret.bold = ret.semibold = ret.light = ret.extralight = ret.italic = True
	return ret

def generateFont(*, black=False, bold=False, semibold=False, light=False, extralight=False, italic=False, output_ttc=False, **kw):
	fontList = [
		fontforge.font(),
		fontforge.font() if italic else None,
		fontforge.font() if black else None,
		fontforge.font() if black and italic else None,
		fontforge.font() if bold else None,
		fontforge.font() if bold and italic else None,
		fontforge.font() if semibold else None,
		fontforge.font() if semibold and italic else None,
		fontforge.font() if light else None,
		fontforge.font() if light and italic else None,
		fontforge.font() if extralight else None,
		fontforge.font() if extralight and italic else None,
	]
	for font in fontList:
		if font is None:
			continue
		font.fontname = "Monocraft"
		font.familyname = "Monocraft"
		font.fullname = "Monocraft"
		font.copyright = "Idrees Hassan, https://github.com/IdreesInc/Monocraft"
		font.encoding = "UnicodeFull"
		font.version = "4.0"
		font.weight = "Regular"
		font.ascent = PIXEL_SIZE * 8
		font.descent = PIXEL_SIZE
		font.em = PIXEL_SIZE * 9
		font.upos = -PIXEL_SIZE  # Underline position
		font.addLookup("ligatures-exp", "gsub_multiple", (),
					   (("ccmp", (("dflt", ("dflt")), ("latn", ("dflt")))), ))
		font.addLookupSubtable("ligatures-exp", "ligatures-exp-subtable")
		font.addLookup("ligatures", "gsub_ligature", (),
					   (("liga", (("dflt", ("dflt")), ("latn", ("dflt")))), ))
		font.addLookupSubtable("ligatures", "ligatures-subtable")

	font = fontList[0]
	if font is not None:
		font.macstyle = 0
		font.os2_stylemap = 0x40
	font = fontList[1]
	if font is not None:
		font.fontname = "Monocraft-Italic"
		font.fullname = "Monocraft Italic"
		font.macstyle = 2
		font.os2_stylemap = 1
		font.italicangle = -15
	font = fontList[2]
	if font is not None:
		font.fontname = "Monocraft-Black"
		font.fullname = "Monocraft Black"
		font.weight = "Black"
		font.macstyle = 1
		font.os2_stylemap = 0x20
	font = fontList[3]
	if font is not None:
		font.fontname = "Monocraft-Black-Italic"
		font.fullname = "Monocraft Black Italic"
		font.weight = "Black"
		font.macstyle = 3
		font.os2_stylemap = 0x21
		font.italicangle = -15
	font = fontList[4]
	if font is not None:
		font.fontname = "Monocraft-Bold"
		font.fullname = "Monocraft Bold"
		font.weight = "Bold"
		font.macstyle = 1
		font.os2_stylemap = 0x20
	font = fontList[5]
	if font is not None:
		font.fontname = "Monocraft-Bold-Italic"
		font.fullname = "Monocraft Bold Italic"
		font.weight = "Bold"
		font.macstyle = 3
		font.os2_stylemap = 0x21
		font.italicangle = -15
	font = fontList[6]
	if font is not None:
		font.fontname = "Monocraft-SemiBold"
		font.fullname = "Monocraft SemiBold"
		font.weight = "Demi"
		font.macstyle = 1
		font.os2_stylemap = 0x20
	font = fontList[7]
	if font is not None:
		font.fontname = "Monocraft-SemiBold-Italic"
		font.fullname = "Monocraft SemiBold Italic"
		font.weight = "Demi"
		font.macstyle = 3
		font.os2_stylemap = 0x21
		font.italicangle = -15
	font = fontList[8]
	if font is not None:
		font.fontname = "Monocraft-Light"
		font.fullname = "Monocraft Light"
		font.weight = "Light"
		font.macstyle = 0
		font.os2_stylemap = 0
	font = fontList[9]
	if font is not None:
		font.fontname = "Monocraft-Light-Italic"
		font.fullname = "Monocraft Light Italic"
		font.weight = "Light"
		font.macstyle = 2
		font.os2_stylemap = 1
		font.italicangle = -15
	font = fontList[10]
	if font is not None:
		font.fontname = "Monocraft-ExtraLight"
		font.fullname = "Monocraft ExtraLight"
		font.weight = "Extra-Light"
		font.macstyle = 0
		font.os2_stylemap = 0
	font = fontList[11]
	if font is not None:
		font.fontname = "Monocraft-ExtraLight-Italic"
		font.fullname = "Monocraft ExtraLight Italic"
		font.weight = "Extra-Light"
		font.macstyle = 2
		font.os2_stylemap = 1
		font.italicangle = -15

	for character in characters:
		charactersByCodepoint[character["codepoint"]] = character
		image, kw = generateImage(character)
		createChar(fontList, character["codepoint"], character["name"], image, **kw)
	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	if output_ttc:
		fontList[0].generateTtc(
			outputDir + "Monocraft-no-ligatures.ttc",
			[i for i in fontList[1:] if i is not None],
			ttcflags=("merge", ),
			layer=1,
		)

	for ligature in ligatures:
		image, kw = generateImage(ligature)
		name = ligature["name"].translate(str.maketrans(" ", "_"))
		createChar(fontList, -1, name, image, **kw)
		for font in fontList:
			if font is None:
				continue
			lig = font[name]
			lig.addPosSub("ligatures-subtable", tuple(map(lambda codepoint: charactersByCodepoint[codepoint]["name"], ligature["sequence"])))
			lig.addPosSub(
				"ligatures-exp-subtable",
				(name, *(charactersByCodepoint[32]["name"] for _ in range(len(ligature["sequence"])-1))),
			);
	print(f"Generated {len(ligatures)} ligatures")

	for font in fontList:
		if font is None:
			continue
		font.generate(f"{outputDir}{font.fontname}.otf")
		font.generate(f"{outputDir}{font.fontname}.ttf")

	if output_ttc:
		fontList[0].generateTtc(
			outputDir + "Monocraft.ttc",
			[i for i in fontList[1:] if i is not None],
			ttcflags=("merge", ),
			layer=1,
		)

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
		data=bytes(v for a in reversed(arr) for v in a),
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

BOLD_THIN_DISTS = {
	"Black": 0.3,
	"Bold": 0.2,
	"Demi": 0.1,
	"Light": -0.1,
	"Extra-Light": -0.3,
}
ITALIC_RATIO = math.tan(math.radians(15))

def boldify(p, boldness):
	l = len(p)
	for i in range(l):
		x, y = p[i]
		dx, dy = 0, 0
		px, py = p[i - 1]
		if px < x:
			dy += boldness
		elif px > x:
			dy -= boldness
		elif py < y:
			dx -= boldness
		else:
			dx += boldness
		px, py = p[(i + 1) % l]
		if px < x:
			dy -= boldness
		elif px > x:
			dy += boldness
		elif py < y:
			dx += boldness
		else:
			dx -= boldness
		yield (dx + x, dy + y)

def createChar(
	fontList,
	code,
	name,
	image=None,
	*,
	width=None,
	dx=0,
	dy=0,
	glyphclass=None,
):
	if image is not None:
		poly = [[(x + dx, y + dy) for x, y in p]
				for p in generatePolygons(image)]

	poly_b = None
	poly_t = None

	for font in fontList:
		if font is None:
			continue
		char = font.createChar(code, name)
		#char.manualHints = True
		if glyphclass is not None:
			char.glyphclass = glyphclass
		if image is None:
			char.width = width if width is not None else PIXEL_SIZE * 6
			continue

		p = poly
		try:
			dist = BOLD_THIN_DISTS[font.weight]
		except KeyError:
			dist = 0

		if dist > 0:
			if poly_b is None:
				poly_b = [[(x + dx, y + dy) for x, y in p] for p in generatePolygons(image, join_polygons=False)]
			p = (boldify(p, dist) for p in poly_b)
		elif dist < 0:
			if poly_t is None:
				poly_t = [[(x + dx, y + dy) for x, y in p] for p in generatePolygons(image, join_polygons=False, exclude_corners=True)]
			p = (boldify(p, dist) for p in poly_t)

		if font.macstyle & 2:
			p = (((x + y * ITALIC_RATIO, y) for x, y in p) for p in p)

		drawPolygon(p, char.glyphPen())
		char.width = width if width is not None else PIXEL_SIZE * 6

args = parseArgs()
generateFont(**vars(args))
generateExamples(characters, ligatures, charactersByCodepoint)
