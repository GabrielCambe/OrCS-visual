# -*- coding: utf-8 -*-
import time
from operator import add, sub
import pyglet
from pyglet.gl import *

class FileReader():
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_line = ''
        self.open_file()

    def open_file(self):
        self.file = open(self.file_path, 'r')

    def get_line(self):
        self.current_line = self.file.readline()
        if self.current_line == '':
            return None
        else:
            return self.current_line

    def close_file(self):
        self.file.close()

class AnimationControler():
    def __init__(self, *args, **kwargs):
        self.fps = kwargs.get("fps", 24)
        self.frame_duration = 1.0/self.fps
        self.animation = None
        self.run_animation = None

    def get_number_of_frames(self, duration):
        return int(duration * self.fps)

class Triangle():
    def __init__(self):
        # anti-clockwise beginning on lower-left side
        self.points = [
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.0, 0.5, 0.0]
        ]

        # RGB ~ 0-255
        self.colors = [
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255]
        ]
        
        self.vertices = pyglet.graphics.vertex_list(
            3,
            ('v3f', sum(self.points, [])),
            ('c3B', sum(self.colors, []))
        )

        self.animator = AnimationControler()
    
    def set_points(self, points):
        self.points = points
        self.vertices = pyglet.graphics.vertex_list(
            3,
            ('v3f', sum(self.points, [])),
            ('c3B', sum(self.colors, []))
        )

    def update_points(self, operation, delta_vector):
        new_points = [ list( map(operation, point, delta_vector) ) for point in self.points]
        self.set_points(new_points)

    def move(self, operation, delta, duration):
        if duration == 0:
            move_vector = [delta, 0, 0]
            self.update_points(operation, move_vector)
        else:
            number_of_frames = self.animator.get_number_of_frames(duration)
            partial_delta = delta / number_of_frames
            delta_vector = [partial_delta, 0, 0]

            self.animator.animation = {
                "delta_vector": delta_vector,
                "number_of_frames": number_of_frames
            }

            def update(dt):
                self.update_points(operation, self.animator.animation["delta_vector"])
                self.animator.animation["number_of_frames"] = self.animator.animation["number_of_frames"] - 1
                if self.animator.animation["number_of_frames"] == 0:
                    self.animator.animation = None
                    pyglet.clock.unschedule(update)

            pyglet.clock.schedule_interval(update, self.animator.frame_duration)

    def move_right(self, delta=0.5, duration=0):
        self.move(add, delta, duration)

    def move_left(self, delta=0.5, duration=0):
        self.move(sub, delta, duration)

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.set_minimum_size(640, 360)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        self.shapes = {}
        self.file_reader = FileReader("/home/gabriel/Documentos/HiPES/OrCS-visual/commands.txt")
        # self.file_reader = FileReader("/home/gabriel/Documents/OrCS-visual/tool/commands.txt")

    def run(self):
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        shape = self.shapes.get("triangle", None)
        if shape:
            shape.vertices.draw(GL_TRIANGLES)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.RIGHT:
            self.file_reader.get_line()
            
            current_line = self.file_reader.current_line.strip()

            if current_line == "spawn triangle as t1":
                self.shapes["triangle"] = Triangle()

            elif current_line == "move t1 right":
                triangle = self.shapes.get("triangle", None)
                if triangle:
                    triangle.move_right(duration=0.5)

            elif current_line == "move t1 left":
                triangle = self.shapes.get("triangle", None)
                if triangle:
                    triangle.move_left(duration=0.5)

            elif current_line == "delete t1":
                self.shapes["triangle"] = None

            elif current_line == "":
                self.close()

        elif symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        pass

if __name__ == "__main__":
    window = Window(
        640, 360, 
        "OrCS-visual", 
        resizable=True
    )
    window.run()