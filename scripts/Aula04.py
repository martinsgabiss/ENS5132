# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 13:41:31 2025

Este scrip usei durante a aula do dia 01/04/25
@author: jrmjr
"""

#%%importando os pacotes que utilizarei
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os 

#%% Revisão numpy

#criando um vetor com arrnjo de dados
x = np.arange(-10,20,0.15)

# Brincando com indexação
print(' Esta é a quarta posição do meu vetor: ' + str(x[3]))

print('Estes são os três primeiros valores:' + str(x[0:3]))

#substituir um valor dentro do vetor
x[9] = 9999999 #exemplo de medição errada
x[11] = -999999 

#extraíndo a média
meanX = np.mean(x)
print(meanX)

# Operação booleana
# and = &
# or = |
# encontrando valores errados
vecBool = (x>20) | (x<-10) #estou usando o simbolo | para or

# extraindo valores errados usando logica booleana
valErrado = x[vecBool]

#substituindo os valores errados por 0
x2 = x.copy() # criando uma copia independente
x2[vecBool] = 0
print('Esta é a média de x substituindo valores errados por 0:'+ 
      str(np.mean(x2))) 

#substituindo por NaN - Not a Number
x3 = x.copy()
x3[vecBool] = np.nan
print('Esta é a média usando np.nanmean de x substituindo valores errados:' + 
      str(np.nanmean(x3)))

#Substituindo pela média
x4 = x.copy() #criando uma copia independente
x4[vecBool] = np.nanmean(x3)
print('Esta é a média de x substituindo valores errados por nan:' + 
      str(np.mean(x4)))

#%% USando matplotlib para inspecionar os vetores

fig, ax = plt.subplots(4)
ax[0].plot(x)
ax[1].plot(x2)
ax[2].plot(x3)
ax[3].plot(x4)

#%% Loop em python

# Loop utilizando range

for ii in range(0,10):
    val = 2**ii
    print(val)

# Loop utilizando range e acumulando em um vetor

vetor = []
for ii in range(0,10):
    val = 2**ii
    vetor.append(val)
    print(val)
    
# Loop utilizando range e acumulando o valor de val em um vetor

vetorAcumulado = []
val = 0
for ii in range(0,10):
    val = val + 2**ii
    vetorAcumulado.append(val)
    
# Loop utilizando uma lista

alunas = ['Mariana','Bianca','AnaJulia','Mariah']
for aluna in alunas:
    print(' A nota da '+aluna+' é:'+str(np.random.rand(1)*10))
    
#%% Trabalhando com Pandas!!

#Criando um DataFram manualmente

df = pd.DataFrame(columns=['date','NH3'], 
                  data=[
                      ['2025/04/01',0.35],
                      ['2025/04/02',1.01]
                      ])

#Criando mais coisas dentro do df
df['NO3'] = np.nan
df['O2'] = [2 , 10]
df['SO4'] = np.nan
df['SO4'][0] = 10

#%% Trabalhando com dado real

#criando um DataFrame manualmente
uf = 'RJ'

#definindo o caminho para a pasta de dados
dataDir = r"C:\Users\jrmjr\Documents\ENS5132" + '/' + uf

# lista de arquivos dentro da pasta
dataList = os.listdir(dataDir)

#movendo para a pasta de dados/uf
os.chdir(dataDir)

# Loop na lista dataList
allFiles = []
for fileInList in dataList:
     print(fileInList)
     dfConc = pd.read_csv(fileInList,encoding='Latin1')
     allFiles.append(dfConc)
     
#concatenando meus DataFrames
allFiles = pd.concat(allFiles)

#Extraindo nomes das estações sem redundança
stations = pd.unique(allFiles['Estacao'])

# usando lógica...
stationDf = allFiles[allFiles['Estacao'] == [0]]

# criando coluna datetime

datetimDf = pd.to_datetime(stationDf.Data, format='%Y-%m-%d')

# criando coluna datetime dentro da stationDf
stationDf['datetime'] = datetimDf

# Transformando a coluna de datetime em index
stationDf = stationDf.set_index(stationDf['datetime'])

#Extrair o ano e o mês
stationDf['year'] = stationDf.index.year
stationDf['month'] = stationDf.index.month
stationDf['day'] = stationDf.index.day

stationDf['hour'] = stationDf.index.hour

    
    
    




      
