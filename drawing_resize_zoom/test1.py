from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QPointF, QSize, QRectF, QLineF
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QPen
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QMouseEvent


class OverlayScene(QGraphicsScene):
    def __init__(self, brush_size=5, view=None, parent=None):
        super().__init__(parent)
        self._pen = QPen(QColor('black'), brush_size)
        self._last_pos = None
        self._view = view

    def mousePressEvent(self, event: QMouseEvent):
        self._last_pos = self._view.mapToScene(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._last_pos is not None:
            current_pos = self._view.mapToScene(event.pos())
            self.addLine(QLineF(self._last_pos, current_pos), self._pen)
            self._last_pos = current_pos

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._last_pos = None

    def clear(self):
        self.clear()


class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 0
        self._pan = False
        self._scene = None

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._overlay_scene = OverlayScene(brush_size=5, view=self, parent=self)
        self._overlay = self._overlay_scene.addPixmap(QPixmap())

    def setImage(self, pixmap):
        self._pixmap = pixmap
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(self._pixmap)
        self.setScene(self._scene)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

        self._overlay.setPixmap(QPixmap(pixmap.size()))
        self._overlay_scene.setSceneRect(QRectF(pixmap.rect()))

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
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
                self.scale(factor, factor)

    def mousePressEvent(self, event):
        if (event.button() == Qt.RightButton) and (QApplication.keyboardModifiers() == Qt.ControlModifier):
            self._pan = True
            self._panStartX = event.x()
            self._panStartY = event.y()

        self._overlay_scene.mousePressEvent(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = False

        self._overlay_scene.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.RightButton) and self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._panStartX))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._panStartY))
            self._panStartX = event.x()
            self._panStartY = event.y()

        self._overlay_scene.mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def clearOverlay(self):
        self._overlay_scene.clear()

    def getOverlayImage(self):
        return self._overlay.pixmap().toImage()

    def showEvent(self, event):
        if self._scene is not None:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def resize(self, event):
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('main_window.ui', self)

        self.viewer = ImageViewer(self)
        self.viewer.setImage(QPixmap('_DSC0072_3.bmp'))

        self.gridLayout_2 = self.findChild(QtWidgets.QGridLayout, 'gridLayout_2')
        self.gridLayout_2.addWidget(self.viewer, 0, 0, -1, -1)

        self.findChild(QtWidgets.QPushButton, 'pushButton_4').clicked.connect(self.pushButton_add_clicked)

        self.show()

    def pushButton_add_clicked(self):
        self.viewer.setImage(QPixmap('_DSC0072_3.bmp'))

    def resizeEvent(self, event):
        self.viewer.resize(event)
        QMainWindow.resizeEvent(self, event)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())
