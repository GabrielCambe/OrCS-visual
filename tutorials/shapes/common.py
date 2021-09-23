from pyglet.gl import *

class Triangle():
    def __init__(self):
        self.vertices = pyglet.graphics.vertex_list(
            3,
            ('v3f', [-0.5,-0.5,0.0, 0.5,-0.5,0.0, 0.0,0.5,0.0]),
            ('c3B', [100,200,220, 200,110,100, 100,250,100])
        )

class Quad():
    def __init__(self):
        self.indexes = [0,1,2, 2,3,0]
        self.vertices = ('v3f', [-0.5,-0.5,0.0] + [0.5,-0.5,0.0] + [0.5,0.5,0.0] + [-0.5,0.5,0.0])
        self.colors = ('c3f', [1.0,0.0,0.0] + [0.0,1.0,0.0] + [0.0,0.0,1.0] + [1.0,1.0,1.0])

        self.shape = pyglet.graphics.vertex_list_indexed(
            4,
            self.indexes,
            self.vertices,
            self.colors
        )

class Quad2():
    def __init__(self):
        self.indexes = [0,1,2, 2,3,0]
        self.vertices = ('v3f', [-0.5,-0.5,0.0] + [0.5,-0.5,0.0] + [0.5,0.5,0.0] + [-0.5,0.5,0.0])
        self.colors = ('c3f', [1.0,0.0,0.0] + [0.0,1.0,0.0] + [0.0,0.0,1.0] + [1.0,1.0,1.0])

    def render(self):
        pyglet.graphics.draw_indexed(
            4,
            GL_TRIANGLES,
            self.indexes,
            self.vertices,
            self.colors
        )
