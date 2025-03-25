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

class StudentManager:
    """
    학생 정보 관리 클래스
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.students_file = os.path.join(data_dir, 'students.json')
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.students_file), exist_ok=True)
        self.students_data = self._load_students_data()
    
    def _load_students_data(self):
        """학생 데이터 로드"""
        if os.path.exists(self.students_file):
            with open(self.students_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except Exception as e:
                    st.error(f"학생 데이터 로드 중 오류 발생: {e}")
                    return []
        return []
    
    def _save_students_data(self):
        """학생 데이터 저장"""
        with open(self.students_file, 'w', encoding='utf-8') as f:
            json.dump(self.students_data, f, ensure_ascii=False, indent=2)
    
    def add_student(self, student_data):
        """학생 추가"""
        # ID 생성
        student_id = str(uuid.uuid4())
        student_data['id'] = student_id
        
        # 생성 시간 추가
        student_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 학생 목록에 추가
        self.students_data.append(student_data)
        
        # 저장
        self._save_students_data()
        
        return student_id
    
    def update_student(self, student_id, student_data):
        """학생 정보 업데이트"""
        for i, student in enumerate(self.students_data):
            if student['id'] == student_id:
                # ID와 생성 시간은 유지
                student_data['id'] = student_id
                student_data['created_at'] = student['created_at']
                
                # 업데이트 시간 추가
                student_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 학생 정보 업데이트
                self.students_data[i] = student_data
                
                # 저장
                self._save_students_data()
                
                return True
        
        return False
    
    def delete_student(self, student_id):
        """학생 삭제"""
        for i, student in enumerate(self.students_data):
            if student['id'] == student_id:
                # 학생 삭제
                del self.students_data[i]
                
                # 저장
                self._save_students_data()
                
                return True
        
        return False
    
    def get_all_students(self):
        """모든 학생 정보 조회"""
        return self.students_data
    
    def get_student_by_id(self, student_id):
        """ID로 학생 정보 조회"""
        for student in self.students_data:
            if student['id'] == student_id:
                return student
        
        return None
    
    def search_students(self, query):
        """학생 검색"""
        query = query.lower()
        results = []
        
        for student in self.students_data:
            # 이름, 학번, 반, 학년 등에서 검색
            if (query in student.get('name', '').lower() or
                query in student.get('student_number', '').lower() or
                query in student.get('grade', '').lower() or
                query in student.get('class_name', '').lower()):
                results.append(student)
        
        return results
    
    def create_user_for_student(self, student_id, user_auth):
        """학생 계정 생성"""
        student = self.get_student_by_id(student_id)
        if not student:
            return False, "학생 정보를 찾을 수 없습니다."
        
        # 학생 이름과 학번을 이용하여 아이디 생성
        username = f"student_{student['student_number']}"
        
        # 기본 비밀번호는 학번과 동일하게 설정
        password = student['student_number']
        
        # 이름은 실제 학생 이름으로 설정
        name = student['name']
        
        # 사용자 계정 생성
        user_id = user_auth.create_user(username, password, 'student', name)
        
        # 학생 정보에 사용자 ID 연결
        for i, s in enumerate(self.students_data):
            if s['id'] == student_id:
                self.students_data[i]['user_id'] = user_id
                self._save_students_data()
                break
        
        return True, f"학생 '{name}'의 계정이 생성되었습니다. 아이디: {username}, 비밀번호: {password}"

def app():
    # CSS 로드
    load_css()
    
    st.title("학생 관리")
    
    # 로그인 확인
    is_logged_in = st.session_state.get('logged_in', False)
    
    if not is_logged_in:
        st.error("이 페이지에 접근하려면 로그인이 필요합니다.")
        st.info("로그인 페이지로 이동하여 로그인해주세요.")
        return
    
    # 데이터 디렉토리 경로
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # StudentManager 인스턴스 생성
    student_manager = StudentManager(data_dir)
    
    # 사용자 역할 확인 (세션에서)
    user_role = st.session_state.get('role', 'student')  # 기본값은 학생
    
    # 관리자 또는 선생님만 접근 가능
    if user_role not in ['admin', 'teacher']:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        return
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["학생 목록", "학생 등록", "계정 관리"])
    
    # 탭 1: 학생 목록
    with tab1:
        st.header("학생 목록")
        
        # 검색 기능
        search_query = st.text_input("이름 또는 학번으로 검색", "")
        
        # 모든 학생 정보 가져오기
        all_students = student_manager.get_all_students()
        
        if search_query:
            # 검색 결과 필터링
            filtered_students = student_manager.search_students(search_query)
        else:
            filtered_students = all_students
        
        if filtered_students:
            # 학생 정보를 DataFrame으로 변환
            student_df = pd.DataFrame([
                {
                    '학번': s.get('student_number', ''),
                    '이름': s.get('name', ''),
                    '학년': s.get('grade', ''),
                    '반': s.get('class_name', ''),
                    '전화번호': s.get('phone', ''),
                    '등록일': s.get('created_at', '')
                } for s in filtered_students
            ])
            
            # 학생 목록 표시
            st.dataframe(student_df)
            
            # 학생 선택
            student_ids = [s['id'] for s in filtered_students]
            student_names = [f"{s.get('name', '')} ({s.get('student_number', '')})" for s in filtered_students]
            
            selected_student_idx = st.selectbox(
                "상세 정보를 볼 학생 선택",
                range(len(student_names)),
                format_func=lambda x: student_names[x]
            )
            
            selected_student_id = student_ids[selected_student_idx]
            selected_student = student_manager.get_student_by_id(selected_student_id)
            
            if selected_student:
                st.subheader(f"{selected_student.get('name', '')}의 정보")
                
                # 학생 정보 표시
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**학번:** {selected_student.get('student_number', '')}")
                    st.write(f"**이름:** {selected_student.get('name', '')}")
                    st.write(f"**학년:** {selected_student.get('grade', '')}")
                    st.write(f"**반:** {selected_student.get('class_name', '')}")
                
                with col2:
                    st.write(f"**전화번호:** {selected_student.get('phone', '')}")
                    st.write(f"**이메일:** {selected_student.get('email', '')}")
                    st.write(f"**주소:** {selected_student.get('address', '')}")
                    st.write(f"**등록일:** {selected_student.get('created_at', '')}")
                
                # 학생 정보 수정
                with st.expander("학생 정보 수정"):
                    # 학생 정보 입력 폼
                    with st.form(f"update_student_form_{selected_student_id}"):
                        student_number = st.text_input("학번", selected_student.get('student_number', ''))
                        name = st.text_input("이름", selected_student.get('name', ''))
                        grade = st.text_input("학년", selected_student.get('grade', ''))
                        class_name = st.text_input("반", selected_student.get('class_name', ''))
                        phone = st.text_input("전화번호", selected_student.get('phone', ''))
                        email = st.text_input("이메일", selected_student.get('email', ''))
                        address = st.text_input("주소", selected_student.get('address', ''))
                        
                        # 폼 제출 버튼
                        update_button = st.form_submit_button("정보 수정")
                        
                        if update_button:
                            # 학생 정보 업데이트
                            student_data = {
                                'student_number': student_number,
                                'name': name,
                                'grade': grade,
                                'class_name': class_name,
                                'phone': phone,
                                'email': email,
                                'address': address
                            }
                            
                            success = student_manager.update_student(selected_student_id, student_data)
                            
                            if success:
                                st.success("학생 정보가 수정되었습니다.")
                                st.rerun()
                            else:
                                st.error("학생 정보 수정에 실패했습니다.")
                
                # 학생 삭제
                if st.button(f"{selected_student.get('name', '')} 학생 삭제", key=f"delete_student_{selected_student_id}"):
                    # 삭제 확인
                    confirm = st.checkbox(f"정말 {selected_student.get('name', '')} 학생을 삭제하시겠습니까?", key=f"confirm_delete_{selected_student_id}")
                    
                    if confirm:
                        success = student_manager.delete_student(selected_student_id)
                        
                        if success:
                            st.success(f"{selected_student.get('name', '')} 학생이 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("학생 삭제에 실패했습니다.")
        else:
            st.info("등록된 학생이 없습니다.")
    
    # 탭 2: 학생 등록
    with tab2:
        st.header("학생 등록")
        
        # 학생 정보 입력 폼
        with st.form("register_student_form"):
            student_number = st.text_input("학번")
            name = st.text_input("이름")
            grade = st.text_input("학년")
            class_name = st.text_input("반")
            phone = st.text_input("전화번호")
            email = st.text_input("이메일")
            address = st.text_input("주소")
            
            # 폼 제출 버튼
            submit_button = st.form_submit_button("학생 등록")
            
            if submit_button:
                if not student_number or not name:
                    st.error("학번과 이름은 필수 입력 항목입니다.")
                else:
                    # 학생 정보 준비
                    student_data = {
                        'student_number': student_number,
                        'name': name,
                        'grade': grade,
                        'class_name': class_name,
                        'phone': phone,
                        'email': email,
                        'address': address
                    }
                    
                    # 학생 등록
                    student_id = student_manager.add_student(student_data)
                    
                    if student_id:
                        st.success(f"{name} 학생이 등록되었습니다.")
                        st.rerun()
                    else:
                        st.error("학생 등록에 실패했습니다.")
    
    # 탭 3: 계정 관리
    with tab3:
        st.header("계정 관리")
        
        # UserAuth 인스턴스 생성
        from app import UserAuth
        user_auth = UserAuth(data_dir)
        
        # 학생 목록 가져오기
        all_students = student_manager.get_all_students()
        
        if all_students:
            # 계정이 없는 학생만 필터링
            students_without_account = [s for s in all_students if 'user_id' not in s]
            
            if students_without_account:
                st.subheader("학생 계정 생성")
                
                # 학생 선택
                student_ids = [s['id'] for s in students_without_account]
                student_names = [f"{s.get('name', '')} ({s.get('student_number', '')})" for s in students_without_account]
                
                selected_student_idx = st.selectbox(
                    "계정을 생성할 학생 선택",
                    range(len(student_names)),
                    format_func=lambda x: student_names[x]
                )
                
                selected_student_id = student_ids[selected_student_idx]
                selected_student = student_manager.get_student_by_id(selected_student_id)
                
                if selected_student:
                    st.write(f"**선택한 학생:** {selected_student.get('name', '')} (학번: {selected_student.get('student_number', '')})")
                    
                    # 계정 생성 버튼
                    if st.button("자동 계정 생성"):
                        success, message = student_manager.create_user_for_student(selected_student_id, user_auth)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    
                    # 수동 계정 생성 폼
                    with st.expander("수동으로 계정 정보 입력"):
                        # 기본값 설정
                        default_username = f"student_{selected_student.get('student_number', '')}"
                        default_password = selected_student.get('student_number', '')
                        
                        # 계정 생성 폼
                        with st.form(f"create_account_form_{selected_student_id}"):
                            username = st.text_input("사용자명", value=default_username)
                            password = st.text_input("비밀번호", value=default_password)
                            name = st.text_input("표시 이름", value=selected_student.get('name', ''))
                            
                            # 폼 제출 버튼
                            create_button = st.form_submit_button("계정 생성")
                            
                            if create_button:
                                if not username or not password:
                                    st.error("사용자명과 비밀번호는 필수 입력 항목입니다.")
                                else:
                                    # 계정 생성
                                    user_id = user_auth.create_user(username, password, 'student', name)
                                    
                                    if user_id:
                                        # 학생 정보에 사용자 ID 연결
                                        for i, s in enumerate(student_manager.students_data):
                                            if s['id'] == selected_student_id:
                                                student_manager.students_data[i]['user_id'] = user_id
                                                student_manager._save_students_data()
                                                break
                                        
                                        st.success(f"{name} 학생의 계정이 생성되었습니다.")
                                        st.info(f"사용자명: {username}, 비밀번호: {password}")
                                        st.rerun()
                                    else:
                                        st.error("이미 존재하는 사용자명입니다. 다른 사용자명을 입력해주세요.")
            else:
                st.info("모든 학생에게 계정이 생성되어 있습니다.")
            
            # 계정 목록 표시
            st.subheader("학생 계정 목록")
            
            # 계정 정보 가져오기
            all_users = user_auth.get_all_users()
            student_users = [u for u in all_users if u['role'] == 'student']
            
            if student_users:
                # 학생 정보와 계정 정보 매핑
                for user in student_users:
                    user_id = user.get('id')
                    # 해당 계정을 가진 학생 정보 찾기
                    associated_student = next((s for s in all_students if s.get('user_id') == user_id), None)
                    if associated_student:
                        user['student_info'] = f"{associated_student.get('grade', '')}학년 {associated_student.get('class_name', '')}반"
                        user['student_number'] = associated_student.get('student_number', '')
                    else:
                        user['student_info'] = "정보 없음"
                        user['student_number'] = "-"
                
                # 계정 정보를 DataFrame으로 변환
                user_df = pd.DataFrame([
                    {
                        '학번': u.get('student_number', '-'),
                        '사용자명': u.get('username', ''),
                        '이름': u.get('name', ''),
                        '학급 정보': u.get('student_info', ''),
                        '생성일': u.get('created_at', '')
                    } for u in student_users
                ])
                
                # 계정 목록 표시
                st.dataframe(user_df)
            else:
                st.info("등록된 학생 계정이 없습니다.")
        else:
            st.info("등록된 학생이 없습니다. 먼저 학생을 등록해주세요.")

if __name__ == "__main__":
    app() 