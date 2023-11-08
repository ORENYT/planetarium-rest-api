# Planetarium Django REST API
* Docker required

### Run with docker:
````
docker-compose build
docker-compose run
````
### Run it local:
1. Download it from GitHub or make a pull
2. Create a PostgreSQL database
3. Create .env file, using .env_sample
   (input your data)
Or run this code:
````
git clone https://github.com/ORENYT/planetarium-rest-api.git
cd planetarium-rest-api
python -m venv venv
source venv/bin/activate
set DB_HOST=<your_data>
set DB_NAME=<your_data>
set DB_USER=<your_data>
set DB_PASSWORD=<your_data>
set DB_PORT=<your_data>
python manage.py migrate
python manage.py runserver
````
### Authentication type is JWT
* Register via [/api/user/register](http://127.0.0.1:8000/api/user/token/)
* Get access via [/api/user/token](http://127.0.0.1:8000/api/user/token/)
