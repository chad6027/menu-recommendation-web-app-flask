import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
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

# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.secret_key = os.urandom(16)


def countQt():
    global cur_qt
    cur_qt += 1


def getSchema():
    global schema

    data = c.execute("PRAGMA table_info('dish')")
    for i in data:
        print(i)
        schema.append(i[1])

    data = c.execute("SELECT * FROM dish")
    print(c.fetchall())


getSchema()


@app.route('/')
def hello_world():
    # newConnector =
    global cur_qt
    cur_qt = 0
    return render_template('home.html')


@app.route('/question')
def question():
    if cur_qt < 5:
        return render_template('question.html', question=qt[cur_qt])
    else:
        return redirect(url_for('result'))


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
