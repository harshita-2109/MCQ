# Import required libraries
import os
import streamlit as st  
import pandas as pd    
from typing import List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator

# Load environment variables from .env file
load_dotenv()

# Define data model for Multiple Choice Questions using Pydantic
class MCQQuestion(BaseModel):
    # Define the structure of an MCQ with field descriptions
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 possible answers")
    correct_answer: str = Field(description="The correct answer from the options")

    # Custom validator to clean question text
    # Handles cases where question might be a dictionary or other format
    @validator('question', pre=True)
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)

# Define data model for Fill in the Blank Questions using Pydantic
class FillBlankQuestion(BaseModel):
    # Define the structure of a fill-in-the-blank question with field descriptions
    question: str = Field(description="The question text with '_____' for the blank")
    answer: str = Field(description="The correct word or phrase for the blank")

    # Custom validator to clean question text
    # Similar to MCQ validator, ensures consistent question format
    @validator('question', pre=True)
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)
    
# Improved QuizManager 

class QuizManager:
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []
        self.current_topic = None
        self.current_difficulty = None
        self.current_quiz_id = None  

    def reset_state(self):
        """Reset all quiz state when starting a new quiz"""
        self.questions = []
        self.user_answers = []
        self.results = []

        
    def generate_quiz_id(self, topic, question_type, difficulty):
        """Generate a unique ID for this quiz session"""
        import time
        import hashlib
        timestamp = str(time.time())
        quiz_str = f"{topic}_{question_type}_{difficulty}_{timestamp}"
        return hashlib.md5(quiz_str.encode()).hexdigest()[:8]

    def generate_questions(self, generator, topic, question_type, difficulty, num_questions):
        """Generate a new set of questions with complete state reset"""
        # Reset state completely for new quiz
        self.reset_state()
        
        # Set current quiz parameters
        self.current_topic = topic
        self.current_difficulty = difficulty
        self.current_quiz_id = self.generate_quiz_id(topic, question_type, difficulty)
        
        try:
            for _ in range(num_questions):
                if question_type == "Multiple Choice":
                    question = generator.generate_mcq(topic, difficulty.lower())
                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_answer': question.correct_answer,
                        'topic': topic,  # Store topic explicitly
                        'quiz_id': self.current_quiz_id  # Store quiz session ID
                    })
                else:
                    question = generator.generate_fill_blank(topic, difficulty.lower())
                    self.questions.append({
                        'type': 'Fill in the Blank',
                        'question': question.question,
                        'correct_answer': question.answer,
                        'topic': topic,  # Store topic explicitly
                        'quiz_id': self.current_quiz_id  # Store quiz session ID
                    })
            
            # Initialize user_answers list with placeholders
            self.user_answers = [[] if q['type'] == 'MCQ' else "" for q in self.questions]
            return True
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return False

    def attempt_quiz(self):
        """Display quiz questions for user to answer"""
        # Verify we're working with the correct quiz session
        for i, q in enumerate(self.questions):
            st.markdown(f"""
            <div class="question-card">
                <div class="question-number">Question {i+1}</div>
                <div class="question-text">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            if q['type'] == 'MCQ':
                # Create a unique key for this question's selections that includes quiz_id
                session_key = f"mcq_selections_{self.current_quiz_id}_{i}"
                
                if session_key not in st.session_state:
                    st.session_state[session_key] = {opt: False for opt in q['options']}
                
                st.write(f"Select answer(s) for Question {i+1}:")
                
                # Create a checkbox for each option and track selections
                for option in q['options']:
                    checkbox_key = f"mcq_option_{self.current_quiz_id}_{i}_{option}"
                    checkbox_state = st.checkbox(
                        option,
                        key=checkbox_key,
                        value=st.session_state[session_key].get(option, False)
                    )
                    st.session_state[session_key][option] = checkbox_state
                
                # Update user_answers with the current selected options
                selected_options = []
                for option, is_selected in st.session_state[session_key].items():
                    if is_selected:
                        selected_options.append(option)
                        
                # Store the current selections in the user_answers list
                self.user_answers[i] = selected_options
            else:
                # For fill in the blank questions - include quiz_id in key
                answer_key = f"fill_blank_{self.current_quiz_id}_{i}"
                if answer_key in st.session_state:
                    self.user_answers[i] = st.session_state[answer_key]
                
                user_answer = st.text_input(
                    f"Fill in the blank for Question {i+1}",
                    key=answer_key,
                    label_visibility="collapsed",
                    placeholder="Type your answer here..."
                )
                self.user_answers[i] = user_answer

    def evaluate_quiz(self):
        """Evaluate quiz answers and generate results"""
        self.results = []
        for i, (q, user_ans) in enumerate(zip(self.questions, self.user_answers)):
            if q['type'] == 'MCQ':
                # For MCQ with checkboxes, we need to check if the correct answer is among the selected options
                is_correct = q['correct_answer'] in user_ans if user_ans else False
                # Format the user's answer for display
                formatted_user_answer = ", ".join(user_ans) if user_ans and len(user_ans) > 0 else "No selection"
                
                result_dict = {
                    'question_number': i + 1,
                    'question': q['question'],
                    'question_type': q['type'],
                    'topic': q['topic'],  # Include topic for verification
                    'quiz_id': q['quiz_id'],  # Include quiz_id for verification
                    'user_answer': formatted_user_answer,
                    'correct_answer': q['correct_answer'],
                    'is_correct': is_correct,
                    'options': q['options']
                }
            else:
                # For fill in the blank, compare ignoring case and whitespace
                is_correct = user_ans.strip().lower() == q['correct_answer'].strip().lower() if user_ans else False
                result_dict = {
                    'question_number': i + 1,
                    'question': q['question'],
                    'question_type': q['type'],
                    'topic': q['topic'],  # Include topic for verification
                    'quiz_id': q['quiz_id'],  # Include quiz_id for verification
                    'user_answer': user_ans if user_ans else "No answer provided",
                    'correct_answer': q['correct_answer'],
                    'is_correct': is_correct,
                    'options': q['options'] if 'options' in q else []
                }
            self.results.append(result_dict)

    def generate_result_dataframe(self):
        """Convert results to a pandas DataFrame"""
        return pd.DataFrame(self.results)

    def save_to_csv(self):
        """Save quiz results to CSV file"""
        try:
            if not self.results:
                st.warning("No results to save.")
                return None
            
            df = self.generate_result_dataframe()
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"quiz_results_{self.current_topic}_{timestamp}.csv"
            
            os.makedirs('results', exist_ok=True)
            full_path = os.path.join('results', unique_filename)
            df.to_csv(full_path, index=False)
            
            st.success(f"Results saved successfully!")
            return full_path
        except Exception as e:
            st.error(f"Failed to save results: {e}")
            return None

    def clear_session_state(self):
        """Clear session state for this quiz session"""
        keys_to_remove = []
        for key in st.session_state:
            if self.current_quiz_id and self.current_quiz_id in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]

class QuestionGenerator:
    def __init__(self):
        """
        Initialize question generator with Groq API
        Sets up the language model with specific parameters:
        - Uses llama-3.1-8b-instant model
        - Sets temperature to 0.9 for creative variety
        """
        self.llm = ChatGroq(
            api_key=os.getenv('GROQ_API_KEY'), 
            model="llama-3.1-8b-instant",
            temperature=0.9
        )

    def generate_mcq(self, topic: str, difficulty: str = 'medium') -> MCQQuestion:
        """
        Generate Multiple Choice Question with robust error handling
        Includes:
        - Output parsing using Pydantic
        - Structured prompt template
        - Multiple retry attempts on failure
        - Validation of generated questions
        """
        # Set up Pydantic parser for type checking and validation
        mcq_parser = PydanticOutputParser(pydantic_object=MCQQuestion)
        
        # Define the prompt template with specific format requirements
        prompt = PromptTemplate(
            template=(
                "Generate a {difficulty} multiple-choice question about {topic}.\n\n"
                "Return ONLY a JSON object with these exact fields:\n"
                "- 'question': A clear, specific question\n"
                "- 'options': An array of exactly 4 possible answers\n"
                "- 'correct_answer': One of the options that is the correct answer\n\n"
                "Example format:\n"
                '{{\n'
                '    "question": "What is the capital of France?",\n'
                '    "options": ["London", "Berlin", "Paris", "Madrid"],\n'
                '    "correct_answer": "Paris"\n'
                '}}\n\n'
                "Your response:"
            ),
            input_variables=["topic", "difficulty"]
        )

        # Implement retry logic with maximum attempts
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Generate response using LLM
                response = self.llm.invoke(prompt.format(topic=topic, difficulty=difficulty))
                parsed_response = mcq_parser.parse(response.content)
                
                # Validate the generated question meets requirements
                if not parsed_response.question or len(parsed_response.options) != 4 or not parsed_response.correct_answer:
                    raise ValueError("Invalid question format")
                if parsed_response.correct_answer not in parsed_response.options:
                    raise ValueError("Correct answer not in options")
                
                return parsed_response
            except Exception as e:
                # On final attempt, raise error; otherwise continue trying
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Failed to generate valid MCQ after {max_attempts} attempts: {str(e)}")
                continue

    def generate_fill_blank(self, topic: str, difficulty: str = 'medium') -> FillBlankQuestion:
        """
        Generate Fill in the Blank Question with robust error handling
        Includes:
        - Output parsing using Pydantic
        - Structured prompt template
        - Multiple retry attempts on failure
        - Validation of blank marker format
        """
        # Set up Pydantic parser for type checking and validation
        fill_blank_parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
        
        # Define the prompt template with specific format requirements
        prompt = PromptTemplate(
            template=(
                "Generate a {difficulty} fill-in-the-blank question about {topic}.\n\n"
                "Return ONLY a JSON object with these exact fields:\n"
                "- 'question': A sentence with '_____' marking where the blank should be\n"
                "- 'answer': The correct word or phrase that belongs in the blank\n\n"
                "Example format:\n"
                '{{\n'
                '    "question": "The capital of France is _____.",\n'
                '    "answer": "Paris"\n'
                '}}\n\n'
                "Your response:"
            ),
            input_variables=["topic", "difficulty"]
        )

        # Implement retry logic with maximum attempts
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Generate response using LLM
                response = self.llm.invoke(prompt.format(topic=topic, difficulty=difficulty))
                parsed_response = fill_blank_parser.parse(response.content)
                
                # Validate the generated question meets requirements
                if not parsed_response.question or not parsed_response.answer:
                    raise ValueError("Invalid question format")
                if "_____" not in parsed_response.question:
                    parsed_response.question = parsed_response.question.replace("___", "_____")
                    if "_____" not in parsed_response.question:
                        raise ValueError("Question missing blank marker '_____'")
                
                return parsed_response
            except Exception as e:
                # On final attempt, raise error; otherwise continue trying
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Failed to generate valid fill-in-the-blank question after {max_attempts} attempts: {str(e)}")
                continue