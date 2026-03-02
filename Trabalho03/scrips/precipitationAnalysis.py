# -*- coding: utf-8 -*-
"""
Created on Sat Jun 21 21:37:58 2025

Avaliar a relação espaço-temporal entre eventos hidrológicos
 (inundações, enxurradas e alagamentos) e a precipitação máxima mensal 
 no Sul do Brasil entre 1991 e 2024.

@author: jrmjr
"""
#importando pacotes

import xarray as xr #biblioteca usada para trabalhar com dados multidimensionais
import glob #serve para buscar um padrao em tipo de arquivo
import pandas as pd  # Para manipulação de dados e DataFrames
import os  # Para manipulação de arquivos e diretórios
import numpy as np # Operações numéricas com arrays


import matplotlib.pyplot as plt  # Geração de gráficos 
import cartopy.crs as ccrs #Define sistemas de coordenadas e projeções geográficas
import cartopy.feature as cfeature #Elementos geográficos 
import seaborn as sns #Biblioteca para visualização estatística de dados em gráficos 

#import netCDF4 as nc
#import geopandas as gpd  # Manipulação de dados espaciais vetoriais (shapefiles)
#%% Tentando abrir o arquivo netCDF com precipitação de 1980-2024 no sul do BR

#Caminho para os arquivos netCDF
arqP = r"C:\Users\jrmjr\Documents\ENS5132\Trabalho03\inputs\M2SMNXSLV_5.12.4-20250622_014127"

# Listar os arquivos .nc
arquivos_nc = sorted(glob.glob(os.path.join(arqP, '*.nc4')))

# Abrir todos os arquivos como um único dataset (data cube) com xarray
try:
    ds = xr.open_mfdataset(arquivos_nc, combine="by_coords")
except ImportError as e:
    print("Erro ao abrir com xarray: ", e)
    print("Tentando abrir com chunks={}")
    ds = xr.open_mfdataset(arquivos_nc, combine="by_coords", chunks={})

# Mostrar resumo do dataset
print(ds) 

prec = ds['TPRECMAX']

#conferindo a variação de latitude e longitude para filtrar para a região sul do Brasil
print(ds['lat'].values.min(), ds['lat'].values.max())
print(ds['lon'].values.min(), ds['lon'].values.max())

prec_sul = prec.sel(
    lat=slice(-34, -23),
    lon=slice(-57, -48)
)

prec_sul_1980_2024 = prec_sul.sel(time=slice("1980", "2024"))

print(prec_sul_1980_2024)
#1 kg/m²/s = 1 mm/s , mas analiso mensalmente

# Aproximadamente 2,63 milhões de segundos por mês 
prec_mm_mes = prec_sul_1980_2024 * 2.63e6

#%% Tentando abrir o csv Eventos hidrológicos, fonte: https://atlasdigital.mdr.gov.br/paginas/downloads.xhtml

repoPath = r'C:\Users\jrmjr\Documents\ENS5132\Trabalho03'

