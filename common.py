import streamlit as st

def load_css():
    """
    CSS 스타일을 로드하는 함수
    """
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #424242;
        }
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #E3F2FD;
            border: 1px solid #90CAF9;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #E8F5E9;
            border: 1px solid #A5D6A7;
        }
        .warning-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #FFF8E1;
            border: 1px solid #FFE082;
        }
        .error-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #FFEBEE;
            border: 1px solid #FFCDD2;
        }
        .stButton>button {
            width: 100%;
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
