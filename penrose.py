#!python3
# Penrose tiling (P2, P3) generator
# Info:
#   https://en.wikipedia.org/wiki/Penrose_tiling
#   https://tartarus.org/~simon/20110412-penrose/penrose.xhtml
# Daniel Wen

import math
from tkinter import *

# Golden ratio
PHI = (math.sqrt(5) - 1) / 2

# Return point that is phi of the way between given points
def goldenMidpoint(A, B):
    (x1, y1), (x2, y2) = (A, B)
    (dx, dy) = (x2 - x1, y2 - y1)
    return (x1 + PHI*dx, y1 + PHI*dy)


class Isoceles(object):
    # Create isoceles triangle given 3 vertices
    def __init__(self, apex, vertex1, vertex2):
        self.apex = apex
        self.vertex1 = vertex1
        self.vertex2 = vertex2

    # Fill interior of triangle
    def draw(self, canvas):
        canvas.create_polygon(self.apex, self.vertex1, self.vertex2,
            fill=self.color)

class KiteDart(Isoceles):
    lineColor = "#555555"

    @staticmethod
    # Create half kite given position and leg length
    def initialTiles(cx, cy, length):
        (cx, cy) = (cx * 2//5, cy * 2//5)
        (left, right) = (cx - length/2, cx + length/2)

        midX = left + length * math.cos(math.pi / 5)
        height = length * math.sin(math.pi / 5)

        (top, bottom) = (cy - height/2, cy + height/2)

        return [Kite((left, bottom), (midX, top), (right, bottom))]

    # Draw extra line to fill gaps between triangles
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_line(self.apex, self.vertex2, width=2, fill=self.color)

    # Draw tile outline
    def drawLines(self, canvas):
        canvas.create_line(self.apex, self.vertex1, self.vertex2, width=1,
            capstyle="round", fill=self.lineColor)

class Kite(KiteDart):
    color = "white"

    # Increase depth of half-kite according to substitution rules
    def deflate(self):
        newPoint1 = goldenMidpoint(self.vertex1, self.apex)
        newPoint2 = goldenMidpoint(self.apex, self.vertex2)

        dart = Dart(newPoint1, newPoint2, self.apex)
        kite1 = Kite(self.vertex1, newPoint1, newPoint2)
        kite2 = Kite(self.vertex1, self.vertex2, newPoint2)

        return dart, kite1, kite2

class Dart(KiteDart):
    color = "#71DCFC"

    # Increase depth of half-dart according to substitution rules
    def deflate(self):
        newPoint = goldenMidpoint(self.vertex2, self.vertex1)

        kite = Kite(self.vertex2, newPoint, self.apex)
        dart = Dart(newPoint, self.apex, self.vertex1)

        return kite, dart

class Rhomb(Isoceles):
    lineColor = "#1C140D"

    @staticmethod
    # Create acute Robinson triangle given position and leg length
    def initialTiles(cx, cy, length):
        cx = cx * 2 // 5
        width = length * math.sin(2 * math.pi / 5)
        height = length * PHI

        (left, right) = (cx - width/2, cx + width/2)
        (top, bottom) = (cy - height/2, cy + height/2)

        return [Acute((left, cy), (right, top), (right, bottom))]

    # Draw extra line to fill gaps between triangles
    def draw(self, canvas):
        super().draw(canvas)
        canvas.create_line(self.vertex1, self.vertex2, width=2, fill=self.color)

    # Draw tile outline
    def drawLines(self, canvas):
        canvas.create_line(self.vertex1, self.apex, self.vertex2, width=1,
            capstyle="round", fill=self.lineColor)

class Acute(Rhomb):
    color = "#CBE86B"

    # Increase depth of acute Robinson triangle according to substitution rules
    def deflate(self):
        newPoint = goldenMidpoint(self.apex, self.vertex1)

        obtuse = Obtuse(newPoint, self.vertex2, self.apex)
        acute = Acute(self.vertex2, newPoint, self.vertex1)

        return obtuse, acute

class Obtuse(Rhomb):
    color = "white"

    # Increase depth of obtuse Robinson triangle according to substitution rules
    def deflate(self):
        newPoint1 = goldenMidpoint(self.vertex1, self.apex)
        newPoint2 = goldenMidpoint(self.vertex1, self.vertex2)

        obtuse1 = Obtuse(newPoint1, newPoint2, self.vertex1)
        acute = Acute(newPoint2, newPoint1, self.apex)
        obtuse2 = Obtuse(newPoint2, self.vertex2, self.apex)

        return obtuse1, acute, obtuse2


# Initialize
def init(data):
    data.tiles = []
    data.tileType = "Rhombs"
    data.baseLength = 30
    data.depth = 0

    refreshTiles(data)

# Increase depth of all tiles in data.tiles
def deflateTiles(data):
    newTiles = []
    for tile in data.tiles:
        newTiles.extend(tile.deflate())
    data.tiles = newTiles

# Generate tiling with depth specified by data.depth
def refreshTiles(data):
    (cx, cy) = (data.width // 2, data.height // 2)
    initialLength = data.baseLength / PHI**data.depth

    if data.tileType == "Kite & Dart":
        data.tiles = KiteDart.initialTiles(cx, cy, initialLength)
    elif data.tileType == "Rhombs":
        data.tiles = Rhomb.initialTiles(cx, cy, initialLength)

    for _ in range(data.depth):
        deflateTiles(data)

def keyPressed(event, data):
    # Change depth
    if event.keysym == "Up":
        data.depth += 1
        refreshTiles(data)
    elif event.keysym == "Down":
        if data.depth > 0:
            data.depth -= 1
            refreshTiles(data)
    # Change tile type
    elif event.keysym == "Tab":
        data.tileType = "Kite & Dart" if data.tileType == "Rhombs" else "Rhombs"
        refreshTiles(data)

def mousePressed(event, data):
    pass

def timerFired(data):
    pass

def redrawAll(canvas, data):
    # Draw tiles
    for tile in data.tiles:
        tile.draw(canvas)
    for tile in data.tiles:
        tile.drawLines(canvas)

    # Create text
    text = "Tile type: %s  |  Depth: %d" % (data.tileType, data.depth)
    canvas.create_text(data.width // 2, 10, anchor="n", text=text)
    info = "Press Up, Down or Tab"
    canvas.create_text(data.width // 2, data.height - 10, anchor="s", text=info)


# MVC framework from https://www.cs.cmu.edu/~112/notes/events-example0.py
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 10000 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800, 500)