def trabHidrolEventsAnalysis(repoPath):
    
    # Define o diretório dos dados
    dataDir = os.path.join(repoPath, 'inputs')

    # Lista todos os arquivos dentro da pasta
    dataList = os.listdir(dataDir)

    # Escolhe o primeiro CSV da lista
    filePath = os.path.join(dataDir, dataList[0])

    # Lê o arquivo CSV
    df = pd.read_csv(filePath, encoding='latin1', sep=';', engine='python')
    
    # entendendo o tipo de eventos que ocorreram
    if 'descricao_tipologia' in df.columns:
        eventos_unicos = df['descricao_tipologia'].dropna().unique()
        
    # Filtrando apenas as colunas desejadas 
    
    #Entendendo quais colunas o dataframe nos oferece
    print(df.columns.tolist())
    
    #Criando uma cópia segura
    dfSul = df.copy()
    
    #Escolhendo as colunas que serão mais úteis
    colunas_originais = [ 
        'Protocolo_S2iD',
        'Nome_Municipio',
        'Sigla_UF',
        'regiao',
        'Data_Evento',
        'descricao_tipologia',
        'grupo_de_desastre'
    ]
    
    #Filtrando o dataFrame com as colunas_originais
    dfSul = dfSul[colunas_originais].copy()

    #Filtrando o dataframe somente com dados de sul do BR e desastre hidrológico
    dfSulHidro = dfSul[(dfSul['regiao'] == 'Sul') & (dfSul['grupo_de_desastre'] == 'Hidrológico')]
    
    #Entendendo o tipo de desastres hidrológicos - valores unicos
    if 'descricao_tipologia' in dfSulHidro.columns:
        classeshidro = dfSulHidro['descricao_tipologia'].dropna().unique()
    print(classeshidro)
    
    #Filtrando somente os eventos para correlacionar com o netcdf de chuva
    tipologia = ['Enxurradas', 'Inundações', 'Alagamentos']
    dfSulHidro = dfSulHidro[dfSulHidro['descricao_tipologia'].isin(tipologia)]
    #isin - Ela retorna uma série booleana, neste caso vai filtrar os valores verdadeiros
      
    #Ajustar para datetime
    dfSulHidro['Data_Evento'] = pd.to_datetime(dfSulHidro['Data_Evento'], 
                                               dayfirst=True, errors='coerce')
    #Extraindo mes e ano de cada evento
    dfSulHidro['ano'] = dfSulHidro['Data_Evento'].dt.year
    dfSulHidro['mes'] = dfSulHidro['Data_Evento'].dt.month
    
    #vai criar um tabela, onde a cada mes e ano, vai avaliar quantos eventos ocorreram
    eventos_mensal = dfSulHidro.groupby(['ano', 'mes']).size().reset_index(name='n_eventos')
    # Criando coluna 'data' para o eixo X
    eventos_mensal['data'] = pd.to_datetime(dict(year=eventos_mensal['ano'],
                                                 month=eventos_mensal['mes'], day=1))

    return dfSulHidro, eventos_mensal

#%%
###scCrs = "EPSG:31982" VER LATER

# Tentando filtrar o sul do brasil no shapefile, para mesclar com meu dataframe de eventos

# def municipiosData(repoPath):
#     """
#     Abre shapefiles de municípios a partir de um repositório base.
    
#     """
#     #  - Abrindo os dados 
#     dadosMun = 'BR_Municipios_2024'
    
#     # Caminho para a pastas do shapefile
#     munPath = os.path.join(repoPath, 'inputs', dadosMun, 'BR_Municipios_2024.shp')
    
#     # Abrindo com geopandas
#     geoMun = gpd.read_file(munPath)
    
#     # Extraindo o sistema de coordenadas de refe^rencias
#     geoMun.crs
#     #EPSG:4674>
    
#     #Filtrando somente dados de SC, PR, RS
#     geoSul = geoMun[geoMun['SIGLA_UF'].isin(['SC', 'PR', 'RS'])]

#     return geoSul

#%% EXPLORANDO FIGURAS

#figura 1 - GRÁFICO COM MM/MES -

# Média da precipitação ao longo do tempo (1980–2024)
media_espacial = prec_mm_mes.mean(dim='time')

# Criar figura e eixo com projeção geográfica
fig = plt.figure(figsize=(10, 6))
ax = plt.axes(projection=ccrs.PlateCarree())  # eixo com projeção

# Adicionar contornos de estados ou países 
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.STATES, linestyle=':', edgecolor='gray')

# Plotar com o eixo projetado
media_espacial.plot(
    ax=ax,
    cmap='Blues',
    transform=ccrs.PlateCarree(),  # dados estão em lat/lon
    cbar_kwargs={'label': 'Precipitação média (mm/mês)'}
)

ax.set_title('Média da Precipitação no Sul do Brasil (1980–2024)')
plt.show()
fig.savefig(os.path.join(repoPath, 'outputs','mediaPrecipitacaoSulBr1980-2024.png'))

# figura 2 - COMO A PRECIPITAÇÃO TEM SE COMPORTADO MES A MES NA REGIAO SUL DO BR NOS ULTIMOS 40 ANOS

