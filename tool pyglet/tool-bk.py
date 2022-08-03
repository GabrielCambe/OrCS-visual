import argparse

from Window import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reads a file and prints its content.')
    parser.add_argument('-f', '--file_path', help='The path to the file to read.')

    args = parser.parse_args()

    window = Window(
        640, 360, 
        "MyWindow", 
        resizable=True
    )
    
    pyglet.app.run()
    