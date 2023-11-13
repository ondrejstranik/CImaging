
''' testing scripts for computation imaging
'''
#%% package import
import numpy as np 
import napari
from skimage import data
import vispy
#import matplotlib.pyplot as plt

print(vispy.sys_info())
#%% napari test

viewer = napari.Viewer()
new_layer = viewer.add_image(data.astronaut(), rgb=True)

napari.run()

# %%
