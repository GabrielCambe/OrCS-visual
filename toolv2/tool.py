# -*- coding: utf-8 -*-
import pygame
import time
from operator import add, sub

ANIMATION_EVENT = pygame.event.custom_type()

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

    def get_number_of_frames(self, duration):
        return int(duration * self.fps)

class Triangle():
    def __init__(self):
        # anti-clockwise beginning on top side
        self.points = [[100, 100], [0, 200], [200, 200]]

        # RGB ~ 0-255
        self.color = (255, 255, 255)

        # 0 -> Filled shape
        self.line_thickness = 0
        
        self.animator = AnimationControler()

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.points, self.line_thickness)
   
    def set_points(self, points):
        self.points = points

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

            animation_event = pygame.event.Event(ANIMATION_EVENT, {
                "delta_vector": delta_vector,
                "operation": operation,
                "shape": self,
            })
            frame_duration_millis = int(self.animator.frame_duration * 1000)
            pygame.time.set_timer(animation_event, frame_duration_millis, loops=number_of_frames)

    def move_right(self, delta=200, duration=0):
        self.move(add, delta, duration)

    def move_left(self, delta=200, duration=0):
        self.move(sub, delta, duration)

class Window():
    def __init__(self, *args, **kwargs):
        self.title = kwargs["title"]
        self.width, self.height = (kwargs["width"], kwargs["height"])
        self.background_color = (127,127,127)
        self.running = False

        self.shapes = {}
        self.file_reader = FileReader("/home/gabriel/Documentos/HiPES/OrCS-visual/tool/commands.txt")
        # self.file_reader = FileReader("/home/gabriel/Documents/OrCS-visual/tool/commands.txt")


    def clear(self):
        self.screen.fill(self.background_color)

    def run(self):
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clear()
        self.running = True

        while self.running:
            self.handle_draw()
            event = pygame.event.wait()
            self.handle_event(event)

    def handle_draw(self):
        self.clear()
        shape = self.shapes.get("triangle", None)
        if shape:
            shape.draw(self.screen)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.close()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.file_reader.get_line()
                
                current_line = self.file_reader.current_line.strip()

                if current_line == "spawn triangle as t1":
                    self.shapes["triangle"] = Triangle()

                if current_line == "move t1 right":
                    triangle = self.shapes.get("triangle", None)
                    if triangle:
                        triangle.move_right(duration=0.5)

                if current_line == "move t1 left":
                    triangle = self.shapes.get("triangle", None)
                    if triangle:
                        triangle.move_left(duration=0.5)

                elif current_line == "delete t1":
                    self.shapes["triangle"] = None

                elif current_line == "":
                    self.close()

            elif event.key == pygame.K_ESCAPE:
                self.close()

        elif event.type == ANIMATION_EVENT:
            event.shape.update_points(event.operation, event.delta_vector)
            self.handle_draw()

    def close(self):
        pygame.quit()
        self.running = False

if __name__ == "__main__":
    pygame.init()

    window = Window(
        width=640,
        height=360, 
        title="OrCS-visual", 
    )    
    window.run()
