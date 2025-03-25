import streamlit as st

def load_css():
    """Load custom CSS styles"""
    st.markdown("""
        <style>
            /* 기본 버튼 스타일 */
            .stButton>button {
                width: 100%;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 8px;
                color: #495057;
                font-weight: 500;
                transition: all 0.3s ease;
                margin-bottom: 10px;
            }
            
            /* 버튼 호버 효과 */
            .stButton>button:hover {
                background-color: #4B89DC;
                color: white;
                border-color: #4B89DC;
            }
            
            /* 체크박스 스타일 */
            .stCheckbox>div>div>label {
                background-color: #f8f9fa;
                padding: 10px 15px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                font-weight: 500;
                margin-right: 10px;
                transition: all 0.3s ease;
            }
            
            .stCheckbox>div>div>label:hover {
                background-color: #e9ecef;
            }
            
            /* 메뉴 라디오 버튼 스타일 */
            div.row-widget.stRadio > div {
                display: flex;
                flex-direction: column;
            }
            
            div.row-widget.stRadio > div[role="radiogroup"] > label {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 12px 15px;
                margin: 0.2rem 0;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid #e9ecef;
            }
            
            div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
                background-color: #e9ecef;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
                background-color: #4B89DC;
            }
            
            /* 폼 입력 스타일 */
            .stTextInput>div>div>input {
                width: 100%;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            .stSelectbox>div>div>select {
                width: 100%;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            /* 탭 스타일 */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                border-radius: 4px 4px 0px 0px;
                padding: 10px 16px;
                background-color: #f8f9fa;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: #4B89DC !important;
                color: white !important;
            }
            
            /* 메뉴 컨테이너 스타일 */
            .menu-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-bottom: 20px;
            }
            
            /* 메뉴 버튼 스타일 */
            .menu-button {
                padding: 12px 15px;
                background-color: #f8f9fa;
                color: #495057;
                border-radius: 8px;
                border: 1px solid #dee2e6;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .menu-button:hover {
                background-color: #e9ecef;
                box-shadow: 0 2px 5px rgba(0,0,0,0.15);
            }
            
            .menu-button.active {
                background-color: #4B89DC;
                color: white;
                border-color: #4B89DC;
                box-shadow: 0 2px 5px rgba(75,137,220,0.3);
            }
            
            /* 사이드바 네비게이션 링크 숨기기 */
            [data-testid="stSidebar"] ul {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

def get_subject_options():
    """
    과목 옵션을 반환하는 함수
    """
    return ["영어", "수학"]

def get_difficulty_options():
    """
    난이도 옵션을 반환하는 함수
    """
    return ["초급", "중급", "고급"]

def get_problem_type_options(subject):
    """
    과목별 문제 유형 옵션을 반환하는 함수
    
    Args:
        subject (str): 과목명
        
    Returns:
        list: 문제 유형 목록
    """
    if subject == "영어":
        return ["어휘", "문법", "독해", "작문", "듣기"]
    elif subject == "수학":
        return ["대수", "기하", "미적분", "확률과 통계", "수열"]
    else:
        return []

def save_dataframe(df, file_path):
    """
    데이터프레임을 CSV 파일로 저장하는 함수
    
    Args:
        df (pandas.DataFrame): 저장할 데이터프레임
        file_path (str): 저장할 파일 경로
    """
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def load_dataframe(file_path, default_df=None):
    """
    CSV 파일에서 데이터프레임을 로드하는 함수
    
    Args:
        file_path (str): 로드할 파일 경로
        default_df (pandas.DataFrame, optional): 파일이 없을 경우 반환할 기본 데이터프레임
        
    Returns:
        pandas.DataFrame: 로드된 데이터프레임
    """
    import os
    import pandas as pd
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path, encoding='utf-8-sig')
    else:
        return default_df if default_df is not None else pd.DataFrame()

def load_env_from_config():
    """
    config.json 파일에서 환경 변수를 로드하는 함수
    """
    import os
    import json
    
    try:
        # 데이터 디렉토리 경로
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        config_file = os.path.join(data_dir, 'config.json')
        
        # config.json 파일이 있는지 확인
        if os.path.exists(config_file):
            try:
                # 설정 파일 로드
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 환경 변수 설정
                for key, value in config_data.items():
                    if value and key not in os.environ:
                        os.environ[key] = value
                
                return True
            except Exception as e:
                print(f"환경 변수 로드 중 오류 발생: {str(e)}")
        return False
    except Exception as e:
        print(f"설정 로드 중 오류 발생: {str(e)}")
        return False
