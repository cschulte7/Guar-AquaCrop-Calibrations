# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 12:52:42 2020

@author: carol
"""
import sys
_=[sys.path.append(i) for i in ['.', '..']] # finds 'AquaCrop' file

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from aquacrop.core import *
from aquacrop.classes import *

# Define Weather
wdf = prepare_weather(get_filepath('champion_weather.txt'))
wdf.head()


# Custom Soil Class
soil = SoilClass('custom',dz=[0.1]*8+[0.2]*4)
soil.add_layer(thickness=0.8,thWP=0.1,thFC=0.45,thS=0.55,Ksat=500,penetrability=100) # add layer using hydraulic proeprties
soil.add_layer_from_texture(thickness=0.8,Sand=30,Clay=30,OrgMat=2.5,penetrability=100) # add layer using texture proeprties
soil.profile
print(soil.profile)

# Adding a second crop with different dates
crop = CropClass('Maize',PlantingDate="05/15",HarvestDate="11/15")
crop2 = CropClass('Maize',PlantingDate="04/15",HarvestDate="10/15")
crop.PlantingDate, crop2.PlantingDate

#crop.__dict__
def run_model(crop):
    model = AquaCropModel('1990/01/01','2001/11/30',wdf,soil,crop)
    model.initialize()
    model.step(till_termination=True)
    return model.Outputs.Final
final = run_model(crop)
final2= run_model(crop2)
final.Yield.plot(label="May 15th",legend=True)
final2.Yield.plot(label="April 15th",legend=True)

plt.xlabel('Season')
plt.ylabel('Yield')

print(final)
print(final2)

