import streamlit as st
import os
import sys
import json
import hashlib
from datetime import datetime
import time
import pandas as pd
import uuid

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 유틸리티 모듈 불러오기
from utils.common import load_css, load_env_from_config

# 페이지 모듈 불러오기
from pages import admin, student_dashboard, problem_generation, problem_solving, feedback_system, feedback_analytics, student_management

# 환경 변수 로드
load_env_from_config()

# CSS 설정
load_css()

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
    
    def _save_users_data(self):
        """사용자 데이터 저장"""
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users_data, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """사용자 인증"""
        for user in self.users_data:
            if user['username'] == username and user['password'] == self._hash_password(password):
                return True, user
        return False, None
    
    def create_user(self, username, password, role='student', name=None):
        """사용자 생성"""
        # 중복 사용자명 체크
        for user in self.users_data:
            if user['username'] == username:
                return None  # 이미 존재하는 사용자명
        
        # 새 사용자 ID 생성
        user_id = str(uuid.uuid4())
        
        # 사용자 정보 준비
        user_data = {
            'id': user_id,
            'username': username,
            'password': self._hash_password(password),
            'role': role,
            'name': name if name else username,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 사용자 목록에 추가
        self.users_data.append(user_data)
        
        # 저장
        self._save_users_data()
        
        return user_id
    
    def update_user(self, user_id, user_data):
        """사용자 정보 업데이트"""
        for i, user in enumerate(self.users_data):
            if user['id'] == user_id:
                # 비밀번호가 제공된 경우 해싱
                if 'password' in user_data and user_data['password']:
                    user_data['password'] = self._hash_password(user_data['password'])
                else:
                    # 비밀번호 필드 제외
                    user_data['password'] = user['password']
                
                # ID와 생성 시간은 유지
                user_data['id'] = user_id
                user_data['created_at'] = user['created_at']
                
                # 업데이트 시간 추가
                user_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 사용자 정보 업데이트
                self.users_data[i] = user_data
                
                # 저장
                self._save_users_data()
                
                return True
        
        return False
    
    def delete_user(self, user_id):
        """사용자 삭제"""
        for i, user in enumerate(self.users_data):
            if user['id'] == user_id:
                # 사용자 삭제
                del self.users_data[i]
                
                # 저장
                self._save_users_data()
                
                return True
        
        return False
    
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
                    'name': '교수',
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
    
    def get_all_users(self):
        """모든 사용자 정보 조회"""
        return self.users_data
    
    def get_user_by_id(self, user_id):
        """ID로 사용자 정보 조회"""
        for user in self.users_data:
            if user['id'] == user_id:
                return user
        
        return None

def init_session_state():
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'name' not in st.session_state:
        st.session_state.name = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'menu' not in st.session_state:
        st.session_state.menu = None
        
    # 역할에 따른 한글 권한명 설정
    if 'role_korean' not in st.session_state:
        if st.session_state.role == 'admin':
            st.session_state.role_korean = '관리자'
        elif st.session_state.role == 'teacher':
            st.session_state.role_korean = '교수'
        elif st.session_state.role == 'student':
            st.session_state.role_korean = '학생'
        else:
            st.session_state.role_korean = '게스트'

def show_login_page():
    """로그인 페이지를 표시합니다."""
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: #4B89DC; margin-bottom: 15px;">학원관리 시스템</h2>
        <p style="color: #6c757d; font-size: 16px;">학습 관리, 문제 풀이, 첨삭 피드백을 한 곳에서</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그인/회원가입 탭
    login_tab, register_tab = st.tabs(["로그인", "회원가입"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("아이디", placeholder="아이디를 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            login_button = st.form_submit_button("로그인", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("아이디와 비밀번호를 모두 입력해주세요.")
                else:
                    with st.spinner("로그인 중..."):
                        # 인증 지연 효과
                        time.sleep(0.5)
                        
                        # 인증 처리
                        user_auth = UserAuth(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
                        success, user_data = user_auth.authenticate(username, password)
                        
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.role = user_data.get('role', 'student')
                            st.session_state.name = user_data.get('name', '사용자')
                            st.session_state.user_id = user_data.get('id')
                            
                            # 역할에 따른 한글 권한명 설정
                            if st.session_state.role == 'admin':
                                st.session_state.role_korean = '관리자'
                            elif st.session_state.role == 'teacher':
                                st.session_state.role_korean = '교수'
                            elif st.session_state.role == 'student':
                                st.session_state.role_korean = '학생'
                            
                            # 역할별 기본 메뉴 설정
                            if st.session_state.role == 'student':
                                st.session_state.menu = 'student_dashboard'
                            elif st.session_state.role == 'teacher':
                                st.session_state.menu = 'problem_management'
                            else:  # admin
                                st.session_state.menu = 'admin'
                            
                            st.success(f"{st.session_state.name}님, 환영합니다!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
    
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("아이디", placeholder="사용할 아이디를 입력하세요")
            new_password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            confirm_password = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
            new_name = st.text_input("이름", placeholder="실명을 입력하세요")
            register_button = st.form_submit_button("회원가입", use_container_width=True)
            
            if register_button:
                if not new_username or not new_password or not new_name:
                    st.error("모든 필드를 입력해주세요.")
                elif new_password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    # 회원가입 처리
                    user_auth = UserAuth(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
                    user_id = user_auth.create_user(new_username, new_password, 'student', new_name)
                    
                    if user_id:
                        st.success(f"회원가입이 완료되었습니다. 아이디: {new_username}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
    
    # 기본 계정 정보 안내
    with st.expander("📌 기본 계정 정보"):
        st.markdown("""
        **관리자 계정**: admin / admin123  
        **교수 계정**: teacher / teacher123  
        **학생 계정**: student / student123
        """)

def logout():
    """로그아웃 처리"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.name = None
    st.session_state.user_id = None
    st.session_state.menu = None
    st.session_state.role_korean = '게스트'
    st.rerun()

def main():
    # 세션 상태 초기화
    init_session_state()
    
    # CSS 로드
    load_css()
    
    # 기본 페이지 네비게이션 숨기기
    st.markdown("""
    <style>
        /* 기본 Streamlit 페이지 네비게이션 숨기기 */
        section[data-testid="stSidebar"] > div.css-163ttbj > div.css-1d391kg > div.block-container {
            display: none;
        }
        
        /* 사이드바 기본 접힘 상태로 설정 */
        .css-1d391kg {
            width: 0px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 타이틀과 로고 설정
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <h1 style="color: #4B89DC; margin: 0; font-family: 'Noto Sans KR', sans-serif;">
            학원 학습 자동화 관리 시스템
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그인 확인
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # 사이드바 메뉴
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #495057;">안녕하세요, {st.session_state.name}님</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                역할: {st.session_state.role_korean}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 역할별 메뉴 옵션
        if st.session_state.role == "student":
            menu_options = {
                "대시보드": "student_dashboard",
                "문제 풀기": "problem_solving",
                "첨삭 확인": "feedback_check"
            }
        elif st.session_state.role == "teacher":
            menu_options = {
                "문제 관리": "problem_management",
                "첨삭 관리": "feedback_management",
                "학생 관리": "student_management"
            }
        else:  # admin
            menu_options = {
                "관리자 메뉴": "admin",
                "문제 관리": "problem_management",
                "첨삭 관리": "feedback_management",
                "학생 관리": "student_management"
            }
        
        # CSS 스타일 추가
        st.markdown("""
        <style>
        div.stButton button {
            background-color: #f8f9fa;
            border: 1px solid #eaeaea;
            padding: 12px 16px;
            text-align: left;
            color: #444;
            font-weight: normal;
            width: 100%;
            margin-bottom: 10px;
            border-radius: 8px;
            transition: all 0.3s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            font-size: 15px;
        }
        div.stButton button:hover {
            background-color: #f2f7ff;
            border-color: #cad9ed;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            transform: translateY(-1px);
        }
        .selected-menu {
            background-color: #4285F4 !important;
            color: white !important;
            border-color: #3b78e7 !important;
            font-weight: 500 !important;
            box-shadow: 0 2px 5px rgba(66, 133, 244, 0.2) !important;
        }
        /* 로그아웃 버튼 스타일 */
        [data-testid="baseButton-secondary"] {
            visibility: hidden;
            height: 0;
            position: absolute;
        }
        #logout_button {
            background-color: #f5f5f5 !important;
            color: #666 !important;
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            margin-top: 10px !important;
            font-weight: normal !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #logout_button:hover {
            background-color: #f0f0f0 !important;
            color: #d32f2f !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 버튼 스타일의 메뉴 생성
        for menu_name, menu_value in menu_options.items():
            # 현재 선택된 메뉴인지 확인
            is_selected = st.session_state.menu == menu_value
            
            # HTML로 버튼 스타일 적용
            button_style = "selected-menu" if is_selected else ""
            
            st.markdown(f"""
            <div class="menu-button">
                <button type="button" id="button-{menu_value}" 
                    class="stButton {button_style}" 
                    onclick="document.getElementById('button-{menu_value}-clicked').click()">
                    {menu_name}
                </button>
            </div>
            """, unsafe_allow_html=True)
            
            # 실제 버튼은 숨김
            if st.button(menu_name, key=f"button-{menu_value}-clicked"):
                st.session_state.menu = menu_value
                st.rerun()
        
        # 로그아웃 버튼
        st.markdown("""<hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">""", unsafe_allow_html=True)
        if st.button("로그아웃", key="logout_button"):
            logout()
    
    # 메뉴 페이지 라우팅
    if st.session_state.role == "student":
        if st.session_state.menu == "student_dashboard":
            import pages.student_dashboard as student_dashboard
            student_dashboard.app()
        elif st.session_state.menu == "problem_solving":
            import pages.problem_solving as problem_solving
            problem_solving.app()
        elif st.session_state.menu == "feedback_check":
            import pages.feedback_check as feedback_check
            feedback_check.app()
    elif st.session_state.role == "teacher" or st.session_state.role == "admin":
        if st.session_state.menu == "problem_management":
            import pages.problem_generation as problem_generation
            problem_generation.app()
        elif st.session_state.menu == "feedback_management":
            import pages.feedback_system as feedback_system
            feedback_system.app()
        elif st.session_state.menu == "student_management":
            import pages.student_management as student_management
            student_management.app()
        elif st.session_state.menu == "admin" and st.session_state.role == "admin":
            import pages.admin as admin
            # 사용자 모델 초기화
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            user_model = UserAuth(data_dir)
            admin.app()

if __name__ == "__main__":
    main()
