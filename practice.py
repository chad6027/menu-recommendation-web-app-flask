import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

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
choice = {'Korean': ['O', 'X'], 'Diet': ['O', 'X'], 'Spicy': ['O', 'X'], 'Partner': ['X', '혼자', '애인', ' 그외'], 'Alcohol': ['X', '맥주', '소주']}
schema = []
ans = []


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
    global cur_qt
    cur_qt = 0
    return render_template('home.html')


@app.route('/question')
def question():
    global cur_qt
    cur_qt = cur_qt + 1
    if cur_qt < choice.__sizeof__():
        return render_template('question.html', question=qt[cur_qt], choices=choice[schema[cur_qt]])
    else:
        return redirect(url_for('result'))


@app.route('/post', methods=['POST'])
def post():
    global cur_qt, ans
    cur_qt = cur_qt + 1
    print(cur_qt)
    if request.method == 'POST':
        print(request.form["data"])
        ans.append(request.form['data'])
        return redirect(url_for('question'))
    else:
        return render_template('home.html')


@app.route('/result', methods=['POST'])
def result():
    sql = "SELECT Menu FROM dish WHERE "
    for i in range(0, ans.__sizeof__() - 1):
        sql = sql + schema[i] + " = " + ans[i] + " and "
    sql.removesuffix('end')
    menu = c.execute(sql)
    if menu.__sizeof__() == 1:
        return render_template('result.html', dish=menu.fetchone())
    else:
        repeat = random.random(0, menu.__sizeof__() - 1)
        while repeat > 0:
            menu.next()
            repeat -= 1
        return render_template('result.html', dish=menu.fetchone())


if __name__ == '__main__':
    app.run()
