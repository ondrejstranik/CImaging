"""
script to generate Diffractive optical Element (DOE)
by phase mask only
(microverse-logo)

@author: ostranik, jan becker
"""
# %% package import
import NanoImagingPack as nip
import numpy as np
from skimage import filters
from skimage.io import imsave, imread
import napari

#%% parameter definition

Niter = 50 # number of ifta iteration
Nps = 8 # number of steps in the phase
fnameR = 'logo.png'
ffolder = r'C:\Users\ostranik\Documents\GitHub\CImaging\CImaging'
imRpixel = 800 # max number of pixel 


totalSize = np.array([2000,2000]) # size of the DOE

w = 0.650 # laser light in micrometer
npol = 1.548 # IP-DIP @643.8nm
print('laser wavelength {} nm'.format(w*1000))
print('polymer IP-Dip n = {} '.format(npol))
print('Design height = {} um'.format(w/(npol-1)))


#%% image pre-processing

# read file
oImage = imread(ffolder + '\\' + fnameR)[:,:,0:3]

#make black and white image
imR = np.mean(oImage,axis=2)

#add edges
imR = nip.pad(imR,20,'maximum')

# resample the image 
sf = 1/(np.max(imR.shape)/imRpixel)
imR = nip.resample(imR, factors=[sf,sf])

# get only edges of the image
imR = filters.sobel(imR)

# binaries the image
imR = nip.image(imR > filters.threshold_otsu(imR))*1.0

# show the images
viewer = napari.Viewer()
viewer.add_image(oImage, name='original Image')
viewer.add_image(imR, name='pre-processed Image')

#%% ifta algorithm

# generate the Goal (myGi)
# expand the size
myGi = nip.extract(imR,ROIsize = totalSize)

# shift particular part of the image to the centre
# center of image == position of zero-order diffraction (alway a little bit visible) 
myGi = nip.shift(myGi, [1000 - 1119,1000 - 828], pixelwise=True)

viewer.add_image(myGi, name='pre-processed Image', colormap='turbo')

# initial guess
# amplitude of the mask stays equal 1 (no absorption)
amp_obj = nip.ones(totalSize.tolist())
est_im = np.sqrt(myGi) +0j

iterLayer = viewer.add_image(myGi,name='iteration image', colormap='turbo')


# main loop
for ii in range(Niter):
    print(f'iteration number {ii}')
    
    # fourier transform
    est_obj = nip.ift2d(est_im)
    # phase of the object .. 0 to 2pi real
    phase_obj = np.angle(est_obj)+np.pi 
    # discretize the phase ... 0 to 2pi with Nps steps
    phase_obj = np.round(phase_obj/2/np.pi*(Nps-1))*2*np.pi/(Nps-1)
    
    # set amplitude of the object to one
    est_obj = amp_obj * np.exp(1j*phase_obj)

    # fourier transform
    est_im = nip.ft2d(est_obj)

    iterLayer.data = np.abs(est_im)**2

    # phase .. 0 to 2pi real
    phase_image = np.angle(est_im)+np.pi 
    est_im = np.sqrt(myGi) * np.exp(1j*phase_image)


# %% results

#  discrete phasemask into steps from 0 to Nps-1
finali_obj = phase_obj/2/np.pi*(Nps-1)
# rescale the values to uint8 for Nanoscribe compatibility
phasemask = (finali_obj/Nps*255).astype(np.uint8)

viewer.add_image(finali_obj,name='phase mask', colormap='turbo')

# final image
finali_image = np.abs(nip.ft2d(est_obj))**2
finali_image /= np.max(finali_image)

viewer.add_image(finali_image,name='final image', colormap='turbo')

napari.run()

# save the data
#imsave('uverse_mask2000x2000.tiff',phasemask)
#imsave('uverse_image2000x2000.png',finali_image)





# %%
