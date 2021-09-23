#!/usr/bin/python3
import pyglet
from pyglet import shapes

window = pyglet.window.Window(width=1120, height=640, caption='window', )
pyglet.gl.glClearColor(1,1,1,1)

labelArgs = {
    'color': (0, 0 , 0, 255),
    'font_name': 'Times New Roman',
    'font_size': 15,
    'x': window.width//2,
    'y': window.height//2,
    'anchor_x': 'center',
    'anchor_y': 'center'
}


class Processor():
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.rectangle = shapes.BorderedRectangle(x=250, y=300, width=400, height=200, border=1, color=(255, 22, 20), batch=self.batch)

    def draw(self):
        self.batch.draw()

processor = Processor()

cursors = [0]
cursorIdx = 0
with open("../OrCS/debug_output.txt", "r") as output:
    output.seek(cursors[cursorIdx])
    line = output.readline()
    label = pyglet.text.Label(line, **labelArgs)
    cursors.append(output.tell())
    

@window.event
def on_draw():
    window.clear()
    # processor.draw()
    label.draw()

@window.event
def on_key_press(symbol, modifiers):
    global cursors
    global label
    global cursorIdx

    with open("../OrCS/debug_output.txt", "r") as output:
        if symbol == pyglet.window.key.RIGHT:
            cursorIdx += 1
            output.seek(cursors[cursorIdx])
            line = output.readline()
            cursors.append(output.tell())
        
        elif symbol == pyglet.window.key.LEFT:
            cursorIdx -= 1
            output.seek(cursors[cursorIdx])
            line = output.readline()
            cursors.append(output.tell())

        label = pyglet.text.Label(line, **labelArgs)

pyglet.app.run()
