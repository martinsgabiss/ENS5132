# -*- coding: utf-8 -*-
"""
Created on Tue May 13 13:37:35 2025
Analisando no espaço com dados do ibge
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/Brasil/BR_Municipios_2024.zip

@author: jrmjr
"""
#importando pacotes

import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx
import rasterio as rio
import rasterio.mask
import numpy as np

#caminho para o arquivo com o shapefile dos municípios - da pra automatizar la com o os
munPath = r"C:\Users\jrmjr\Documents\ENS5132\Projeto02\inputs\BR_Municipios_2024\BR_Municipios_2024.shp"

# abrindo o arquivo shapefile
geoMun = gpd.read_file(munPath)

# Extraindo o sistema de coordenadas de refe^rencias
geoMun.crs
#<Geographic 2D CRS: EPSG:4674>
#Name: SIRGAS 2000
#- Lat[north]: Geodetic latitude (degree)
#- Lon[east]: Geodetic longitude (degree)

# Extraindo a área - cuidado ainda não convertido! - está em graus/degrees
#(transformar crs - oq é isso? Coordinate Reference System - sistema de referência precisaa ser igual)
geoMun['AREA_graus'] = geoMun.geometry.area

# Converter para UTM - PSEUDO-MERCATOR (deformação) - é uma variante da 
#projeção de Mercator usada para mapeamento online. 
geoMun= geoMun.to_crs('epsg:3857')

# Extraindo a área - cuidado ainda não convertido!
geoMun['AREA_km2Novo'] = geoMun.geometry.area/(10**6)
#deu diferença na área - cuidar a distorção!!!!

#pip install utm - calcular a area com a zona adequada - pesquisa google!

#Converter para WGS84 python - aparentemente é mais compativel este CRS
geoMun= geoMun.to_crs('epsg:4326')

# Extraindo o centroide
#as vezes precisa que coloque geometry , neste caso não, pq,n sei?
# geoMun.centroid = retorna o centroide da coluna de geometria ativa (normalmente geometry)
# geoMun.geometry.centroid = mesma coisa, mas você está especificando explicitamente a coluna
geoMun['centroid']= geoMun.centroid

# Extraindo bordas/contorno
geoMun['boundary'] = geoMun.boundary

#Dados no espaço – ponto, linha, polígono, pixel, etc. 
#Pacote geopandas
#Leitura de arquivos
#Analisar e alterar CRS
#Explorar atributos (área, centroide,boundary)

# Extraindo limites, (minx, miny, maxx, maxy)
geoMun.geometry[0].bounds
#vai ser bem útil, no trablho, agora n entendo

#Criando uma geometria  dentro do geopandas
# (lat,lon) - (y,x)

#Criando um ponto e transformando em um geopandas
#ludico

#object shapely
pontoQualquer = Point(-27, -49)

#Para geopandas
pontoQualquer = gpd.GeoSeries(pontoQualquer, crs=4326)
#Você agora tem um ponto geográfico com coordenadas lon -49 e lat -27, 
#armazenado em um objeto do GeoPandas com o sistema de coordenadas WGS84 (EPSG:4326 — graus decimais)

# Calculando distância entre pontpQualquer e controide das cidades
geoMun['dist'] = [float(pontoQualquer.distance(centroid)) / 1000 for centroid in geoMun.centroid]


# Abrindo um arquivo com coordenadas
#os usar aqui, n lembro!!!

stationPath = r"C:\Users\jrmjr\Documents\ENS5132\Projeto02\inputs\Monitoramento_QAr_BR_latlon_2024.csv" 

#Abrindo com pandas
stations = pd.read_csv(stationPath)
#para identificar como a geometria tem que estar daquele forma de point etc

#Transformando para geopandas
gdf = gpd.GeoDataFrame( stations, 
                       geometry= gpd.points_from_xy(
                           stations.LONGITUDE, stations.LATITUDE), 
                       crs="EPSG:4326" ) 

# Plotando na figura
#OBSERVAÇÃO- ELE QUER QUE ORGANIZE MELHOR O CODIGO, NÃO ASSIM DO JEITO QUE ESTÁ: POR EXEMPLO ESSA FIGURA
fig, ax = plt.subplots()
geoMun.boundary.plot(ax=ax, color='gray', linewidth = 0.2)
gdf.plot(ax=ax)

