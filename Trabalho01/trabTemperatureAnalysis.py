# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 00:18:15 2025

@author: jrmjr
"""

#Importação de pacotes

import pandas as pd  # Para manipulação de dados e DataFrames
import os  # Para manipulação de arquivos e diretórios

#%% Organizando os dados

def trabTemperatureAnalysis(dados, repoPath):
    #  - Abrir os dados 
    # Definindo nome da estação e caminho para os dados
    dados = 'INMET_FLORIANOPOLIS'
    repoPath = r'C:\Users\jrmjr\Documents\ENS5132\Trabalho01'
    dataDir = os.path.join(repoPath, 'inputs', dados)

    # Lista de arquivos dentro da pasta
    dataList = os.listdir(dataDir)

    # Lê todos os arquivos CSV válidos da pasta em uma lista de DataFrames
    allFiles = [
        pd.read_csv(os.path.join(dataDir, file), encoding='latin1',
                    sep=';', engine='python', skiprows=8)
        for file in dataList
        if os.path.isfile(os.path.join(dataDir, file))
    ]

    # Concatenando os DataFrames
    aqData = pd.concat(allFiles, ignore_index=True)

    # - Inserir coluna datetime 
   
    # Remove ' UTC' da coluna de hora
    aqData['Hora UTC'] = aqData['Hora UTC'].str.replace(" UTC", "")

    # Corrige 'Hora UTC' para formato HH:MM:SS
    aqData['Hora UTC'] = aqData['Hora UTC'].astype(str).str.zfill(4)
    aqData['Hora UTC'] = aqData['Hora UTC'].str[:2] + ':' + aqData['Hora UTC'].str[2:] + ':00'
    
    # Cria a coluna datetime 
    aqData['datetime'] = pd.to_datetime(
        aqData['Data'].astype(str).str.strip() + ' ' + aqData['Hora UTC'],
        format='%Y/%m/%d %H:%M:%S',
        errors='coerce'
    )

    # Ajusta UTC para horário de Brasília (UTC-3)
    aqData['datetime'] = aqData['datetime'] - pd.Timedelta(hours=3)

    # Filtra datas válidas e dentro de um intervalo esperado
    aqData = aqData[
        (aqData['datetime'].notna()) &
        (aqData['datetime'] >= '2000-01-01') &
        (aqData['datetime'] <= '2025-03-31')
    ]

    # Define datetime como índice
    aqData = aqData.set_index('datetime')

    # Extrai componentes de data
    aqData['year'] = aqData.index.year
    aqData['month'] = aqData.index.month
    aqData['day'] = aqData.index.day
    aqData['hour'] = aqData.index.hour

    # - Filtrar apenas as colunas desejadas 
    aqDataCompleto = aqData.copy()

    colunas_originais = [
        'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)',
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'
    ]

    aqFiltrado = aqData[colunas_originais].copy()

    # Renomeia as colunas
    aqFiltrado.rename(columns={
        'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)': 'TBS',
        'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)': 'TMax',
        'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)': 'TMin'
    }, inplace=True)

    # Substitui vírgula por ponto e converte para float
    for col in ['TBS', 'TMax', 'TMin']:
        aqFiltrado[col] = aqFiltrado[col].astype(str).str.replace(',', '.', regex=False)
        aqFiltrado[col] = pd.to_numeric(aqFiltrado[col], errors='coerce')

    # Preenche os NaNs com a média da coluna
    aqFiltrado = aqFiltrado.fillna(aqFiltrado.mean())

    # Remove todas as observações do ano de 2018
    aqFiltrado = aqFiltrado[aqFiltrado.index.year != 2018]

    # - Estatísticas 
    tabela_estatisticas = aqFiltrado.describe()
    media_anual = aqFiltrado.resample('Y').mean()

    return aqFiltrado

  

