from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5 import QtWidgets, uic
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('main_window.ui', self) # Load the .ui file
        
        self.findChild(QtWidgets.QPushButton, 'pushButton_plot').clicked.connect(self.pushButton_plot_clicked)
        self.findChild(QtWidgets.QPushButton, 'pushButton_img').clicked.connect(self.pushButton_img_clicked)
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.findChild(QHBoxLayout, 'horizontalLayout_figure').addWidget(self.canvas)

        
        
        self.show()
        
        
        
    def pushButton_plot_clicked(self):
        
        print('plot clicked')
        self.figure.clear()
        ax1 = self.figure.add_subplot(1, 1, 1)
        ax1.plot([0,1,2,3,4], [10,1,20,3,40])
        self.canvas.draw()
        

    def pushButton_img_clicked(self):
        
        self.figure.clear()
        ax1 = self.figure.add_subplot(1, 1, 1)
        ax1.imshow(np.random.rand(50,50))
        self.canvas.draw()
        
        
        



app = QtWidgets.QApplication(sys.argv)
window = Ui() 
app.exec_()

