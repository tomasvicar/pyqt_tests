from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QFileDialog
from PyQt5 import QtWidgets, uic
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
from skimage import io, morphology
from skimage.morphology import disk
from skimage.draw import line
from skimage.color import rgb2gray
from matplotlib.patches import Circle

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
        self.path = []  # path of the line
        self.line = None  # line object
        self.preview_circle = None

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
            self.path.append((event.xdata, event.ydata))
            self.path.append((event.xdata, event.ydata))

    def mouseRelease(self, event):
        if event.button == 1 and self.path:  # left mouse button
            # create a binary image of the line
            binary_img = np.zeros_like(rgb2gray(self.img),dtype=bool)
            for i in range(len(self.path) - 1):
                rr, cc = line(int(self.path[i][1]), int(self.path[i][0]), int(self.path[i + 1][1]), int(self.path[i + 1][0]))
                binary_img[rr, cc] = True
            # apply morphological dilation to the binary image
            selem = morphology.disk(self.spinBox_brush_size.value())
            dilated_img = morphology.binary_dilation(binary_img, selem)

            # apply the dilated image to the original image
            self.img[dilated_img > 0] = 0  # change this to modify the color of the line

            self.preview_circle = None 

            self.ax.clear()

            self.ax.imshow(self.img)
            
            self.path.clear()  # clear the path
            

            self.canvas.draw()

    def mouseMove(self, event):
        # add a line preview when hovering and mouse is pressed
        if event.inaxes == self.ax and self.path:
            self.path.append((event.xdata, event.ydata))
            self.line = Line2D(*zip(*self.path[-2:]), color='black', linewidth=self.spinBox_brush_size.value())
            if self.preview_circle is not None:
                self.preview_circle.remove()  # remove the old preview circle
                self.preview_circle = None
            self.ax.add_line(self.line)
            self.canvas.draw()
            
        elif event.inaxes == self.ax:
            if self.preview_circle is not None:
                self.preview_circle.remove()  # remove the old preview circle
            self.preview_circle = Circle((event.xdata, event.ydata), self.spinBox_brush_size.value(), fill=False, edgecolor='lightpink')
            self.ax.add_patch(self.preview_circle)
            self.canvas.draw()
            
            
            

            

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()