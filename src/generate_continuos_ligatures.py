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


def generate_continous_ligatures(filename):
    """
    Generates continuos ligature data from a JSON file.

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
    data = json.load(open(filename))
    out = []
    for d in data:
        name = f'{d["head_name"]} {d["body_name"]} '
        body_pixels = d["body_pixels"]
        head_pixels = d["head_pixels"]
        body = [[] for _ in  range(len(body_pixels))] # copy.deepcopy(body_pixels)
        for i in range( d["min_length"],d["max_length"] + 1):
            o = {}
            #generate ligature data
            o["name"] = name + str(i); 
            if d["direction"] == "right":
                o["ligature"] = d["body"] * i +d["head"]
            else:
                o["ligature"] = d["head"] + d["body"] * i
            o["sequence"] = [ord(c) for c in o["ligature"]]
            #generate pixels
            #expand the body by 1
            for k in range(len(body)):
                body[k] += body_pixels[k]
            pixels = []
            if d["direction"] == "right":
                pixels = copy.deepcopy(body)
                for j in range(len(pixels)):
                    pixels[j] += head_pixels[j]
            else:
                pixels = copy.deepcopy(head_pixels)
                for j in range(len(pixels)):
                    pixels[j] += body[j]
            o["pixels"] = pixels
            out.append(o)
    return out
