from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel,QFrame
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
import sys

class DrawingLabel(QLabel):
    def __init__(self, parent=None):
        super(DrawingLabel, self).__init__(parent)
        self.image = QImage()
        self.image.load('_DSC0072_3.bmp')
        self.pixmap = QPixmap.fromImage(self.image)

        self.drawing = False
        self.brushSize = 5
        self.brushColor = Qt.red
        self.lastPoint = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            new_point = event.pos()
            painter.drawLine(self.lastPoint, new_point)
            self.lastPoint = new_point
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    def resizeEvent(self, event):
        self.pixmap = QPixmap.fromImage(self.image.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    MainWindow = QMainWindow()
    uic.loadUi('main_window.ui', MainWindow)  # Replace 'your_ui_file.ui' with your actual ui file
    # label = MainWindow.findChild(QLabel, 'label')  # Replace 'label' with the name of your QLabel in Qt Designer
    frame = MainWindow.findChild(QFrame, 'frame')  # Replace 'label' with the name of your QLabel in Qt Designer
    drawing_label = DrawingLabel(frame)

    MainWindow.show()

    sys.exit(app.exec())