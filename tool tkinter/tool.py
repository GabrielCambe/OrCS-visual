# -*- coding: utf-8 -*-
import tkinter as tk
import time
from operator import add, sub

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
    def __init__(self, canvas):

        # anti-clockwise starting from the top
        self.points = [
            50, 0,
            0, 100,
            100, 100
        ]

        # RGB ~ "#HexHexHex"
        self.color = "#FFFFFF"
        
        self.animator = AnimationControler()

        self.canvas = canvas
        self.shape = self.canvas.create_polygon(self.points, fill=self.color, 
        tags="triangle"
        )

    def move(self, root, delta, duration):
        if duration == 0:
            inc_vector = (delta, 0)
            root.canvas.move(self.shape, *inc_vector)
            root.window.update()
            # time.sleep(Refresh_Sec)
        else:
            number_of_frames = self.animator.get_number_of_frames(duration)
            partial_delta = delta / number_of_frames
            inc_vector = (partial_delta, 0)

            while number_of_frames > 0:
                root.canvas.move(self.shape, *inc_vector)
                root.window.update()
                time.sleep(self.animator.frame_duration)
                number_of_frames = number_of_frames - 1

    def move_right(self, root, delta=200, duration=0):
        self.move(root, delta, duration)

    def move_left(self, root, delta=-200, duration=0):
        self.move(root, delta, duration)

    def draw(self, canvas):
        self.shape = canvas.create_polygon(self.points, fill=self.color, 
        tags="triangle"
        )

class Window():
    def __init__(self, *args, **kwargs):
        self.window = tk.Tk()
        self.window.title(kwargs.get('title'))
        
        self.offset_x = kwargs.get('offset_x', 0)
        self.offset_y = kwargs.get('offset_y', 0)
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.window.geometry('%sx%s+%s+%s' % (self.width, self.height, self.offset_x, self.offset_y))

        # Binding handle function to key event 
        self.window.bind('<KeyPress>', self.handle_key_press)
  
        self.color = "#7E7E7E"
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg=self.color)
        self.canvas.pack()

        self.shapes = {}
        self.file_reader = FileReader("/home/gabriel/Documentos/HiPES/OrCS-visual/commands.txt")
        # self.file_reader = FileReader("/home/gabriel/Documents/OrCS-visual/tool/commands.txt")

        self.running = False

    def clear(self):
        self.canvas.delete("all")

    def run(self):
        self.running = True

        while self.running:
            self.window.update_idletasks()
            self.window.update()

    def handle_key_press(self, event):
        if event.keysym == "Right":
            self.file_reader.get_line()
                
            current_line = self.file_reader.current_line.strip()
            print(current_line)

            if current_line == "spawn triangle as t1":
                self.shapes["triangle"] = Triangle(self.canvas)

            if current_line == "move t1 right":
                triangle = self.shapes.get("triangle", None)
                if triangle:
                    triangle.move_right(self, duration=.5)

            if current_line == "move t1 left":
                triangle = self.shapes.get("triangle", None)
                if triangle:
                    triangle.move_left(self, duration=.5)

            elif current_line == "delete t1":
                self.shapes["triangle"] = None
                self.canvas.delete("triangle")

            elif current_line == "":
                self.close()

        elif event.keysym == "Escape":
            self.close()

    def close(self):
        self.window.destroy()
        self.running = False

if __name__ == "__main__":
    window = Window(
        width=640, height=360, 
        title="OrCS-visual", 
        resizable=True
    )
    window.run()

