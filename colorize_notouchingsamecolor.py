import numpy as np
from skimage.morphology import disk
from scipy.ndimage import binary_dilation

from collections import defaultdict
import networkx as nx
from scipy.ndimage import generate_binary_structure, binary_dilation
import random

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
    
    
    idxs_sorted_from_most_neighbours = np.argsort([len(neigbour) for neigbour in neigbours])[::-1]
    ## it is beter heuristic to start from higher degree nodes
    
    
    
    
    max_tries = 500
    for try_num in range(max_tries):
    
        all_is_not_done = False
        
        used_colors = set()
        all_colors = set(range(alowed_num_of_colors))
        colors = np.zeros(N,dtype=int);
        
        numcolors=1
        for idx_actual in idxs_sorted_from_most_neighbours:
            
            idxs_of_neighbours = neigbours[idx_actual]
            
            neighborcolors = set(colors[idxs_of_neighbours])
            
            
            
            ## faster but not use all the colors.....
            # aval_colors = used_colors - neighborcolors
            # if len(aval_colors) == 0:
            #     new_color = random.choice(list(all_colors - used_colors))
            #     aval_colors = set([new_color])
            #     used_colors.add(new_color)
            
            
            # slower but use colors at random
            aval_colors = all_colors - neighborcolors
            
            
            
            
            if len(aval_colors) == 0:
                all_is_not_done = True
                break
            
            
            thiscolor = random.choice(list(aval_colors))
            colors[idx_actual] = thiscolor
            
            
        if ~all_is_not_done:
            break
        
        
        if try_num == (max_tries-1):
            raise NameError('colors not found')
            
            
    
    color_ind_img=np.zeros(L.shape,'uint8')
    
    for k in range(N):
        color_ind_img[L==k+1]=colors[k]+1
          
    return color_ind_img


# import numpy as np
# from scipy.ndimage.morphology import binary_dilation
# from scipy.ndimage import generate_binary_structure
# from sklearn.utils import shuffle


# def colorize_notouchingsamecolor_optimized(L, alowed_num_of_colors=8, min_dist=5):

#     # Get max value and shape of the input matrix
#     N = np.max(L)
    
#     # Initialize structure for dilation

#     struct = disk(min_dist) > 0
    

#     # Initialize labels, colors and neighbor array
#     colors = {i: 0 for i in range(N)}
#     neighbors = [np.array([], dtype=np.uint8) for _ in range(N)]

#     # Find all neighbor labels for each label
#     for k in range(N):
#         cell = L == (k + 1)
#         cell_dilate = binary_dilation(cell, structure=struct)
#         neighbors_k = np.unique(L[cell_dilate])
#         neighbors[k] = neighbors_k[(neighbors_k != 0) & (neighbors_k != k + 1)] - 1
    
#     # Shuffle labels
#     I = shuffle(list(colors.keys()))

#     # Loop until all labels have different colors or max rounds reached
#     for _ in range(500):
#         # Assign color to each label
#         for k in I:
#             neighbor_colors = np.unique([colors[n] for n in neighbors[k]])
#             available_colors = list(set(range(alowed_num_of_colors)) - set(neighbor_colors))

#             # If no available color, select any color
#             if len(available_colors) == 0:
#                 available_colors = list(range(alowed_num_of_colors))
            
#             # Assign color randomly
#             colors[k] = np.random.choice(available_colors)
        
#         # If all labels have different colors, break
#         if len(set(colors.values())) == N:
#             break
#     else:
#         raise ValueError('colors not found')
    
#     # Map labels to colors
#     color_ind_img = np.zeros_like(L, dtype=np.uint8)
#     for k in range(N):
#         color_ind_img[L == (k + 1)] = colors[k] + 1
    
#     return color_ind_img



# def colorize_notouchingsamecolor_optimized_v2(L, alowed_num_of_colors=8, min_dist=5):

#     # Get max value and shape of the input matrix
#     N = np.max(L)
    
#     # Initialize structure for dilation
#     struct = disk(min_dist) > 0

#     # Initialize labels, colors and neighbor array
#     colors = {i: 0 for i in range(N)}
#     neighbors = [np.array([], dtype=np.uint8) for _ in range(N)]

#     # Find all neighbor labels for each label
#     for k in range(N):
#         cell = L == (k + 1)
#         cell_dilate = binary_dilation(cell, structure=struct)
#         neighbors_k = np.unique(L[cell_dilate])
#         neighbors[k] = neighbors_k[(neighbors_k != 0) & (neighbors_k != k + 1)] - 1
    
#     # Sort labels by the degree (number of neighbors)
#     I = sorted(colors.keys(), key=lambda x: len(neighbors[x]), reverse=True)

#     for _ in range(500):
#         # Initialize count of used colors
#         used_colors = set()
    
#         # Assign color to each label
#         for k in I:
#             neighbor_colors = set(colors[n] for n in neighbors[k])
#             available_colors = set(range(1, alowed_num_of_colors + 1)) - neighbor_colors
    
#             # If no available color, select any color not used yet
#             if not available_colors and len(used_colors) < alowed_num_of_colors:
#                 available_colors = set(range(1, alowed_num_of_colors + 1)) - used_colors
    
#             # If still no available color, select any color
#             if not available_colors:
#                 available_colors = set(range(1, alowed_num_of_colors + 1))
                
#             # Assign color randomly from available colors
#             colors[k] = color = np.random.choice(list(available_colors))
#             used_colors.add(color)
    
#             # Early termination if all colors are used
#             if len(used_colors) == alowed_num_of_colors:
#                 break
            
            
    
#     # Map labels to colors
#     color_ind_img = np.zeros_like(L, dtype=np.uint8)
#     for k in range(N):
#         color_ind_img[L == (k + 1)] = colors[k]
    
#     return color_ind_img



# import networkx as nx
# from scipy.ndimage import generate_binary_structure, binary_dilation

# def colorize_notouchingsamecolor_networkx(L, alowed_num_of_colors=8, min_dist=5):

#     # Get max value and shape of the input matrix
#     N = np.max(L)
    
#     # Initialize structure for dilation
#     struct = generate_binary_structure(2, 1)
#     struct = binary_dilation(struct, iterations=min_dist)

#     # Initialize neighbors list
#     neighbors = [np.array([], dtype=np.uint8) for _ in range(N)]
    
#     # Find all neighbor labels for each label
#     for k in range(N):
#         cell = L == (k + 1)
#         cell_dilate = binary_dilation(cell, structure=struct)
#         neighbors_k = np.unique(L[cell_dilate])
#         neighbors[k] = neighbors_k[(neighbors_k != 0) & (neighbors_k != k + 1)] - 1

#     # Create graph from adjacency list
#     G = nx.Graph()
#     for i, neighbors_i in enumerate(neighbors):
#         for neighbor in neighbors_i:
#             G.add_edge(i, neighbor)

#     # Perform coloring using NetworkX's greedy_color function
#     colors = nx.algorithms.coloring.greedy_color(G, strategy="largest_first")
    
#     # Map labels to colors (consider the allowed number of colors)
#     color_ind_img = np.zeros_like(L, dtype=np.uint8)
#     for k in range(N):
#         color_ind_img[L == (k + 1)] = (colors.get(k, 0) % alowed_num_of_colors) + 1
    
#     return color_ind_img