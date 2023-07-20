from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QSizePolicy, QGraphicsPixmapItem, QSpinBox, QCheckBox
from PyQt5.QtCore import Qt, QPointF, QSize, QRectF, QLineF, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QCursor, QPen, QMouseEvent
from PyQt5 import QtWidgets, uic
from AdvancedSettingsWindow import AdvancedSettingsWindow



from utils import set_pixmap_transparency



class ImageViewerDrawing(QGraphicsView):
    def __init__(self, parent, advanced_settings_window):
        super().__init__(parent)
        self.advanced_settings_window = advanced_settings_window
        self._zoom = 0
        self._pan = False
        self._scene = None
        self._mouse_position_old = QPointF()
        self._draw = False
        self.ellipse = None
        
        self.checkBox_drawing_visible = parent.findChild(QCheckBox,"checkBox_drawing_visible")
        
        
        self._color_triplet = (0, 0, 255)
        self._color = QColor(*self._color_triplet, 255)
        self._brush_size = 1

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setMouseTracking(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.checkBox_drawing_visible.setChecked(not self.checkBox_drawing_visible.isChecked())

        
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
        elif self._zoom < 0:
            self._zoom = 0
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.scale(factor, factor)
    
    
        mouse_pos_after_zoom = self.mapFromScene(mouse_pos_before_zoom_global)

        diff = (mouse_pos_after_zoom - mouse_pos_before_zoom)
        
        diff = -1 * diff

        self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - diff.x()))
        self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - diff.y()))
        
    
    def update_brush_size(self, event):
        self._color = QColor(*self._color_triplet, 255 - int(self.advanced_settings_window.spinBox_transparency.value() / 100 * 255))
        if event.modifiers() == Qt.ShiftModifier:
            self._brush_size = self.advanced_settings_window.spinBox_brush_size_shift.value()
        elif event.modifiers() == Qt.ControlModifier:
            self._brush_size = self.advanced_settings_window.spinBox_brush_size_ctrl.value()
        else:
            self._brush_size = self.advanced_settings_window.spinBox_brush_size.value()
        



    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = True
            self._panStart = event.pos()
        elif event.button() == Qt.LeftButton:
            self.update_brush_size(event)
            self._mouse_position_old =  self.mapToScene(event.pos())
            self._draw = True
            self.drawLine(event)
            
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = False
        elif event.button() == Qt.LeftButton:
            self._draw = False
            
            
    def updateOverlay(self):
        if self.checkBox_drawing_visible.isChecked():
            self._photo_overlay.setPixmap(self.overlay)
        else:
            tmp = QPixmap(self.overlay.size())
            tmp.fill(Qt.transparent)
            self._photo_overlay.setPixmap(tmp)
            
    def drawLine(self, event):
        mouse_position = self.mapToScene(event.pos()) + QPointF(0.1, 0.1)
        painter = QPainter(self.overlay)
        painter.setPen(QPen(self._color, self._brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawLine(self._mouse_position_old, mouse_position)
        painter.end()
        self._mouse_position_old = mouse_position
        self.updateOverlay()
        
            
            
    def mouseMoveEvent(self, event):
        self.update_brush_size(event)
        if self.ellipse is not None:
            self._scene.removeItem(self.ellipse)
        
        if self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._panStart.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._panStart.y()))
            self._panStart = event.pos()
            
        elif self._draw:
            self.update_brush_size(event)
            self.drawLine(event)
            
        else:
            self.update_brush_size(event)
            mouse_position = self.mapToScene(event.pos())
            brush_size = self._brush_size
            brushRect = QRectF(mouse_position.x() - brush_size // 2,
                                mouse_position.y() - brush_size // 2,
                                brush_size, brush_size)
            
            if not (brushRect.top() < 0 or brushRect.left() < 0  or brushRect.bottom() >= self._pixmap.height() or brushRect.right() >= self._pixmap.width()):
            
                self.ellipse = self._scene.addEllipse(brushRect, QPen(QColor(Qt.red), 2))

            

    def showEvent(self, event):
        if self._scene is not None:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def resize(self, event):
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

        
    def update_trasparency(self):
        self.overlay = set_pixmap_transparency(self.overlay, 255 - int(self.advanced_settings_window.spinBox_transparency.value() / 100 * 255))
        self._photo_overlay.setPixmap(self.overlay)



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('main_window.ui', self)

        self.advanced_settings_window = AdvancedSettingsWindow(self)

        self.viewer = ImageViewerDrawing(self, self.advanced_settings_window)
        self.viewer.setImage(QPixmap('_DSC0072_3.bmp'))
        
        self.advanced_settings_window.setViewer(self.viewer)

        self.gridLayout_img = self.findChild(QtWidgets.QGridLayout, 'gridLayout_img')
        self.gridLayout_img.addWidget(self.viewer, 0, 0, -1, -1)
        
        self.actionAdvanced_settings = self.findChild(QtWidgets.QAction, 'actionAdvanced_settings')
        self.actionAdvanced_settings.triggered.connect(self.open_advanced_settings)
        
        
        self.checkBox_drawing_visible = self.findChild(QCheckBox,"checkBox_drawing_visible")
        self.checkBox_drawing_visible.stateChanged.connect(self.viewer.updateOverlay)

        self.show()
        
    def open_advanced_settings(self):
        
        self.advanced_settings_window.show()


    def resizeEvent(self, event):
        self.viewer.resize(event)
        QMainWindow.resizeEvent(self, event)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())