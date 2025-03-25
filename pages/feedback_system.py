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

class ProblemModel:
    """
    문제 데이터 관리 클래스
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.problems_file = os.path.join(data_dir, 'problems.json')
        self.problems_data = self._load_problems_data()
    
    def _load_problems_data(self):
        """문제 데이터 로드"""
        if os.path.exists(self.problems_file):
            with open(self.problems_file, 'r', encoding='utf-8') as f:
                return pd.DataFrame(json.load(f))
        return pd.DataFrame(columns=['id', 'title', 'content', 'answer', 'category', 'difficulty', 'created_at', 'created_by'])
    
    def get_problem_by_id(self, problem_id):
        """ID로 문제 조회"""
        if problem_id in self.problems_data['id'].values:
            return self.problems_data[self.problems_data['id'] == problem_id].iloc[0].to_dict()
        return None
    
    def get_unique_values(self, column):
        """특정 컬럼의 고유값 목록 반환"""
        if column in self.problems_data.columns:
            return sorted(self.problems_data[column].unique().tolist())
        return []
    
    def filter_problems(self, **kwargs):
        """문제 필터링"""
        filtered_data = self.problems_data.copy()
        for key, value in kwargs.items():
            if key in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[key] == value]
        return filtered_data

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

def app(show_problem_solving=False, show_feedback_check=False):
    # CSS 로드
    load_css()
    
    st.title("첨삭 시스템")
    
    # 로그인 확인
    is_logged_in = st.session_state.get('logged_in', False)
    
    if not is_logged_in:
        st.error("이 페이지에 접근하려면 로그인이 필요합니다.")
        st.info("로그인 페이지로 이동하여 로그인해주세요.")
        return
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # ProblemModel 인스턴스 생성
    problem_model = ProblemModel(data_dir)
    
    # FeedbackModel 인스턴스 생성
    feedback_model = FeedbackModel(data_dir)
    
    # 사용자 역할 확인 (세션에서)
    user_role = st.session_state.get('role', 'student')  # 기본값은 학생
    
    # 현재 메뉴 확인 (메인 앱에서 전달)
    current_menu = st.session_state.get('menu', '')
    
    # 요청된 탭만 표시 (헤더 페이지에서 링크 이동용)
    if show_problem_solving:
        # 문제 풀기 탭만 표시
        st.header("문제 풀기")
        show_problem_solving_tab(problem_model, feedback_model)
    elif show_feedback_check:
        # 첨삭 확인 탭만 표시
        st.header("첨삭 확인")
        show_feedback_check_tab(feedback_model, problem_model)
    else:
        # 둘 다 표시 (기존 방식)
        tab1, tab2 = st.tabs(["문제 풀기", "첨삭 확인"])
        
        # 탭 1: 문제 풀기
        with tab1:
            st.header("문제 풀기")
            show_problem_solving_tab(problem_model, feedback_model)
        
        # 탭 2: 첨삭 확인
        with tab2:
            st.header("첨삭 확인")
            show_feedback_check_tab(feedback_model, problem_model)

def show_problem_solving_tab(problem_model, feedback_model):
    """문제 풀기 탭 표시 함수"""
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
    
    # 시험 모드 체크
    if 'test_mode' not in st.session_state:
        st.session_state.test_mode = False
        
    # 일반 모드일 때 보여줄 내용
    if not st.session_state.test_mode:
        if not filtered_problems.empty:
            # 문제 선택 및 개별 문제 풀이 부분 제거하고 직접 시험 모드로 연결
            st.markdown("---")
            st.subheader("문제 풀기")
            st.write("선택한 조건에 맞는 문제를 풀어볼 수 있습니다.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                problem_count = st.number_input("문제 수", min_value=1, max_value=10, value=3)
            
            with col2:
                time_limit = st.number_input("시간 제한 (분)", min_value=5, max_value=120, value=30)
            
            # 문제 필터링 (필터 옵션 적용)
            all_problems = filtered_problems.to_dict('records')
            
            # 시험 시작 버튼
            if st.button("문제 풀기 시작"):
                # 문제 수가 필터링된 문제보다 많으면 조정
                actual_count = min(problem_count, len(all_problems))
                
                if actual_count > 0:
                    # 충분한 문제가 있는지 확인
                    if len(all_problems) < actual_count:
                        st.error(f"선택한 조건에 맞는 문제가 부족합니다. 현재 {len(all_problems)}개의 문제만 사용 가능합니다.")
                    else:
                        try:
                            # 랜덤 샘플링 전에 문제 ID별로 그룹화하여 중복 제거
                            unique_problems = {}
                            for p in all_problems:
                                if p['id'] not in unique_problems:
                                    unique_problems[p['id']] = p
                            
                            # 고유한 문제 목록에서 샘플링
                            import random
                            available_problems = list(unique_problems.values())
                            
                            # 샘플 수가 가용 문제보다 많으면 조정
                            actual_count = min(actual_count, len(available_problems))
                            
                            # 무작위 선택
                            selected_problems = random.sample(available_problems, actual_count)
                            
                            # 세션 상태 설정
                            st.session_state.test_mode = True
                            st.session_state.selected_problems = selected_problems
                            st.session_state.student_answers = {p['id']: "" for p in selected_problems}
                            st.session_state.start_time = datetime.now()
                            st.session_state.time_limit = time_limit
                            st.session_state.test_completed = False
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"문제 선택 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("선택한 필터 조건에 맞는 문제가 없습니다.")
        
        # 시험 모드일 때 보여줄 내용
        else:
            st.warning("선택한 조건에 맞는 문제가 없습니다.")
    else:
        # 시험 모드 UI 표시
        # 현재 시간과 시작 시간의 차이를 계산
        current_time = datetime.now()
        elapsed_time = (current_time - st.session_state.start_time).total_seconds() / 60  # 분 단위
        remaining_time = max(0, st.session_state.time_limit - elapsed_time)
        
        # 남은 시간 표시
        time_col1, time_col2 = st.columns([3, 1])
        with time_col1:
            st.subheader("문제 풀이")
        with time_col2:
            if remaining_time > 0 and not st.session_state.test_completed:
                st.info(f"남은 시간: {int(remaining_time)}분 {int((remaining_time % 1) * 60)}초")
            else:
                st.warning("시간 종료")
        
        # 시간이 종료되었거나 제출 완료된 경우
        if remaining_time <= 0 and not st.session_state.test_completed:
            st.session_state.test_completed = True
            st.warning("시간이 종료되었습니다. 답안이 자동으로 제출되었습니다.")
            st.rerun()
        
        # 문제 풀기 진행 상태
        if not st.session_state.test_completed:
            answered_count = sum(1 for ans in st.session_state.student_answers.values() if ans.strip())
            total_count = len(st.session_state.selected_problems)
            st.progress(answered_count / total_count, f"풀이 진행: {answered_count}/{total_count} 문제")
        
        # 문제와 답안 입력 필드 표시
        for i, problem in enumerate(st.session_state.selected_problems):
            problem_id = problem['id']  # 고유 ID로 구분
            
            # 각 문제마다 명확한 스타일로 구분
            with st.container():
                # 박스 스타일 적용
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                <h3>문제 {i+1}: {problem['title']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # expander 대신 표시
                st.markdown(f"**과목:** {problem.get('subject', '')}")
                st.markdown(f"**유형:** {problem.get('problem_type', '')}")
                st.markdown(f"**난이도:** {problem.get('difficulty', '')}")
                
                st.markdown("### 문제")
                st.markdown(problem['content'])
                
                # 과목과 문제 유형에 따라 다른 응답 방식 제공
                problem_subject = problem.get('subject', '').lower()
                problem_type = problem.get('problem_type', '').lower()
                
                # 선택형 문제인지 확인
                has_choices = '선택지' in problem['content'] or '보기' in problem['content'] or any(line.strip().startswith(('1.', '2.', '3.', '4.', '5.')) for line in problem['content'].split('\n'))
                
                # 정답 입력 필드
                if not st.session_state.test_completed:
                    # 선택형 문제인 경우 체크박스로 표시
                    if has_choices:
                        # 선택지 추출 시도
                        choices = []
                        lines = problem['content'].split('\n')
                        for line in lines:
                            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                                choices.append(line.strip())
                        
                        # 선택지가 추출되었다면 체크박스로 표시
                        if choices:
                            st.markdown("### 답안 선택")
                            
                            # 현재 선택된 답안 가져오기
                            current_answer = st.session_state.student_answers.get(problem_id, "")
                            
                            # 각 선택지에 대한 체크박스 표시
                            selected_answer = None
                            selection_cols = st.columns(len(choices))
                            
                            for idx, (choice, col) in enumerate(zip(choices, selection_cols), 1):
                                # 현재 선택된 답안인지 확인
                                is_selected = current_answer == str(idx)
                                with col:
                                    # 체크박스 생성
                                    if st.checkbox(f"{idx}", 
                                                  value=is_selected, 
                                                  key=f"choice_cb_{problem_id}_{idx}"):
                                        selected_answer = str(idx)
                            
                            # 선택된 항목 표시
                            if selected_answer:
                                choice_text = choices[int(selected_answer)-1] if int(selected_answer) <= len(choices) else ""
                                st.success(f"선택한 답: {selected_answer}. {choice_text}")
                                st.session_state.student_answers[problem_id] = selected_answer
                            elif current_answer:
                                # 이전에 선택했던 답안이 있으면 표시
                                choice_idx = int(current_answer) - 1
                                if 0 <= choice_idx < len(choices):
                                    st.info(f"현재 선택: {current_answer}. {choices[choice_idx]}")
                        else:
                            # 선택지 추출 실패시 텍스트 입력으로 대체
                            student_answer = st.text_input(
                                "정답 입력 (번호만 입력)",
                                key=f"choice_text_{problem_id}_{i}"
                            )
                            st.session_state.student_answers[problem_id] = student_answer
                    # 수학 문제인 경우 LaTeX 지원 입력 필드
                    elif '수학' in problem_subject or '수학' in problem_type:
                        student_answer = st.text_area(
                            "정답 입력 (LaTeX 수식도 지원됩니다 - $수식$ 형태로 입력)",
                            key=f"math_{problem_id}_{i}",
                            height=100
                        )
                        st.session_state.student_answers[problem_id] = student_answer
                    # 일반 서술형 문제
                    else:
                        student_answer = st.text_area(
                            "정답 입력",
                            key=f"desc_{problem_id}_{i}",
                            height=100
                        )
                        st.session_state.student_answers[problem_id] = student_answer
                    
                    # 문제 구분선 추가
                    st.markdown("---")
                # 테스트 완료된 경우에만 정답과 해설 표시
                else:
                    # 학생의 답안 먼저 표시
                    student_ans = st.session_state.student_answers.get(problem_id, "")
                    
                    # 학생 답안 표시
                    st.markdown("### 내 답안")
                    st.markdown(student_ans)
                    
                    # 문제 구분선 추가
                    st.markdown("---")
        
        # 버튼 영역
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            if not st.session_state.test_completed:
                if st.button("모든 답안 제출"):
                    # 현재 사용자 ID 가져오기 (세션에서)
                    current_user = st.session_state.get('username', '익명')
                    
                    # 채점 및 점수 계산
                    correct_count = 0
                    total_count = len(st.session_state.selected_problems)
                    
                    # 모든 답안 제출 및 채점
                    for problem in st.session_state.selected_problems:
                        # 제출 ID 생성
                        submission_id = str(uuid.uuid4())
                        
                        # 제출 시간 추가
                        submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 학생 답안
                        student_ans = st.session_state.student_answers.get(problem['id'], "")
                        
                        # 정답 확인
                        correct_answer = problem['answer'].split('\n')[0].strip()  # 첫 줄만 정답으로 간주
                        is_correct = False
                        
                        # 선택형 문제인 경우 번호로 비교
                        has_choices = '선택지' in problem['content'] or '보기' in problem['content'] or any(line.strip().startswith(('1.', '2.', '3.', '4.', '5.')) for line in problem['content'].split('\n'))
                        if has_choices:
                            # 정답에서 번호만 추출 (예: "3. had known" -> "3")
                            correct_answer_num = correct_answer.split('.')[0].strip() if '.' in correct_answer else correct_answer
                            # 학생 답안에서 번호만 추출
                            student_ans_num = student_ans.split('.')[0].strip() if '.' in student_ans else student_ans
                            
                            # 번호만 비교
                            is_correct = student_ans_num == correct_answer_num
                        # 서술형 문제의 경우 키워드 포함 여부로 판단
                        else:
                            # 키워드 추출 (정답에서 중요 단어)
                            keywords = [word.strip() for word in correct_answer.split(',')]
                            # 학생 답안에 키워드가 포함되어 있는지 확인
                            keyword_match_count = sum(1 for kw in keywords if kw in student_ans)
                            # 50% 이상의 키워드가 포함되어 있으면 정답으로 간주
                            is_correct = keyword_match_count >= len(keywords) * 0.5
                        
                        if is_correct:
                            correct_count += 1
                        
                        # 제출 데이터 생성
                        submission_data = {
                            'id': submission_id,
                            'problem_id': problem['id'],
                            'problem_title': problem['title'],
                            'subject': problem.get('subject', '기타'),
                            'student_id': current_user,
                            'answer': student_ans,
                            'is_correct': is_correct,
                            'submitted_at': submitted_at
                        }
                        
                        # 첨삭 데이터 추가
                        feedback_model.add_submission(submission_data)
                        
                    # 테스트 완료 상태로 변경
                    st.session_state.test_completed = True
                    st.session_state.correct_count = correct_count
                    st.session_state.accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
                    
                    st.success("모든 답안이 제출되었습니다!")
                    st.rerun()
        
        with button_col2:
            if st.button("시험 종료하기"):
                # 시험 모드 종료 및 상태 초기화
                st.session_state.test_mode = False
                if 'selected_problems' in st.session_state:
                    del st.session_state.selected_problems
                if 'student_answers' in st.session_state:
                    del st.session_state.student_answers
                if 'start_time' in st.session_state:
                    del st.session_state.start_time
                if 'time_limit' in st.session_state:
                    del st.session_state.time_limit
                if 'test_completed' in st.session_state:
                    del st.session_state.test_completed
                
                st.success("시험이 종료되었습니다.")
                st.rerun()
        
        # 테스트 완료된 경우 결과 표시
        if st.session_state.test_completed:
            st.markdown("---")
            st.subheader("결과 요약")
            
            # 결과 통계 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총점", f"{st.session_state.correct_count}/{len(st.session_state.selected_problems)}")
            with col2:
                st.metric("정답 수", st.session_state.correct_count)
            with col3:
                st.metric("정확도", f"{st.session_state.accuracy:.1f}%")
            
            # 피드백 제공
            if st.session_state.accuracy < 60:
                st.warning("더 많은 연습이 필요합니다. 틀린 문제를 다시 확인해보세요.")
            elif st.session_state.accuracy < 80:
                st.info("좋은 성과입니다! 조금만 더 노력하면 더 좋은 결과를 얻을 수 있습니다.")
            else:
                st.success("훌륭한 결과입니다! 대부분의 문제를 정확하게 해결했습니다.")
            
            st.markdown("---")
            st.subheader("모든 문제 정답 및 해설")
            
            # 모든 문제의 정답과 해설 표시
            for i, problem in enumerate(st.session_state.selected_problems):
                # 각 문제 구분선 추가
                if i > 0:
                    st.markdown("---")
                
                st.markdown(f"## 문제 {i+1}: {problem['title']}")
                
                # 문제 내용과 정보 표시 (구분을 위해 카드 형태로)
                with st.container():
                    st.markdown(f"**과목:** {problem.get('subject', '')}")
                    st.markdown(f"**유형:** {problem.get('problem_type', '')}")
                    st.markdown(f"**난이도:** {problem.get('difficulty', '')}")
                    
                    # 문제 내용 표시
                    st.markdown("### 문제")
                    st.markdown(problem['content'])
                    
                    # 학생 답안
                    student_ans = st.session_state.student_answers.get(problem['id'], "")
                    st.markdown("### 내 답안")
                    st.markdown(student_ans if student_ans else "답변 없음")
                    
                    # 정답 확인
                    correct_answer = problem['answer'].split('\n')[0].strip()  # 첫 줄만 정답으로 간주
                    is_correct = False
                    
                    # 선택형 문제인 경우 번호로 비교
                    has_choices = '선택지' in problem['content'] or '보기' in problem['content'] or any(line.strip().startswith(('1.', '2.', '3.', '4.', '5.')) for line in problem['content'].split('\n'))
                    if has_choices:
                        # 정답에서 번호만 추출 (예: "3. had known" -> "3")
                        correct_answer_num = correct_answer.split('.')[0].strip() if '.' in correct_answer else correct_answer
                        # 학생 답안에서 번호만 추출
                        student_ans_num = student_ans.split('.')[0].strip() if '.' in student_ans else student_ans
                        
                        # 번호만 비교
                        is_correct = student_ans_num == correct_answer_num
                    # 서술형 문제의 경우 키워드 포함 여부로 판단
                    else:
                        # 키워드 추출 (정답에서 중요 단어)
                        keywords = [word.strip() for word in correct_answer.split(',')]
                        # 학생 답안에 키워드가 포함되어 있는지 확인
                        keyword_match_count = sum(1 for kw in keywords if kw in student_ans)
                        # 50% 이상의 키워드가 포함되어 있으면 정답으로 간주
                        is_correct = keyword_match_count >= len(keywords) * 0.5
                    
                    # 정답 여부 표시
                    if is_correct:
                        st.success("정답입니다!")
                    else:
                        st.error("오답입니다.")
                    
                    # 정답 및 해설 표시
                    st.markdown("### 정답 및 해설")
                    # 정답 표시
                    st.markdown(f"**정답:** {correct_answer}")
                    
                    # 해설 표시 (answer에 정답과 해설이 함께 있는 경우를 처리)
                    answer_parts = problem['answer'].split('\n')
                    if len(answer_parts) > 1:
                        # 첫 줄은 정답, 나머지는 해설로 간주
                        explanation = '\n'.join(answer_parts[1:])
                        if explanation.strip():
                            st.markdown("**해설:**")
                            st.markdown(explanation)
                    elif '해설' in problem['answer']:
                        # '해설:' 형식으로 되어 있는 경우
                        parts = problem['answer'].split('해설:')
                        if len(parts) > 1:
                            st.markdown("**해설:**")
                            st.markdown(parts[1].strip())
            else:
                        # 해설이 없을 경우, 예제 해설 제공
                        st.markdown("**해설:**")
                        st.markdown("제공된 해설이 없습니다. 선생님의 첨삭을 확인해주세요.")
                        
                        # 문제에 따른 자동 해설 생성 (기본적인 설명)
                        if '영어' in problem.get('subject', ''):
                            if '문법' in problem.get('problem_type', ''):
                                st.markdown("이 문제는 영어 문법 개념을 정확히 이해해야 풀 수 있습니다.")
                            elif '어휘' in problem.get('problem_type', ''):
                                st.markdown("이 문제는 문맥에 맞는 적절한 어휘 선택이 중요합니다.")
                            elif '독해' in problem.get('problem_type', ''):
                                st.markdown("이 문제는 글의 주요 내용과 논리적 흐름을 파악하는 것이 중요합니다.")

def show_feedback_check_tab(feedback_model, problem_model):
    """첨삭 확인 탭 표시 함수"""
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
                [s['id'] for s in user_submissions]
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
        else:
            st.info("첨삭 완료된 답안이 없습니다.")
    else:
        st.info("제출된 답안이 없습니다.")