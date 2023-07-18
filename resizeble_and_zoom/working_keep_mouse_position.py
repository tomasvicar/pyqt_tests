from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QPointF, QSize, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QCursor
from PyQt5 import QtWidgets, uic


class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 0
        self._pan = False
        self._scene = None
        self._mouse_scene_pos = QPointF()

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setImage(self, pixmap):
        self._pixmap = pixmap
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(self._pixmap)
        self.setScene(self._scene)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        # Get the position of the mouse in the view coordinates before zooming
        mouse_pos_before_zoom = event.pos()
        
        # mouse_pos_before_zoom = self.mapFromScene(mouse_pos_before_zoom)
        mouse_pos_before_zoom_global = self.mapToScene(mouse_pos_before_zoom)
        
        # tmp = mouse_pos_before_zoom
        # tmp = self.mapToScene(mouse_pos_before_zoom)
        # tmp = self.mapFromScene(mouse_pos_before_zoom)
    
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
    
        # mouse_pos_after_zoom = event.pos()
        
        
    
        # Calculate the new position of the mouse in the view coordinates after zooming
        mouse_pos_after_zoom = self.mapFromScene(mouse_pos_before_zoom_global)
        # mouse_pos_after_zoom = self.mapToScene(tmp)
        
        # mouse_pos_after_zoom = self.mapToScene(tmp)
        
        print(mouse_pos_before_zoom, mouse_pos_before_zoom_global,  mouse_pos_after_zoom)
    
        # Calculate the difference between the mouse positions before and after zooming
        # diff = mouse_pos_after_zoom - mouse_pos_before_zoom
    
        # Adjust the translation of the image to keep the mouse at the same position in the view
        # self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
        # self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
        
        
        
        # diff = (mouse_pos_after_zoom - mouse_pos_before_zoom) * factor
        # diff = (mouse_pos_after_zoom - mouse_pos_before_zoom) / factor
        diff = (mouse_pos_after_zoom - mouse_pos_before_zoom)
        
        diff = -1 * diff

        # Adjust the translation of the scene by the difference considering the zoom factor
        # self.translate(diff.x() / factor, diff.y() / factor)
        
        # self.translate(diff.x(), diff.y() )
        
        self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - diff.x()))
        self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - diff.y()))
        
        # self.centerOn(mouse_pos_after_zoom)


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

    def showEvent(self, event):
        if self._scene is not None:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def resize(self, event):
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def setCursorPosition(self, pos):
        # Set the cursor position to the specified position
        global_pos = self.mapToGlobal(pos)
        QCursor.setPos(global_pos)


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
