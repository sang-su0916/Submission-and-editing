import streamlit as st
import pandas as pd
import os
import sys
import json
import uuid
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_css

class ProblemSolvingSystem:
    """
    학생들이 문제를 풀고 제출하는 시스템
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.problems_file = os.path.join(data_dir, 'problems.json')
        self.feedback_file = os.path.join(data_dir, 'feedback_data.json')
        os.makedirs(data_dir, exist_ok=True)
        self.problems_data = self._load_problems_data()
        self.feedback_data = self._load_feedback_data()
    
    def _load_problems_data(self):
        """문제 데이터 로드"""
        if os.path.exists(self.problems_file):
            try:
                with open(self.problems_file, 'r', encoding='utf-8') as f:
                    problems = json.load(f)
                    return problems
            except Exception as e:
                st.error(f"문제 데이터 로드 중 오류 발생: {e}")
                return []
        return []
    
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
    
    def _save_feedback_data(self):
        """피드백 데이터 저장"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"피드백 데이터 저장 중 오류 발생: {e}")
            return False
    
    def get_available_problems(self, user_id=None):
        """학생이 풀 수 있는 문제 목록"""
        # 현재는 모든 문제를 반환, 추후 학생 수준별 필터링 가능
        return self.problems_data
    
    def get_problem_by_id(self, problem_id):
        """ID로 문제 정보 가져오기"""
        for problem in self.problems_data:
            if problem['id'] == problem_id:
                return problem
        return None
    
    def get_submitted_problems(self, student_id):
        """학생이 제출한 문제 목록"""
        return [submission for submission in self.feedback_data if submission.get('student_id') == student_id]
    
    def is_problem_submitted(self, student_id, problem_id):
        """이미 제출한 문제인지 확인"""
        for submission in self.feedback_data:
            if submission.get('student_id') == student_id and submission.get('problem_id') == problem_id:
                return True
        return False
    
    def submit_answer(self, submission_data):
        """학생 답안 제출"""
        submission_id = str(uuid.uuid4())
        submission_data['submission_id'] = submission_id
        submission_data['submitted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submission_data['status'] = 'pending'  # 첨삭 대기 상태
        
        # 문제 정보 가져오기
        problem = self.get_problem_by_id(submission_data['problem_id'])
        if problem:
            submission_data['problem_title'] = problem.get('title', '')
            submission_data['subject'] = problem.get('subject', '')
            submission_data['problem_type'] = problem.get('problem_type', '')
            
            # 자동 채점 (객관식이나 단답형인 경우)
            if problem.get('problem_type') in ['객관식', '단답형']:
                if str(submission_data['answer']).strip() == str(problem.get('answer')).strip():
                    submission_data['is_correct'] = True
                    submission_data['auto_score'] = 100
                else:
                    submission_data['is_correct'] = False
                    submission_data['auto_score'] = 0
        
        # 피드백 데이터에 추가
        self.feedback_data.append(submission_data)
        self._save_feedback_data()
        
        return submission_id
    
    def get_subjects(self):
        """과목 목록 가져오기"""
        subjects = set()
        for problem in self.problems_data:
            if 'subject' in problem and problem['subject']:
                subjects.add(problem['subject'])
        return sorted(list(subjects))
    
    def get_problem_types(self):
        """문제 유형 목록 가져오기"""
        problem_types = set()
        for problem in self.problems_data:
            if 'problem_type' in problem and problem['problem_type']:
                problem_types.add(problem['problem_type'])
        return sorted(list(problem_types))

def app():
    # CSS 로드
    load_css()
    
    st.title("문제 풀기")
    
    # 스타일 추가
    st.markdown("""
    <style>
    .problem-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .problem-header {
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 15px;
        margin-bottom: 15px;
    }
    .problem-content {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .option-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        transition: all 0.2s;
    }
    .option-card:hover {
        border-color: #4285F4;
        box-shadow: 0 2px 5px rgba(66, 133, 244, 0.2);
    }
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .stRadio label {
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        width: 100%;
        margin-bottom: 5px;
    }
    h3 {
        color: #4285F4;
        margin-top: 30px;
    }
    .submitted-answer {
        background-color: #e8f0fe;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #4285F4;
        margin-bottom: 20px;
    }
    .answer-section {
        margin-top: 20px;
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .subject-info {
        display: inline-block;
        background-color: #e8f0fe;
        color: #1967d2;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9em;
        margin-right: 8px;
    }
    .difficulty-info {
        display: inline-block;
        background-color: #fef0e8;
        color: #d26919;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9em;
        margin-right: 8px;
    }
    .type-info {
        display: inline-block;
        background-color: #e8f5e9;
        color: #1b873b;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # ProblemSolvingSystem 인스턴스 생성
    problem_system = ProblemSolvingSystem(data_dir)
    
    # 사용자 정보 확인 (세션에서)
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', '익명')
    user_role = st.session_state.get('role', 'student')
    
    # 로그인 상태와 학생인지 확인
    if not st.session_state.get('logged_in', False) or user_role != 'student':
        st.error("학생으로 로그인해야 이 페이지를 볼 수 있습니다.")
        return
    
    # 세션 상태 초기화
    if 'selected_problem_id' not in st.session_state:
        st.session_state.selected_problem_id = None
    
    if 'problem_submitted' not in st.session_state:
        st.session_state.problem_submitted = False
    
    # 필터링 영역을 확장 가능한 컨테이너로 변경
    with st.expander("문제 필터링", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subject_filter = st.selectbox(
                "과목 선택",
                ["전체"] + problem_system.get_subjects(),
                key="subject_filter_solving"
            )
        
        with col2:
            problem_type_filter = st.selectbox(
                "문제 유형 선택",
                ["전체"] + problem_system.get_problem_types(),
                key="problem_type_filter_solving"
            )
        
        with col3:
            difficulty_filter = st.selectbox(
                "난이도 선택",
                ["전체", "초급", "중급", "고급"],
                key="difficulty_filter_solving"
            )
    
    # 이용 가능한 문제 목록
    available_problems = problem_system.get_available_problems(username)
    
    # 필터링 적용
    filtered_problems = []
    for problem in available_problems:
        if subject_filter != "전체" and problem.get('subject') != subject_filter:
            continue
        if problem_type_filter != "전체" and problem.get('problem_type') != problem_type_filter:
            continue
        if difficulty_filter != "전체" and problem.get('difficulty') != difficulty_filter:
            continue
        filtered_problems.append(problem)
    
    # 이미 제출한 문제인지 확인
    submitted_problem_ids = [sub.get('problem_id') for sub in problem_system.get_submitted_problems(username)]
    
    # 탭 생성
    tab1, tab2 = st.tabs(["문제 풀기", "제출 이력"])
    
    # 탭 1: 문제 풀기
    with tab1:
        if not filtered_problems:
            st.info("선택한 필터에 해당하는 문제가 없습니다.")
        else:
            # 문제 선택 옵션 생성
            problem_options = []
            for problem in filtered_problems:
                status = " [✓ 제출완료]" if problem.get('id') in submitted_problem_ids else ""
                problem_options.append(f"{problem.get('title')}{status}")
            
            selected_problem_display = st.selectbox("문제 선택", problem_options, key="problem_selector")
            
            # 실제 문제 객체 찾기
            selected_index = problem_options.index(selected_problem_display)
            selected_problem = filtered_problems[selected_index]
            st.session_state.selected_problem_id = selected_problem.get('id')
            
            # 선택된 문제 표시 (카드 형태로 개선)
            st.markdown(f"""
            <div class="problem-card">
                <div class="problem-header">
                    <h2>{selected_problem.get('title')}</h2>
                    <div>
                        <span class="subject-info">{selected_problem.get('subject', '-')}</span>
                        <span class="type-info">{selected_problem.get('problem_type', '-')}</span>
                        <span class="difficulty-info">{selected_problem.get('difficulty', '-')}</span>
                    </div>
                </div>
                <h3>문제 내용</h3>
                <div class="problem-content">
                    {selected_problem.get('content', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 이미 제출한 문제인지 확인
            is_submitted = problem_system.is_problem_submitted(username, selected_problem.get('id'))
            
            if is_submitted:
                st.warning("이미 제출한 문제입니다. 제출 이력 탭에서 확인할 수 있습니다.")
                
                # 기존 제출 정보 표시
                for submission in problem_system.get_submitted_problems(username):
                    if submission.get('problem_id') == selected_problem.get('id'):
                        st.markdown(f"""
                        <div class="answer-section">
                            <h3>제출했던 답안</h3>
                            <div class="submitted-answer">
                                {submission.get('answer', '')}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if 'feedback' in submission:
                            st.markdown(f"""
                            <h3>첨삭 내용</h3>
                            <div class="submitted-answer">
                                {submission.get('feedback', '')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if 'score' in submission:
                                st.metric("점수", submission.get('score', 0))
                        else:
                            st.info("아직 첨삭이 완료되지 않았습니다.")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        break
            else:
                # 답안 입력 영역 개선
                st.markdown("""
                <div class="answer-section">
                    <h3>답안 작성</h3>
                """, unsafe_allow_html=True)
                
                # 문제 유형에 따라 답안 입력 방식 변경
                answer_input = ""
                
                if selected_problem.get('problem_type') == '객관식':
                    options = selected_problem.get('options', '1,2,3,4,5').split(',')
                    options = [opt.strip() for opt in options]
                    answer_input = st.radio(
                        "정답 선택",
                        options,
                        key="answer_radio"
                    )
                else:
                    answer_input = st.text_area(
                        "답안 작성",
                        key="answer_text",
                        height=200
                    )
                
                # 제출 버튼
                if st.button("답안 제출", key="submit_answer"):
                    if not answer_input:
                        st.error("답안을 입력해주세요.")
                    else:
                        # 제출 데이터 생성
                        submission_data = {
                            'student_id': username,
                            'problem_id': selected_problem.get('id'),
                            'answer': answer_input,
                            'submitted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # 답안 제출
                        submission_id = problem_system.submit_answer(submission_data)
                        
                        if submission_id:
                            st.success("답안이 성공적으로 제출되었습니다.")
                            st.session_state.problem_submitted = True
                            st.rerun()
                        else:
                            st.error("답안 제출 중 오류가 발생했습니다.")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # 탭 2: 제출 이력
    with tab2:
        st.subheader("제출한 문제 목록")
        
        # 제출한 문제 목록 가져오기
        submissions = problem_system.get_submitted_problems(username)
        
        if not submissions:
            st.info("아직 제출한 문제가 없습니다.")
        else:
            # 제출 목록을 DataFrame으로 변환하여 표시
            submission_data = []
            for sub in submissions:
                status = "첨삭 완료" if "feedback" in sub else "첨삭 대기"
                score = sub.get("score", "N/A") if "score" in sub else "N/A"
                
                submission_data.append({
                    '제목': sub.get('problem_title', ''),
                    '과목': sub.get('subject', ''),
                    '제출일': sub.get('submitted_at', ''),
                    '상태': status,
                    '점수': score
                })
            
            df = pd.DataFrame(submission_data)
            
            # 데이터프레임 스타일링 적용
            st.markdown("""
            <style>
            .dataframe-container {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True) 