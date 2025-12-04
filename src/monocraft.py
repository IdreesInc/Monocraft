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
from typing import NamedTuple
from generate_diacritics import generateDiacritics
from generate_examples import generateExamples
from polygonizer import PixelImage, generatePolygons
from generate_continuous_ligatures import generate_continuous_ligatures

PIXEL_SIZE = 120
WEIGHT_STROKE_OFFSETS = {
	"Black": 0.3,
	"Bold": 0.2,
	"Demi": 0.1,
	"Light": -0.1,
	"Extra-Light": -0.3,
}
ITALIC_RATIO = math.tan(math.radians(15))

characters = json.load(open("./characters.json"))
diacritics = json.load(open("./diacritics.json"))
ligatures = json.load(open("./ligatures.json"))
ligatures += generate_continuous_ligatures("./continuous_ligatures.json")

characters = generateDiacritics(characters, diacritics)
charactersByCodepoint = {}


def parseArgs() -> argparse.Namespace:
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


def generateFont(
	*,
	black=False,
	bold=False,
	semibold=False,
	light=False,
	extralight=False,
	italic=False,
	output_ttc=False,
	**kw,
):
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
		font.version = "4.2"
		font.weight = "Regular"
		# See https://monotype.github.io/panose/pan2.htm
		# (2: Latin Text, 11: Normal Sans, ..., 9: Monospaced)
		font.os2_panose = (2, 11, 0, 9, 0, 0, 0, 0, 0, 0)
		font.ascent = PIXEL_SIZE * 8
		font.descent = PIXEL_SIZE
		font.em = PIXEL_SIZE * 9
		font.upos = -PIXEL_SIZE  # Underline position
		font.addLookup(
			"ligatures-exp",
			"gsub_multiple",
			(),
			(("ccmp", (("dflt", ("dflt")), ("latn", ("dflt")))),),
		)
		font.addLookupSubtable("ligatures-exp", "ligatures-exp-subtable")
		font.addLookup(
			"ligatures", "gsub_ligature", (), (("liga", (("dflt", ("dflt")), ("latn", ("dflt")))),)
		)
		font.addLookupSubtable("ligatures", "ligatures-subtable")

	class FontWeight(NamedTuple):
		suffix: str
		weight: str
		macstyle: int
		os2_stylemap: int
		panose_weight: int
		italic_angle: int

	font_weights: list[FontWeight] = [
		FontWeight("", "Regular", 0, 0x40, 6, 0),
		FontWeight("Italic", "Regular", 2, 1, 6, -15),
		FontWeight("Black", "Black", 1, 0x20, 10, 0),
		FontWeight("Black-Italic", "Black", 3, 0x21, 10, -15),
		FontWeight("Bold", "Bold", 1, 0x20, 8, 0),
		FontWeight("Bold-Italic", "Bold", 3, 0x21, 8, -15),
		FontWeight("SemiBold", "Demi", 1, 0x20, 7, 0),
		FontWeight("SemiBold-Italic", "Demi", 3, 0x21, 7, -15),
		FontWeight("Light", "Light", 0, 0, 3, 0),
		FontWeight("Light-Italic", "Light", 2, 1, 3, -15),
		FontWeight("ExtraLight", "Extra-Light", 0, 0, 2, 0),
		FontWeight("ExtraLight-Italic", "Extra-Light", 2, 1, 2, -15),
	]

	for index, config in enumerate(font_weights):
		font = fontList[index]
		if font is not None:
			font.fontname = f"Monocraft{'-' + config.suffix if config.suffix else ''}"
			font.fullname = (
				f"Monocraft{' ' + config.suffix.replace('-', ' ') if config.suffix else ''}"
			)
			font.weight = config.weight
			font.macstyle = config.macstyle
			font.os2_stylemap = config.os2_stylemap
			# Update PANOSE weight value
			panose = list(font.os2_panose)
			panose[2] = int(config.panose_weight)
			font.os2_panose = tuple(panose)
			if config.italic_angle != 0:
				font.italicangle = config.italic_angle

	for character in characters:
		charactersByCodepoint[character["codepoint"]] = character
		image, kw = generatePixels(character)
		createGlyph(fontList, character["codepoint"], character["name"], image, **kw)

	print(f"Generated {len(characters)} characters")

	outputDir = "../dist/"
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)

	if output_ttc:
		fontList[0].generateTtc(
			outputDir + "Monocraft-no-ligatures.ttc",
			[i for i in fontList[1:] if i is not None],
			ttcflags=("merge",),
			layer=1,
		)

	for ligature in ligatures:
		image, kw = generatePixels(ligature)
		name = ligature["name"].translate(str.maketrans(" ", "_"))
		createGlyph(fontList, -1, name, image, **kw)
		for font in fontList:
			if font is None:
				continue
			lig = font[name]
			lig.addPosSub(
				"ligatures-subtable",
				tuple(
					map(
						lambda codepoint: charactersByCodepoint[codepoint]["name"],
						ligature["sequence"],
					)
				),
			)
			lig.addPosSub(
				"ligatures-exp-subtable",
				(
					name,
					*(
						charactersByCodepoint[32]["name"]
						for _ in range(len(ligature["sequence"]) - 1)
					),
				),
			)

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
			ttcflags=("merge",),
			layer=1,
		)


