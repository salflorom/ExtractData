# Author: Santiago A. Flores Roman
# Description: 
# Requirements:
# Instructions:

import os,sys,re
import pandas as pd
import numpy as np
import CoolProp.CoolProp as cp
import scipy.constants as const
import matplotlib.pyplot as plt

kb = const.Boltzmann #kb in J/K
avogadro = const.Avogadro #mol^-1

dirsPath = 'lochness-entries/'
inputSubPath = 'Output/System_0/'
outputRaspaPath = './'

species = 'MIC benzene'
variables = 'L V N P U' 
units = 'kPa'
dimensions = 'x'

# Excecute extractRaspaData.py
# dirs = os.listdir(dirsPath)
# if 'Output' in dirs:
    # outputRaspaFile = f'{dirsPath[:-1]}.dat'
    # os.system(f'python3 extractRaspaData.py -i {dirsPath}/{inputSubPath} '
              # f'-o {outputRaspaPath}{outputRaspaFile} -c {species} '
              # f'-v {variables} -u {units} -d {dimensions} -f -s init')
# else:
    # for i in dirs:
        # outputRaspaFile = f'{i}.dat'
        # os.system(f'python3 extractRaspaData.py -i {dirsPath}{i}/{inputSubPath} '
                  # f'-o {outputRaspaPath}{outputRaspaFile} -c {species} '
                  # f'-v {variables} -u {units} -d {dimensions} -f -s init')

# Read output files.
# dirs = os.listdir(outputRaspaPath)
# reducedData = {'V[A^3]':[],'deltaV[A^3]':[],'x MIC':[],'x benzene':[],'U[K]':[],'deltaU[K]':[],f'P[{units}]':[]}
# for i in dirs:
    # if i.endswith('.dat'):
        # df = pd.read_csv(i,sep='\t')
        # if (i == '0Bnzn10MIC.dat'):
            # reducedData[f'P[{units}]'].append(101.325)
            # reducedData['V[A^3]'].append(df['V[A^3]'][3:].mean())
            # reducedData['deltaV[A^3]'].append(df['V[A^3]'][3:].std())
            # reducedData['U[K]'].append(df['U[K]'].values[0])
            # reducedData['deltaU[K]'].append(df['U[K]'].values[1])
            # reducedData['x MIC'].append(0.0)
            # reducedData['x benzene'].append(1.0)
        # elif (i == '10Bnzn0MIC.dat'):
            # reducedData[f'P[{units}]'].append(101.325)
            # reducedData['V[A^3]'].append(df['V[A^3]'][3:].mean())
            # reducedData['deltaV[A^3]'].append(df['V[A^3]'][3:].std())
            # reducedData['U[K]'].append(df['U[K]'][3:].mean())
            # reducedData['deltaU[K]'].append(df['U[K]'][3:].std())
            # reducedData['x MIC'].append(1.0)
            # reducedData['x benzene'].append(0.0)
        # else:
            # reducedData[f'P[{units}]'].append(df[f'P[{units}]'].mean())
            # reducedData['V[A^3]'].append(df['V[A^3]'][1:].mean())
            # reducedData['deltaV[A^3]'].append(df['V[A^3]'][1:].std())
            # reducedData['U[K]'].append(df['U[K]'][1:].mean())
            # reducedData['deltaU[K]'].append(df['U[K]'][1:].std())
            # reducedData['x MIC'].append(df['N MIC'][0]/(df['N MIC'][0]+df['N benzene'][0]))
            # reducedData['N MIC'].append(df['N MIC'].mean())
            # reducedData['x benzene'].append(df['N benzene'][0]/(df['N MIC'][0]+df['N benzene'][0]))
            # reducedData['N benzene'].append(df['N benzene'].mean())
