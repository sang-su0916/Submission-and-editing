import pandas as pd
import os

class ProblemModel:
    """
    문제 데이터 모델 클래스
    """
    def __init__(self, data_dir):
        """
        초기화 함수
        
        Args:
            data_dir (str): 데이터 디렉토리 경로
        """
        self.data_dir = data_dir
        self.problems_file = os.path.join(data_dir, 'problems.csv')
        self._ensure_data_dir()
        self._load_problems()
    
    def _ensure_data_dir(self):
        """데이터 디렉토리가 존재하는지 확인하고 없으면 생성"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_problems(self):
        """문제 데이터 로드"""
        if os.path.exists(self.problems_file):
            self.problems_df = pd.read_csv(self.problems_file, encoding='utf-8-sig')
        else:
            self.problems_df = pd.DataFrame({
                'id': [],
                'subject': [],
                'problem_type': [],
                'difficulty': [],
                'title': [],
                'content': [],
                'answer': [],
                'created_by': []
            })
    
    def save_problems(self):
        """문제 데이터 저장"""
        self.problems_df.to_csv(self.problems_file, index=False, encoding='utf-8-sig')
    
    def get_all_problems(self):
        """모든 문제 반환"""
        return self.problems_df
    
    def get_problem_by_id(self, problem_id):
        """ID로 문제 조회"""
        if problem_id in self.problems_df['id'].values:
            return self.problems_df[self.problems_df['id'] == problem_id].iloc[0].to_dict()
        return None
    
    def add_problem(self, problem_data):
        """새 문제 추가"""
        # 새 ID 생성
        new_id = max(self.problems_df['id'].astype(int)) + 1 if not self.problems_df.empty else 1
        problem_data['id'] = new_id
        
        # 데이터프레임에 추가
        new_row = pd.DataFrame([problem_data])
        self.problems_df = pd.concat([self.problems_df, new_row], ignore_index=True)
        
        # 저장
        self.save_problems()
        return new_id
    
    def update_problem(self, problem_id, problem_data):
        """문제 업데이트"""
        if problem_id in self.problems_df['id'].values:
            for key, value in problem_data.items():
                if key != 'id':  # ID는 변경하지 않음
                    self.problems_df.loc[self.problems_df['id'] == problem_id, key] = value
            
            # 저장
            self.save_problems()
            return True
        return False
    
    def delete_problem(self, problem_id):
        """문제 삭제"""
        if problem_id in self.problems_df['id'].values:
            self.problems_df = self.problems_df[self.problems_df['id'] != problem_id]
            
            # 저장
            self.save_problems()
            return True
        return False
    
    def filter_problems(self, subject=None, problem_type=None, difficulty=None, search_term=None):
        """문제 필터링"""
        filtered_df = self.problems_df.copy()
        
        if subject:
            filtered_df = filtered_df[filtered_df['subject'] == subject]
        
        if problem_type:
            filtered_df = filtered_df[filtered_df['problem_type'] == problem_type]
        
        if difficulty:
            filtered_df = filtered_df[filtered_df['difficulty'] == difficulty]
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['title'].str.contains(search_term, case=False, na=False) | 
                filtered_df['content'].str.contains(search_term, case=False, na=False)
            ]
        
        return filtered_df


class SubmissionModel:
    """
    답안 제출 데이터 모델 클래스
    """
    def __init__(self, data_dir):
        """
        초기화 함수
        
        Args:
            data_dir (str): 데이터 디렉토리 경로
        """
        self.data_dir = data_dir
        self.submissions_file = os.path.join(data_dir, 'submissions.csv')
        self._ensure_data_dir()
        self._load_submissions()
    
    def _ensure_data_dir(self):
        """데이터 디렉토리가 존재하는지 확인하고 없으면 생성"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_submissions(self):
        """답안 제출 데이터 로드"""
        if os.path.exists(self.submissions_file):
            self.submissions_df = pd.read_csv(self.submissions_file, encoding='utf-8-sig')
        else:
            self.submissions_df = pd.DataFrame({
                'id': [],
                'student_name': [],
                'problem_id': [],
                'problem_title': [],
                'answer': [],
                'score': [],
                'feedback': [],
                'evaluated_by': []
            })
    
    def save_submissions(self):
        """답안 제출 데이터 저장"""
        self.submissions_df.to_csv(self.submissions_file, index=False, encoding='utf-8-sig')
    
    def get_all_submissions(self):
        """모든 답안 제출 반환"""
        return self.submissions_df
    
    def get_submission_by_id(self, submission_id):
        """ID로 답안 제출 조회"""
        if submission_id in self.submissions_df['id'].values:
            return self.submissions_df[self.submissions_df['id'] == submission_id].iloc[0].to_dict()
        return None
    
    def add_submission(self, submission_data):
        """새 답안 제출 추가"""
        # 새 ID 생성
        new_id = max(self.submissions_df['id'].astype(int)) + 1 if not self.submissions_df.empty else 1
        submission_data['id'] = new_id
        
        # 데이터프레임에 추가
        new_row = pd.DataFrame([submission_data])
        self.submissions_df = pd.concat([self.submissions_df, new_row], ignore_index=True)
        
        # 저장
        self.save_submissions()
        return new_id
    
    def update_submission(self, submission_id, submission_data):
        """답안 제출 업데이트"""
        if submission_id in self.submissions_df['id'].values:
            for key, value in submission_data.items():
                if key != 'id':  # ID는 변경하지 않음
                    self.submissions_df.loc[self.submissions_df['id'] == submission_id, key] = value
            
            # 저장
            self.save_submissions()
            return True
        return False
    
    def delete_submission(self, submission_id):
        """답안 제출 삭제"""
        if submission_id in self.submissions_df['id'].values:
            self.submissions_df = self.submissions_df[self.submissions_df['id'] != submission_id]
            
            # 저장
            self.save_submissions()
            return True
        return False
    
    def get_submissions_by_student(self, student_name):
        """학생별 답안 제출 조회"""
        return self.submissions_df[self.submissions_df['student_name'] == student_name]
    
    def get_submissions_by_problem(self, problem_id):
        """문제별 답안 제출 조회"""
        return self.submissions_df[self.submissions_df['problem_id'] == problem_id]
    
    def get_pending_submissions(self):
        """평가 대기 중인 답안 제출 조회"""
        return self.submissions_df[self.submissions_df['feedback'].isna() | (self.submissions_df['feedback'] == '')]
    
    def get_evaluated_submissions(self):
        """평가 완료된 답안 제출 조회"""
        return self.submissions_df[~self.submissions_df['feedback'].isna() & (self.submissions_df['feedback'] != '')]


