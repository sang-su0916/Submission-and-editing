import streamlit as st
import pandas as pd
import os
import sys
import json
import uuid
from datetime import datetime
import io

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from models.problem_generator import ProblemGenerator, ProblemTemplateGenerator
    from utils.common import load_css
except ImportError as e:
    st.error(f"모듈을 가져오는 중 오류가 발생했습니다: {e}")
    st.info("필요한 모듈이 설치되어 있는지 확인해주세요.")

# 기존 ProblemModel을 LocalProblemModel로 변경하여 이름 충돌 방지
class LocalProblemModel:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.problems_file = os.path.join(data_dir, 'problems.json')
        os.makedirs(data_dir, exist_ok=True)  # 디렉토리가 없으면 생성
        self.problems_data = self._load_problems_data()
    
    def _load_problems_data(self):
        if os.path.exists(self.problems_file):
            with open(self.problems_file, 'r', encoding='utf-8') as f:
                try:
                    return pd.DataFrame(json.load(f))
                except:
                    return pd.DataFrame(columns=['id', 'title', 'content', 'answer', 'category', 'difficulty', 'created_at', 'created_by', 'subject', 'problem_type'])
        return pd.DataFrame(columns=['id', 'title', 'content', 'answer', 'category', 'difficulty', 'created_at', 'created_by', 'subject', 'problem_type'])
    
    def save_problem(self, problem_data):
        problem_id = str(uuid.uuid4())
        problem_data['id'] = problem_id
        problem_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if os.path.exists(self.problems_file):
            with open(self.problems_file, 'r', encoding='utf-8') as f:
                try:
                    problems = json.load(f)
                except:
                    problems = []
        else:
            problems = []
        
        problems.append(problem_data)
        
        with open(self.problems_file, 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        
        return problem_id
    
    def save_multiple_problems(self, problems_list):
        """여러 문제를 한 번에 저장"""
        if os.path.exists(self.problems_file):
            with open(self.problems_file, 'r', encoding='utf-8') as f:
                try:
                    existing_problems = json.load(f)
                except:
                    existing_problems = []
        else:
            existing_problems = []
        
        # 현재 시간
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 새 문제 목록에 ID와 시간 추가
        for problem in problems_list:
            problem['id'] = str(uuid.uuid4())
            if 'created_at' not in problem:
                problem['created_at'] = current_time
        
        # 기존 문제 목록에 새 문제 추가
        updated_problems = existing_problems + problems_list
        
        # 업데이트된 문제 목록 저장
        with open(self.problems_file, 'w', encoding='utf-8') as f:
            json.dump(updated_problems, f, ensure_ascii=False, indent=2)
        
        return len(problems_list)
    
    def get_unique_values(self, column):
        """특정 컬럼의 고유값 목록 반환"""
        if column in self.problems_data.columns:
            return sorted(self.problems_data[column].dropna().unique().tolist())
        return []
    
    def filter_problems(self, **kwargs):
        """문제 필터링"""
        filtered_data = self.problems_data.copy()
        for key, value in kwargs.items():
            if key in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[key] == value]
        return filtered_data

