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

def generateExamples(characters, ligatures, charactersByCodepoint):
	terminalOutput = 26*"-" + " Monocraft " + 26*"-"
	index = 0
	for character in characters:
		if character["codepoint"] == 32:
			continue
		if index % 32 == 0:
			terminalOutput += "\n"
		terminalOutput += chr(character["codepoint"]) + " "
		index += 1

	print(terminalOutput)

	characterOutput = "--- Monocraft ---\n\n"
	for i in range(65, 91):
		characterOutput += chr(i) + " "
	characterOutput += "\n"
	for i in range(97, 123):
		characterOutput += chr(i) + " "
	characterOutput += "\n"*2
	for i in range(48, 58):
		characterOutput += chr(i) + " "
	characterOutput += "\n"*2
	for i in range(33, 48):
		characterOutput += chr(i) + " "
	for i in range(58, 65):
		characterOutput += chr(i) + " "
	for i in range(91, 97):
		characterOutput += chr(i) + " "
	for i in range(123, 127):
		characterOutput += chr(i) + " "
	index = 0
	for i in range(161, 65534):
		if i == 382 or i == 1120 or i == 8363:
			index = 0
			characterOutput += "\n"
		if i in charactersByCodepoint:
			if index % 32 == 0:
				characterOutput += "\n"
			characterOutput += chr(i) + " "
			index += 1

	ligatureOutput = "--- Ligatures ---"
	for ligature in ligatures:
		start = ''.join(map(lambda codepoint: ' ' + chr(codepoint), ligature['sequence']))
		start += (7 - len(ligature['sequence'])) * " "
		output = 5 * " " + ''.join(map(lambda codepoint: chr(codepoint), ligature['sequence']))
		ligatureOutput += "\n" + start + "->" + output

	f = open("../examples/glyphs.txt", "w")
	f.write(characterOutput + 2*"\n" + ligatureOutput)
	f.close()