import pyrebase
from flask import Flask, render_template, request

app = Flask(__name__)

config = {
    "apiKey": "AIzaSyAqAZIyg2YSVvXCgtqI0b4IGYfp-R88mH8",
    "authDomain": "winter-80fa9.firebaseapp.com",
    "databaseURL": "https://winter-80fa9-default-rtdb.firebaseio.com",
    "projectId": "winter-80fa9",
    "storageBucket": "winter-80fa9.appspot.com",
    "messagingSenderId": "1047783723358",
    "appId": "1:1047783723358:web:0e0aaaae52df428877bfcf",
    "measurementId": "G-XFTNSE9Z2V"
  };

firebase = pyrebase.initialize_app(config)
db = firebase.database()

@app.route('/')
def hello_world():
    db.child('test').update({"company" : "google"})
    db.child('winter').update({"friend": "윤석"})
    return render_template('home.html')


@app.route('/post', methods=['POST'])
def post():
    if request.method == 'POST':
        data = request.form['data']
        return data
    else:
        return render_template('home.html')


if __name__ == '__main__':
    app.run()
