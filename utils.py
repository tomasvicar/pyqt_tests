from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor, QPen
from PyQt5.QtCore import Qt, QLineF

import numpy as np
from PyQt5.QtGui import qRgb
import matplotlib.pyplot as plt

from skimage.measure import label
from skimage.morphology import disk,dilation
from scipy.ndimage.morphology import binary_dilation



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
    
    return colors



def transform_colors_with_transparency_rounding(colors, transparency):
    colors_out = []
    for color in colors:
        # Create a QImage to draw on.
        pixmap = QPixmap(1, 1)
        pixmap.fill(Qt.transparent)
    
        # Create a QPainter to perform the drawing.
        painter = QPainter(pixmap)
    
        # Set the color and draw a point.
        color = QColor(*color, transparency)  
        painter.setPen(color)
        painter.drawPoint(0, 0)
    
        # Done painting.
        painter.end()
        
        color_out = QPixmapToArray(pixmap)[0,0,:3]
        
        colors_out.append(color_out)

    return np.stack(colors_out)


def QPixmapToArray(pixmap):
    # or import qimage2ndarray
    channels_count = 4
    image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
    # image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32_Premultiplied)
    # image = pixmap.toImage()
    width = image.width()
    height = image.height()
    s = image.bits().asstring(width * height * channels_count)
    arr = np.fromstring(s, dtype=np.uint8).reshape(( height, width, channels_count))
    
    arr = arr[:,:,[2, 1, 0, 3]].copy()
    
    return arr
    
  
def arrayToQPixmap(arr):
    # or import qimage2ndarray
    arr = arr[:,:,[2, 1, 0, 3]].copy()
    
    height, width, channels_count = arr.shape
    image = QImage(arr.data, width, height, channels_count * width, QImage.Format_ARGB32)
    # image = QImage(arr.data, width, height, channels_count * width, QImage.Format_ARGB32_Premultiplied)
    pixmap = QPixmap.fromImage(image)
    return pixmap


def toBinaryLine(q_points, size):
    binary_image = QImage(size, QImage.Format_ARGB32)
    binary_image.fill(Qt.transparent)  # Fill the image with transparency

    painter = QPainter(binary_image)
    painter.setPen(QPen(Qt.black, 1))  # Set the pen to red color, 1 pixel width
    for i in range(len(q_points) - 1):
        painter.drawLine(q_points[i], q_points[i+1])
    painter.end()
    
    return binary_image
    



def get_unique_colors(image):

    w, h, d = image.shape
    image_array = np.reshape(image, (w * h, d))

    # Get all unique colors
    unique_colors = np.unique(image_array, axis=0)

    return unique_colors

# def custom_round(x):
#     return int(x + (0.5 if x > 0 else -0.5))

# v_custom_round = np.vectorize(custom_round)


# def custom_round(value):
#     if value < 0:
#         return np.ceil(value - 0.5)
#     else:
#         return np.floor(value + 0.5)

# v_custom_round = np.vectorize(custom_round)



def colorToLabel(overlay_arr, transparency):
    
    colors = getColors()
    print(colors)
    colors = transform_colors_with_transparency_rounding(colors, transparency)
    
    
    # print(colors)
    # colors_adjusted = colors * (transparency / 255.0)
    # colors_adjusted = np.round(colors_adjusted)
    # colors_rounded = colors_adjusted * (255.0 / transparency)
    # colors_rounded = np.clip(colors_rounded, 0, 255)
    # colors = colors_rounded.astype(int)

    
    # u_colors = get_unique_colors(overlay_arr[:,:,:3])
    # u_colors = np.delete(u_colors, np.where(u_colors == np.array([0, 0, 0])))
    # for u_color in u_colors:
    #     pass
        
    
    
    # u_vals = np.unique(overlay_arr[:,:,:2])
    
    # colors = np.round(np.round(colors * (transparency/255)) /  (transparency/255))
    # colors = v_custom_round(v_custom_round(colors * (transparency/255)) /  (transparency/255))
    # overlay_arr = overlay_arr.astype(np.int16)
    
    # transparency = 72 / 255.0

    # colors_adjusted = np.round(colors / transparency).astype(int)

    # colors_adjusted = np.clip(colors_adjusted, 0, 255
    
    # colors = v_custom_round(v_custom_round(colors * (transparency / 255)) / (transparency / 255))
    

    
    label_arr = np.zeros(overlay_arr.shape[:2], dtype=np.uint8)
    print(colors)
    print(get_unique_colors(overlay_arr[:,:,:3]))
    print(np.unique(overlay_arr[:,:,3]))
    for idx_color, color in enumerate(colors):
        # why color is not precise?
        # label_arr[(np.abs(overlay_arr[:,:,0] - color[0]) < 5) & (np.abs(overlay_arr[:,:,1] - color[1]) < 5) & (np.abs(overlay_arr[:,:,2] - color[2]) < 5)] = idx_color + 1 
        
        label_arr[(overlay_arr[:,:,0] == color[0]) & (overlay_arr[:,:,1] == color[1])  & (overlay_arr[:,:,2] == color[2])] = idx_color + 1 
        # tolerance = 5
        # label_arr[ np.isclose(overlay_arr[:,:,0], color[0], atol=tolerance) & \
        #            np.isclose(overlay_arr[:,:,1], color[1], atol=tolerance) & \
        #            np.isclose(overlay_arr[:,:,2], color[2], atol=tolerance)] = idx_color + 1 
        
    return label_arr


