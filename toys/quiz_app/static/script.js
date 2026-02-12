// Konfiguracja quizu (przekazana z backend przez quiz.html)
const QUIZ_CONFIG = window.QUIZ_CONFIG;
const QUIZ_ID = document.body.dataset.quizId;

// Stan quizu
let currentQuestion = null;
let answered = false;
let correctCount = 0;
let totalAnswered = 0;
let totalQuestions = 0;

// Elementy DOM
let startScreen, questionScreen, finishScreen, loadingEl;
let btnStart, btnNext, btnRestart;
let questionText, feedbackBox, feedbackHeader, feedbackText;
let answersGrid;
let questionCounter, scoreResult, scorePercent, scoreBar;
let progressBar, progressFill;

// Etykiety odpowiedzi (A, B, C, D...)
const ANSWER_LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'];

document.addEventListener('DOMContentLoaded', function() {
    // Pobranie elementów
    startScreen = document.getElementById('start-screen');
    questionScreen = document.getElementById('question-screen');
    finishScreen = document.getElementById('finish-screen');
    loadingEl = document.getElementById('loading');

    btnStart = document.getElementById('btn-start');
    btnNext = document.getElementById('btn-next');
    btnRestart = document.getElementById('btn-restart');

    questionText = document.getElementById('question-text');
    feedbackBox = document.getElementById('feedback-box');
    feedbackHeader = document.getElementById('feedback-header');
    feedbackText = document.getElementById('feedback-text');
    answersGrid = document.getElementById('answers-grid');
    questionCounter = document.getElementById('question-counter');
    scoreResult = document.getElementById('score-result');
    scorePercent = document.getElementById('score-percent');
    scoreBar = document.getElementById('score-bar');
    progressBar = document.getElementById('progress-bar');
    progressFill = document.getElementById('progress-fill');

    // Event listeners
    btnStart.addEventListener('click', startQuiz);
    btnRestart.addEventListener('click', startQuiz);
    btnNext.addEventListener('click', loadNextQuestion);
});

/**
 * Rozpocznij quiz - inicjalizacja sesji
 */
