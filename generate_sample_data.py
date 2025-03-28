import pandas as pd
import os
import json

# 데이터 디렉토리 생성
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# 영어 문제 샘플 데이터
english_problems = [
    {
        'id': 1,
        'subject': '영어',
        'problem_type': '어휘',
        'difficulty': '초급',
        'title': '기초 영어 어휘 문제 1',
        'content': '''다음 빈칸에 들어갈 가장 적절한 단어를 고르시오.

The weather was so nice that we decided to ________ our picnic in the park.
a) cancel
b) postpone
c) have
d) avoid''',
        'answer': 'c) have',
        'created_by': '김선생'
    },
    {
        'id': 2,
        'subject': '영어',
        'problem_type': '문법',
        'difficulty': '중급',
        'title': '영어 시제 문제',
        'content': '''다음 문장의 빈칸에 들어갈 가장 적절한 표현을 고르시오.

By the time we arrived at the theater, the movie ________.
a) already started
b) has already started
c) had already started
d) was already starting''',
        'answer': 'c) had already started',
        'created_by': '김선생'
    },
    {
        'id': 3,
        'subject': '영어',
        'problem_type': '독해',
        'difficulty': '고급',
        'title': '영어 독해 지문 분석',
        'content': '''다음 글을 읽고 물음에 답하시오.

The concept of sustainable development has gained significant traction in recent decades as humanity grapples with the environmental consequences of industrialization and population growth. At its core, sustainable development seeks to meet the needs of the present without compromising the ability of future generations to meet their own needs. This principle acknowledges the finite nature of Earth's resources and the delicate balance of ecosystems that support all life.

Critics argue that sustainable development is an oxymoron—that development inherently depletes resources and damages environments. However, proponents counter that with appropriate technology, policy frameworks, and social consciousness, human societies can progress economically while maintaining environmental integrity. This perspective emphasizes innovation, efficiency, and the circular economy as pathways to reconcile human advancement with ecological preservation.

글의 주제로 가장 적절한 것은?
a) 지속 가능한 개발의 개념과 그에 대한 다양한 관점
b) 산업화로 인한 환경 문제의 심각성
c) 미래 세대를 위한 자원 보존의 중요성
d) 환경 보호를 위한 기술 혁신의 필요성''',
        'answer': 'a) 지속 가능한 개발의 개념과 그에 대한 다양한 관점',
        'created_by': '김선생'
    },
    {
        'id': 4,
        'subject': '영어',
        'problem_type': '작문',
        'difficulty': '중급',
        'title': '영어 에세이 작성',
        'content': '''다음 주제에 대해 100-150단어 분량의 영어 에세이를 작성하시오.

Topic: The advantages and disadvantages of social media in modern society.

Your essay should include:
- An introduction with a clear thesis statement
- At least two advantages with examples
- At least two disadvantages with examples
- A conclusion summarizing your main points''',
        'answer': '''Sample answer:
Social media has fundamentally transformed how we communicate and interact in modern society, bringing both benefits and drawbacks. On the positive side, platforms like Instagram and Twitter enable instant global communication, allowing people to maintain relationships regardless of distance. Additionally, social media has democratized information sharing, giving voice to marginalized communities and facilitating social movements.

However, these benefits come with significant costs. The constant exposure to curated, idealized versions of others' lives has been linked to increased anxiety, depression, and poor self-image, especially among young users. Furthermore, the echo chamber effect of algorithmic content selection reinforces existing beliefs and contributes to societal polarization.

In conclusion, while social media offers unprecedented connectivity and information access, we must be mindful of its psychological impacts and tendency to divide rather than unite.''',
        'created_by': '김선생'
    },
    {
        'id': 5,
        'subject': '영어',
        'problem_type': '듣기',
        'difficulty': '초급',
        'title': '영어 대화 이해하기',
        'content': '''다음 대화를 듣고 질문에 답하시오. (실제 앱에서는 오디오 파일이 제공됩니다)

Woman: Excuse me, do you know what time the library closes today?
Man: Yes, it usually closes at 9 PM on weekdays, but today is Friday, so it closes at 6 PM.
Woman: Oh, I see. And what about the weekend?
Man: It's open from 10 AM to 4 PM on Saturday, but it's closed on Sunday.
Woman: Thank you for the information.

질문: 오늘 도서관은 몇 시에 문을 닫나요?
a) 오후 4시
b) 오후 6시
c) 오후 9시
d) 오늘은 문을 열지 않습니다''',
        'answer': 'b) 오후 6시',
        'created_by': '김선생'
    }
]

