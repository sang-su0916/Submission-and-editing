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
from utils.common import load_css

class FeedbackModel:
    """
    학생 답안 및 첨삭 데이터 관리 클래스
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.feedback_file = os.path.join(data_dir, 'feedback_data.json')
        self.feedback_data = self._load_feedback_data()
    
    def _load_feedback_data(self):
        """피드백 데이터 로드"""
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_feedback_data(self):
        """피드백 데이터 저장"""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
    
    def add_submission(self, submission_data):
        """학생 답안 제출 추가"""
        self.feedback_data.append(submission_data)
        self._save_feedback_data()
    
    def update_feedback(self, submission_id, feedback_content, score=None):
        """첨삭 내용 업데이트"""
        for submission in self.feedback_data:
            if submission['id'] == submission_id:
                submission['feedback'] = feedback_content
                if score is not None:
                    submission['score'] = score
                submission['feedback_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_feedback_data()
                return True
        return False
    
    def get_submissions(self, student_id=None, problem_id=None, has_feedback=None):
        """제출된 답안 조회"""
        submissions = self.feedback_data
        
        if student_id:
            submissions = [s for s in submissions if s['student_id'] == student_id]
        
        if problem_id:
            submissions = [s for s in submissions if s['problem_id'] == problem_id]
        
        if has_feedback is not None:
            if has_feedback:
                submissions = [s for s in submissions if 'feedback' in s and s['feedback']]
            else:
                submissions = [s for s in submissions if 'feedback' not in s or not s['feedback']]
        
        return submissions
    
    def get_submission_by_id(self, submission_id):
        """ID로 제출 답안 조회"""
        for submission in self.feedback_data:
            if submission['id'] == submission_id:
                return submission
        return None

def app():
    # CSS 로드
    load_css()
    
    st.title("첨삭 시스템")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # ProblemModel 인스턴스 생성
    problem_model = ProblemModel(data_dir)
    
    # FeedbackModel 인스턴스 생성
    feedback_model = FeedbackModel(data_dir)
    
    # 사용자 역할 확인 (세션에서)
    user_role = st.session_state.get('role', 'student')  # 기본값은 학생
    
    # 탭 생성 (역할에 따라 다른 탭 표시)
    if user_role == 'teacher':
        tab1, tab2 = st.tabs(["첨삭 대기 목록", "첨삭 완료 목록"])
        
        # 탭 1: 첨삭 대기 목록
        with tab1:
            st.header("첨삭 대기 목록")
            
            # 첨삭되지 않은 제출 답안 목록
            pending_submissions = feedback_model.get_submissions(has_feedback=False)
            
            if pending_submissions:
                # 제출 목록 표시
                submission_df = pd.DataFrame([
                    {
                        '제출 ID': s['id'],
                        '학생 ID': s['student_id'],
                        '문제 제목': s['problem_title'],
                        '제출 시간': s['submitted_at']
                    } for s in pending_submissions
                ])
                
                st.dataframe(submission_df)
                
                # 선택한 제출 답안 첨삭
                selected_submission_id = st.selectbox(
                    "첨삭할 제출 답안 선택",
                    [s['id'] for s in pending_submissions],
                    format_func=lambda x: f"{next((s['student_id'] for s in pending_submissions if s['id'] == x), '')} - {next((s['problem_title'] for s in pending_submissions if s['id'] == x), '')}"
                )
                
                if selected_submission_id:
                    selected_submission = feedback_model.get_submission_by_id(selected_submission_id)
                    
                    if selected_submission:
                        st.subheader("제출 답안 정보")
                        st.write(f"**학생 ID:** {selected_submission['student_id']}")
                        st.write(f"**문제 제목:** {selected_submission['problem_title']}")
                        st.write(f"**제출 시간:** {selected_submission['submitted_at']}")
                        
                        # 문제 내용 표시
                        problem_id = selected_submission['problem_id']
                        problem_data = problem_model.get_problem_by_id(problem_id)
                        
                        if problem_data:
                            st.subheader("문제 내용")
                            st.write(problem_data['content'])
                            
                            st.subheader("정답")
                            st.write(problem_data['answer'])
                        
                        # 학생 답안 표시
                        st.subheader("학생 답안")
                        st.write(selected_submission['answer'])
                        
                        # 첨삭 입력
                        st.subheader("첨삭 내용")
                        feedback_content = st.text_area("첨삭 내용을 입력하세요", height=200)
                        
                        # 점수 입력
                        score = st.slider("점수", 0, 100, 0)
                        
                        # 첨삭 저장 버튼
                        if st.button("첨삭 저장"):
                            if feedback_content:
                                # 첨삭 내용 저장
                                feedback_model.update_feedback(
                                    selected_submission_id,
                                    feedback_content,
                                    score
                                )
                                
                                st.success("첨삭이 저장되었습니다!")
                                st.experimental_rerun()
                            else:
                                st.error("첨삭 내용을 입력해주세요.")
            else:
                st.info("첨삭 대기 중인 제출 답안이 없습니다.")
        
        # 탭 2: 첨삭 완료 목록
        with tab2:
            st.header("첨삭 완료 목록")
            
            # 첨삭된 제출 답안 목록
            completed_submissions = feedback_model.get_submissions(has_feedback=True)
            
            if completed_submissions:
                # 제출 목록 표시
                submission_df = pd.DataFrame([
                    {
                        '제출 ID': s['id'],
                        '학생 ID': s['student_id'],
                        '문제 제목': s['problem_title'],
                        '점수': s.get('score', 'N/A'),
                        '첨삭 시간': s.get('feedback_at', 'N/A')
                    } for s in completed_submissions
                ])
                
                st.dataframe(submission_df)
                
                # 선택한 제출 답안 상세 보기
                selected_submission_id = st.selectbox(
                    "상세 보기할 제출 답안 선택",
                    [s['id'] for s in completed_submissions],
                    format_func=lambda x: f"{next((s['student_id'] for s in completed_submissions if s['id'] == x), '')} - {next((s['problem_title'] for s in completed_submissions if s['id'] == x), '')}"
                )
                
                if selected_submission_id:
                    selected_submission = feedback_model.get_submission_by_id(selected_submission_id)
                    
                    if selected_submission:
                        st.subheader("제출 답안 정보")
                        st.write(f"**학생 ID:** {selected_submission['student_id']}")
                        st.write(f"**문제 제목:** {selected_submission['problem_title']}")
                        st.write(f"**제출 시간:** {selected_submission['submitted_at']}")
                        st.write(f"**점수:** {selected_submission.get('score', 'N/A')}")
                        
                        # 문제 내용 표시
                        problem_id = selected_submission['problem_id']
                        problem_data = problem_model.get_problem_by_id(problem_id)
                        
                        if problem_data:
                            st.subheader("문제 내용")
                            st.write(problem_data['content'])
                            
                            st.subheader("정답")
                            st.write(problem_data['answer'])
                        
                        # 학생 답안 표시
                        st.subheader("학생 답안")
                        st.write(selected_submission['answer'])
                        
                        # 첨삭 내용 표시
                        st.subheader("첨삭 내용")
                        st.write(selected_submission['feedback'])
                        
                        # 첨삭 수정 옵션
                        if st.checkbox("첨삭 수정하기"):
                            # 첨삭 입력
                            new_feedback_content = st.text_area(
                                "첨삭 내용을 수정하세요",
                                selected_submission['feedback'],
                                height=200
                            )
                            
                            # 점수 입력
                            new_score = st.slider(
                                "점수",
                                0, 100,
                                selected_submission.get('score', 0)
                            )
                            
                            # 첨삭 저장 버튼
                            if st.button("첨삭 수정 저장"):
                                if new_feedback_content:
                                    # 첨삭 내용 저장
                                    feedback_model.update_feedback(
                                        selected_submission_id,
                                        new_feedback_content,
                                        new_score
                                    )
                                    
                                    st.success("첨삭이 수정되었습니다!")
                                    st.experimental_rerun()
                                else:
                                    st.error("첨삭 내용을 입력해주세요.")
            else:
                st.info("첨삭 완료된 제출 답안이 없습니다.")
    
    else:  # 학생 역할
        tab1, tab2 = st.tabs(["문제 풀기", "첨삭 확인"])
        
        # 탭 1: 문제 풀기
        with tab1:
            st.header("문제 풀기")
            
            # 필터링 옵션
            col1, col2, col3 = st.columns(3)
            
            with col1:
                subject_filter = st.selectbox(
                    "과목 선택",
                    ["전체"] + problem_model.get_unique_values('subject')
                )
            
            with col2:
                problem_type_filter = st.selectbox(
                    "문제 유형 선택",
                    ["전체"] + problem_model.get_unique_values('problem_type')
                )
            
            with col3:
                difficulty_filter = st.selectbox(
                    "난이도 선택",
                    ["전체"] + problem_model.get_unique_values('difficulty')
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
                selected_problem_title = st.selectbox("문제 선택", problem_titles)
                
                # 선택된 문제 정보
                selected_problem = filtered_problems[filtered_problems['title'] == selected_problem_title].iloc[0].to_dict()
                
                # 문제 내용 표시
                st.subheader("문제")
                st.write(f"**제목:** {selected_problem['title']}")
                st.write(f"**과목:** {selected_problem['subject']}")
                st.write(f"**유형:** {selected_problem['problem_type']}")
                st.write(f"**난이도:** {selected_problem['difficulty']}")
                st.write("**문제 내용:**")
                st.write(selected_problem['content'])
                
                # 답안 입력
                st.subheader("답안 작성")
                student_answer = st.text_area("답안을 작성하세요", height=200)
                
                # 현재 사용자 ID 가져오기 (세션에서)
                current_user = st.session_state.get('username', '익명')
                
                # 제출 버튼
                if st.button("답안 제출"):
                    if student_answer:
                        # 제출 ID 생성
                        submission_id = str(uuid.uuid4())
                        
                        # 제출 시간 추가
                        submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 제출 데이터 준비
                        submission_data = {
                            'id': submission_id,
                            'student_id': current_user,
                            'problem_id': selected_problem['id'],
                            'problem_title': selected_problem['title'],
                            'answer': student_answer,
                            'submitted_at': submitted_at
                        }
                        
                        # 제출 저장
                        feedback_model.add_submission(submission_data)
                        
                        st.success("답안이 제출되었습니다!")
                        
                        # 입력 필드 초기화
                        st.experimental_rerun()
                    else:
                        st.error("답안을 입력해주세요.")
            else:
                st.warning("선택한 조건에 맞는 문제가 없습니다.")
        
        # 탭 2: 첨삭 확인
        with tab2:
            st.header("첨삭 확인")
            
            # 현재 사용자 ID 가져오기 (세션에서)
            current_user = st.session_state.get('username', '익명')
            
            # 사용자의 제출 답안 목록
            user_submissions = feedback_model.get_submissions(student_id=current_user)
            
            if user_submissions:
                # 첨삭 여부에 따라 분류
                feedback_completed = [s for s in user_submissions if 'feedback' in s and s['feedback']]
                feedback_pending = [s for s in user_submissions if 'feedback' not in s or not s['feedback']]
                
                # 첨삭 완료된 답안 목록
                if feedback_completed:
                    st.subheader("첨삭 완료된 답안")
                    
                    # 제출 목록 표시
                    completed_df = pd.DataFrame([
                        {
                            '문제 제목': s['problem_title'],
                            '제출 시간': s['submitted_at'],
                            '점수': s.get('score', 'N/A'),
                            '첨삭 시간': s.get('feedback_at', 'N/A')
                        } for s in feedback_completed
                    ])
                    
                    st.dataframe(completed_df)
                    
                    # 선택한 제출 답안 상세 보기
                    selected_submission_id = st.selectbox(
                        "상세 보기할 답안 선택",
                        [s['id'] for s in feedback_completed],
                        format_func=lambda x: f"{next((s['problem_title'] for s in feedback_completed if s['id'] == x), '')} ({next((s['submitted_at'] for s in feedback_completed if s['id'] == x), '')})"
                    )
                    
                    if selected_submission_id:
                        selected_submission = feedback_model.get_submission_by_id(selected_submission_id)
                        
                        if selected_submission:
                            st.write(f"**문제 제목:** {selected_submission['problem_title']}")
                            st.write(f"**제출 시간:** {selected_submission['submitted_at']}")
                            st.write(f"**점수:** {selected_submission.get('score', 'N/A')}")
                            
                            # 문제 내용 표시
                            problem_id = selected_submission['problem_id']
                            problem_data = problem_model.get_problem_by_id(problem_id)
                            
                            if problem_data:
                                st.subheader("문제 내용")
                                st.write(problem_data['content'])
                            
                            # 학생 답안 표시
                            st.subheader("내 답안")
                            st.write(selected_submission['answer'])
                            
                            # 첨삭 내용 표시
                            st.subheader("첨삭 내용")
                            st.write(selected_submission['feedback'])
                
                # 첨삭 대기 중인 답안 목록
                if feedback_pending:
                    st.subheader("첨삭 대기 중인 답안")
                    
                    # 제출 목록 표시
                    pending_df = pd.DataFrame([
                        {
                            '문제 제목': s['problem_title'],
                            '제출 시간': s['submitted_at']
                        } for s in feedback_pending
                    ])
                    
                    st.dataframe(pending_df)
                    
                    # 선택한 제출 답안 상세 보기
                    selected_pending_id = st.selectbox(
                        "상세 보기할 답안 선택",
                        [s['id'] for s in feedback_pending],
                        format_func=lambda x: f"{next((s['problem_title'] for s in feedback_pending if s['id'] == x), '')} ({next((s['submitted_at'] for s in feedback_pending if s['id'] == x), '')})"
                    )
                    
                    if selected_pending_id:
                        selected_pending = feedback_model.get_submission_by_id(selected_pending_id)
                        
                        if selected_pending:
                            st.write(f"**문제 제목:** {selected_pending['problem_title']}")
                            st.write(f"**제출 시간:** {selected_pending['submitted_at']}")
                            
                            # 문제 내용 표시
                            problem_id = selected_pending['problem_id']
                            problem_data = problem_model.get_problem_by_id(problem_id)
                            
                            if problem_data:
                                st.subheader("문제 내용")
                                st.write(problem_data['content'])
                            
                            # 학생 답안 표시
                            st.subheader("내 답안")
                            st.write(selected_pending['answer'])
                            
                            st.info("첨삭 대기 중입니다.")
            else:
                st.info("제출한 답안이 없습니다.")

if __name__ == "__main__":
    app()
