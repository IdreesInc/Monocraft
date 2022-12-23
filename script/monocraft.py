import fontforge

print("hi")

# monocraft = fontforge.open("./base.sfd")
monocraft = fontforge.font()
monocraft.fontname = "Monocraft Generated"
monocraft.createChar(65, "A")
pen = monocraft["A"].glyphPen()
pen.moveTo((100,100))
pen.lineTo((100,200))
pen.lineTo((200,200))
pen.lineTo((200,100))
pen.closePath()
print(monocraft["A"].width)
monocraft.generate("generated.ttf")