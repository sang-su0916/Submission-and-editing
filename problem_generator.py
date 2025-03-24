import random
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# 간단한 문장 분리 함수
def simple_sent_tokenize(text):
    """
    간단한 문장 분리 함수
    """
    # 마침표, 물음표, 느낌표로 문장 분리
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # 빈 문장 제거
    return [s for s in sentences if s.strip()]

# 간단한 단어 분리 함수
def simple_word_tokenize(text):
    """
    간단한 단어 분리 함수
    """
    # 공백과 구두점으로 단어 분리
    words = re.findall(r'\b\w+\b', text.lower())
    return words

# 간단한 품사 태깅 함수 (명사, 동사, 형용사만 구분)
def simple_pos_tag(words):
    """
    간단한 품사 태깅 함수
    """
    # 영어 품사 사전 (간단한 예시)
    noun_list = ['weather', 'picnic', 'park', 'movie', 'book', 'student', 'teacher', 'school', 'house', 'car']
    verb_list = ['go', 'have', 'do', 'make', 'see', 'say', 'get', 'find', 'take', 'know', 'decided']
    adj_list = ['nice', 'good', 'bad', 'happy', 'sad', 'big', 'small', 'hot', 'cold', 'new', 'old']
    
    tagged_words = []
    for word in words:
        if word in noun_list:
            tagged_words.append((word, 'NN'))
        elif word in verb_list:
            tagged_words.append((word, 'VB'))
        elif word in adj_list:
            tagged_words.append((word, 'JJ'))
        else:
            tagged_words.append((word, 'OTHER'))
    
    return tagged_words

# 간단한 유의어 사전
synonyms_dict = {
    'nice': ['pleasant', 'lovely', 'wonderful', 'delightful'],
    'good': ['great', 'excellent', 'fine', 'superb'],
    'bad': ['poor', 'terrible', 'awful', 'horrible'],
    'happy': ['glad', 'joyful', 'pleased', 'delighted'],
    'sad': ['unhappy', 'sorrowful', 'depressed', 'gloomy'],
    'big': ['large', 'huge', 'enormous', 'massive'],
    'small': ['little', 'tiny', 'miniature', 'petite'],
    'hot': ['warm', 'heated', 'burning', 'fiery'],
    'cold': ['cool', 'chilly', 'freezing', 'icy'],
    'go': ['move', 'travel', 'proceed', 'advance'],
    'have': ['possess', 'own', 'hold', 'maintain'],
    'see': ['observe', 'view', 'witness', 'notice'],
    'make': ['create', 'produce', 'form', 'construct'],
    'find': ['discover', 'locate', 'uncover', 'detect'],
    'decided': ['determined', 'resolved', 'concluded', 'settled'],
    'weather': ['climate', 'conditions', 'atmosphere', 'elements'],
    'picnic': ['outing', 'excursion', 'trip', 'expedition'],
    'park': ['garden', 'grounds', 'area', 'field'],
    'movie': ['film', 'picture', 'cinema', 'show'],
    'book': ['volume', 'publication', 'text', 'work'],
    'student': ['pupil', 'learner', 'scholar', 'apprentice'],
    'teacher': ['instructor', 'educator', 'tutor', 'mentor'],
    'school': ['academy', 'institution', 'college', 'university'],
    'house': ['home', 'residence', 'dwelling', 'abode'],
    'car': ['vehicle', 'automobile', 'auto', 'motorcar']
}

