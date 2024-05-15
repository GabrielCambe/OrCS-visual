import argparse
import sys
from PyQt5 import QtWidgets

from models.Window import Visualizer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='OrCViz - Ordinary Computer Visualizator.'
    )
    parser.add_argument('-t', '--trace', dest='trace')
    parser.add_argument('-o', '--plot_name', dest='plot_name')
    parser.add_argument('-p', '--play', dest='play', action='store_true')
    parser.add_argument('-x', '--exit', dest='exit', action='store_true')
    parser.add_argument('-s', '--show', dest='histogram', action='store_true')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    orcs_visualizer = Visualizer(
        title='OrCViz', 
        trace=args.trace, 
        plot_name=args.plot_name,
        skip_exit_confirmation=args.exit,
        play= args.play,
        show_histogram= args.histogram 
    )
    orcs_visualizer.showMaximized()
    sys.exit(app.exec_())
