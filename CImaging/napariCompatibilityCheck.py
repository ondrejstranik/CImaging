'''
 testing scripts for running napari
(openGl compatibility)
'''
#%% package import
import numpy as np 
import napari
from skimage import data
import vispy

print(vispy.sys_info())
#%% napari test

viewer = napari.Viewer()
new_layer = viewer.add_image(data.astronaut(), rgb=True)

napari.run()
