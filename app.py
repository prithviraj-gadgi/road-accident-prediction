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
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            email = session.get('email')
            cursor.execute('SELECT age_of_driver FROM user WHERE email = % s', (email,))
            age_of_driver = cursor.fetchone()['age_of_driver']
            cursor.execute('SELECT age_of_vehicle FROM user WHERE email = % s', (email,))
            age_of_vehicle = cursor.fetchone()['age_of_vehicle']
            cursor.execute('SELECT engine_capacity_in_cc FROM user WHERE email = % s', (email,))
            engine_capacity_in_cc = cursor.fetchone()['engine_capacity_in_cc']
            cursor.execute('SELECT gender FROM user WHERE email = % s', (email,))
            gender = cursor.fetchone()['gender']
            if gender == "1":
                gender = 'Male'
            elif gender == "2":
                gender = 'Female'
            elif gender == "3":
                gender = 'Unknown'
            cursor.execute('SELECT vehicle_type FROM user WHERE email = % s', (email,))
            vehicle_type = cursor.fetchone()['vehicle_type']
            if vehicle_type == "1":
                vehicle_type = "Pedal cycle"
            elif vehicle_type == "2":
                vehicle_type = "Motorcycle 50cc and under"
            elif vehicle_type == "3":
                vehicle_type = "Motorcycle 125cc and under"
            elif vehicle_type == "4":
                vehicle_type = "Motorcycle over 125cc and up to 500cc"
            elif vehicle_type == "5":
                vehicle_type = "Motorcycle over 500cc"
            elif vehicle_type == "8":
                vehicle_type = "Taxi/Private hire car"
            elif vehicle_type == "9":
                vehicle_type = "Car"
            elif vehicle_type == "10":
                vehicle_type = "Minibus (8 - 16 passenger seats)"
            elif vehicle_type == "11":
                vehicle_type = "Bus or coach (17 or more pass seats)"
            elif vehicle_type == "18":
                vehicle_type = "Tram"
            elif vehicle_type == "20":
                vehicle_type = "Truck(Goods)"
            elif vehicle_type == "23":
                vehicle_type = "Electric motorcycle"
            return render_template('index.html', message=message, age_of_driver=age_of_driver,
                                   age_of_vehicle=age_of_vehicle, engine_capacity_in_cc=engine_capacity_in_cc,
                                   gender=gender, vehicle_type=vehicle_type)
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
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s)', (
            userName, email, password, age_of_driver, vehicle_type, age_of_vehicle, engine_capacity_in_cc, gender,))
            mysql.connection.commit()
            message = 'You have successfully registered !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message=message)


@app.route('/home', methods=['GET'])
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    email = session.get('email')
    cursor.execute('SELECT age_of_driver FROM user WHERE email = % s', (email,))
    age_of_driver = cursor.fetchone()['age_of_driver']
    cursor.execute('SELECT age_of_vehicle FROM user WHERE email = % s', (email,))
    age_of_vehicle = cursor.fetchone()['age_of_vehicle']
    cursor.execute('SELECT engine_capacity_in_cc FROM user WHERE email = % s', (email,))
    engine_capacity_in_cc = cursor.fetchone()['engine_capacity_in_cc']
    cursor.execute('SELECT gender FROM user WHERE email = % s', (email,))
    gender = cursor.fetchone()['gender']
    if gender == "1":
        gender = 'Male'
    elif gender == "2":
        gender = 'Female'
    elif gender == "3":
        gender = 'Unknown'
    cursor.execute('SELECT vehicle_type FROM user WHERE email = % s', (email,))
    vehicle_type = cursor.fetchone()['vehicle_type']
    if vehicle_type == "1":
        vehicle_type = "Pedal cycle"
    elif vehicle_type == "2":
        vehicle_type = "Motorcycle 50cc and under"
    elif vehicle_type == "3":
        vehicle_type = "Motorcycle 125cc and under"
    elif vehicle_type == "4":
        vehicle_type = "Motorcycle over 125cc and up to 500cc"
    elif vehicle_type == "5":
        vehicle_type = "Motorcycle over 500cc"
    elif vehicle_type == "8":
        vehicle_type = "Taxi/Private hire car"
    elif vehicle_type == "9":
        vehicle_type = "Car"
    elif vehicle_type == "10":
        vehicle_type = "Minibus (8 - 16 passenger seats)"
    elif vehicle_type == "11":
        vehicle_type = "Bus or coach (17 or more pass seats)"
    elif vehicle_type == "18":
        vehicle_type = "Tram"
    elif vehicle_type == "20":
        vehicle_type = "Truck(Goods)"
    elif vehicle_type == "23":
        vehicle_type = "Electric motorcycle"
    return render_template('index.html', age_of_driver=age_of_driver, age_of_vehicle=age_of_vehicle,
                           engine_capacity_in_cc=engine_capacity_in_cc, gender=gender, vehicle_type=vehicle_type)


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
