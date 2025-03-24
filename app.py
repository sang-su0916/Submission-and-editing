import streamlit as st
import os
import sys
import json
import hashlib
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_css

class UserAuth:
    """
    사용자 인증 관리 클래스
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.users_data = self._load_users_data()
    
    def _load_users_data(self):
        """사용자 데이터 로드"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _hash_password(self, password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """사용자 인증"""
        for user in self.users_data:
            if user['username'] == username and user['password'] == self._hash_password(password):
                return True, user
        return False, None
    
    def create_default_users(self):
        """기본 사용자 생성 (초기 설정용)"""
        # 사용자 파일이 없는 경우에만 실행
        if not os.path.exists(self.users_file):
            default_users = [
                {
                    'id': '1',
                    'username': 'admin',
                    'password': self._hash_password('admin123'),
                    'role': 'admin',
                    'name': '관리자',
                    'email': 'admin@example.com',
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    'id': '2',
                    'username': 'teacher',
                    'password': self._hash_password('teacher123'),
                    'role': 'teacher',
                    'name': '선생님',
                    'email': 'teacher@example.com',
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    'id': '3',
                    'username': 'student',
                    'password': self._hash_password('student123'),
                    'role': 'student',
                    'name': '학생',
                    'email': 'student@example.com',
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
            
            # 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            # 파일에 저장
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, ensure_ascii=False, indent=2)
            
            return True
        return False

def init_session_state():
    """세션 상태 초기화"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'name' not in st.session_state:
        st.session_state.name = None

def login_page():
    """로그인 페이지"""
    st.title("학원 문제 관리 시스템")
    st.subheader("로그인")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # UserAuth 인스턴스 생성
    user_auth = UserAuth(data_dir)
    
    # 기본 사용자 생성 (초기 설정)
    user_auth.create_default_users()
    
    # 로그인 폼
    with st.form("login_form"):
        username = st.text_input("사용자명")
        password = st.text_input("비밀번호", type="password")
        
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            if not username or not password:
                st.error("사용자명과 비밀번호를 입력해주세요.")
            else:
                # 사용자 인증
                success, user = user_auth.authenticate(username, password)
                
                if success:
                    # 세션 상태 업데이트
                    st.session_state.logged_in = True
                    st.session_state.username = user['username']
                    st.session_state.user_id = user['id']
                    st.session_state.role = user['role']
                    st.session_state.name = user.get('name', user['username'])
                    
                    st.success("로그인 성공!")
                    st.experimental_rerun()
                else:
                    st.error("사용자명 또는 비밀번호가 올바르지 않습니다.")
    
    # 기본 계정 정보 안내
    st.markdown("---")
    st.subheader("기본 계정 정보")
    st.markdown("""
    - 관리자: admin / admin123
    - 선생님: teacher / teacher123
    - 학생: student / student123
    """)

def logout():
    """로그아웃 처리"""
    # 세션 상태 초기화
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.name = None
    
    st.success("로그아웃 되었습니다.")
    st.experimental_rerun()

def app():
    # CSS 로드
    load_css()
    
    # 세션 상태 초기화
    init_session_state()
    
    # 로그인 상태 확인
    if not st.session_state.logged_in:
        # 로그인 페이지 표시
        login_page()
    else:
        # 사이드바에 로그아웃 버튼 추가
        with st.sidebar:
            st.write(f"로그인: {st.session_state.name} ({st.session_state.role})")
            if st.button("로그아웃"):
                logout()
        
        # 메인 페이지 표시
        st.title("학원 문제 관리 시스템")
        
        # 역할에 따른 메뉴 표시
        if st.session_state.role == 'admin':
            st.write("관리자 메뉴")
            menu = st.selectbox(
                "메뉴 선택",
                ["홈", "문제 출제", "첨삭 시스템", "첨삭 결과 분석", "사용자 관리"]
            )
            
            if menu == "홈":
                st.write("관리자 대시보드")
                st.write("모든 기능에 접근할 수 있습니다.")
            elif menu == "문제 출제":
                from pages.problem_generation import app as problem_app
                problem_app()
            elif menu == "첨삭 시스템":
                from pages.feedback_system import app as feedback_app
                feedback_app()
            elif menu == "첨삭 결과 분석":
                from pages.feedback_analytics import app as analytics_app
                analytics_app()
            elif menu == "사용자 관리":
                from pages.admin import app as admin_app
                admin_app()
        
        elif st.session_state.role == 'teacher':
            st.write("선생님 메뉴")
            menu = st.selectbox(
                "메뉴 선택",
                ["홈", "문제 출제", "첨삭 시스템", "첨삭 결과 분석"]
            )
            
            if menu == "홈":
                st.write("선생님 대시보드")
                st.write("문제 출제, 첨삭, 분석 기능에 접근할 수 있습니다.")
            elif menu == "문제 출제":
                from pages.problem_generation import app as problem_app
                problem_app()
            elif menu == "첨삭 시스템":
                from pages.feedback_system import app as feedback_app
                feedback_app()
            elif menu == "첨삭 결과 분석":
                from pages.feedback_analytics import app as analytics_app
                analytics_app()
        
        else:  # student
            st.write("학생 메뉴")
            menu = st.selectbox(
                "메뉴 선택",
                ["홈", "문제 풀기", "첨삭 확인", "학습 진행 상황"]
            )
            
            if menu == "홈":
                st.write("학생 대시보드")
                st.write("문제 풀기, 첨삭 확인, 학습 진행 상황 기능에 접근할 수 있습니다.")
            elif menu == "문제 풀기" or menu == "첨삭 확인":
                from pages.feedback_system import app as feedback_app
                feedback_app()
            elif menu == "학습 진행 상황":
                from pages.feedback_analytics import app as analytics_app
                analytics_app()

if __name__ == "__main__":
    app()
