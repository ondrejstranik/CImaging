# %%
"""
script to generate Diffractive optical Element (DOE)
by phase mask only
(Abbe)

@author: ostranik, jan becker
"""

import NanoImagingPack as nip
import numpy as np
from skimage import filters
from skimage.io import imsave, imread
import napari

#%% parameter definition

Niter = 50 # number of ifta iteration
Nps = 8 # number of steps in the phase
fnameR = 'Rainer3.jpg'
imRpixel = 800
fnameA = 'Abbe2_eq.jpg'
imApixel = 800
fnameS = 'SIM_eq.jpg'
imSpixel = 800


#totalSize = np.array([1000,1000])
totalSize = np.array([2000,2000])
#innerSize = np.array([600,600])
innerSize = np.array([1300,1300])



#%% image pre-processing

# imR  .. image of Rainer
# single value
imR = np.mean(nip.readim(fnameR),axis = (0,1))
sf = 1/(np.max(imR.shape)/imRpixel)
# resample the image
imR = nip.resample(imR, factors=[sf,sf])
# get edges and binaries it
imR = filters.sobel(imR)
imR = nip.image(imR > filters.threshold_otsu(imR))*1.0

# imA  .. image of Abbe two
# single value + negative
imA = np.mean(nip.readim(fnameA),axis = (0,1))
imA = np.max(imA)-imA
sf = 1/(np.max(imA.shape)/imApixel)
# resample the image
imA = nip.resample(imA, factors=[sf,sf])
# binaries it
imA = nip.image(imA > filters.threshold_otsu(imA))*1.0

# imS .. image of SIM eq
# single value + negative
imS = np.mean(nip.readim(fnameS),axis = (0,1))
imS = np.max(imS)-imS
sf = 1/(np.max(imS.shape)/imSpixel)
# resample the image
imS = nip.resample(imS, factors=[sf,sf])
# binaries it
imS = nip.image(imS > filters.threshold_otsu(imS))*1.0

# show the images
viewer = napari.Viewer()
viewer.add_image(imR, name='Rainer')
viewer.add_image(imA, name='Abbe 2')
viewer.add_image(imS, name='SIM')


#%% ifta algorithm - inner part

# generate the Goal (myGi)
myGi1 = nip.extract(imR,ROIsize = totalSize)
myGi1 = nip.shift(myGi1, [500,-500], pixelwise=True)
myGi2 = nip.extract(imS,ROIsize = totalSize)
myGi2 = nip.shift(myGi2, [-250,-500], pixelwise=True)
myGi = myGi1 + myGi2

viewer.add_image(myGi, name='goal inside')


# Digital  holography
amp_obj = nip.extract(np.ones(innerSize),ROIsize = totalSize)
est_im = np.sqrt(myGi) +0j

for ii in range(Niter):
    print(f'inside - iteration number {ii}')
    est_obj = nip.ift2d(est_im)
    phase_obj = np.angle(est_obj)+np.pi # phase .. 0 to 2pi real
    phase_obj = np.round(phase_obj/2/np.pi*(Nps-1))*2*np.pi/(Nps-1) # phase .. 0 to 2pi with Nps steps
    est_obj = amp_obj * np.exp(1j*phase_obj)

    est_im = nip.ft2d(est_obj)
    phase_image = np.angle(est_im)+np.pi # phase .. 0 to 2pi real
    est_im = np.sqrt(myGi) * np.exp(1j*phase_image)


# %% final inner results
finali_obj = phase_obj/2/np.pi*(Nps-1)*amp_obj

viewer.add_image(finali_obj,name='phase mask inside', colormap='turbo')

finali_image = np.abs(nip.ft2d(est_obj*np.exp(1j*np.pi)))**2
finali_image /= np.max(finali_image)
# normalize to the illumination area
finali_image *= amp_obj.sum()/finali_image.sum()

viewer.add_image(finali_image,name='final image', colormap='turbo')

#%% ifta algorithm - outer part