# 수학 문제 샘플 데이터
math_problems = [
    {
        'id': 6,
        'subject': '수학',
        'problem_type': '대수',
        'difficulty': '초급',
        'title': '일차방정식 풀기',
        'content': '''다음 방정식을 풀어 x의 값을 구하시오.

3x + 7 = 22''',
        'answer': 'x = 5',
        'created_by': '김선생'
    },
    {
        'id': 7,
        'subject': '수학',
        'problem_type': '기하',
        'difficulty': '중급',
        'title': '삼각형의 넓이 구하기',
        'content': '''밑변의 길이가 8cm이고 높이가 6cm인 삼각형의 넓이를 구하시오.''',
        'answer': '24cm²',
        'created_by': '김선생'
    },
    {
        'id': 8,
        'subject': '수학',
        'problem_type': '미적분',
        'difficulty': '고급',
        'title': '함수의 미분',
        'content': '''다음 함수를 x에 대해 미분하시오.

f(x) = 3x² + 5x - 2''',
        'answer': 'f\'(x) = 6x + 5',
        'created_by': '김선생'
    },
    {
        'id': 9,
        'subject': '수학',
        'problem_type': '확률과 통계',
        'difficulty': '중급',
        'title': '확률 계산하기',
        'content': '''주머니에 빨간 공 3개, 파란 공 2개, 노란 공 1개가 들어있다. 이 주머니에서 무작위로 2개의 공을 동시에 꺼낼 때, 두 공의 색이 같을 확률을 구하시오.''',
        'answer': '1/5 = 0.2',
        'created_by': '김선생'
    },
    {
        'id': 10,
        'subject': '수학',
        'problem_type': '수열',
        'difficulty': '고급',
        'title': '수열의 일반항 구하기',
        'content': '''다음 수열의 일반항 a_n을 구하시오.

2, 6, 12, 20, 30, ...''',
        'answer': 'a_n = n(n+1)',
        'created_by': '김선생'
    }
]

# 모든 문제 합치기
all_problems = english_problems + math_problems

# 문제 데이터프레임 생성 및 저장
problems_df = pd.DataFrame(all_problems)
problems_file = os.path.join(data_dir, 'problems.csv')
problems_df.to_csv(problems_file, index=False, encoding='utf-8-sig')

print(f"샘플 문제 데이터가 성공적으로 생성되었습니다. 총 {len(all_problems)}개의 문제가 {problems_file}에 저장되었습니다.")

# 기본 사용자 데이터 생성
users = {
    "teacher1": {"password": "teacher1", "type": "선생님", "name": "김선생"},
    "student1": {"password": "student1", "type": "학생", "name": "이학생"}
}

# 사용자 데이터 저장
users_file = os.path.join(data_dir, 'users.json')
with open(users_file, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=4)

print(f"기본 사용자 데이터가 성공적으로 생성되었습니다. {users_file}에 저장되었습니다.")

# 빈 제출 데이터프레임 생성 및 저장
submissions_df = pd.DataFrame({
    'id': [],
    'student_name': [],
    'problem_id': [],
    'problem_title': [],
    'answer': [],
    'score': [],
    'feedback': [],
    'evaluated_by': []
})
submissions_file = os.path.join(data_dir, 'submissions.csv')
submissions_df.to_csv(submissions_file, index=False, encoding='utf-8-sig')

print(f"빈 제출 데이터프레임이 성공적으로 생성되었습니다. {submissions_file}에 저장되었습니다.")
