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

# Excecutes extractRaspaData.py
def ExecuteExtractRaspaDataPy(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section):
    dirs = os.listdir(dirsPath)
    if 'Output' in dirs:
        outputRaspaFile = f'{dirsPath[:-1]}.dat'
        os.system(f'python3 extractRaspaData.py -i {dirsPath}/{inputSubPath} '
                  f'-o {outputRaspaPath}{outputRaspaFile} -c {species} '
                  f'-v {variables} -u {units} -d {dimensions} -f -s {section}')
    else:
        for i in dirs:
            outputRaspaFile = f'{i}.dat'
            os.system(f'python3 extractRaspaData.py -i {dirsPath}{i}/{inputSubPath} '
                      f'-o {outputRaspaPath}{outputRaspaFile} -c {species} '
                      f'-v {variables} -u {units} -d {dimensions} -f -s {section}')
# Reads outputs from extractRaspaData.py and creates a Pandas DataFrame.
def CreateDataFrame(outputRaspaPath,variables,units,dimensions,species,sort):
    # Create preDataFrame (dictionary with the column names).
    reducedData = {}
    for var in variables.split(' '):
        # Units handled in Raspa.
        if (var == 'Rho'):
            var += ' [kg/m^3]'
            deltaVar = 'delta'+var
            for spcs in range(len(species.split(' '))):
                spcVar =  var+f' {species[spcs]}'; reducedData[spcVar] = []
                deltaVar += ' {species[scpcs]}'; reducedData[deltaVar] = []
        elif (var == 'N'): 
            deltaVar = 'delta'+var
            for spcs in range(len(species.split(' '))):
                spcVar = var+f' {species[spcs]}'; reducedData[var] = []
                deltaVar += ' {species[scpcs]}'; reducedData[deltaVar] = []
        elif (var == 'V'): 
            var += f' [A^3]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'P'): 
            var += f' [{units}]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'T'): 
            var += f' [K]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'U'): 
            var += f' [K]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'Mu'): 
            var += f' [K]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
    #Create DataFrame
    dirs = os.listdir(outputRaspaPath)
    for i in dirs:
        if i.endswith('.dat'):
            df = pd.read_csv(outputRaspaPath+i,sep='\t')
            for var in df.columns:
                if (df[var].count() > 2):
                    reducedData[var].append(df[var][3:].mean())
                    reducedData['delta'+var].append(df[var][3:].std())
                elif (df[var].count() == 2):
                    reducedData[var].append(df[var].values[0])
                    reducedData['delta'+var].append(df[var].values[1])
                else:
                    reducedData[var].append(df[var].values[0])
                    reducedData['delta'+var].append(0.0)
    reducedData = pd.DataFrame(reducedData)
    reducedData.sort_values(sort) 
    print(reducedData)
    return reduceData
if __name__=='__main__':
    # Input parameters.
    dirsPath = '../lochness-entries/'
    inputSubPath = 'Output/System_0/'
    outputRaspaPath = '../'

    species = 'TIP4P-2005'
    variables = 'Rho N V P T' 
    units = 'kPa' #Available units: kPa, bar, atm.
    dimensions = 'x'
    section = 'prod'
    sort = 'P'

    # Running code.
    ExecuteExtractRaspaDataPy(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section)
    # CreateDataFrame(outputRaspaPath,variables,units,dimensions,species,sort)

    # From now on, the lines below have to be edited by the user.
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
