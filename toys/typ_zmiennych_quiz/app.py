from flask import Flask, render_template, jsonify, request
import json
import random
import os
import sys

app = Flask(__name__)

# === Ładowanie pytań z JSON ===
def get_bundle_dir():
    """Zwraca ścieżkę do katalogu z plikami (dev vs .exe)"""
    if getattr(sys, 'frozen', False):
        # W .exe - PyInstaller wypakował do _MEIPASS
        return sys._MEIPASS
    else:
        # Dev mode
        return os.path.dirname(__file__)

def load_questions():
    """Wczytuje pytania z questions.json"""
    bundle_dir = get_bundle_dir()
    json_path = os.path.join(bundle_dir, 'questions.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data['questions']

# Wczytaj pytania na starcie aplikacji (cache)
ALL_QUESTIONS = load_questions()

# === Sesja quizu (in-memory, per-user) ===
# W uproszczeniu: jedna globalna sesja (wystarczy dla single-user desktop app)
quiz_session = {
    'remaining_questions': [],  # ID pytań do wylosowania
    'shuffled': False
}

@app.route('/')
def index():
    """Strona główna - renderuje interfejs quizu"""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_quiz():
    """
    Inicjalizuje sesję quizu: tasuje pytania

    Returns:
        JSON: {success: bool, total_questions: int}
    """
    try:
        # Tasuj wszystkie pytania
        question_ids = [q['id'] for q in ALL_QUESTIONS]
        random.shuffle(question_ids)

        quiz_session['remaining_questions'] = question_ids
        quiz_session['shuffled'] = True

        return jsonify({
            'success': True,
            'total_questions': len(question_ids)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Błąd inicjalizacji: {str(e)}'
        }), 500

@app.route('/api/next', methods=['GET'])
def next_question():
    """
    Zwraca kolejne pytanie (bez odpowiedzi)

    Returns:
        JSON: {
            success: bool,
            question: {id, question},  # BEZ 'correct' i 'explanation'
            remaining: int,            # ile pytań zostało
            finished: bool             # czy koniec pytań
        }
    """
    try:
        # Jeśli nie shufflowano, zrób to teraz
        if not quiz_session['shuffled']:
            start_quiz()

        # Sprawdź czy są pytania
        if not quiz_session['remaining_questions']:
            return jsonify({
                'success': True,
                'finished': True,
                'message': 'Gratulacje! Przeszedłeś przez wszystkie pytania.'
            })

        # Pobierz kolejne pytanie
        next_id = quiz_session['remaining_questions'][0]
        question = next((q for q in ALL_QUESTIONS if q['id'] == next_id), None)

        if not question:
            raise ValueError(f"Pytanie ID {next_id} nie znalezione")

        return jsonify({
            'success': True,
            'finished': False,
            'question': {
                'id': question['id'],
                'question': question['question']
            },
            'remaining': len(quiz_session['remaining_questions'])
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Błąd pobierania pytania: {str(e)}'
        }), 500

@app.route('/api/check', methods=['POST'])
def check_answer():
    """
    Sprawdza odpowiedź użytkownika

    Body:
        {question_id: int, answer: str}

    Returns:
        JSON: {
            success: bool,
            correct: bool,
            explanation: str,
            correct_answer: str
        }
    """
    try:
        data = request.json
        question_id = int(data.get('question_id'))
        user_answer = data.get('answer')

        # Znajdź pytanie
        question = next((q for q in ALL_QUESTIONS if q['id'] == question_id), None)

        if not question:
            raise ValueError(f"Pytanie ID {question_id} nie znalezione")

        # Sprawdź odpowiedź
        is_correct = (user_answer == question['correct'])

        # Usuń pytanie z remaining (użytkownik już na nie odpowiedział)
        if question_id in quiz_session['remaining_questions']:
            quiz_session['remaining_questions'].remove(question_id)

        return jsonify({
            'success': True,
            'correct': is_correct,
            'explanation': question['explanation'],
            'correct_answer': question['correct']
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Błąd sprawdzania odpowiedzi: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Uruchom serwer Flask (tylko dla testów - w produkcji używamy PyWebView)
    # Port 5001 (histogram używa 5000)
    app.run(debug=True, port=5001)
