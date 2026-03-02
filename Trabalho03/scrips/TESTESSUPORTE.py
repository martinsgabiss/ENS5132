# -*- coding: utf-8 -*-
"""
Created on Fri Jul  4 20:48:46 2025

@author: jrmjr
"""

TESTES DE GRAFICOS PRA ANALISE DE PRECIPITAÇÃO, DESASTRES HIDROLOGICOS!

#AQUI É SAZONALIDADE !!!!! MILHOES DE LINHAS - COLORIDAS E LEGENDA EM TODOS OS ANOS, NO CODIGO PRINCIPAL TODAS ESTAO CINZAS, E MEDIA EM PRETO 

import pandas as pd

# Converter a média de precipitação para uma tabela com ano e mês
df = prec_mm_mes.mean(dim=['lat', 'lon']).to_dataframe(name='precipitacao')
df['ano'] = df.index.get_level_values('time').year
df['mes'] = df.index.get_level_values('time').month

# Pivotar para ter meses nas colunas e anos nas linhas
tabela_sazonal = df.pivot_table(index='ano', columns='mes', values='precipitacao')

# Plotar
plt.figure(figsize=(12, 6))
for ano in tabela_sazonal.index:
    plt.plot(tabela_sazonal.columns, tabela_sazonal.loc[ano], label=str(ano), alpha=0.3)

plt.plot(tabela_sazonal.columns, tabela_sazonal.mean(axis=0), color='black', linewidth=2.5, label='Média 1980–2024')