# 1. Agrupar por mês e calcular a média 
media_mensal = prec_mm_mes.groupby('time.month').mean(dim='time')

# 2. Plotar todos os meses em uma grade de mapas

fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 10),
                         subplot_kw={'projection': ccrs.PlateCarree()})
fig.suptitle('Precipitação Mensal no Sul do Brasil (1980–2024)', fontsize=16)

# Lista de nomes dos meses (opcional)
nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

for i, ax in enumerate(axes.flat):
    im = media_mensal.isel(month=i).plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap='Blues',
        add_colorbar=False
    )
    ax.set_title(nomes_meses[i])
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':', edgecolor='gray')

# Barra de cores vertical à direita
cbar_ax = fig.add_axes([0.92, 0.25, 0.015, 0.5])  # [left, bottom, width, height]
cbar = fig.colorbar(im, cax=cbar_ax, orientation='vertical')
cbar.set_label('Precipitação média (mm/mês)')

plt.tight_layout(rect=[0, 0, 0.9, 0.95])  # espaço para barra à direita e título
plt.show()
fig.savefig(os.path.join(repoPath, 'outputs','mesamesPrecipitacaoSulBr1980-2024.png'))


# figura 3 - analizando sazonalidade - todos os anos 

# 1. Calcula a média espacial (lat/lon) para cada ponto no tempo (mensal)
prec_sul_mensal_mean = prec_mm_mes.mean(dim=['lat', 'lon'])

# 2. Cria DataFrame com tempo como índice
df_prec_mensal = prec_sul_mensal_mean.to_dataframe(name='prec_mm').reset_index()

# 3. Extrai ano e mês
df_prec_mensal['ano'] = df_prec_mensal['time'].dt.year
df_prec_mensal['mes'] = df_prec_mensal['time'].dt.month

# 4. Reorganiza em formato de tabela: anos como linhas, meses como colunas
tabela_sazonal = df_prec_mensal.pivot(index='ano', columns='mes', values='prec_mm')

# 5. Gráfico clean de sazonalidade
fig, ax = plt.subplots(figsize=(12, 6))

# Linhas de todos os anos (sem legenda individual)
for ano in tabela_sazonal.index:
    plt.plot(tabela_sazonal.columns, tabela_sazonal.loc[ano], color='gray', 
             alpha=0.3, linewidth=1)

# Linha da média (com legenda e mais grossa)
plt.plot(tabela_sazonal.columns, tabela_sazonal.mean(axis=0), color='black',
         linewidth=2.5, label='Média 1980–2024')

plt.title('Precipitação (Sul do Brasil, 1980–2024)')
plt.xlabel('Mês')
plt.ylabel('Precipitação Média (mm/mês)')
plt.xticks(ticks=range(1, 13), labels=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
plt.legend(loc='upper right')
plt.grid(True)
plt.tight_layout()
plt.show()
fig.savefig(os.path.join(repoPath, 'outputs','todosAnosPrecipitacaoSulBr1980-2024.png'))


#figura 4 - tendência

# 1. Média anual (média dos 12 meses de cada ano)
media_anual = df_prec_mensal.groupby('ano')['prec_mm'].mean()

# 2. Plot
fig, ax = plt.subplots(figsize=(12, 6)) 

# Linha da série histórica
plt.plot(media_anual.index, media_anual.values, color='cornflowerblue', 
         linewidth=2, label='Média Anual')

# Linha de tendência (regressão linear)
coef = np.polyfit(media_anual.index, media_anual.values, deg=1)
trend = np.poly1d(coef)
plt.plot(media_anual.index, trend(media_anual.index), linestyle='--', color='crimson',
         linewidth=2.5, label='Tendência Linear')

# Layout e labels
plt.title('Tendência da Precipitação Média Anual\nSul do Brasil (1980–2024)', fontsize=14)
plt.xlabel('Ano')
plt.ylabel('Precipitação Média Anual (mm/mês)')
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Salvar a figura 
fig.savefig(os.path.join(repoPath, 'outputs', 'tendencia_precipitacao_anual.png'), dpi=300)


#figura 5 - HEATMAP - para precipitação e eventos hidrologicos por anos, lado a lado.

# Junta os dois dataframes no mesmo por ano e mês
df_corr = pd.merge(df_prec_mensal[['ano', 'mes', 'prec_mm']],
                   eventos_mensal[['ano', 'mes', 'n_eventos']],
                   on=['ano', 'mes'],
                   how='left')  # mantém todos os meses com precipitação, mesmo sem evento

df_corr['n_eventos'] = df_corr['n_eventos'].fillna(0)  # preenche meses sem eventos com 0
df_corr['ano'] = df_corr['ano'].astype(int)  # garante tipo correto

# Pivot para formar matriz ano x mês
heat_prec = df_corr.pivot(index='ano', columns='mes', values='prec_mm')
heat_eventos = df_corr.pivot(index='ano', columns='mes', values='n_eventos')

# Gráfico heatmap lado a lado
fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharey=True)

