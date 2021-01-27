import os
import string
import random
from modules import db
from flask import Flask, render_template, request, redirect, url_for, session, jsonify


app = Flask(__name__)

mysql = db.Database()
app.secret_key = os.urandom(16)


# 호찬이가 올려준 함수 임의로 사용가능하게 수정했음
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
    # ajax 에서 보낸 데이터 받기
    data = request.get_json()
    session_key = data['session']
    ans = data['answer']

    # html 에 띄워야 할 보기를 저장하는 리스트
    answer_list = list()

    # session[]에 저장하는 값이 자료 구조라면 session.modified 를 내가 True 로 set 해줘야 안에 들어있는 값을 수정할 수 있다.
    session.modified = True
    cur_idx = session[session_key]['question_order_cur']

    # question_order_cur 업데이트
    session[session_key]['question_order_cur'] += 1

    # 만약에 더 이상 질문이 없다면 바로 done=True 를 json 형태로 리턴
    if cur_idx >= (len(session[session_key]['question_order'])):
        return jsonify(done=True)

    # 데이터 베이스에서 질문과 보기 가져오기
    cur_qna_idx = session[session_key]['question_order'][cur_idx]
    query = "SELECT * FROM qna WHERE que_no = " + str(cur_qna_idx)

    cur_qna = mysql.executeOne(query)

    #ans_v*가 null 이면 버튼 추가X
    if cur_qna['ans_v1'] is not None:
        answer_list.append(cur_qna['ans_v1'])
    if cur_qna['ans_v2'] is not None:
        answer_list.append(cur_qna['ans_v2'])
    if cur_qna['ans_v3'] is not None:
        answer_list.append(cur_qna['ans_v3'])

    print("Session requested : " + data['session'])

    # javascript 쪽에서 받은 제대로 된 데이터가 있을 때만 prior 을 업데이트 해야하므로
    # 그것을 구분하기 위해 ans 에 저장된 값이 0인지 확인
    if ans != 0:
        # 질문과 관련된 table의 이름 가져오기
        table_name = cur_qna['udo_name']
        # table에서 사용자가 보낸 값 (udo_v1 / udo_v2 / udo_v3)에 대응하는 확률 값 가져오기
        query = "SELECT " + ans + " FROM " + table_name
        udo = mysql.executeAll(query)
        # 가져온 값들은
        # { { 'udo_v1' : 0.8 }, { 'udo_v1' : 0.2 }, { 'udo_v1' : 0.8 } }
        # 이런 dictionary 형태로 저장되어있기 때문에 다시 list 형태로 저장
        udo = [value[ans] for value in udo]
        
        # prior값들 업데이트
        session[session_key]['prior'] = updatePrior(session[session_key]['prior'], udo)

    return jsonify(result=cur_qna['que'], answer=answer_list, done=False)


@app.route('/result', methods=['GET', 'POST'])
def result():
    # 호찬이가 제안한 Bayes 정리를 이용한 결과 처리
    # POST로 넘어온 session key값 받기
    session_key = request.form['session_key']

    # 가장 높은 prior 값을 갖는 index 를 찾아 most_recommended_no에 저장
    # 현재 같은 prior 값이 있으면 그냥 index가 가장 작은 음식의 이름이 나오도록 되어있음.
    # 같은 값이 있으면 랜덤하게?
    most_recommended_no = session[session_key]['prior'].index(max(session[session_key]['prior'])) + 1

    # DB에서 most_recommended_no에 해당하는 음식의 이름 가져와 most_recommended_name에 저장
    query = "SELECT food_name FROM food_prior WHERE food_no = " + str(most_recommended_no)
    most_recommended_name = mysql.executeOne(query)
    most_recommended_name = most_recommended_name['food_name']

    # 이 부분은 호찬이와 윤석이의 이해를 돕기 위해 따로 코딩한 것이므로 생략 가능
    # -------------------------------------------------------------------------------------
    # 결과 확인
    food_name = "SELECT food_name FROM food_prior"
    food_name = mysql.executeAll(food_name)
    food_name = [value['food_name'] for value in food_name]

    _result = {name: value for name, value in zip(food_name, session[session_key]['prior'])}

    for index, value in enumerate(session[session_key]['prior']):
        print(str(index + 1) + ". " + food_name[index] + " - " + str(value))
    # --------------------------------------------------------------------------------------

    return render_template('result.html', dish=most_recommended_name, results=_result)


if __name__ == '__main__':
    app.run()
