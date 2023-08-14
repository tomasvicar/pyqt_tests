from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QGraphicsPixmapItem, QSpinBox, QCheckBox
from PyQt5.QtWidgets import  QRadioButton, QGroupBox, QFileDialog
from PyQt5.QtCore import Qt, QPointF, QSize, QRectF, QLineF, QPoint, QRect
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QCursor, QPen, QMouseEvent
from PyQt5 import QtWidgets, uic

from AdvancedSettingsWindow import AdvancedSettingsWindow
import utils

import numpy as np
from skimage.io import imread
from skimage.io import imsave
import copy

COLORS = utils.getColors()


class History():
    def __init__(self, viewer):
        self.viewer = viewer
        self.counter = 0
        self.max_history_len = 10
        
    def init_history(self):
        self.overlays_history = [self.viewer.overlay for x in range(self.max_history_len)]
        
    def counter_next(self):  
        self.counter = self.counter + 1 
        if self.counter < 0:
            self.counter = self.max_history_len - 1
        if self.counter > self.max_history_len - 1:
            self.counter  = 0  
            
    def counter_previous(self):
        self.counter = self.counter - 1 
        if self.counter < 0:
            self.counter = self.max_history_len - 1
        if self.counter > self.max_history_len - 1:
            self.counter  = 0  
            
        
    def save_state(self):
        self.counter_next()
        self.overlays_history[self.counter] =self.viewer.overlay.copy()
        
    
    def undo(self):
        self.counter_previous()
        self.viewer.setOverlay(self.overlays_history[self.counter])
    
    def redo(self):
        self.counter_next()
        self.viewer.setOverlay(self.overlays_history[self.counter])
        
    
    

        
        
    



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
        self._drawline = False
        self._drawline_clicked = False
        self.parent = parent
        
        self.overlay_original = None
        
        self.checkBox_drawing_visible = parent.findChild(QCheckBox,"checkBox_drawing_visible")
        
        self._brush_size = 1
        self._color_auto = True
        self._color_triplet = None

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.history = History(self)
        
        self.setMouseTracking(True)
        # self.setFocusPolicy(Qt.StrongFocus)
        # self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.checkBox_drawing_visible.setChecked(not self.checkBox_drawing_visible.isChecked())
            
        if event.key() == Qt.Key_0:
            self.parent.radio_buttons[0].setChecked(True)
        if event.key() == Qt.Key_1:
            self.parent.radio_buttons[1].setChecked(True)
        if event.key() == Qt.Key_2:
            self.parent.radio_buttons[2].setChecked(True)
        if event.key() == Qt.Key_3:
            self.parent.radio_buttons[3].setChecked(True)
        if event.key() == Qt.Key_4:
            self.parent.radio_buttons[4].setChecked(True)
        if event.key() == Qt.Key_5:
            self.parent.radio_buttons[5].setChecked(True)
        if event.key() == Qt.Key_6:
            self.parent.radio_buttons[6].setChecked(True)
        if event.key() == Qt.Key_7:
            self.parent.radio_buttons[7].setChecked(True)
        if (event.key() == Qt.Key_8) or (event.key() == Qt.Key_9) or (event.key() == Qt.Key_Period) or (event.key() == Qt.Key_Comma):
            self.parent.radio_buttons[8].setChecked(True)
            

        
    def getOverlay(self):
        return self.overlay
    
    
    def setOverlay(self, overlay):
        self.overlay = overlay
        self.updateOverlay()
        
    
    def setColorIndex(self, index_str):
        if index_str != 'auto':
            self._color_triplet = COLORS[int(index_str)]
            self._color_auto = False
        else:
            self._color_triplet = index_str
            self._color_auto = True
    


    def setImage(self, pixmap):
        
        self._pixmap = pixmap
        self._scene = QGraphicsScene(self)
        self._photo = self._scene.addPixmap(self._pixmap)
        self.setScene(self._scene)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        
        
        # self.overlay = QPixmap.fromImage(QImage(self._pixmap.size(), QImage.Format_ARGB32))
        # self.overlay = QPixmap(self._pixmap.size())
        
        self.overlay = QImage(self._pixmap.size(), QImage.Format_ARGB32)
        self.overlay.fill(Qt.transparent)
        self._photo_overlay = self._scene.addPixmap(QPixmap.fromImage(self.overlay))
        self.history.init_history()
        
        

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
        if event.modifiers() == Qt.ShiftModifier:
            self._brush_size = self.advanced_settings_window.spinBox_brush_size_shift.value()
        elif event.modifiers() == Qt.ControlModifier:
            self._brush_size = self.advanced_settings_window.spinBox_brush_size_ctrl.value()
        else:
            self._brush_size = self.advanced_settings_window.spinBox_brush_size.value()
        

    def updateColor(self): 
        if isinstance(self._color_triplet, QColor):
            self._color = self._color_triplet
        else:
            self._color = QColor(*self._color_triplet, self.getTransparency())
        
        

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = True
            self._panStart = event.pos()
        elif event.button() == Qt.LeftButton:
            if not self._drawline:
                self.update_brush_size(event)
                self._mouse_position_old =  self.mapToScene(event.pos())
                self._draw = True
                if self._color_auto:
                    self._color_triplet = self.overlay.pixelColor( int(self._mouse_position_old.x()), int(self._mouse_position_old.y()))
                    
                self.drawLine(event)
            else:
                self._drawline_clicked = True
                self.whole_line_pos= []
                self.whole_line_parts = []
                self._mouse_position_old =  self.mapToScene(event.pos())
                self.whole_line_pos.append(self._mouse_position_old)
                self.drawLineButtons(event)
            
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = False
        elif event.button() == Qt.LeftButton:
            self._draw = False
            if self._drawline:
                self._drawline = False
                self._drawline_clicked = False
                QApplication.restoreOverrideCursor()
                for part in self.whole_line_parts:
                    self._scene.removeItem(part)
                if self._buttonType == 'split':
                    self.splitCell()
                elif self._buttonType == 'join':
                    self.joinCell()  
                elif self._buttonType == 'remove':
                    self.removeCell()  
                elif self._buttonType == 'new':
                    self.newCell()  
            else:
                self.history.save_state()
                        
                        
            
            
    def updateOverlay(self):
        if self.checkBox_drawing_visible.isChecked():
            self._photo_overlay.setPixmap(QPixmap.fromImage(self.overlay))
        else:
            tmp = QPixmap(self.overlay.size())
            tmp.fill(Qt.transparent)
            self._photo_overlay.setPixmap(tmp)
            
    def drawLine(self, event):
        self.updateColor()
        mouse_position = self.mapToScene(event.pos()) + QPointF(0.1, 0.1)
        painter = QPainter(self.overlay)
        painter.setPen(QPen(self._color, self._brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawLine(self._mouse_position_old, mouse_position)
        painter.end()
        self._mouse_position_old = mouse_position
        self.updateOverlay()
        
    def drawLineButtons(self, event):
        mouse_position = self.mapToScene(event.pos()) + QPointF(0.1, 0.1)
        self.whole_line_pos.append(mouse_position)
        line_part = self._scene.addLine(QLineF(self._mouse_position_old, mouse_position), QPen(QColor("blue"), 2))
        self.whole_line_parts.append(line_part)
        self._mouse_position_old = mouse_position
            
            
    def mouseMoveEvent(self, event):
        if self._scene is None:
            return
        
        if self.ellipse is not None:
            self._scene.removeItem(self.ellipse)
        
        if self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._panStart.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._panStart.y()))
            self._panStart = event.pos()
            
        elif self._draw:
            self.update_brush_size(event)
            self.drawLine(event)
            
        elif self._drawline_clicked:
            self.drawLineButtons(event)
            
        elif self._drawline:
            pass
            
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
        if self._scene is not None:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
            
    def getTransparency(self):
        
        return 255 - int(self.advanced_settings_window.spinBox_transparency.value() / 100 * 255)

        
    def update_trasparency(self):
        self.overlay = utils.set_image_transparency(self.overlay, self.getTransparency())
        self._photo_overlay.setPixmap(QPixmap.fromImage(self.overlay))
        
    def setDrawLineButtons(self, buttonType):
        self._drawline = True
        QApplication.setOverrideCursor(Qt.CrossCursor)
        self._buttonType = buttonType
        
        
    def splitCell(self):
        birnary_line = utils.toBinaryLine(self.whole_line_pos, self._pixmap.size())
        self.overlay = utils.splitCell(self.overlay, birnary_line)
        self.updateOverlay()
        self.history.save_state()
    
    def joinCell(self):
        birnary_line = utils.toBinaryLine(self.whole_line_pos, self._pixmap.size())
        self.overlay = utils.joinCell(self.overlay, birnary_line)
        self.updateOverlay()
        self.history.save_state()
    
    def removeCell(self):
        birnary_line = utils.toBinaryLine(self.whole_line_pos, self._pixmap.size())
        self.overlay = utils.removeCell(self.overlay, birnary_line)
        self.updateOverlay()
        self.history.save_state()
    
    def newCell(self):
        birnary_line = utils.toBinaryLine(self.whole_line_pos, self._pixmap.size(), closed=True)
        self.overlay = utils.newCell(self.overlay, birnary_line, 255 - int(self.advanced_settings_window.spinBox_transparency.value() / 100 * 255))
        self.updateOverlay()
        self.history.save_state()
    



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('main_window.ui', self)

        self.advanced_settings_window = AdvancedSettingsWindow(self)

        self.viewer = ImageViewerDrawing(self, self.advanced_settings_window)
        # self.viewer.setImage(QPixmap('_DSC0072_3.bmp'))
        
        self.advanced_settings_window.setViewer(self.viewer)

        self.gridLayout_img = self.findChild(QtWidgets.QGridLayout, 'gridLayout_img')
        self.gridLayout_img.addWidget(self.viewer, 0, 0, -1, -1)
        
        self.actionAdvanced_settings = self.findChild(QtWidgets.QAction, 'actionAdvanced_settings')
        self.actionAdvanced_settings.triggered.connect(self.open_advanced_settings)
        
        self.actionOpen = self.findChild(QtWidgets.QAction, 'actionOpen')
        self.actionOpen.triggered.connect(self.actionOpen_clicked)
        
        self.actionLoad = self.findChild(QtWidgets.QAction, 'actionLoad')
        self.actionLoad.triggered.connect(self.actionLoad_clicked)
        
        self.actionSave = self.findChild(QtWidgets.QAction, 'actionSave')
        self.actionSave.triggered.connect(self.actionSave_clicked)
        
        
        self.actionUndo = self.findChild(QtWidgets.QAction, 'actionUndo_2')
        self.actionUndo.triggered.connect(self.actionUndo_clicked)
        
        self.actionRedo = self.findChild(QtWidgets.QAction, 'actionRedo_2')
        self.actionRedo.triggered.connect(self.actionRedo_clicked)
        
        self.actionReset = self.findChild(QtWidgets.QAction, 'actionReset_2')
        self.actionReset.triggered.connect(self.actionReset_clicked)
        
        
        self.checkBox_drawing_visible = self.findChild(QCheckBox,"checkBox_drawing_visible")
        self.checkBox_drawing_visible.stateChanged.connect(self.viewer.updateOverlay)
        
        
        
        self.pushButton_split = self.findChild(QtWidgets.QPushButton,"pushButton_split")
        self.pushButton_split.clicked.connect(self.pushButton_split_clicked)
        
        self.pushButton_join = self.findChild(QtWidgets.QPushButton,"pushButton_join")
        self.pushButton_join.clicked.connect(self.pushButton_join_clicked)
        
        
        self.pushButton_remove = self.findChild(QtWidgets.QPushButton,"pushButton_remove")
        self.pushButton_remove.clicked.connect(self.pushButton_remove_clicked)
        
        
        self.pushButton_new_cell = self.findChild(QtWidgets.QPushButton,"pushButton_new_cell")
        self.pushButton_new_cell.clicked.connect(self.pushButton_new_cell_clicked)
        

        
        
        
        self.radio_buttons = []
        for color_ind, color in enumerate(COLORS):
            radio_button = self.findChild(QRadioButton, "radioButton_" + str(color_ind))
            radio_button.setStyleSheet(f"color: rgb({color[0]}, {color[1]}, {color[2]});")
            radio_button.toggled.connect(self.radio_button_color_clicked)
            self.radio_buttons.append(radio_button)
            
        radio_button = self.findChild(QRadioButton, "radioButton_" + "auto")
        radio_button.toggled.connect(self.radio_button_color_clicked)
        self.radio_buttons.append(radio_button)
        self.show()
        self.viewer.setFocusPolicy(Qt.StrongFocus)
        self.viewer.setFocus()
        
        
    def open_advanced_settings(self):
        self.advanced_settings_window.show()
        
        
    def radio_button_color_clicked(self):
        button = self.sender()
        if button.isChecked():
            button_name = button.objectName().replace('radioButton_', '').replace(' ■','')
            self.viewer.setColorIndex(button_name)
    
    def resizeEvent(self, event):
        self.viewer.resize(event)
        QMainWindow.resizeEvent(self, event)
        
    def pushButton_split_clicked(self):
        self.viewer.setDrawLineButtons('split')
        
    def pushButton_join_clicked(self):
        self.viewer.setDrawLineButtons('join')
        
    def pushButton_remove_clicked(self):
        self.viewer.setDrawLineButtons('remove')
        
    def pushButton_new_cell_clicked(self):
        self.viewer.setDrawLineButtons('new')

    def actionOpen_clicked(self):
        # Open a QFileDialog in 'Open File' mode.
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if fileName:
            # Set the selected image on the viewer.
            self.viewer.setImage(QPixmap(fileName))
    
    def actionLoad_clicked(self):

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Mask", "", "Image Files (*.png);;All Files (*)", options=options)
        
        if fileName:
            label_arr = imread(fileName)
            # label_arr_u = utils.colorize_notouchingsamecolor(label_arr_u, alowed_num_of_colors=8, min_dist=3)
            overlay_arr = utils.labelToColor(label_arr, self.viewer.getTransparency())
            overlay = utils.arrayToQImage(overlay_arr)
            self.viewer.setOverlay(overlay)
            self.viewer.overlay_original = overlay.copy()
        
        
    
    def actionSave_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Save As...", "", "Image Files (*.png)", options=options)
        if fileName:
            overlay = self.viewer.getOverlay()
            overlay_arr = utils.QImageToArray(overlay)
            label_arr = utils.colorToLabel(overlay_arr, self.viewer.getTransparency())
            # label_arr_u = utils.toUniqueLabel(label_arr)
            imsave(fileName, label_arr)
        
    
    def actionUndo_clicked(self):
        self.viewer.history.undo()
       
    
    def actionRedo_clicked(self):
        self.viewer.history.redo()
    
    
    
    def actionReset_clicked(self):
        if self.viewer.overlay_original != None:
            self.viewer.setOverlay(self.viewer.overlay_original)
        else:
            self.overlay.fill(Qt.transparent)
    
    


        

        


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())