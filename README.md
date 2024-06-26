# Road Accident Prediction
A Predictive Model of Road Traffic Accidents

## Follow below steps to setup the project (Windows)
> conda create --prefix=./venv python=3.6
> 
> conda activate venv
> 
> pip install -r requirements.txt

## Follow below steps to setup the project (Linux)
> sudo apt install python3-dev
> 
> sudo apt install libmysqlclient-dev
> 
> sudo apt install libssl-dev
> 
> sudo apt install build-essential
> 
> conda create --prefix=./venv python=3.6
> 
> conda activate venv
> 
> pip install -r requirements.txt
> 
> conda install -c conda-forge gcc

## Execute below command in Git Bash to generate a new self-signed SSL certificate
> openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

### It will prompt you to enter details as mentioned below:
>Country Name (2 letter code) [AU]:IN  
>State or Province Name (full name) [Some-State]:Karnataka  
>Locality Name (eg, city) []:Bangalore  
>Organization Name (eg, company) [Internet Widgits Pty Ltd]:IIT Jodhpur  
>Organizational Unit Name (eg, section) []:DCS  
>Common Name (e.g. server FQDN or YOUR name) []:Prithviraj  
>Email Address []:prithvirajgadgi@gmail.com

**Note:** The existing certificate will expire on `Saturday 21 June 2025 at 23:04:36`

## Execute below commands in MySQL
>CREATE DATABASE \`user-system`;
> 
>USE user-system;
> 
>CREATE TABLE user (
>    userid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
>    name VARCHAR(100) NOT NULL,
>    email VARCHAR(100) NOT NULL UNIQUE,
>    password VARCHAR(255) NOT NULL,
>    age_of_driver VARCHAR(100) NOT NULL,
>    vehicle_type VARCHAR(100) NOT NULL,
>    age_of_vehicle VARCHAR(100) NOT NULL,
>    engine_capacity_in_cc VARCHAR(100) NOT NULL,
>    gender VARCHAR(100) NOT NULL
>);

## Setup in AWS
The first step is to install Anaconda and MySQL in Ubuntu EC2-Instance.

Execute below commands to run the application.
>sudo apt install python3-pip supervisor -y
> 
>sudo nano /etc/supervisor/conf.d/flaskapp.conf
> 
>[program:flaskapp]  
>directory=/path/to/project  
>command=/path/to/venv/python /path/to/project/app.py  
>autostart=true  
>autorestart=true  
>startretries=3  
>stdout_logfile=/var/log/flaskapp.out.log  
>stderr_logfile=/var/log/flaskapp.err.log
> 
>sudo supervisorctl reread
> 
>sudo supervisorctl update
> 
>sudo supervisorctl start flaskapp
> 
>sudo supervisorctl status flaskapp
> 
>sudo systemctl enable supervisor
> 
>sudo systemctl status supervisor

### To view the logs
>cat /var/log/flaskapp.out.log
> 
>cat /var/log/flaskapp.err.log