class UserModel:
    """
    사용자 데이터 모델 클래스
    """
    def __init__(self, data_dir):
        """
        초기화 함수
        
        Args:
            data_dir (str): 데이터 디렉토리 경로
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self._ensure_data_dir()
        self._load_users()
    
    def _ensure_data_dir(self):
        """데이터 디렉토리가 존재하는지 확인하고 없으면 생성"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_users(self):
        """사용자 데이터 로드"""
        import json
        
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            # 기본 사용자 생성
            self.users = {
                "teacher1": {"password": "teacher1", "type": "선생님", "name": "김선생"},
                "student1": {"password": "student1", "type": "학생", "name": "이학생"}
            }
            self.save_users()
    
    def save_users(self):
        """사용자 데이터 저장"""
        import json
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
    
    def get_all_users(self):
        """모든 사용자 반환"""
        return self.users
    
    def get_user(self, username):
        """사용자 조회"""
        return self.users.get(username)
    
    def add_user(self, username, user_data):
        """새 사용자 추가"""
        if username in self.users:
            return False
        
        self.users[username] = user_data
        self.save_users()
        return True
    
    def update_user(self, username, user_data):
        """사용자 정보 업데이트"""
        if username not in self.users:
            return False
        
        for key, value in user_data.items():
            self.users[username][key] = value
        
        self.save_users()
        return True
    
    def delete_user(self, username):
        """사용자 삭제"""
        if username not in self.users:
            return False
        
        del self.users[username]
        self.save_users()
        return True
    
    def authenticate(self, username, password):
        """사용자 인증"""
        if username in self.users and self.users[username]["password"] == password:
            return True, self.users[username]["type"], self.users[username]["name"]
        return False, None, None