# generate the Goal (myGi)
myGo1 = nip.extract(imA,ROIsize = totalSize)
myGo1 = nip.shift(myGo1, [-250,-500], pixelwise=True)

# smear off part of the inner Goal (myGi1) and add noise so that it is not visible
myGo2 = nip.gaussf(myGi1,40)*(1-myGi1)*(np.random.random(size=myGi1.shape)>0.5)

# adjust manually contrast accordingly so that the smear off part has the same intensity as myGi1
mycontrast = 5
myGo = np.abs(myGo1/mycontrast + myGo2)

viewer.add_image(myGo,name='goal outside', colormap='turbo')

# Digital  holography
amp_obj = 1 - nip.extract(np.ones(innerSize),ROIsize = totalSize)
est_im = np.sqrt(myGo) +0j

for ii in range(Niter):
    print(f'inside - iteration number {ii}')
    est_obj = nip.ift2d(est_im)
    phase_obj = np.angle(est_obj)+np.pi # phase .. 0 to 2pi real
    phase_obj = np.round(phase_obj/2/np.pi*(Nps-1))*2*np.pi/(Nps-1) # phase .. 0 to 2pi with Nps steps
    est_obj = amp_obj * np.exp(1j*phase_obj)

    est_im = nip.ft2d(est_obj)
    phase_image = np.angle(est_im)+np.pi # phase .. 0 to 2pi real
    est_im = np.sqrt(myGo) * np.exp(1j*phase_image)

#%% final outer results
finalo_obj = phase_obj/2/np.pi*(Nps-1)*amp_obj

viewer.add_image(finalo_obj,name='phase mask outside', colormap='turbo')

finalo_image = np.abs(nip.ft2d(est_obj))**2
finalo_image /= np.max(finalo_image)
# normalize to the illumination area
finalo_image *= amp_obj.sum()/finalo_image.sum()

viewer.add_image(finalo_image,name='final image outside', colormap='turbo')

#%% whole DOE result

# whole screen (in + out)
whole_obj = finali_obj*(1-amp_obj) + finalo_obj*amp_obj
# rescale the values to uint8 for Nanoscribe compatibility
phasemask = (whole_obj/Nps*255).astype(np.uint8)
viewer.add_image(whole_obj,name='phase mask whole', colormap='turbo')

whole_image = np.abs(nip.ft2d(np.exp(1j*whole_obj*2*np.pi/(Nps-1))))**2
whole_image /= np.max(whole_image)
whole_image *= np.ones(totalSize).sum()/whole_image.sum()

viewer.add_image(whole_image,name='final image whole', colormap='turbo')

# new viewer to see the images
napari.view_image(nip.catE(whole_image,finali_image),colormap='turbo')

#%% precision test of the adjustment 

# from center
ss = np.linspace(0, totalSize[0], num=10)
ss = ss.astype(int)
pt1 = np.zeros((len(ss),*whole_image.shape))

for jj,ii in enumerate(ss):
    myap = nip.extract(np.ones((ii,ii)),ROIsize = totalSize)
    myimage = np.abs(nip.ft2d(np.exp(1j*whole_obj*2*np.pi/(Nps-1))*myap))**2
    myimage /= np.max(myimage)
    myimage *= myap.sum()/myimage.sum()
    pt1[jj,...] = myimage

napari.view_image(pt1, name = 'central alignment')

# from side
ss = (np.linspace(1, totalSize[0], num=10)).astype('int')
pt2 = np.zeros((len(ss),*whole_image.shape))

for jj,ii in enumerate(ss):
    myap = np.zeros(totalSize)
    myap[:,0:ii] = 1
    myimage = np.abs(nip.ft2d(np.exp(1j*whole_obj*2*np.pi/(Nps-1))*myap))**2
    myimage /= np.max(myimage)
    myimage *= myap.sum()/myimage.sum()
    pt2[jj,...] = myimage

napari.view_image(pt2, name = 'side alignment')


#imsave('mask2000x2000_1300x1300.tiff',phasemask)
#imsave('image2000x2000.png',whole_image)
#imsave('image1300x1300.png',finali_image)




# %%
