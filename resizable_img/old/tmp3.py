from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint
import sys

class DrawingLabel(QLabel):
    def __init__(self, parent=None):
        super(DrawingLabel, self).__init__(parent)
        self.original_image = QImage()
        self.original_image.load('_DSC0072_3.bmp')

        self.image = self.original_image.copy()
        self.pixmap = QPixmap.fromImage(self.image)
        self.aspectRatio = self.image.width() / self.image.height()

        self.drawing = False
        self.brushSize = 5
        self.brushColor = Qt.red
        self.lastPoint = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = self.transformPos(event.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            new_point = self.transformPos(event.pos())
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
        scaledSize = self.original_image.size()
        scaledSize.scale(self.size(), Qt.KeepAspectRatio)

        if not self.image.isNull():
            self.image = self.original_image.scaled(scaledSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.pixmap = QPixmap.fromImage(self.image)

    def transformPos(self, point):
        return QPoint(int(point.x() * (self.image.width() / self.width())), int(point.y() * (self.image.height() / self.height())))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    MainWindow = QMainWindow()
    uic.loadUi('main_window.ui', MainWindow)  # Replace 'your_ui_file.ui' with your actual ui file
    frame = MainWindow.findChild(QFrame, 'frame')  # Replace 'label' with the name of your QLabel in Qt Designer

    layout = QVBoxLayout(frame)
    drawing_label = DrawingLabel()
    layout.addWidget(drawing_label)
    frame.setLayout(layout)

    MainWindow.show()

    sys.exit(app.exec())
