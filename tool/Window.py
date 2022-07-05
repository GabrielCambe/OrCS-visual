# -*- coding: utf-8 -*-
import time
from pyglet.gl import *
from shapes.common import Triangle
from operator import add, sub

class FileReader:
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

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        print("__init__")
        super().__init__(*args,**kwargs)
        self.set_minimum_size(640, 360)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        self.shapes = {}
        self.file_reader = FileReader("/home/gabriel/Documentos/HiPES/OrCS-visual/tool/commands.txt")
        # self.file_reader = FileReader("/home/gabriel/Documents/OrCS-visual/tool/commands.txt")

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
            print(self.file_reader.current_line)
            
            current_line = self.file_reader.current_line.strip()

            if current_line == "spawn triangle as t1":
                self.shapes["triangle"] = Triangle()

            if current_line == "move t1 right":
                triangle = self.shapes.get("triangle", None)
                if triangle:
                    # TODO aqui você troca o estado do  animator do shape para "MOVING" pois essa função deve retornar antes de on_draw ser chamado
                    triangle.move_right(duration=1)
                    
                    if triangle.animation:
                        if triangle.animation["duration"] > 0:
                            while triangle.animation["frames_until_idle"] > 0:
                                triangle.animation["frames_until_idle"] = triangle.animation["frames_until_idle"] - 1
                                time.sleep(triangle.animator.frame_duration)
                                triangle.update_points(add, triangle.animation["delta_vector"])
                                self.dispatch_event('on_draw')
                        triangle.animation = None

#                         def update(dt):
#     # ...
# pyglet.clock.schedule_interval(update, 0.1)


            if current_line == "move t1 left":
                triangle = self.shapes.get("triangle", None)
                if triangle:
                    triangle.move_left()

            if current_line == "delete t1":
                self.shapes["triangle"] = None

            if current_line == "":
                self.close()

        elif symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        pass
