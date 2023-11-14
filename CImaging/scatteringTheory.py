''' scalar scattering 
for computational imaging
Stranik 23-11-14'''
#%% packages
import numpy as np
import napari
from scipy.special import hankel1
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import inv

# %% function definition

def scatter(alpha,k,r0,r):

    ''' field of a scatter '''

    #distanceR = np.linalg.norm(r - r0)
    distanceR = np.sqrt((r[:,0] - r0[0])**2 + (r[:,1] - r0[1])**2)
    G = 1j*np.pi*hankel1(0,k*distanceR)
    G[distanceR==0] = 0

    return alpha*G

def IImage(E,MN):
    ''' get the intensity image from columns of field '''
    return (np.abs(E)**2).reshape(MN)

def PImage(E,MN):
    ''' get the phase image from columns of field '''
    return (np.angle(E)).reshape(MN)

#%% space definition
MN = (200,100) # grid size
dspace = 200 # [nm] grid spacing

# space matrix
Z,X = np.meshgrid(np.arange(MN[1])*dspace,np.arange(MN[0])*dspace)
# space columns
r = np.vstack((X.ravel(),Z.ravel())).T


#%% source generation
alpha0 = 1    
wavelength = 500 # [nm]
r0 = np.array([-10,50])*dspace #  position of the source

k = 2*np.pi/wavelength # [nm-1]

soE = scatter(alpha0,k,r0,r)

soI = IImage(soE,MN)
soP = PImage(soE,MN)

viewer = napari.Viewer()
viewer.add_image(soI)
viewer.add_image(soP)
viewer.add_points(r0/dspace,opacity=0.5, name='source', face_color='red')

#%% generate scatter (spheres)

# low density
#scatterDensity = 0.002
# high density
scatterDensity = 0.01

# random positioning of the spheres
_spPosition = np.random.rand(MN[0]*MN[1])>1 - scatterDensity

# restrict to the central area
rCenterDistance = np.sqrt((r[:,0] - MN[0]//2*dspace)**2 + (r[:,1] - MN[1]//2*dspace)**2)
spPosition = (_spPosition) & (rCenterDistance< dspace* np.min(MN)/4)

spIdx = np.arange(MN[0]*MN[1])[spPosition]
nSp = spIdx.shape[0]
print(f'number of spheres {nSp}')

# display position of the scatterers

viewer.add_points(r[spIdx,:]/dspace, opacity=0.5, name='spheres')

#%% field of the scatterers (M-matrix)

alpha = 0.5

M = np.zeros((MN[0]*MN[1],MN[0]*MN[1]),dtype='complex128')

# place the spheres at given column of the M matrix
for ii in range(nSp):
    M[:,spIdx[ii]] = scatter(alpha,k,r[spIdx[ii]],r)

# %% show the field of the scatter

# sum of the M matrix
msE = np.sum(M,axis=1)


msI = IImage(msE,MN)
#msP = PImage(msE,MN)
viewer.add_image(msI)
#viewer.add_image(msP)


# %% born approximation

boE = soE + np.dot(M,soE)

boI = IImage(boE,MN)
#boP = (np.angle(boE)).reshape(MN)
viewer.add_image(boI, colormap='turbo')
#viewer.add_image(boP)

# %% foldy solution

foM = np.eye((MN[0]*MN[1])) - M

if True:
    # use of sparse Matrix for inversion
    _foM = csc_matrix(foM)
    _foMi = inv(_foM)
    foMi = _foMi.toarray()
    del _foM
    del _foMi

else:
    # standard numpy inversion
    foMi = np.linalg.inv(foM)

foE = np.dot(foMi,soE)


#%%
foI = IImage(foE,MN)
#foP = (np.angle(foE)).reshape(MN)
viewer.add_image(foI,colormap='turbo')
#viewer.add_image(foP)

# %% fixed point iteration

gamma = 0.75
nFP = 20

# fixed point matrix
fpM = gamma*M + (1-gamma)*np.eye((MN[0]*MN[1]))

fpE = soE
for ii in range(nFP):
    print(f'iteration number {ii}')
    fpE = gamma*soE + np.dot(fpM,fpE)

#%%
fpI = IImage(fpE,MN)
#fpP = PImage(fpE,MN)
viewer.add_image(fpI,colormap='turbo')
#viewer.add_image(fpP)

# %% 
napari.run()