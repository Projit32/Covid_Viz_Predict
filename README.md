# Covid-19 India Visualization and Prediction
This is a Visialization that was created as a submission to the [FLATTENING THE CURVE: COVID-19 DATA CHALLENGE](https://cgdv.github.io/challenges/COVID-19/?fbclid=IwAR1Kuy0orhoGu2I2rXPODXSqVQvb86Ioa0CMH7AR0PEtjCI4_FzfkEDLFJ0).

We generate the visualizations using Tableau, which you can be accessed from [here](https://public.tableau.com/shared/7XCMTG2Q3?:display_count=y&:origin=viz_share_link&:embed=y), for the following :

1. Tree Map of Overall Confirmed, Decesed and Recovered Cases in India **(Till May 1, 2020).**

![Total Cases](Images/Cumulative%20COVID-19%20Cases%20in%20India.png)

2. Line chart for Daily nuber of Cases and Bar chart for the cumulative cases in a particular state and the comparison of positive cases vs the wellenss factor of that state **(Till May 1, 2020).**

![Daily Report](Images/Daily%20COVID-19%20report.png)

3. Weekly rolling average of confirmed Cases and average of changes in confirmed cases. **(Till May 1, 2020).**

![Weekly Report](Images/Weekly%20rolling%20average.png)

4. Future predictions for the next 7 days **(From May 2, 2020 and onwards)**.

![Predictions](Images/COVID-19%20Prediction.png)

For this purpose, we collected data, using Pyhton, from [Crowdsourced database for COVID-19](https://api.covid19india.org/) and formatted in such a way that it can be used in Tableau to generate visualizations. Entire formatted data has been saved as excel file in ```Output``` folder.

Purpose of the ```daily.py``` file was to calculate the following:
- State-wise daily & cumulative cases for Confirmed, Recovered and Deceased cases. (API doesnt provides cumulative\/total number of cases)

- Daily wellness Factor of individual states:
> Wellness = Recovered - Confirmed - Death 

- Cumulative and daily tests conducted and the positive detections of individual states. (API only provides cumulative)

- Wellness vs Positives of individual states.

- Rolling averages of daily cases and Changes in daily cases

We've created some basic visualization using ```Matplotlib``` to verify certain results:
1. The Cumulative Cases in India (Viz only shows the confirm cases but all others like recovered and deceased are there in the file).
![Cumulative Cases](Images/Figure%202020-05-01%20080000.png)
2. Rolling average of daily confirmed cases. [Read more on Rolling Averages.](https://www.portent.com/blog/analytics/rolling-averages-math-moron.htm)
![Daily Rolling Averages](Images/Figure%202020-04-29%20153127.png)
3. Rolling average of changes in  confimed cases.
![Changes in daily cases Rolling avegrage](Images/Figure%202020-04-29%20153116.png)

Purpose of ```rnn_covid_daily.py``` file:

This is a Recurrent Neural Network that was build using [LSTM](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM) from [Tensorflow 2.1.0 - Keras](https://www.tensorflow.org/guide/keras) to predict the possible number of daily cases in the next 7 days. For this, we used the past data and converted into the format that the official site suggest ```[batch, timesteps, feature]```. For us, that becomes a matrix of  ```rows x 3 x 1``` where the row referes to the data availave - timestamp.

Results: 

1. Training
![Training](Images/Figure%202020-04-30%20233817.png)

2.Testing
![Testing](Images/Figure%202020-04-30%20233720.png)

3. Training the test set to get the compelte trained model
![After Training the test set](Images/Figure%202020-05-02%20111856.png)

4. Predicting the future
![Future Predictions](Images/Figure%202020-04-30%20233714.png)

Purpose of ```rnn_covid_cumulative.py``` file:

This is a Recurrent Neural Network that was build using [LSTM](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM) from [Tensorflow 2.1.0 - Keras](https://www.tensorflow.org/guide/keras) to predict the possible number of overall cases in the next 7 days.

Results: 

1. Training
![Training](Images/Figure%202020-04-30%20232011.png)

2.Testing
![Testing](Images/Figure%202020-04-30%20232007.png)

3. Training the test set to get the compelte trained model
![After Training the test set](Images/Figure%202020-05-02%20103659.png)

4. Predicting the future
![Future Predictions](Images/Figure%202020-05-01%20082123.png)
