# Stock Oracle Group
# 4/9/2025
# File for the predictor function
import datetime
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_tomorrow(graph_instance):
    # Ensure the graph data is loaded
    if not graph_instance.data:
        graph_instance.read_csv()

    # Create a DataFrame
    data = pd.DataFrame(graph_instance.data, columns=['Date', 'Value'])
    data['Date'] = pd.to_datetime(data['Date'])
    data['Date_ordinal'] = data['Date'].map(datetime.datetime.toordinal)

    # Train the linear regression model using all historical data
    x = data[['Date_ordinal']]
    y = data['Value']
    model = LinearRegression()
    model.fit(x, y)

    # Predict tomorrow's value based on the model
    last_date = data['Date'].max()
    tomorrow = last_date + pd.Timedelta(days=1)
    prediction = model.predict([[tomorrow.toordinal()]])

    return prediction[0]