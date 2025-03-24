import streamlit as st
import pandas as pd
import os
import sys
import json
import hashlib
import uuid
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가하여 모듈 import가 가능하도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common import load_css

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

def app():
    # CSS 로드
    load_css()
    
    st.title("사용자 관리")
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # UserModel 인스턴스 생성
    user_model = UserModel(data_dir)
    
    # 사용자 역할 확인 (세션에서)
    user_role = st.session_state.get('role', None)
    
    # 관리자만 접근 가능
    if user_role != 'admin':
        st.warning("관리자만 접근할 수 있는 페이지입니다.")
        return
    
    # 탭 생성
    tab1, tab2 = st.tabs(["사용자 목록", "사용자 추가"])
    
    # 탭 1: 사용자 목록
    with tab1:
        st.header("사용자 목록")
        
        # 모든 사용자 가져오기
        all_users = user_model.get_all_users()
        
        if all_users:
            # 사용자 목록 표시
            user_df = pd.DataFrame([
                {
                    '사용자 ID': user['id'],
                    '사용자명': user['username'],
                    '이름': user.get('name', ''),
                    '역할': user['role'],
                    '이메일': user.get('email', ''),
                    '생성일': user['created_at']
                } for user in all_users
            ])
            
            st.dataframe(user_df)
            
            # 선택한 사용자 관리
            selected_user_id = st.selectbox(
                "관리할 사용자 선택",
                [user['id'] for user in all_users],
                format_func=lambda x: f"{next((user['username'] for user in all_users if user['id'] == x), '')} ({next((user['role'] for user in all_users if user['id'] == x), '')})"
            )
            
            if selected_user_id:
                selected_user = user_model.get_user_by_id(selected_user_id)
                
                if selected_user:
                    st.subheader("사용자 정보")
                    
                    # 사용자 정보 표시 및 수정
                    with st.form("user_edit_form"):
                        username = st.text_input("사용자명", selected_user['username'], disabled=True)
                        name = st.text_input("이름", selected_user.get('name', ''))
                        email = st.text_input("이메일", selected_user.get('email', ''))
                        role = st.selectbox("역할", ["student", "teacher", "admin"], index=["student", "teacher", "admin"].index(selected_user['role']))
                        new_password = st.text_input("새 비밀번호 (변경 시에만 입력)", type="password")
                        
                        submit_button = st.form_submit_button("정보 수정")
                        
                        if submit_button:
                            update_data = {
                                'name': name,
                                'email': email,
                                'role': role
                            }
                            
                            if new_password:
                                update_data['password'] = new_password
                            
                            # 사용자 정보 업데이트
                            if user_model.update_user(selected_user_id, **update_data):
                                st.success("사용자 정보가 수정되었습니다.")
                                st.experimental_rerun()
                            else:
                                st.error("사용자 정보 수정에 실패했습니다.")
                    
                    # 사용자 삭제 버튼
                    if st.button("사용자 삭제"):
                        # 확인 대화상자
                        confirm = st.checkbox("정말로 이 사용자를 삭제하시겠습니까?")
                        
                        if confirm:
                            # 사용자 삭제
                            if user_model.delete_user(selected_user_id):
                                st.success("사용자가 삭제되었습니다.")
                                st.experimental_rerun()
                            else:
                                st.error("사용자 삭제에 실패했습니다.")
        else:
            st.info("등록된 사용자가 없습니다.")
    
    # 탭 2: 사용자 추가
    with tab2:
        st.header("사용자 추가")
        
        # 사용자 추가 폼
        with st.form("user_add_form"):
            username = st.text_input("사용자명 *")
            password = st.text_input("비밀번호 *", type="password")
            confirm_password = st.text_input("비밀번호 확인 *", type="password")
            name = st.text_input("이름")
            email = st.text_input("이메일")
            role = st.selectbox("역할 *", ["student", "teacher", "admin"])
            
            submit_button = st.form_submit_button("사용자 추가")
            
            if submit_button:
                if not username or not password:
                    st.error("사용자명과 비밀번호는 필수 입력 항목입니다.")
                elif password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    # 사용자 추가
                    success, message = user_model.add_user(username, password, role, name, email)
                    
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)

if __name__ == "__main__":
    app()
