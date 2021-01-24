import os
import string
import random
from modules import db
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)

mysql = db.Database()
dict_session_question = dict()
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
    # main 기능 X
    # newConnector =
    return render_template('home.html')


@app.route('/play')
def play():
    # generate session random key
    new_session = get_random_key()
    while new_session in session:
        new_session = get_random_key()

    # session 안에 데이터로 음식들의 prior값을 넣으면 나중에 처리하기 쉬워질 것 같다.
    session[new_session] = 0

    # random question order
    rand_question = mysql.executeAll("select que_no from qna ORDER BY rand()")

    # list 안에 dict 형태로 SELECT 결과가 저장되어있는 것을 value 만 갖고와서 따로 list 로 저장
    rand_question = [value['que_no'] for value in rand_question]
    print("Session requested : " + new_session)
    print(rand_question)
    dict_session_question[new_session] = rand_question

    return render_template('question.html', key=new_session)


@app.route('/ajax', methods=['POST'])
def ajax():
    data = request.get_json()
    key = data['session']
    answer_list = list()

    next_idx = dict_session_question[key][session[key]]
    session[key] += 1

    query = "SELECT * FROM qna WHERE que_no = " + str(next_idx)
    next_qna = mysql.executeOne(query)

    #ans_v*가 null 이면 버튼 추가X
    if next_qna['ans_v1'] is not None:
        answer_list.append(next_qna['ans_v1'])
    if next_qna['ans_v2'] is not None:
        answer_list.append(next_qna['ans_v2'])
    if next_qna['ans_v3'] is not None:
        answer_list.append(next_qna['ans_v3'])

    print("Session requested : " + data['session'])
    print("next idx : " + str(next_idx))
    print(answer_list)

    return jsonify(result=next_qna['que'], answer=answer_list)

# @app.route('/result', methods=['POST'])
# def result():
# 호찬이가 제안한 Bayes 정리를 이용한 결과 처리 방식 도입 예정


if __name__ == '__main__':
    app.run()
