from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QPen
from PyQt5.QtCore import Qt, QLineF

import numpy as np
from PyQt5.QtGui import qRgb
import matplotlib.pyplot as plt

from skimage.measure import label

from colorize_notouchingsamecolor import colorize_notouchingsamecolor
from scipy.ndimage import generate_binary_structure, binary_dilation, grey_dilation
from skimage.morphology import disk
from scipy.ndimage import binary_fill_holes

import time

def get_pixel_color(pixmap, x, y):
    image = pixmap.toImage()
    color = image.pixelColor(x, y)
    return color

def getColors():
    
    # please check ifyour color works with colorToLabel due to rounding of colors (multiplying by transparency)
    colors = np.array([ [255,   0,   0],
                        [  0, 255,   0],
                        [  0,   0, 255],
                        [211, 211,  15],
                        [255,   0, 255],
                        [255, 127,   0],
                        [  0, 255, 255],
                        [114,   0,  20]])
    
    # colors = np.array([ [255,   0,   0],
    #                     [  0, 255,   0],
    #                     [  0,   0, 255],
    #                     [255, 255,  0],
    #                     [255,   0, 255],
    #                     [255, 128,   0],
    #                     [  0, 255, 255],
    #                     [128,   0,  0]])
    
    return colors



def transform_colors_with_transparency_rounding(colors, transparency):
    colors_out = []
    
    image = QImage(1, len(colors), QImage.Format_ARGB32)
    
    image.fill(Qt.transparent)
    painter = QPainter(image)

    
    for color_idx, color in enumerate(colors):

        painter.setPen(QColor(*color, transparency) )
       
        painter.drawPoint(0, color_idx)
    
    
    painter.end()
        
    arr = QImageToArray(image)[:,:,:3]
    for color_idx, color in enumerate(colors):
        color_out = arr[color_idx, 0]
        
        colors_out.append(color_out)

    return np.stack(colors_out)



    
  
def arrayToQImage(arr):
    # or import qimage2ndarray
    arr = arr[:,:,[2, 1, 0, 3]].copy()
    
    height, width, channels_count = arr.shape
    image = QImage(arr.data, width, height, channels_count * width, QImage.Format_ARGB32)
    # image = QImage(arr.data, width, height, channels_count * width, QImage.Format_ARGB32_Premultiplied)
    # pixmap = QPixmap.fromImage(image)
    return image



def QImageToArray(image):
    # or import qimage2ndarray
    channels_count = 4
    # image = image.convertToFormat(QImage.Format_ARGB32)
    # image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32_Premultiplied)
    # image = pixmap.toImage()
    width = image.width()
    height = image.height()
    s = image.bits().asstring(width * height * channels_count)
    arr = np.fromstring(s, dtype=np.uint8).reshape(( height, width, channels_count))
    
    arr = arr[:,:,[2, 1, 0, 3]].copy()
    
    return arr
    


def toBinaryLine(q_points, size, closed=False):
    binary_image = QImage(size, QImage.Format_ARGB32)
    binary_image.fill(Qt.transparent)  # Fill the image with transparency

    painter = QPainter(binary_image)
    painter.setPen(QPen(Qt.black, 1))  # Set the pen to red color, 1 pixel width
    for i in range(len(q_points) - 1):
        painter.drawLine(q_points[i], q_points[i+1])
    if closed:
        painter.drawLine(q_points[i+1], q_points[0])   
    painter.end()
    
    return binary_image
    



def colorToLabel(overlay_arr, transparency):
    
    colors = getColors()
    # print(colors)
    colors = transform_colors_with_transparency_rounding(colors, transparency)
    # print(colors)
    label_arr = np.zeros(overlay_arr.shape[:2], dtype=np.uint8)
    # print(get_unique_colors(overlay_arr))
    for idx_color, color in enumerate(colors):

        label_arr[(overlay_arr[:,:,0] == color[0]) & (overlay_arr[:,:,1] == color[1])  & (overlay_arr[:,:,2] == color[2])] = idx_color + 1 

    return label_arr


def labelToColor(label_arr, transparency):
    colors = getColors()
    colors = transform_colors_with_transparency_rounding(colors, transparency)
    
    # Create an empty array for the color image.
    color_arr = np.zeros((*label_arr.shape, 4), dtype=np.uint8)  # 3 for RGB channels
    
    # Loop over the colors and assign pixels with the current label the current color.
    for idx_color, color in enumerate(colors):
        color_tmp = np.concatenate((color, np.array([transparency])))
        color_arr[label_arr == idx_color + 1] = color_tmp
        
        
    
    return color_arr


