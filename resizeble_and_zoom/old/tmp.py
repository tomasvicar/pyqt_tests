from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QPainter

class ImageViewer(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self._zoom = 0
        self._pan = False

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

    def setImage(self, path):
        self._zoom = 0

        # Load image
        self._pixmap = QPixmap(path)

        # Create a QGraphicsScene
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(self._pixmap)

        # Set the scene
        self.setScene(self._scene)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1

        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom == 0:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        else:
            self._zoom = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pan = True
            self._panStartX = event.x()
            self._panStartY = event.y()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pan = False

    def mouseMoveEvent(self, event):
        if self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._panStartX))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._panStartY))
            self._panStartX = event.x()
            self._panStartY = event.y()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.viewer = ImageViewer(self)
        self.viewer.setImage("_DSC0072_3.bmp")  # set the image path here

        self.setCentralWidget(self.viewer)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.setGeometry(500, 300, 800, 600)
    window.show()

    sys.exit(app.exec_())
