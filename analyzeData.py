# Author: Santiago A. Flores Roman
# Description: 
# Requirements:
# Instructions:

import os,sys,re
import pandas as pd
import numpy as np
import scipy.constants as const
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import extractData as extData

kb = const.Boltzmann #kb in J/K
avogadro = const.Avogadro #mol^-1
planck = const.Planck #J*s
Rg = const.R #J/(mol*K)

# Input parameters.
dataFilesPath = '../analysis/dataFiles/'
groups = 'lj sqw'
sortDataFrames = 'N'
countDataFrom = 8500
joinDataFrames = False

# Extract data.
dataFrames = extData.SumUpDataFrames(dataFilesPath,groups,sortDataFrames,joinDataFrames,countDataFrom)

# Process data.
temp = dataFrames['lj']['T[K]'].values[0]
mass = 16.04/avogadro*1e-3 #kg
thermalWL = planck/np.sqrt(2*np.pi*mass*kb*temp)
for i in groups.split():
    dataFrames[i]['P[Pa]'] = dataFrames[i]['N']*kb*dataFrames[i]['T[K]']/(dataFrames[i]['V[A^3]']*1e-30)
    dataFrames[i]['P[kPa]'] = dataFrames[i]['P[Pa]']*1e-3
    dataFrames[i]['IdMu[kJ/mol]'] = Rg*temp*np.log(dataFrames[i]['P[Pa]']*thermalWL**3/(kb*temp))*1e-3
    dataFrames[i]['Mu[kJ/mol]'] = dataFrames[i]['IdMu[kJ/mol]']+dataFrames[i]['Mu[K]']*Rg*1e-3
    dataFrames[i]['deltaMu[kJ/mol]'] = dataFrames[i]['deltaMu[K]']*Rg*1e-3
    print(i+'\n',dataFrames[i])

# Read paper files.
press = dataFrames['lj']['P[kPa]']
paperData = pd.DataFrame({'P[kPa]':press,'IdMu[kJ/mol]':dataFrames['lj']['IdMu[kJ/mol]']})
print('Reference')
print(paperData)

# Plot dataframes.
fig,axs = plt.subplots(1)
dataFrames['lj'][:-4].plot(x='P[kPa]',y='Mu[kJ/mol]',ax=axs,yerr='deltaMu[kJ/mol]',capsize=3,fmt='1',label='Lennard-Jones')
dataFrames['sqw'][:-3].plot(x='P[kPa]',y='Mu[kJ/mol]',ax=axs,yerr='deltaMu[kJ/mol]',capsize=3,fmt='2',label='Square Well')
paperData.plot(x='P[kPa]',y='IdMu[kJ/mol]',ax=axs,style='--',label='Ideal')
axs.set_xlabel('P [kPa]'); axs.set_ylabel('$\mu$ [kJ/mol]')
fig.tight_layout()
fig.savefig('../analysis/PVsMu.pdf')
