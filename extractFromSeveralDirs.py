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
        outputRaspaFile = re.split('/',dirsPath)[-2]+'.dat'
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
def SearchDataFiles(dirsPath,outputRaspaPath):
    dataFilesPath = outputRaspaPath+'dataFiles/'
    dataFiles = ' '.join(os.listdir(dataFilesPath))
    dataFileNames = os.listdir(dirsPath)
    dataFilesPerName = {}
    for name in dataFileNames: dataFilesPerName[name] = re.findall(f'\s\d+_{name}|^\d+_{name}',dataFiles)
    return dataFilesPerName
def CreateDataFrame(outputRaspaPath,dataFileName,inputSubPath,variables,units,dimensions,species,sort):
    # Create preDataFrame (dictionary with the column names).
    reducedData = {}
    for var in variables.split(' '):
        # Units handled in Raspa.
        if (var == 'Rho'):
            var += '[kg/m^3]'
            deltaVar = 'delta'+var
            spcs = species.split(' ')
            for i in range(len(spcs)):
                spcVar =  var+f' {spcs[i]}'; reducedData[spcVar] = []
                deltaVar += f' {spcs[i]}'; reducedData[deltaVar] = []
        elif (var == 'N'): 
            deltaVar = 'delta'+var
            spcs = species.split(' ')
            for i in range(len(spcs)):
                spcVar = var+f' {spcs[i]}'; reducedData[spcVar] = []
                deltaVar += f' {spcs[i]}'; reducedData[deltaVar] = []
        elif (var == 'V'): 
            var += f'[A^3]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'P'): 
            var += f'[{units}]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'T'): 
            var += f'[K]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'U'): 
            var += f'[K]'; reducedData[var] = []
            deltaVar = 'delta'+var; reducedData[deltaVar] = []
        elif (var == 'Mu'): 
            var += '[K]'
            deltaVar = 'delta'+var
            spcs = species.split(' ')
            for i in range(len(spcs)):
                spcVar = var+f' {spcs[i]}'; reducedData[spcVar] = []
                deltaVar += f' {spcs[i]}'; reducedData[deltaVar] = []
    #Create DataFrame
    dirs = os.listdir(outputRaspaPath+'dataFiles/')
    for i in dirs:
        if i.endswith(f'{dataFileName}.dat'):
            df = pd.read_csv(outputRaspaPath+'dataFiles/'+i,sep='\t')
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
    for var in reducedData.keys():
        reducedData[var] = pd.Series(reducedData[var],index=range(len(reducedData[var])))
    reducedData = pd.DataFrame(reducedData)
    for key in reducedData.columns:
        sortVal = re.search('^'+sort+'.+',key)
        if sortVal: 
            reducedData.sort_values(sortVal.group(),inplace=True,ignore_index=True)
            break
    return reducedData
if __name__=='__main__':
    # Input parameters.
    dirsPath = '../lochness-entries/6_try/'
    inputSubPath = 'Output/System_0/'
    outputRaspaPath = '../'

    species = 'TIP4P-2005'
    variables = 'Mu P T N V Rho' 
    units = 'kPa' #Available units: kPa, bar, atm.
    dimensions = 'x'
    section = 'init prod'
    sort = 'P'

    # Running code.
    # ExecuteExtractRaspaDataPy(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section)
    dataFiles = SearchDataFiles(dirsPath,outputRaspaPath)
    dataFrames = {}
    for name in sorted(dataFiles.keys()): 
        dataFrames[name] = CreateDataFrame(outputRaspaPath,name,inputSubPath,variables,units,dimensions,species,sort)
        print('\n'+name)
        print(dataFrames[name])

    ###############################################################################################################
    ############### From now on, the lines below have to be edited by the user. ###################################
    # Edit raspaData.
    # pSat300K = 778e-3 #Saturation pressure at 300 K in kPa.
    # raspaData['Rho[g/cm^3]'] = raspaData['Rho[kg/m^3] TIP4P-2005']*1e-3
    # raspaData['deltaRho[g/cm^3]'] = raspaData['deltaRho[kg/m^3] TIP4P-2005']*1e-3
    # raspaData['p/p0'] = raspaData['P[kPa]']/pSat300K*0.036
    # print(raspaData)

    # # Read paper files.
    # paperData = pd.read_csv('../paperIsotherm-10A-300K.csv',skiprows=5,sep=',')[:-1]
    # print(paperData)

    # # Plot dataframes.
    # fig,axs = plt.subplots(1)
    # raspaData[8:].plot(x='p/p0',y='Rho[g/cm^3]',ax=axs,yerr='deltaRho[g/cm^3]',capsize=3,fmt='.',label='RASPA-GCMC')
    # paperData.plot(x='p/p0',y='rho[g/cm^3]',ax=axs,style='--',label='Guse, C.\'s',logx=True)
    # axs.set_ylabel('$\\rho$ [g/$cm^3$]'); axs.set_xlabel('$P/P_0$')
    # axs.legend()
    # fig.tight_layout()
    # fig.savefig('../Guse10A.pdf')
