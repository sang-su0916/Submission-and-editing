import streamlit as st
import os
import sys
import json
import pandas as pd
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_css

class FeedbackCheck:
    """
    학생이 제출한 답안에 대한 첨삭 내용을 확인하는 클래스
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.feedback_file = os.path.join(data_dir, 'feedback_data.json')
        self.problems_file = os.path.join(data_dir, 'problems.json')
        self.feedback_data = self._load_feedback_data()
        self.problems_data = self._load_problems_data()
    
    def _load_feedback_data(self):
        """피드백 데이터 로드"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"피드백 데이터 로드 중 오류 발생: {e}")
                return []
        return []
    
    def _load_problems_data(self):
        """문제 데이터 로드"""
        if os.path.exists(self.problems_file):
            try:
                with open(self.problems_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"문제 데이터 로드 중 오류 발생: {e}")
                return []
        return []
    
    def get_student_feedbacks(self, student_id):
        """학생이 받은 첨삭 목록"""
        return [f for f in self.feedback_data if f.get('student_id') == student_id]
    
    def get_feedback_by_id(self, submission_id):
        """ID로 첨삭 정보 가져오기"""
        for feedback in self.feedback_data:
            if feedback.get('submission_id') == submission_id:
                return feedback
        return None
    
    def get_problem_by_id(self, problem_id):
        """ID로 문제 정보 가져오기"""
        for problem in self.problems_data:
            if problem.get('id') == problem_id:
                return problem
        return None
    
    def get_feedback_stats(self, student_id):
        """학생의 첨삭 통계 정보"""
        feedbacks = self.get_student_feedbacks(student_id)
        
        if not feedbacks:
            return {
                'total_submissions': 0,
                'graded_submissions': 0,
                'average_score': 0,
                'subject_stats': {}
            }
        
        graded_submissions = [f for f in feedbacks if 'feedback' in f]
        
        # 과목별 통계
        subject_stats = {}
        for feedback in graded_submissions:
            subject = feedback.get('subject', '기타')
            if subject not in subject_stats:
                subject_stats[subject] = {
                    'count': 0,
                    'total_score': 0
                }
            subject_stats[subject]['count'] += 1
            if 'score' in feedback:
                subject_stats[subject]['total_score'] += feedback['score']
        
        # 과목별 평균 점수 계산
        for subject in subject_stats:
            if subject_stats[subject]['count'] > 0:
                subject_stats[subject]['average_score'] = (
                    subject_stats[subject]['total_score'] / subject_stats[subject]['count']
                )
        
        # 전체 평균 계산
        total_score = sum(f.get('score', 0) for f in graded_submissions if 'score' in f)
        graded_with_score = [f for f in graded_submissions if 'score' in f]
        average_score = total_score / len(graded_with_score) if graded_with_score else 0
        
        return {
            'total_submissions': len(feedbacks),
            'graded_submissions': len(graded_submissions),
            'average_score': average_score,
            'subject_stats': subject_stats
        }

