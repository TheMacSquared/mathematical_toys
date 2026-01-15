// Stan quizu
let currentQuestion = null;
let answered = false;

// Elementy DOM
let startScreen, questionScreen, finishScreen, loadingEl;
let btnStart, btnNext, btnRestart;
let questionText, feedbackBox, feedbackHeader, feedbackText;
let answerButtons;

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

    answerButtons = document.querySelectorAll('.btn-answer');

    // Event listeners
    btnStart.addEventListener('click', startQuiz);
    btnRestart.addEventListener('click', startQuiz);
    btnNext.addEventListener('click', loadNextQuestion);

    answerButtons.forEach(btn => {
        btn.addEventListener('click', handleAnswer);
    });
});

/**
 * Rozpocznij quiz - inicjalizacja sesji
 */
async function startQuiz() {
    try {
        showLoading();

        // Wywołaj /api/start (shuffle pytań)
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        if (data.success) {
            // Przejdź do ekranu pytań
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

        // Reset stanu
        answered = false;
        feedbackBox.classList.add('hidden');
        enableAnswerButtons();

        // Pobierz pytanie z /api/next
        const response = await fetch('/api/next');

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        if (data.success) {
            if (data.finished) {
                // Koniec pytań
                showScreen('finish');
            } else {
                // Wyświetl pytanie
                currentQuestion = data.question;
                questionText.textContent = currentQuestion.question;
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
 * Obsługa wyboru odpowiedzi
 */
async function handleAnswer(event) {
    if (answered) return;  // Już odpowiedziano

    const selectedAnswer = event.target.dataset.answer;

    try {
        showLoading();

        // Wyślij odpowiedź do /api/check
        const response = await fetch('/api/check', {
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
            disableAnswerButtons();

            // Pokaż feedback
            if (data.correct) {
                feedbackHeader.textContent = '✅ Poprawna odpowiedź!';
                feedbackHeader.className = 'feedback-header correct';
            } else {
                feedbackHeader.textContent = '❌ Niepoprawna odpowiedź';
                feedbackHeader.className = 'feedback-header incorrect';
            }

            feedbackText.textContent = data.explanation;
            feedbackBox.classList.remove('hidden');

            // Podświetl poprawną odpowiedź
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
 * Podświetl poprawną odpowiedź (zielone) i niepoprawną (czerwone)
 */
function highlightCorrectAnswer(correctAnswer, userAnswer) {
    answerButtons.forEach(btn => {
        const answer = btn.dataset.answer;

        if (answer === correctAnswer) {
            btn.classList.add('correct');
        } else if (answer === userAnswer && userAnswer !== correctAnswer) {
            btn.classList.add('incorrect');
        }
    });
}

/**
 * Wyłącz przyciski odpowiedzi (po odpowiedzi)
 */
function disableAnswerButtons() {
    answerButtons.forEach(btn => {
        btn.disabled = true;
        btn.style.cursor = 'not-allowed';
    });
}

/**
 * Włącz przyciski odpowiedzi (nowe pytanie)
 */
function enableAnswerButtons() {
    answerButtons.forEach(btn => {
        btn.disabled = false;
        btn.style.cursor = 'pointer';
        btn.classList.remove('correct', 'incorrect');
    });
}

/**
 * Pokaż określony ekran (start/question/finish)
 */
function showScreen(screenName) {
    startScreen.classList.remove('active');
    questionScreen.classList.remove('active');
    finishScreen.classList.remove('active');

    if (screenName === 'start') startScreen.classList.add('active');
    else if (screenName === 'question') questionScreen.classList.add('active');
    else if (screenName === 'finish') finishScreen.classList.add('active');
}

/**
 * Pokaż/ukryj loading indicator
 */
function showLoading() {
    loadingEl.classList.add('active');
}

function hideLoading() {
    loadingEl.classList.remove('active');
}