class ProblemGenerator:
    """
    기존 문제를 기반으로 새로운 문제를 생성하는 클래스
    """
    def __init__(self):
        pass
    
    def generate_problem(self, original_problem, strategy='synonym_replacement', difficulty_change=0):
        """
        기존 문제를 기반으로 새로운 문제 생성
        
        Args:
            original_problem (dict): 원본 문제 데이터
            strategy (str): 문제 생성 전략 ('synonym_replacement', 'sentence_structure', 'difficulty_adjustment')
            difficulty_change (int): 난이도 변경 정도 (-1: 쉽게, 0: 유지, 1: 어렵게)
            
        Returns:
            dict: 생성된 새 문제 데이터
        """
        # 원본 문제 복사
        new_problem = original_problem.copy()
        
        # ID는 새로 생성될 것이므로 제거
        if 'id' in new_problem:
            del new_problem['id']
        
        # 제목 변경
        new_problem['title'] = f"변형 - {original_problem['title']}"
        
        # 문제 내용 변경
        if strategy == 'synonym_replacement':
            new_problem['content'] = self._apply_synonym_replacement(original_problem['content'])
        elif strategy == 'sentence_structure':
            new_problem['content'] = self._apply_sentence_restructure(original_problem['content'])
        elif strategy == 'difficulty_adjustment':
            new_problem['content'] = self._adjust_difficulty(original_problem['content'], difficulty_change)
            
            # 난이도 조정
            difficulties = ['초급', '중급', '고급']
            current_idx = difficulties.index(original_problem['difficulty'])
            new_idx = max(0, min(2, current_idx + difficulty_change))
            new_problem['difficulty'] = difficulties[new_idx]
        
        # 정답 변경 (필요한 경우)
        if strategy == 'synonym_replacement' and original_problem['subject'] == '영어':
            new_problem['answer'] = self._adjust_answer_for_synonym(original_problem['answer'], original_problem['content'], new_problem['content'])
        elif strategy == 'difficulty_adjustment':
            new_problem['answer'] = self._adjust_answer_for_difficulty(original_problem['answer'], difficulty_change)
        
        return new_problem
    
    def _apply_synonym_replacement(self, text):
        """단어를 유의어로 대체하는 함수"""
        sentences = simple_sent_tokenize(text)
        new_sentences = []
        
        for sentence in sentences:
            # 문장에서 단어 토큰화
            words = simple_word_tokenize(sentence)
            
            # 품사 태깅
            tagged_words = simple_pos_tag(words)
            
            new_words = []
            for word, tag in tagged_words:
                # 명사, 동사, 형용사만 대체
                if tag in ['NN', 'VB', 'JJ']:
                    # 50% 확률로 유의어 대체
                    if random.random() < 0.5:
                        synonym = self._get_synonym(word)
                        if synonym:
                            new_words.append(synonym)
                        else:
                            new_words.append(word)
                    else:
                        new_words.append(word)
                else:
                    new_words.append(word)
            
            # 문장 재구성
            new_sentence = ' '.join(new_words)
            
            # 기본적인 문장 교정
            new_sentence = self._fix_sentence(new_sentence)
            
            new_sentences.append(new_sentence)
        
        return ' '.join(new_sentences)
    
    def _apply_sentence_restructure(self, text):
        """문장 구조를 변경하는 함수"""
        # 문제 유형에 따라 다른 처리
        if "다음 빈칸에 들어갈" in text or "빈칸에 들어갈" in text:
            return self._restructure_fill_in_blank(text)
        elif "보기" in text and ("고르시오" in text or "고르세요" in text):
            return self._restructure_multiple_choice(text)
        else:
            return self._restructure_general_text(text)
    
    def _restructure_fill_in_blank(self, text):
        """빈칸 채우기 문제 구조 변경"""
        # 지문과 선택지 분리
        parts = re.split(r'[a-d]\)', text, flags=re.IGNORECASE)
        
        if len(parts) > 1:
            passage = parts[0]
            options = re.findall(r'[a-d]\)(.*?)(?=[a-d]\)|$)', text, flags=re.IGNORECASE)
            
            # 선택지 순서 변경
            random.shuffle(options)
            
            # 새 문제 구성
            new_text = passage
            for i, option in enumerate(options):
                new_text += f"{chr(97+i)}) {option.strip()}"
                if i < len(options) - 1:
                    new_text += "\n"
            
            return new_text
        
        return text
    
    def _restructure_multiple_choice(self, text):
        """객관식 문제 구조 변경"""
        # 지문과 선택지 분리
        match = re.search(r'(.*?)([a-d]\).*)', text, flags=re.DOTALL | re.IGNORECASE)
        
        if match:
            passage = match.group(1)
            options_text = match.group(2)
            
            # 선택지 추출
            options = re.findall(r'([a-d]\).*?)(?=[a-d]\)|$)', options_text, flags=re.IGNORECASE | re.DOTALL)
            
            # 선택지 순서 변경
            random.shuffle(options)
            
            # 새 문제 구성
            new_text = passage + ''.join(options)
            
            return new_text
        
        return text
    
    def _restructure_general_text(self, text):
        """일반 텍스트 구조 변경"""
        sentences = simple_sent_tokenize(text)
        
        # 문장 순서 일부 변경 (첫 문장과 마지막 문장은 유지)
        if len(sentences) > 3:
            middle_sentences = sentences[1:-1]
            random.shuffle(middle_sentences)
            new_sentences = [sentences[0]] + middle_sentences + [sentences[-1]]
            return ' '.join(new_sentences)
        
        return text
    
    def _adjust_difficulty(self, text, difficulty_change):
        """난이도 조정 함수"""
        if difficulty_change == 0:
            return text
        
        sentences = simple_sent_tokenize(text)
        new_sentences = []
        
        for sentence in sentences:
            if difficulty_change > 0:
                # 난이도 증가: 문장 복잡화
                new_sentence = self._increase_difficulty(sentence)
            else:
                # 난이도 감소: 문장 단순화
                new_sentence = self._decrease_difficulty(sentence)
            
            new_sentences.append(new_sentence)
        
        return ' '.join(new_sentences)
    
    def _increase_difficulty(self, sentence):
        """문장 난이도 증가"""
        words = simple_word_tokenize(sentence)
        tagged_words = simple_pos_tag(words)
        
        new_words = []
        for word, tag in tagged_words:
            # 명사, 동사, 형용사를 더 어려운 단어로 대체
            if tag.startswith('N') or tag.startswith('V') or tag.startswith('J'):
                complex_word = self._get_complex_synonym(word)
                if complex_word:
                    new_words.append(complex_word)
                else:
                    new_words.append(word)
            else:
                new_words.append(word)
        
        new_sentence = ' '.join(new_words)
        return self._fix_sentence(new_sentence)
    
    def _decrease_difficulty(self, sentence):
        """문장 난이도 감소"""
        words = simple_word_tokenize(sentence)
        tagged_words = simple_pos_tag(words)
        
        new_words = []
        for word, tag in tagged_words:
            # 명사, 동사, 형용사를 더 쉬운 단어로 대체
            if tag.startswith('N') or tag.startswith('V') or tag.startswith('J'):
                simple_word = self._get_simple_synonym(word)
                if simple_word:
                    new_words.append(simple_word)
                else:
                    new_words.append(word)
            else:
                new_words.append(word)
        
        new_sentence = ' '.join(new_words)
        return self._fix_sentence(new_sentence)
    
    def _get_synonym(self, word):
        """단어의 유의어 반환"""
        word = word.lower()
        if word in synonyms_dict:
            return random.choice(synonyms_dict[word])
        return None
    
    def _get_complex_synonym(self, word):
        """더 복잡한 유의어 반환"""
        word = word.lower()
        if word in synonyms_dict:
            # 원래 단어보다 긴 유의어 선택
            longer_synonyms = [syn for syn in synonyms_dict[word] if len(syn) > len(word)]
            if longer_synonyms:
                return random.choice(longer_synonyms)
        return None
    
    def _get_simple_synonym(self, word):
        """더 단순한 유의어 반환"""
        word = word.lower()
        if word in synonyms_dict:
            # 원래 단어보다 짧거나 같은 길이의 유의어 선택
            simpler_synonyms = [syn for syn in synonyms_dict[word] if len(syn) <= len(word)]
            if simpler_synonyms:
                return random.choice(simpler_synonyms)
        return None
    
    def _fix_sentence(self, sentence):
        """기본적인 문장 교정"""
        # 첫 글자 대문자화
        if sentence and sentence[0].isalpha():
            sentence = sentence[0].upper() + sentence[1:]
        
        # 마침표 확인
        if sentence and not sentence.endswith(('.', '?', '!')):
            sentence += '.'
        
        # 공백 정리
        sentence = re.sub(r'\s+', ' ', sentence)
        sentence = re.sub(r'\s([.,;:!?])', r'\1', sentence)
        
        return sentence
    
    def _adjust_answer_for_synonym(self, answer, original_content, new_content):
        """유의어 대체에 따른 정답 조정"""
        # 객관식 문제인 경우
        if re.search(r'[a-d]\)', answer, flags=re.IGNORECASE):
            # 원본 문제에서 정답 옵션 찾기
            answer_option = re.search(r'([a-d])\)', answer, flags=re.IGNORECASE).group(1).lower()
            
            # 원본 문제의 선택지들
            original_options = re.findall(r'([a-d])\)(.*?)(?=[a-d]\)|$)', original_content, flags=re.IGNORECASE | re.DOTALL)
            
            # 새 문제의 선택지들
            new_options = re.findall(r'([a-d])\)(.*?)(?=[a-d]\)|$)', new_content, flags=re.IGNORECASE | re.DOTALL)
            
            if original_options and new_options:
                # 원본 정답 내용 찾기
                original_answer_content = None
                for opt, content in original_options:
                    if opt.lower() == answer_option:
                        original_answer_content = content.strip()
                        break
                
                if original_answer_content:
                    # 새 문제에서 가장 유사한 선택지 찾기
                    vectorizer = TfidfVectorizer()
                    
                    # 선택지 내용만 추출
                    option_contents = [content.strip() for _, content in new_options]
                    
                    if option_contents:
                        try:
                            # 원본 정답과 새 선택지들 간의 유사도 계산
                            tfidf_matrix = vectorizer.fit_transform([original_answer_content] + option_contents)
                            similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0][1:]
                            
                            # 가장 유사한 선택지 찾기
                            most_similar_idx = np.argmax(similarity)
                            new_answer_option = new_options[most_similar_idx][0].lower()
                            
                            return f"{new_answer_option}) {option_contents[most_similar_idx]}"
                        except:
                            pass
        
        return answer
    
    def _adjust_answer_for_difficulty(self, answer, difficulty_change):
        """난이도 변경에 따른 정답 조정"""
        # 수학 문제의 경우 난이도 변경에 따라 정답도 변경될 수 있음
        # 여기서는 간단한 예시만 구현
        
        # 숫자 값이 포함된 경우
        numbers = re.findall(r'\d+', answer)
        if numbers:
            new_answer = answer
            for num in numbers:
                # 난이도 증가: 숫자 값을 약간 변경
                if difficulty_change > 0:
                    new_num = str(int(num) + random.randint(1, 3))
                # 난이도 감소: 숫자 값을 단순화
                elif difficulty_change < 0:
                    new_num = str(max(1, int(num) - random.randint(1, 2)))
                else:
                    new_num = num
                
                new_answer = new_answer.replace(num, new_num, 1)
            
            return new_answer
        
        return answer


class ProblemTemplateGenerator:
    """
    문제 유형별 템플릿을 생성하는 클래스
    """
    def __init__(self):
        pass
    
    def get_template(self, subject, problem_type, difficulty):
        """
        과목, 문제 유형, 난이도에 따른 템플릿 반환
        
        Args:
            subject (str): 과목 ('영어', '수학')
            problem_type (str): 문제 유형
            difficulty (str): 난이도 ('초급', '중급', '고급')
            
        Returns:
            dict: 템플릿 문제 데이터
        """
        if subject == '영어':
            return self._get_english_template(problem_type, difficulty)
        elif subject == '수학':
            return self._get_math_template(problem_type, difficulty)
        else:
            return self._get_default_template(subject, problem_type, difficulty)
    
    def _get_english_template(self, problem_type, difficulty):
        """영어 과목 템플릿"""
        templates = {
            '어휘': {
                '초급': {
                    'title': '기초 영어 어휘 문제',
                    'content': '''다음 빈칸에 들어갈 가장 적절한 단어를 고르시오.

The students ________ to school every morning.
a) go
b) goes
c) going
d) went''',
                    'answer': 'a) go'
                },
                '중급': {
                    'tit<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>