def app():
    # CSS 로드
    load_css()
    
    st.title("첨삭 확인")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # FeedbackCheck 인스턴스 생성
    feedback_check = FeedbackCheck(data_dir)
    
    # 사용자 정보 확인 (세션에서)
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', '익명')
    user_role = st.session_state.get('role', 'student')
    
    # 로그인 상태와 학생인지 확인
    if not st.session_state.get('logged_in', False) or user_role != 'student':
        st.error("학생으로 로그인해야 이 페이지를 볼 수 있습니다.")
        return
    
    # 세션 상태 초기화
    if 'selected_feedback_id' not in st.session_state:
        st.session_state.selected_feedback_id = None
    
    # 첨삭 통계 가져오기
    stats = feedback_check.get_feedback_stats(username)
    
    # 통계 표시
    st.subheader("첨삭 요약")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 제출 문제", stats['total_submissions'])
    
    with col2:
        st.metric("첨삭 완료", stats['graded_submissions'])
    
    with col3:
        avg_score = f"{stats['average_score']:.1f}" if stats['graded_submissions'] > 0 else "N/A"
        st.metric("평균 점수", avg_score)
    
    # 과목별 통계 (선택적)
    if stats['subject_stats']:
        st.subheader("과목별 성적")
        
        # 표로 표시
        subject_data = []
        for subject, data in stats['subject_stats'].items():
            avg = data.get('average_score', 0)
            subject_data.append({
                '과목': subject,
                '문제 수': data.get('count', 0),
                '평균 점수': f"{avg:.1f}" if avg > 0 else "N/A"
            })
        
        if subject_data:
            df = pd.DataFrame(subject_data)
            st.dataframe(df)
    
    # 첨삭 목록 가져오기
    feedbacks = feedback_check.get_student_feedbacks(username)
    
    if not feedbacks:
        st.info("아직 제출한 문제가 없습니다.")
    else:
        # 탭 생성
        tab1, tab2 = st.tabs(["전체 첨삭 목록", "첨삭 상세 보기"])
        
        # 탭 1: 전체 첨삭 목록
        with tab1:
            st.subheader("첨삭 목록")
            
            # 첨삭 데이터 추출 및 변환
            feedback_list = []
            for feedback in feedbacks:
                status = "첨삭 완료" if "feedback" in feedback else "첨삭 대기"
                score = feedback.get("score", "N/A") if "score" in feedback else "N/A"
                
                feedback_list.append({
                    '제목': feedback.get('problem_title', ''),
                    '과목': feedback.get('subject', ''),
                    '제출일': feedback.get('submitted_at', ''),
                    '상태': status,
                    '점수': score,
                    'ID': feedback.get('submission_id', '')
                })
            
            # 데이터프레임으로 변환하여 표시
            if feedback_list:
                df = pd.DataFrame(feedback_list)
                # ID 열 숨기기
                display_df = df.drop(columns=['ID'])
                st.dataframe(display_df)
                
                # 첨삭 선택
                selected_index = st.selectbox(
                    "상세 확인할 첨삭 선택",
                    range(len(feedback_list)),
                    format_func=lambda i: f"{feedback_list[i]['제목']} ({feedback_list[i]['상태']})"
                )
                
                selected_feedback_id = feedback_list[selected_index]['ID']
                st.session_state.selected_feedback_id = selected_feedback_id
                
                # 탭 2로 이동 버튼
                if st.button("상세 보기"):
                    st.session_state.active_tab = "상세"
        
        # 탭 2: 첨삭 상세 보기
        with tab2:
            selected_id = st.session_state.get('selected_feedback_id')
            
            if selected_id:
                feedback = feedback_check.get_feedback_by_id(selected_id)
                
                if feedback:
                    problem_id = feedback.get('problem_id')
                    problem = feedback_check.get_problem_by_id(problem_id) if problem_id else None
                    
                    # 문제 정보
                    st.subheader(f"문제: {feedback.get('problem_title', '')}")
                    
                    if problem:
                        st.markdown("### 문제 내용")
                        st.markdown(problem.get('content', ''))
                    
                    # 학생 답안
                    st.markdown("### 제출한 답안")
                    st.markdown(feedback.get('answer', ''))
                    
                    # 첨삭 내용
                    if 'feedback' in feedback:
                        st.markdown("### 첨삭 내용")
                        st.markdown(feedback.get('feedback', ''))
                        
                        if 'score' in feedback:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.metric("점수", feedback.get('score', 0))
                            with col2:
                                if 'feedback_at' in feedback:
                                    st.info(f"첨삭일: {feedback.get('feedback_at', '')}")
                    else:
                        st.warning("아직 첨삭이 완료되지 않았습니다.")
                else:
                    st.error("선택한 첨삭 정보를 찾을 수 없습니다.")
            else:
                st.info("왼쪽 탭에서 확인할 첨삭을 선택해주세요.") 