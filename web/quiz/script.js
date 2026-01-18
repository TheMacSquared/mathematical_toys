/**
 * Quiz Statystyczny - Wersja Webowa (bez backendu)
 * Cala logika dziala w przegladarce
 */

// Stan quizu
let quizConfig = null;      // Konfiguracja aktualnego quizu
let allQuestions = [];      // Wszystkie pytania
let remainingQuestions = []; // Indeksy pytan do zadania
let currentQuestion = null;  // Aktualne pytanie
let answered = false;

// Elementy DOM
let startScreen, questionScreen, finishScreen, loadingEl;
let btnStart, btnNext, btnRestart;
let questionText, feedbackBox, feedbackHeader, feedbackText;
let answersGrid;

/**
 * Inicjalizacja po zaladowaniu strony
 */
document.addEventListener('DOMContentLoaded', async function() {
    // Pobranie elementow DOM
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

    // Event listeners
    btnStart.addEventListener('click', startQuiz);
    btnRestart.addEventListener('click', startQuiz);
    btnNext.addEventListener('click', loadNextQuestion);

    // Zaladuj quiz na podstawie parametru URL
    await initializeQuiz();
});

/**
 * Pobierz ID quizu z URL i zaladuj dane
 */
async function initializeQuiz() {
    try {
        showLoading();

        // Pobierz ID quizu z URL (?id=xxx)
        const urlParams = new URLSearchParams(window.location.search);
        const quizId = urlParams.get('id');

        if (!quizId) {
            throw new Error('Brak parametru id w URL');
        }

        // Zaladuj konfiguracje quizow
        const configResponse = await fetch('data/quiz_config.json');
        const configData = await configResponse.json();

        // Znajdz konfiguracje dla tego quizu
        quizConfig = configData.quizzes.find(q => q.id === quizId);

        if (!quizConfig) {
            throw new Error(`Quiz "${quizId}" nie znaleziony`);
        }

        // Zaktualizuj naglowek strony
        document.getElementById('quiz-title').textContent =
            `${quizConfig.emoji} ${quizConfig.name}`;
        document.getElementById('quiz-subtitle').textContent = quizConfig.description;
        document.title = `${quizConfig.emoji} ${quizConfig.name}`;

        // Zaladuj pytania
        const questionsResponse = await fetch(`data/${quizConfig.file}`);
        const questionsData = await questionsResponse.json();
        allQuestions = questionsData.questions;

    } catch (error) {
        console.error('Blad inicjalizacji:', error);
        alert('Blad ladowania quizu: ' + error.message);
        window.location.href = 'index.html';
    } finally {
        hideLoading();
    }
}

/**
 * Rozpocznij quiz - tasuj pytania
 */
function startQuiz() {
    // Utworz tablice indeksow i przetasuj
    remainingQuestions = allQuestions.map((_, index) => index);
    shuffleArray(remainingQuestions);

    // Przejdz do ekranu pytan
    showScreen('question');
    loadNextQuestion();
}

/**
 * Zaladuj kolejne pytanie
 */
function loadNextQuestion() {
    // Reset stanu
    answered = false;
    feedbackBox.classList.add('hidden');

    // Sprawdz czy sa pytania
    if (remainingQuestions.length === 0) {
        showScreen('finish');
        return;
    }

    // Pobierz kolejne pytanie
    const questionIndex = remainingQuestions.shift();
    currentQuestion = allQuestions[questionIndex];

    // Wyswietl pytanie
    questionText.textContent = currentQuestion.question;

    // Wygeneruj przyciski odpowiedzi
    generateAnswerButtons();
}

/**
 * Generuj przyciski odpowiedzi
 */
function generateAnswerButtons() {
    answersGrid.innerHTML = '';

    let options = [];

    // Okresl opcje odpowiedzi na podstawie typu quizu
    if (quizConfig.answer_type === 'multiple_choice_4' ||
        quizConfig.answer_type === 'multiple_choice_3') {
        // Stale opcje (typy zmiennych, rozklady)
        options = quizConfig.options;
    } else if (quizConfig.answer_type === 'multiple_choice_random') {
        // Losowe 3 opcje z puli (testy statystyczne)
        options = getRandomOptions(quizConfig.all_options, currentQuestion.correct, 3);
    }

    // Dostosuj grid do liczby opcji
    if (options.length === 3) {
        answersGrid.className = 'answers-grid grid-3';
    } else if (options.length === 4) {
        answersGrid.className = 'answers-grid grid-4';
    }

    // Utworz przyciski
    options.forEach(option => {
        const btn = document.createElement('button');
        btn.className = 'btn-answer';

        if (typeof option === 'string') {
            // Dla testow - opcje sa stringami
            btn.dataset.answer = option;
            btn.textContent = option;
        } else {
            // Dla innych quizow - opcje to obiekty {value, label}
            btn.dataset.answer = option.value;
            btn.textContent = option.label;
        }

        btn.addEventListener('click', handleAnswer);
        answersGrid.appendChild(btn);
    });
}

/**
 * Losuj n opcji z tablicy, zapewniajac ze correct jest w wyniku
 */
function getRandomOptions(allOptions, correctAnswer, n) {
    // Usun correct z puli
    const otherOptions = allOptions.filter(opt => opt !== correctAnswer);

    // Wylosuj (n-1) niepoprawnych odpowiedzi
    shuffleArray(otherOptions);
    const selected = otherOptions.slice(0, n - 1);

    // Dodaj correct i wymieszaj wszystko
    const result = [...selected, correctAnswer];
    shuffleArray(result);

    return result;
}

/**
 * Obsluga wyboru odpowiedzi
 */
function handleAnswer(event) {
    if (answered) return;

    answered = true;
    const selectedAnswer = event.target.dataset.answer;
    const isCorrect = (selectedAnswer === currentQuestion.correct);

    // Wylacz przyciski
    disableAnswerButtons();

    // Pokaz feedback
    if (isCorrect) {
        feedbackHeader.textContent = 'Poprawna odpowiedz!';
        feedbackHeader.className = 'feedback-header correct';
    } else {
        feedbackHeader.textContent = 'Niepoprawna odpowiedz';
        feedbackHeader.className = 'feedback-header incorrect';
    }

    feedbackText.textContent = currentQuestion.explanation;
    feedbackBox.classList.remove('hidden');

    // Podswietl odpowiedzi
    highlightCorrectAnswer(currentQuestion.correct, selectedAnswer);
}

/**
 * Podswietl poprawna odpowiedz (zielona) i niepoprawna (czerwona)
 */
function highlightCorrectAnswer(correctAnswer, userAnswer) {
    const answerButtons = answersGrid.querySelectorAll('.btn-answer');

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
 * Wylacz przyciski odpowiedzi
 */
function disableAnswerButtons() {
    const answerButtons = answersGrid.querySelectorAll('.btn-answer');
    answerButtons.forEach(btn => {
        btn.disabled = true;
        btn.style.cursor = 'not-allowed';
    });
}

/**
 * Pokaz okreslony ekran (start/question/finish)
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
 * Pokaz/ukryj loading indicator
 */
function showLoading() {
    loadingEl.classList.add('active');
}

function hideLoading() {
    loadingEl.classList.remove('active');
}

/**
 * Tasowanie tablicy (Fisher-Yates)
 */
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}
