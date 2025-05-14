import streamlit as st
import pandas as pd
import random
import os
import base64
from utils import QuestionGenerator

# Function to load and encode images for background
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Set page configuration
st.set_page_config(
    page_title="NIELIT Quiz Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

#UI
st.markdown("""
    <style>
        /* Base styling */
        * {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        /* Main container */
        .main {
            background-color: #f8f9fa;
            padding: 0;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1e3a8a;
            padding-top: 2rem;
        }
        
        [data-testid="stSidebar"] .block-container {
            padding-top: 0;
        }
        
        /* Sidebar text */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label {
            color: white;
        }
        
        
        
        /* Headers */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        h2 {
            color: #1e3a8a;
            font-weight: 600;
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
        }
        
        /* Questions styling */
        .question-card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            border-left: 5px solid #3b82f6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .question-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        }
        
        .question-number {
            font-weight: 700;
            color: #3b82f6;
            margin-bottom: 8px;
            font-size: 1.1rem;
            display: inline-block;
            padding: 2px 8px;
            background-color: #f0f7ff;
            border-radius: 6px;
        }
        
        .question-text {
            font-size: 1.05rem;
            line-height: 1.5;
            margin-top: 5px;
            color: #333;
        }
        
        /* Result cards */
        .correct-answer {
            background-color: #f0fdf4;
            border-left: 5px solid #10b981;
            padding: 16px 20px;
            border-radius: 12px;
            margin: 16px 0;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
            position: relative;
        }
        
        .correct-answer::after {
            content: "✓";
            position: absolute;
            top: 12px;
            right: 15px;
            font-size: 1.4rem;
            color: #10b981;
            font-weight: bold;
        }
        
        .incorrect-answer {
            background-color: #fef2f2;
            border-left: 5px solid #ef4444;
            padding: 16px 20px;
            border-radius: 12px;
            margin: 16px 0;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
            position: relative;
        }
        
        .incorrect-answer::after {
            content: "✗";
            position: absolute;
            top: 12px;
            right: 15px;
            font-size: 1.4rem;
            color: #ef4444;
            font-weight: bold;
        }
        
        .result-question {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 10px;
        }
        
        .answer-detail {
            margin-top: 8px;
            padding: 8px 12px;
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 8px;
        }
        
        /* Score display */
        .score-display {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border-radius: 16px;
            padding: 24px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .score-display::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            opacity: 0.6;
        }
        
        .score-percentage {
            position: relative;
            font-size: 3rem;
            font-weight: 800;
            margin: 10px 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .score-label {
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .score-fraction {
            font-size: 1.2rem;
            font-weight: 500;
            position: relative;
        }
        
        /* Logo styling */
        .app-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e3a8a;
        }
        
        /* Button styling */  
        .stButton > button {
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3);
            transform: translateY(-2px);
        }
        
        /* Submit button special styling */
        .submit-button .stButton > button {
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
        }
        
        .submit-button .stButton > button:hover {
            background: linear-gradient(90deg, #059669 0%, #047857 100%);
            box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3);
        }
        
        /* Inputs styling */
        .stSelectbox > div > div, 
        .stNumberInput > div > div:last-child {
            border-radius: 5px;
        }
        
        /* Hide hamburger menu for more space */
        button[kind="header"] {
            display: none;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 20px;
        }
        
        /* Radio button styling */
        .stRadio > div {
            margin: 10px 0 !important;
        }
        
        .stRadio > div > div > label {
            padding: 10px 15px !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            width: 100% !important;
            display: block !important;
            transition: all 0.2s ease !important;
        }
        
        .stRadio > div > div > label:hover {
            background-color: #f8fafc !important;
            border-color: #cbd5e1 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Main quiz manager class
class QuizManager:
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []

    def generate_questions(self, generator, topic, question_type, difficulty, num_questions):
        self.questions = []
        self.user_answers = []
        self.results = []
        
        try:
            for _ in range(num_questions):
                if question_type == "Multiple Choice":
                    question = generator.generate_mcq(topic, difficulty.lower())
                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_answer': question.correct_answer
                    })
                else:
                    question = generator.generate_fill_blank(topic, difficulty.lower())
                    self.questions.append({
                        'type': 'Fill in the Blank',
                        'question': question.question,
                        'correct_answer': question.answer
                    })
            
            # Initialize user_answers list with placeholders
            self.user_answers = ["" for _ in self.questions]
            return True
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return False

    def attempt_quiz(self):
        for i, q in enumerate(self.questions):
            st.markdown(f"""
            <div class="question-card">
                <div class="question-number">Question {i+1}</div>
                <div class="question-text">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            if q['type'] == 'MCQ':
                # Create a radio button key for this question
                radio_key = f"mcq_selection_{i}"
                
                # Get stored answer from session state if exists
                default_index = 0
                if radio_key in st.session_state and st.session_state[radio_key] in q['options']:
                    default_index = q['options'].index(st.session_state[radio_key])
                
                # Create radio buttons for this question
                selected_option = st.radio(
                    f"Select answer for Question {i+1}:",
                    options=q['options'],
                    index=default_index,
                    key=radio_key
                )
                
                # Update user_answers with the selected option
                self.user_answers[i] = selected_option
            else:
                # For fill in the blank questions
                answer_key = f"fill_blank_{i}"
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
        self.results = []
        for i, (q, user_ans) in enumerate(zip(self.questions, self.user_answers)):
            if q['type'] == 'MCQ':
                # For MCQ with radio buttons, we compare the selected option with the correct answer
                is_correct = user_ans == q['correct_answer'] if user_ans else False
                
                result_dict = {
                    'question_number': i + 1,
                    'question': q['question'],
                    'question_type': q['type'],
                    'user_answer': user_ans if user_ans else "No selection",
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
                    'user_answer': user_ans if user_ans else "No answer provided",
                    'correct_answer': q['correct_answer'],
                    'is_correct': is_correct,
                    'options': q['options'] if 'options' in q else []
                }
            self.results.append(result_dict)

    def generate_result_dataframe(self):
        return pd.DataFrame(self.results)

    def save_to_csv(self):
        try:
            if not self.results:
                st.warning("No results to save.")
                return None
            
            df = self.generate_result_dataframe()
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"quiz_results_{timestamp}.csv"
            
            os.makedirs('results', exist_ok=True)
            full_path = os.path.join('results', unique_filename)
            df.to_csv(full_path, index=False)
            
            st.success(f"Results saved successfully!")
            return full_path
        except Exception as e:
            st.error(f"Failed to save results: {e}")
            return None

# Initialize session state
if 'quiz_manager' not in st.session_state:
    st.session_state.quiz_manager = QuizManager()
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

# Sidebar
with st.sidebar:
    st.markdown('<h2 style="color: white; text-align: center;">NIELIT Quiz</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #a0aec0; text-align: center; margin-bottom: 20px;">Configure your quiz settings</p>', unsafe_allow_html=True)
    
    # Quiz configuration
    st.markdown('<p style="color: #a0aec0; font-weight: 600;">Question Format</p>', unsafe_allow_html=True)
    question_type = st.selectbox("", ["Multiple Choice", "Fill in the Blank"], index=0, label_visibility="collapsed")
    
    st.markdown('<p style="color: #a0aec0; font-weight: 600; margin-top: 15px;">Subject Area</p>', unsafe_allow_html=True)
    topic = st.text_input("Enter a topic (e.g. Operating System, DBMS)") 

    st.markdown('<p style="color: #a0aec0; font-weight: 600; margin-top: 15px;">Difficulty Level</p>', unsafe_allow_html=True)
    difficulty = st.selectbox("", ["Easy", "Medium", "Hard"], index=1, label_visibility="collapsed")
    
    st.markdown('<p style="color: #a0aec0; font-weight: 600; margin-top: 15px;">Number of Questions</p>', unsafe_allow_html=True)
    num_questions = st.number_input("", min_value=1, max_value=50, value=5, label_visibility="collapsed")
    
    # Generate quiz button
    st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
    generate_quiz = st.button("Generate Quiz", use_container_width=True)
    
    # Sidebar footer
    st.markdown('<div class="footer" style="color: #a0aec0; margin-top: 40px;">NIELIT MCQ Generator<br>© 2025</div>', unsafe_allow_html=True)

# Main content
content_col = st.container()

with content_col:
    # Header with modern design
    st.markdown('<div class="content-card app-header">', unsafe_allow_html=True)
    st.markdown('''
    <div style="text-align: center;">
        <div style="display: inline-block; background: linear-gradient(90deg, #1e40af, #3b82f6); padding: 8px 16px; border-radius: 30px; margin-bottom: 15px;">
            <span style="color: white; font-weight: 700; letter-spacing: 1.5px;">NIELIT</span>
        </div>
        <h1 style="text-align: center; margin-top: 5px;">MCQ Generator & Quiz Platform</h1>
        <p style="text-align: center; max-width: 600px; margin: 10px auto; color: #4b5563;">
            Create customized quizzes on various computer science topics to enhance your learning experience
        </p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process quiz generation
    if generate_quiz:
        with st.spinner("Creating your personalized quiz..."):
            st.session_state.quiz_submitted = False
            generator = QuestionGenerator()
            st.session_state.quiz_generated = st.session_state.quiz_manager.generate_questions(
                generator, topic, question_type, difficulty, num_questions
            )
            st.rerun()

    # Display quiz if generated
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h2 style="margin: 0;">{topic} Quiz</h2>
            <div style="background-color: #e0f2fe; color: #0369a1; font-weight: 600; padding: 5px 12px; border-radius: 20px; font-size: 0.9rem;">
                {difficulty} Level
            </div>
        </div>
        <p>Complete all {num_questions} questions and submit your answers. For multiple choice questions, select one option.</p>
        <div style="height: 3px; width: 100px; background: linear-gradient(90deg, #3b82f6, #93c5fd); margin: 15px 0;"></div>
        ''', unsafe_allow_html=True)
        
        # IMPORTANT: We must call attempt_quiz() to create and gather the current answers
        st.session_state.quiz_manager.attempt_quiz()
        
        st.markdown('<div class="submit-button">', unsafe_allow_html=True)
        submit_quiz = st.button("Submit Quiz", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submit_quiz:
            # First, save the current state from radio buttons into the user_answers
            for i, q in enumerate(st.session_state.quiz_manager.questions):
                if q['type'] == 'MCQ':
                    radio_key = f"mcq_selection_{i}"
                    st.session_state.quiz_manager.user_answers[i] = st.session_state[radio_key]
                else:
                    st.session_state.quiz_manager.user_answers[i] = st.session_state[f"fill_blank_{i}"]
            
            # Now evaluate with the updated answers
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            st.rerun()

    # Display results if quiz submitted
    if st.session_state.quiz_submitted:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<h2>Quiz Results</h2>', unsafe_allow_html=True)
        
        results_df = st.session_state.quiz_manager.generate_result_dataframe()
        
        if not results_df.empty:
            correct_count = results_df['is_correct'].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100
            
            # Score display
            st.markdown(f"""
            <div class="score-display">
                <div class="score-label">Your Score</div>
                <div class="score-percentage">{score_percentage:.1f}%</div>
                <div class="score-fraction">{correct_count} out of {total_questions} correct</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Question results
            for _, result in results_df.iterrows():
                if result['is_correct']:
                    st.markdown(f"""
                    <div class="correct-answer">
                        <div class="result-question">Question {result['question_number']}</div>
                        <p>{result['question']}</p>
                        <div class="answer-detail">
                            <strong>Your Answer:</strong> {result['user_answer']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="incorrect-answer">
                        <div class="result-question">Question {result['question_number']}</div>
                        <p>{result['question']}</p>
                        <div class="answer-detail">
                            <strong>Your Answer:</strong> {result['user_answer']}
                        </div>
                        <div class="answer-detail" style="background-color: rgba(16, 185, 129, 0.1);">
                            <strong>Correct Answer:</strong> {result['correct_answer']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Save and download options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Results", use_container_width=True):
                    saved_file = st.session_state.quiz_manager.save_to_csv()
                    if saved_file:
                        st.session_state.saved_file_path = saved_file
                        st.rerun()
            
            with col2:
                if 'saved_file_path' in st.session_state and st.session_state.saved_file_path:
                    with open(st.session_state.saved_file_path, 'rb') as f:
                        st.download_button(
                            label="Download Results",
                            data=f.read(),
                            file_name=os.path.basename(st.session_state.saved_file_path),
                            mime='text/csv',
                            use_container_width=True
                        )
        else:
            st.warning("No results available. Please complete the quiz first.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    
    if not st.session_state.quiz_generated and not st.session_state.quiz_submitted:
        st.markdown('<div class="content-card" style="text-align: center; padding: 30px;">', unsafe_allow_html=True)
        st.markdown('<h2>Welcome to the NIELIT MCQ Generator</h2>', unsafe_allow_html=True)
        st.markdown("""
        <p style="font-size: 1.1rem; margin-bottom: 20px;">Create customized quizzes to test your knowledge in various computer science subjects.</p>
        <div style="display: flex; justify-content: center; margin: 30px 0;">
            <div style="max-width: 500px; text-align: left;">
                <p style="font-weight: 600; margin-bottom: 10px;">How to use:</p>
                <ol>
                    <li>Select your preferred settings from the sidebar</li>
                    <li>Click "Generate Quiz" to create questions</li>
                    <li>Answer the questions and submit your responses</li>
                    <li>View your results and download them if needed</li>
                </ol>
            </div>
        </div>
        <p style="font-style: italic; color: #4b5563;">Perfect for exam preparation and self-assessment</p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)