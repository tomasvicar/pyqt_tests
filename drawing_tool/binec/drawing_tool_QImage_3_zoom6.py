from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLabel, QFrame, QMainWindow
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint, QRectF, QPointF, QRect
import sys


class ImageLabel(QLabel):
    def __init__(self, parent=None, ui=None):
        super(ImageLabel, self).__init__(parent)
        self.setMouseTracking(True)
        self.drawing = False
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.original_image = QImage()
        self.original_overlay = QImage()
        self.overlay = QImage()
        self.overlayVisible = False
        self.scaleFactor = 1.0
        self.spinBox_brush_size = ui.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        self.brushRect = QRectF()
        self.panning = False
        self.last_pan_point = QPoint()
        self.zoom_origin = QPoint()
        self.image_rect = QRectF()
        self.image_rect_scaled = QRectF()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.panning = True
                self.last_pan_point = event.pos()
            else:
                self.drawing = True
                self.lastPoint = self.mapToImage(event.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.panning:
            displacement = self.last_pan_point - event.pos()
            self.move(self.pos() - displacement)
            self.last_pan_point = event.pos()
        elif (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.original_overlay)
            painter.setPen(
                QPen(self.brushColor, self.spinBox_brush_size.value() / self.scaleFactor, Qt.SolidLine, Qt.RoundCap,
                     Qt.RoundJoin))
            painter.drawLine(self.lastPoint, self.mapToImage(event.pos()))
            self.lastPoint = self.mapToImage(event.pos())
            self.update_overlay()
            self.update()
        else:
            brush_size = self.spinBox_brush_size.value() * self.scaleFactor
            self.brushRect = QRectF(event.pos().x() - brush_size / 2,
                                    event.pos().y() - brush_size / 2,
                                    brush_size, brush_size)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.panning:
                self.panning = False
            elif self.drawing:
                self.drawing = False

    def setPixmap(self, pixmap):
        self.original_image = pixmap.toImage()
        self.original_overlay = QImage(self.original_image.size(), QImage.Format_ARGB32)
        self.original_overlay.fill(Qt.transparent)
        self.update_overlay()
        self.scaleFactor = 1.0
        self.zoom_origin = QPoint()
        self.image_rect = QRectF(QRect(QPoint(0, 0), self.original_image.size()))
    
        super().setPixmap(QPixmap.fromImage(self.original_image))
        self.update_scaled_rect()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.image_rect_scaled.toRect(), QPixmap.fromImage(self.original_image), self.image_rect.toRect())
        if self.overlayVisible:
            painter.drawImage(self.image_rect_scaled.topLeft(), self.overlay)
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

    def mapToImage(self, pos):
        return self.image_rect.topLeft() + (pos - self.image_rect_scaled.topLeft()) / self.scaleFactor

    def zoomImage(self, factor, zoom_pos):
        prev_scale = self.scaleFactor
        self.scaleFactor *= factor
    
        # Calculate the zoom offset based on the zoom factor and previous scale
        offset = (zoom_pos - self.image_rect_scaled.topLeft()) * (1 / prev_scale - 1 / self.scaleFactor)
    
        # Translate the image rect to the adjusted zoom origin
        self.image_rect.moveCenter(self.zoom_origin + offset)
    
        # Update the scaled rect and overlay
        self.update_scaled_rect()
        self.update_overlay()
        self.update()

    def resizeEvent(self, event):
        self.update_scaled_rect()

    def update_overlay(self):
        self.overlay = self.original_overlay.scaled(self.image_rect_scaled.size().toSize(), Qt.KeepAspectRatio,
                                                    Qt.SmoothTransformation)

    def update_scaled_rect(self):
        scaled_top_left = self.image_rect.topLeft() * self.scaleFactor
        scaled_bottom_right = self.image_rect.bottomRight() * self.scaleFactor
    
        rect_f = QRectF(self.rect())
        self.image_rect_scaled = QRectF(scaled_top_left, scaled_bottom_right).intersected(rect_f)
    
        if self.image_rect_scaled.width() < rect_f.width() or self.image_rect_scaled.height() < rect_f.height():
            self.image_rect_scaled = self.image_rect.intersected(rect_f)
    
        self.zoom_origin = self.image_rect.center()


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main_window2.ui', self)

        self.frame = self.findChild(QFrame, 'frame')

        self.image_label = ImageLabel(self.frame, self)
        self.image_label.setScaledContents(True)

        self.findChild(QtWidgets.QPushButton, 'pushButton_load_img').clicked.connect(self.pushButton_load_img_clicked)
        self.findChild(QtWidgets.QPushButton, 'pushButton_save_img').clicked.connect(self.pushButton_save_img_clicked)
        self.findChild(QtWidgets.QCheckBox, 'checkBox_show_drawing').stateChanged.connect(
            self.checkBox_show_drawing_stateChanged)

        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.image_label)

        self.show()

    def pushButton_load_img_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File")
        if file_name:
            self.image_label.setPixmap(QPixmap(file_name))

    def pushButton_save_img_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image File")
        if file_name:
            self.image_label.pixmap().save(file_name)

    def checkBox_show_drawing_stateChanged(self, state):
        self.image_label.setOverlayVisible(state == Qt.Checked)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()