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
        
        for item in data:
            if isinstance(item.get('correct_answer'), str):
                item['correct_answer'] = clean_text(item['correct_answer'])
            elif isinstance(item.get('correct_answer'), list):
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

def initialize_quiz():
    """Inicjalizuje lub resetuje stan quizu w sesji."""
    questions = load_data('data.json')
    st.session_state.questions = questions
    st.session_state.total_questions = len(questions)
    
    question_indices = list(range(st.session_state.total_questions))
    random.shuffle(question_indices)
    st.session_state.question_indices = question_indices
    
    st.session_state.current_q_index_ptr = 0
    st.session_state.score = 0
    st.session_state.quiz_history = []
    st.session_state.answer_submitted = False
    st.session_state.quiz_started = True
    st.session_state.checkbox_states = {}

def reset_quiz():
    """Całkowicie resetuje quiz, usuwając stan sesji."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def go_to_next_question():
    """Przechodzi do następnego pytania."""
    st.session_state.current_q_index_ptr += 1
    st.session_state.answer_submitted = False
    st.session_state.checkbox_states = {}


# --- Główna logika aplikacji ---

st.title("🚀 Kahoot z Metody Elementów Skończonych")

# Inicjalizacja stanu, jeśli aplikacja jest uruchamiana po raz pierwszy
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

# Przycisk restartu w panelu bocznym
if st.sidebar.button("Zrestartuj test", type="primary"):
    reset_quiz()

# --- Ekran startowy ---
if not st.session_state.quiz_started:
    if st.button("Rozpocznij Quiz!", type="primary", use_container_width=True):
        initialize_quiz()
        st.rerun()

# --- Przebieg Quizu ---
elif st.session_state.current_q_index_ptr < st.session_state.total_questions:
    
    # Pobierz bieżące pytanie
    question_idx = st.session_state.question_indices[st.session_state.current_q_index_ptr]
    question_data = st.session_state.questions[question_idx]
    question_text = question_data["question"]
    options = question_data.get("options", {})
    correct_answer = question_data["correct_answer"]

    # Pasek postępu
    progress = (st.session_state.current_q_index_ptr) / st.session_state.total_questions
    st.progress(progress, text=f"Pytanie {st.session_state.current_q_index_ptr + 1} z {st.session_state.total_questions}")
    
    st.subheader(f"Pytanie {st.session_state.current_q_index_ptr + 1}:")
    st.markdown(question_text)
    st.write("---")

    # Jeśli odpowiedź została udzielona, pokaż feedback
    if st.session_state.answer_submitted:
        last_result = st.session_state.quiz_history[-1]
        
        # <<< POCZĄTEK ZMIANY W BLOKU FEEDBACKU >>>
        # Przygotuj sformatowany tekst dla poprawnej/poprawnych odpowiedzi
        if isinstance(last_result['correct_answer'], list):
            correct_answer_display = "\n" + "\n".join([f"- {ans}" for ans in last_result['correct_answer']])
            correct_answer_heading = "**Poprawne odpowiedzi:**"
        else:
            correct_answer_display = f"**{last_result['correct_answer']}**"
            correct_answer_heading = "**Poprawna odpowiedź to:**"
        
        feedback_message = ""
        if last_result['is_correct']:
            feedback_message = f"✅ Dobrze! {correct_answer_heading}{correct_answer_display}"
        else:
            user_answer_str = ", ".join(last_result['user_answer']) if isinstance(last_result['user_answer'], list) else last_result['user_answer']
            feedback_message = f"❌ Niestety, źle. Twoja odpowiedź: **{user_answer_str}**. {correct_answer_heading}{correct_answer_display}"
        
        st.success(feedback_message)
        # <<< KONIEC ZMIANY W BLOKU FEEDBACKU >>>
        
        st.button("Następne pytanie", on_click=go_to_next_question, use_container_width=True, type="primary")
    
    # Jeśli odpowiedź nie została udzielona, pokaż opcje
    else:
        is_multi_select = "Wybierz wszystkie poprawne" in question_text

        if is_multi_select:
            user_answers = []
            for option_text in options.values():
                if st.checkbox(option_text, key=option_text):
                    user_answers.append(option_text)
            
            if st.button("Sprawdź odpowiedzi", use_container_width=True):
                is_correct = set(user_answers) == set(correct_answer)
                if is_correct:
                    st.session_state.score += 1
                
                st.session_state.quiz_history.append({
                    "question": question_text,
                    "user_answer": user_answers,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct
                })
                st.session_state.answer_submitted = True
                st.rerun()
        else:
            cols = st.columns(2)
            col_idx = 0
            for option_text in options.values():
                if cols[col_idx].button(option_text, key=option_text, use_container_width=True):
                    is_correct = (option_text == correct_answer)
                    if is_correct:
                        st.session_state.score += 1

                    st.session_state.quiz_history.append({
                        "question": question_text,
                        "user_answer": option_text,
                        "correct_answer": correct_answer,
                        "is_correct": is_correct
                    })
                    st.session_state.answer_submitted = True
                    st.rerun()
                col_idx = (col_idx + 1) % 2

# --- Ekran końcowy ze statystykami ---
else:
    st.balloons()
    st.header("🎉 Koniec Quizu! 🎉")
    
    score = st.session_state.score
    total = st.session_state.total_questions
    percentage = (score / total * 100) if total > 0 else 0
    
    st.subheader("Podsumowanie wyników:")
    col1, col2 = st.columns(2)
    col1.metric("Twój wynik", f"{score}/{total}")
    col2.metric("Procentowo", f"{percentage:.2f}%")
    
    st.write("---")
    
    st.subheader("Szczegółowa analiza odpowiedzi:")
    for i, result in enumerate(st.session_state.quiz_history):
        icon = "✅" if result["is_correct"] else "❌"
        with st.expander(f"{icon} Pytanie {i+1} - {'Poprawnie' if result['is_correct'] else 'Błędnie'}", expanded=not result["is_correct"]):
            st.markdown(f"**Pytanie:** {result['question']}")
            
            user_answer_str = ", ".join(result['user_answer']) if isinstance(result['user_answer'], list) else result['user_answer']
            st.info(f"**Twoja odpowiedź:** {user_answer_str}")
            
            if isinstance(result['correct_answer'], list):
                formatted_answers = "\n".join([f"- {ans}" for ans in result['correct_answer']])
                st.success(f"**Poprawne odpowiedzi:**\n{formatted_answers}")
            else:
                st.success(f"**Poprawna odpowiedź:** {result['correct_answer']}")

    st.write("---")
    if st.button("Zagraj jeszcze raz!", type="primary", use_container_width=True):
        initialize_quiz()
        st.rerun()
