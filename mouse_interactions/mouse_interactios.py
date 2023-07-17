from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5 import QtWidgets, uic
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('main_window.ui', self)  # Load the .ui file

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.findChild(QHBoxLayout, 'horizontalLayout_figure').addWidget(self.canvas)

        self.figure.clear()
        self.ax = self.figure.add_subplot(1, 1, 1)  # keep reference to the Axes object
        self.ax.imshow(np.random.rand(50,50))
        self.canvas.draw()

        self.canvas.mpl_connect('button_press_event', self.mousePress)
        self.canvas.mpl_connect('button_release_event', self.mouseRelease)
        self.canvas.mpl_connect('motion_notify_event', self.mouseMove)

        self.drawing_line = False  # flag to keep track of whether we're currently drawing a line
        self.current_line = None  # the Line2D object of the line currently being drawn

        self.show()

    def mousePress(self, event):
        # If right button is pressed, start drawing a line
        if event.button == 3 and event.inaxes == self.ax:  # 3 is the right button
            self.drawing_line = True
            self.current_line, = self.ax.plot([event.xdata], [event.ydata], color='b')  # start the line at the click position
        # If left button is pressed, add an asterisk
        elif event.button == 1 and event.inaxes == self.ax:  # 1 is the left button
            self.ax.plot(event.xdata, event.ydata, 'b*')  # 'b*' makes the point blue and star-shaped
            self.canvas.draw()  # redraw the canvas to show the new point

    def mouseRelease(self, event):
        # stop drawing when the right button is released
        if event.button == 3 and self.drawing_line:
            self.drawing_line = False
            self.current_line = None
            self.canvas.draw()  # redraw the canvas to show the completed line

    def mouseMove(self, event):
        # add a point to the line when the mouse is moved
        if self.drawing_line and event.inaxes == self.ax:
            xdata, ydata = self.current_line.get_data()
            xdata = xdata.tolist()
            ydata = ydata.tolist()
            xdata.append(event.xdata)
            ydata.append(event.ydata)
            self.current_line.set_data(np.array(xdata), np.array(ydata))
            self.canvas.draw_idle()  # update the canvas without forcing an immediate redraw
        

        
        

app = QtWidgets.QApplication(sys.argv)
window = Ui() 
app.exec_()

