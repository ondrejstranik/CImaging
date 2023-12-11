# %% 
"""
script to generate Digital holograph
(microverselogo)

@author: ostranik
"""

import NanoImagingPack as nip
from NanoImagingPack import v5
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters
from skimage.io import imsave, imread
import napari

#%% code begining - parameter definition
plt.close('all')
#nip.setDefault('IMG_VIEWER', 'VIEW5D')  # if Java is installed correctly


Niter = 50 # number of ifta iteration
Nps = 8 # number of steps in the phase
fnameR = 'logo.png'
imRpixel = 800

totalSize = np.array([2000,2000])

w = 0.650 # laser light in micrometer
npol = 1.548 # IP-DIP @643.8nm
print('laser wavelength {} nm'.format(w*1000))
print('polymer IP-Dip n = {} '.format(npol))
print('Design height = {} um'.format(w/(npol-1)))


#%% image preprocession

# imR  .. image of Rainer
# single value
imR = np.mean(nip.readim(fnameR),axis = (0,1))
imR = nip.pad(imR,20,'maximum')
sf = 1/(np.max(imR.shape)/imRpixel)
# resample teh image
imR = nip.resample(imR, factors=[sf,sf])
# get edges and binarise it
imR = filters.sobel(imR)
imR = nip.image(imR > filters.threshold_otsu(imR))*1.0
napari.view_image(imR)
#v5(imR)

#%% ifta algorithm - inner part

# generate the Goal (myGi)
myGi = nip.extract(imR,ROIsize = totalSize)
myGi = nip.shift(myGi, [1000 - 1119,1000 - 828], pixelwise=True)

#v5(myGi)

# Digital  holography
amp_obj = nip.ones(totalSize.tolist())
est_im = np.sqrt(myGi) +0j

for ii in range(Niter):
    est_obj = nip.ift2d(est_im)
    phase_obj = np.angle(est_obj)+np.pi # phase .. 0 to 2pi real
    phase_obj = np.round(phase_obj/2/np.pi*(Nps-1))*2*np.pi/(Nps-1) # phase .. 0 to 2pi with Nps steps
    est_obj = amp_obj * np.exp(1j*phase_obj)

    est_im = nip.ft2d(est_obj)
    phase_image = np.angle(est_im)+np.pi # phase .. 0 to 2pi real
    est_im = np.sqrt(myGi) * np.exp(1j*phase_image)

# final inner results
finali_obj = phase_obj/2/np.pi*(Nps-1)*amp_obj
finali_image = np.abs(nip.ft2d(est_obj*np.exp(1j*np.pi)))**2
finali_image /= np.max(finali_image)
finali_image *= amp_obj.sum()/finali_image.sum()

#v5(nip.catE(myGi,finali_image,finali_obj))


phasemask = (finali_obj/Nps*255).astype(np.uint8)
#imsave('uverse_mask2000x2000.tiff',phasemask)
#imsave('uverse_image2000x2000.png',finali_image)