def generatePixels(character) -> tuple[PixelImage, dict]:
	image = PixelImage()
	kw = {}
	if "pixels" in character:
		arr = character["pixels"]
		leftMargin = character["leftMargin"] if "leftMargin" in character else 0
		x = math.floor(leftMargin)
		kw["dx"] = leftMargin - x
		descent = -character["descent"] if "descent" in character else 0
		y = math.floor(descent)
		kw["dy"] = descent - y
		image = image | imageFromArray(arr, x, y)

	if "reference" in character:
		other = generatePixels(charactersByCodepoint[character["reference"]])
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


def findHighestY(image: PixelImage) -> int:
	for y in range(image.y_end - 1, image.y, -1):
		for x in range(image.x, image.x_end):
			if image[x, y]:
				return y
	return image.y


def imageFromArray(arr, x=0, y=0) -> PixelImage:
	return PixelImage(
		x=x,
		y=y,
		width=len(arr[0]),
		height=len(arr),
		data=bytes(v for a in reversed(arr) for v in a),
	)


def drawPolygons(polygons, pen):
	for polygon in polygons:
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


def modifyStroke(p, stroke_mod):
	length = len(p)
	for i in range(length):
		x, y = p[i]
		dx, dy = 0, 0
		px, py = p[i - 1]
		if px < x:
			dy += stroke_mod
		elif px > x:
			dy -= stroke_mod
		elif py < y:
			dx -= stroke_mod
		else:
			dx += stroke_mod
		px, py = p[(i + 1) % length]
		if px < x:
			dy -= stroke_mod
		elif px > x:
			dy += stroke_mod
		elif py < y:
			dx += stroke_mod
		else:
			dx -= stroke_mod
		yield (dx + x, dy + y)


def createGlyph(
	fontList,
	code,
	name,
	image: PixelImage,
	*,
	width=None,
	dx=0,
	dy=0,
	glyphclass=None,
):
	base_polygons = [[(x + dx, y + dy) for x, y in p] for p in generatePolygons(image)]
	bold_polygons = None
	thin_polygons = None

	for font in fontList:
		if font is None:
			continue

		char = font.createChar(code, name)
		# char.manualHints = True
		if glyphclass is not None:
			char.glyphclass = glyphclass
		if image is None:
			char.width = width if width is not None else PIXEL_SIZE * 6
			continue

		polygons = base_polygons
		try:
			offset = WEIGHT_STROKE_OFFSETS[font.weight]
		except KeyError:
			offset = 0

		if offset > 0:
			if bold_polygons is None:
				bold_polygons = [
					[(x + dx, y + dy) for x, y in p]
					for p in generatePolygons(image, join_polygons=False)
				]
			polygons = (modifyStroke(p, offset) for p in bold_polygons)
		elif offset < 0:
			if thin_polygons is None:
				thin_polygons = [
					[(x + dx, y + dy) for x, y in p]
					for p in generatePolygons(image, join_polygons=False, exclude_corners=True)
				]
			polygons = (modifyStroke(p, offset) for p in thin_polygons)

		if font.macstyle & 2:
			polygons = (((x + y * ITALIC_RATIO, y) for x, y in p) for p in polygons)

		drawPolygons(polygons, char.glyphPen())
		char.width = width if width is not None else PIXEL_SIZE * 6


args = parseArgs()
generateFont(**vars(args))
generateExamples(characters, ligatures, charactersByCodepoint)
