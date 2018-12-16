# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 13:56:53 2018

@author: ylb10119
"""
import pandas as pd
import pulp
import matplotlib.pyplot as plt
from dataprocess import dataFormat

def esRenewable(esCap, demand):

    disE = 0.85 #example battery efficiencies
    chaE = 0.85
    flow = demand['Power']
    idsA = flow.where(flow > 0)
    idsB = flow.where(flow < 0)
    above = idsA.dropna()
    below = idsB.dropna()
    aboveIds = above.index
    belowIds = below.index

 
    charge = pulp.LpVariable.dicts("charge", 
                               ((Idx,1) for Idx in demand.index), 
                               lowBound=0,
                               upBound=esCap)

    discharge = pulp.LpVariable.dicts("discharge", 
                            ((Idx,1) for Idx in demand.index), 
                            lowBound=-esCap,
                            upBound=0)

    state = pulp.LpVariable.dicts("state", 
                        ((Idx,1) for Idx in demand.index), 
                        lowBound=esCap*0.2,
                        upBound=esCap*0.9)


                          
    model = pulp.LpProblem("Battery scheduling problem", pulp.LpMinimize) 


    hours=demand.index
    for Idx in hours:
        if Idx == 1:
            model += state[(Idx,1)] - (esCap*0.6) - ((charge[(Idx,1)]) * chaE) - ((discharge[(Idx,1)]) * (1/disE))== 0
            model += (charge[(Idx,1)]) + (esCap*0.6) <= ((esCap*0.9) / chaE)
            model += (esCap*0.6) + discharge[(Idx,1)] >= ((esCap*0.2) * disE)
        elif Idx > 1:
            model += state[(Idx,1)] - state[((Idx-1),1)] - ((charge[(Idx,1)]) * chaE) - ((discharge[(Idx,1)]) * (1/disE)) == 0
            model += ((charge[(Idx,1)])) + state[((Idx-1),1)] <= ((esCap*0.9) / chaE)
            model += state[((Idx-1),1)] + discharge[(Idx,1)]  >= ((esCap*0.2) * disE)

    for Idx in hours:
        if flow[Idx] < flow.mean(0):
            model += discharge[Idx,1] == 0
        elif flow[Idx] > flow.mean(0):
            model += charge[Idx,1] == 0

    model += state[Idx,1] == esCap*0.6

    for Idx in hours:
        model += charge[Idx,1] >= 0
        model += discharge[Idx,1] <= 0 

    for Idx in demand.index:
        model += state[Idx,1] <= esCap*0.9
        model += state[Idx,1] >= esCap*0.2

    for Idx in belowIds:
        model += charge[Idx,1] + (demand.loc[Idx]) <= flow.mean(0) 
        model += charge[Idx,1] >=0

    for Idx in aboveIds:
        model += discharge[Idx,1] + (demand.loc[Idx]) >= flow.mean(0)
        model += discharge[Idx,1] <=0
 
#    mP=flow.max()
#    mP2=flow.where(flow==mP)
#    mP3=mP2.dropna()
#    idMax=mP3.index
    
    
    idsA = flow.where(flow > flow.mean(0))
    above = idsA.dropna()
    ordered=demand.sort_values(by='Power')
    times=ordered.index
    maxFlow=times[(len(flow)-int((len(above)/3))):len(flow)]
    #maxFlow=times[(len(flow)-int((len(above)))):len(flow)]

        
    # Objective Function
    model +=  pulp.lpSum(demand.loc[Idx] + discharge[Idx,1] for Idx in maxFlow) + (pulp.lpSum((charge[Idx,1] + discharge[Idx,1] + demand.loc[Idx]) - flow.mean(0)  for Idx in aboveIds)/len(aboveIds)) 
    
    model.solve()

    chg = [ charge[Idx,1].varValue for Idx in hours ]
    dischg = [ discharge[Idx,1].varValue for Idx in hours ]
    ste = [ state[Idx,1].varValue for Idx in hours ]

    f=pd.Series(demand['Power'], demand.index)
    c=pd.Series(chg, demand.index)
    d=pd.Series(dischg, demand.index)
    newDemand=pd.Series(f+c+d, demand.index)


    plt.plot(demand['Power'], label='Original Demand') 
    plt.plot(newDemand, label='New Demand')
    plt.show()

    figure = plt.figure()
    plt.plot(ste)
    plt.show()
       
    return f, newDemand, maxFlow, c, d
    
if __name__ == '__main__':
    demandProxy = dataFormat()
    demandProxy[((24*day)-24):(24*day)]
    esCap = 60
    
    f, newDemand, maxFlow, c, d = esRenewable(esCap, demand)                
