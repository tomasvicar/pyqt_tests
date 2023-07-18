from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main_window.ui', self)
        self.original_pixmap = QPixmap("_DSC0072_3.bmp")

        self.label = self.findChild(QtWidgets.QLabel, 'label')
        size = self.label.size()
        self.label.setPixmap(self.original_pixmap.scaled(size.width(), size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.label.setScaledContents(True)

    def resizeEvent(self, event):
        size = self.label.size()
        self.label.setPixmap(self.original_pixmap.scaled(size.width(), size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        super(MainWindow, self).resizeEvent(event)

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()