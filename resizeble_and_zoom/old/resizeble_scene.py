from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, QSize, QSizeF, QRectF
from PyQt5 import QtWidgets, uic



class ResizebleScene(QGraphicsScene):
    def __init__(self, parent, ui):
        super().__init__(parent)   
        self.parent = parent
        self.ui = ui
        
 
        self.view = QGraphicsView(self, self.parent)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.pixmap = QPixmap("_DSC0072_3.bmp")
    
        self.pixmap_item = None
        
        self.pan = False
        self.offset = QPoint()
        self.zoomFactor = 1
        
    
    def mousePressEvent(self, event):
        
        if (event.button() == Qt.RightButton) and (QApplication.keyboardModifiers() == Qt.ControlModifier):
            self.pan = True
            self.panStart = event.pos()


    def mouseMoveEvent(self, event):
        mouse_position = event.pos()
        mouse_position_in_orig = (mouse_position - self.offset) / self.zoomFactor
        if (event.buttons() & Qt.RightButton) and self.pan:
            pos = event.pos() 
            self.offset += event.pos() - self.panStart
            self.panStart = pos
            self.update()
            
    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            degrees = event.delta() / 8
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
            

    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.scale(self.zoomFactor, self.zoomFactor)
        painter.translate(self.offset /self.zoomFactor)
        
        
        painter.drawPixmap(0, 0, self.pixmap())


            

    def mouseReleaseEvent(self, event):
        self.pan = False
        
    
        
    
    def resize(self, event):
        # must be called when main window is resized (overwrite resizeEvent of main window)
        # eg:
            
        # def resizeEvent(self, event):
        #     self.resizebleScene.resize(event)
        #     QMainWindow.resizeEvent(self, event)
        #
        
        if self.pixmap_item is not None:
            resized_pixmap = self.pixmap.scaled(self.parent.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmap_item.setPixmap(resized_pixmap)
        else:
            
            resized_pixmap = self.pixmap.scaled(self.ui.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmap_item = self.addPixmap(resized_pixmap)
            
        self.setSceneRect(QRectF(self.pixmap.rect()))
        
        
    



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        uic.loadUi('main_window.ui', self)
        
        self.resizebleScene = ResizebleScene(self.frame, self)
            
        self.show()
        
    def resizeEvent(self, event):
        self.resizebleScene.resize(event)
        QMainWindow.resizeEvent(self, event)
        
        

            
            
            

        



def main():
    app = QApplication([])
    window = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()