# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:16:31 2018

@author: gghysels

Script to plot a cross-sectional view of ln Kv realizations simulated with SGS (in SGeMS).
Used to create Fig. 9 in Ghysels et al. (2019), Hydrogeol. J.
"""

import numpy as np 
import matplotlib.pyplot as plt 
import os
from matplotlib import colors

Nr = 1
Nc = 2

os.chdir('C:\Users\gghysels\OneDrive - Vrije Universiteit Brussel\Papers\Paper Pseudo River\Manuscript\Review\Figures')

img = np.loadtxt('lnKprofile1.txt')
img2 = np.loadtxt('lnKprofile2.txt')
images = []

fig, axs = plt.subplots(2, 1)
fig.suptitle('Cross-sections Riverbed')

images.append(axs[0].imshow(img, cmap='RdYlBu_r', vmin=-4, vmax=2, aspect=4, extent=(0,12.5,0,1)))
images.append(axs[1].imshow(img2, cmap='RdYlBu_r', vmin=-4, vmax=2, aspect=4, extent=(0,12.5,0,1)))

vmin = -4
vmax = 2
norm = colors.Normalize(vmin=vmin, vmax=vmax)
for im in images:
    im.set_norm(norm)

fig.colorbar(images[0], ax=axs)


axs[0].set_xticks(np.arange(0.0,12.5+1,2.5))
axs[1].set_xticks(np.arange(0.0,12.5+1,2.5))

axs[0].set_yticks(np.arange(0.0,1+0.1,0.5))
axs[1].set_yticks(np.arange(0.0,1+0.1,0.5))

labels = [item.get_text() for item in axs[0].get_xticklabels()]
empty_string_labels = ['']*len(labels)
axs[0].set_xticklabels(empty_string_labels)

plt.savefig('Kprofile1.png', dpi=200, bbox_inches='tight')
plt.savefig('Kprofile1.pdf', dpi=200, bbox_inches='tight')
plt.show()