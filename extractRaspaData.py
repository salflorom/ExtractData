# Author: Santiago A. Flores Roman
# Description: This script extracts the requested data from the data files generated by RASPA.
# Requirements: Numpy, Pandas and matplotlib have to be installed.
# Instructions: 
#   This script assumes that there is only one data file per Output/System_#/ directory. The reason
#   is that several points can be run at the same time in Slurm, acceleating the simulation. If there
#   are several data files in one directory, then RASPA will have simulated point by point, which is 
#   slow as the program is not parallelized.
#   Run the script as following for more information.
#   python3 extractRaspaData.py -h 

import os,re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sys import argv,exit
##########################################################################################################
def ExtractVolumes(fileLines,sections):
    volumes = []
    for sec in sections:
        if (sec.lower() == 'init'):
            for line in range(len(fileLines)):
                findVolume = re.search(r'^Volume:\s+(\d+\.?\d*)\s+\[A\^3\]$',fileLines[line])
                if findVolume: volumes.append(float(findVolume.group(1))) #A^3
        elif (sec.lower() == 'prod'):
            for line in range(len(fileLines)):
                findVolume = re.search(r'Volume:\s+(\d+\.?\d*).+Average\s+Volume:',fileLines[line])
                if findVolume: volumes.append(float(findVolume.group(1))) #A^3
    return volumes
def ExtractPressures(fileName,fileLines,unit,sections):
    pressures = []
    for sec in sections:
        if (sec.lower() == 'init'):
            print('Warning: Pressure is not calculated by RASPA during initialization and equilibration cycles.')
            print('Extracting fixed external pressure.')
            for line in range(len(fileLines)):
                findPressure = re.search(f'.+_(\d+\.?\d*)\.data',fileName)
                if findPressure: 
                    if unit == 'bar': pressures.append(float(findPressure.group(1))*1e-5); break
                    elif unit == 'atm': pressures.append(float(findPressure.group(1))*9.896e-6); break
                    else: pressures.append(float(findPressure.group(1))*1e-3); break #kPa
        elif (sec.lower() == 'prod'):
            for line in range(len(fileLines)):
                findPressure = re.search(f'Average Pressure:.+?(\d+\.\d*)\s+\[{unit}\]',fileLines[line])
                if (findPressure and float(findPressure.group(1)) != 0.0): 
                    pressures.append(float(findPressure.group(1)))
            if (len(pressures) == 0):
                print('No molecular pressures were found. Extracting fixed external pressure.')
                findPressure = re.search(f'.+_(\d+\.?\d*)\.data',fileName)
                if unit == 'bar': pressures.append(float(findPressure.group(1))*1e-5)
                elif unit == 'atm': pressures.append(float(findPressure.group(1))*9.896e-6)
                else: pressures.append(float(findPressure.group(1))*1e-3) #kPa
    return pd.Series(pressures,index=range(len(pressures)))
def ExtractTemperatures(fileName,fileLines,sections):
    temperatures = []
    for sec in sections:
        if (sec.lower() == 'init'):
            print('Warning: Temperature is not calculated by RASPA during initialization cycles.')
            for line in range(len(fileLines)):
                findTemperature = re.search(f'^Temperature:\s+(\d+\.?\d*)$',fileLines[line])
                if findTemperature: temperatures.append(float(findTemperature.group(1)))
        elif (sec.lower() == 'prod'):
            for line in range(len(fileLines)):
                findTemperature = re.search(f'Temperature:\s+(\d+\.?\d*).+Translational',fileLines[line])
                if findTemperature: temperatures.append(float(findTemperature.group(1)))
        if (len(temperatures) == 0):
            print('No molecular temperatures were found. Extracting fixed external temperatures.')
            temperatures.append(float(re.search('.+_(\d+\.?\d*)_\d+\.?\d*\.data',fileName).group(1)))
    return pd.Series(temperatures,index=range(len(temperatures)))
