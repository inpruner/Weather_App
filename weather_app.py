from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import sys
import os


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = os.urandom(16)
dialect = 'sqlite:///'
db_path = '\\db\\weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
uri = os.getenv("DATABASE_URL")
if uri is not None:
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or (dialect + app.root_path + db_path)
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'{self.name}'


db.create_all()


def get_weather(city_name):
    url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city_name,
              'units': 'metric',
              'appid': 'ccd0fe135c3a9971a1844fe5364d210c'}
    res = requests.get(url, params=params).json()
    if res['cod'] in ['400', '404']:
        return None
    else:
        current_weather = {'name': res['name'].upper(),
                           'id': res['id'],
                           'temp': round(res['main']['temp']),
                           'weather_state': res['weather'][0]['main']}
        return current_weather


@app.route('/')
def index():
    cities = City.query.all()
    weather_dict = []
    for city in cities:
        weather_dict.append(get_weather(city))
    return render_template('index.html', weather=weather_dict)


@app.route('/add', methods=['POST'])
def add_city():
    city_name = request.form['city_name']
    city = get_weather(city_name)
    if city is None:
        flash("The city doesn't exist!")
        return redirect(url_for('index'))
    else:
        if City.query.filter_by(id=city['id']).first() is not None:
            flash('The city has already been added to the list!')
        else:
            db.session.add(City(id=city['id'], name=city['name']))
            db.session.commit()
        return redirect(url_for('index'))


@app.route('/delete/<city_id>', methods=['POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
