# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 11:34:49 2020

@author: proji
"""
import requests
import pandas as pd
import numpy as np
import io
import datetime

url = 'https://api.covid19india.org/states_daily.json'
data=requests.get(url).json()

data=data['states_daily']

state_code=['AN', 'AP', 'AR', 'AS', 'BR', 'CH', 'CT', 'DN', 'DD', 'DL', 'GA',
       'GJ', 'HR', 'HP', 'JK', 'JH', 'KA', 'LA', 'KL', 'LD', 'MP', 'MH',
       'MN', 'ML', 'MZ', 'NL', 'OR', 'PY', 'PB', 'RJ', 'SK', 'TN', 'TG',
       'TR', 'UP', 'UT', 'WB']
state_names=['Andaman and Nicobar Islands', 'Andhra Pradesh',
       'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh',
       'Chhattisgarh', 'Dadra and Nagar Haveli', 'Daman and Diu', 'Delhi',
       'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
       'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Ladakh', 'Kerala',
       'Lakshadweep', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
       'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Puducherry',
       'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
       'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']

names=dict()
codes=dict()

for i in range(len(state_names)):
    codes[state_names[i].upper()]=state_code[i].upper()
    names[state_code[i].upper()]=state_names[i].upper()
    
# Daily
daily=list()
daily_tt=list()
for record in data:
    date=record['date']
    date = datetime.datetime.strptime(date, "%d-%b-%y").date()
    status=record['status']
    for key in record.keys():
        if key not in ['date','status','tt']:
            daily.append([date,status,key.upper(),names[key.upper()],record[key]])
        elif key == 'tt':
            daily_tt.append([date,status,record[key]])

daily=pd.DataFrame(daily)
tt_daily=pd.DataFrame(daily_tt)
daily.columns=['Date','Status','Code','State','Cases']
tt_daily.columns=['Date', 'Status', 'Cases']
daily=daily.replace(to_replace="", value =0)
daily['Cases']=pd.to_numeric(daily['Cases'])
tt_daily['Cases']=pd.to_numeric(tt_daily['Cases'])


# Contribution
confirmed_data=daily[daily['Status']=='Confirmed'].reset_index()
recovered_data=daily[daily['Status']=='Recovered'].reset_index()
deceased_data=daily[daily['Status']=='Deceased'].reset_index()

contribution= recovered_data['Cases']-(confirmed_data['Cases']+deceased_data['Cases'])

contrib_list=list()
for i in range(len(contribution)):
    date=confirmed_data.Date.iloc[i]
    code=confirmed_data.Code.iloc[i]
    state=names[code.upper()]
    contrib_list.append([date,code,state,confirmed_data.Cases.iloc[i],recovered_data.Cases.iloc[i],deceased_data.Cases.iloc[i],contribution[i]])
    
contribution_daily=pd.DataFrame(contrib_list)
contribution_daily.columns=['Date','Code','State','Confirmed','Recovered','Deaths','Contribution']


# Testing
url = 'https://api.covid19india.org/state_test_data.json'
data=requests.get(url).json()
data=data['states_tested_data']

testing=list()

for row in data:
    if row['totaltested'] != '':
        date=row['updatedon'].split('/')
        date=datetime.date(int(date[2]), int(date[1]), int(date[0]))
        impact=contribution_daily['Contribution'][(contribution_daily['State']==row['state'].upper()) & (contribution_daily['Date']==date)]
        impact=impact.values
        if len(impact)!=0:
            impact=impact[0]
            testing.append([date,row['state'].upper(),codes[row['state'].upper()],row['totaltested'],impact])


testing=pd.DataFrame(testing)
testing.columns=['Date','State','Code','Tests','Wellness']

# Total
url = "https://api.covid19india.org/csv/latest/state_wise.csv"
s = requests.get(url).content
total = pd.read_csv(io.StringIO(s.decode('utf-8'))).iloc[1:,0:5]
total['Code']=total['State']
# Putting State Codes
for i in range(len(total)):
    total['Code'].iloc[i]=codes[total['Code'].iloc[i].upper()]

cnf_total=total[['State','Confirmed','Code']]
cnf_total['Status']=['Confirmed']*len(cnf_total)
rcv_total=total[['State','Recovered','Code']]
rcv_total['Status']=['Recovered']*len(rcv_total)
dth_total=total[['State','Deaths','Code']]
dth_total['Status']=['Deaths']*len(dth_total)
cnf_total.columns=rcv_total.columns=dth_total.columns=['State','Code','Cases','Status']
total=pd.concat([cnf_total,rcv_total,dth_total])


# Rolling Average
previous=0

daily_confirmed= tt_daily[tt_daily['Status']=='Confirmed'].reset_index()
daily_confirmed['Cases_Delta']=daily_confirmed['Cases']
daily_confirmed['Cumulative']=daily_confirmed['Cases']


# Finding Cumulative
for i in range(1,len(daily_confirmed)):
    daily_confirmed['Cumulative'].iloc[i]=np.sum(daily_confirmed[0:(i+1)]['Cases'].values)
    
# Finding Deltas
for row in daily_confirmed.index:
    daily_confirmed['Cases_Delta'].iloc[row]=daily_confirmed['Cases'].iloc[row]-previous
    previous=daily_confirmed['Cases'].iloc[row]

daily_confirmed['Cases_Avg']=[0]*len(daily_confirmed)
daily_confirmed['Cases_Delta_Avg']=[0]*len(daily_confirmed)

# Finding Rolling Avgs
for i in range(6,len(daily_confirmed)):
    daily_confirmed['Cases_Avg'].iloc[i]=np.mean(daily_confirmed[i-6:i+1]['Cases'].values)
    daily_confirmed['Cases_Delta_Avg'].iloc[i]=np.mean(daily_confirmed[i-6:i+1]['Cases_Delta'].values)

import matplotlib.pyplot as plt
plt.rcParams['figure.figsize']= 20,10

plt.plot(daily_confirmed['Cases_Avg'].values,marker='o')
plt.xticks(list(range(len(daily_confirmed))),daily_confirmed['Date'].values,rotation='vertical')
plt.title('Daily Cases Rolling Averages')
plt.xlabel('Date')
plt.ylabel('Rolling Avg')
plt.show()

plt.plot(daily_confirmed['Cases_Delta_Avg'].values, c='Red', marker='o')
plt.xticks(list(range(len(daily_confirmed))),daily_confirmed['Date'].values,rotation='vertical')
plt.title('Changes in Daily Cases Rolling Averages')
plt.xlabel('Date')
plt.ylabel('Rolling Avg')
plt.show()

plt.plot(daily_confirmed['Cumulative'].values, c='Green', marker='o')
plt.xticks(list(range(len(daily_confirmed))),daily_confirmed['Date'].values,rotation='vertical')
plt.title('Cumulative Cases')
plt.xlabel('Date')
plt.ylabel('Rolling Avg')
plt.show()

# Daily Cumulative
# Confirmed
state_cumulative=pd.DataFrame()
for state in state_code:
    state_data=confirmed_data[confirmed_data['Code']==state]
    temp=0
    state_data['Cumulative']=confirmed_data['Cases']
    for i in range(len(state_data)):
        temp+=state_data['Cases'].iloc[i]
        state_data['Cumulative'].iloc[i]=temp
    state_cumulative=pd.concat([state_cumulative,state_data])

# Recovered
for state in state_code:
    state_data=recovered_data[recovered_data['Code']==state]
    temp=0
    state_data['Cumulative']=recovered_data['Cases']
    for i in range(len(state_data)):
        temp+=state_data['Cases'].iloc[i]
        state_data['Cumulative'].iloc[i]=temp
    state_cumulative=pd.concat([state_cumulative,state_data])

# Deceased
for state in state_code:
    state_data=deceased_data[deceased_data['Code']==state]
    temp=0
    state_data['Cumulative']=deceased_data['Cases']
    for i in range(len(state_data)):
        temp+=state_data['Cases'].iloc[i]
        state_data['Cumulative'].iloc[i]=temp
    state_cumulative=pd.concat([state_cumulative,state_data])
        



# Saving Files
daily.to_excel('Daily Formatted.xlsx', index=False)
contribution_daily.to_excel('Contribution.xlsx', index=False)
testing.to_excel('Test Report.xlsx', index=False)
total.to_excel("Total Data.xlsx",index=False)
daily_confirmed.to_excel('Rolling Averages.xlsx', index=False)
state_cumulative.to_excel('Statewise Cumulative.xlsx', index=False)

