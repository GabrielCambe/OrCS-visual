import time

class Animator():
    def __init__(self, *args, **kwargs):
        self.fps = kwargs.get("fps", 24)
        self.status = 'IDLE'

    def run(self):
        self.last_tick_time = time.time()
        while True:
            print("self.start_time: %s" % self.last_tick_time)
            self.last_tick_time = time.time()
            time.sleep(1/self.fps)
