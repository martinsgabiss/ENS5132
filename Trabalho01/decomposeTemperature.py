# -*- coding: utf-8 -*-
"""
Created on Sat May  3 11:52:12 2025

@author: jrmjr
"""
import numpy as np
import matplotlib.pyplot as plt
import pymannkendall as mk
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
from temperatureFigures import normalityCheckTemperature, trendFigureSingleTemperature, trendForAllColumns
from datetime import datetime


#Decomposição

def timeSeriesDecompose(aqFiltrado,repoPath, cols=['TBS', 'TMax', 'TMin']):
    
    # Decomposição da série temporal
    for col in cols:
      
        dataDecompose = aqFiltrado[[col,'datetime']]
        #dataDecompose = dataDecompose.set_index('datetime')
        dataDecomposeMonthly = dataDecompose.groupby(pd.PeriodIndex( 
            dataDecompose['datetime'], freq="M"))[col].mean()
        
        # Formata o dataframe para funcionar na função seasonal_decompose do statsmodel
        dataDecomposeMonthly = pd.Series(np.array(dataDecomposeMonthly),
                                         index = pd.PeriodIndex(dataDecomposeMonthly.index))
    
        # Gerando um PeriodIndex completo no intervalo desejado
        full_index = pd.period_range(start=dataDecomposeMonthly.index.min(), 
                                     end=dataDecomposeMonthly.index.max(), freq='M')
    
        # Reindexando para preencher os períodos faltantes com NaN
        complete_data = dataDecomposeMonthly.reindex(full_index)
        
        # Interpolando dados que possuem nan
        complete_data = complete_data.interpolate().dropna()
        complete_data.index = complete_data.index.to_timestamp()
        # Decompondo a série repetição em 12 meses
        res = seasonal_decompose(complete_data,period=12) 
        
        # Gerando figura
        fig, axes = plt.subplots(ncols=1, nrows=4, sharex=True)
        res.observed.plot(ax=axes[0], legend=False,color='blue')
        axes[0].set_ylabel('Observed')
        res.trend.plot(ax=axes[1], legend=False, color='red')
        axes[1].set_ylabel('Trend')
        res.seasonal.plot(ax=axes[2], legend=False, color='yellow')
        axes[2].set_ylabel('Seasonal')
        res.resid.plot(ax=axes[3], legend=False, color='gray')
        axes[3].set_ylabel('Residual')
        fig.savefig(repoPath+'/figuras/'+'/decompose_'+'_'+col+'.png')
        
        return res,complete_data