# Heatmap de eventos
sns.heatmap(heat_eventos, cmap="Reds", ax=axes[0], linewidths=0.5, linecolor='gray', 
            cbar_kws={'label': 'Nº de Eventos'})
axes[0].set_title('Eventos Hidrológicos por Mês e Ano')
axes[0].set_xlabel('Mês')
axes[0].set_ylabel('Ano')
axes[0].set_xticks(np.arange(12) + 0.5)
axes[0].set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                         'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], rotation=0)

# Heatmap de precipitação
sns.heatmap(heat_prec, cmap="Blues", ax=axes[1], linewidths=0.5, linecolor='gray', 
            cbar_kws={'label': 'Precipitação (mm/mês)'})
axes[1].set_title('Precipitação por Mês e Ano')
axes[1].set_xlabel('Mês')
axes[1].set_ylabel('')

plt.tight_layout()
plt.show()

# Salvar a figura (opcional)
fig.savefig(os.path.join(repoPath, 'outputs', 'heatmapEventosVsPrecipitacao.png'))

#figura 6 - CORRELAÇÃO - PRECIPITAÇÃO em cada célula (ano, mês) E EVENTOS HIDROLOGICOS

# Filtra os dados a partir de 1991
heat_prec_1991 = heat_prec.loc[1991:]
heat_eventos_1991 = heat_eventos.loc[1991:]

# Calcular a correlação entre eventos e precipitação a partir de 1991
correlacoes_mes = []
meses = range(1, 13)

for mes in meses:
    eventos_mes = heat_eventos_1991[mes]
    prec_mes = heat_prec_1991[mes]
    corr = eventos_mes.corr(prec_mes)
    correlacoes_mes.append(corr)

# Transformar em DataFrame para plotar heatmap
df_corr_mes = pd.DataFrame({'mes': meses, 'correlacao': correlacoes_mes}).set_index('mes')

fig, ax = plt.subplots(figsize=(10, 5)) 

sns.heatmap(df_corr_mes.T, annot=True, cmap='coolwarm', center=0,
            cbar_kws={'label': 'Correlação'}, ax=ax)

ax.set_xticks(np.arange(12) + 0.5)
ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'], rotation=0)

ax.set_title('Correlação entre nº de Eventos e Precipitação por Mês (1991–2024)')
ax.set_yticks([])

plt.tight_layout()
fig.savefig(os.path.join(repoPath, 'outputs', 'correlacaoEventos&PrecipitacaoSulBr1991-2024.png'))
plt.show()


#figura 7 - regularidade da chuva 

# Agrupa por mês e tira a média ao longo dos anos
media_mensal_pixel = prec_mm_mes.groupby('time.month').mean('time')

# Calcula amplitude (máximo - mínimo) da sazonalidade
amplitude_sazonal = media_mensal_pixel.max('month') - media_mensal_pixel.min('month')

# Plot
fig = plt.figure(figsize=(10,6))
ax = plt.axes(projection=ccrs.PlateCarree())

