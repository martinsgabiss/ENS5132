# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 14:42:31 2025

@author: jrmjr
"""
import os
import sys

# Adiciona o diretório atual (onde está o main.py) ao path
sys.path.append(os.getcwd())

from airqualityAnalysis import airQualityAnalysis
from airQualityFigures import airQualityHist, airQualityTimeSeries
import os



# Reconhecer pasta do repositório
repoPath = os.path.dirname(os.getcwd())

# Definindo pasta de dados
dataPath = repoPath +'/inputs'

# Lista pastas dentro de dataPath
ufs = os.listdir(dataPath)


# Loop para todos os estados
for uf in ufs:
    
    aqData, stations = airQualityAnalysis(uf)
    
    os.chdir(repoPath+'/scripts')
    #airQualityHist(aqData,stations,uf,repoPath)
    airQualityTimeSeries(aqData,stations,uf,repoPath)