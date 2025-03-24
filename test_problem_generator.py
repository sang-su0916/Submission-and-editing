import streamlit as st
import pandas as pd
import os
import sys
import nltk

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.data_models import ProblemModel
from models.problem_generator import ProblemGenerator, ProblemTemplateGenerator

# NLTK 데이터 다운로드 확인
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

def test_problem_generator():
    """
    문제 생성 기능 테스트
    """
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # ProblemModel 인스턴스 생성
    problem_model = ProblemModel(data_dir)
    
    # ProblemGenerator 인스턴스 생성
    problem_generator = ProblemGenerator()
    
    # ProblemTemplateGenerator 인스턴스 생성
    template_generator = ProblemTemplateGenerator()
    
    print("===== 문제 생성 기능 테스트 =====")
    
    # 1. 기존 문제 기반 새 문제 생성 테스트
    print("\n1. 기존 문제 기반 새 문제 생성 테스트")
    
    # 영어 문제 선택
    english_problems = problem_model.filter_problems(subject='영어')
    if not english_problems.empty:
        english_problem = english_problems.iloc[0].to_dict()
        
        print(f"원본 문제: {english_problem['title']}")
        print(f"내용: {english_problem['content'][:100]}...")
        
        # 유의어 대체 전략으로 새 문제 생성
        new_problem_synonym = problem_generator.generate_problem(english_problem, strategy='synonym_replacement')
        print("\n유의어 대체 전략으로 생성된 문제:")
        print(f"제목: {new_problem_synonym['title']}")
        print(f"내용: {new_problem_synonym['content'][:100]}...")
        
        # 문장 구조 변경 전략으로 새 문제 생성
        new_problem_structure = problem_generator.generate_problem(english_problem, strategy='sentence_structure')
        print("\n문장 구조 변경 전략으로 생성된 문제:")
        print(f"제목: {new_problem_structure['title']}")
        print(f"내용: {new_problem_structure['content'][:100]}...")
        
        # 난이도 조정 전략으로 새 문제 생성 (난이도 증가)
        new_problem_harder = problem_generator.generate_problem(english_problem, strategy='difficulty_adjustment', difficulty_change=1)
        print("\n난이도 증가 전략으로 생성된 문제:")
        print(f"제목: {new_problem_harder['title']}")
        print(f"난이도: {new_problem_harder['difficulty']}")
        print(f"내용: {new_problem_harder['content'][:100]}...")
    
    # 수학 문제 선택
    math_problems = problem_model.filter_problems(subject='수학')
    if not math_problems.empty:
        math_problem = math_problems.iloc[0].to_dict()
        
        print(f"\n원본 문제: {math_problem['title']}")
        print(f"내용: {math_problem['content']}")
        
        # 난이도 조정 전략으로 새 문제 생성 (난이도 감소)
        new_problem_easier = problem_generator.generate_problem(math_problem, strategy='difficulty_adjustment', difficulty_change=-1)
        print("\n난이도 감소 전략으로 생성된 문제:")
        print(f"제목: {new_problem_easier['title']}")
        print(f"난이도: {new_problem_easier['difficulty']}")
        print(f"내용: {new_problem_easier['content']}")
    
    # 2. 문제 유형별 템플릿 생성 테스트
    print("\n2. 문제 유형별 템플릿 생성 테스트")
    
    # 영어 어휘 중급 템플릿
    english_vocab_template = template_generator.get_template('영어', '어휘', '중급')
    print("\n영어 어휘 중급 템플릿:")
    print(f"제목: {english_vocab_template['title']}")
    print(f"내용: {english_vocab_template['content'][:100]}...")
    
    # 수학 기하 고급 템플릿
    math_geometry_template = template_generator.get_template('수학', '기하', '고급')
    print("\n수학 기하 고급 템플릿:")
    print(f"제목: {math_geometry_template['title']}")
    print(f"내용: {math_geometry_template['content']}")
    
    print("\n문제 생성 기능 테스트가 완료되었습니다.")

if __name__ == "__main__":
    test_problem_generator()
