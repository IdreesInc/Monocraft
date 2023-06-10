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

import json
import copy


def generate_continuous_ligatures(filename):
    """
    Generates continuous ligature data from a JSON file.

    The JSON file should have the following structure:
    [
        {
            "head_name": "string",
            "body_name": "string",
            "head": "string",
            "body": "string",
            "direction": "left" or "right",
            "min_length": int,
            "max_length": int,
            "head_pixels": [[int, int, ...], ...],
            "body_pixels": [[int, int, ...], ...]
        },
        ...
    ]

    Returns a list of progress bars, where each progress bar is a dictionary with the following keys:
    - "name": a string representing the name of the progress bar
    - "ligature": a string representing the progress bar
    - "sequence": a list of integers representing the Unicode code points of the characters in the progress bar
    - "pixels": a list of integers representing the pixels of the progress bar
    """
    continuous_ligatures = json.load(open(filename))
    out = []
    for ligature in continuous_ligatures:
        name = f'{ligature["head_name"]} {ligature["body_name"]} '
        body_pixels = ligature["body_pixels"]
        head_pixels = ligature["head_pixels"]
        body = [[] for _ in  range(len(body_pixels))]
        for i in range( ligature["min_length"],ligature["max_length"] + 1):
            glyph = {}
            # Generate ligature data
            glyph["name"] = name + str(i); 
            if ligature["direction"] == "right":
                glyph["ligature"] = ligature["body"] * i + ligature["head"]
            else:
                glyph["ligature"] = ligature["head"] + ligature["body"] * i
            glyph["sequence"] = [ord(c) for c in glyph["ligature"]]
            # Generate pixels
            # Expand the body by 1
            for k in range(len(body)):
                body[k] += body_pixels[k]
            pixels = []
            if ligature["direction"] == "right":
                pixels = copy.deepcopy(body)
                for j in range(len(pixels)):
                    pixels[j] += head_pixels[j]
            else:
                pixels = copy.deepcopy(head_pixels)
                for j in range(len(pixels)):
                    pixels[j] += body[j]
            glyph["pixels"] = pixels
            out.append(glyph)
    return out
