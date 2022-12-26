# This program is free software:
# you can redistribute it and/or modify it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation; 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. 
# If not, see https://www.gnu.org/licenses/. 

import json
#load pre set data
characters = json.load(open("./characters.json"))
diacriticsJson = json.load(open("./diacritics.json"))

#Create dictionaries for faster lookup
charactersDic = {}
diacritics = {}
for c in characters:
    charactersDic[c["name"]] = c["codepoint"]
for d in diacriticsJson:
    diacritics[d] = 0

#List to store generated dictionary
charList = []

#Parse the text file
lines = open("./UnicodeData.txt").readlines()
for line in lines:
    #find all line with a WITH in them
    if not "WITH" in line:
        continue
    #Get the diacritic name
    spl = line.split("WITH")
    diacritic = spl[1].split(';')[0].strip().lower()
    name = spl[0].split(';')[1].strip().lower()
    if not diacritic.lower() in diacritics:continue
    #Getting reference to the original characters
    reference = 0
    if name.split(" ")[0] == "latin":
        spl1 = name.split("letter")
        letter = spl1[1].strip()
    if name.split(" ")[0] == "latin" and len(letter) == 1:
        case = spl1[0].split(" ")[-2].strip()
        reference = ord(letter)
        if case == "capital":
            reference = ord(letter.capitalize())
    else:
        if not name in charactersDic:continue
        reference = charactersDic[name]
    codepoint = int(line.split(";")[0].strip(),16)

    #Store in a dictionary for serialization
    char = {}
    char["character"] = chr(codepoint)
    char["name"] = name + " with " + diacritic
    char["codepoint"] = codepoint
    char["reference"] = reference
    char["diacritic"] = diacritic
    char["diacriticSpace"] = 1
    charList.append(char)
i = 0
for c in charList:
    if c["name"] in charactersDic:continue
    i+=1
    characters.append(c)
print("Added " + str(i) + " new characters")
with open("full_characters.json","w") as file:
    j = json.dump(characters,file,ensure_ascii=False,indent='\t')
