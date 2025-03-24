import streamlit as st
import pandas as pd
import os
import sys

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.data_models import ProblemModel, SubmissionModel, UserModel

def test_problem_database():
    """
    문제 데이터베이스 기능 테스트
    """
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # ProblemModel 인스턴스 생성
    problem_model = ProblemModel(data_dir)
    
    # 모든 문제 가져오기
    all_problems = problem_model.get_all_problems()
    print(f"총 문제 수: {len(all_problems)}")
    
    # 과목별 문제 필터링
    english_problems = problem_model.filter_problems(subject='영어')
    math_problems = problem_model.filter_problems(subject='수학')
    print(f"영어 문제 수: {len(english_problems)}")
    print(f"수학 문제 수: {len(math_problems)}")
    
    # 난이도별 문제 필터링
    beginner_problems = problem_model.filter_problems(difficulty='초급')
    intermediate_problems = problem_model.filter_problems(difficulty='중급')
    advanced_problems = problem_model.filter_problems(difficulty='고급')
    print(f"초급 문제 수: {len(beginner_problems)}")
    print(f"중급 문제 수: {len(intermediate_problems)}")
    print(f"고급 문제 수: {len(advanced_problems)}")
    
    # 문제 유형별 필터링
    for subject in ['영어', '수학']:
        print(f"\n{subject} 과목 문제 유형별 분포:")
        for problem_type in problem_model.filter_problems(subject=subject)['problem_type'].unique():
            count = len(problem_model.filter_problems(subject=subject, problem_type=problem_type))
            print(f"- {problem_type}: {count}개")
    
    # 새 문제 추가 테스트
    new_problem = {
        'subject': '영어',
        'problem_type': '어휘',
        'difficulty': '중급',
        'title': '테스트 문제',
        'content': '이것은 테스트 문제입니다.',
        'answer': '테스트 답안',
        'created_by': '테스트 사용자'
    }
    
    new_id = problem_model.add_problem(new_problem)
    print(f"\n새 문제가 추가되었습니다. ID: {new_id}")
    
    # 추가된 문제 확인
    added_problem = problem_model.get_problem_by_id(new_id)
    print(f"추가된 문제 제목: {added_problem['title']}")
    
    # 문제 업데이트 테스트
    update_data = {
        'title': '업데이트된 테스트 문제',
        'content': '이것은 업데이트된 테스트 문제입니다.'
    }
    
    problem_model.update_problem(new_id, update_data)
    print(f"\n문제가 업데이트되었습니다. ID: {new_id}")
    
    # 업데이트된 문제 확인
    updated_problem = problem_model.get_problem_by_id(new_id)
    print(f"업데이트된 문제 제목: {updated_problem['title']}")
    
    # 문제 삭제 테스트
    problem_model.delete_problem(new_id)
    print(f"\n문제가 삭제되었습니다. ID: {new_id}")
    
    # 삭제 확인
    deleted_problem = problem_model.get_problem_by_id(new_id)
    print(f"삭제된 문제 조회 결과: {deleted_problem}")
    
    print("\n문제 데이터베이스 기능 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_problem_database()