def ExtractInternalEnergy(fileLines,sections):
    for sec in sections:
        if (sec.lower() == 'init'):
            print('Warning: Internal energy is not calculated by RASPA during initialization, equilibration and production cycles.')
            print('Conserved energy will be extracted. It is calculated after initialization cycles (from equilibration and production cycles).')
            energies = []
            for line in range(len(fileLines)):
                findEnergy = re.search(f'^Conserved\senergy:\s+(-?\d+\.?\d*)',fileLines[line])
                if findEnergy: energies.append(float(findEnergy.group(1)))
            if (len(energies) == 0):
                print('Warning: There was no conserved energy to extract. Extracting current energies per cycle.')
                currentEnergies = []
                for line in range(len(fileLines)):
                    currentEnergy = re.search(f'Current.+energy:\s+(-?\d+\.?\d*)',fileLines[line])
                    lastCurrentEnergy = re.search(f'Current Adsorbate-Cation energy:\s+(-?\d+\.?\d*)',fileLines[line])
                    if lastCurrentEnergy: 
                        currentEnergies.append(float(lastCurrentEnergy.group(1)))
                        energies.append(sum(currentEnergies))
                        currentEnergies = []
                    elif currentEnergy: currentEnergies.append(float(currentEnergy.group(1)))
            return pd.Series(energies,index=range(len(energies)))
        elif (sec.lower() == 'prod'):
            energies = []
            try:
                for line in range(len(fileLines)-1,0,-1):
                    findEnergy = re.search(f'Total energy:',fileLines[line])
                    if findEnergy:
                        energy = re.search(f'Average\s+(-?\d+\.\d+).+?(\d+\.\d+)',fileLines[line+8])
                        energies.append(float(energy.group(1))) #J/kb
                        energies.append(float(energy.group(2))) #J/kb
                        break
            except: 
                print('Error: Tried to read internal energy, but simulation hasn\'t ended properly.')
                print('Extracting current energies per cycle.')
                currentEnergies = []
                for line in range(len(fileLines)):
                    currentEnergy = re.search(f'Current.+energy:\s+(-?\d+\.?\d*).+avg\.',fileLines[line])
                    lastCurrentEnergy = re.search(f'Current Adsorbate-Cation energy:\s+(-?\d+\.?\d*).+avg\.',fileLines[line])
                    if lastCurrentEnergy: 
                        currentEnergies.append(float(lastCurrentEnergy.group(1)))
                        energies.append(sum(currentEnergies))
                        currentEnergies = []
                    elif currentEnergy: currentEnergies.append(float(currentEnergy.group(1)))
            finally:
                return pd.Series(energies,index=range(len(energies)))
def ExtractDensitiesPerComponent(fileLines,component,sections):
    densities = []
    for sec in sections:
        if (sec.lower() == 'init'):
            for line in range(len(fileLines)):
                findDensity = re.search(f'Component.+\({component}\).+density:\s+(\d+\.?\d*)\s+\[kg',fileLines[line])
                if findDensity: densities.append(float(findDensity.group(1)))
        elif (sec.lower() == 'prod'):
            for line in range(len(fileLines)):
                findDensity = re.search(f'Component.+\({component}\).+density:\s+(\d+\.?\d*)\s+\(',fileLines[line])
                if findDensity: densities.append(float(findDensity.group(1))) #kg/m^3
    return pd.Series(densities,index=range(len(densities)))
def ExtractBoxLengths(fileLines,dimLetter,sections):
    dimension = {'x':1,'y':2,'z':3}
    boxLengths = []
    for sec in sections:
        if (sec.lower() == 'init'):
            for line in range(len(fileLines)):
                findLength = re.search(f'Box-lengths:\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+Box-angles',fileLines[line])
                if findLength: boxLengths.append(float(findLength.group(dimension[dimLetter]))) #A
        if (sec.lower() == 'prod'):
            for line in range(len(fileLines)):
                findLength = re.search(f'Box-lengths:\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*).+Average',fileLines[line])
                if findLength: boxLengths.append(float(findLength.group(dimension[dimLetter]))) #A
    return pd.Series(boxLengths,index=range(len(boxLengths)))
