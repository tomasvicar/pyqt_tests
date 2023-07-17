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
        self.overlayVisible = True
        self.spinBox_brush_size = ui.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        self.brushRect = QRect()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
        

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.overlay)
            painter.setPen(QPen(self.brushColor, self.spinBox_brush_size.value(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
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
        painter.drawImage(0, 0, self.overlay)



class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main_window2.ui', self)

        self.frame = self.findChild(QFrame, 'frame')
        self.image = QImage(self.frame.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.image_label = ImageLabel(self.frame, self)
        self.image_label.setPixmap(QPixmap.fromImage(self.image))


        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.image_label)
        
        self.pushButton_load_img_clicked()


        self.show()

    def pushButton_load_img_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File")
        if file_name:
            self.image = QImage(file_name)
            pixmap = QPixmap.fromImage(self.image)
            self.image_label.setPixmap(pixmap.scaled(self.frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            
            


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()