amplitude_sazonal.plot(ax=ax, cmap='YlOrRd', transform=ccrs.PlateCarree(),
                       cbar_kwargs={'label': 'Amplitude Sazonal (mm/mês)'})
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.set_title('Amplitude Sazonal da Precipitação (1980–2024)')
plt.show()
fig.savefig(os.path.join(repoPath, 'outputs', 'amplitudeSazonalPrecipitacaoSulBr1980-2024.png'))




















# # Agrupa por mês e ano
# prec_grouped = prec_mm_mes.groupby('time.year')  # ou ('time.year', 'time.month') dependendo do recorte

# # Cria um DataArray da série de eventos (média no Sul, por ano)
# eventos_ano = df_corr.groupby('ano')['n_eventos'].sum()
# eventos_ano = xr.DataArray(eventos_ano.values, coords=[eventos_ano.index], dims=['year'])

# # Agrega a precipitação também por ano
# prec_ano = prec_mm_mes.groupby('time.year').mean('time')  # média anual por pixel

# # Calcula a correlação pixel a pixel (simplificado)
# corr_map = xr.corr(prec_ano, eventos_ano, dim='year')
# print(corr_map)
# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
# import cartopy.feature as cfeature

# # Cria figura e eixo com projeção geográfica
# fig = plt.figure(figsize=(10, 8))
# ax = plt.axes(projection=ccrs.PlateCarree())

# # Adiciona recursos como costas, estados e limites
# ax.coastlines(resolution='10m', linewidth=0.8)
# ax.add_feature(cfeature.BORDERS, linestyle=':')
# ax.add_feature(cfeature.STATES, linewidth=0.5)

# # Define limites para o Sul do Brasil (ajuste se necessário)
# ax.set_extent([-57, -47, -34.5, -22.5], crs=ccrs.PlateCarree())

# # Plota o mapa da correlação
# img = corr_map.plot(
#     ax=ax,
#     transform=ccrs.PlateCarree(),
#     cmap='coolwarm',         # azul → negativo, vermelho → positivo
#     vmin=-1, vmax=1,
#     cbar_kwargs={
#         'label': 'Correlação (r)',
#         'shrink': 0.7,
#         'orientation': 'vertical'
#     }
# )

# # Título do gráfico
# plt.title('Correlação entre Precipitação Anual e Eventos Hidrológicos (1991–2024)', fontsize=12)

# plt.tight_layout()
# plt.show()



# ------------------------- TIRANDO ISSO AQUI QUE N É FIGURA
# #TEMOS GEODATAFRAME COM DATA DO EVENTO E GEOMETRY

# # Agrupar por ano e calcular a média para cada pixel (lat/lon)
# prec_sul_anual = prec_sul_1980_2024.groupby('time.year').mean('time')
# # Já temos o geoSul com geometrias dos municípios
# # Vamos cruzar com dfSulHidro (que tem os eventos por município e ano)

# # Junta eventos ocorridos (que tem data e cidade unica) com shapefile dos municípios (geometry)
# dfEventosGeo = dfSulHidro.merge(geoSul[['NM_MUN', 'SIGLA_UF', 'geometry']], 
#                                 left_on=['Nome_Municipio', 'Sigla_UF'],
#                                 right_on=['NM_MUN', 'SIGLA_UF'], how='left')
# # Transforma em GeoDataFrame
# gdfEventos = gpd.GeoDataFrame(dfEventosGeo, geometry='geometry', crs=geoSul.crs)

# ------------------------
# # 1. Converte o DataArray de precipitação para DataFrame
# # Formato: cada linha será um pixel em um mês (tempo, lat, lon, valor)

# df_prec = prec_mm_mes.to_dataframe(name='prec_mm').reset_index()

# # 2. Remove valores nulos
# df_prec = df_prec.dropna(subset=['prec_mm'])

# # 3. Converte para GeoDataFrame com pontos
# gdf_prec = gpd.GeoDataFrame(df_prec,
#                             geometry=gpd.points_from_xy(df_prec['lon'], df_prec['lat']),
#                             crs='EPSG:4326')  # Certifique-se de que o CRS está correto