plt.title('Sazonalidade Anual da Precipitação (Sul do Brasil, 1980–2024)')
plt.xlabel('Mês')
plt.ylabel('Precipitação Média (mm/mês)')
plt.xticks(ticks=range(1, 13), labels=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
plt.legend(loc='upper right', fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.show()


media = tabela_sazonal.mean(axis=0)
std = tabela_sazonal.std(axis=0)

plt.plot(media.index, media, color='black', linewidth=2, label='Média 1980–2024')



#ACHO QUE COM DESVIO PADRÃO E MENOS ANOS
#tentando melhorar a visualização do grafico
import matplotlib.pyplot as plt

# Converter para mm/mês (se ainda não estiver)
prec_mm_mes = prec_sul_1980_2024 * 2.63e6

# Criar DataFrame com a média mensal por ano
prec_df = prec_mm_mes.groupby('time').mean(['lat', 'lon']).to_dataframe(name='prec')
prec_df['Ano'] = prec_df.index.year
prec_df['Mes'] = prec_df.index.month

# Pivotar para formato (Ano x Mês)
df_pivot = prec_df.reset_index().pivot(index='Ano', columns='Mes', values='prec')

# Calcular estatísticas
media_mensal = df_pivot.mean(axis=0)
desvio_mensal = df_pivot.std(axis=0)

# Anos selecionados para destacar
anos_destaque = [1980, 1990, 2000, 2010, 2020, 2024]

# Plot
plt.figure(figsize=(12, 6))

# Faixa de desvio padrão
plt.fill_between(
    media_mensal.index,
    media_mensal - desvio_mensal,
    media_mensal + desvio_mensal,
    color='lightgray',
    alpha=0.5,
    label='±1 Desvio Padrão'
)

# Linhas dos anos selecionados
for ano in anos_destaque:
    if ano in df_pivot.index:
        plt.plot(df_pivot.columns, df_pivot.loc[ano], label=str(ano), linestyle='--')

# Linha média
plt.plot(media_mensal.index, media_mensal.values, color='black', linewidth=2.5, label='Média 1980–2024')

# Estética
plt.xticks(ticks=range(1, 13), labels=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
plt.title('Sazonalidade Média da Precipitação (Sul do Brasil, 1980–2024)', fontsize=14)
plt.xlabel('Mês')
plt.ylabel('Precipitação Média (mm/mês)')
plt.legend(loc='upper right', ncol=2)
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()


#NEM LEMBRO OQ FAZ NEM QUERO LER E PENSAR

# # Média da precipitação ao longo do tempo (1980–2024)
# media_espacial = prec_sul_1980_2024.mean(dim='time')

# # Criar figura e eixo com projeção geográfica
# fig = plt.figure(figsize=(10, 6))
# ax = plt.axes(projection=ccrs.PlateCarree())  # eixo com projeção

# # Adicionar contornos de estados ou países (opcional)
# ax.add_feature(cfeature.COASTLINE)
# ax.add_feature(cfeature.BORDERS, linestyle=':')
# ax.add_feature(cfeature.STATES, linestyle=':', edgecolor='gray')

# # Plotar com o eixo projetado
# media_espacial.plot(
#     ax=ax,
#     cmap='Blues',
#     transform=ccrs.PlateCarree(),  # dados estão em lat/lon
#     cbar_kwargs={'label': 'Precipitação média (kg/m²/s)'}
# )

# ax.set_title('Média da Precipitação no Sul do Brasil (1980–2024)')
# plt.show()

#GRAFICO QUE MOSTRA LINHAS ENTRE NUMERO DE EVENTOS E PRECIPITAÇÃO
# Selecionar o ano de interesse
ano_focus = 2023

# Filtrar a precipitação para esse ano, calcular média mensal espacial (Sul do Brasil)
prec_ano = (
    prec_mm_mes
    .sel(time=str(ano_focus))
    .groupby('time.month')
    .mean(dim=['lat', 'lon'], skipna=True)
    .to_dataframe()
    .reset_index()
)

# Renomear coluna
# Extrair mês da coluna 'time' após reset_index
prec_ano['mes'] = prec_ano['time'].dt.month

# Renomear a coluna da variável de precipitação
prec_ano = prec_ano.rename(columns={'TPRECMAX': 'prec_media'})

# Filtrar eventos para o mesmo ano
eventos_ano = eventos_mensal[eventos_mensal['ano'] == ano_focus].copy()

# Garantir que todos os meses estão presentes no gráfico
todos_meses = pd.DataFrame({'mes': range(1, 13)})
prec_ano = pd.merge(todos_meses, prec_ano, on='mes', how='left')
eventos_ano = pd.merge(todos_meses, eventos_ano, on='mes', how='left')
eventos_ano['n_eventos'] = eventos_ano['n_eventos'].fillna(0)

# Juntar os dois DataFrames
df_final = pd.merge(prec_ano, eventos_ano[['mes', 'n_eventos']], on='mes', how='left')

# Plotando gráfico combinado
fig, ax1 = plt.subplots(figsize=(10, 5))

# Barras: eventos
ax1.bar(df_final['mes'], df_final['n_eventos'], color='cornflowerblue', label='Eventos Hidrológicos')
ax1.set_ylabel('Nº de Eventos', color='cornflowerblue')
ax1.set_xlabel('Mês')
ax1.set_xticks(range(1, 13))
ax1.set_title(f'Eventos Hidrológicos e Precipitação Média Mensal - {ano_focus}')

# Linha: precipitação
ax2 = ax1.twinx()
ax2.plot(df_final['mes'], df_final['prec_media'], color='darkgreen', marker='o', label='Precipitação Média')
ax2.set_ylabel('Precipitação Média (mm)', color='darkgreen')

# Legenda
fig.legend(loc="upper right", bbox_to_anchor=(0.85, 0.85))
plt.tight_layout()
plt.show()


#ESSE DEU ERRO NEM SEI
# Definir o ano de interesse
ano_interesse = 2015

# Selecionar somente esse ano no DataArray
prec_ano = prec_sul.sel(time=slice(f'{ano_interesse}-01-01', f'{ano_interesse}-12-31'))

# Calcular a média espacial (lat/lon) para cada mês
prec_mensal = prec_ano.groupby('time.month').mean(dim=['lat', 'lon']).to_dataframe(name='prec_media').reset_index()
# Filtrar eventos somente do ano desejado
eventos_ano = dfSulHidro[dfSulHidro['ano'] == ano_interesse]

# Contar eventos por mês
eventos_mensal = eventos_ano.groupby('mes').size().reset_index(name='n_eventos')

# Mesclar pelos meses (1 a 12)
df_plot = pd.merge(prec_mensal, eventos_mensal, left_on='month', right_on='mes', how='left')

# Preencher meses sem eventos com zero
df_plot['n_eventos'] = df_plot['n_eventos'].fillna(0).astype(int)

#N LEMBRO TBM OQ ERA

# # Média espacial e soma anual (total de precipitação por ano no Sul)
# prec_anual = prec_sul_1980_2024.mean(dim=['lat', 'lon'])  # média espacial
# prec_anual_df = prec_anual.groupby('time.year').sum('time').to_dataframe(name='precipitacao_total').reset_index()
# prec_anual_df.rename(columns={'year': 'ano'}, inplace=True)

# eventos_anuais = dfSulHidro.groupby('ano').size().reset_index(name='n_eventos')

# df_anual = pd.merge(prec_anual_df, eventos_anuais, on='ano', how='left')
# df_anual['n_eventos'] = df_anual['n_eventos'].fillna(0)

# import matplotlib.pyplot as plt

# fig, ax1 = plt.subplots(figsize=(12,6))

# # Linha de precipitação
# ax1.set_xlabel('Ano')
# ax1.set_ylabel('Precipitação Total (mm)', color='tab:blue')
# ax1.plot(df_anual['ano'], df_anual['precipitacao_total'], color='tab:blue', label='Precipitação')
# ax1.tick_params(axis='y', labelcolor='tab:blue')

# # Segundo eixo: eventos
# ax2 = ax1.twinx()
# ax2.set_ylabel('Nº de Eventos Hidrológicos', color='tab:red')
# ax2.plot(df_anual['ano'], df_anual['n_eventos'], color='tab:red', label='Eventos')
# ax2.tick_params(axis='y', labelcolor='tab:red')

# plt.title("Precipitação total x Eventos hidrológicos anuais (Sul do Brasil)")
# plt.show()





# # Transformar para DataFrame agrupado por ano e mês
# prec_mensal_df = prec_sul_1980_2024.mean(dim=['lat', 'lon']).to_dataframe(name='precipitacao').reset_index()
# prec_mensal_df['ano'] = prec_mensal_df['time'].dt.year
# prec_mensal_df['mes'] = prec_mensal_df['time'].dt.month

# # Agrupar por ano e mês
# prec_mensal_df = prec_mensal_df.groupby(['ano', 'mes'])['precipitacao'].mean().reset_index()

# # Já tínhamos isso antes:
# eventos_mensal = dfSulHidro.groupby(['ano', 'mes']).size().reset_index(name='n_eventos')

# # Agora, juntamos com precipitação
# df_comparacao = pd.merge(prec_mensal_df, eventos_mensal, on=['ano', 'mes'], how='left')

# # Preencher com 0 os meses sem eventos
# df_comparacao['n_eventos'] = df_comparacao['n_eventos'].fillna(0)


# import matplotlib.pyplot as plt
# import seaborn as sns

# plt.figure(figsize=(12,6))
# sns.lineplot(data=df_comparacao, x='mes', y='precipitacao', hue='ano', palette='Blues', alpha=0.5, legend=None)
# sns.scatterplot(data=df_comparacao, x='mes', y='precipitacao', size='n_eventos', hue='n_eventos', palette='Reds')
# plt.title("Precipitação mensal e número de eventos hidrológicos")

    







# import xarray as xr
# import geopandas as gpd
# import pandas as pd

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

# # Abrir precipitação e shapefile

# prec.name = 'prec_mm'

# # Shapefile dos municípios do Sul

# geoSulNew = geoSul[['CD_MUN', 'NM_MUN', 'geometry']]  # manter colunas essenciais



# # Converter de tempo mensal
# prec_mensal = prec.groupby('time.month').groupby('time.year')

# # Lista para armazenar resultados
# lista_dfs = []

# # Loop sobre todos os meses
# for t in prec.time.values:
#     da = prec.sel(time=t)

#     # Média espacial por município para esse mês
#     zonal = da.rio.clip(geoSul.geometry, geoSul.crs).mean(dim='time', skipna=True)
#     df_mes = da.rio.clip(geoSul.geometry, geoSul.crs).rio zonal_stats(geoSul, stats="mean", geojson_out=True)
    
#     # Alternativa manual (mais robusta): usar masked mean
#     values = da.rio.clip(geoSul.geometry, geoSul.crs, drop=True, all_touched=True)
#     df_temp = geoSul.copy()
#     df_temp['prec_mm'] = values.mean(dim=('lat', 'lon')).values
#     df_temp['time'] = pd.to_datetime(str(t))
#     df_temp['ano'] = df_temp['time'].dt.year
#     df_temp['mes'] = df_temp['time'].dt.month
#     lista_dfs.append(df_temp[['CD_MUN', 'NM_MUN', 'ano', 'mes', 'prec_mm']])
    
# # Unir tudo
# df_prec_mun = pd.concat(lista_dfs, ignore_index=True)

# # dfEventos com colunas: ['codigo_ibge', 'ano', 'mes', 'qtd_eventos']
# # dfPrecMun com colunas: ['codigo_ibge', 'ano', 'mes', 'precipitacao']

# df_merged = dfEventos.merge(dfPrecMun, on=['codigo_ibge', 'ano', 'mes'])

# # Agrupar por município
# corrs_municipio = df_merged.groupby('codigo_ibge')[['qtd_eventos', 'precipitacao']].corr().iloc[0::2, -1]

# # Juntar com shapefile para mapear
# gdfMun['correlacao'] = gdfMun['codigo_ibge'].map(corrs_municipio)




# import xarray as xr
# import geopandas as gpd
# import rioxarray  # para trabalhar com raster + vetorial
# import pandas as pd
# import numpy as np


# # 4. Função para extrair média mensal por município
# def extrair_media_precipitacao_por_municipio(ds_prec, gdf_municipios):
#     resultados = []
    
#     for _, mun in gdf_municipios.iterrows():
#         # Máscara do polígono do município
#         poligono = mun['geometry']
        
#         # Recorte espacial do dataset pela área do município
#         ds_recortado = ds_prec.rio.clip([poligono], gdf_municipios.crs, drop=True, invert=False)
        
#         # Calcular média espacial mensal dentro do município
#         # ds_recortado tem dimensão time, lat, lon
#         media_mensal = ds_recortado.mean(dim=['lat', 'lon'], skipna=True)
        
#         # Converter para DataFrame e adicionar colunas do município
#         df_mun = media_mensal.to_dataframe(name='precipitacao').reset_index()
#         df_mun['codigo_ibge'] = mun['codigo_ibge'] if 'codigo_ibge' in mun else mun['CD_MUN']
#         df_mun['municipio'] = mun['NM_MUN']
#         df_mun['uf'] = mun['SIGLA_UF']
        
#         resultados.append(df_mun)
        
#     # Concatenar resultados para todos os municípios
#     df_result = pd.concat(resultados, ignore_index=True)
    
#     # Extrair ano e mês da coluna time para facilitar merge futuro
#     df_result['ano'] = df_result['time'].dt.year
#     df_result['mes'] = df_result['time'].dt.month
    
#     return df_result[['codigo_ibge', 'municipio', 'uf', 'ano', 'mes', 'precipitacao']]

# # 5. Rodar a função para obter precipitação mensal média por município
# prec_mun_mensal = extrair_media_precipitacao_por_municipio(prec_mm_mes, geoSul)

# print(prec_mun_mensal.head())


# # Certifique-se de que ambos têm colunas: 'codigo_ibge', 'ano', 'mes'
# dfMerge = dfSulHidro.merge(prec_mun_mensal, on=['codigo_ibge', 'ano', 'mes'])

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






----------------------------------
municipios = heat_prec.columns
meses = range(1, 13)

# DataFrame para armazenar as correlações
df_corr_municipios = pd.DataFrame(index=municipios, columns=meses)
for mes in meses:
    for mun in municipios:
        serie_prec = heat_prec_1991.loc[:, mes][mun]
        serie_eventos = heat_eventos_1991.loc[:, mes][mun]

        # Só calcula se tiver dados suficientes
        if serie_prec.notna().sum() > 5 and serie_eventos.notna().sum() > 5:
            corr = serie_prec.corr(serie_eventos)
        else:
            corr = np.nan

        df_corr_municipios.loc[mun, mes] = corr
plt.figure(figsize=(14, 10))
sns.heatmap(df_corr_municipios.astype(float), cmap='coolwarm', center=0,
            annot=False, cbar_kws={'label': 'Correlação'})
plt.title('Correlação entre Eventos e Precipitação por Município e Mês')
plt.xlabel('Mês')
plt.ylabel('Município')
plt.xticks(ticks=np.arange(12)+0.5, labels=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'], rotation=45)
plt.tight_layout()
plt.show()
