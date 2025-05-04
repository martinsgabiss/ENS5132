# -*- coding: utf-8 -*-
"""
Created on Fri May  2 10:56:00 2025

@author: jrmjr
"""

#Importação de pacotes

import matplotlib.pyplot as plt #criar gráficos
import os #Interagir com o sistema de arquivos
import seaborn as sns #Biblioteca de visualização baseada no matplotlib
import pandas as pd # análise de dados tabulares (DataFrames)
from scipy import stats #Funções estatísticas e testes de hipóteses
import numpy as np #Manipulação de arrays e operações matemáticas
import statsmodels.api as sm #Modelos estatísticos mais avançados
from pymannkendall import original_test #Aplica o teste de tendência de Mann-Kendall

#%% Criando Gráficos

#Criando Histogramas de Temperatura

def temperatureHist(aqFiltrado, repoPath):
    os.makedirs(os.path.join(repoPath, 'figuras'), exist_ok=True)
    colors = ['lightpink', 'lightblue', 'lightgreen']  #cores dos gráficos

    for i, col in enumerate(aqFiltrado.columns):
        if col == 'datetime':
            continue
        plt.figure(figsize=(8, 5))
        color = colors[i % len(colors)]  # escolhe a cor com base no índice
        plt.hist(aqFiltrado[col].dropna(), bins=30, color=color, edgecolor='black')
        plt.title(f'{col} (°C)')
        plt.tight_layout()
        plt.savefig(os.path.join(repoPath, 'figuras', f'hist_{col}.png'))
        plt.close()

# Criando Gráfico de Série Temporal

def temperaturePlotTimeSeries(aqFiltrado, repoPath):
    os.makedirs(os.path.join(repoPath, 'figuras'), exist_ok=True)
    aqFiltrado['datetime'] = aqFiltrado.index

    # nomes já padronizados
    séries = ['TBS', 'TMax', 'TMin']
    labels = ['Temperatura Bulbo Seco', 'Temperatura Máxima', 'Temperatura Mínima']

    # verifica se tudo existe
    if not all(col in aqFiltrado.columns for col in séries) or 'datetime' not in aqFiltrado.columns:
        print("DataFrame sem as colunas necessárias.")
        return

    # cria 3 subplots verticalmente, compartilhando o eixo X
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    for ax, serie, label in zip(axes, séries, labels):
        ax.plot(aqFiltrado['datetime'], aqFiltrado[serie], linewidth=0.8)
        ax.set_ylabel('°C')
        ax.set_title(label)
        ax.grid(True)

    # só o último eixo recebe o label de eixo X
    axes[-1].set_xlabel('Data')

    plt.tight_layout()
    caminho = os.path.join(repoPath, 'figuras', 'plot_Temperature.png')
    fig.savefig(caminho)
    plt.close()
    print(f'Gráfico salvo em: {caminho}')

#boxplot por ANO
def boxplotYearTemperature(aqFiltrado, repoPath):
    os.makedirs(os.path.join(repoPath, 'figuras'), exist_ok=True)

    # Garante que a coluna "year" exista
    aqFiltrado['year'] = aqFiltrado['datetime'].dt.year

    # Converte para formato longo
    df_melted = aqFiltrado.melt(id_vars=['year'], value_vars=['TBS', 'TMax', 'TMin'],
                                var_name='Tipo', value_name='Temperatura')

    # Cria boxplot por ano
    plt.figure(figsize=(14, 6))
    sns.boxplot(data=df_melted, x='year', y='Temperatura', hue='Tipo', 
                palette=['lightpink', 'lightblue', 'lightgreen'])
    plt.title('Boxplot das Temperaturas por Ano')
    plt.xlabel('Ano')
    plt.ylabel('Temperatura (°C)')
    plt.legend(title='Tipo')
    plt.xticks(rotation=45)
    plt.tight_layout()

    caminho = os.path.join(repoPath, 'figuras', 'Boxplot_Temperaturas_Por_Ano.png')
    plt.savefig(caminho)
    plt.close()

#boxplot por MES

