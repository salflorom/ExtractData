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

kb = const.Boltzmann #kb in J/K
avogadro = const.Avogadro #mol^-1
planck = const.Planck #J*s

class SummarizeDataFrames():
    def __init__(self,dataFilesPath,groups,sort,joinDataFrames,countFrom):
        self.dataFilesPath = dataFilesPath
        self.groups = groups.split()
        self.joinDataFrames = joinDataFrames
        self.countDataFrom = countFrom
        self.sortDataFramesBy = sort
        self.summedDataFrame, self.summedDataFrames, self.groupedDataFrames = {}, {}, {}
    def SearchDataFiles(self):
        dataFilesPath = self.dataFilesPath
        groups = self.groups
        countFrom = self.countDataFrom
        dataFileNames = os.listdir(dataFilesPath)
        groupedDataFrames = {i:[] for i in groups}
        for dataFile in dataFileNames: 
            dataFrame = pd.read_csv(dataFilesPath+dataFile,sep='\t')
            dfFirstRow = dataFrame[:1]
            dataFrame = pd.concat([dfFirstRow,dataFrame[countFrom:]])
            for i in groups:
                if re.search(i,dataFile): groupedDataFrames[i].append(dataFrame)
        self.groupedDataFrames = groupedDataFrames
    def JoinDataFrames(self):
        sort = self.sortDataFramesBy
        dataFrames = self.summedDataFrames
        concatDataFrame = pd.concat(dataFrames).reset_index()
        concatDataFrame.drop(columns={'level_1'},inplace=True)
        concatDataFrame.rename(columns={'level_0':'Group'},inplace=True)
        for key in concatDataFrame.columns:
            findSortValue = re.search(f'^{sort}\[.+',key)
            if findSortValue: concatDataFrame.sort_values(findSortValue.group(),ignore_index=True,inplace=True)
        print('Data Frame:\n')
        print(concatDataFrame)
        self.summedDataFrame = concatDataFrame
    def SetSummedDataFrames(self):
        groups = self.groups
        summedDataFrames = self.summedDataFrames
        for i in groups:        
            summedDataFrames[i] = pd.DataFrame(columns=[])
        self.summedDataFrames = summedDataFrames
    def CreateSummedDataFrames(self):
        sort = self.sortDataFramesBy
        groups = self.groups
        groupedDataFrames = self.groupedDataFrames
        summedDataFrames = self.summedDataFrames
        for i in groups:
            for var in groupedDataFrames[i][0].columns:
                summedDataFrames[i][var] = pd.Series([groupedDataFrames[i][j][var].mean() for j in range(len(groupedDataFrames[i]))])
                summedDataFrames[i][f'delta{var}'] = pd.Series([groupedDataFrames[i][j][var].std() for j in range(len(groupedDataFrames[i]))])
            summedDataFrames[i].sort_values(sort,ignore_index=True,inplace=True)
        self.summedDataFrames = summedDataFrames
    def Extract(self):
        self.SearchDataFiles()
        self.SetSummedDataFrames()
        self.CreateSummedDataFrames()
        dataFrames = self.summedDataFrames
        groups = self.groups
        for i in groups:
            print('\n'+i)
            print(dataFrames[i])
def SumUpDataFrames(dataFilesPath,groups,sortDataFrames,joinDataFrames,countDataFrom):
    data = SummarizeDataFrames(dataFilesPath,groups,sortDataFrames,joinDataFrames,countDataFrom)
    data.Extract()
    if joinDataFrames:
        data.JoinDataFrames()
        return data.summedDataFrame
    else: return data.summedDataFrames
####################################################################################################################
####################################################################################################################
if __name__=='__main__':
    # Input parameters.
    dataFilesPath = './analysis/dataFiles/'
    groups = 'JX101CH4 JX101N2 MCM41CH4 MSC5ACH4'
    sortDataFrames = 'Mu[K]'
    countDataFrom = 750
    joinDataFrames = False
    
    dataFrames = SumUpDataFrames(dataFilesPath,groups,sortDataFrames,joinDataFrames,countDataFrom)

    ###############################################################################################################
    ############### From now on, the lines below have to be edited by the user. ###################################
    # # Edit data frames.
    # for i in groups.split():
        # dataFrames[i]['Rho[mol/m^3]'] = (dataFrames[i]['N']/dataFrames[i]['V[A^3]'])/avogadro*1e30
        # dataFrames[i]['deltaRho[mol/m^3]'] = (dataFrames[i]['deltaN']/dataFrames[i]['V[A^3]'])/avogadro*1e30
        # print(i+'\n',dataFrames[i])

    # # Read paper files.
    # paperData = pd.read_csv('../paperIsotherm-10A-300K.csv',skiprows=5,sep=',')[:-1]
    # print(paperData)

    # # Plot dataframes.
    # fig,axs = plt.subplots(1)
    # for i in groups.split():
        # dataFrames[i].plot(x='Mu[K]',y='Rho[mol/m^3]',ax=axs,yerr='deltaRho[mol/m^3]',capsize=3,fmt='1',label=i)
    # axs.set_xlabel('$\mu$ [K]'); axs.set_ylabel('Amount adsorbed [mol/$m^3$]')
    # fig.tight_layout()
    # fig.savefig('./analysis/rhoVsMu.pdf')