#plot usando folium
gdf.geometry.explore()

# Buffer ao redor das estações
#3000 = quanto +- representa uma estação de monit no espaço ,3000 metros (3 km) ao redor de cada ponto.
gdf['buffer'] = gdf.to_crs('epsg:3857').buffer(3000).to_crs('epsg:4326')

#operações espaciais

# area total monitorada em km^2
areaMonitorada = gdf['buffer'].to_crs('epsg:3857').unary_union.area/(10**6)
#unary_union para tirar a dupla contagem de area

# área do BR
areaBR = geoMun.AREA_km2Novo.sum()
porcentagemMonitorada = (areaMonitorada/areaBR)*100
print(porcentagemMonitorada)

#unindo geometrias
#pegou todas as estações e diz o municipio
#juntou gdf,geoMun
geoUnion = gpd.sjoin(geoMun,gdf,how='inner')

#figura com mapa de fundo
#ax = gdf.to_crs('epsg:3857').plot(figsize=(10,10)), alpha=0.5, edgecolor = 'k'
#cx.add_basemap(ax, source=cx.providers.Esri.WorldPhysical)

# Figura com mapa de fundo
ax = gdf.to_crs('epsg:3857').plot(column=gdf['ESTADO'],figsize=(10, 10), alpha=0.5, edgecolor="k")
cx.add_basemap(ax, source=cx.providers.Esri.WorldPhysical)
#geoMun estava já no epsg 3857


#%% Análise usando raster

mapBiomasPath= r"C:\Users\jrmjr\Documents\ENS5132\Projeto02\inputs\mapbiomas_10m_collection2_integration_v1-classification_2023 (1).tif"

# Abrindo o arquivo utilizando o rasterio
src = rio.open(mapBiomasPath)

# Extraindo coordenadas dos pontos para uma lista
gdfUnique = gdf.geometry.unique()
coord_list = [(x,y) for x, y in zip(gdf.geometry.x, gdf.geometry.y)]

# amostrando os pontos no raster mapbiomas
gdf['mapbiomas'] = [x[0] for x in src.sample(coord_list)]

#Contagem de estaçõespor uso de solo
contaUso = gdf.groupby(['mapbiomas']).count()

#grafico de barras com o uso do solo onde as estações estão instaladas
fig, ax = plt.subplots()
ax.bar(contaUso.index,contaUso.ESTADO)

---
with rio.open(mapBiomasPath) as src:
    crsOriginal = src.crs
    print(crsOriginal.to_epsg())
    out_image, out_transform = rasterio.mask.mask(src,
                                             [gdf.iloc[0,:].buffer],
                                             crop=True)
    # Extraindo propriedades do raster
    out_meta = src.meta
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    # Se conseguir recortar...
    if out_meta:   
        # Abre um novo arquvio e salva na pasta de outputs recortado
        with rio.open('teste.tif', "w", **out_meta) as dest:
            dest.write(out_image)
    


# Open the raster
raster = riox.open_rasterio("teste.tif")

# Reproject to EPSG:3857
raster_3857 = raster.rio.reproject("EPSG:3857")

# Save the reprojected raster
#raster_3857.rio.to_raster("output_3857.tif")

# Cuidado com o tamanho da figura
# fig,ax = plt.subplots()
# ax.pcolor(xs.reshape(cols.shape),ys.reshape(cols.shape),out_image[0,:,:])

# Selecionando primeiro ponto de monitoramento para plotar
# Precisa converter para PseudoMercator para utilizar o Contextly
gdfTarget = gdf.to_crs('epsg:3857')[gdf.index==0]

#Sem converter
gdfTarget = gdf[gdf.index==0]

# Figura com mapa de fundo
ax = gdfTarget.plot(figsize=(10, 10), alpha=0.5, edgecolor="k")
raster.plot(ax=ax, alpha=0.1)
#plt.pcolor(xs.reshape(cols.shape),ys.reshape(cols.shape),out_image[0,:,:],alpha=0.2)
cx.add_basemap(ax, source=cx.providers.Esri.WorldPhysical, crs=gdfTarget.crs)