def boxplotMonthTemperature(aqFiltrado, repoPath):
    os.makedirs(os.path.join(repoPath, 'figuras'), exist_ok=True)
    
    # Garante que a coluna "month" exista
    aqFiltrado['month'] = aqFiltrado['datetime'].dt.month

    # Converte o DataFrame para formato "longo" (melt)
    df_melted = aqFiltrado.melt(id_vars=['month'], value_vars=['TBS', 'TMax', 'TMin'],
                                var_name='Tipo', value_name='Temperatura')

    # Cria o boxplot com Seaborn
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_melted, x='month', y='Temperatura', hue='Tipo', 
                palette=['lightpink', 'lightblue', 'lightgreen'])
    plt.title('Boxplot das Temperaturas por Mês')
    plt.xlabel('Mês')
    plt.ylabel('Temperatura (°C)')
    plt.legend(title='Tipo')
    plt.tight_layout()
    
    caminho = os.path.join(repoPath, 'figuras', 'Boxplot_Temperaturas_Meses.png')
    plt.savefig(caminho)
    plt.close()

#Teste de Normalidade

def normalityCheckTemperature(aqFiltrado, repoPath):

    cols = ['TBS', 'TMax', 'TMin']
    
    # Cria pasta se não existir
    out_dir = os.path.join(repoPath, 'figuras')
    os.makedirs(out_dir, exist_ok=True)
    
    for col in cols:
        # Seleciona dados sem NaNs
        dados = aqFiltrado[col].dropna()

        # Cria a figura
        fig, ax = plt.subplots(3, 1, figsize=(8, 10))

        # 1) Log transform
        ax[0].hist(np.log(dados), bins=30, color='violet')
        ax[0].set_title(f'Log transformado')

        # 2) Box-Cox
        bc, _ = stats.boxcox(dados)
        ax[1].hist(bc, bins=30, color='orange')
        ax[1].set_title(f'Box-Cox')
        
        # 3) Dados originais
        ax[2].hist(dados, bins=30, color='lightgray')
        ax[2].set_title(f'Dados originais')
        ax[2].set_xlabel(col)

        # Ajusta layout e salva a figura
        plt.tight_layout()
        fig.savefig(os.path.join(out_dir, f'normalidade_{col}.png'))
        plt.close(fig)

# Tendência
def trendFigureSingleTemperature(aqFiltrado, repoPath, col='TBS'):
    """
    Gera gráfico de autocorrelação e tendência linear para a média anual
    de uma coluna de temperatura (col).
    """
    # 1) Preparo dos dados
    df = aqFiltrado.copy()
    df.index = pd.to_datetime(df.index)

    # Agrupa por ano e tira média
    annual = df[col].groupby(df.index.year).mean()

    # 2) Teste de Mann-Kendall (não-paramétrico) para obter slope/intercept
    result = original_test(annual)

    # 3) Linha de tendência a partir de slope/intercept
    x = np.arange(len(annual))
    trend_line = x * result.slope + result.intercept

    # 4) Plot
    fig, ax = plt.subplots(2, 1, figsize=(8, 6))

    # Autocorrelação da série anual
    sm.graphics.tsa.plot_acf(annual, lags=5, ax=ax[0])
    ax[0].set_title(f'Autocorrelação (ACF) – média anual de {col}')

    # Série anual + tendência
    ax[1].plot(annual.index, annual.values, marker='o', label='Média Anual')
    ax[1].plot(annual.index, trend_line, linestyle='--', color='orange', label='Tendência MK')
    ax[1].set_title(f'Tendência Linear (Mann–Kendall) – {col}')
    ax[1].set_xlabel('Ano')
    ax[1].set_ylabel(f'{col} (°C)')
    ax[1].legend()

    plt.tight_layout()

    # 5) Salvar figura
    out_dir = os.path.join(repoPath, 'figuras')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f'trend_{col}.png')
    fig.savefig(out_file)
    plt.close(fig)
    print(f'[✓] Gráfico salvo em {out_file}')

    return result, annual
    
def trendForAllColumns(aqFiltrado, repoPath, cols=None):
    """
    Executa a função trendFigureSingleTemperature para todas as colunas de temperatura em aqFiltrado.

    """
    # Se não for passado nenhuma lista de colunas, usa todas as colunas do DataFrame
    if cols is None:
        cols = aqFiltrado.columns

    # Itera sobre as colunas e chama a função trendFigureSingleTemperature
    for col in cols:
        print(f'[✓] Gerando gráfico para a coluna: {col}')
        trendFigureSingleTemperature(aqFiltrado, repoPath, col=col)

  



