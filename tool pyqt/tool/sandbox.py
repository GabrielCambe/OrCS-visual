from PyQt5 import QtWidgets, QtGui, QtCore

window = QtWidgets.QWidget()
button1 = QtWidgets.QPushButton("One")
button2 = QtWidgets.QPushButton("Two")
button3 = QtWidgets.QPushButton("Three")
button4 = QtWidgets.QPushButton("Four")
button5 = QtWidgets.QPushButton("Five")

layout = QtWidgets.QHBoxLayout()
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(button3)
layout.addWidget(button4)
layout.addWidget(button5)

window.setLayout(layout)
window.show()