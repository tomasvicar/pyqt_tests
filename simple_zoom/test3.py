from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLabel, QFrame, QMainWindow
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, QSize, QSizeF
import sys

class ImageLabel(QLabel):
    def __init__(self, parent=None, ui=None):
        super(ImageLabel, self).__init__(parent)
        self.setMouseTracking(True)
        self.drawing = False
        self.brushColor = Qt.black
        self.last_mouse_position_in_orig = QPoint()
        self.overlay = QImage()
        self.overlayVisible = True
        self.spinBox_brush_size = ui.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        self.brushRect = QRect()
        self.offset = QPoint()
        self.zoomFactor = 1
        self.pan = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mouse_position = event.pos()
            mouse_position_in_orig = (mouse_position - self.offset) / self.zoomFactor
            self.drawing = True
            self.last_mouse_position_in_orig = mouse_position_in_orig
        elif (event.button() == Qt.RightButton) and (QApplication.keyboardModifiers() == Qt.ControlModifier):
            self.pan = True
            self.panStart = event.pos()


    def mouseMoveEvent(self, event):
        mouse_position = event.pos()
        mouse_position_in_orig = (mouse_position - self.offset) / self.zoomFactor
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            
            painter = QPainter(self.overlay)
            painter.setPen(QPen(self.brushColor, self.spinBox_brush_size.value(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_mouse_position_in_orig , mouse_position_in_orig)
            
            self.last_mouse_position_in_orig = mouse_position_in_orig
            self.update()
        elif (event.buttons() & Qt.RightButton) and self.pan:
            pos = event.pos() 
            self.offset += event.pos() - self.panStart
            self.panStart = pos
            self.update()
        else:
            self.brushRect = QRect(mouse_position_in_orig.x() - self.spinBox_brush_size.value() // 2,
                                    mouse_position_in_orig.y() - self.spinBox_brush_size.value() // 2,
                                    self.spinBox_brush_size.value(), self.spinBox_brush_size.value())
            self.update()

            

    def mouseReleaseEvent(self, event):
        self.drawing = False
        self.pan = False

    def setPixmap(self, pixmap):
        super().setPixmap(pixmap)
        self.overlay = QImage(self.pixmap().size(), QImage.Format_ARGB32)
        self.overlay.fill(Qt.transparent)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        
        painter.scale(self.zoomFactor, self.zoomFactor)
        painter.translate(self.offset /self.zoomFactor)
        
        
        painter.drawPixmap(0, 0, self.pixmap())
        if self.overlayVisible:
            painter.drawImage(0, 0, self.overlay)
            
        if (not self.drawing) and (not self.pan):
            painter.setPen(QPen(Qt.red, 2))  # Red, dotted line
            painter.drawEllipse(self.brushRect)

    
    def setOverlayVisible(self, visible):
        self.overlayVisible = visible
        self.update()
        

            
            
    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            degrees = event.angleDelta().y() / 8
            steps = degrees / 15
            zoom_factor = 1 + steps / 10
    
            zoom_factor_old = self.zoomFactor
            mouse_position = event.pos()
    
            # Get the mouse position relative to the original (unzoomed) image
            mouse_position_in_orig = (mouse_position - self.offset) / zoom_factor_old
    
            # Update the zoom factor
            self.zoomFactor = self.zoomFactor * zoom_factor
    
            # Calculate the new offset based on the change in zoom factor and the mouse position
            self.offset = mouse_position - mouse_position_in_orig * self.zoomFactor
    
            self.update()
            

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main_window3.ui', self)

        self.frame = self.findChild(QFrame, 'frame')
        self.image = QImage(self.frame.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.image_label = ImageLabel(self.frame, self)
        self.image_label.setPixmap(QPixmap.fromImage(self.image))

    
        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.image_label)

        self.show()
        
        self.pushButton_load_img_clicked()

    def pushButton_load_img_clicked(self):
        file_name = '_DSC0072_3.bmp'
        if file_name:
            self.image = QImage(file_name)
            pixmap = QPixmap.fromImage(self.image)
            self.image_label.setPixmap(pixmap.scaled(self.frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()