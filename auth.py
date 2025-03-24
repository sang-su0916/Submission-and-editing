import streamlit as st
import os
import json
import pandas as pd

def check_password():
    """
    간단한 비밀번호 확인 함수
    Returns:
        tuple: (인증 여부, 사용자 유형, 사용자 이름)
    """
    # 사용자 데이터 파일 경로
    users_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')
    
    # 사용자 데이터 파일이 없으면 생성
    if not os.path.exists(users_file):
        default_users = {
            "teacher1": {"password": "teacher1", "type": "선생님", "name": "김선생"},
            "student1": {"password": "student1", "type": "학생", "name": "이학생"}
        }
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)
    
    # 사용자 데이터 로드
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # 로그인 폼
    st.subheader("로그인")
    username = st.text_input("사용자 ID")
    password = st.text_input("비밀번호", type="password")
    
    if st.button("로그인"):
        if username in users and users[username]["password"] == password:
            st.success(f"환영합니다, {users[username]['name']}님!")
            return True, users[username]["type"], users[username]["name"]
        else:
            st.error("사용자 ID 또는 비밀번호가 잘못되었습니다.")
    
    return False, None, None
