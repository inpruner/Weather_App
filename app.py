from flask import Flask
from flask import render_template
from flask import request
import requests
import sys

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_city():
    if request.form['city_name']:
        city_name = request.form['city_name']
    else:
        city_name = ''
    url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city_name,
              'units': 'metric',
              'appid': 'ccd0fe135c3a9971a1844fe5364d210c'}
    res = requests.get(url, params=params)
    weather_from_owa = res.json()
    weather_info = {'city_name': city_name.upper(),
                    'temp': round(weather_from_owa['main']['temp']),
                    'weather_state': weather_from_owa['weather'][0]['main']}
    return render_template('index.html', weather=weather_info)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
