from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, QSize, QSizeF, QRectF
from PyQt5 import QtWidgets, uic


class ResizableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(ResizableGraphicsView, self).__init__(parent)
        self._isPanning = False
        self._mousePressedPos = None
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # modified
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # modified
        self.horizontalScrollBar().hide()  # added
        self.verticalScrollBar().hide()  # added

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._mousePressedPos = event.pos()
            self._isPanning = True
        super(ResizableGraphicsView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._isPanning and event.buttons() & Qt.MiddleButton:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - (event.x() - self._mousePressedPos.x()))
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - (event.y() - self._mousePressedPos.y()))
            self._mousePressedPos = event.pos()
        super(ResizableGraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._isPanning = False
        super(ResizableGraphicsView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        super(ResizableGraphicsView, self).resizeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = uic.loadUi('main_window.ui', self)
        self.scene = QGraphicsScene(self)
        self.view = ResizableGraphicsView(self)
        self.pixmap = QPixmap("_DSC0072_3.bmp")
        self.pixmap_item = self.scene.addPixmap(self.pixmap)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.show()

def main():
    app = QApplication([])
    window = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()