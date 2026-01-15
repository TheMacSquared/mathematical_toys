# Quiz - Typy Zmiennych Losowych

Interaktywny quiz do nauki rozróżniania czterech typów zmiennych statystycznych:
- **Ilościowa dyskretna** - wartości przeliczalne (liczby całkowite)
- **Ilościowa ciągła** - wartości z przedziału (nieprzeliczalne)
- **Jakościowa porządkowa** - kategorie z naturalnym porządkiem
- **Jakościowa nominalna** - kategorie bez porządku

## Funkcje

- 25 przykładowych pytań z różnych dziedzin
- Losowa kolejność pytań (bez powtórzeń w sesji)
- Natychmiastowy feedback z wyjaśnieniem
- Podświetlenie poprawnej odpowiedzi
- Responsywny interfejs
- Spójny styl wizualny z pozostałymi zabawkami

## Uruchomienie (Development Mode)

### Windows PowerShell

```powershell
# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj venv
.\venv\Scripts\Activate.ps1

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python main.py
```

### Linux/Mac

```bash
# Utwórz środowisko wirtualne
python3 -m venv venv

# Aktywuj venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python main.py
```

## Budowanie .exe (Windows)

```powershell
# Upewnij się, że venv jest aktywny
python build.py
```

Plik `.exe` zostanie utworzony w `dist/typ_zmiennych_quiz.exe`.

## Dodawanie Nowych Pytań

1. Edytuj plik `questions.json`
2. Dodaj nowe pytanie w formacie:
```json
{
  "id": 26,
  "question": "Opis zmiennej (np. wartości przykładowe)",
  "correct": "ilosciowa_dyskretna",
  "explanation": "Wyjaśnienie dlaczego ta odpowiedź jest poprawna."
}
```
3. Sprawdź poprawność składni JSON
4. Przebuduj .exe: `python build.py`

**Dostępne wartości dla `correct`:**
- `ilosciowa_dyskretna`
- `ilosciowa_ciagla`
- `jakosciowa_porzadkowa`
- `jakosciowa_nominalna`

## Struktura Projektu

```
typ_zmiennych_quiz/
├── app.py                  # Flask backend (3 endpointy API)
├── main.py                 # PyWebView wrapper
├── build.py                # Skrypt budowania .exe
├── questions.json          # Bank pytań (25 pytań)
├── requirements.txt        # Zależności Python
├── templates/
│   └── index.html          # UI quizu
└── static/
    ├── style.css           # Style (spójne z histogramem)
    └── script.js           # Logika quizu (fetch API)
```

## API Endpoints

### `POST /api/start`
Inicjalizuje sesję quizu (shuffluje pytania).

**Response:**
```json
{
  "success": true,
  "total_questions": 25
}
```

### `GET /api/next`
Zwraca kolejne pytanie (bez poprawnej odpowiedzi).

**Response:**
```json
{
  "success": true,
  "finished": false,
  "question": {
    "id": 5,
    "question": "Liczba dzieci w rodzinie (0, 1, 2, 3, ...)"
  },
  "remaining": 20
}
```

### `POST /api/check`
Sprawdza odpowiedź użytkownika.

**Request:**
```json
{
  "question_id": 5,
  "answer": "ilosciowa_dyskretna"
}
```

**Response:**
```json
{
  "success": true,
  "correct": true,
  "explanation": "Liczba dzieci to wartości przeliczalne (liczby całkowite nieujemne). To zmienna ilościowa dyskretna.",
  "correct_answer": "ilosciowa_dyskretna"
}
```

## Technologie

- **Backend**: Flask 3.0+ (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Desktop**: PyWebView 5.0+ (native window)
- **Build**: PyInstaller 6.0+ (standalone .exe)

## Licencja

Część projektu "Statystyczne Zabawki" - narzędzia do nauczania statystyki.
