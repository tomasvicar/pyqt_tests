from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton, QVBoxLayout, QSpinBox
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QCursor, QPen

class AdvancedSettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(AdvancedSettingsWindow, self).__init__(parent)
        uic.loadUi('advanced_settings_window.ui', self)
        
        self.spinBox_brush_size = self.findChild(QSpinBox,"spinBox_brush_size")
        self.spinBox_brush_size_ctrl = self.findChild(QSpinBox,"spinBox_brush_size_ctrl")
        self.spinBox_brush_size_shift = self.findChild(QSpinBox,"spinBox_brush_size_shift")
        self.spinBox_transparency = self.findChild(QSpinBox,"spinBox_transparency")

        self.spinBox_transparency.valueChanged.connect(self.spinBox_transparency_value_changed)
         
        
    def setViewer(self, viewer):
        self.viewer = viewer
        
    def spinBox_transparency_value_changed(self):
        self.viewer.update_trasparency()
        
        
        
        
        
        
        