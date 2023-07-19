from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QSizePolicy, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF, QSize, QRectF, QLineF, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QCursor,QPen, QMouseEvent
from PyQt5 import QtWidgets, uic
from datetime import datetime





class ImageViewerDrawing(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 0
        self._pan = False
        self._scene = None
        self._mouse_position_old = QPointF()
        self._draw = False
        self._pen = QPen(QColor(Qt.black), 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.ellipse = None

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setMouseTracking(True)

    def setPen(self, pen):
        self._pen = pen 
        
    def getOverlay(self):
        return self.overlay

    def setImage(self, pixmap):
        
        self._pixmap = pixmap
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(self._pixmap)
        self.setScene(self._scene)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        
        self.overlay = QPixmap(self._pixmap.size())
        self.overlay.fill(Qt.transparent)
        self._photo_overlay = self._scene.addPixmap(self.overlay)
        
        


    def wheelEvent(self, event):

        mouse_pos_before_zoom = event.pos()
        
        mouse_pos_before_zoom_global = self.mapToScene(mouse_pos_before_zoom)
  
    
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
    
    
        mouse_pos_after_zoom = self.mapFromScene(mouse_pos_before_zoom_global)

        diff = (mouse_pos_after_zoom - mouse_pos_before_zoom)
        
        diff = -1 * diff

        self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - diff.x()))
        self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - diff.y()))
        


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pan = True
            self._panStart = event.pos()
        elif event.button() == Qt.RightButton:
            self._mouse_position_old =  self.mapToScene(event.pos())
            self._draw = True
            self.drawLine(event)
            
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pan = False
        elif event.button() == Qt.RightButton:
            self._draw = False
            
            
    def drawLine(self, event):
        mouse_position = self.mapToScene(event.pos()) + QPointF(0.1, 0.1)
        painter = QPainter(self.overlay)
        painter.setPen(self._pen)
        painter.drawLine(self._mouse_position_old, mouse_position)
        painter.end()
        self._mouse_position_old = mouse_position
        self._photo_overlay.setPixmap(self.overlay)
            
            
    def mouseMoveEvent(self, event):
        if self.ellipse is not None:
            self._scene.removeItem(self.ellipse)
        
        
        if self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._panStart.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._panStart.y()))
            self._panStart = event.pos()
            
        elif self._draw:
            self.drawLine(event)
            
        else:

            mouse_position = self.mapToScene(event.pos())
            brush_size = self._pen.width()
            brushRect = QRectF(mouse_position.x() - brush_size // 2,
                                mouse_position.y() - brush_size // 2,
                                brush_size, brush_size)
            
            
            self.ellipse = self._scene.addEllipse(brushRect, QPen(QColor(Qt.red), 2))

            

    def showEvent(self, event):
        if self._scene is not None:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def resize(self, event):
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

        





class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('main_window.ui', self)

        self.viewer = ImageViewerDrawing(self)
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
