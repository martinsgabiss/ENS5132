# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 19:59:25 2025

@author: jrmjr
"""
#importando pacotes

import os # Manipulação de caminhos e arquivos
import geopandas as gpd  # Manipulação de dados espaciais vetoriais (shapefiles)
import matplotlib.pyplot as plt # Geração de gráficos e mapas estáticos
import folium # Geração de mapas interativos

import rasterio.mask # Recorta em rasters 
from rasterio.mask import mask  # Máscara raster
from rasterio.features import shapes # Para converter raster para vetor
from shapely.geometry import shape #Converte dicionários GeoJSON em objetos geométricos
import numpy as np # Operações numéricas com arrays
import pandas as pd #Manipulação de tabelas

#%% Organizando os dados com shapefiles

repoPath = r'C:\Users\jrmjr\Documents\ENS5132\Trabalho02'
scCrs = "EPSG:31982"

def ucsSpatialAnalysis(repoPath):
    """
    Abre shapefiles de municípios e unidades de conservação a partir de um repositório base.
    
    """
    #  - Abrindo os dados 
    dadosMun = 'BR_Municipios_2024'
    dadosUcs = 'limites_ucs_federais'
    
    # Caminhos para as pastas dos shapefiles
    munPath = os.path.join(repoPath, 'inputs', dadosMun, 'BR_Municipios_2024.shp')
    ucPath = os.path.join(repoPath, 'inputs', dadosUcs, 'limites_ucs_federais_27022025_a.shp' )
    
    # Abrindo com geopandas
    geoMun = gpd.read_file(munPath)
    geoUCs = gpd.read_file(ucPath)

    # Extraindo o sistema de coordenadas de refe^rencias
    geoMun.crs
    #EPSG:4674>
    geoUCs.crs
    # EPSG:4674>
    
    #Filtrando somente dados de SC
    geoSC = geoMun[geoMun['SIGLA_UF'] == 'SC'] 
    geoUCsSC = geoUCs[geoUCs['UFAbrang'] == 'SC']
    
    geoMun = geoMun.to_crs(scCrs)
    geoUCs = geoUCs.to_crs(scCrs)
    geoSC = geoSC.to_crs(scCrs)
    geoUCsSC = geoUCsSC.to_crs(scCrs)
    
    # Filtrar a UC 'PARQUE NACIONAL DA SERRA DO ITAJAÍ' (filtra a linha desejada e cria cópia independente)
    gdfIta = geoUCsSC[geoUCsSC['NomeUC'].str.contains('PARQUE NACIONAL DA SERRA DO ITAJAÍ', 
                                                          case=False)].copy()
    if gdfIta.empty:
        raise ValueError("Parque Nacional da Serra do Itajaí não encontrado no GeoDataFrame.")
     
    gdfIta = gdfIta.to_crs(scCrs)
    
    #Mapa simples com limite de SC e destacado a UC
    fig, ax = plt.subplots(figsize=(12, 12))

    # Contorno dos municípios
    geoSC.boundary.plot(ax=ax, color='gray', linewidth=0.5)

    # Preenchimento da UC em vermelho
    gdfIta.plot(ax=ax,
                  color='red',
                  edgecolor='black',
                  linewidth=0.5,
                  alpha=0.5)  # transparência para visualizar o fundo

    # Título e estética
    plt.title('Unidade de Conservação Parque Nacional da Serra do Itajaí', fontsize=14)
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()
    
    #Criando um mapa iterativo da UNIDADE DE CONSERVAÇÃO DA SERRA DO ITAJAÍ
    m = gdfIta.explore( 
        column='NomeUC',    
        cmap='tab20',        # Paleta de cores 
        legend=True, 
        tooltip='NomeUC'    # Mostra nome ao passar o mouse 
        )
    m
       # Salvar o mapa interativo no caminho desejado
    m.save(os.path.join(repoPath, 'outputs', 'mapa_uc_Serra_Itajaí.html'))
   
    return geoMun, geoUCs, geoUCsSC, geoSC, gdfIta
#%% Abrindo arquivos com Raster

def ucsSCSpatialComparison1985_2023(repoPath, geoUCsSC, gdfIta):

    # Carregando os dois rasters (1985 e 2023)
    mapBiomas1985 = rasterio.open(os.path.join(repoPath, 'inputs', 'brasil_coverage_1985.tif'))
    mapBiomas2023 = rasterio.open(os.path.join(repoPath, 'inputs', 'brasil_coverage_2023.tif'))

    # Garantir CRS compatível pelo menos UMA vez
    if gdfIta.crs != mapBiomas2023.crs:#se o crs for diferente
        gdfIta = gdfIta.to_crs(mapBiomas2023.crs) #transforma o crs de ita para o do raster

    # Obter geometria da UC para posterior recorte
    geoms = gdfIta.geometry.values # extrai os valores dessa coluna como um array ou algo semelhante
    
    # Extraindo os dados do raster apenas dentro da UC 'PARQUE NACIONAL DA SERRA DO ITAJAÍ' 
    out_image_1985, out_transform_1985 = mask(mapBiomas1985, geoms, crop=True)        
    out_image_2023, out_transform_2023 = mask(mapBiomas2023, geoms, crop=True)        

    # Limpando os dados
    land_1985 = np.where(out_image_1985[0] == mapBiomas1985.nodata, np.nan, out_image_1985[0])
    land_2023 = np.where(out_image_2023[0] == mapBiomas2023.nodata, np.nan, out_image_2023[0])
    
    #Classes de uso do solo
    classes1985 = np.unique(land_1985[~np.isnan(land_1985)]).astype(int)
    classes2023 = np.unique(land_2023[~np.isnan(land_2023)]).astype(int)

    # Função para vetorizar raster - transformar esse raster(land_"x") em um GeoDataFrame
    def raster_to_vector(raster_array, transform, crs):
        mask_array = ~np.isnan(raster_array) #máscara booleana diz valores válidos no raster (onde não é np.nan)
        shapes_gen = (
            {"geometry": shape(geom), "uso_solo": int(value)}
            for geom, value in shapes(raster_array, mask=mask_array, transform=transform)
        ) #exrai vetores(poligonos)
        records = list(shapes_gen)
        
        # Cria GeoDataFrame sem o CRS, depois define o CRS separadamente
        gdf = gpd.GeoDataFrame(records)
        gdf.set_crs(crs, inplace=True)
        
        return gdf
    # Vetorizar
    gdf1985 = raster_to_vector(land_1985, out_transform_1985, mapBiomas1985.crs).to_crs(scCrs)
    gdf2023 = raster_to_vector(land_2023, out_transform_2023, mapBiomas2023.crs).to_crs(scCrs)

#5: {'label': 'Mangue (floresta)', 'color': '#04381d'},
#24: {'label': 'Área Urbanizada', 'color': '#d4271e'},
#32: {'label': 'Apicum (vegetação herbácea e arbustiva)', 'color': '#fc8114'},
#49: {'label': 'Restinga arbórea (floresta)', 'color': '#02d659'},

    # Legenda MapBiomas simplificada
    legend = {
        0: {'label': 'Sem informação', 'color': '#ffffff'},
        3: {'label': 'Formação Florestal (floresta)', 'color': '#1f8d49'},
        9: {'label': ' Silvicultura ', 'color': '#7a5900'},
        15: {'label': 'Pastagem (agropecuária)', 'color': '#edde8e'},
        21: {'label': 'Mosaico de Usos (agropecuária)', 'color': '#ffefc3'},
        25: {'label': 'Outras Áreas não Vegetadas', 'color': '#db4d4f'},
        29: {'label': 'Afloramento Rochoso (vegetação herbácea e arbustiva)', 'color': '#ffaa5f'},
        33: {'label': 'Rio, Lago e Oceano', 'color': '#2532e4'},
        41: {'label': 'Outras Lavouras Temporárias (agricultura)', 'color': '#f54ca9'},
        }
  
    def plot_vector_map(gdf, legend, year, uc_name="PARQUE NACIONAL DA SERRA DO ITAJAÍ", save=True):
        gdf = gdf.to_crs("EPSG:4326")
        # Calcular centro do mapa (latitude, longitude)
        center = gdf.geometry.unary_union.centroid.coords[0][::-1]
     # gdf1985.geometry.unary_union: une todos os polígonos em uma única geometria.
     # .centroid: calcula o centro (ponto médio) dessa geometria.
     # .coords[0]: extrai as coordenadas (x, y).
     # [::–1]: inverte para (latitude, longitude), como o folium exige.
     
        # Criar mapa base
        m = folium.Map(location=center, zoom_start=12, tiles='CartoDB positron')
     # tiles: estilo do fundo do mapa (limpo e claro)
     
        # Adicionar polígonos por classe
        for val, info in legend.items():
            subset = gdf[gdf['uso_solo'] == val]
            if not subset.empty:
                folium.GeoJson(
                    subset,
                    style_function=lambda x, color=info['color']: {
                        'fillColor': color,
                        'color': color,
                        'weight': 0.5,
                        'fillOpacity': 0.6
                    },
                    name=info['label']
                ).add_to(m)
    
        # Adicionar controle de camadas
        folium.LayerControl().add_to(m)
    
        # Salvar HTML
        if save:
            safe_name = uc_name.replace(" ", "_").replace("/", "_")
            filename = f'uso_solo_{year}_{safe_name}.html'
            m.save(os.path.join(repoPath, 'outputs', filename))
    
        return m

    plot_vector_map(gdf1985, legend, year=1985)
    plot_vector_map(gdf2023, legend, year=2023)


# Verificando dados por área em hectares
    
    def calcular_area_por_classe(gdf, ano, epsg_metrico=5880):
        # Reprojetar para CRS métrico adequado (metros)
        gdf_metrico = gdf.to_crs(epsg=epsg_metrico)
    
        # Calcular área em hectares (1 hectare = 10.000 m²)
        gdf_metrico['area_ha'] = gdf_metrico.area / 10000
    
        # Agrupar por classe de uso do solo
        area_por_classe = gdf_metrico.groupby('uso_solo')['area_ha'].sum().reset_index()
        area_por_classe.columns = ['uso_solo', f'area_ha_{ano}']
        
        return area_por_classe
    
    # Calcular para ambos os anos
    area_1985 = calcular_area_por_classe(gdf1985, 1985)
    area_2023 = calcular_area_por_classe(gdf2023, 2023)
    
    # Juntar em um único DataFrame
    df_area = pd.merge(area_1985, area_2023, on='uso_solo', how='outer').fillna(0)
    
    # rótulos da legenda MapBiomas
    df_area['legenda'] = df_area['uso_solo'].map({k: v['label'] for k, v in legend.items()})
    
    # Reordenar colunas
    df_area = df_area[['uso_solo', 'legenda', 'area_ha_1985', 'area_ha_2023']]
    
    dfAtual = df_area.drop(index=0)
    
        # Ordenar pelas maiores áreas totais
    dfAtual['area_total'] = dfAtual['area_ha_1985'] + dfAtual['area_ha_2023']
    dfAtual = dfAtual.sort_values(by='area_total', ascending=False)
    
    # Dados
    codigos = dfAtual['uso_solo']
    descricao_legenda = dfAtual['legenda']
    area_1985 = dfAtual['area_ha_1985'].replace(0, 0.1)
    area_2023 = dfAtual['area_ha_2023'].replace(0, 0.1)
    
    x = np.arange(len(codigos))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Barras sobrepostas com transparência
    bar_1985 = ax.bar(x, area_1985, width=0.6, color='steelblue', label='1985', alpha=0.6)
    bar_2023 = ax.bar(x, area_2023, width=0.4, color='orange', label='2023', alpha=0.6)
    
    # Eixo logarítmico
    ax.set_yscale('log')
    
    # Eixo X com códigos numéricos
    ax.set_xlabel('Uso do Solo',fontsize=14)
    ax.set_ylabel('Área (ha)',fontsize=14)
    ax.set_title('Uso do Solo - 1985 vs 2023',fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(codigos, rotation=0)
    
    # Remover grid
    ax.grid(False)
    
    # Legenda com cores + descrições
    from matplotlib.patches import Patch
    handles = [
        Patch(color='steelblue', alpha=0.6, label='1985'),
        Patch(color='orange', alpha=0.6, label='2023')
    ]
    ax.legend(handles=handles, title='Ano', loc='upper right')
    
    # Adicionar descrição dos códigos em anotações laterais (opcional)
    for i, (codigo, desc) in enumerate(zip(codigos, descricao_legenda)):
        ax.text(x[i], ax.get_ylim()[0]*1.2, f'{desc}', rotation=90,
                ha='center', va='bottom', fontsize=14, color='gray')
    
    plt.tight_layout()
    plt.show()
    fig.savefig(os.path.join(repoPath, 'outputs','usodosolocomparação.png'))
        
    dfAtual['variacao_percentual'] = 100 * (dfAtual['area_ha_2023'] - dfAtual['area_ha_1985']) / dfAtual['area_ha_1985'].replace(0, np.nan)


##############################
