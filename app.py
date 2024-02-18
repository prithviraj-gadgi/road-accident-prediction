import os
import requests
import numpy as np
from flask import Flask, render_template, request, jsonify
from sklearn.externals import joblib

app = Flask(__name__)
model = joblib.load('model.sav')


def send_sms(message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    numbers = "9632029678"

    payload = f'message={message}&language=english&route=q&numbers={numbers}'

    headers = {
        'authorization': os.environ['FAST2SMS_API_KEY'],
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def cal(ip):
    input = dict(ip)
    Did_Police_Officer_Attend = input['Did_Police_Officer_Attend'][0]
    age_of_driver = input['age_of_driver'][0]
    vehicle_type = input['vehicle_type'][0]
    age_of_vehicle = input['age_of_vehicle'][0]
    engine_cc = input['engine_cc'][0]
    day = input['day'][0]
    weather = input['weather'][0]
    light = input['light'][0]
    roadsc = input['roadsc'][0]
    gender = input['gender'][0]
    speedl = input['speedl'][0]

    data = np.array(
        [Did_Police_Officer_Attend, age_of_driver, vehicle_type,
         age_of_vehicle, engine_cc, day, weather, roadsc, light,
         gender, speedl]
    )

    print("logging", data)
    data = data.astype(float)
    data = data.reshape(1, -1)

    try:
        result = model.predict(data)
    except Exception as e:
        result = str(e)

    return str(result[0])


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/map', methods=['GET'])
def map():
    return render_template('map.html')


@app.route('/visualization', methods=['GET'])
def visualization():
    return render_template('visualization.html')


@app.route('/', methods=['POST'])
def get():
    return cal(request.form)


@app.route('/sms', methods=['POST'])
def sms():
    message = request.form['message']
    try:
        send_sms(message)
        return 'SMS sent successfully!'
    except Exception as e:
        return str(e)


@app.route('/get_message', methods=['GET'])
def get_message():
    message = os.environ['OPEN_WEATHER_MAP_API_KEY']
    return jsonify({'message': message})


if __name__ == '__main__':
    app.run(debug=True)
