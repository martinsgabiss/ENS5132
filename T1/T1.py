# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 19:49:47 2025

@author: jrmjr
"""

#%% ---------------- 0. Baixando bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% ---------------- 1. Baixando dados

# ------ 1.1 Abrindo o arquivo meteorológico do INMET (Estação Florianópolis)
dados = pd.read_csv('INMET_S_SC_A806_FLORIANOPOLIS_01-01-2024_A_31-12-2024.CSV'
                    , skiprows=8, delimiter= ";", encoding='latin1',
                    decimal = ',')

# ------ 1.2 Variáveis meteorológicas analisadas
var_meteo = ['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)', 
             'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)',
             'RADIACAO GLOBAL (Kj/m²)', 
             'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)', 
             'UMIDADE RELATIVA DO AR, HORARIA (%)',
             'VENTO, VELOCIDADE HORARIA (m/s)']


#%% ---------------- 2. Manipulação dos dados

# ------ 2.1 Removendo o texto "UTC" da coluna de Horas
dados['Hora UTC'] = dados['Hora UTC'].str.replace(" UTC", "")

# ------ 2.2 Criando uma coluna de data
dados['Data Completa'] = pd.to_datetime(dados['Data'] + ' ' + dados['Hora UTC'])

#%% ---------------- 3. Análise Descritiva

# ------ 3.1 Média
media = [dados[var].mean() for var in var_meteo]
# --- Imprimindo na tela as médias
for var in var_meteo: print(var+": "+ str(round(dados[var].mean(),4)))

# ------ 3.2 Mediana
mediana = [dados[var].median() for var in var_meteo]
# --- Imprimindo na tela as médias
for var in var_meteo: print(var+": "+ str(round(dados[var].median(),4)))

# ------ 3.3 Desvio Padrão
desv = [dados[var].std() for var in var_meteo]
# --- Imprimindo na tela as médias
for var in var_meteo: print(var+": "+ str(round(dados[var].std(),4)))

# ------ 3.4 Máximo
maximo = [dados[var].max() for var in var_meteo]
# --- Imprimindo na tela as médias
for var in var_meteo: print(var+": "+ str(round(dados[var].max(),4)))

# ------ 3.5 Mínimo
minimo = [dados[var].min() for var in var_meteo]
# --- Imprimindo na tela as médias
for var in var_meteo: print(var+": "+ str(round(dados[var].min(),4)))

#%% ---------------- 4. Análise de Distribuição

for var in var_meteo:
    ax = plt.subplots(figsize=(8, 5))  # Define o tamanho da figura (opcional)
    plt.hist(dados[var], bins=5, edgecolor='white')  # bins = número de barras
    plt.xlabel(var)
    plt.ylabel('Frequência')
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)



















