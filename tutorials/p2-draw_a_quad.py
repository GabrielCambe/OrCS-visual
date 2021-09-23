from pyglet.gl import *
from shapes.common import Triangle, Quad, Quad2

class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.set_minimum_size(640, 360)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        self.quad = Quad()
        self.quad2 = Quad2()

    def on_draw(self):
        self.clear()
        # self.quad.shape.draw(GL_TRIANGLES)
        self.quad2.render()


    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

if __name__ == "__main__":
    window = MyWindow(640, 360, "MyWindow", resizable=True)
    pyglet.app.run()