from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def hello_world():
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
