import streamlit as st
import pandas as pd
import os
import sys
import json
import uuid
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.data_models import ProblemModel
from models.problem_generator import ProblemGenerator, ProblemTemplateGenerator
from utils.common import load_css

def app():
    # CSS 로드
    load_css()
    
    st.title("문제 출제 시스템")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # ProblemModel 인스턴스 생성
    problem_model = ProblemModel(data_dir)
    
    # ProblemGenerator 인스턴스 생성
    problem_generator = ProblemGenerator()
    
    # ProblemTemplateGenerator 인스턴스 생성
    template_generator = ProblemTemplateGenerator()
    
    # 세션 상태 초기화
    if 'generated_problem' not in st.session_state:
        st.session_state.generated_problem = None
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["기존 문제 변형", "템플릿으로 새 문제 생성", "직접 문제 작성"])
    
    # 탭 1: 기존 문제 변형
    with tab1:
        st.header("기존 문제 변형")
        
        # 필터링 옵션
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subject_filter = st.selectbox(
                "과목 선택",
                ["전체"] + problem_model.get_unique_values('subject'),
                key="subject_filter_tab1"
            )
        
        with col2:
            problem_type_filter = st.selectbox(
                "문제 유형 선택",
                ["전체"] + problem_model.get_unique_values('problem_type'),
                key="problem_type_filter_tab1"
            )
        
        with col3:
            difficulty_filter = st.selectbox(
                "난이도 선택",
                ["전체"] + problem_model.get_unique_values('difficulty'),
                key="difficulty_filter_tab1"
            )
        
        # 필터링 적용
        filter_kwargs = {}
        if subject_filter != "전체":
            filter_kwargs['subject'] = subject_filter
        if problem_type_filter != "전체":
            filter_kwargs['problem_type'] = problem_type_filter
        if difficulty_filter != "전체":
            filter_kwargs['difficulty'] = difficulty_filter
        
        filtered_problems = problem_model.filter_problems(**filter_kwargs)
        
        if not filtered_problems.empty:
            # 문제 선택
            problem_titles = filtered_problems['title'].tolist()
            selected_problem_title = st.selectbox("문제 선택", problem_titles, key="selected_problem_tab1")
            
            # 선택된 문제 정보
            selected_problem = filtered_problems[filtered_problems['title'] == selected_problem_title].iloc[0].to_dict()
            
            # 문제 내용 표시
            st.subheader("선택된 문제")
            st.write(f"**제목:** {selected_problem['title']}")
            st.write(f"**과목:** {selected_problem['subject']}")
            st.write(f"**유형:** {selected_problem['problem_type']}")
            st.write(f"**난이도:** {selected_problem['difficulty']}")
            st.write("**문제 내용:**")
            st.text_area("", selected_problem['content'], height=150, key="original_content_tab1", disabled=True)
            st.write("**정답:**")
            st.text_area("", selected_problem['answer'], height=100, key="original_answer_tab1", disabled=True)
            
            # 변형 옵션
            st.subheader("변형 옵션")
            
            col1, col2 = st.columns(2)
            
            with col1:
                generation_strategy = st.selectbox(
                    "변형 전략",
                    ["유의어 대체", "문장 구조 변경", "난이도 조정"],
                    key="generation_strategy_tab1"
                )
            
            with col2:
                if generation_strategy == "난이도 조정":
                    difficulty_change = st.selectbox(
                        "난이도 변경",
                        [("쉽게", -1), ("유지", 0), ("어렵게", 1)],
                        format_func=lambda x: x[0],
                        key="difficulty_change_tab1"
                    )[1]
                else:
                    difficulty_change = 0
            
            # 전략 매핑
            strategy_mapping = {
                "유의어 대체": "synonym_replacement",
                "문장 구조 변경": "sentence_structure",
                "난이도 조정": "difficulty_adjustment"
            }
            
            # 문제 생성 버튼
            if st.button("문제 변형하기", key="generate_button_tab1"):
                with st.spinner("문제를 변형하는 중..."):
                    # 문제 생성
                    new_problem = problem_generator.generate_problem(
                        selected_problem,
                        strategy=strategy_mapping[generation_strategy],
                        difficulty_change=difficulty_change
                    )
                    
                    # 생성된 문제 저장
                    st.session_state.generated_problem = new_problem
            
            # 생성된 문제 표시
            if st.session_state.generated_problem:
                st.subheader("변형된 문제")
                st.write(f"**제목:** {st.session_state.generated_problem['title']}")
                st.write(f"**과목:** {st.session_state.generated_problem['subject']}")
                st.write(f"**유형:** {st.session_state.generated_problem['problem_type']}")
                st.write(f"**난이도:** {st.session_state.generated_problem['difficulty']}")
                st.write("**문제 내용:**")
                
                # 문제 내용 편집 가능
                edited_content = st.text_area(
                    "",
                    st.session_state.generated_problem['content'],
                    height=150,
                    key="edited_content_tab1"
                )
                st.session_state.generated_problem['content'] = edited_content
                
                st.write("**정답:**")
                
                # 정답 편집 가능
                edited_answer = st.text_area(
                    "",
                    st.session_state.generated_problem['answer'],
                    height=100,
                    key="edited_answer_tab1"
                )
                st.session_state.generated_problem['answer'] = edited_answer
                
                # 문제 저장 버튼
                if st.button("문제 저장하기", key="save_button_tab1"):
                    with st.spinner("문제를 저장하는 중..."):
                        # 현재 사용자 정보 가져오기 (세션에서)
                        current_user = st.session_state.get('username', '시스템')
                        
                        # 문제 ID 생성
                        problem_id = str(uuid.uuid4())
                        
                        # 생성 시간 추가
                        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 문제 데이터 준비
                        problem_data = {
                            'id': problem_id,
                            'title': st.session_state.generated_problem['title'],
                            'subject': st.session_state.generated_problem['subject'],
                            'problem_type': st.session_state.generated_problem['problem_type'],
                            'difficulty': st.session_state.generated_problem['difficulty'],
                            'content': edited_content,
                            'answer': edited_answer,
                            'created_by': current_user,
                            'created_at': created_at
                        }
                        
                        # 문제 저장
                        problem_model.add_problem(problem_data)
                        
                        st.success("문제가 성공적으로 저장되었습니다!")
                        
                        # 세션 상태 초기화
                        st.session_state.generated_problem = None
                        
                        # 페이지 새로고침
                        st.experimental_rerun()
        else:
            st.warning("선택한 조건에 맞는 문제가 없습니다.")
    
    # 탭 2: 템플릿으로 새 문제 생성
    with tab2:
        st.header("템플릿으로 새 문제 생성")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            template_subject = st.selectbox(
                "과목 선택",
                ["영어", "수학"],
                key="subject_tab2"
            )
        
        with col2:
            # 과목에 따른 문제 유형 옵션
            if template_subject == "영어":
                problem_types = ["어휘", "문법", "독해", "작문", "듣기"]
            else:  # 수학
                problem_types = ["대수", "기하", "미적분", "확률과 통계", "수열"]
            
            template_problem_type = st.selectbox(
                "문제 유형 선택",
                problem_types,
                key="problem_type_tab2"
            )
        
        with col3:
            template_difficulty = st.selectbox(
                "난이도 선택",
                ["초급", "중급", "고급"],
                key="difficulty_tab2"
            )
        
        # 템플릿 가져오기 버튼
        if st.button("템플릿 가져오기", key="template_button_tab2"):
            with st.spinner("템플릿을 가져오는 중..."):
                # 템플릿 생성
                template = template_generator.get_template(
                    template_subject,
                    template_problem_type,
                    template_difficulty
                )
                
                # 생성된 템플릿 저장
                st.session_state.generated_problem = template
        
        # 생성된 템플릿 표시
        if st.session_state.generated_problem:
            st.subheader("템플릿 문제")
            
            # 제목 편집 가능
            edited_title = st.text_input(
                "제목",
                st.session_state.generated_problem['title'],
                key="edited_title_tab2"
            )
            st.session_state.generated_problem['title'] = edited_title
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**과목:** {st.session_state.generated_problem['subject']}")
            
            with col2:
                st.write(f"**유형:** {st.session_state.generated_problem['problem_type']}")
            
            with col3:
                st.write(f"**난이도:** {st.session_state.generated_problem['difficulty']}")
            
            st.write("**문제 내용:**")
            
            # 문제 내용 편집 가능
            edited_content = st.text_area(
                "",
                st.session_state.generated_problem['content'],
                height=200,
                key="edited_content_tab2"
            )
            st.session_state.generated_problem['content'] = edited_content
            
            st.write("**정답:**")
            
            # 정답 편집 가능
            edited_answer = st.text_area(
                "",
                st.session_state.generated_problem['answer'],
                height=150,
                key="edited_answer_tab2"
            )
            st.session_state.generated_problem['answer'] = edited_answer
            
            # 문제 저장 버튼
            if st.button("문제 저장하기", key="save_button_tab2"):
                with st.spinner("문제를 저장하는 중..."):
                    # 현재 사용자 정보 가져오기 (세션에서)
                    current_user = st.session_state.get('username', '시스템')
                    
                    # 문제 ID 생성
                    problem_id = str(uuid.uuid4())
                    
                    # 생성 시간 추가
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 문제 데이터 준비
                    problem_data = {
                        'id': problem_id,
                        'title': edited_title,
                        'subject': st.session_state.generated_problem['subject'],
                        'problem_type': st.session_state.generated_problem['problem_type'],
                        'difficulty': st.session_state.generated_problem['difficulty'],
                        'content': edited_content,
                        'answer': edited_answer,
                        'created_by': current_user,
                        'created_at': created_at
                    }
                    
                    # 문제 저장
                    problem_model.add_problem(problem_data)
                    
                    st.success("문제가 성공적으로 저장되었습니다!")
                    
                    # 세션 상태 초기화
                    st.session_state.generated_problem = None
                    
                    # 페이지 새로고침
                    st.experimental_rerun()
    
    # 탭 3: 직접 문제 작성
    with tab3:
        st.header("직접 문제 작성")
        
        # 문제 정보 입력
        title = st.text_input("제목", key="title_tab3")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subject = st.selectbox(
                "과목",
                ["영어", "수학"],
                key="subject_tab3"
            )
        
        with col2:
            # 과목에 따른 문제 유형 옵션
            if subject == "영어":
                problem_types = ["어휘", "문법", "독해", "작문", "듣기"]
            else:  # 수학
                problem_types = ["대수", "기하", "미적분", "확률과 통계", "수열"]
            
            problem_type = st.selectbox(
                "문제 유형",
                problem_types,
                key="problem_type_tab3"
            )
        
        with col3:
            difficulty = st.selectbox(
                "난이도",
                ["초급", "중급", "고급"],
                key="difficulty_tab3"
            )
        
        # 문제 내용 입력
        content = st.text_area("문제 내용", height=200, key="content_tab3")
        
        # 정답 입력
        answer = st.text_area("정답", height=150, key="answer_tab3")
        
        # 문제 저장 버튼
        if st.button("문제 저장하기", key="save_button_tab3"):
            if title and content and answer:
                with st.spinner("문제를 저장하는 중..."):
                    # 현재 사용자 정보 가져오기 (세션에서)
                    current_user = st.session_state.get('username', '시스템')
                    
                    # 문제 ID 생성
                    problem_id = str(uuid.uuid4())
                    
                    # 생성 시간 추가
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 문제 데이터 준비
                    problem_data = {
                        'id': problem_id,
                        'title': title,
                        'subject': subject,
                        'problem_type': problem_type,
                        'difficulty': difficulty,
                        'content': content,
                        'answer': answer,
                        'created_by': current_user,
                        'created_at': created_at
                    }
                    
                    # 문제 저장
                    problem_model.add_problem(problem_data)
                    
                    st.success("문제가 성공적으로 저장되었습니다!")
                    
                    # 입력 필드 초기화
                    st.experimental_rerun()
            else:
                st.error("제목, 문제 내용, 정답을 모두 입력해주세요.")

if __name__ == "__main__":
    app()
