from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QFileDialog
from PyQt5 import QtWidgets, uic
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from skimage.draw import disk


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('main_window.ui', self)  # Load the .ui file

        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.findChild(QHBoxLayout, 'horizontalLayout_figure').addWidget(self.canvas)
        
        self.canvas.mpl_connect('button_press_event', self.mousePress)
        self.canvas.mpl_connect('button_release_event', self.mouseRelease)
        self.canvas.mpl_connect('motion_notify_event', self.mouseMove)

        self.findChild(QtWidgets.QPushButton, 'pushButton_load_img').clicked.connect(self.pushButton_load_img_clicked)
        self.findChild(QtWidgets.QPushButton, 'pushButton_save_img').clicked.connect(self.pushButton_save_img_clicked)
        
        self.spinBox_brush_size = self.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        
        self.img = None  # holds the loaded image
        self.drawing = False  # flag for when the left mouse button is pressed
        self.preview_circle = None  # circle patch for previewing the brush size

        self.show()

    def pushButton_load_img_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File")
        if file_name:
            self.img = io.imread(file_name)
            self.ax.imshow(self.img)
            self.canvas.draw()

    def pushButton_save_img_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image File")
        if file_name and self.img is not None:
            io.imsave(file_name, self.img)
    
    def mousePress(self, event):
        if event.button == 1 and event.inaxes == self.ax:  # left mouse button
            self.drawing = True
            self.draw_circle(event)

    def mouseRelease(self, event):
        if event.button == 1 and self.drawing:  # left mouse button
            self.drawing = False

    def mouseMove(self, event):
        # add a circle preview when hovering
        if event.inaxes == self.ax:
            if self.preview_circle is not None:
                self.preview_circle.remove()  # remove the old preview circle
            self.preview_circle = Circle((event.xdata, event.ydata), self.spinBox_brush_size.value(), fill=False, edgecolor='lightpink')
            self.ax.add_patch(self.preview_circle)
            self.canvas.draw()

            # draw the circle when mouse is pressed and moving
            if self.drawing:
                self.draw_circle(event)

    def draw_circle(self, event):
        brush_radius = self.spinBox_brush_size.value()
        rr, cc = disk((event.ydata, event.xdata), brush_radius, shape=self.img.shape)
        self.img[rr, cc] = 0  # change this to modify the color of the brush
        if self.ax.images:
            self.ax.images[-1].remove()  # remove the old image
        self.ax.imshow(self.img)  # display the new image
        self.canvas.draw()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()