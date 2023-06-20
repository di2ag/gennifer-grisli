import os
import pandas as pd
from pathlib import Path
import uuid
import json
import numpy as np
import shutil

from .zenodo import load_file

#DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sample_data')


def generateInputs(zenodo_id):
    '''
    Function to generate desired inputs for GRISLI.
    If the folder/files under RunnerObj.datadir exist, 
    this function will not do anything.
    '''
    os.makedirs("/tmp/", exist_ok=True) # Create the /tmp/ directory if it doesn't exist
    uniqueID = str(uuid.uuid4())
    tempUniqueDirPath = "/tmp/" + uniqueID
    os.makedirs(tempUniqueDirPath, exist_ok=True)
    
    ExpressionData = load_file(zenodo_id, 'ExpressionData.csv')
    PTData = load_file(zenodo_id, 'PseudoTime.csv')
            
    colNames = PTData.columns
    for idx in range(len(colNames)):
        os.makedirs(os.path.join(tempUniqueDirPath, "GRISLI", str(idx)))
        #RunnerObj.inputDir.joinpath("GRISLI/"+str(idx)).mkdir(exist_ok = True)
        
        # Select cells belonging to each pseudotime trajectory
        colName = colNames[idx]
        index = PTData[colName].index[PTData[colName].notnull()]
        
        exprName = os.path.join(tempUniqueDirPath, "GRISLI", str(idx), "ExpressionData.tsv")
        #exprName = "GRISLI/"+str(idx)+"/ExpressionData.tsv"
        ExpressionData.loc[:,index].to_csv(exprName, sep = '\t', header  = False, index = False)
        
        #cellName = "GRISLI/"+str(idx)+"/PseudoTime.tsv"
        cellName = os.path.join(tempUniqueDirPath, "GRISLI", str(idx), "PseudoTime.tsv")
        ptDF = PTData.loc[index,[colName]]                
        ptDF.to_csv(cellName, sep = '\t', header  = False, index = False)
    return tempUniqueDirPath, PTData, ExpressionData

def run(tempUniqueDirPath, PTData, L, R, alphaMin):
    '''
    Function to run GRISLI algorithm
    '''
    # make output dirs if they do not exist:
    outDir = os.path.join(tempUniqueDirPath, "outputs")
    os.makedirs(outDir, exist_ok = True)

    colNames = PTData.columns
    for idx in range(len(colNames)):
        #inputPath = "data"+str(RunnerObj.inputDir).split(str(Path.cwd()))[1]+"/GRISLI/"+str(idx)+"/"
        inputPath = os.path.join(tempUniqueDirPath, "GRISLI", str(idx)) + "/"
        os.makedirs(os.path.join(outDir, str(idx)), exist_ok = True)

        outFile = os.path.join(outDir, str(idx), "outFile.txt")

        cmdToRun = ' '.join(['./GRISLI', inputPath, outFile, str(L), str(R), str(alphaMin)])

        os.system(cmdToRun)
    return outDir


def parseOutput(tempUniqueDirPath, outDir, PTData, ExpressionData):
    '''
    Function to parse outputs from GRISLI.
    '''
    

    colNames = PTData.columns

    results = {'Gene1': [], 
               'Gene2': [],
               'EdgeWeight': []}

    for indx in range(len(colNames)):
        # Read output
        outFile = os.path.join(outDir, str(indx), 'outFile.txt')
        OutDF = pd.read_csv(outFile, sep = ',', header = None)    
        # Sort values in a matrix using code from:
        # https://stackoverflow.com/questions/21922806/sort-values-of-matrix-in-python
        OutMatrix = OutDF.values
        idx = np.argsort(OutMatrix, axis = None)
        rows, cols = np.unravel_index(idx, OutDF.shape)    
        DFSorted = OutMatrix[rows, cols]

        GeneList = list(ExpressionData.index)

        for row, col, val in zip(rows, cols, DFSorted):
            results['Gene1'].append(GeneList[row])
            results['Gene2'].append(GeneList[col])
            results['EdgeWeight'].append(len(GeneList)*len(GeneList) - val)
        
        # megre the dataframe by taking the maximum value from each DF
        # From here: https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
    outDF = pd.DataFrame.from_dict(results)

    res = outDF.groupby(['Gene1','Gene2'],as_index=False).max()
    # Sort values in the dataframe   
    finalDF = res.sort_values('EdgeWeight',ascending=False)  
    results = finalDF.to_dict('list')
    
    shutil.rmtree(tempUniqueDirPath)
    
    return results
