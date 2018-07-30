import colormeshop
from colormeshop.rest import ApiException

import os
import datetime
import requests
import json
import numpy as np
import matplotlib.pyplot as plt

from flask import Flask

# TODO: error handling
def fetch_sales():
    configuration = colormeshop.Configuration()
    configuration.access_token = os.environ['COLORME_ACCESS_TOKEN']

    api_instance = colormeshop.SaleApi(colormeshop.ApiClient(configuration))

    try:
        api_response = api_instance.get_sales(after='2012-01-01')
        return api_response['sales']
    except ApiException as e:
        print("Exception when calling SaleApi->get_sales: %s\n" % e)

def date_to_sale():
    date_to_sale = {}
    for sale in fetch_sales():
        key = datetime.date.fromtimestamp(sale['make_date']).strftime("%Y%m%d")
        if date_to_sale.get(key) is None:
            date_to_sale[key] = 0
        date_to_sale[datetime.date.fromtimestamp(sale['make_date']).strftime("%Y%m%d")] += sale['total_price']
    return date_to_sale

# TODO: error handling
def fetch_temperature(date):
    time = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]), 12).timestamp()
    uri = "https://api.darksky.net/forecast/{apikey}/35.658034,139.701636,{time}"
    response = requests.get(uri.format(apikey=os.environ['DARKSKY_API_KEY'], time=int(time)))
    data = json.loads(response.text)
    return to_sessi(data['daily']['data'][0]['temperatureHigh'])

def fetch_forecast():
    uri = "https://api.darksky.net/forecast/{apikey}/35.658034,139.701636"
    response = requests.get(uri.format(apikey=os.environ['DARKSKY_API_KEY']))
    return json.loads(response.text)


def to_sessi(n):
    return int(5.0 / 9.0 * (n - 32))

class LeastSquaresMethod:
    def __init__(self, temperatures, sales):
        self.temperatures = temperatures
        self.sales = sales
        self.build_model()

    def build_model(self):
        self.coefficient = self.covariance() / self.variance()
        self.constant = np.mean(self.sales) - self.coefficient * np.mean(self.temperatures)

    def predict(self, temperatures):
        return temperatures * self.coefficient + self.constant

    def variance(self):
        n = len(self.sales)
        mean_temperatures = np.mean(self.temperatures)
        v = 0
        for i in range(n):
            v += (1 / n) * (self.temperatures[i] - mean_temperatures) ** 2
        return v

    def covariance(self):
        n = len(self.sales)
        mean_temperatures = np.mean(self.temperatures)
        mean_sales = np.mean(self.sales)
        v = 0
        for i in range(n):
            v += (1 / n) * (self.temperatures[i] - mean_temperatures) * (self.sales[i] - mean_sales)
        return v

app = Flask(__name__, static_folder='images')

@app.route("/")
def hello():
    sales = []
    temperatures = []
    
    for date, sale in date_to_sale().items():
        sales.append(sale)
        temperatures.append(fetch_temperature(date))
    
    least_squares_method = LeastSquaresMethod(temperatures, sales)

    d = []
    s = []
    for f in fetch_forecast()['daily']['data']:
        d.append(datetime.date.fromtimestamp(f['time']).strftime('%m/%d'))
        s.append(least_squares_method.predict(to_sessi(f['temperatureHigh'])))

    plt.plot(d, s, 'b-')
    plt.xlabel('date')
    plt.ylabel('sales')
    plt.grid(True)
    plt.savefig('images/out.png')

    return '<img src="/images/out.png">'
