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
        self.original_overlay = QImage()
        self.overlay = QImage()
        self.overlayVisible = False
        self.scaleFactor = 1.0
        self.spinBox_brush_size = ui.findChild(QtWidgets.QSpinBox, 'spinBox_brush_size')
        self.brushRect = QRect()
        self.panning = False
        self.last_pan_point = QPoint()
        self.zoom_offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.panning = True
                self.last_pan_point = event.pos()
            else:
                self.drawing = True
                self.lastPoint = self.mapToPixmap(event.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.panning:
            displacement = self.last_pan_point - event.pos()
            self.move(self.pos() - displacement)
            self.last_pan_point = event.pos()
        elif (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.original_overlay)
            painter.setPen(QPen(self.brushColor, self.spinBox_brush_size.value() / self.scaleFactor, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, self.mapToPixmap(event.pos()))
            self.lastPoint = self.mapToPixmap(event.pos())
            self.update_overlay()
            self.update()
        else:
            brush_size = self.spinBox_brush_size.value() * self.scaleFactor
            self.brushRect = QRect(int(event.pos().x() - brush_size // 2),
                                   int(event.pos().y() - brush_size // 2),
                                   int(brush_size), int(brush_size))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.panning:
                self.panning = False
            elif self.drawing:
                self.drawing = False

    def setPixmap(self, pixmap):
        prev_width = self.pixmap().width() if self.pixmap() is not None else 1
        prev_height = self.pixmap().height() if self.pixmap() is not None else 1

        super().setPixmap(pixmap.scaled(int(pixmap.width() * self.scaleFactor), int(pixmap.height() * self.scaleFactor), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.original_overlay = QImage(self.image.size(), QImage.Format_ARGB32)
        self.original_overlay.fill(Qt.transparent)
        self.update_overlay()

        new_width = self.pixmap().width()
        new_height = self.pixmap().height()

        # Adjust zoom offset based on zoom factor and previous image position
        self.zoom_offset.setX(int(self.zoom_offset.x() * (new_width / prev_width)))
        self.zoom_offset.setY(int(self.zoom_offset.y() * (new_height / prev_height)))

        # Translate the image to the adjusted zoom position
        self.move(self.pos() + self.zoom_offset)

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
            self.scaleImage(1 + steps / 10, event.pos())

    def mapToPixmap(self, pos):
        return self.pixmap().rect().topLeft() + (pos - self.rect().topLeft()) / self.scaleFactor

    def scaleImage(self, factor, zoom_pos):
        prev_width = self.pixmap().width() if self.pixmap() is not None else 0
        prev_height = self.pixmap().height() if self.pixmap() is not None else 0

        self.scaleFactor *= factor
        self.setPixmap(QPixmap.fromImage(self.image))

        new_width = self.pixmap().width()
        new_height = self.pixmap().height()

        # Calculate the difference in image position due to zooming
        diff_x = (zoom_pos.x() - self.pos().x()) * (1 - (new_width / prev_width))
        diff_y = (zoom_pos.y() - self.pos().y()) * (1 - (new_height / prev_height))

        # Adjust the zoom offset
        self.zoom_offset.setX(int(self.zoom_offset.x() - diff_x))
        self.zoom_offset.setY(int(self.zoom_offset.y() - diff_y))

        # Translate the image to the adjusted zoom position
        self.move(self.pos() + self.zoom_offset)

    def resizeEvent(self, event):
        if self.pixmap() is not None:
            self.setPixmap(QPixmap.fromImage(self.image))

    def update_overlay(self):
        self.overlay = self.original_overlay.scaled(self.pixmap().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)



class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main_window2.ui', self)

        self.frame = self.findChild(QFrame, 'frame')

        self.image_label = ImageLabel(self.frame, self)
        self.image_label.image = QImage(self.frame.size(), QImage.Format_RGB32)
        self.image_label.image.fill(Qt.white)
        self.image_label.setPixmap(QPixmap.fromImage(self.image_label.image))

        self.findChild(QtWidgets.QPushButton, 'pushButton_load_img').clicked.connect(self.pushButton_load_img_clicked)
        self.findChild(QtWidgets.QPushButton, 'pushButton_save_img').clicked.connect(self.pushButton_save_img_clicked)
        self.findChild(QtWidgets.QCheckBox, 'checkBox_show_drawing').stateChanged.connect(self.checkBox_show_drawing_stateChanged)

        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.image_label)

        self.show()

    def pushButton_load_img_clicked(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File")
        if file_name:
            self.image_label.image = QImage(file_name)
            self.image_label.setPixmap(QPixmap.fromImage(self.image_label.image))

    def pushButton_save_img_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image File")
        if file_name:
            final_image = self.image_label.pixmap().toImage()
            overlay_painter = QPainter(final_image)
            overlay_painter.drawImage(0, 0, self.image_label.original_overlay)
            final_image.save(file_name)

    def checkBox_show_drawing_stateChanged(self, state):
        self.image_label.setOverlayVisible(state == Qt.Checked)

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()