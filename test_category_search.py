import streamlit as st
import pandas as pd
import os
import sys

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.data_models import ProblemModel, SubmissionModel, UserModel

def test_category_and_search():
    """
    문제 카테고리 및 검색 기능 테스트
    """
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # ProblemModel 인스턴스 생성
    problem_model = ProblemModel(data_dir)
    
    print("===== 문제 카테고리 및 검색 기능 테스트 =====")
    
    # 카테고리별 필터링 테스트
    print("\n1. 카테고리별 필터링 테스트")
    
    # 과목별 필터링
    subjects = problem_model.get_all_problems()['subject'].unique()
    print(f"과목 목록: {', '.join(subjects)}")
    
    for subject in subjects:
        subject_problems = problem_model.filter_problems(subject=subject)
        print(f"{subject} 과목 문제 수: {len(subject_problems)}")
    
    # 문제 유형별 필터링
    problem_types = problem_model.get_all_problems()['problem_type'].unique()
    print(f"\n문제 유형 목록: {', '.join(problem_types)}")
    
    for problem_type in problem_types:
        type_problems = problem_model.filter_problems(problem_type=problem_type)
        print(f"{problem_type} 유형 문제 수: {len(type_problems)}")
    
    # 난이도별 필터링
    difficulties = problem_model.get_all_problems()['difficulty'].unique()
    print(f"\n난이도 목록: {', '.join(difficulties)}")
    
    for difficulty in difficulties:
        difficulty_problems = problem_model.filter_problems(difficulty=difficulty)
        print(f"{difficulty} 난이도 문제 수: {len(difficulty_problems)}")
    
    # 복합 필터링 테스트
    print("\n2. 복합 필터링 테스트")
    
    # 영어 + 중급 문제
    english_intermediate = problem_model.filter_problems(subject='영어', difficulty='중급')
    print(f"영어 중급 문제 수: {len(english_intermediate)}")
    
    # 수학 + 고급 문제
    math_advanced = problem_model.filter_problems(subject='수학', difficulty='고급')
    print(f"수학 고급 문제 수: {len(math_advanced)}")
    
    # 검색 기능 테스트
    print("\n3. 검색 기능 테스트")
    
    # 제목 검색
    title_search = problem_model.filter_problems(search_term='기초')
    print(f"'기초'가 포함된 문제 수: {len(title_search)}")
    
    # 내용 검색
    content_search = problem_model.filter_problems(search_term='삼각형')
    print(f"'삼각형'이 포함된 문제 수: {len(content_search)}")
    
    # 복합 검색 (과목 + 검색어)
    combined_search = problem_model.filter_problems(subject='영어', search_term='essay')
    print(f"영어 과목에서 'essay'가 포함된 문제 수: {len(combined_search)}")
    
    print("\n문제 카테고리 및 검색 기능 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_category_and_search()