# reducedData = pd.DataFrame(reducedData)
# reducedData.sort_values('x MIC',inplace=True,ignore_index=True)
# reducedData['V[m^3]'] = reducedData['V[A^3]']*1e-30
# reducedData['deltaV[m^3]'] = reducedData['deltaV[A^3]']*1e-30
# reducedData['H[K]'] = reducedData['U[K]']+reducedData[f'P[{units}]']*reducedData['V[m^3]']*1e-3/kb
# reducedData['deltaH[K]'] = reducedData['deltaU[K]']+reducedData[f'P[{units}]']*reducedData['deltaV[m^3]']*1e-3/kb
# reducedData['mixV[m^3/mol]'] = (reducedData['V[m^3]'].values-(reducedData['x benzene']*reducedData['V[m^3]'].values[0]+reducedData['x MIC']*reducedData['V[m^3]'].values[-1]))*avogadro #Check
# reducedData['mixH[K/mol]'] = (reducedData['H[K]'].values-(reducedData['x benzene']*reducedData['H[K]'].values[0]+reducedData['x MIC']*reducedData['H[K]'].values[-1]))*avogadro*kb*1e-6  #Check
# reducedData['mixV[m^3/mol]'][1:-1] -= reducedData['mixV[m^3/mol]'][1:-1].mean() #Check
# reducedData['mixH[K/mol]'][1:-1] -= reducedData['mixH[K/mol]'][1:-1].mean() #check
# reducedData['deltamixV[m^3/mol]'] = 0.25*abs(reducedData['deltaV[m^3]'].values-(reducedData['x benzene']*reducedData['deltaV[m^3]'].values[0]+reducedData['x MIC']*reducedData['deltaV[m^3]'].values[-1]))*avogadro
# reducedData['deltamixH[K/mol]'] = abs(reducedData['deltaH[K]'].values-(reducedData['x benzene']*reducedData['deltaH[K]'].values[0]+reducedData['x MIC']*reducedData['deltaH[K]'].values[-1]))*avogadro*kb*1e-6
# print(reducedData)


# # Read paper files.
# experData = {'rho[kg/m^3]':[],'Beta_T[GPa^-1]':[],'T[K]':[]}
# for i in range(len(reducedData['T[K]'])):
    # # print(cp.PropsSI('isothermal_compressibility','P',101325,'T',reducedData['T[K]'][i],'water'))
    # beta_T = cp.PropsSI('isothermal_compressibility','P',reducedData['P[Pa]'][i],'T',reducedData['T[K]'][i],'water')*1e9
    # density = cp.PropsSI('D','P',reducedData['P[Pa]'][i],'T',reducedData['T[K]'][i],'water')
    # experData['rho[kg/m^3]'].append(density)
    # experData['Beta_T[GPa^-1]'].append(beta_T)
    # experData['T[K]'].append(reducedData['T[K]'][i])
# experData = pd.DataFrame(experData)
# experData['K_T[GPa]'] = 1/experData['Beta_T[GPa^-1]']
# print(experData)

# # Plot dataframes.
# fig,axs = plt.subplots(1)
# # reducedData.plot(x='x MIC',y='mixV[m^3]',ax=axs,style='.',legend=False)
# reducedData.plot(x='x MIC',y='mixV[m^3/mol]',ax=axs,yerr='deltamixV[m^3/mol]',capsize=3,fmt='.',legend=False)
# axs.plot(np.linspace(0,1,50),[0 for i in np.linspace(0,1,50)],'k--')
# axs.set_ylabel('$\Delta_{exss}V$ [$cm^3/mol$]')
# axs.set_xlabel('Mole fraction of MIC')
# axs.set_xticks([i for i in np.linspace(0,1,11)])
# fig.tight_layout()
# fig.savefig('ExssV.pdf')

# fig,axs = plt.subplots(1)
# # reducedData.plot(x='x MIC',y='mixH[K]',ax=axs,style='.',legend=False)
# reducedData.plot(x='x MIC',y='mixH[K/mol]',ax=axs,yerr='deltamixH[K/mol]',capsize=3,fmt='.',legend=False)
# axs.plot(np.linspace(0,1,50),[0 for i in np.linspace(0,1,50)],'k--')
# axs.set_ylabel('$\Delta_{exss}H$ [kJ/mol]')
# axs.set_xlabel('Mole fraction of MIC')
# axs.set_xticks([i for i in np.linspace(0,1,11)])
# fig.tight_layout()
# fig.savefig('ExssH.pdf')

print(50.5*kb*avogadro*2.39e-4)
