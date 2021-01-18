import os
import sqlite3
import string
import random
from modules import db
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

test_db = db.Database()

conn = sqlite3.connect('2020.db')
c = conn.cursor()
cur_qt = 0
qt = [
    '한식 어때?',
    '다이어트중이야?',
    '매운게 끌려?',
    '누구랑 먹어?',
    '술은? 안드시게? 이걸 참아?'
]
schema = []
ans = []
#
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.secret_key = os.urandom(16)


def get_random_key():
    sample_str = ''.join((random.choice(string.ascii_letters) for i in range(5)))
    sample_str += ''.join((random.choice(string.digits) for i in range(5)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)
    return final_string


@app.route('/')
def hello_world():
    # newConnector =
    global cur_qt
    cur_qt = 0
    return render_template('home.html')


@app.route('/play')
def play():
    new_session = get_random_key()
    while new_session in session:
        new_session = get_random_key()
    session[new_session] = 0

    return new_session


@app.route('/question')
def question():
    global cur_qt
    if request.method == 'POST':
        print(request.form["data"])
        ans.append(request.form["data"])
        return redirect(url_for('question'))
    else:
        return render_template('question.html', question=qt[cur_qt])


@app.route('/post', methods=['POST'])
def post():
    global cur_qt, ans
    cur_qt = cur_qt + 1
    if request.method == 'POST':
        print(request.form["data"])
        ans.append(request.form["data"])
        return redirect(url_for('question'))
    else:
        return render_template('home.html')


# @app.route('/result', methods=['POST'])
# def result():
# 호찬이가 제안한 Bayes 정리를 이용한 결과 처리 방식 도입 예정


if __name__ == '__main__':
    app.run()