async function startQuiz() {
    try {
        showLoading();

        const response = await fetch(`/api/quiz/${QUIZ_ID}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        if (data.success) {
            totalQuestions = data.total_questions;
            correctCount = 0;
            totalAnswered = 0;

            // Pokaż progress bar
            progressBar.style.display = '';
            updateProgress();

            showScreen('question');
            loadNextQuestion();
        } else {
            alert('Błąd inicjalizacji: ' + data.error);
        }
    } catch (error) {
        console.error('Błąd startu quizu:', error);
        alert('Błąd połączenia: ' + error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Załaduj kolejne pytanie
 */
async function loadNextQuestion() {
    try {
        showLoading();

        answered = false;
        feedbackBox.classList.add('st-feedback--hidden');

        const response = await fetch(`/api/quiz/${QUIZ_ID}/next`);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        if (data.success) {
            if (data.finished) {
                showFinishScreen();
            } else {
                currentQuestion = data.question;
                questionText.textContent = currentQuestion.question;

                const questionNum = totalAnswered + 1;
                questionCounter.textContent = `Pytanie ${questionNum} / ${totalQuestions}`;
                updateProgress();

                generateAnswerButtons();
            }
        } else {
            alert('Błąd: ' + data.error);
        }
    } catch (error) {
        console.error('Błąd ładowania pytania:', error);
        alert('Błąd połączenia: ' + error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Aktualizuj progress bar
 */
function updateProgress() {
    const progress = totalQuestions > 0
        ? ((totalAnswered) / totalQuestions) * 100
        : 0;
    progressFill.style.width = `${progress}%`;
}

/**
 * Generuj przyciski odpowiedzi
 */
function generateAnswerButtons() {
    answersGrid.innerHTML = '';

    let options = [];

    if (QUIZ_CONFIG.answer_type === 'multiple_choice_4' ||
        QUIZ_CONFIG.answer_type === 'multiple_choice_3') {
        options = QUIZ_CONFIG.options;
    } else if (QUIZ_CONFIG.answer_type === 'multiple_choice_random') {
        options = currentQuestion.options;
    }

    // Grid layout based on option count
    if (options.length <= 3) {
        answersGrid.className = 'st-answer-grid st-answer-grid--cols-1';
    } else {
        answersGrid.className = 'st-answer-grid st-answer-grid--cols-2';
    }

    options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'st-btn-answer';

        const label = document.createElement('span');
        label.className = 'st-btn-answer__label';
        label.textContent = ANSWER_LABELS[index];

        const text = document.createElement('span');

        if (typeof option === 'string') {
            btn.dataset.answer = option;
            text.textContent = option;
        } else {
            btn.dataset.answer = option.value;
            text.textContent = option.label;
        }

        btn.appendChild(label);
        btn.appendChild(text);
        btn.addEventListener('click', handleAnswer);
        answersGrid.appendChild(btn);
    });
}

/**
 * Obsługa wyboru odpowiedzi
 */
async function handleAnswer(event) {
    if (answered) return;

    const btn = event.target.closest('.st-btn-answer');
    if (!btn) return;
    const selectedAnswer = btn.dataset.answer;

    try {
        showLoading();

        const response = await fetch(`/api/quiz/${QUIZ_ID}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: currentQuestion.id,
                answer: selectedAnswer
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        if (data.success) {
            answered = true;
            totalAnswered++;
            if (data.correct) correctCount++;
            disableAnswerButtons();
            updateProgress();

            // Feedback
            const icon = data.correct
                ? '<span class="st-feedback__icon st-feedback__icon--correct"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg></span>'
                : '<span class="st-feedback__icon st-feedback__icon--incorrect"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></span>';

            if (data.correct) {
                feedbackHeader.innerHTML = icon + ' Poprawna odpowiedź!';
                feedbackHeader.className = 'st-feedback__header st-feedback__header--correct';
            } else {
                feedbackHeader.innerHTML = icon + ' Niepoprawna odpowiedź';
                feedbackHeader.className = 'st-feedback__header st-feedback__header--incorrect';
            }

            feedbackText.textContent = data.explanation;
            feedbackBox.classList.remove('st-feedback--hidden');

            highlightCorrectAnswer(data.correct_answer, selectedAnswer);
        } else {
            alert('Błąd: ' + data.error);
        }
    } catch (error) {
        console.error('Błąd sprawdzania odpowiedzi:', error);
        alert('Błąd połączenia: ' + error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Podświetl odpowiedzi
 */
function highlightCorrectAnswer(correctAnswer, userAnswer) {
    const answerButtons = answersGrid.querySelectorAll('.st-btn-answer');

    answerButtons.forEach(btn => {
        const answer = btn.dataset.answer;

        if (answer === correctAnswer) {
            btn.classList.add('st-btn-answer--correct');
        } else if (answer === userAnswer && userAnswer !== correctAnswer) {
            btn.classList.add('st-btn-answer--incorrect');
        } else {
            btn.classList.add('st-btn-answer--dimmed');
        }
    });
}

/**
 * Wyłącz przyciski odpowiedzi
 */
function disableAnswerButtons() {
    const answerButtons = answersGrid.querySelectorAll('.st-btn-answer');
    answerButtons.forEach(btn => {
        btn.disabled = true;
    });
}

/**
 * Pokaż określony ekran
 */
function showScreen(screenName) {
    startScreen.classList.remove('st-screen--active');
    questionScreen.classList.remove('st-screen--active');
    finishScreen.classList.remove('st-screen--active');

    if (screenName === 'start') startScreen.classList.add('st-screen--active');
    else if (screenName === 'question') questionScreen.classList.add('st-screen--active');
    else if (screenName === 'finish') finishScreen.classList.add('st-screen--active');
}

function showLoading() {
    loadingEl.classList.add('st-loading--active');
}

function hideLoading() {
    loadingEl.classList.remove('st-loading--active');
}

/**
 * Pokaż ekran końcowy
 */
function showFinishScreen() {
    const percent = totalAnswered > 0 ? Math.round((correctCount / totalAnswered) * 100) : 0;

    scoreResult.textContent = `${correctCount} / ${totalAnswered}`;
    scorePercent.textContent = `${percent}%`;

    scoreBar.style.width = `${percent}%`;

    if (percent >= 70) {
        scoreBar.className = 'st-score__bar-fill st-score__bar-fill--excellent';
    } else if (percent >= 50) {
        scoreBar.className = 'st-score__bar-fill st-score__bar-fill--good';
    } else {
        scoreBar.className = 'st-score__bar-fill st-score__bar-fill--needs-work';
    }

    // Ukryj progress bar na ekranie końcowym
    progressBar.style.display = 'none';

    showScreen('finish');
}
