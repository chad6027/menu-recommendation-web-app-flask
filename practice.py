import os
import string
import random
from modules import db
from flask import Flask, render_template, request, redirect, url_for, session, jsonify


app = Flask(__name__)

mysql = db.Database()
app.secret_key = os.urandom(16)


def updatePrior(prior, udo):  # bayes정리를 이용하여 사전확률을 갱신한다.
    up, down = 0, 0
    result = []  # 초기화해야 함수를 반복적으로 사용 가능

    for index, value in enumerate(prior):
        up = udo[index] * value  # 분자 계산
        for in_index, in_value in enumerate(prior):  # 분모 계산
            down += udo[in_index] * in_value

        postValue = round(up / down, 5)  # postValue : 사후확률, 소수점 아래 조절
        result.append(postValue)  # list result에 값 삽입
        up, down = 0, 0

    return result


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
    session[new_session] = dict()
    session[new_session]['cur'] = 0

    # random question order
    rand_question = mysql.executeAll("SELECT que_no FROM qna ORDER BY rand()")

    # list 안에 dict 형태로 SELECT 결과가 저장되어있는 것을 value 만 갖고와서 따로 list 로 저장
    rand_question = [value['que_no'] for value in rand_question]
    session[new_session]['question_order_cur'] = 0
    session[new_session]['question_order'] = rand_question

    #사전 확률 구해서 저장
    prior_probability = mysql.executeAll("SELECT prior FROM food_prior")
    prior_probability = [value['prior'] for value in prior_probability]
    session[new_session]['prior'] = prior_probability

    return render_template('question.html', key=new_session)


@app.route('/ajax', methods=['POST'])
def ajax():
    data = request.get_json()
    session_key = data['session']
    ans = data['answer']
    answer_list = list()

    session.modified = True
    session[session_key]['question_order_cur'] += 1
    next_idx = session[session_key]['question_order_cur']
    next_qna_idx = session[session_key]['question_order'][next_idx]

    query = "SELECT * FROM qna WHERE que_no = " + str(next_qna_idx)

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

    if ans != 0:
        table_name = next_qna['udo_name']
        query = "SELECT " + ans + " FROM " + table_name
        udo = mysql.executeAll(query)
        udo = [value[ans] for value in udo]

        session[session_key]['prior'] = updatePrior(session[session_key]['prior'], udo)

    return jsonify(result=next_qna['que'], answer=answer_list)


# @app.route('/result', methods=['POST'])
# def result():
# 호찬이가 제안한 Bayes 정리를 이용한 결과 처리 방식 도입 예정


if __name__ == '__main__':
    app.run()