# # 4. Faz junção espacial com municípios do Sul
# # certifique-se que `geoSul` também está em EPSG:4326
# if geoSul.crs != 'EPSG:4326':
#     geoSul = geoSul.to_crs('EPSG:4326')

# gdf_prec_mun = gpd.sjoin(gdf_prec, geoSul[['NM_MUN', 'SIGLA_UF', 'geometry']], how='inner', predicate='within')

# # 5. Agrupa por município, ano e mês, e calcula a média da precipitação
# gdf_prec_mun['ano'] = gdf_prec_mun['time'].dt.year
# gdf_prec_mun['mes'] = gdf_prec_mun['time'].dt.month

# prec_mensal_municipio = gdf_prec_mun.groupby(['NM_MUN', 'SIGLA_UF', 'ano', 'mes'])['prec_mm'].mean().reset_index()

# # 6. Cria coluna data para facilitar a correlação depois
# prec_mensal_municipio['data'] = pd.to_datetime(dict(year=prec_mensal_municipio['ano'],
#                                                     month=prec_mensal_municipio['mes'],
#                                                     day=1))






# geoSul e arquivonetcdf (prec_mm_mes)
# import xarray as xr

# ds = xr.open_dataset('seuarquivo.nc')
# prec = ds['TPRECMAX']  # ou o nome exato da variável
# prec_df = prec_mm_mes.to_dataframe().reset_index()

# prec_mm_mes=
# geoSul = geoSul.to_crs('EPSG:4326') 

# from shapely.geometry import Point

# prec_df = prec_df.dropna(subset=['TPRECMAX'])  # remove valores nulos
# prec_gdf = gpd.GeoDataFrame(
#     prec_df,
#     geometry=gpd.points_from_xy(prec_df.lon, prec_df.lat),
#     crs='EPSG:4326'
# )
# prec_com_mun = gpd.sjoin(prec_gdf, geoSul[['CD_MUN', 'geometry']], how='inner', predicate='within')

# prec_com_mun['ano'] = prec_com_mun['time'].dt.year
# prec_com_mun['mes'] = prec_com_mun['time'].dt.month

# # Média mensal por município
# prec_mun_mensal = prec_com_mun.groupby(['CD_MUN', 'ano', 'mes'])['TPRECMAX'].mean().reset_index()
# prec_mun_mensal.rename(columns={'TPRECMAX': 'precipitacao'}, inplace=True)


# #saiu algo aqui heinnnnnnnnnnnn
# # Média total (1980–2024) por município
# prec_mun_media = prec_mun_mensal.groupby('CD_MUN')['precipitacao'].mean().reset_index()
# prec_mun_media.rename(columns={'precipitacao': 'prec_media'}, inplace=True)
# geo_prec_media = geoSul.merge(prec_mun_media, on='CD_MUN', how='left')
# import matplotlib.pyplot as plt

# fig, ax = plt.subplots(figsize=(10, 8))
# geo_prec_media.plot(
#     column='prec_media',
#     cmap='YlGnBu',
#     linewidth=0.5,
#     edgecolor='grey',
#     legend=True,
#     ax=ax,
#     missing_kwds={
#         "color": "lightgrey",
#         "label": "Sem dados"
#     }
# )

# ax.set_title('Precipitação Média (1980–2024)\nMunicípios da Região Sul', fontsize=14)
# ax.axis('off')
# plt.tight_layout()
# plt.show()





# # Junta precipitação e eventos por município e mês
# df_correlacao = pd.merge(prec_mensal_municipio,
#                          dfSulHidro.groupby(['Nome_Municipio', 'Sigla_UF', 'ano', 'mes']).size().reset_index(name='n_eventos'),
#                          left_on=['NM_MUN', 'SIGLA_UF', 'ano', 'mes'],
#                          right_on=['Nome_Municipio', 'Sigla_UF', 'ano', 'mes'],
#                          how='left')

# # Substitui NaN por 0 nos eventos (nenhum evento naquele mês/município)
# df_correlacao['n_eventos'] = df_correlacao['n_eventos'].fillna(0)

