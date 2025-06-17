import streamlit as st
import json
import random
import re

# Konfiguracja strony
st.set_page_config(
    page_title="Quiz MES",
    page_icon="🚀",
    layout="centered"
)

# --- Funkcje pomocnicze ---

@st.cache_data
def load_data(file_path: str) -> list:
    """Wczytuje i czyści dane pytań z pliku JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Czyszczenie danych: usuwanie zbędnych znaków i spacji
        for item in data:
            if isinstance(item['correct_answer'], str):
                item['correct_answer'] = clean_text(item['correct_answer'])
            elif isinstance(item['correct_answer'], list):
                item['correct_answer'] = [clean_text(ans) for ans in item['correct_answer']]
            
            if isinstance(item.get('options'), dict):
                cleaned_options = {}
                for key, value in item['options'].items():
                   cleaned_options[key] = clean_text(value)
                item['options'] = cleaned_options

        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Błąd wczytywania pliku data.json: {e}")
        return []

def clean_text(text: str) -> str:
    """Usuwa niechciane znaki i białe znaki z tekstu."""
    return re.sub(r'[✓X]|\s+$', '', text).strip()


def initialize_quiz_state():
    """Inicjalizuje lub resetuje stan quizu w sesji."""
    questions = load_data('data.json')
    st.session_state.questions = questions
    st.session_state.total_questions = len(questions)
    
    question_indices = list(range(st.session_state.total_questions))
    random.shuffle(question_indices)
    st.session_state.question_indices = question_indices
    
    st.session_state.current_q_index_ptr = 0
    st.session_state.score = 0
    st.session_state.quiz_history = []  # Do przechowywania szczegółowych odpowiedzi
    st.session_state.answer_submitted = False # Flaga do kontroli feedbacku
    st.session_state.quiz_started = True

def go_to_next_question():
    """Przechodzi do następnego pytania i resetuje flagę odpowiedzi."""
    st.session_state.current_q_index_ptr += 1
    st.session_state.answer_submitted = False


# --- Główna logika aplikacji ---

st.title("🚀 Kahoot z Metody Elementów Skończonych")

# Inicjalizacja stanu
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

# --- Ekran startowy ---
if not st.session_state.quiz_started:
    if st.button("Rozpocznij Quiz!", type="primary", use_container_width=True):
        initialize_quiz_state()
        st.rerun()

# --- Przebieg Quizu ---
elif st.session_state.current_q_index_ptr < st.session_state.total_questions:
    
    # Pobierz bieżące pytanie
    question_idx = st.session_state.question_indices[st.session_state.current_q_index_ptr]
    question_data = st.session_state.questions[question_idx]

    # Pasek postępu
    progress = (st.session_state.current_q_index_ptr) / st.session_state.total_questions
    st.progress(progress, text=f"Pytanie {st.session_state.current_q_index_ptr + 1} z {st.session_state.total_questions}")
    
    st.subheader(f"Pytanie {st.session_state.current_q_index_ptr + 1}:")
    st.markdown(question_data["question"])
    st.write("---")

    # Jeśli odpowiedź nie została jeszcze udzielona, pokaż przyciski
    if not st.session_state.answer_submitted:
        options = question_data.get("options", {})
        correct_answer = question_data["correct_answer"]
        
        cols = st.columns(2)
        col_idx = 0
        for option_text in options.values():
            if cols[col_idx].button(option_text, key=option_text, use_container_width=True):
                
                # Sprawdź odpowiedź
                is_correct = False
                if isinstance(correct_answer, list):
                    if option_text in correct_answer:
                        is_correct = True
                elif option_text == correct_answer:
                    is_correct = True
                
                if is_correct:
                    st.session_state.score += 1

                # Zapisz historię odpowiedzi
                st.session_state.quiz_history.append({
                    "question": question_data["question"],
                    "user_answer": option_text,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct
                })
                
                st.session_state.answer_submitted = True
                st.rerun()

            col_idx = (col_idx + 1) % 2
            
    # Jeśli odpowiedź została udzielona, pokaż feedback
    else:
        last_result = st.session_state.quiz_history[-1]
        correct_answer_str = ", ".join(last_result['correct_answer']) if isinstance(last_result['correct_answer'], list) else last_result['correct_answer']
        
        feedback_message = ""
        if last_result['is_correct']:
            feedback_message = f"✅ Dobrze! Poprawna odpowiedź to: **{correct_answer_str}**"
        else:
            feedback_message = f"❌ Niestety, źle. Poprawna odpowiedź to: **{correct_answer_str}**"
        
        st.success(feedback_message) # Zawsze zielony kolor
        
        st.button("Następne pytanie", on_click=go_to_next_question, use_container_width=True, type="primary")


# --- Ekran końcowy ze statystykami ---
else:
    st.balloons()
    st.header("🎉 Koniec Quizu! 🎉")
    
    score = st.session_state.score
    total = st.session_state.total_questions
    percentage = (score / total * 100) if total > 0 else 0
    
    st.subheader("Podsumowanie wyników:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Twój wynik", f"{score}/{total}")
    col2.metric("Procentowo", f"{percentage:.2f}%")
    
    st.write("---")
    
    st.subheader("Szczegółowa analiza odpowiedzi:")
    for i, result in enumerate(st.session_state.quiz_history):
        icon = "✅" if result["is_correct"] else "❌"
        with st.expander(f"{icon} Pytanie {i+1}", expanded=not result["is_correct"]):
            st.markdown(f"**Pytanie:** {result['question']}")
            st.info(f"**Twoja odpowiedź:** {result['user_answer']}")
            
            correct_answer_str = ", ".join(result['correct_answer']) if isinstance(result['correct_answer'], list) else result['correct_answer']
            st.success(f"**Poprawna odpowiedź:** {correct_answer_str}")

    st.write("---")
    if st.button("Zagraj jeszcze raz!", type="primary", use_container_width=True):
        initialize_quiz_state()
        st.rerun()