def ExtractNumberOfMoleculesPerComponent(fileLines,component,sections):
    nMolecules = []
    for sec in sections:
        if (sec.lower() == 'init'):
            for line in range(len(fileLines)):
                findAmountMolecules = re.search(f'Component.+\({component}\).+molecules:\s+(\d+)/\d+/\d+,',fileLines[line])
                if findAmountMolecules: nMolecules.append(float(findAmountMolecules.group(1)))
        elif (sec.lower() == 'prod'):
            for line in range(len(fileLines)):
                findAmountMolecules = re.search(f'Component.+\({component}\).+molecules:\s+(\d+)/.+\(',fileLines[line])
                if findAmountMolecules: nMolecules.append(float(findAmountMolecules.group(1)))
    return nMolecules
def ExtractWidomChemicalPotentialPerComponent(fileLines,component,sections):
    for sec in sections:
        if (sec.lower() == 'init'):
            chemPots = [np.nan]
            print('Warning: Chemical potential is not calculated by RASPA during initialization and equilibration cycles.')
            return pd.Series(chemPots,index=[0])
        elif (sec.lower() == 'prod'):
            try:
                chemPots = []
                for line in range(len(fileLines)-1,0,-1):
                    findChemPot = re.search(f'Average Widom chemical potential:',fileLines[line])
                    if findChemPot:
                        for subline in range(line+8,len(fileLines),7):
                            chemPot = re.search(f'\[{component}\]\s+Average.+?(-?\d+\.?\d*)\s+.+?(\d+\.?\d*)',fileLines[subline])
                            if chemPot: 
                                chemPots.append(float(chemPot.group(1))) #J/kb
                                chemPots.append(float(chemPot.group(2))) #J/kb
                                break
                        break
                return pd.Series(chemPots,index=[0,1])
            except: print('Error: Tried to read chemical potential, but simulation hasn\'t ended properly.')
            finally:
                chemPots.append(np.nan)
                return pd.Series(chemPots,index=[0])
def CallExtractors(varsToExtract,fileName,fileLines,components,dimensions,unit,sections):
    outData = {}
    if ('V' in varsToExtract): outData['V[A^3]'] = ExtractVolumes(fileLines,sections)
    if ('T' in varsToExtract): outData['T[K]'] = ExtractTemperatures(fileName,fileLines,sections)
    if ('P' in varsToExtract): outData[f'P[{unit}]'] = ExtractPressures(fileName,fileLines,unit,sections)
    if ('U' in varsToExtract): outData['U[K]'] = ExtractInternalEnergy(fileLines,sections)
    if ('Mu' in varsToExtract): 
        for comp in components:
            outData['Mu[K]'+f' {comp}'] = ExtractWidomChemicalPotentialPerComponent(fileLines,comp,sections)
    if ('Rho' in varsToExtract): 
        for comp in components:
            outData['Rho[kg/m^3]'+f' {comp}'] = ExtractDensitiesPerComponent(fileLines,comp,sections)
    if ('N' in varsToExtract): 
        for comp in components:
            outData['N'+f' {comp}'] = ExtractNumberOfMoleculesPerComponent(fileLines,comp,sections)
    if ('L' in varsToExtract): 
        for dim in dimensions:
            outData['Box-L[A]'+f' {dim}'] = ExtractBoxLengths(fileLines,dim,sections)
    return outData
def Flags(argv):
    path = './Outputs/System_0/'
    units = 'kPa'
    dimensions = ['x','y','z']
    components = []
    varsToExtract = []
    outFile = ('outData.dat',False)
    printInputParams = createFigures = False
    sections = ['prod']

    for i in range(len(argv)):
        if (argv[i] == '-h' or argv[i] == '-H'): Help()
        if (argv[i] == '-p' or argv[i] == '-P'): printInputParams = True
        if (argv[i] == '-f' or argv[i] == '-F'): createFigures = True
        elif (argv[i] == '-i' or argv[i] == '-I'): path = argv[i+1]
        elif (argv[i] == '-u' or argv[i] == '-U'): units = argv[i+1]
        elif (argv[i] == '-o' or argv[i] == '-O'): outFile = (argv[i+1],True)
        elif (argv[i] == '-d' or argv[i] == '-D'): 
            dimensions = []
            for j in range(i+1,len(argv)):
                if (argv[j][0] == '-'): break
                dimensions.append(argv[j])
        elif (argv[i] == '-c' or argv[i] == '-C'): 
            for j in range(i+1,len(argv)):
                if (argv[j][0] == '-'): break
                components.append(argv[j])
        elif (argv[i] == '-v' or argv[i] == '-V'): 
            for j in range(i+1,len(argv)):
                if (argv[j][0] == '-'): break
                varsToExtract.append(argv[j])
        elif (argv[i] == '-s' or argv[i] == '-S'): 
            sections = []
            for j in range(i+1,len(argv)):
                if (argv[j][0] == '-'): break
                sections.append(argv[j])
    return path,outFile,units,components,dimensions,varsToExtract,printInputParams,createFigures,sections
