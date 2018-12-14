# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 13:38:06 2018

@author: ylb10119
"""

import pandas as pd
import pulp
import matplotlib.pyplot as plt


day=200
idReal=list(range(1,25))
demandProxy = pd.DataFrame.from_csv('gsp_demand.csv')
demand=demandProxy[((day*24)- 24):(day*24)]
demand.index = [idReal]
demand.columns=['Vol (MW)']
esCap = 20
disE = 0.9 #example battery efficiencies
chaE = 0.9

#demand = pd.DataFrame.from_csv('gsp_demand.csv', index_col=['Idx'])

flow = demand['Vol (MW)']
idsA = flow.where(flow > flow.mean(0))
idsB = flow.where(flow < flow.mean(0))
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
    model += charge[Idx,1] + (demand.loc[Idx]/ chaE) <= flow.mean(0) 
    model += charge[Idx,1] >=0

for Idx in aboveIds:
    model += discharge[Idx,1] + (demand.loc[Idx]* disE) >= flow.mean(0)
    model += discharge[Idx,1] <=0
        

model += pulp.lpSum((charge[Idx,1] + discharge[Idx,1] + demand.loc[Idx]) - flow.mean(0) for Idx in aboveIds)/len(aboveIds)

#pulp.lpSum(flow.mean(0) - (charge[Idx,1] + discharge[Idx,1] + demand.loc[Idx]) for Idx in belowIds)/len(belowIds) +

model.solve()

chg = [ charge[Idx,1].varValue for Idx in hours ]
dischg = [ discharge[Idx,1].varValue for Idx in hours ]
ste = [ state[Idx,1].varValue for Idx in hours ]

f=pd.Series(demand['Vol (MW)'], demand.index)
c=pd.Series(chg, demand.index)
d=pd.Series(dischg, demand.index)
newDemand=pd.Series(f+c+d, demand.index)


plt.plot(demand['Vol (MW)'], label='Original Demand') 
plt.plot(newDemand, label='New Demand')
plt.show()

figure = plt.figure()
plt.plot(ste)
plt.show()