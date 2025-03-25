from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import os
import json
import random
import uuid

# google-generativeai 라이브러리 임포트 시도
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ProblemGenerator:
    """
    문제 생성기 클래스
    """
    def __init__(self):
        # 기본 템플릿 로드
        self.templates = self._load_default_templates()
        
        # API 키 환경 변수에서 가져오기 시도
        self.api_key = os.environ.get('GOOGLE_API_KEY', '')
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                print(f"Gemini API 구성 중 오류: {str(e)}")
    
    def _load_default_templates(self):
        """기본 템플릿 로드"""
        return {
            "객관식": {
                "영어": [
                    "다음 문장의 빈칸에 들어갈 가장 적절한 표현은?",
                    "다음 중 문법적으로 올바른 문장은?",
                    "다음 대화에서 밑줄 친 부분과 의미가 가장 비슷한 것은?"
                ],
                "수학": [
                    "다음 방정식의 해는?",
                    "다음 그래프에서 최댓값은?",
                    "다음 함수의 극한값으로 옳은 것은?"
                ]
            },
            "주관식": {
                "영어": [
                    "다음 문장을 영작하시오.",
                    "다음 글을 요약하시오.",
                    "다음 대화의 상황을 설명하시오."
                ],
                "수학": [
                    "다음 문제를 풀이과정과 함께 서술하시오.",
                    "다음 증명을 완성하시오.",
                    "다음 수열의 일반항을 구하시오."
                ]
            }
        }
    
    def generate_problem(self, base_problem, variation_type="similar"):
        """
        기본 문제를 변형하여 새로운 문제 생성
        """
        if not base_problem:
            return {"error": "기본 문제가 없습니다."}
        
        # API 사용 시도
        if self.api_key and GEMINI_AVAILABLE:
            try:
                return self._generate_with_api(base_problem, variation_type)
            except Exception as e:
                print(f"API 생성 실패, 기본 변형 사용: {str(e)}")
                # API 실패 시 기본 변형으로 대체
        
        # 기본 변형 적용
        new_problem = base_problem.copy()
        new_problem["id"] = str(uuid.uuid4())
        new_problem["title"] = f"{base_problem.get('title', '문제')} - 변형"
        
        # 문제 유형별 간단한 변형 로직
        problem_type = base_problem.get('problem_type', '객관식')
        subject = base_problem.get('subject', '영어')
        
        # 문제 내용 변형 (간단한 패턴 변형)
        original_content = base_problem.get('content', '')
        
        if variation_type == "similar":
            # 유사 문제 생성
            if problem_type == "객관식":
                if "영어" in subject:
                    # 영어 객관식 문제 변형 예시
                    new_problem["content"] = self._modify_english_mcq(original_content)
                elif "수학" in subject:
                    # 수학 객관식 문제 변형 예시
                    new_problem["content"] = self._modify_math_mcq(original_content)
                else:
                    # 일반 변형
                    new_problem["content"] = f"변형 문제: {original_content}"
            else:
                # 주관식 문제 변형
                new_problem["content"] = f"변형된 주관식 문제: {original_content}"
                
        elif variation_type == "difficulty_up":
            # 난이도 상향 문제
            new_problem["content"] = f"[난이도 상향] {original_content}"
            new_problem["difficulty"] = "고급"
            
        elif variation_type == "difficulty_down":
            # 난이도 하향 문제
            new_problem["content"] = f"[난이도 하향] {original_content}"
            new_problem["difficulty"] = "초급"
            
        new_problem["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return new_problem
    
    def _generate_with_api(self, base_problem, variation_type):
        """API를 사용한 문제 생성"""
        # API 키와 라이브러리가 있는지 다시 확인
        if not self.api_key or not GEMINI_AVAILABLE:
            raise Exception("API 키 또는 라이브러리가 설정되지 않았습니다.")
            
        try:
            # 모델 설정
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # 프롬프트 구성
            prompt = self._build_prompt(base_problem, variation_type)
            
            # API 호출
            response = model.generate_content(prompt)
            
            # 응답 처리
            new_problem = self._parse_api_response(response.text, base_problem, variation_type)
            return new_problem
            
        except Exception as e:
            raise Exception(f"API 호출 중 오류: {str(e)}")
    
    def _build_prompt(self, base_problem, variation_type):
        """API 호출을 위한 프롬프트 구성"""
        subject = base_problem.get('subject', '영어')
        problem_type = base_problem.get('problem_type', '객관식')
        original_content = base_problem.get('content', '')
        
        # 변형 유형에 따른 지시문
        variation_instruction = ""
        if variation_type == "similar":
            variation_instruction = "유사한 난이도로 내용만 조금 다른"
        elif variation_type == "difficulty_up":
            variation_instruction = "더 어려운 난이도의"
        elif variation_type == "difficulty_down":
            variation_instruction = "더 쉬운 난이도의"
        
        prompt = f"""
다음 {subject} {problem_type} 문제를 {variation_instruction} 새로운 문제로 변형해주세요:

원본 문제:
{original_content}

{base_problem.get('options', [])}

정답: {base_problem.get('answer', '')}

JSON 형식으로 다음 필드를 포함하여 응답해주세요:
- content: 새 문제 내용
- options: 객관식인 경우 보기 목록 (배열)
- answer: 정답
"""
        return prompt
    
    def _parse_api_response(self, response_text, base_problem, variation_type):
        """API 응답 파싱"""
        # 기본 구조 복사
        new_problem = base_problem.copy()
        new_problem["id"] = str(uuid.uuid4())
        
        # 변형 유형에 따른 제목 설정
        if variation_type == "similar":
            new_problem["title"] = f"{base_problem.get('title', '문제')} - 유사 변형"
        elif variation_type == "difficulty_up":
            new_problem["title"] = f"{base_problem.get('title', '문제')} - 난이도 상향"
            new_problem["difficulty"] = "고급"
        elif variation_type == "difficulty_down":
            new_problem["title"] = f"{base_problem.get('title', '문제')} - 난이도 하향"
            new_problem["difficulty"] = "초급"
        
        new_problem["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # JSON 응답 추출 시도
        try:
            # JSON 형식 찾기
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                parsed_data = json.loads(json_str)
                
                # 필드 업데이트
                if 'content' in parsed_data:
                    new_problem['content'] = parsed_data['content']
                if 'options' in parsed_data:
                    new_problem['options'] = parsed_data['options']
                if 'answer' in parsed_data:
                    new_problem['answer'] = parsed_data['answer']
            else:
                # JSON이 없으면 텍스트 처리
                lines = response_text.split('\n')
                content_lines = []
                options = []
                answer = ""
                
                in_content = True
                for line in lines:
                    if line.startswith('- ') and in_content:
                        # 보기 시작
                        in_content = False
                    
                    if in_content:
                        if line and not line.startswith('원본 문제:') and not line.startswith('JSON'):
                            content_lines.append(line)
                    elif line.startswith('- '):
                        options.append(line[2:].strip())
                    elif line.startswith('정답:'):
                        answer = line[3:].strip()
                
                if content_lines:
                    new_problem['content'] = '\n'.join(content_lines).strip()
                if options:
                    new_problem['options'] = options
                if answer:
                    new_problem['answer'] = answer
        
        except Exception as e:
            print(f"API 응답 파싱 오류: {str(e)}")
            # 파싱 실패 시 원본 텍스트로 설정
            new_problem['content'] = f"변형 문제: {response_text[:200]}..."
        
        return new_problem
    
    def _modify_english_mcq(self, content):
        """영어 객관식 문제 변형"""
        # 간단한 변형 로직 구현
        if "I" in content:
            return content.replace("I", "You")
        elif "is" in content:
            return content.replace("is", "are")
        elif "have" in content:
            return content.replace("have", "has")
        else:
            # 기본 변형
            replacements = {
                "the": "a", "a": "the",
                "was": "were", "were": "was",
                "today": "yesterday", "yesterday": "today",
                "go": "come", "come": "go"
            }
            
            for old, new in replacements.items():
                if old in content:
                    return content.replace(old, new)
            
            return f"새로운 형태: {content}"
    
    def _modify_math_mcq(self, content):
        """수학 객관식 문제 변형"""
        # 숫자 변형 (간단한 예시)
        import re
        
        # 숫자 찾기
        numbers = re.findall(r'\d+', content)
        if numbers:
            # 첫 번째 숫자 변경
            old_num = numbers[0]
            new_num = str(int(old_num) + 1)
            return content.replace(old_num, new_num, 1)
        
        return f"수정된 수학 문제: {content}"

class ProblemTemplateGenerator:
    """
    템플릿 기반 문제 생성기
    """
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """템플릿 로드"""
        default_templates = {
            "영어_객관식": [
                {
                    "title": "영어 단어 선택",
                    "template": "다음 문장의 빈칸에 들어갈 가장 적절한 단어는?\n\nI _____ my homework, so I can go to the movies now.",
                    "options": ["finish", "finished", "have finished", "am finishing"],
                    "answer": "have finished"
                },
                {
                    "title": "영어 문법",
                    "template": "다음 중 문법적으로 올바른 문장은?",
                    "options": [
                        "She have been working here for 3 years.",
                        "She has been working here for 3 years.", 
                        "She has working here for 3 years.",
                        "She having been work here for 3 years."
                    ],
                    "answer": "She has been working here for 3 years."
                }
            ],
            "수학_객관식": [
                {
                    "title": "방정식 풀이",
                    "template": "방정식 3x + 6 = 15의 해는?",
                    "options": ["2", "3", "4", "5"],
                    "answer": "3"
                },
                {
                    "title": "함수의 최댓값",
                    "template": "함수 f(x) = -x² + 4x - 3의 최댓값은?",
                    "options": ["0", "1", "2", "3"],
                    "answer": "1"
                }
            ],
            "영어_주관식": [
                {
                    "title": "영어 에세이",
                    "template": "다음 주제에 대해 100단어 내외로 영작하시오: 'My favorite hobby'"
                },
                {
                    "title": "영어 번역",
                    "template": "다음 문장을 영어로 번역하시오: '나는 내일 친구를 만나기로 약속했다.'"
                }
            ],
            "수학_주관식": [
                {
                    "title": "미분 문제",
                    "template": "함수 f(x) = x³ - 3x² + 2x - 1의 도함수를 구하시오."
                },
                {
                    "title": "적분 문제",
                    "template": "∫(2x + 3)dx의 부정적분을 구하시오."
                }
            ]
        }
        return default_templates
    
    def get_template_categories(self):
        """템플릿 카테고리 목록 반환"""
        return list(self.templates.keys())
    
    def get_templates_by_category(self, category):
        """카테고리별 템플릿 목록 반환"""
        return self.templates.get(category, [])
    
    def generate_from_template(self, template, customizations=None):
        """템플릿 기반 문제 생성"""
        if not template:
            return None
        
        new_problem = {
            "id": str(uuid.uuid4()),
            "title": template.get("title", "새 문제"),
            "content": template.get("template", ""),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 과목과 유형 설정
        if "_" in template.get("category", ""):
            subject, problem_type = template.get("category", "기타_객관식").split("_")
            new_problem["subject"] = subject
            new_problem["problem_type"] = problem_type
        
        # 객관식인 경우 보기와 정답 추가
        if "options" in template:
            new_problem["options"] = template.get("options", [])
            new_problem["problem_type"] = "객관식"
        
        if "answer" in template:
            new_problem["answer"] = template.get("answer", "")
        
        # 사용자 정의 내용 적용
        if customizations:
            for key, value in customizations.items():
                if key in new_problem and value:
                    new_problem[key] = value
        
        return new_problem

def generate_sample_problems():
    """샘플 문제 생성"""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "중학 영어 - 현재완료 시제",
            "content": "다음 문장의 빈칸에 들어갈 가장 적절한 표현은?\n\nI _____ my homework, so I can go to the movies now.",
            "options": "finish, finished, have finished, am finishing",
            "answer": "have finished",
            "subject": "영어",
            "problem_type": "객관식",
            "difficulty": "중급",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": "admin"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "고등 수학 - 미분",
            "content": "함수 f(x) = x^2 + 2x - 1의 도함수 f'(x)는?",
            "options": "2x + 1, 2x + 2, 2x - 1, x^2 + 2",
            "answer": "2x + 2",
            "subject": "수학",
            "problem_type": "객관식",
            "difficulty": "고급",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": "admin"
        }
    ] 