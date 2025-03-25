import streamlit as st
import pandas as pd
import os
import sys
import json
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_css

class StudentDashboard:
    """
    학생별 학습 진도 및 성적 관리 클래스
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.feedback_file = os.path.join(data_dir, 'feedback_data.json')
        self.students_file = os.path.join(data_dir, 'students.json')
        self.feedback_data = self._load_feedback_data()
        self.students_data = self._load_students_data()
    
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
    
    def _load_students_data(self):
        """학생 데이터 로드"""
        if os.path.exists(self.students_file):
            try:
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"학생 데이터 로드 중 오류 발생: {e}")
                return []
        return []
    
    def get_student_info(self, user_id):
        """사용자 ID로 학생 정보 조회"""
        for student in self.students_data:
            if student.get('user_id') == user_id:
                return student
        return None
    
    def get_student_submissions(self, user_id):
        """학생이 제출한 답안 목록"""
        return [s for s in self.feedback_data if s['student_id'] == user_id]
    
    def get_student_progress(self, user_id):
        """학생의 진행 상황 분석"""
        # 학생의 제출 답안 필터링
        student_submissions = self.get_student_submissions(user_id)
        
        if not student_submissions:
            return {
                'total_submissions': 0,
                'graded_submissions': 0,
                'average_score': 0,
                'scores_by_date': [],
                'recent_feedback': [],
                'subject_performance': {},
                'correct_rate': 0
            }
        
        # 첨삭 완료된 답안만 필터링
        graded_submissions = [s for s in student_submissions if 'score' in s]
        
        # 날짜별 점수 추출
        scores_by_date = []
        for submission in sorted(graded_submissions, key=lambda x: x.get('feedback_at', '')):
            if 'feedback_at' in submission and 'score' in submission:
                scores_by_date.append({
                    'date': submission['feedback_at'],
                    'score': submission['score'],
                    'problem_title': submission['problem_title']
                })
        
        # 과목별 성적 분석
        subject_performance = {}
        for submission in graded_submissions:
            if 'subject' in submission:
                subject = submission['subject']
                if subject not in subject_performance:
                    subject_performance[subject] = {
                        'count': 0,
                        'total_score': 0,
                        'correct_count': 0
                    }
                subject_performance[subject]['count'] += 1
                subject_performance[subject]['total_score'] += submission.get('score', 0)
                if submission.get('is_correct', False):
                    subject_performance[subject]['correct_count'] += 1
        
        # 과목별 평균 점수 계산
        for subject in subject_performance:
            if subject_performance[subject]['count'] > 0:
                subject_performance[subject]['average_score'] = (
                    subject_performance[subject]['total_score'] / subject_performance[subject]['count']
                )
                subject_performance[subject]['correct_rate'] = (
                    subject_performance[subject]['correct_count'] / subject_performance[subject]['count'] * 100
                )
        
        # 최근 피드백 내용 추출 (최대 3개)
        recent_feedback = []
        for submission in sorted(graded_submissions, key=lambda x: x.get('feedback_at', ''), reverse=True)[:3]:
            if 'feedback' in submission:
                recent_feedback.append({
                    'problem_title': submission['problem_title'],
                    'feedback': submission['feedback'],
                    'score': submission.get('score', 'N/A'),
                    'date': submission.get('feedback_at', 'N/A')
                })
        
        # 정답률 계산
        correct_submissions = [s for s in student_submissions if s.get('is_correct', False)]
        correct_rate = len(correct_submissions) / len(student_submissions) * 100 if student_submissions else 0
        
        return {
            'total_submissions': len(student_submissions),
            'graded_submissions': len(graded_submissions),
            'average_score': sum(s.get('score', 0) for s in graded_submissions) / len(graded_submissions) if graded_submissions else 0,
            'scores_by_date': scores_by_date,
            'recent_feedback': recent_feedback,
            'subject_performance': subject_performance,
            'correct_rate': correct_rate
        }

def app():
    # CSS 로드
    load_css()
    
    st.title("학생 대시보드")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # StudentDashboard 인스턴스 생성
    dashboard = StudentDashboard(data_dir)
    
    # 사용자 정보 확인 (세션에서)
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', '익명')
    user_role = st.session_state.get('role', 'student')
    
    # 로그인 상태와 학생인지 확인
    if not user_id or user_role != 'student':
        st.error("학생으로 로그인해야 이 페이지를 볼 수 있습니다.")
        return
    
    # 학생 정보 가져오기
    student_info = dashboard.get_student_info(user_id)
    
    if student_info:
        # 학생 기본 정보 표시
        st.header(f"{student_info.get('name', username)}님의 학습 현황")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**학번:** {student_info.get('student_number', '-')}")
            st.markdown(f"**학년:** {student_info.get('grade', '-')}")
        
        with col2:
            st.markdown(f"**반:** {student_info.get('class_name', '-')}")
            st.markdown(f"**최근 로그인:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 학생 진도 데이터 가져오기
    progress_data = dashboard.get_student_progress(username)
    
    # 기본 통계 지표
    st.subheader("학습 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 문제 풀이", progress_data['total_submissions'])
    
    with col2:
        st.metric("첨삭 완료", progress_data['graded_submissions'])
    
    with col3:
        avg_score = f"{progress_data['average_score']:.1f}" if progress_data['graded_submissions'] > 0 else "N/A"
        st.metric("평균 점수", avg_score)
    
    with col4:
        correct_rate = f"{progress_data['correct_rate']:.1f}%" if progress_data['total_submissions'] > 0 else "N/A"
        st.metric("정답률", correct_rate)
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["성적 추이", "과목별 분석", "최근 피드백"])
    
    # 탭 1: 성적 추이
    with tab1:
        st.subheader("점수 변화 추이")
        
        if progress_data['scores_by_date']:
            # 데이터프레임 생성
            scores_df = pd.DataFrame(progress_data['scores_by_date'])
            scores_df['date'] = pd.to_datetime(scores_df['date'])
            scores_df = scores_df.sort_values('date')
            
            # streamlit 내장 차트 사용
            st.line_chart(scores_df.set_index('date')['score'])
            
            # 점수 데이터 테이블로 표시
            st.subheader("점수 데이터")
            display_df = scores_df.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d %H:%M')
            display_df.columns = ['날짜', '점수', '문제 제목']
            st.dataframe(display_df)
        else:
            st.info("아직 첨삭 완료된 답안이 없습니다.")
    
    # 탭 2: 과목별 분석
    with tab2:
        st.subheader("과목별 성적 분석")
        
        if progress_data['subject_performance']:
            # 데이터프레임 생성
            subject_data = []
            for subject, data in progress_data['subject_performance'].items():
                subject_data.append({
                    '과목': subject,
                    '문제 수': data['count'],
                    '평균 점수': data.get('average_score', 0),
                    '정답률': data.get('correct_rate', 0)
                })
            
            subject_df = pd.DataFrame(subject_data)
            
            # streamlit 내장 차트 사용
            st.bar_chart(subject_df.set_index('과목')['평균 점수'])
            st.bar_chart(subject_df.set_index('과목')['정답률'])
            
            # 과목별 데이터 테이블
            st.subheader("과목별 데이터")
            display_df = subject_df.copy()
            display_df['평균 점수'] = display_df['평균 점수'].round(1)
            display_df['정답률'] = display_df['정답률'].round(1).astype(str) + '%'
            st.dataframe(display_df)
        else:
            st.info("아직 과목별 분석 데이터가 없습니다.")
    
    # 탭 3: 최근 피드백
    with tab3:
        st.subheader("최근 받은 피드백")
        
        if progress_data['recent_feedback']:
            for i, feedback in enumerate(progress_data['recent_feedback']):
                with st.expander(f"{feedback['problem_title']} (점수: {feedback['score']})"):
                    st.write(f"**날짜:** {feedback['date']}")
                    st.write("**피드백 내용:**")
                    st.write(feedback['feedback'])
        else:
            st.info("아직 받은 피드백이 없습니다.")
    
    # 제출 이력
    st.subheader("전체 제출 이력")
    
    # 학생의 모든 제출 이력 가져오기
    submissions = dashboard.get_student_submissions(username)
    
    if submissions:
        # 데이터프레임 생성
        submissions_df = pd.DataFrame([
            {
                '제출일': s.get('submitted_at', ''),
                '문제 제목': s.get('problem_title', ''),
                '첨삭 여부': '완료' if 'feedback' in s and s['feedback'] else '대기중',
                '점수': s.get('score', '-'),
                '정답 여부': '정답' if s.get('is_correct', False) else '오답'
            } for s in submissions
        ])
        
        # 정렬 (최신순)
        submissions_df = submissions_df.sort_values('제출일', ascending=False)
        
        # 테이블 표시
        st.dataframe(submissions_df)
    else:
        st.info("아직 제출한 답안이 없습니다.")

if __name__ == "__main__":
    app() 