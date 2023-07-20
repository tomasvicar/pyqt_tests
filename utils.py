from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor
from PyQt5.QtCore import Qt


import numpy as np
from PyQt5.QtGui import qRgb
import matplotlib.pyplot as plt


def QPixmapToArray(pixmap):
    # or import qimage2ndarray
    channels_count = 4
    image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
    width = image.width()
    height = image.height()
    s = image.bits().asstring(width * height * channels_count)
    arr = np.fromstring(s, dtype=np.uint8).reshape(( height, width, channels_count))
    
    return arr
    
  
def arrayToQPixmap(arr):
    # or import qimage2ndarray
    height, width, channels_count = arr.shape
    image = QImage(arr.data, width, height, channels_count * width, QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(image)
    return pixmap




def set_pixmap_transparency(pixmap, alpha):
    
    arr = QPixmapToArray(pixmap)
    
    
    tmp = arr[:,:,3]
    tmp[tmp > 0] = alpha
    arr[:,:,3] = tmp

    pixmap = arrayToQPixmap(arr)
    
    
    

    return pixmap