def labelToColor(label_arr, transparency):
    COLORS = getColors()
    
    # Create an empty array for the color image.
    color_arr = np.zeros((*label_arr.shape, 4), dtype=np.uint8)  # 3 for RGB channels
    
    # Loop over the colors and assign pixels with the current label the current color.
    for idx_color, color in enumerate(COLORS):
        color_tmp = np.concatenate((color, np.array([transparency])))
        color_arr[label_arr == idx_color + 1] = color_tmp
        
        
    
    return color_arr


def splitCell(overlay, birnary_line):
    
    overlay_arr = QPixmapToArray(overlay)
    transparency = np.max(overlay_arr[:,:,3])
    label_arr = colorToLabel(overlay_arr, transparency)
    
    birnary_line_arr = QPixmapToArray(QPixmap.fromImage(birnary_line))[:,:,3] == 255
    label_arr[birnary_line_arr] = 0
    
    label_arr_u = toUniqueLabel(label_arr)
    
    label_arr_u = colorize_notouchingsamecolor(label_arr_u, alowed_num_of_colors=8, min_dist=5)
    
    overlay_arr = labelToColor(label_arr_u, transparency)
    # overlay_arr = labelToColor(label_arr, transparency)
    overlay = arrayToQPixmap(overlay_arr)
    
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
        
        
        
    
    
  
def relabel(label_arr):
    pass
    
    
        


    



def set_pixmap_transparency(pixmap, alpha):
    
    arr = QPixmapToArray(pixmap)
    tmp = arr[:,:,3]
    tmp[tmp > 0] = alpha
    arr[:,:,3] = tmp

    pixmap = arrayToQPixmap(arr)
    
    
    

    return pixmap





import numpy as np

def colorize_notouchingsamecolor(L, alowed_num_of_colors=8, min_dist=5):
    
    N=np.max(L)
    
    neigbours=[]
    for k in range(N):
        k=k+1
        
        cell=L==k
        
        cell_dilate=binary_dilation(cell,disk(min_dist)>0)
        
        tmp=np.unique(L[cell_dilate])
        tmp=tmp[(tmp!=0)&(tmp!=k)]
        
        neigbours.append(tmp-1)
        
        
    numcolors = np.inf
    all_is_not_done=1
    rounds=0
       
    
    maxxx=500
    for qqq in range(maxxx):
    
        all_is_not_done=0
        rounds=rounds+1
        
        I=np.random.permutation(N)
        
        
        colors=np.zeros(N);
        
        numcolors=1
        for k in I:
            
            idx = neigbours[k]
            
            neighborcolors = np.unique(colors[idx])
            
            # neighborcolors=neighborcolors[neighborcolors!=0]
            
            thiscolor = list(set(list(np.arange(alowed_num_of_colors))) - set(neighborcolors))
             
            if len(thiscolor) ==0 :
                all_is_not_done=1
                thiscolor=list(np.arange(alowed_num_of_colors))
            
            
            thiscolor = thiscolor[np.random.randint(len(thiscolor))]
            # thiscolor = thiscolor[0]
            colors[k] = thiscolor
            
            
        if ~all_is_not_done:
            break
        
        
        if qqq==(maxxx-1):
            raise NameError('colors not found')
            
            
    

    color_ind_img=np.zeros(L.shape,'uint8')
    
    for k in range(N):
        color_ind_img[L==k+1]=colors[k]+1
          
    return color_ind_img