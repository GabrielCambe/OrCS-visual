from pyglet.gl import *
from operator import add, sub
import time

class AnimationControler():
    def __init__(self, *args, **kwargs):
        self.fps = kwargs.get("fps", 24)
        self.status = 'IDLE'
        self.frames_until_idle = 0
        self.frame_duration = 1.0/self.fps

    def get_number_of_frames(self, duration):
        return int(duration * self.fps)
    
    def sleep(self):
        self.last_frame_time = time.time()
        self.frames_until_idle = self.frames_until_idle - 1
        time.sleep(self.frame_duration)

    def run(self, duration=0, callback=lambda : None):
        self.last_frame_time = time.time()

        if duration > 0:
            self.frames_until_idle = int(duration / self.frame_duration)
            while self.frames_until_idle > 0:
                self.sleep()
                callback()

# TODO: deixar representação das formas separadas dos objetos necessários para sua renderização
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
        self.animation = None
    
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

    def move_right(self, delta=0.5, duration=0):
        if duration == 0:
            move_vector = [delta, 0, 0]
            self.update_points(add, move_vector)
        else:
            number_of_frames = self.animator.get_number_of_frames(duration)
            delta = delta / number_of_frames
            delta_vector = [delta, 0, 0]

            self.animation = {
                "duration": duration,
                "delta_vector": delta_vector,
                "frames_until_idle": int(duration / self.animator.frame_duration)
            }
        
    def move_left(self, delta=0.5, duration=0):
        if duration == 0:
            move_vector = [delta, 0, 0]
            self.update_points(sub, move_vector)


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
