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


def generate_progress_bars(file):
    #json structure:
    #Charecter definition + direction, specifies what the progress bar is made of
        #head string
        #body string
        #head_name string
        #body_name
        #direction : "left"/right
    #Length definition 
        #min_length int: Minimum number of body chars needed for it to be considered a progress bar
        #max_length int: We can't add infinite number of ligatures, so we cap it with this
    #Pixel definition, pretty self explanatory
        #head_pixels
        #body_pixels
    data = json.load(open(file))
    out = []
    for d in data:
        name = d["head_name"] + " " + d["body_name"] + " "
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
            body = d["body_pixels"]
            for j in range(i):
                #print(len(body))
                for k in range(len(body)):
                    #print(f'len(body) = {len(body)} len(d[\"body\"]) = {len(d["body"])} k = {k}')
                    body[k] += d["body_pixels"][k]
            if d["direction"] == "right":
                o["pixels"] = body
                for j in range(len(o["pixels"])):
                    o["pixels"][j] += d["head_pixels"][j]
            else:
                o["pixels"] = d["head_pixels"]
                for j in range(len(o["pixels"])):
                    o["pixels"][j] += body[j]
            out.append(o)
    return out;

