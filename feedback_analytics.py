import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import json
from datetime import datetime, timedelta
import numpy as np

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_css

class FeedbackAnalytics:
    """
    첨삭 결과 분석 및 시각화 클래스
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
    
    def get_student_progress(self, student_id):
        """학생의 진행 상황 분석"""
        # 학생의 제출 답안 필터링
        student_submissions = [s for s in self.feedback_data if s['student_id'] == student_id]
        
        if not student_submissions:
            return None
        
        # 첨삭 완료된 답안만 필터링
        graded_submissions = [s for s in student_submissions if 'score' in s]
        
        if not graded_submissions:
            return {
                'total_submissions': len(student_submissions),
                'graded_submissions': 0,
                'average_score': 0,
                'scores_by_date': [],
                'recent_feedback': []
            }
        
        # 날짜별 점수 추출
        scores_by_date = []
        for submission in sorted(graded_submissions, key=lambda x: x.get('feedback_at', '')):
            if 'feedback_at' in submission and 'score' in submission:
                scores_by_date.append({
                    'date': submission['feedback_at'],
                    'score': submission['score'],
                    'problem_title': submission['problem_title']
                })
        
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
        
        return {
            'total_submissions': len(student_submissions),
            'graded_submissions': len(graded_submissions),
            'average_score': sum(s.get('score', 0) for s in graded_submissions) / len(graded_submissions),
            'scores_by_date': scores_by_date,
            'recent_feedback': recent_feedback
        }
    
    def get_teacher_analytics(self):
        """교사용 분석 데이터"""
        if not self.feedback_data:
            return None
        
        # 첨삭 완료된 답안만 필터링
        graded_submissions = [s for s in self.feedback_data if 'score' in s]
        
        if not graded_submissions:
            return {
                'total_submissions': len(self.feedback_data),
                'graded_submissions': 0,
                'average_score': 0,
                'submissions_by_date': [],
                'score_distribution': []
            }
        
        # 날짜별 제출 수 계산
        submissions_by_date = {}
        for submission in self.feedback_data:
            date = submission['submitted_at'].split()[0]  # YYYY-MM-DD 부분만 추출
            if date in submissions_by_date:
                submissions_by_date[date] += 1
            else:
                submissions_by_date[date] = 1
        
        # 점수 분포 계산
        score_ranges = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81-100': 0
        }
        
        for submission in graded_submissions:
            score = submission.get('score', 0)
            if 0 <= score <= 20:
                score_ranges['0-20'] += 1
            elif 21 <= score <= 40:
                score_ranges['21-40'] += 1
            elif 41 <= score <= 60:
                score_ranges['41-60'] += 1
            elif 61 <= score <= 80:
                score_ranges['61-80'] += 1
            else:
                score_ranges['81-100'] += 1
        
        return {
            'total_submissions': len(self.feedback_data),
            'graded_submissions': len(graded_submissions),
            'average_score': sum(s.get('score', 0) for s in graded_submissions) / len(graded_submissions),
            'submissions_by_date': [{'date': k, 'count': v} for k, v in submissions_by_date.items()],
            'score_distribution': [{'range': k, 'count': v} for k, v in score_ranges.items()]
        }

def app():
    # CSS 로드
    load_css()
    
    st.title("첨삭 결과 분석")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # FeedbackAnalytics 인스턴스 생성
    feedback_analytics = FeedbackAnalytics(data_dir)
    
    # 사용자 역할 확인 (세션에서)
    user_role = st.session_state.get('role', 'student')  # 기본값은 학생
    
    if user_role == 'teacher':
        # 교사용 분석 대시보드
        st.header("교사용 분석 대시보드")
        
        # 분석 데이터 가져오기
        analytics_data = feedback_analytics.get_teacher_analytics()
        
        if analytics_data:
            # 기본 통계 표시
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 제출 답안 수", analytics_data['total_submissions'])
            
            with col2:
                st.metric("첨삭 완료 답안 수", analytics_data['graded_submissions'])
            
            with col3:
                st.metric("평균 점수", f"{analytics_data['average_score']:.1f}")
            
            # 날짜별 제출 수 그래프
            st.subheader("날짜별 제출 답안 수")
            
            if analytics_data['submissions_by_date']:
                # 데이터프레임 생성
                date_df = pd.DataFrame(analytics_data['submissions_by_date'])
                date_df['date'] = pd.to_datetime(date_df['date'])
                date_df = date_df.sort_values('date')
                
                # 그래프 생성
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(date_df['date'], date_df['count'], color='skyblue')
                ax.set_xlabel('날짜')
                ax.set_ylabel('제출 수')
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                # x축 날짜 포맷 설정
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig)
            else:
                st.info("제출 데이터가 없습니다.")
            
            # 점수 분포 그래프
            st.subheader("점수 분포")
            
            if analytics_data['score_distribution']:
                # 데이터프레임 생성
                score_df = pd.DataFrame(analytics_data['score_distribution'])
                
                # 그래프 생성
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(score_df['range'], score_df['count'], color='lightgreen')
                ax.set_xlabel('점수 범위')
                ax.set_ylabel('학생 수')
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                plt.tight_layout()
                
                st.pyplot(fig)
            else:
                st.info("점수 데이터가 없습니다.")
        else:
            st.info("분석할 데이터가 없습니다.")
    
    else:  # 학생 역할
        # 학생용 진행 상황 대시보드
        st.header("나의 학습 진행 상황")
        
        # 현재 사용자 ID 가져오기 (세션에서)
        current_user = st.session_state.get('username', '익명')
        
        # 학생 진행 상황 데이터 가져오기
        progress_data = feedback_analytics.get_student_progress(current_user)
        
        if progress_data:
            # 기본 통계 표시
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 제출 답안 수", progress_data['total_submissions'])
            
            with col2:
                st.metric("첨삭 완료 답안 수", progress_data['graded_submissions'])
            
            with col3:
                st.metric("평균 점수", f"{progress_data['average_score']:.1f}" if progress_data['graded_submissions'] > 0 else "N/A")
            
            # 점수 추이 그래프
            st.subheader("점수 추이")
            
            if progress_data['scores_by_date']:
                # 데이터프레임 생성
                scores_df = pd.DataFrame(progress_data['scores_by_date'])
                scores_df['date'] = pd.to_datetime(scores_df['date'])
                scores_df = scores_df.sort_values('date')
                
                # 그래프 생성
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(scores_df['date'], scores_df['score'], marker='o', linestyle='-', color='blue')
                
                # 문제 제목 툴팁 추가
                for i, row in scores_df.iterrows():
                    ax.annotate(row['problem_title'],
                                (row['date'], row['score']),
                                textcoords="offset points",
                                xytext=(0, 10),
                                ha='center',
                                fontsize=8,
                                alpha=0.7)
                
                ax.set_xlabel('날짜')
                ax.set_ylabel('점수')
                ax.set_ylim(0, 100)
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # x축 날짜 포맷 설정
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig)
            else:
                st.info("아직 첨삭 완료된 답안이 없습니다.")
            
            # 최근 피드백 내용
            st.subheader("최근 받은 피드백")
            
            if progress_data['recent_feedback']:
                for i, feedback in enumerate(progress_data['recent_feedback']):
                    with st.expander(f"{feedback['problem_title']} (점수: {feedback['score']})"):
                        st.write(f"**날짜:** {feedback['date']}")
                        st.write("**피드백 내용:**")
                        st.write(feedback['feedback'])
            else:
                st.info("아직 받은 피드백이 없습니다.")
        else:
            st.info("아직 제출한 답안이 없습니다.")

if __name__ == "__main__":
    app()
