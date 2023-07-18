from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5 import QtWidgets, uic

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.pixmap = QPixmap("_DSC0072_3.bmp")
        uic.loadUi('main_window.ui', self)
        
        self.scene = QGraphicsScene(self.frame)
        self.view = QGraphicsView(self.scene, self.frame)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.pixmap_item = None
        
        self.show()
        
    def resizeEvent(self, event):

        
        if self.pixmap_item is not None:
            resized_pixmap = self.pixmap.scaled(self.frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmap_item.setPixmap(resized_pixmap)
        else:
            
            resized_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmap_item = self.scene.addPixmap(resized_pixmap)
            
        self.scene.setSceneRect(QRectF(self.pixmap.rect()))
            
            
            
            

        QMainWindow.resizeEvent(self, event)

def main():
    app = QApplication([])
    window = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()