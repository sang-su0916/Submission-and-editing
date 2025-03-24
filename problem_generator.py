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
                    'title': '중급 영어 어휘 문제',
                    'content': '''다음 빈칸에 들어갈 가장 적절한 단어를 고르시오.

The company has been ________ its products to international markets for over a decade.
a) exporting
b) exported
c) exports
d) export''',
                    'answer': 'a) exporting'
                },
                '고급': {
                    'title': '고급 영어 어휘 문제',
                    'content': '''다음 빈칸에 들어갈 가장 적절한 단어를 고르시오.

The professor's ________ lecture on quantum physics left many students bewildered by its complexity.
a) abstruse
b) lucid
c) rudimentary
d) transparent''',
                    'answer': 'a) abstruse'
                }
            },
            '문법': {
                '초급': {
                    'title': '기초 영어 문법 문제',
                    'content': '''다음 문장의 괄호 안에 들어갈 가장 적절한 표현을 고르시오.

She (______) television when I called her yesterday.
a) watched
b) was watching
c) has watched
d) watches''',
                    'answer': 'b) was watching'
                },
                '중급': {
                    'title': '중급 영어 문법 문제',
                    'content': '''다음 문장의 괄호 안에 들어갈 가장 적절한 표현을 고르시오.

If I ________ the lottery, I would buy a new house.
a) win
b) won
c) had won
d) would win''',
                    'answer': 'b) won'
                },
                '고급': {
                    'title': '고급 영어 문법 문제',
                    'content': '''다음 문장의 괄호 안에 들어갈 가장 적절한 표현을 고르시오.

Not only ________ the exam, but she also received the highest score in the class.
a) she passed
b) did she pass
c) she did pass
d) passed she''',
                    'answer': 'b) did she pass'
                }
            },
            '독해': {
                '초급': {
                    'title': '기초 영어 독해 문제',
                    'content': '''다음 글을 읽고 물음에 답하시오.

Tom likes to play sports. He plays soccer on Mondays and Wednesdays. He plays basketball on Tuesdays and Thursdays. On Fridays, he goes swimming. On weekends, he rests at home.

질문: What sport does Tom play on Tuesday?
a) Soccer
b) Basketball
c) Swimming
d) He doesn't play sports on Tuesday''',
                    'answer': 'b) Basketball'
                },
                '중급': {
                    'title': '중급 영어 독해 문제',
                    'content': '''다음 글을 읽고 물음에 답하시오.

Coffee is one of the world's most popular beverages. It is grown in many countries, including Brazil, Colombia, and Ethiopia. Coffee beans are actually seeds from the coffee plant. These seeds are roasted to varying degrees to create different flavors. The two main types of coffee beans are Arabica and Robusta. Arabica beans are known for their smooth, complex flavor, while Robusta beans have a stronger, more bitter taste.

이 글의 주제로 가장 적절한 것은?
a) 커피의 역사와 발전
b) 커피의 종류와 특성
c) 커피 재배 국가의 경제
d) 커피 소비의 건강상 영향''',
                    'answer': 'b) 커피의 종류와 특성'
                },
                '고급': {
                    'title': '고급 영어 독해 문제',
                    'content': '''다음 글을 읽고 물음에 답하시오.

The concept of emotional intelligence, popularized by psychologist Daniel Goleman, encompasses the ability to recognize, understand, and manage our own emotions, as well as recognize, understand, and influence the emotions of others. Unlike IQ, which remains relatively stable throughout life, emotional intelligence can be developed and improved with practice and attention. Research suggests that emotional intelligence may be a better predictor of success in many areas of life than traditional measures of intelligence. In the workplace, individuals with high emotional intelligence often excel in leadership positions, as they can effectively navigate complex social dynamics and inspire others.

글의 요지로 가장 적절한 것은?
a) 감성지능은 전통적인 지능 측정보다 성공을 더 잘 예측할 수 있다.
b) 감성지능은 IQ와 달리 개발하고 향상시킬 수 있다.
c) 감성지능이 높은 사람들은 리더십 위치에서 뛰어난 성과를 보인다.
d) 감성지능은 자신과 타인의 감정을 인식하고 관리하는 능력이다.''',
                    'answer': 'a) 감성지능은 전통적인 지능 측정보다 성공을 더 잘 예측할 수 있다.'
                }
            },
            '작문': {
                '초급': {
                    'title': '기초 영어 작문 문제',
                    'content': '''다음 주제에 대해 5문장 이상의 영어 문단을 작성하시오.

Topic: My favorite hobby''',
                    'answer': '''Sample answer:
My favorite hobby is reading books. I enjoy reading various genres, including fiction, non-fiction, and poetry. Reading helps me learn new things and improves my vocabulary. I try to read at least one book every week. This hobby has been a great way for me to relax and escape from daily stress.'''
                },
                '중급': {
                    'title': '중급 영어 작문 문제',
                    'content': '''다음 주제에 대해 100단어 내외의 영어 에세이를 작성하시오.

Topic: The importance of exercise''',
                    'answer': '''Sample answer:
Regular exercise is crucial for maintaining both physical and mental health. Physically, it helps control weight, reduces the risk of heart disease, and strengthens muscles and bones. Mentally, exercise releases endorphins that improve mood and reduce stress. It can also enhance cognitive function and memory. Despite these benefits, many people struggle to incorporate exercise into their daily routines due to busy schedules or lack of motivation. However, even small amounts of physical activity, such as a 30-minute walk each day, can significantly improve overall health and well-being. Therefore, making exercise a priority is an essential investment in one's long-term health.'''
                },
                '고급': {
                    'title': '고급 영어 작문 문제',
                    'content': '''다음 주제에 대해 200단어 내외의 영어 에세이를 작성하시오. 서론, 본론, 결론 구조를 갖추고, 적절한 예시와 근거를 포함하시오.

Topic: The impact of social media on modern communication''',
                    'answer': '''Sample answer:
The advent of social media has fundamentally transformed how humans communicate in the 21st century, bringing both unprecedented opportunities and significant challenges. This essay examines the multifaceted impact of social media platforms on modern communication patterns.

Social media has democratized communication by removing traditional barriers to information sharing. Individuals can now broadcast their thoughts to global audiences instantly, facilitating movements like #MeToo and Arab Spring that might have struggled to gain traction in pre-digital eras. Furthermore, these platforms have created new avenues for maintaining relationships across vast distances, allowing people to preserve connections that might otherwise fade due to geographic separation.

However, this communication revolution comes with substantial costs. The brevity encouraged by platforms like Twitter has led to a simplification of complex issues, while algorithm-driven content curation creates echo chambers that reinforce existing beliefs rather than challenging them. Moreover, the replacement of face-to-face interaction with digital communication has been linked to declining empathy and social skills, particularly among younger generations who have grown up immersed in social media environments.

In conclusion, while social media has expanded our ability to connect across boundaries, it has simultaneously altered the quality and depth of those connections. As these platforms continue to evolve, society must critically evaluate their impact and develop strategies to maximize their benefits while mitigating their detrimental effects on meaningful human communication.'''
                }
            },
            '듣기': {
                '초급': {
                    'title': '기초 영어 듣기 문제',
                    'content': '''다음 대화를 듣고 질문에 답하시오. (실제 앱에서는 오디오 파일이 제공됩니다)

Woman: Excuse me, what time does the movie start?
Man: It starts at 7:30 PM.
Woman: And how long is it?
Man: It's about two hours.
Woman: Thank you.

질문: 영화는 몇 시에 시작하나요?
a) 6:30 PM
b) 7:00 PM
c) 7:30 PM
d) 8:00 PM''',
                    'answer': 'c) 7:30 PM'
                },
                '중급': {
                    'title': '중급 영어 듣기 문제',
                    'content': '''다음 대화를 듣고 질문에 답하시오. (실제 앱에서는 오디오 파일이 제공됩니다)

Woman: I'm thinking about taking a vacation next month. Do you have any suggestions?
Man: Well, it depends on what you're looking for. If you want beaches and warm weather, I'd recommend Hawaii or Florida.
Woman: I was actually hoping for something more cultural, like museums and historical sites.
Man: In that case, you might enjoy visiting Rome or Paris. They both have amazing architecture and world-class museums.
Woman: Paris sounds perfect! I've always wanted to see the Louvre.
Man: Great choice! The best time to visit is during the spring or fall when there are fewer tourists.

여자가 휴가지로 선택한 곳은 어디인가요?
a) 하와이
b) 플로리다
c) 로마
d) 파리''',
                    'answer': 'd) 파리'
                },
                '고급': {
                    'title': '고급 영어 듣기 문제',
                    'content': '''다음 강연을 듣고 질문에 답하시오. (실제 앱에서는 오디오 파일이 제공됩니다)

"Today I'd like to discuss the concept of 'planned obsolescence' in modern manufacturing. Planned obsolescence is a business strategy in which the obsolescence of a product is planned and built into it from its conception. This is done so that in the future the consumer feels a need to purchase new products and services that the manufacturer brings out as replacements for the old ones. There are several types of planned obsolescence, including technical obsolescence, where products are designed to break down or become less useful over time, and style obsolescence, where products go out of fashion or appear less desirable. Critics argue that planned obsolescence is wasteful and environmentally harmful, as it leads to more products being discarded. Defenders, however, claim that it drives innovation and economic growth by encouraging the development of new and improved products."

강연의 주제로 가장 적절한 것은?
a) 현대 제조업의 환경적 영향
b) 계획된 노후화의 개념과 그 영향
c) 소비자 행동 패턴의 변화
d) 지속 가능한 제조 관행의 중요성''',
                    'answer': 'b) 계획된 노후화의 개념과 그 영향'
                }
            }
        }
        
        # 요청된 문제 유형과 난이도에 대한 템플릿 반환
        if problem_type in templates and difficulty in templates[problem_type]:
            template = templates[problem_type][difficulty].copy()
            template['subject'] = '영어'
            template['problem_type'] = problem_type
            template['difficulty'] = difficulty
            template['created_by'] = '시스템'
            return template
        
        # 기본 템플릿 반환
        return self._get_default_template('영어', problem_type, difficulty)
    
    def _get_math_template(self, problem_type, difficulty):
        """수학 과목 템플릿"""
        templates = {
            '대수': {
                '초급': {
                    'title': '기초 대수 문제',
                    'content': '''다음 방정식을 풀어 x의 값을 구하시오.

2x + 5 = 15''',
                    'answer': 'x = 5'
                },
                '중급': {
                    'title': '중급 대수 문제',
                    'content': '''다음 연립방정식을 풀어 x와 y의 값을 구하시오.

3x + 2y = 13
x - y = 1''',
                    'answer': 'x = 3, y = 2'
                },
                '고급': {
                    'title': '고급 대수 문제',
                    'content': '''다음 이차방정식의 근을 구하시오.

2x² - 5x - 3 = 0''',
                    'answer': 'x = 3 또는 x = -1/2'
                }
            },
            '기하': {
                '초급': {
                    'title': '기초 기하 문제',
                    'content': '''가로 길이가 8cm, 세로 길이가 5cm인 직사각형의 넓이와 둘레를 구하시오.''',
                    'answer': '넓이: 40cm², 둘레: 26cm'
                },
                '중급': {
                    'title': '중급 기하 문제',
                    'content': '''반지름이 6cm인 원에 내접하는 정사각형의 한 변의 길이를 구하시오.''',
                    'answer': '한 변의 길이: 6√2 cm ≈ 8.49cm'
                },
                '고급': {
                    'title': '고급 기하 문제',
                    'content': '''삼각형 ABC에서 각 A = 30°, 각 B = 45°, 변 AB = 10cm일 때, 변 BC의 길이를 구하시오.''',
                    'answer': 'BC = 10 × sin(30°) / sin(105°) ≈ 5.35cm'
                }
            },
            '미적분': {
                '초급': {
                    'title': '기초 미적분 문제',
                    'content': '''다음 함수를 미분하시오.

f(x) = 3x² + 2x - 5''',
                    'answer': 'f\'(x) = 6x + 2'
                },
                '중급': {
                    'title': '중급 미적분 문제',
                    'content': '''다음 함수를 적분하시오.

∫(2x³ + 3x² - 4x + 1)dx''',
                    'answer': '(1/2)x⁴ + x³ - 2x² + x + C (C는 적분상수)'
                },
                '고급': {
                    'title': '고급 미적분 문제',
                    'content': '''다음 정적분의 값을 구하시오.

∫₀^π sin²(x)dx''',
                    'answer': 'π/2'
                }
            },
            '확률과 통계': {
                '초급': {
                    'title': '기초 확률 문제',
                    'content': '''주사위를 한 번 던질 때, 짝수가 나올 확률을 구하시오.''',
                    'answer': '3/6 = 1/2 = 0.5'
                },
                '중급': {
                    'title': '중급 확률 문제',
                    'content': '''주머니에 빨간 공 3개, 파란 공 2개, 노란 공 1개가 들어있다. 이 주머니에서 무작위로 2개의 공을 동시에 꺼낼 때, 두 공의 색이 다를 확률을 구하시오.''',
                    'answer': '4/5 = 0.8'
                },
                '고급': {
                    'title': '고급 통계 문제',
                    'content': '''다음 데이터의 평균, 중앙값, 표준편차를 구하시오.

7, 12, 8, 15, 9, 11, 10''',
                    'answer': '평균: 10.29, 중앙값: 10, 표준편차: 약 2.69'
                }
            },
            '수열': {
                '초급': {
                    'title': '기초 수열 문제',
                    'content': '''다음 수열의 첫 5개 항을 구하시오.

a_n = 2n + 1''',
                    'answer': '3, 5, 7, 9, 11'
                },
                '중급': {
                    'title': '중급 수열 문제',
                    'content': '''다음 수열의 일반항을 구하시오.

2, 6, 12, 20, 30, ...''',
                    'answer': 'a_n = n(n+1)'
                },
                '고급': {
                    'title': '고급 수열 문제',
                    'content': '''피보나치 수열에서 20번째 항을 구하시오. (피보나치 수열은 F₁ = 1, F₂ = 1이고, n ≥ 3일 때 F_n = F_{n-1} + F_{n-2}로 정의됩니다.)''',
                    'answer': 'F₂₀ = 6765'
                }
            }
        }
        
        # 요청된 문제 유형과 난이도에 대한 템플릿 반환
        if problem_type in templates and difficulty in templates[problem_type]:
            template = templates[problem_type][difficulty].copy()
            template['subject'] = '수학'
            template['problem_type'] = problem_type
            template['difficulty'] = difficulty
            template['created_by'] = '시스템'
            return template
        
        # 기본 템플릿 반환
        return self._get_default_template('수학', problem_type, difficulty)
    
    def _get_default_template(self, subject, problem_type, difficulty):
        """기본 템플릿"""
        return {
            'subject': subject,
            'problem_type': problem_type,
            'difficulty': difficulty,
            'title': f'{subject} {problem_type} {difficulty} 문제',
            'content': f'이것은 {subject} 과목의 {problem_type} 유형 {difficulty} 난이도 문제 템플릿입니다. 실제 문제 내용을 입력해주세요.',
            'answer': '정답을 입력해주세요.',
            'created_by': '시스템'
        }