def app():
    # CSS 로드
    load_css()
    
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
    .content-area {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .option-box {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 15px;
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
    h3 {
        color: #4285F4;
        margin-top: 30px;
    }
    .submit-button {
        background-color: #4285F4;
        color: white;
        border-radius: 5px;
        margin-top: 20px;
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
    
    # 로그인 및 권한 확인
    is_logged_in = st.session_state.get('logged_in', False)
    user_role = st.session_state.get('role', '')
    
    if not is_logged_in:
        st.error("이 페이지에 접근하려면 로그인이 필요합니다.")
        st.info("로그인 페이지로 이동하여 로그인해주세요.")
        return
    
    if user_role not in ['admin', 'teacher']:
        st.error("이 페이지는 관리자 또는 선생님만 접근할 수 있습니다.")
        st.info("권한이 없는 페이지입니다. 다른 메뉴를 이용해주세요.")
        return
    
    st.title("문제 생성 설정")
    
    # 데이터 디렉토리 경로
    import os  # 명시적으로 os 모듈 다시 import
    
    current_file = os.path.abspath(__file__)
    parent_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(parent_dir)
    data_dir = os.path.join(project_root, 'data')
    
    # 디렉토리가 없으면 생성
    os.makedirs(data_dir, exist_ok=True)
    
    # ProblemModel 인스턴스 생성 - 클래스 이름 변경
    problem_model = LocalProblemModel(data_dir)
    
    # ProblemGenerator 인스턴스 생성
    problem_generator = ProblemGenerator()
    
    # ProblemTemplateGenerator 인스턴스 생성
    template_generator = ProblemTemplateGenerator()
    
    # 세션 상태 초기화
    if 'generated_problem' not in st.session_state:
        st.session_state.generated_problem = None
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["기존 문제 변형", "템플릿으로 새 문제 생성", "직접 문제 작성", "파일 업로드", "예제 문제 생성"])
    
    # 탭 1: 기존 문제 변형
    with tab1:
        st.header("기존 문제 변형")
        
        with st.expander("문제 필터링", expanded=True):
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
                    ["전체", "초급", "중급", "고급"],
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
            
            # 문제 내용 표시 (카드 형식으로 개선)
            st.markdown(f"""
            <div class="problem-card">
                <div class="problem-header">
                    <h2>{selected_problem['title']}</h2>
                    <div>
                        <span class="subject-info">{selected_problem.get('subject', '-')}</span>
                        <span class="type-info">{selected_problem.get('problem_type', '-')}</span>
                        <span class="difficulty-info">{selected_problem.get('difficulty', '-')}</span>
                    </div>
                </div>
                <h3>문제 내용</h3>
                <div class="content-area">
                    {selected_problem.get('content', '')}
                </div>
                <h3>정답</h3>
                <div class="content-area">
                    {selected_problem.get('answer', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 변형 옵션
            st.subheader("변형 옵션")
            
            col1, col2 = st.columns(2)
            
            with col1:
                variation_type = st.selectbox(
                    "변형 유형",
                    ["similar", "difficulty_up", "difficulty_down"],
                    format_func=lambda x: {
                        "similar": "유사 문제", 
                        "difficulty_up": "난이도 상향", 
                        "difficulty_down": "난이도 하향"
                    }.get(x, x),
                    key="variation_type"
                )
            
            # 변형 버튼
            if st.button("문제 변형하기", key="transform_problem_button"):
                with st.spinner("문제 변형 중..."):
                    # 문제 변형
                    transformed_problem = problem_generator.generate_problem(selected_problem, variation_type)
                    
                    if 'error' not in transformed_problem:
                        st.session_state.generated_problem = transformed_problem
                        
                        # 변형된 문제 표시
                        st.subheader("변형된 문제")
                        st.markdown(f"""
                        <div class="problem-card">
                            <div class="problem-header">
                                <h2>{transformed_problem['title']}</h2>
                                <div>
                                    <span class="subject-info">{transformed_problem.get('subject', '-')}</span>
                                    <span class="type-info">{transformed_problem.get('problem_type', '-')}</span>
                                    <span class="difficulty-info">{transformed_problem.get('difficulty', '-')}</span>
                                </div>
                            </div>
                            <h3>문제 내용</h3>
                            <div class="content-area">
                                {transformed_problem.get('content', '')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 저장 버튼
                        if st.button("변형된 문제 저장", key="save_transformed_problem"):
                            problem_id = problem_model.save_problem(transformed_problem)
                            st.success(f"변형된 문제가 저장되었습니다. (ID: {problem_id})")
                            st.rerun()
                    else:
                        st.error(transformed_problem['error'])
        else:
            st.info("선택한 필터 조건에 맞는 문제가 없습니다.")
    
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
                problem_types = ["어휘", "문법", "독해", "작문", "듣기", "말하기", "숙어", "단어", "빈칸채우기", "배열", "대화문"]
            else:  # 수학
                problem_types = ["대수", "기하", "미적분", "확률과 통계", "수열", "방정식", "부등식", "함수", "경우의 수", "도형", "벡터"]
            
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
                "템플릿 문제 내용",
                st.session_state.generated_problem['content'],
                height=200,
                key="edited_content_tab2"
            )
            st.session_state.generated_problem['content'] = edited_content
            
            st.write("**정답:**")
            
            # 정답 편집 가능
            edited_answer = st.text_area(
                "템플릿 정답",
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
                    
                    # 문제 데이터 준비
                    problem_data = {
                        'title': edited_title,
                        'subject': st.session_state.generated_problem['subject'],
                        'problem_type': st.session_state.generated_problem['problem_type'],
                        'difficulty': st.session_state.generated_problem['difficulty'],
                        'content': edited_content,
                        'answer': edited_answer,
                        'created_by': current_user
                    }
                    
                    # 문제 저장
                    problem_id = problem_model.save_problem(problem_data)
                    
                    if problem_id:
                        st.success("새 문제가 성공적으로 출제되었습니다!")
                        st.rerun()
    
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
                problem_types = ["어휘", "문법", "독해", "작문", "듣기", "말하기", "숙어", "단어", "빈칸채우기", "배열", "대화문"]
            else:  # 수학
                problem_types = ["대수", "기하", "미적분", "확률과 통계", "수열", "방정식", "부등식", "함수", "경우의 수", "도형", "벡터"]
            
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
                    
                    # 문제 데이터 준비
                    problem_data = {
                        'title': title,
                        'subject': subject,
                        'problem_type': problem_type,
                        'difficulty': difficulty,
                        'content': content,
                        'answer': answer,
                        'created_by': current_user
                    }
                    
                    # 문제 저장
                    problem_id = problem_model.save_problem(problem_data)
                    
                    if problem_id:
                        st.success("새 문제가 성공적으로 출제되었습니다!")
                        st.rerun()
            else:
                st.error("제목, 문제 내용, 정답을 모두 입력해주세요.")
    
    # 탭 4: 파일 업로드
    with tab4:
        st.header("문제 파일 업로드")
        
        # 파일 형식 안내
        st.info("""
        업로드할 파일은 다음 열을 포함해야 합니다:
        - title (필수): 문제 제목
        - content (필수): 문제 내용
        - option1 (선택): 보기1
        - option2 (선택): 보기2
        - option3 (선택): 보기3
        - option4 (선택): 보기4
        - answer (필수): 정답
        - subject (선택): 과목 (영어, 수학 등)
        - difficulty (선택): 난이도 (초급, 중급, 고급)
        - category (선택): 카테고리
        - tags (선택): 태그 (쉼표로 구분)
        """)
        
        # 파일 업로드
        uploaded_file = st.file_uploader("엑셀 또는 CSV 파일 업로드", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                # 파일 확장자 확인
                file_ext = uploaded_file.name.split('.')[-1].lower()
                
                if file_ext == 'csv':
                    # CSV 파일 읽기
                    df = pd.read_csv(uploaded_file)
                else:
                    # 엑셀 파일 읽기
                    try:
                        df = pd.read_excel(uploaded_file)
                    except Exception as e:
                        # 엑셀 파일 읽기 오류 발생 시
                        st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {str(e)}")
                        st.info("CSV 파일로 업로드하거나 필요한 라이브러리를 설치해 주세요.")
                        return
                
                # 필수 열 확인
                required_columns = ['title', 'content', 'answer']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"필수 열이 누락되었습니다: {', '.join(missing_columns)}")
                else:
                    # 파일 내용 미리보기
                    st.subheader("파일 내용 미리보기")
                    st.dataframe(df.head())
                    
                    # 데이터 검증
                    if df.isnull().values.any():
                        st.warning("일부 데이터에 누락된 값이 있습니다.")
                    
                    # 데이터 개수
                    st.write(f"총 {len(df)}개 문제가 발견되었습니다.")
                    
                    # 업로드 버튼
                    if st.button("문제 업로드", key="upload_button"):
                        with st.spinner("문제를 업로드하는 중..."):
                            # 현재 사용자 정보 가져오기 (세션에서)
                            current_user = st.session_state.get('username', '시스템')
                            
                            # 데이터프레임을 문제 리스트로 변환
                            problems_list = []
                            for _, row in df.iterrows():
                                problem = {
                                    'title': row['title'],
                                    'content': row['content'],
                                    'answer': row['answer'],
                                    'created_by': current_user,
                                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                
                                # 선택적 열 추가
                                optional_columns = [
                                    'option1', 'option2', 'option3', 'option4', 
                                    'subject', 'problem_type', 'difficulty', 
                                    'category', 'tags'
                                ]
                                
                                for col in optional_columns:
                                    if col in df.columns and not pd.isna(row.get(col, '')):
                                        problem[col] = row[col]
                                
                                problems_list.append(problem)
                            
                            # 문제 저장
                            saved_count = problem_model.save_multiple_problems(problems_list)
                            
                            st.success(f"{saved_count}개 문제가 성공적으로 저장되었습니다!")
            
            except Exception as e:
                st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
        
        # 샘플 파일 다운로드
        st.subheader("샘플 파일 다운로드")
        
        # 샘플 데이터 생성
        sample_data = {
            'title': ['영어 독해 문제 1', '수학 기하 문제 1'],
            'content': ['다음 글을 읽고 질문에 답하시오...', '다음 삼각형에서 각 A의 크기는...'],
            'option1': ['보기 1: 답은 3이다.', '보기 1: 30도'],
            'option2': ['보기 2: 답은 4이다.', '보기 2: 45도'],
            'option3': ['보기 3: 답은 5이다.', '보기 3: 60도'],
            'option4': ['보기 4: 답은 6이다.', '보기 4: 90도'],
            'answer': ['정답은 3번입니다.', '정답은 60도입니다.'],
            'subject': ['영어', '수학'],
            'problem_type': ['독해', '기하'],
            'difficulty': ['중급', '초급'],
            'category': ['학교시험', '수능대비'],
            'tags': ['독해,영어,지문해석', '기하,삼각형,각도']
        }
        
        sample_df = pd.DataFrame(sample_data)
        
        # CSV 샘플 파일
        csv_sample = sample_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV 샘플 파일 다운로드",
            data=csv_sample,
            file_name="sample_problems.csv",
            mime="text/csv"
        )
        
        # 엑셀 샘플 파일
        try:
            # openpyxl로 엑셀 파일 생성
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                sample_df.to_excel(writer, index=False, sheet_name='문제')
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="엑셀 샘플 파일 다운로드",
                data=excel_data,
                file_name="sample_problems.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.info("엑셀 파일 다운로드에 문제가 발생했습니다. CSV 파일을 다운로드하여 엑셀에서 열어주세요.")

    # 탭 5: 예제 문제 생성
    with tab5:
        st.header("예제 문제 생성")
        
        st.markdown("""
        <div class="problem-card">
            <div class="problem-header">
                <h2>예제 문제 생성</h2>
            </div>
            <p>기본 제공되는 예제 문제를 생성합니다. 다양한 과목과 유형의 문제가 포함되어 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("예제 문제 생성하기", key="generate_sample_problems"):
            # 예제 문제 생성
            from models.problem_generator import generate_sample_problems
            sample_problems = generate_sample_problems()
            
            # 예제 문제 저장
            count = problem_model.save_multiple_problems(sample_problems)
            
            st.success(f"{count}개의 예제 문제가 성공적으로 생성되었습니다.")
            
            # 생성된 문제 표시
            for problem in sample_problems:
                st.markdown(f"""
                <div class="problem-card">
                    <div class="problem-header">
                        <h2>{problem['title']}</h2>
                        <div>
                            <span class="subject-info">{problem.get('subject', '-')}</span>
                            <span class="type-info">{problem.get('problem_type', '-')}</span>
                            <span class="difficulty-info">{problem.get('difficulty', '-')}</span>
                        </div>
                    </div>
                    <h3>문제 내용</h3>
                    <div class="content-area">
                        {problem.get('content', '')}
                    </div>
                    <h3>정답</h3>
                    <div class="content-area">
                        {problem.get('answer', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 문제 백업 기능
    with st.expander("데이터 백업 및 내보내기"):
        st.header("문제 백업")
        
        # 문제 데이터 가져오기
        all_problems = problem_model.problems_data
        
        if not all_problems.empty:
            # 백업 형식 선택
            backup_format = st.radio(
                "백업 형식",
                ["CSV", "Excel"],
                horizontal=True
            )
            
            # 필터링 옵션
            col1, col2, col3 = st.columns(3)
            
            with col1:
                backup_subject = st.multiselect(
                    "과목 필터",
                    ["전체"] + problem_model.get_unique_values('subject'),
                    default=["전체"]
                )
            
            with col2:
                backup_type = st.multiselect(
                    "유형 필터",
                    ["전체"] + problem_model.get_unique_values('problem_type'),
                    default=["전체"]
                )
            
            with col3:
                backup_difficulty = st.multiselect(
                    "난이도 필터",
                    ["전체", "초급", "중급", "고급"],
                    default=["전체"]
                )
            
            # 필터링 적용
            filtered_data = all_problems.copy()
            
            if "전체" not in backup_subject:
                filtered_data = filtered_data[filtered_data['subject'].isin(backup_subject)]
                
            if "전체" not in backup_type:
                filtered_data = filtered_data[filtered_data['problem_type'].isin(backup_type)]
                
            if "전체" not in backup_difficulty:
                filtered_data = filtered_data[filtered_data['difficulty'].isin(backup_difficulty)]
            
            st.write(f"백업 가능한 문제: {len(filtered_data)}개")
            
            # 테이블 미리보기
            st.dataframe(
                filtered_data[['title', 'subject', 'problem_type', 'difficulty', 'created_at']].head(10),
                use_container_width=True
            )
            
            # 백업 파일 생성
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_format == "CSV":
                csv_data = filtered_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="CSV로 다운로드",
                    data=csv_data,
                    file_name=f"problem_backup_{now}.csv",
                    mime="text/csv"
                )
            else:  # Excel
                try:
                    # Excel 파일 생성
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        filtered_data.to_excel(writer, index=False, sheet_name='문제')
                    excel_data = buffer.getvalue()
                    
                    st.download_button(
                        label="Excel로 다운로드",
                        data=excel_data,
                        file_name=f"problem_backup_{now}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Excel 파일 생성 중 오류가 발생했습니다: {str(e)}")
                    st.info("CSV 형식으로 다운로드하거나 필요한 라이브러리를 설치해 주세요.")
        else:
            st.info("저장된 문제가 없습니다.")

if __name__ == "__main__":
    app()
