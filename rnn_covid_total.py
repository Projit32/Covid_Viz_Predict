# -*- coding: utf-8 -*-


import tensorflow as tf

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime

# Importing the training set
dataset = pd.read_excel('Rolling Averages.xlsx')

total_set =dataset.iloc[:,5:6].values
print(total_set,total_set.shape)

test_size=7
window= 3 # Number of Timestamps

train_dates=dataset['Date'].iloc[:-test_size]
train_dates=[date.date()+datetime.timedelta(days=window) for date in train_dates]
test_dates=dataset['Date'].iloc[-test_size:]
test_dates=[date.date()+datetime.timedelta(days=window) for date in test_dates]
last_day = dataset['Date'].iloc[-1].date()

training_set=total_set[:-test_size]
testing_set=total_set[-test_size:]
print("train=", training_set.shape)
print("test=", testing_set.shape)

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))
training_set_scaled =sc.fit_transform(training_set)
testing_set_scaled =sc.transform(testing_set)
print(training_set_scaled.shape)
print(testing_set_scaled.shape)

X_train = []
y_train = []
for i in range(window, len(training_set)):
    X_train.append(training_set_scaled[i-window:i, 0])
    y_train.append(training_set_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)

# Reshaping
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model

regressor = Sequential()

# Adding the first LSTM layer and some Dropout regularisation
regressor.add(LSTM(units = 250, return_sequences = True, input_shape = (X_train.shape[1], X_train.shape[2])))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 250, return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 250, return_sequences = False))
regressor.add(Dropout(0.2))

# Adding the output layer
regressor.add(Dense(units = 1))
regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

mc = ModelCheckpoint('Model/best_model_cumulative_v1.h5', monitor='loss', mode='min', verbose=1, save_best_only=True)

regressor.fit(X_train, y_train, epochs = 150,  batch_size = 4, callbacks=[mc])

regressor=load_model('Model/best_model_cumulative_v1.h5')

X_test = []
y_test=[]
y_test_unscaled=[]
for i in range(window,len(testing_set_scaled)):
    X_test.append(testing_set_scaled[i-window:i, 0])
    y_test.append(testing_set_scaled[i, 0])
    y_test_unscaled.append(testing_set[i, 0])
X_test , y_test = np.array(X_test), np.array(y_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

print(X_test.shape)

y_pred = regressor.predict(X_test)
y_pred = sc.inverse_transform(y_pred)
print(y_pred.shape)

y_pred_train = regressor.predict(X_train)
y_pred_train = sc.inverse_transform(y_pred_train)
print(y_pred_train.shape)

train_y=y_train.reshape(-1,1)
train_y=sc.inverse_transform(train_y)


# Visualising the train results
plt.rcParams['figure.figsize']= 20,10

plt.plot(train_y, color = 'red', label = 'Real Total cases')
plt.plot(y_pred_train, color = 'blue', label = 'Predicted Total cases')
plt.title('Total Cases Trend Training')
plt.xticks(list(range(0,len(y_pred_train))), train_dates, rotation='vertical')
plt.xlabel('Date')
plt.ylabel('No. of Cases')
plt.legend()
plt.show()

# Visualising the test results
plt.plot(y_test_unscaled, color = 'red', label = 'Real Total cases')
plt.plot(y_pred, color = 'blue', label = 'Predicted Total cases')
plt.title('Total Cases Trend Testing')
plt.xticks(list(range(0,len(y_pred))), test_dates, rotation='vertical')
plt.xlabel('Date')
plt.ylabel('No. of Cases')
plt.legend()
plt.show()

# training of the Test set to make future predictions
regressor=load_model('Model/best_model_cumulative_v1.h5')
new_mc = ModelCheckpoint('best_model_cumulative_v2.h5', monitor='loss', mode='min', verbose=1, save_best_only=True)
regressor.fit(X_test, y_test, epochs = 500,  batch_size = 4, callbacks=[new_mc])
regressor=load_model('Model/best_model_cumulative_v2.h5')

y_pred_new = regressor.predict(X_test)
y_pred_new = sc.inverse_transform(y_pred_new)
print(y_pred_new.shape)

# Visualising the test results after training 
plt.plot(y_test_unscaled, color = 'red', label = 'Real Total cases')
plt.plot(y_pred_new, color = 'green', label = 'Predicted Total cases')
plt.title('Total Cases Trend Testing After Training')
plt.xticks(list(range(0,len(y_pred))), test_dates, rotation='vertical')
plt.xlabel('Date')
plt.ylabel('No. of Cases')
plt.legend()
plt.show()

# Predctions
predict_for=X_test[-1]

predictions=list()
dates=list()
for i in range(7):
    test=np.reshape(predict_for, (1,predict_for.shape[0],predict_for.shape[1]))
    test=regressor.predict(test)
    dates.append(last_day+datetime.timedelta(days=i+1))
    predictions.append(sc.inverse_transform(test)[0])
    predict_for=np.array([predict_for[1],predict_for[2],test[0]])

predictions=np.array(predictions)

# Visualising the results
plt.plot(predictions, color = 'blue', label = 'Predicted Total cases')
plt.xticks(list(range(len(predictions))),dates,rotation='vertical')
plt.title('Cases Total Future')
plt.xlabel('Date')
plt.ylabel('No. of Cases')
plt.legend()
plt.show()

import pandas as pd
future_predictions= pd.DataFrame(np.append(np.array(dates).reshape(-1,1),predictions, axis=1))
future_predictions.columns=['Date','Predictions']


future_predictions.to_excel("Future Cumulative Predictions.xlsx", index=False)
