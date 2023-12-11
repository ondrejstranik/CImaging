# %%
"""
script to generate Digital holograph
two layers
"""

import NanoImagingPack as nip
from NanoImagingPack import v5
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters
from skimage.io import imsave, imread
import numpy

#%% code begining - parameter definition
plt.close('all')
#nip.setDefault('IMG_VIEWER', 'VIEW5D')  # if Java is installed correctly


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



#%% image preprocession

# imR  .. image of Rainer
# single value
imR = np.mean(nip.readim(fnameR),axis = (0,1))
sf = 1/(np.max(imR.shape)/imRpixel)
# resample teh image
imR = nip.resample(imR, factors=[sf,sf])
# get edges and binarise it
imR = filters.sobel(imR)
imR = nip.image(imR > filters.threshold_otsu(imR))*1.0
#v5(imR)

# imA  .. image of Abbe two
# single value + negative
imA = np.mean(nip.readim(fnameA),axis = (0,1))
imA = np.max(imA)-imA
sf = 1/(np.max(imA.shape)/imApixel)
# resample teh image
imA = nip.resample(imA, factors=[sf,sf])
# binarise it
imA = nip.image(imA > filters.threshold_otsu(imA))*1.0
#v5(imA)

# imS .. image of SIM eq
# single value + negative
imS = np.mean(nip.readim(fnameS),axis = (0,1))
imS = np.max(imS)-imS
sf = 1/(np.max(imS.shape)/imSpixel)
# resample teh image
imS = nip.resample(imS, factors=[sf,sf])
# binarise it
imS = nip.image(imS > filters.threshold_otsu(imS))*1.0
#v5(imA)





#%% ifta algorithm - inner part

# generate the Goal (myGi)
myGi1 = nip.extract(imR,ROIsize = totalSize)
myGi1 = nip.shift(myGi1, [500,-500], pixelwise=True)
myGi2 = nip.extract(imS,ROIsize = totalSize)
myGi2 = nip.shift(myGi2, [-250,-500], pixelwise=True)
myGi = myGi1 + myGi2

# do again the binarisation is necessary
#myGin = nip.image(myGin > filters.threshold_otsu(myGin))*1.0
#v5(myGi)

# Digital  holography
amp_obj = nip.extract(np.ones(innerSize),ROIsize = totalSize)
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

#%% ifta algorithm - outer part

# generate the Goal (myGi)
myGo1 = nip.extract(imA,ROIsize = totalSize)
myGo1 = nip.shift(myGo1, [-250,-500], pixelwise=True)
imR_random = (np.random.random(size=imR.shape)>0.5)*(1-imR)
#myGo2 = nip.extract(imR_random,ROIsize = totalSize)
#myGo2 = nip.extract(1-imR,ROIsize = totalSize)
#myGo2 = nip.shift(myGo2, [100,00], pixelwise=True)
myGo2 = nip.gaussf(myGi1,40)*(1-myGi1)*(np.random.random(size=myGi1.shape)>0.5)

# adjust manually contrast accordincally
mycontrast = 5
myGo = np.abs(myGo1/mycontrast + myGo2)



# do again the binarisation is necessary
#myGon = nip.image(myGon > filters.threshold_otsu(myGon))*1.0
#v5(myGo)

# Digital  holography
amp_obj = 1 - nip.extract(np.ones(innerSize),ROIsize = totalSize)
est_im = np.sqrt(myGo) +0j

for ii in range(Niter):
    est_obj = nip.ift2d(est_im)
    phase_obj = np.angle(est_obj)+np.pi # phase .. 0 to 2pi real
    phase_obj = np.round(phase_obj/2/np.pi*(Nps-1))*2*np.pi/(Nps-1) # phase .. 0 to 2pi with Nps steps
    est_obj = amp_obj * np.exp(1j*phase_obj)

    est_im = nip.ft2d(est_obj)
    phase_image = np.angle(est_im)+np.pi # phase .. 0 to 2pi real
    est_im = np.sqrt(myGo) * np.exp(1j*phase_image)

# final outer results
finalo_obj = phase_obj/2/np.pi*(Nps-1)*amp_obj
finalo_image = np.abs(nip.ft2d(est_obj))**2
finalo_image /= np.max(finalo_image)
finalo_image *= amp_obj.sum()/finalo_image.sum()
#v5(nip.catE(myGo,finalo_image,finalo_obj))



#%% end results
#nip.setDefault('IMG_VIEWER', 'NAPARI')  # if Java is installed correctly


# whole screen (iin + out)
whole_obj = finali_obj*(1-amp_obj) + finalo_obj*amp_obj
whole_image = np.abs(nip.ft2d(np.exp(1j*whole_obj*2*np.pi/(Nps-1))))**2
whole_image /= np.max(whole_image)
whole_image *= np.ones(totalSize).sum()/whole_image.sum()

#v5(nip.catE(myGi + myGo,whole_image,whole_obj))
napari.view_image(nip.catE(whole_image,finali_image))

#%% precission test

nip.setDefault('IMG_VIEWER', 'NAPARI')  # if napari is installed correctly

# from center
ss = np.linspace(0, totalSize[0], num=10)
ss = ss.astype(int)
pt1 = whole_image*0
for ii in ss:
    myap = nip.extract(np.ones((ii,ii)),ROIsize = totalSize)
    myimage = np.abs(nip.ft2d(np.exp(1j*whole_obj*2*np.pi/(Nps-1))*myap))**2
    myimage /= np.max(myimage)
    myimage *= myap.sum()/myimage.sum()
    pt1 = nip.catE(pt1,myimage)

pt1.view()

# from side
ss = np.linspace(1, totalSize[0], num=10)
ss = ss.astype(int)
pt2 = whole_image*0
for ii in ss:
    myap = np.zeros(totalSize)
    myap[:,0:ii] = 1
    myimage = np.abs(nip.ft2d(np.exp(1j*whole_obj*2*np.pi/(Nps-1))*myap))**2
    myimage /= np.max(myimage)
    myimage *= myap.sum()/myimage.sum()
    pt2 = nip.catE(pt2,myimage)

pt2.view()

phasemask = (whole_obj/Nps*255).astype(np.uint8)
#imsave('mask2000x2000_1300x1300.tiff',phasemask)
#imsave('image2000x2000.png',whole_image)
#imsave('image1300x1300.png',finali_image)



