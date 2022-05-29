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
planck = const.Planck #J*s

# Excecutes extractRaspaData.py
def ExecuteExtractRaspaDataPy(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section,sort):
    dirs = os.listdir(dirsPath)
    if 'Output' in dirs:
        outputRaspaFile = re.split('/',dirsPath)[-2]+'.dat'
        os.system(f'python3 extractRaspaData.py -i {dirsPath}/{inputSubPath} '
                  f'-o {outputRaspaPath}{outputRaspaFile} -c {species} '
                  f'-v {variables} -u {units} -d {dimensions} -f -t {section} -s {sort}')
    else:
        for i in dirs:
            outputRaspaFile = f'{i}.dat'
            os.system(f'python3 extractRaspaData.py -i {dirsPath}{i}/{inputSubPath} '
                      f'-o {outputRaspaPath}{outputRaspaFile} -c {species} '
                      f'-v {variables} -u {units} -d {dimensions} -f -t {section} -s {sort}')
# Reads outputs from extractRaspaData.py and creates a Pandas DataFrame.
def SearchDataFiles(dirsPath,outputRaspaPath):
    dataFilesPath = outputRaspaPath+'dataFiles/'
    dataFiles = ' '.join(os.listdir(dataFilesPath))
    dataFileNames = os.listdir(dirsPath)
    dataFilesPerName = {}
    for name in dataFileNames: 
        findDataFile = re.findall(f'\s\d+_{name}|^\d+_{name}',dataFiles)
        if (len(findDataFile) != 0): dataFilesPerName[name] = findDataFile
    return dataFilesPerName
def CreateDataFrame(outputRaspaPath,dataFileName,inputSubPath,variables,units,dimensions,species,sort,countFrom):
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
        elif (var == 'IdMu'): 
            var += '[K]'
            deltaVar = 'delta'+var
            spcs = species.split(' ')
            for i in range(len(spcs)):
                spcVar = var+f' {spcs[i]}'; reducedData[spcVar] = []
                deltaVar += f' {spcs[i]}'; reducedData[deltaVar] = []
        elif (var == 'ExMu'): 
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
                if (df[var].count() > 1):
                    reducedData[var].append(df[var][countFrom:].mean())
                    reducedData['delta'+var].append(df[var][countFrom:].std())
                elif (df[var].count() == 1):
                    reducedData[var].append(df[var].values[0])
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
def JoinDataFrames(dataFrames,sort):
    concatDataFrame = pd.concat(dataFrames).reset_index()
    concatDataFrame.drop(columns={'level_1'},inplace=True)
    concatDataFrame.rename(columns={'level_0':'Directory'},inplace=True)
    for key in concatDataFrame.columns:
        findSortValue = re.search(f'^{sort}\[.+',key)
        if findSortValue: concatDataFrame.sort_values(findSortValue.group(),ignore_index=True,inplace=True)
    return concatDataFrame
def ExtractFromRaspa(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section,sort,joinDataFrames,countFrom):
    dataFiles = SearchDataFiles(dirsPath,outputRaspaPath)
    dataFrames = {}
    for name in sorted(dataFiles.keys()): 
        dataFrames[name] = CreateDataFrame(outputRaspaPath,name,inputSubPath,variables,units,dimensions,species,sort,countFrom)
        print('\n'+name)
        print(dataFrames[name])
    if joinDataFrames: 
        dataFrame = JoinDataFrames(dataFrames,sort)
        print('\nConcatenated dataframe:'); print(dataFrame)
        return dataFrame
    return dataFrames
####################################################################################################################
####################################################################################################################
if __name__=='__main__':
    # Input parameters.
    dirsPath = '../lochness-entries/'
    inputSubPath = 'Output/System_0/'
    outputRaspaPath = '../'

    species = 'TIP4P-2005'
    variables = 'ExMu P T N V' 
    units = 'kPa' #Available units: kPa, bar, atm.
    dimensions = 'x'
    section = 'prod'
    sort = None
    sortDataFrames = 'P'
    countDataFrom = 0
    joinDataFrames = True

    # Running code.
    # ExecuteExtractRaspaDataPy(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section,sort)
    raspaData = ExtractFromRaspa(dirsPath,inputSubPath,outputRaspaPath,species,variables,units,dimensions,section,
                                 sortDataFrames,joinDataFrames,countDataFrom)
    print()

    ###############################################################################################################
    ############### From now on, the lines below have to be edited by the user. ###################################
    # # Edit raspaData.
    # raspaData['ExMu[kcal/mol]'] = raspaData['ExMu[K] TIP4P-2005']*kb*avogadro*2.39e-4
    # raspaData['deltaExMu[kcal/mol]'] = raspaData['deltaExMu[K] TIP4P-2005']*kb*avogadro*2.39e-4
    # raspaData['Rho[m^-3]'] = raspaData['N TIP4P-2005']/raspaData['V[A^3]']*1e30
    # TIP4P2005mass = 18.015e-3/avogadro #kg
    # debroglie = np.sqrt(planck**2/(2.0*np.pi*TIP4P2005mass*kb*raspaData['T[K]']))
    # p0 = raspaData['P[kPa]'].values[1]
    # mu0 = raspaData['T[K]']*np.log(raspaData['Rho[m^-3]'].values[1]*debroglie**3)*kb*avogadro*2.39e-4
    # raspaData['p/p0'] = raspaData['P[kPa]']/p0
    # raspaData['IdMu[kcal/mol]'] = mu0 + raspaData['T[K]']*np.log(raspaData['p/p0'])*kb*avogadro*2.39e-4
    # raspaData['Mu[kcal/mol]'] = raspaData['IdMu[kcal/mol]']+raspaData['ExMu[kcal/mol]']
    # raspaData['IdMu[K]'] = raspaData['IdMu[kcal/mol]']/(kb*avogadro)*4184
    # raspaData['deltaMu[kcal/mol]'] = raspaData['deltaExMu[kcal/mol]']
    # print(raspaData[['p/p0','Mu[kcal/mol]','IdMu[kcal/mol]','ExMu[kcal/mol]','deltaMu[kcal/mol]']])

    # # Read paper files.
    # paperData = pd.read_csv('../paperIsotherm-10A-300K.csv',skiprows=5,sep=',')[:-1]
    # print(paperData)

    # # Plot dataframes.
    # fig,axs = plt.subplots(1)
    # raspaData.plot(x='p/p0',y='Mu[kcal/mol]',ax=axs,yerr='deltaMu[kcal/mol]',capsize=3,fmt='.',label='$\mu_{W}$')
    # raspaData.plot(x='p/p0',y='IdMu[kcal/mol]',ax=axs,style='--',label='$\mu_{id}$')
    # axs.set_ylabel('$\mu$ [kcal/mol]'); axs.set_xlabel('$P/P_0$')
    # axs.legend()
    # fig.tight_layout()
    # fig.savefig('../JasonMu.pdf')
