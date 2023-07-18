from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, QSize, QSizeF, QRectF
from PyQt5 import QtWidgets, uic


class ResizebleView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(ResizebleView, self).__init__(scene, parent)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.pixmap = QPixmap("_DSC0072_3.bmp")
        self.pixmap_item = self.scene().addPixmap(self.pixmap)

        self.pan = False
        self.zoomFactor = 1

    def mousePressEvent(self, event):
        if (event.button() == Qt.RightButton) and (QApplication.keyboardModifiers() == Qt.ControlModifier):
            self.pan = True
            self.panStart = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.RightButton) and self.pan:
            dx = event.x() - self.panStart.x()
            dy = event.y() - self.panStart.y()
            self.panStart = event.pos()

            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            h_bar.setValue(h_bar.value() - dx)
            v_bar.setValue(v_bar.value() - dy)

    def mouseReleaseEvent(self, event):
        self.pan = False
        self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            angle_delta = event.angleDelta().y()
            factor = 1.0 + angle_delta / 1200.0
            self.zoom(factor, event.pos())

    def zoom(self, factor, center):
        self.zoomFactor *= factor

        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        self.scale(factor, factor)

        center = self.mapToScene(center)
        viewport_center = self.mapToScene(self.viewport().rect().center())

        self.centerOn(center)
        diff = center - viewport_center
        self.centerOn(center - diff)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.pixmap_item is not None:
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
            self.centerOn(self.pixmap_item)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi('main_window.ui', self)

        self.resizebleScene = QGraphicsScene(self)
        self.resizebleView = ResizebleView(self.resizebleScene, self)

        self.setCentralWidget(self.resizebleView)

        self.show()

def main():
    app = QApplication([])
    window = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()