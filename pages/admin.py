import streamlit as st
import pandas as pd
import os
import sys
import json
import hashlib
import uuid
from datetime import datetime
import time

try:
    import google.generativeai as genai
except ImportError:
    st.error("google-generativeai 패키지를 설치해주세요: pip install google-generativeai")
    genai = None

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_dataframe, save_dataframe

class UserModel:
    """
    사용자 데이터 관리 클래스
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
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users_data, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password):
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def add_user(self, username, password, role, name=None, email=None):
        """사용자 추가"""
        # 이미 존재하는 사용자인지 확인
        if any(user['username'] == username for user in self.users_data):
            return False, "이미 존재하는 사용자명입니다."
        
        # 사용자 ID 생성
        user_id = str(uuid.uuid4())
        
        # 생성 시간 추가
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 사용자 데이터 준비
        user_data = {
            'id': user_id,
            'username': username,
            'password': self._hash_password(password),
            'role': role,
            'name': name if name else username,
            'email': email,
            'created_at': created_at
        }
        
        # 사용자 추가
        self.users_data.append(user_data)
        self._save_users_data()
        
        return True, "사용자가 성공적으로 추가되었습니다."
    
    def authenticate(self, username, password):
        """사용자 인증"""
        for user in self.users_data:
            if user['username'] == username and user['password'] == self._hash_password(password):
                return True, user
        return False, None
    
    def get_user_by_id(self, user_id):
        """ID로 사용자 조회"""
        for user in self.users_data:
            if user['id'] == user_id:
                return user
        return None
    
    def get_user_by_username(self, username):
        """사용자명으로 사용자 조회"""
        for user in self.users_data:
            if user['username'] == username:
                return user
        return None
    
    def update_user(self, user_id, **kwargs):
        """사용자 정보 업데이트"""
        for user in self.users_data:
            if user['id'] == user_id:
                for key, value in kwargs.items():
                    if key == 'password':
                        user[key] = self._hash_password(value)
                    else:
                        user[key] = value
                self._save_users_data()
                return True
        return False
    
    def delete_user(self, user_id):
        """사용자 삭제"""
        for i, user in enumerate(self.users_data):
            if user['id'] == user_id:
                del self.users_data[i]
                self._save_users_data()
                return True
        return False
    
    def get_all_users(self):
        """모든 사용자 조회"""
        return self.users_data

def test_api_key(api_key):
    """API 키 테스트"""
    if genai is None:
        return False, "google-generativeai 패키지가 설치되어 있지 않습니다. 먼저 패키지를 설치해주세요."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content('Hello, this is a test.')
        return True, "API 키가 정상적으로 작동합니다."
    except Exception as e:
        return False, f"API 키 테스트 중 오류가 발생했습니다: {str(e)}"

def app():
    """관리자 페이지"""
    
    # 로그인 상태 확인
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("로그인이 필요합니다.")
        return
    
    # 관리자 권한 확인
    if st.session_state.role != 'admin':
        st.error("관리자 권한이 필요합니다.")
        return
    
    st.title("관리자 대시보드")
    
    # 사용자 모델 초기화
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    user_model = UserModel(data_dir)
    
    # 탭 구성
    tabs = st.tabs(["사용자 관리", "학급 관리", "API 설정"])
    
    # 사용자 관리 탭
    with tabs[0]:
        st.subheader("사용자 관리")
        
        # 사용자 목록 불러오기
        users = user_model.get_all_users()
        
        # 사용자 목록을 데이터프레임으로 변환
        users_df = pd.DataFrame(users)
        
        # 비밀번호 필드 제외, 날짜 형식 변환
        if not users_df.empty:
            users_df = users_df.drop(columns=['password'])
            
            # created_at 날짜 포맷 변경
            if 'created_at' in users_df.columns:
                users_df['created_at'] = pd.to_datetime(users_df['created_at']).dt.strftime('%Y-%m-%d')
            
            # updated_at 날짜 포맷 변경
            if 'updated_at' in users_df.columns:
                users_df['updated_at'] = pd.to_datetime(users_df['updated_at'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # 역할별 필터링 옵션
        role_filter = st.selectbox("역할별 필터링", ["전체", "관리자", "교수", "학생"], 
                                 format_func=lambda x: {"전체": "전체", "관리자": "관리자", "교수": "교수", "학생": "학생"}[x])
        
        # 필터링 적용
        if role_filter != "전체":
            role_map = {"관리자": "admin", "교수": "teacher", "학생": "student"}
            filtered_df = users_df[users_df["role"] == role_map[role_filter]]
        else:
            filtered_df = users_df
        
        # 역할 표시 변환 (admin, teacher, student -> 관리자, 교수, 학생)
        if not filtered_df.empty:
            filtered_df["role"] = filtered_df["role"].map({"admin": "관리자", "teacher": "교수", "student": "학생"})
        
        # 사용자 목록 표시
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.info("사용자가 없습니다.")
        
        # 사용자 관리 섹션
        st.subheader("사용자 추가/수정")
        
        # 수정할 사용자 선택 옵션
        edit_mode = st.radio("작업 선택", ["새 사용자 추가", "기존 사용자 수정"], horizontal=True)
        
        if edit_mode == "새 사용자 추가":
            with st.form("add_user_form"):
                username = st.text_input("아이디", key="add_username")
                password = st.text_input("비밀번호", type="password", key="add_password")
                confirm_password = st.text_input("비밀번호 확인", type="password", key="add_confirm_password")
                name = st.text_input("이름", key="add_name")
                role = st.selectbox("역할", ["관리자", "교수", "학생"], 
                                  format_func=lambda x: {"관리자": "관리자", "교수": "교수", "학생": "학생"}[x],
                                  key="add_role")
                
                # 역할 매핑
                role_map = {"관리자": "admin", "교수": "teacher", "학생": "student"}
                
                # 제출 버튼
                submit_button = st.form_submit_button("사용자 추가")
                
                if submit_button:
                    if not username or not password:
                        st.error("아이디와 비밀번호는 필수 항목입니다.")
                    elif password != confirm_password:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        # 사용자 추가
                        result = user_model.add_user(username, password, role_map[role], name)
                        
                        if result:
                            st.success(f"사용자 '{username}'이(가) 추가되었습니다.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"사용자 '{username}'이(가) 이미 존재합니다.")
        else:
            # 수정할 사용자 선택
            if not users_df.empty:
                selected_user = st.selectbox("수정할 사용자 선택", 
                                           users_df["username"], 
                                           format_func=lambda x: f"{x} ({users_df[users_df['username'] == x]['name'].iloc[0]})")
                
                # 선택된 사용자 정보 가져오기
                selected_user_data = users_df[users_df["username"] == selected_user].iloc[0].to_dict()
                
                with st.form("edit_user_form"):
                    st.text_input("아이디", value=selected_user_data["username"], disabled=True)
                    password = st.text_input("비밀번호 (변경 시에만 입력)", type="password", key="edit_password")
                    confirm_password = st.text_input("비밀번호 확인", type="password", key="edit_confirm_password")
                    name = st.text_input("이름", value=selected_user_data["name"], key="edit_name")
                    
                    # 역할 한글 매핑
                    role_korean_map = {"admin": "관리자", "teacher": "교수", "student": "학생"}
                    role_options = list(role_korean_map.values())
                    
                    # 현재 역할 인덱스 찾기
                    current_role_index = list(role_korean_map.keys()).index(selected_user_data["role"])
                    
                    role = st.selectbox("역할", role_options, index=current_role_index, key="edit_role")
                    
                    # 역할 역매핑
                    role_map = {"관리자": "admin", "교수": "teacher", "학생": "student"}
                    
                    # 사용자 삭제 옵션
                    delete_user = st.checkbox("이 사용자 삭제", key="delete_user")
                    
                    # 제출 버튼
                    submit_button = st.form_submit_button("변경사항 저장")
                    
                    if submit_button:
                        if delete_user:
                            # 사용자 삭제
                            result = user_model.delete_user(selected_user_data["id"])
                            
                            if result:
                                st.success(f"사용자 '{selected_user}'이(가) 삭제되었습니다.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"사용자 '{selected_user}' 삭제 중 오류가 발생했습니다.")
                        else:
                            # 비밀번호 검증
                            if password and password != confirm_password:
                                st.error("비밀번호가 일치하지 않습니다.")
                            else:
                                # 업데이트할 사용자 데이터 준비
                                update_data = {
                                    "username": selected_user_data["username"],
                                    "password": password,  # 빈 문자열인 경우 업데이트 안 함
                                    "name": name,
                                    "role": role_map[role]
                                }
                                
                                # 사용자 정보 업데이트
                                result = user_model.update_user(selected_user_data["id"], update_data)
                                
                                if result:
                                    st.success(f"사용자 '{selected_user}' 정보가 업데이트되었습니다.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"사용자 '{selected_user}' 정보 업데이트 중 오류가 발생했습니다.")
            else:
                st.info("수정할 사용자가 없습니다.")
    
    # 학급 관리 탭
    with tabs[1]:
        st.subheader("학급 관리")
        st.info("학급 관리 기능은 준비 중입니다.")
    
    # API 설정 탭
    with tabs[2]:
        st.subheader("API 설정")
        
        # API 키 입력
        api_key = st.text_input("Gemini API 키", type="password")
        
        # 저장 옵션
        save_option = st.selectbox(
            "저장 옵션",
            ["환경 변수와 config.json에 저장"],
            format_func=lambda x: x
        )
        
        col1, col2 = st.columns(2)
        
        # API 키 저장 버튼
        if col1.button("API 키 저장"):
            if not api_key:
                st.error("API 키를 입력해주세요.")
            else:
                try:
                    # config.json 파일에 저장
                    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.streamlit')
                    os.makedirs(config_dir, exist_ok=True)
                    config_file = os.path.join(config_dir, 'config.json')
                    
                    config_data = {}
                    if os.path.exists(config_file):
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                    
                    config_data['GEMINI_API_KEY'] = api_key
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                    
                    st.success("API 키가 성공적으로 저장되었습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"API 키 저장 중 오류가 발생했습니다: {str(e)}")
        
        # API 키 테스트 버튼
        if col2.button("API 키 테스트"):
            if not api_key:
                st.error("API 키를 입력해주세요.")
            else:
                success, message = test_api_key(api_key)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # API 키 삭제 버튼
        if st.button("API 키 삭제"):
            try:
                config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.streamlit')
                config_file = os.path.join(config_dir, 'config.json')
                
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    if 'GEMINI_API_KEY' in config_data:
                        del config_data['GEMINI_API_KEY']
                        
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump(config_data, f, ensure_ascii=False, indent=2)
                        
                        st.success("API 키가 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.info("저장된 API 키가 없습니다.")
                else:
                    st.info("저장된 API 키가 없습니다.")
            except Exception as e:
                st.error(f"API 키를 삭제하는 중 오류가 발생했습니다: {str(e)}")
        
        # API 키 관련 정보 및 가이드
        st.markdown("""
        ### Gemini API 키 안내
        
        1. [Google AI Studio](https://aistudio.google.com/)에 접속하여 계정을 생성합니다.
        2. 'API keys' 메뉴에서 새 API 키를 생성합니다.
        3. 생성된 API 키를 위 입력 필드에 입력하고 저장합니다.
        
        **참고**: API 키는 외부에 노출되지 않도록 주의하세요.
        """)
        
        # API 키 테스트 섹션
        if api_key:
            st.markdown("### API 키 테스트")
            if st.button("API 키 테스트"):
                with st.spinner("API 연결 테스트 중..."):
                    try:
                        # API 키 테스트 로직 (간단한 요청 보내기)
                        success, message = test_api_key(api_key)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"API 키 테스트 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    app()
