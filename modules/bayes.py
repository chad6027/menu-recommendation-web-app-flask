prior = {1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2}  # 사전확률
# 질문 리스트가 담긴 테이블을 만들어야 하나..?
udo_kor = [0.9, 0.9, 0.9, 0.1, 0.1]  # 답이 두개 초과인 경우 2차원리스트?
udo_diet = [0.9, 0.1, 0.1, 0.1, 0.9]
udo_spicy = [0.1, 0.9, 0.1, 0.1, 0.1]
udo_drinking = [0.9, 0.1, 0.9, 0.9, 0.1]
key = {1, 2, 3, 4, 5}


def updatePrior(prior, udo):  # bayes정리를 이용하여 사전확률을 갱신한다.
    up, down = 0, 0
    ans1 = input("(y or n) : ")
    result = []  # 초기화해야 함수를 반복적으로 사용 가능

    for index, value in enumerate(prior):
        up = udo[index] * value  # 분자 계산
        for in_index, in_value in enumerate(prior):  # 분모 계산
            down += udo[in_index] * in_value

        postValue = round(up / down, 4)  # postValue : 사후확률, 소수점 아래 조절
        result.append(postValue)  # list result에 값 삽입
        up, down = 0, 0

    return result

    # if ans1 == 'y':
    #     for k, v in prior.items():  # 사후 확률 계산
    #         up = udo[k - 1] * v  # 분자 계산
    #         for ke, va in prior.items():  # 분모 계산
    #             down += udo[ke - 1] * va
    #
    #         postValue = round(up / down, 4)  # postValue : 사후확률, 소수점 아래 조절
    #         result.append(postValue)  # list result에 값 삽입
    #         up, down = 0, 0

    # dict_result = dict(zip(key, result))  # 두 리스트를 딕셔너리 형태로 변환
    # print(dict_result)
    #
    # return dict_result

prior = updatePrior(prior, udo_kor, "한식 어때")

prior = updatePrior(prior, udo_diet, "다이어트 중?")

prior = updatePrior(prior, udo_spicy, "매운거 어때")

prior = updatePrior(prior, udo_drinking, "술ㄱ?")
