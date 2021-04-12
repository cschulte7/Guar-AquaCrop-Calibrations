# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['list_data', 'get_filepath', 'get_data', 'prepare_weather', 'AquaCropModel']

# Cell
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import os
import pandas as pd
import sys
[sys.path.append(i) for i in ['.', '..']]

# Cell
from .initialize import *
from .timestep import *
from .classes import *
from aquacrop import data

# Cell
def list_data():
    """
    lists all built-in data files
    """
    path=data.__path__[0]

    return os.listdir(path)

# Cell
def get_filepath(filename):
    """
    get selected data file
    """
    filepath = os.path.join(data.__path__[0],filename)

    return filepath


# Cell
def get_data(filename, **kwargs):
    """
    get selected data file
    """
    filepath = os.path.join(data.__path__[0],filename)

    return np.genfromtxt(filepath,**kwargs)

# Cell
def prepare_weather(weatherFilePath):
    """
    function to read in weather data and return a dataframe containing
    the weather data
    *Arguments:*\n
    `FileLocations` : `FileLocationsClass`:  input File Locations
    `weatherFilePath` : `str` :  file location of weather data
    *Returns:*
    `weather_df`: `pandas.DataFrame` :  weather data for simulation period
    """


    weather_df = pd.read_csv(weatherFilePath,header=0,delim_whitespace=True)

    assert len(weather_df.columns) == 7

    # rename the columns
    weather_df.columns = str("Day Month Year MinTemp MaxTemp Precipitation ReferenceET").split()

    # put the weather dates into datetime format
    weather_df["Date"] = pd.to_datetime(weather_df[['Year','Month','Day']])

    # drop the day month year columns
    weather_df = weather_df.drop(["Day","Month","Year"],axis=1)

    # set limit on ET0 to avoid divide by zero errors
    weather_df.ReferenceET.clip(lower=0.1,inplace=True)


    return weather_df

# Cell
class AquaCropModel:

    def __init__(self,SimStartTime,SimEndTime,wdf,Soil,Crop,InitWC,
                     IrrMngt=None,FieldMngt=None,FallowFieldMngt=None,
                     Groundwater=None,planting_dates=None,
                     harvest_dates=None,CO2conc=None):

        self.SimStartTime = SimStartTime
        self.SimEndTime = SimEndTime
        self.wdf = wdf
        self.Soil = Soil
        self.Crop = Crop
        self.InitWC = InitWC
        self.planting_dates = planting_dates
        self.harvest_dates = harvest_dates
        self.CO2conc = CO2conc

        self.IrrMngt = IrrMngt
        self.FieldMngt = FieldMngt
        self.FallowFieldMngt = FallowFieldMngt
        self.Groundwater = Groundwater

        if IrrMngt == None:  self.IrrMngt = IrrMngtClass(IrrMethod=0);
        if FieldMngt == None:  self.FieldMngt = FieldMngtClass();
        if FallowFieldMngt == None:  self.FallowFieldMngt = FieldMngtClass();
        if Groundwater == None:  self.Groundwater = GwClass();
        #if InitWC == None:  self.InitWC = InitWCClass();




    def initialize(self,):
        """
        Initialize variables
        """

        # define model runtime
        self.ClockStruct = read_clock_paramaters(self.SimStartTime,self.SimEndTime)

        # get weather data
        self.weather_df = read_weather_inputs(self.ClockStruct,self.wdf)

        # read model params
        self.ClockStruct, self.ParamStruct = read_model_parameters(self.ClockStruct,self.Soil,
                                                                   self.Crop,self.weather_df)

        # read irrigation management
        self.ParamStruct = read_irrigation_management(self.ParamStruct,self.IrrMngt,self.ClockStruct)

        # read field management
        self.ParamStruct = read_field_management(self.ParamStruct,self.FieldMngt,self.FallowFieldMngt)

        # read groundwater table
        self.ParamStruct = read_groundwater_table(self.ParamStruct,self.Groundwater,self.ClockStruct)

        # Compute additional variables
        self.ParamStruct.CO2concAdj = self.CO2conc
        self.ParamStruct = compute_variables(self.ParamStruct,self.weather_df,self.ClockStruct)

        # read, calculate inital conditions
        self.ParamStruct, self.InitCond = read_model_initial_conditions(self.ParamStruct,self.ClockStruct,self.InitWC)

        self.ParamStruct = create_soil_profile(self.ParamStruct)

        #self.InitCond.ParamStruct = self.ParamStruct

        Outputs = OutputClass()
        Outputs.Water = np.zeros((len(self.ClockStruct.TimeSpan),3+len(self.InitCond.th)))
        Outputs.Flux = np.zeros((len(self.ClockStruct.TimeSpan),16))
        Outputs.Growth = np.zeros((len(self.ClockStruct.TimeSpan),13))
        Outputs.Final = pd.DataFrame(columns = ['Season','Crop Type','Harvest Date (YYYY/MM/DD)',
                                                'Harvest Date (Step)','Yield (tonne/ha)',
                                                'Seasonal irrigation (mm)'])


        self.Outputs=Outputs

         # save model weather to InitCond
        self.weather = self.weather_df.values

        #return self.ClockStruct,self.InitCond,self.Outputs
        return


    def step(self,num_steps=1,till_termination=False):

        if till_termination==True:

            while self.ClockStruct.ModelTermination == False:

                self.ClockStruct,self.InitCond,self.ParamStruct,self.Outputs = self.perform_timestep()
        else:

            for i in range(num_steps):

                self.ClockStruct,self.InitCond,self.ParamStruct,self.Outputs = self.perform_timestep()

                if self.ClockStruct.ModelTermination: return

        #return self.ClockStruct,self.InitCond,self.Outputs
        return


    def perform_timestep(self):

        """
        Function to run a single time-step (day) calculation of AquaCrop-OS
        """


        # extract weather data for current timestep
        #weather_step = weather_df[weather_df.Date==ClockStruct.StepStartTime]
        weather_step = self.weather[self.ClockStruct.TimeStepCounter]

        #%% Get model solution %%
        NewCond,ParamStruct,Outputs = solution(self.InitCond,self.ParamStruct,self.ClockStruct,weather_step,self.Outputs)

        #%% Check model termination %%
        ClockStruct = check_model_termination(self.ClockStruct,NewCond)

        #%% Update time step %%
        ClockStruct,InitCond,ParamStruct,Outputs = update_time(ClockStruct,NewCond,ParamStruct,Outputs,self.weather)

        return ClockStruct,InitCond,ParamStruct,Outputs