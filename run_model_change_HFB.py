# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 16:30:31 2018

@author: gghysels

Script that changes the parameters of the Horizontal-Flow Boundary (HFB) Package in a MODFLOW model,
in order to analyze the effect of lateral exchange fluxes through river banks.
"""

import os
import numpy as np
import subprocess
import sys
import pandas as pd
import matplotlib.pyplot as plt 

wdir = 'WORKING_DIR'
os.chdir(wdir)

#Define the range over which the K/T parameter in the HFB package will be varied, and the step size it will increase each run 
K_T_min = 0.0
K_T_max = 20.0
K_T_step = 0.1

#List of K_Tvalues
K_Tlist = np.arange(K_T_min,K_T_max+K_T_step,K_T_step)
np.append(K_Tlist,10.31) #Append K/T based on measurements K banks Baya Veliz 2017
A = 14406.25 #Area of river cells

#Create empty dataframe to store leakage data
df = pd.DataFrame(columns=['K','Total Leakage','Bank Leakage','Bed Leakage','Horizontal Bed Leakage','Vertical Bed Leakage'])


#open HFB6file, store as matrix
print 'Reading HFB6 file...\n'
hfb = np.genfromtxt('hfb6p_Copy.dat', skip_header=3, skip_footer=2)

with open("hfb6p_Copy.dat") as hfbfile:
    
    hfb_all = hfbfile.readlines()

header = ''.join(hfb_all[:3])
head = header[:-2]
foot = ''.join(hfb_all[-2:])


#Looping over all K_T values in K_Tlist
for s in range(0,len(K_Tlist)):    

    print '###############################'   
    print '#        SIMULATION',str(s),'        #'
    print '###############################'

    #Change K/T parameter in hfb array to specific value
    K_T = K_Tlist[s]
    K = K_T/2.0
    hfb[:, -1] = K_T
    
    print 'Writing new HFB6 file...'
    np.savetxt('hfb6p.dat', hfb, fmt=['%d', '%d', '%d', '%d', '%d', '%.2f'], header=head, footer=foot, comments='')
    print '\t K/T set to', K_T
    
    
    #Check MODFLOW batch file
    path = os.getcwd()
    batchname = '/MODFLOWbat.BAT'
    extraline = 'C:\n'
    newline = '\r\n'
    secondline = 'mf2005.exe<startit'
    
    with open("MODFLOW.BAT") as batch:
        result = [line for line in batch]
    print '\nChecking MODFLOW.bat file...'
    
    with open("MODFLOWbat.bat", "wb") as newbatch:
        if result[0] == extraline:
            print '\tMODFLOW Batch file not modified.'
            
            for r in result[:-1]: 
                newbatch.write(r+newline)
        else:
            newbatch.write(extraline+newline)
            print '\tMODFLOW Batch file is modified.\n\t'+extraline[:-1]+' added to top of file.'
            
            if result[1][:2] == 'c:':
                newbatch.write(result[0]+newline)
                newbatch.write(secondline+newline)
                print '\tDeleted path on second line.'
                            
            for r in result[2:-1]: 
                newbatch.write(r+newline)
            print '\tDeleted last line (@PAUSE).'
            print '\tCreated MODFLOWbat.BAT.'       
            
    
    #run MODFLOW-batch file
    print '\nRunning MODFLOW...'        
    try:
        p=subprocess.Popen(path+batchname, shell=True)
        p.wait()
        print '\nMODFLOW model ran succesfully!\n'
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        print '\nSomething went wrong, try again\n'
        
    
    #CHECK WATERBUDGET FILE
    WBL = '\BUDGET.BAT'
    print 'Checking PMWBL.bat file...'
    
    with open("PMWBL.BAT") as budget:
        budgetfile = [line for line in budget]
        
        
    with open("BUDGET.bat", "wb") as newbudget:
        
            for b in budgetfile[:-2]: 
                newbudget.write(b+newline)
            print '\tDeleted last two lines.'
            print '\tCreated BUDGET.BAT.'
    
    
    #run WATERBUDGET               
    try:
        p=subprocess.Popen(path+WBL, shell=True)
        p.wait()
        print '\nWATERBUDGET ran succesfully!'
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        print '\nSomething went wrong, try again'
        
        
    leakline = []
    #Opening waterbudget file, reading leakage
    print '\nReading WATERBUDGET file...'
    with open('WATERBDG.dat') as bud:
        budtext = [[str(f) for f in line.split()] for line in bud]
        
    total_leakage = float(budtext[20][3])
    bank_leakage = float(budtext[21][2])
    bed_leakage = float(budtext[23][2])
    bed_leakage_h = float(budtext[47][4])
    bed_leakage_v = float(budtext[49][2])
    
    #Convert from m³/d to mm/d
    total_leakage_mmd = (total_leakage/A)*1000
    bank_leakage_mmd = (bank_leakage/A)*1000
    bed_leakage_mmd = (bed_leakage/A)*1000
    bed_leakage_h_mmd = (bed_leakage_h/A)*1000
    bed_leakage_v_mmd = (bed_leakage_v/A)*1000
    
    
    #Print out leakage components
    print '\tTotal Leakage =', total_leakage, 'm³/d = ', total_leakage_mmd, 'mm/d'
    print '\t\tRiverbank Leakage =', bank_leakage, 'm³/d = ', bank_leakage_mmd, 'mm/d'
    print '\t\tRiverbed Leakage =', bed_leakage, 'm³/d = ', bed_leakage_mmd, 'mm/d'
    print '\t\t\t Horizontal Component =', bed_leakage_h, 'm³/d = ', bed_leakage_h_mmd, 'mm/d'
    print '\t\t\t Vertical Component =', bed_leakage_v, 'm³/d = ', bed_leakage_v_mmd, 'mm/d\n\n'
    
    #Check if leakages are consistent
    if total_leakage != round(bank_leakage + bed_leakage, 4):
        print 'Error: Total Leakage not equal to sum of Bank and Bed Leakage'
        
    #Store leakage data in dataframe   
    data = pd.DataFrame({'K': [K], 'Total Leakage': [total_leakage_mmd],'Bank Leakage': [bank_leakage_mmd],'Bed Leakage': [bed_leakage_mmd],'Horizontal Bed Leakage': [bed_leakage_mmd],'Vertical Bed Leakage': [bed_leakage_mmd]})
    df = df.append(data)


#Plot of leakage data vs K/T
fig = plt.figure(1)
plt.plot(df['K'], df['Total Leakage'], 'bo', markersize=3)
plt.plot(df['K'], df['Bed Leakage'], 'r^', markersize=3)
plt.plot(df['K'], df['Bank Leakage'], 'gs', markersize=3)
plt.xlabel('K$_{bank}$ (m/d)')
plt.ylabel('Exchange Flux (mm/d)')
plt.show()

fig.savefig('Leakage_vs_KT_test.png', dpi=200, bbox_inches='tight')
fig.savefig('Leakage_vs_KT_test.pdf', dpi=200, bbox_inches='tight')
