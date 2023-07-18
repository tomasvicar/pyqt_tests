from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
import sys

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = QImage()
        self.image.load('_DSC0072_3.bmp')

        self.drawing = False
        self.brushSize = 5
        self.brushColor = Qt.red
        self.lastPoint = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = self._map_to_image(event.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            new_point = self._map_to_image(event.pos())
            painter.drawLine(self.lastPoint, new_point)
            self.lastPoint = new_point
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_img = self.image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.render_x = max(0, (self.width() - scaled_img.width()) // 2)
        self.render_y = max(0, (self.height() - scaled_img.height()) // 2)
        painter.drawImage(QPoint(self.render_x, self.render_y), scaled_img)

    def _map_to_image(self, pos):
        return QPoint(int((pos.x() - self.render_x) * (self.image.width() / max(1, self.width() - 2 * self.render_x))),
                      int((pos.y() - self.render_y) * (self.image.height() / max(1, self.height() - 2 * self.render_y))))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec())
