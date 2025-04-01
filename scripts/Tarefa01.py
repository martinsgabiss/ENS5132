# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 16:02:08 2025

@author: jrmjr
"""

import numpy as np

#Crie uma matriz com números aleatórios com duas dimensões (2D) com 100 linhas e 100 colunas.
matA = np.random.rand(100,100)

#Determine o valor da última linha e coluna
print(matA[99,99])

#Recorte a primeira linha e liste os valores
matB = matA[0,:]

print(matB)