def PrintInputParameters(path,listInFiles,outFile,components,dimensions,varsToExtract,units,createFigures,sections):
    print(f'\tInput path: {path}')
    print(f'\tFluid components: {components}')
    print(f'\tVariables to extract: {varsToExtract}')
    print(f'\tPressure unit: {units}')
    print(f'\tBox dimensions: {dimensions}')
    print(f'\tSections to analyze: {sections}')
    print(f'\tCreate figures: {createFigures}')
    print(f'\tCreate output file: {outFile[1]}')
    for i in range(len(listInFiles)):
        print(f'\tInput file:')
        print(f'\t\t{listInFiles[i]}')
        if outFile[1]: print(f'\tOutput file: {i}_{outFile[0]}')
def Help():
    print('\nDescription:')
    print('\tThis script extracts the output data generated by RASPA (from production cycles on) and prints it on the Terminal')
    print('\t(and/or saves it in an output file). Primarily, it was created to analize a system\'s general behavior, but it can also')
    print('\tbe used to extract data from RASPA\'s outputs in dataframe formats.')
    print('Requirements: Numpy and Pandas libraries must be installed.')
    print('Warning: This script will read only the last data file produced by RASPA in the indicated directory.')
    print('Instructions:')
    print('\tpython3 extractRaspaData.py [-[Flag] [Arguments]] [-[Flag] [Arguments]] ...')
    print('\tFlags allowed:')
    print('\t\t-h or -H: Call for help.')
    print('\t\t-s or -S: The types of cycles to analyze: Production cycles (prod) or initialization cycles (init). By default: prod')
    print('\t\t\tEquilibration cycles (if added), are included in initialization cycles.')
    print('\t\t-f or -F: Plot the evolution of variables along the cycles.')
    print('\t\t\tThe plot file will be outputFile.pdf, where outputFile is indicated by the -o flag.')
    print('\t\t-p or -P: Print input parameters.')
    print('\t\t-i or -I: Indicate the path where the data file is found. By default: Output/System_0')
    print('\t\t-o or -O: Indicate the path/fileName where the extracted data will be printed.')
    print('\t\t\tBy default, no file is created.')
    print('\t\t-u or -U: Indicate the units for the pressure (kPa, atm or bar). By default: kPa')
    print('\t\t-c or -C: List of components involved in the simulation (fluid mixture). You must specify the species, even if it was only one')
    print('\t\t-d or -D: List of dimensions to extract the box-lengths. By deafault, the three dimensions.')
    print('\t\t-v or -V: Indicate the list of variables that will be extracted from the RASPA\'s data files (per cycle). By default: Rho')
    print('\tVariables allowed:')
    print('\t\tV: Volume in A^3.')
    print('\t\tT: Temperature in K.')
    print('\t\tP: Pressure in kPa.')
    print('\t\t\tThree different units can be specified: kPa, atm or bar. By default, kPa.')
    print('\t\tU: Internal energy in K (J/kb).')
    print('\t\t\tSimulation must have ended to be extracted.')
    print('\t\t\tOnly two values will be printed: Average (1st row) and its standard deviation (2nd row).')
    print('\t\tMu: Chemical Potential in K (J/kb) by Widom insertion method.')
    print('\t\t\tSimulation must have ended to be extracted.')
    print('\t\t\tOnly two values will be printed: Average (1st row) and its standard deviation (2nd row).')
    print('\t\t\tRequires the components to be indicated.')
    print('\t\tRho: Density in kg/m^3.')
    print('\t\t\tRequires the components to be indicated.')
    print('\t\tL: Box-length in A.')
    print('\t\t\tRequires the dimentions to be indicated (x, y or z).')
    print('\t\tN: Number of molecules/atoms.') 
    print('\t\t\tRequires the components to be indicated.')
    print('Example:')
    print('\tThe following command would extract the volume and internal energy of a methane-benzene binary mixture from Output/System_1,')
    print('\tas well as the pressure (in atm) and the box-length in the x direction.')
    print('\tThe extracted data would be saved in the file excessProps.dat')
    print('\tpython3 extractRaspaData.py -I Outputs/System_1/ -o ./excessProps.dat -s prod -C methane benzene -v U V P L -U atm -d x -p')
    exit(1)
