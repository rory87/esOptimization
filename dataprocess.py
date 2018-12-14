import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def dataFormat():
    demandProxy = pd.DataFrame.from_csv('gsp_demand.csv')
    daily = np.linspace(1,24,24) # create an array of hourse from 1 to 24
    hours = np.zeros(8784)
    hours = hours.astype(int)

    for i in range(1,367):
        hours[ ((24*i)-24) : (24*i)] = daily

    demand = demandProxy
    demand.index = hours
    demand.set_axis(['Power'], axis='columns', inplace=True)

    return demand
