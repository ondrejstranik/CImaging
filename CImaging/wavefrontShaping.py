# %%
''' wavefront shaping
for computational imaging
Stranik
'''

# %% package import
import NanoImagingPack as nip
import numpy as np
import napari


# %% parameters

N = 2**9 # image size
c = 50 # shape factor
nIter = int(1e3)
lPar = 1

# define source and target
R = nip.rr((N,N),scale=2/N)

# source
S = np.exp(-c*R**2) - np.exp(-2*c*R**2)
S = S / np.max(S)

# target
T= 1*S

# iteration vector
v = np.exp(1j*2*np.pi*np.random.rand(N,N))

# %% power method of eigen vector search

for ii in range(nIter):
    if ii%50==0:
        print(f'iteration {ii}')
    v = 1/(1+lPar -S )* nip.ift(T*nip.ft(v)) # B-1*A*v
    v = v / np.linalg.norm(v)
    


# %% result
res = nip.catE(S,np.abs(v),np.abs(nip.ft(v)))
napari.view_image(res, colormap='turbo')