# # Pronto para análises de correlação


# # Certifique-se de que ambos têm colunas: 'codigo_ibge', 'ano', 'mes'
# dfMerge = dfSulHidro.merge(prec_mensal_municipio, on=['Nome_Municipio', 'ano', 'mes'])

# # Calcula a correlação para cada município (linha = código IBGE)
# corrs_mun = dfMerge.groupby('codigo_ibge')[['precipitacao', 'eventos']].corr().iloc[0::2, -1]
# corrs_mun.name = 'correlacao'
# df_corr_mun = corrs_mun.reset_index()

# # Junta correlação com o GeoDataFrame
# geoSul_corr = geoSul.merge(df_corr_mun, on='codigo_ibge', how='left')
# import matplotlib.pyplot as plt

# fig, ax = plt.subplots(figsize=(10, 8))
# geoSul_corr.plot(column='correlacao', cmap='coolwarm', linewidth=0.5, edgecolor='grey',
#                  legend=True, ax=ax, missing_kwds={'color': 'lightgrey', "label": "Sem dados"})
# ax.set_title('Correlação Precipitação x Eventos Hidrológicos (1991–2024)\nMunicípios da Região Sul')
# ax.axis('off')

# # Salvar
# fig.savefig(os.path.join(repoPath, 'outputs', 'mapaCorrelacao_PrecEventos_Sul.png'), dpi=300)
# plt.show()






# # Garante o CRS certo
# geoSul = geoSul.to_crs("EPSG:4326")

# # Usa uma coluna de ID única dos municípios — aqui usaremos o código do IBGE
# # Se ainda não existir, crie:
# geoSul = geoSul.rename(columns={'CD_MUN': 'codigo_ibge'})  # ajuste conforme nome da sua base shapefile
# prec_mensal_municipio = prec_mensal_municipio.rename(columns={'NM_MUN': 'Nome_Municipio'})

# # Junta a precipitação média com os eventos (n_eventos), município por mês
# df_eventos_mensal = dfSulHidro.groupby(['Nome_Municipio', 'Sigla_UF', 'ano', 'mes']).size().reset_index(name='n_eventos')

# # Junta com precipitação
# df_merge = pd.merge(prec_mensal_municipio,
#                     df_eventos_mensal,
#                     on=['Nome_Municipio', 'SIGLA_UF', 'ano', 'mes'],
#                     how='left')

# # Preenche com zero onde não houve eventos
# df_merge['n_eventos'] = df_merge['n_eventos'].fillna(0)

# # Junta com código IBGE para cada município
# df_merge = df_merge.merge(geoSul[['Nome_Municipio', 'Sigla_UF', 'codigo_ibge']], 
#                           on=['Nome_Municipio', 'Sigla_UF'], how='left')

# # Calcula correlação precipitação x eventos por município
# corrs_mun = df_merge.groupby('codigo_ibge')[['prec_mm', 'n_eventos']].corr().iloc[0::2, -1]
# corrs_mun.name = 'correlacao'
# df_corr_mun = corrs_mun.reset_index()

# # Junta a correlação com o GeoDataFrame
# geoSul_corr = geoSul.merge(df_corr_mun[['codigo_ibge', 'correlacao']], on='codigo_ibge', how='left')

# # Plot do mapa
# fig, ax = plt.subplots(figsize=(10, 8))
# geoSul_corr.plot(column='correlacao',
#                  cmap='coolwarm',
#                  linewidth=0.5,
#                  edgecolor='grey',
#                  legend=True,
#                  ax=ax,
#                  missing_kwds={'color': 'lightgrey', "label": "Sem dados"})

# ax.set_title('Correlação Precipitação x Eventos Hidrológicos (1991–2024)\nMunicípios da Região Sul')
# ax.axis('off')

# # Salva o mapa
# os.makedirs(os.path.join(repoPath, 'outputs'), exist_ok=True)
# fig.savefig(os.path.join(repoPath, 'outputs', 'mapaCorrelacao_PrecEventos_Sul.png'), dpi=300)
# plt.show()






