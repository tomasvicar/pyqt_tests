from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLabel, QFrame, QMainWindow
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint, QRect
import sys

class ImageLabel(QLabel):
    def __init__(self, parent=None, ui=None):
        super(ImageLabel, self).__init__(parent)
        self.setMouseTracking(True)
        self.drawing = False
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.overlay = QImage()
        self.overlayVisible = False
        self.spinBox_brush_size = ui.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        self.brushRect = QRect()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.overlay)
            painter.setPen(QPen(self.brushColor, self.spinBox_brush_size.value(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
        else:
            self.brushRect = QRect(event.pos().x() - self.spinBox_brush_size.value() // 2,
                                   event.pos().y() - self.spinBox_brush_size.value() // 2,
                                   self.spinBox_brush_size.value(), self.spinBox_brush_size.value())
            self.update()
            

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def setPixmap(self, pixmap):
        super().setPixmap(pixmap)
        self.overlay = QImage(self.pixmap().size(), QImage.Format_ARGB32)
        self.overlay.fill(Qt.transparent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap())
        if self.overlayVisible:
            painter.drawImage(0, 0, self.overlay)
        if not self.drawing:
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
            zoom_pos = event.pos()
            
            self.zoomImage(zoom_factor, zoom_pos)
            
            
        

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main_window2.ui', self)

        self.frame = self.findChild(QFrame, 'frame')
        self.image = QImage(self.frame.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.image_label = ImageLabel(self.frame, self)
        self.image_label.setPixmap(QPixmap.fromImage(self.image))

        self.findChild(QtWidgets.QPushButton, 'pushButton_load_img').clicked.connect(self.pushButton_load_img_clicked)
        self.findChild(QtWidgets.QPushButton, 'pushButton_save_img').clicked.connect(self.pushButton_save_img_clicked)
        self.findChild(QtWidgets.QCheckBox, 'checkBox_show_drawing').stateChanged.connect(self.checkBox_show_drawing_stateChanged)

        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.image_label)

        self.show()

    def pushButton_load_img_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File")
        if file_name:
            self.image = QImage(file_name)
            pixmap = QPixmap.fromImage(self.image)
            self.image_label.setPixmap(pixmap.scaled(self.frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def pushButton_save_img_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image File")
        if file_name:
            final_image = self.image_label.pixmap().toImage()
            overlay_painter = QPainter(final_image)
            overlay_painter.drawImage(0, 0, self.image_label.overlay)
            final_image.save(file_name)

    def checkBox_show_drawing_stateChanged(self, state):
        self.image_label.setOverlayVisible(state == Qt.Checked)

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()