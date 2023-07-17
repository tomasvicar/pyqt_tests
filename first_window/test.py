from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets, uic
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('main_window.ui', self) # Load the .ui file
        
        self.findChild(QtWidgets.QPushButton, 'pushButton_add').clicked.connect(self.pushButton_add_clicked)
        
        self.show()
        
        
    def pushButton_add_clicked(self):
        
        label = self.findChild(QtWidgets.QLabel, 'label_count')
        
        label.setText(str(1 + int(label.text())))
        
        
        
        



app = QtWidgets.QApplication(sys.argv)
window = Ui() 
app.exec_()

