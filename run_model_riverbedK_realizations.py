# -*- coding: utf-8 -*-
"""
Created on Mon May 14 10:44:22 2018

@author: gghysels

Script that uses spatially distributed fields of riverbed K simulated in SGeMS as input for an existing groundwater flow model (MODFLOW).
The model is run for each rivebed K realization and resulting river-aquifer exchange fluxes are extracted from the model's cell budget file.
"""

import numpy as np
import os
import time
import flopy.modflow as fpm
import flopy.utils.binaryfile as bf
import flopy.utils.zonbud as zb


start_time = time.time()

#==============================================================================
# Set variables
#==============================================================================
real = 3 #Amount of realizations/model runs
layers = 4 #Number of riverbed layers
r = 600 #Number of rows
c = 720 #Number of columns
rivercells = 3789 #Number of rivercells

#==============================================================================
#Set paths to folders with new model, initial model and SGeMS simulated data
#==============================================================================
PATH = 'PATH_TO_NEW_MODEL_FOLDER'
INPUTS = 'PATH_TO_INPUTS_FOLDER'
SGEMS = 'PATH_TO_SGEMS_REALIZATIONS_FOLDER'

os.chdir(INPUTS)


#Load in Water Budget Zone 1 (location of river)
print 'Reading in Water Budget Zone file...'
wbzone1 = np.loadtxt(INPUTS+'\\wbzone1')
zb.write_zbarray('zbarray', wbzone1)

#Load in location of river
print 'Reading in River Location file...'
rivloc = np.loadtxt(INPUTS+'\\riverloc.txt')

#open SGS simulation, store in matrix   
print 'Reading in SGS simulation file...'
with open(SGEMS+'\\SGS_3D_range7_3realizations') as sgems:
    sgems.readline()
    sgems.readline()
    sgems.readline()
    sgems.readline()
    sgems.readline()
    
    for re in range(0,real):
        sgems.readline()
   
    simall = [[float(f) for f in line.split()] for line in sgems]

#Load Existing model
print 'Loading MODFLOW model...\n'
model = fpm.Modflow.load('pm_2l.nam')

#Change directory to folder new model
os.chdir(PATH)

#Writing header to leakage output summary file
header = 'Realization\tTotal Leakage\r\n'
with open('leakage_overview.txt', 'wb') as lek:
    lek.write(header)


#==============================================================================
# Running MODFLOW with K-values of SGS simulation
#==============================================================================
#looping over all realizations
for s in range(0,real):
    print '###############################'   
    print '#        REALIZATION',str(s),'      #'
    print '###############################'

    print '\nSGS simulated K REALIZATION',str(s)
    #Reading SGS simulation for layer x
    print '\nReading SGS file for realization', str(s), '...\n'
    sim = []
    sim[:] = [x[s+3] for x in simall]
    
    
    #create dictionary with element for each layer, store SGS values in dictionary
    simlayer = {}    
    print 'Converting SGS file to matrix for each layer...'
    for l in range (1,layers+1):
        simlayer[str(l)] = sim[rivercells*(5-l-1):rivercells*(5-l)]
        print 'Layer:', l
        
    #Convert ln Kv to Kv
    simlayerK = {}
    meanKlist = []
    print '\nConvert ln Kv to Kv for each layer...'
    for l in range(1,layers+1):
        simlayerK[str(l)] = [np.exp(x) for x in simlayer[str(l)]]
        meanKlist.append(np.mean(simlayerK[str(l)]))
        print 'Layer:', l, '\tMean K = ', np.mean(simlayerK[str(l)])
              
    meanKlist.append(np.mean(meanKlist))
        
    #write SGS categories to riverloc matrix position
    print '\nAssign SGS values to river location...'
    SGS_matrix = {}
    j = 0
    k = 0
    for layer in range(1,5):
        counter = 0
        i = r-2  
        SGS_matrix[str(layer)] = np.full((600, 720), -999.0)
        print 'Layer:', layer
        while i > -1:
            while j < c:
                if rivloc[i][j] == 1:
                    
                    SGS_matrix[str(layer)][i][j] = simlayerK[str(layer)][counter]
                    counter = counter + 1
                    
                j = j+1  
                
            j = 0
            i = i-1
            k = k+1
        np.savetxt('real'+str(s)+'K_l'+str(layer)+'.txt', SGS_matrix[str(layer)])
            
    
    #Read vertical conductivity from lpf package
    print '\nChanging VK riverbed...'
    vka = model.lpf.vka.array
    
    #Change VK at location of river in layers 2 to 5
    for l in xrange(1,5):
        for (i,row) in enumerate(vka[l]):
          for (j,value) in enumerate(row):
            if rivloc[i][j] == 1:
                vka[l][i][j] = SGS_matrix[str(l)][i][j]
    
    #Substitute VK in LPF with new values
    print '\nUpdating LPF package...'
    model.lpf.vka = vka
    
    #Create input files
    print '\nWriting MODFLOW input files...'
    model.write_input()
    
    #Run the model
    print '\nRunning MODFLOW model...\n'
    model.run_model()
    
    #Read CellBudgetFile
    print '\nReading Water Budget...'
    cbb = bf.CellBudgetFile('budget.dat')
    
    #Read Constant Head and Flow Lower Face from CellBudgetFile
    csth = cbb.get_data(text='CONSTANT HEAD', kstpkper=(0,0))[0]
    flf = cbb.get_data(text='FLOW LOWER FACE', kstpkper=(0,0))[0]
    
    #Multiply with zone array Zone1
    csth_zone1 = csth[0]*wbzone1
    flf_zone1 = flf[0]*wbzone1
    
    print '\tLeakage SGeMS realization',str(s),'=', -np.sum(csth_zone1), 'm³/d'
    
    #writing leakage to overview file
    print '\nWriting leakage to file...\n'
    with open('leakage_overview.txt','a') as leak:
        output = str(s)+'\t'+str(-np.sum(csth_zone1))+'\r\n'
        leak.write(output)

##END LOOP

totaltime = time.time() - start_time
print '\nTotal time to run script:', "%.2f" %totaltime, "seconds"