def CreateDataFrame(outData,components,dimensions):
    keys = list(outData.keys())
    longestKey = keys[0]
    for i in range(1,len(keys)):
        if (len(outData[keys[i]]) > len(outData[keys[i-1]])): longestKey = keys[i]
    outData = pd.DataFrame(outData,index=range(len(outData[longestKey])))
    print(outData)
    return outData
def CreateOutFile(outData,fileNumber,out):
    if out[0]: #If output file is in a subdirectory.
        os.makedirs(out[0]+'dataFiles/', exist_ok=True)
    else: #If output file is not in a subdirectory.
        os.makedirs('dataFiles/', exist_ok=True)
    outData.to_csv(out[0]+'dataFiles/'+str(fileNumber)+'_'+out[1]+out[2],sep='\t',index=False,na_rep='NaN')
def PlotVariables(outData,fileNumber,out):
    if out[0]: #If output file is in a subdirectory.
        os.makedirs(out[0]+'Figures/', exist_ok=True)
    else: #If output file is not in a subdirectory.
        os.makedirs('Figures/', exist_ok=True)
    # prefixFileName = re.sub(f'(^.+)\..+$',r'\1',outFileName)
    outData.plot(style='.',subplots=True,grid=True,xlabel='Number of cycles')
    plt.tight_layout()
    plt.savefig(out[0]+'Figures/'+str(fileNumber)+'_'+out[1]+'.pdf')
def ReadOutputFile(outFile):
    out = re.search(r'(^.+/)(.+)(\..+$)',outFile[0])
    if not out.group(3): return (out.group(1),out.group(2),'.dat')
    else: return out.group(1,2,3)
##########################################################################################################
if __name__ == '__main__':
    print('Author: Santiago A. Flores Roman')
    print('\nReading input parameters...')
    path,outFile,units,components,dimensions,varsToExtract,printInputParams,createFigures,sections = Flags(argv)
    print('\nReading input files...')
    listInFiles = os.listdir(path)
    if printInputParams == True: 
        PrintInputParameters(path,listInFiles,outFile,components,dimensions,varsToExtract,units,createFigures,sections)
    for i in range(len(listInFiles)):
        print('\nExtracting data...')
        with open(path+listInFiles[i],'r') as fileContent: inFileLines = fileContent.readlines()
        outData = CallExtractors(varsToExtract,listInFiles[i],inFileLines,components,dimensions,units,sections)
        print('\nOrganizing data...')
        outData = CreateDataFrame(outData,components,dimensions)
        print(outData.describe())
        if outFile[1] == True:
            out = ReadOutputFile(outFile)
            print(f'\nCreating output file: {out[0]}dataFiles/{i}_{out[1]}{out[2]} ...')
            CreateOutFile(outData,i,out)
            if createFigures: 
                print('\nCreating figures...')
                PlotVariables(outData,i,out)
        else:
            if createFigures: 
                out = ReadOutputFile(outFile)
                print('\nCreating figures...')
                PlotVariables(outData,out)
        print(f'\nNormal termination for file {listInFiles[i]}')
    print(f'\nNormal termination.')
    exit(0)

# EOS
