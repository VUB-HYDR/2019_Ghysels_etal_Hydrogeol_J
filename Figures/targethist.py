# -*- coding: utf-8 -*-
"""
Created on Wed May 30 13:20:24 2018

@author: gertg

Script to plot the target histogram used in the SGS simulations.
Used to create Fig. 8 in Ghysels et al. (2019), Hydrogeol. J.
"""

import numpy as np
import matplotlib.pyplot as plt

s = np.loadtxt('distribution.txt')

mu, sigma = -1.869, 1.708

abs(mu - np.mean(s)) < 0.01
abs(sigma - np.std(s, ddof=1)) < 0.01

fig = plt.figure(1)
count, bins, ignored = plt.hist(s, 30, normed=True)
plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')
plt.xlabel('ln Kv')
plt.ylabel('Density')
plt.title('Target histogram ln Kv for SGS simulations')
plt.show()

fig.savefig('targethist.png', dpi=200, bbox_inches='tight')
fig.savefig('targethist.pdf', dpi=200, bbox_inches='tight')