def splitCell(overlay, birnary_line):
    
    overlay_arr = QImageToArray(overlay)
    transparency = np.max(overlay_arr[:,:,3])
    

    label_arr = colorToLabel(overlay_arr, transparency)
    
    
    
    birnary_line_arr = QImageToArray(birnary_line)[:,:,3] == 255
    
    birnary_line_arr_in_cell = birnary_line_arr & (label_arr > 0)
    label_arr[birnary_line_arr] = 0
    
    
    

    label_arr_u = toUniqueLabel(label_arr)

    

    
    label_arr_u = colorize_notouchingsamecolor(label_arr_u, alowed_num_of_colors=8, min_dist=3)
    label_arr_u[birnary_line_arr_in_cell] = grey_dilation(label_arr_u, size=(3, 3)) [birnary_line_arr_in_cell]

    
    overlay_arr = labelToColor(label_arr_u, transparency)
    

    
    # overlay_arr = labelToColor(label_arr, transparency)
    
    
    overlay = arrayToQImage(overlay_arr)
    

    
    return overlay


def joinCell(overlay, birnary_line):
    
    overlay_arr = QImageToArray(overlay)
    transparency = np.max(overlay_arr[:,:,3])
    

    label_arr = colorToLabel(overlay_arr, transparency)
    
    
    
    birnary_line_arr = QImageToArray(birnary_line)[:,:,3] == 255
    
    label_arr_u = toUniqueLabel(label_arr)


    selected_nums = label_arr_u[birnary_line_arr]
    selected_nums = selected_nums[selected_nums != 0]
    
    if len(selected_nums) > 0:
        label_arr_u[np.isin(label_arr_u, selected_nums)] = selected_nums[0]

    
    label_arr_u = colorize_notouchingsamecolor(label_arr_u, alowed_num_of_colors=8, min_dist=3)

    
    overlay_arr = labelToColor(label_arr_u, transparency)
    
    
    
    overlay = arrayToQImage(overlay_arr)
    
    return overlay


def removeCell(overlay, birnary_line):
    
    overlay_arr = QImageToArray(overlay)
    transparency = np.max(overlay_arr[:,:,3])
    

    label_arr = colorToLabel(overlay_arr, transparency)
    
    
    birnary_line_arr = QImageToArray(birnary_line)[:,:,3] == 255
    
    label_arr_u = toUniqueLabel(label_arr)

    selected_nums = label_arr_u[birnary_line_arr]
    selected_nums = selected_nums[selected_nums != 0]
    
    if len(selected_nums) > 0:
        overlay_arr[np.isin(label_arr_u, selected_nums)] = 0

    
    
    overlay = arrayToQImage(overlay_arr)
    
    return overlay


def newCell(overlay, birnary_line, transparency):
    
    overlay_arr = QImageToArray(overlay)
        
    

    label_arr = colorToLabel(overlay_arr, transparency)
    
    label_arr_u = toUniqueLabel(label_arr)
    
        
    birnary_line_arr = QImageToArray(birnary_line)[:,:,3] == 255
    birnary_line_arr_fill = binary_fill_holes(birnary_line_arr)
    
    label_arr_u[birnary_line_arr_fill] = np.max(label_arr_u) + 1


    label_arr_u = colorize_notouchingsamecolor(label_arr_u, alowed_num_of_colors=8, min_dist=3)

    overlay_arr = labelToColor(label_arr_u, transparency)
    

    # overlay_arr = labelToColor(label_arr, transparency)
    
    
    overlay = arrayToQImage(overlay_arr)
    
    return overlay

    


def toUniqueLabel(label_arr):
    
    COLORS = getColors()
    label_arr_u = np.zeros(label_arr.shape[:2], dtype=np.uint16)
    largest = 0
    for idx_color, color in enumerate(COLORS):
        tmp, num = label(label_arr == (idx_color + 1), return_num=True, connectivity=1)
        tmp[tmp > 0] = tmp[tmp > 0] + largest
        largest = largest + num
        label_arr_u = label_arr_u + tmp
        
        
    return label_arr_u
        
        
        
def get_unique_colors(image):

    w, h, d = image.shape
    image_array = np.reshape(image, (w * h, d))

    # Get all unique colors
    unique_colors = np.unique(image_array, axis=0)

    return unique_colors
  




def set_image_transparency(image, alpha):
    
    arr = QImageToArray(image)
    
    transparency = np.max(arr[:,:,3])
    
    colors = getColors()
    # print('--------')
    # print('original colors:')
    # print(colors)
    colors_in = transform_colors_with_transparency_rounding(colors, transparency)
    colors_out = transform_colors_with_transparency_rounding(colors, alpha)
    
    # print('transofrmed colors:')
    # print(colors)
    
    # print('image colors:')
    # print(get_unique_colors(arr))
    
    
    
    
    arr_copy = np.zeros_like(arr)
    
    for idx_color, (color_in, color_out) in enumerate(zip(colors_in, colors_out)):

        
        mask = (arr[:,:,0] == color_in[0]) & (arr[:,:,1] == color_in[1])  & (arr[:,:,2] == color_in[2])
        
        colorx = np.append(color_out, alpha)
        for channel in range(4):
            arr_copy[:, :, channel][mask] =  colorx[channel]
 
    
    image = arrayToQImage(arr_copy)
    
    
    # tmp = arr[:,:,3]
    # tmp[tmp > 0] = alpha
    # arr[:,:,3] = tmp

    # image = arrayToQImage(arr)
    

    return image





