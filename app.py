import os
import requests
import numpy as np
from sklearn.externals import joblib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import bcrypt

app = Flask(__name__)

app.secret_key = 'xyz'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'user-system'

mysql = MySQL(app)

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


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully !'
            return render_template('index.html', message=message)
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'age_of_driver' in request.form and 'vehicle_type' in request.form and 'age_of_vehicle' in request.form and 'engine_capacity_in_cc' in request.form and 'gender' in request.form:
        userName = request.form['name']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        email = request.form['email']
        age_of_driver = request.form['age_of_driver']
        vehicle_type = request.form['vehicle_type']
        age_of_vehicle = request.form['age_of_vehicle']
        engine_capacity_in_cc = request.form['engine_capacity_in_cc']
        gender = request.form['gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not userName or not password or not email or not age_of_driver or not vehicle_type or not age_of_vehicle or not engine_capacity_in_cc or not gender:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s)', (userName, email, password, age_of_driver, vehicle_type, age_of_vehicle, engine_capacity_in_cc, gender,))
            mysql.connection.commit()
            message = 'You have successfully registered !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message=message)


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/map', methods=['GET'])
def map():
    return render_template('map.html')


@app.route('/visualization', methods=['GET'])
def visualization():
    return render_template('visualization.html')


@app.route('/ip', methods=['POST'])
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
