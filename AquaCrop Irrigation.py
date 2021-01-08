# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 12:56:25 2020

@author: carol
"""

#export
import sys
_=[sys.path.append(i) for i in ['.', '..']]


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from aquacrop.core import *
from aquacrop.classes import *

# No Irrigation
wdf = prepare_weather(get_filepath('champion_weather.txt'))
soil = SoilClass('Loam')
crop = CropClass('Maize',PlantingDate='05/01',HarvestDate='10/30')
model = AquaCropModel('2000/05/01','2018/10/31',wdf,soil,crop)
model.initialize()
model.step(till_termination=True)
final_rainfed = model.Outputs.Final
final_rainfed.plot(x="HarvestDate",y="Yield")

# set constant soil moisture target of 50% total available water
# irrigation method 1 - soil moisture thresholds
irrmngt = IrrMngtClass(IrrMethod=1,SMT=[50]*4) # 4 growth stages / thresholds have 50% of total water. They irrigate as soon as the soil moisture gets down to 50% 
model = AquaCropModel('2000/05/01','2018/10/31',wdf,
                      soil,crop,IrrMngt=irrmngt)

model.initialize()
model.step(till_termination=True)
final_irr = model.Outputs.Final

fig,ax=plt.subplots()
final_irr.plot(x="HarvestDate",y="Yield",label="Irr",legend=True,ax=ax)
final_rainfed.plot(x="HarvestDate",y="Yield",label="rainfed",legend=True,ax=ax)
final_irr

print(final_irr)
