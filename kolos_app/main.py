import streamlit as st
import json
import random
import re
import time
from pathlib import Path

# Konfiguracja strony
st.set_page_config(
    page_title="Quiz",
    page_icon="🚀",
    layout="centered"
)

# --- FUNKCJA DO ŁADOWANIA LOKALNEGO CSS ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Plik {file_name} nie został znaleziony. Aplikacja będzie działać ze standardowymi stylami.")

# Wywołanie funkcji, aby załadować style z pliku style.css
local_css("style.css")


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
        st.error(f"Błąd wczytywania pliku {file_path}: {e}")
        return []

def find_quizzes(data_dir="questions"):
    """Skanuje folder 'data' i zwraca słownik z nazwami quizów i ścieżkami do plików."""
    data_path = Path(data_dir)
    if not data_path.is_dir():
        return {}
    quiz_files = list(data_path.glob("*.json"))
    # Tworzy mapowanie: przyjazna nazwa -> pełna ścieżka
    return {file.stem.replace("_", " ").capitalize(): file for file in quiz_files}

def clean_text(text: str) -> str:
    """Usuwa niechciane znaki i białe znaki z tekstu."""
    return re.sub(r'[✓X]|\s+$', '', text).strip()

def initialize_quiz(quiz_file_path):
    """Inicjalizuje lub resetuje stan quizu w sesji na podstawie wybranego pliku."""
    questions = load_data(quiz_file_path)
    
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
    st.session_state.timer_stopped = False

def reset_quiz():
    """Całkowicie resetuje quiz, usuwając stan sesji, wracając do ekranu wyboru."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def go_to_next_question():
    """Przechodzi do następnego pytania i resetuje stany."""
    st.session_state.current_q_index_ptr += 1
    st.session_state.answer_submitted = False
    st.session_state.checkbox_states = {}
    st.session_state.timer_stopped = False


# --- Główna logika aplikacji ---

st.title("🚀 Super Quiz")

if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

if st.session_state.quiz_started:
    if st.sidebar.button("Zmień quiz", type="secondary"):
        reset_quiz()
    if st.sidebar.button("Zrestartuj test", type="primary"):
        current_quiz_path = st.session_state.get('current_quiz_path')
        reset_quiz()
        st.session_state.selected_quiz_path = current_quiz_path
        if current_quiz_path:
            initialize_quiz(current_quiz_path)
            st.rerun()

# --- Ekran startowy i wybór quizu ---
if not st.session_state.quiz_started:
    st.header("Wybierz quiz do rozwiązania")
    
    quiz_map = find_quizzes()
    
    if not quiz_map:
        st.error("Nie znaleziono żadnych plików .json w folderze 'data'. Upewnij się, że folder istnieje i zawiera pliki z quizami.")
    else:
        st.session_state.quiz_map = quiz_map
        
        selected_quiz_name = st.selectbox(
            "Dostępne quizy:",
            options=list(quiz_map.keys())
        )
        
        if st.button(f"Rozpocznij: {selected_quiz_name}", type="primary", use_container_width=True):
            selected_path = quiz_map[selected_quiz_name]
            st.session_state.current_quiz_path = selected_path
            initialize_quiz(selected_path)
            st.rerun()

# --- Przebieg Quizu ---
elif st.session_state.current_q_index_ptr < st.session_state.total_questions:
    
    question_idx = st.session_state.question_indices[st.session_state.current_q_index_ptr]
    question_data = st.session_state.questions[question_idx]
    question_text = question_data["question"]
    options = question_data.get("options", {})
    correct_answer = question_data["correct_answer"]

    progress = (st.session_state.current_q_index_ptr) / st.session_state.total_questions
    st.progress(progress, text=f"Pytanie {st.session_state.current_q_index_ptr + 1} z {st.session_state.total_questions}")
    
    st.subheader(f"Pytanie {st.session_state.current_q_index_ptr + 1}:")
    st.markdown(question_text)
    st.write("---")

    # Jeśli odpowiedź została udzielona, pokaż feedback i timer
    if st.session_state.answer_submitted:
        last_result = st.session_state.quiz_history[-1]
        
        if isinstance(last_result['correct_answer'], list):
            correct_answer_display = "\n" + "\n".join([f"- {ans}" for ans in last_result['correct_answer']])
            correct_answer_heading = "**Poprawne odpowiedzi:**"
        else:
            correct_answer_display = f"**{last_result['correct_answer']}**"
            correct_answer_heading = "**Poprawna odpowiedź to:**"
        
        if last_result['is_correct']:
            feedback_message = f"✅ Dobrze! {correct_answer_heading}{correct_answer_display}"
            st.success(feedback_message)
            countdown_duration = 2
        else:
            user_answer_str = ", ".join(last_result['user_answer']) if isinstance(last_result['user_answer'], list) else last_result['user_answer']
            feedback_message = f"❌ Niestety, źle. Twoja odpowiedź: **{user_answer_str}**. {correct_answer_heading}{correct_answer_display}"
            st.error(feedback_message)
            countdown_duration = 5
        
        st.write("---")

        if st.session_state.timer_stopped:
            st.info("Timer zatrzymany. Kliknij, aby kontynuować.")
            if st.button("Następne pytanie", use_container_width=True, type="primary"):
                go_to_next_question()
                st.rerun()
        else:
            placeholder = st.empty()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Przejdź natychmiast", use_container_width=True):
                    go_to_next_question()
                    st.rerun()
            if not last_result['is_correct']:
                with col2:
                    if st.button("Zatrzymaj timer", use_container_width=True):
                        st.session_state.timer_stopped = True
                        st.rerun()

            for i in range(countdown_duration, 0, -1):
                placeholder.markdown(f"### Automatyczne przejście za **{i}** s...")
                time.sleep(1)
            
            go_to_next_question()
            st.rerun()

    # Jeśli odpowiedź nie została udzielona, pokaż opcje
    else:
        is_multi_select = "Wybierz wszystkie poprawne" in question_text

        # <<< POCZĄTEK ZMIANY: LOSOWANIE ODPOWIEDZI >>>
        shuffled_options = list(options.values())
        random.shuffle(shuffled_options)
        # <<< KONIEC ZMIANY >>>

        if is_multi_select:
            st.markdown("Wybierz jedną lub więcej odpowiedzi i kliknij 'Sprawdź'.")
            user_answers = []
            for option_text in shuffled_options: # Używamy przetasowanej listy
                if st.checkbox(option_text, key=f"q{st.session_state.current_q_index_ptr}_{option_text}"):
                    user_answers.append(option_text)
            
            if st.button("Sprawdź odpowiedzi", use_container_width=True, type="primary"):
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
            st.markdown("Wybierz jedną odpowiedź:")
            cols = st.columns(2)
            col_idx = 0
            for option_text in shuffled_options: # Używamy przetasowanej listy
                if cols[col_idx].button(option_text, key=f"q{st.session_state.current_q_index_ptr}_{option_text}", use_container_width=True):
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

# --- Ekran końcowy ---
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
    if st.button("Zagraj w ten quiz jeszcze raz!", type="primary", use_container_width=True):
        current_quiz_path = st.session_state.get('current_quiz_path')
        reset_quiz()
        st.session_state.selected_quiz_path = current_quiz_path
        if current_quiz_path:
            initialize_quiz(current_quiz_path)
            st.rerun()
