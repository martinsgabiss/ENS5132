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
uf = 'CE'

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

# Diretório onde salvar os arquivos CSV
outputDir = r"C:\Users\jrmjr\Documents\ENS5132\CE"
os.makedirs(outputDir, exist_ok=True)

# Loop para cada estação
for station in stations:

    stationDf = allFiles[allFiles['Estacao'] == station].copy()

    # Criando coluna datetime
    datetimDf = pd.to_datetime(stationDf['Data'], format='%Y-%m-%d', errors='coerce')
    stationDf['datetime'] = datetimDf
    stationDf = stationDf.dropna(subset=['datetime'])  # remove linhas com data inválida

    # Transformando a coluna de datetime em index
    stationDf = stationDf.set_index('datetime')

    # Extraindo ano, mês, dia
    stationDf['year'] = stationDf.index.year
    stationDf['month'] = stationDf.index.month
    stationDf['day'] = stationDf.index.day

    # Extraindo a hora
    horas = stationDf['Hora'].astype(str).str.split(':')
    horaDf = [h[0] if isinstance(h, list) else '0' for h in horas]
    stationDf['hour'] = horaDf

    # Corrigindo a coluna datetime
    stationDf['datetime'] = pd.to_datetime(
        stationDf[['year', 'month', 'day', 'hour']].astype(str),
        format='%Y%m%d %H',
        errors='coerce'
    )

    # Criando nome limpo para o arquivo
    station_name_clean = station.replace(" ", "_").replace("/", "_")
    file_name = f"{station_name_clean}.csv"
    output_path = os.path.join(outputDir, file_name)

    # Exportando
    stationDf.to_csv(output_path, index=True)
   

'''
#%% Trabalhando com Pandas!!

# Criando um DataFrame manualmente 
#São utilizados para armazenar, organizar e manipular dados de forma eficiente, 
#facilitando tarefas como leitura de arquivos (CSV, Excel, etc.), limpeza 
#de dados, análise exploratória e modelagem estatística.

df = pd.DataFrame(columns=['date','NH3'],
                  data=[
                      ['2025/04/01',0.35],
                      ['2025/04/02',1.01]
                      ])

# Criando mais coisas dentro do df
df['NO3'] = np.nan 
df['O2'] = [2 , 10]
df['SO4'] = np.nan 
df['SO4'][0] = 10

#%% Trabalhando com dado real
# Criando variável com o nome do estado
uf = 'CE'

# Definindo o caminho para a pasta de dados
dataDir = r"C:\Users\jrmjr\Documents\ENS5132" +'/'+ uf

# Lista de arquivos dentro da pasta (os.listdir(caminho) pega todos os nomes 
#dos arquivos e subpastas que estão no caminho que você passar.)
dataList = os.listdir(dataDir)

# Movendo para a pasta de dados/uf - caminho 'novo'
os.chdir(dataDir)

allFiles =[]
# Loop na lista dataList 
for fileInList in dataList:
    print(fileInList) #vaii mostrar o arquivo a cada loop
    dfConc = pd.read_csv(fileInList,encoding='latin1') #vai ler cada arq em csv, encoding para evitar erro na escrita
    allFiles.append(dfConc) # Guarda o DataFrame na lista allFiles

# Concatenando meus DataFrames
allFiles = pd.concat(allFiles)

# Extraindo nomes das estações sem redundância
stations = pd.unique(allFiles['Estacao'])

# usando lógica...
stationDf = allFiles[allFiles['Estacao'] == stations[0]]

# Criando coluna datetime
datetimeDf = pd.to_datetime(stationDf.Data, format='%Y-%m-%d')


# Criando coluna datetime dentro de stationDf
stationDf['datetime'] = datetimeDf

# Transformando a coluna de datetime em index
stationDf = stationDf.set_index(stationDf['datetime'])

# Extrair o ano e mês
stationDf['year'] = stationDf.index.year
stationDf['month'] = stationDf.index.month
stationDf['day'] = stationDf.index.day

# Extraindo a hora
horas  = stationDf.Hora.str.split(':')

horaDf = []
for hora in horas:
    print(hora[0])
    horaDf.append(hora[0])

stationDf['hour'] = horaDf


# Corrigindo a coluna datetime
stationDf['datetime'] = pd.to_datetime(
    stationDf[['year', 'month','day','hour']],format='%Y%m%d %H')

# Vamos assumir que:
# - airQualityDf é o DataFrame geral
# - stations é a lista com o nome de cada estação
# - Dentro do DataFrame existe uma coluna chamada 'station' que indica a estação de cada linha
outputDir = r"C:\Users\jrmjr\Documents\ENS5132\CE"


for station in stations:
    # 1) Filtra
    df_st = allFiles[allFiles['Estacao'] == station].copy()
    
    # 2) Reconstrói a coluna datetime a partir de 'Data' e 'Hora'
    #    assumindo 'Data' no formato 'YYYY-MM-DD' e 'Hora' em 'HH:MM:SS'
    df_st['datetime'] = pd.to_datetime(
        df_st['Data'] + ' ' + df_st['Hora'],
        format='%Y-%m-%d %H:%M:%S'
    )
    
    # 3) Define como índice e nomeia
    df_st = df_st.set_index('datetime')
    df_st.index.name = 'datetime'
    
    # 4) Salva o CSV, agora com primeiro campo 'datetime' corretamente nomeado
    safe_name = station.replace(' ', '_').replace('/', '_')
    out_path = os.path.join(outputDir, f'{safe_name}.csv')
    df_st.to_csv(out_path, index=True)
    
    print(f'✔️ Salvou: {out_path}')


# Para cada estação...
for station in stations:
    # Filtra os dados daquela estação
    stationDf = allFiles[allFiles['Estacao'] == station]
    
    # Cria um nome de arquivo baseado no nome da estação

   
   
    # Criando nome limpo para o arquivo
    station_name_clean = station.replace(" ", "_").replace("/", "_")
    fileName = f"{station_name_clean}.csv"
    output_path = os.path.join(outputDir, fileName)

    # Exportando
    stationDf.to_csv(output_path, index=True)
'''
    
