# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 11:30:54 2020

@author: carol
"""

#export
#https://colab.research.google.com/github/thomasdkelly/aquacrop/blob/master/tutorials/01_basics.ipynb#scrollTo=nXAX0rIvC3uT
#https://colab.research.google.com/github/thomasdkelly/aquacrop/blob/master/tutorials/02_irrigation.ipynb

import sys
_=[sys.path.append(i) for i in ['.', '..']] # finds 'AquaCrop' file

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from aquacrop.core_Guar import *
from aquacrop.classes_Guar import *

wdf = prepare_weather(get_filepath('champion_weather.txt'))
print(wdf)
soil = SoilClass('Loam')
crop = CropClass('Maize',PlantingDate='05/01',HarvestDate='10/30')
model = AquaCropModel('2000/05/01','2018/10/31',wdf,soil,crop)
model.initialize()

print(wdf.Date.iloc[0])


model.step(till_termination=True)
final = model.Outputs.Final; final
final.Yield.plot()
print(final)
plt.xlabel('Season') # seaons is the same as year. 2000 = 0, 2001 = 1, etc
plt.ylabel('Yield')

# list_data()