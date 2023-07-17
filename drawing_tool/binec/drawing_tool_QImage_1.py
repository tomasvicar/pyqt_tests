from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QFileDialog, QLabel, QFrame
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QImage, QPainter, QPen
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('main_window2.ui', self)  # Load the .ui file


        self.frame = self.findChild(QFrame, 'frame')
        self.image = QImage(self.frame.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        
        self.spinBox_brush_size = self.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        
        self.drawing = False
        self.brushColor = Qt.black
        self.lastPoint = QPoint()


        self.show()
        
        
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.spinBox_brush_size.value(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
            print(event.pos())
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            
            
    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
        
            
        
        
        
        
        
        
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
