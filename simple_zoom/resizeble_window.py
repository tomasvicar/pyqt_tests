from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.pixmap = QPixmap("_DSC0072_3.bmp")
        self.initUI()

    def initUI(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.pixmap_item = self.scene.addPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.setCentralWidget(self.view)

    def resizeEvent(self, event):
        if self.pixmap_item is not None:
            self.pixmap_item.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        QMainWindow.resizeEvent(self, event)

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
