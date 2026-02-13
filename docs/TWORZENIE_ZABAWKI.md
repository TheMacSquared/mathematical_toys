# Tworzenie Nowej Zabawki - Instrukcja Krok po Kroku

Ten dokument przeprowadzi Cie przez caly proces tworzenia nowej interaktywnej zabawki matematycznej od zera do gotowego pliku .exe.

## Spis Tresci

1. [Wymagania Wstepne](#wymagania-wstepne)
2. [Architektura Zabawki](#architektura-zabawki)
3. [Krok 1: Setup Struktury](#krok-1-setup-struktury)
4. [Krok 2: Backend Flask](#krok-2-backend-flask)
5. [Krok 3: Frontend (HTML/CSS/JS)](#krok-3-frontend-htmlcssjs)
6. [Krok 4: PyWebView Wrapper](#krok-4-pywebview-wrapper)
7. [Krok 5: Testowanie Lokalne](#krok-5-testowanie-lokalne)
8. [Krok 6: Budowanie .exe](#krok-6-budowanie-exe)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Checklist Przed Publishem](#checklist-przed-publishem)

---

## Wymagania Wstepne

### Software
- **Python 3.10+**
  - Pobierz z [python.org](https://www.python.org/downloads/)
  - Podczas instalacji zaznacz "Add Python to PATH"

- **Git** (opcjonalnie, ale zalecane)
  - Pobierz z [git-scm.com](https://git-scm.com/)

### Umiejetnosci
- Podstawowa znajomosc Python (pisanie funkcji, listy, slowniki)
- Podstawowa HTML/CSS (struktura strony, style)
- Podstawowa JavaScript (zmienne, funkcje, fetch API)
- **Nie musisz byc ekspertem!** - dostarczone template wystarczy do startu

### Setup Projektu
```bash
cd mathematical_toys
pip install -r requirements.txt
```

---

## Architektura Zabawki

Kazda zabawka sklada sie z trzech warstw:

```
┌─────────────────────────────────────┐
│   PyWebView (Natywne Okno)         │
│   ┌─────────────────────────────┐   │
│   │  Frontend (HTML/CSS/JS)     │   │ <- UI (suwaki, wykresy)
│   │  - index.html               │   │
│   │  - script.js                │   │
│   │  - style.css                │   │
│   └──────────┬──────────────────┘   │
│              │ HTTP (fetch)          │
│   ┌──────────▼──────────────────┐   │
│   │  Backend (Flask)            │   │ <- Logika (Python)
│   │  - app.py                   │   │
│   │  - endpointy API            │   │
│   └─────────────────────────────┘   │
│   ┌─────────────────────────────┐   │
│   │  main.py                    │   │ <- Wrapper (uruchamia wszystko)
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Przeplyw danych**:
1. Student zmienia parametr w UI (suwak, input, klikniecie)
2. JavaScript wywoluje fetch() do Flask endpoint
3. Flask wykonuje obliczenia w Python (numpy, scipy)
4. Flask zwraca JSON z wynikami
5. JavaScript aktualizuje wykres Plotly.js

---

## Krok 1: Setup Struktury

Stworz nowa zabawke w katalogu `toys/`:

```bash
cd toys
mkdir nazwa_zabawki
cd nazwa_zabawki
mkdir templates static
```

Struktura powinna wygladac tak:

```
toys/nazwa_zabawki/
├── app.py              # Backend Flask
├── main.py             # PyWebView wrapper
├── templates/
│   └── index.html      # UI (strona HTML)
└── static/
    ├── style.css       # Style specyficzne dla apki
    ├── script.js       # Logika JavaScript
    └── favicon.svg     # Ikona
```

---

## Krok 2: Backend Flask

Stworz plik `app.py` - wzoruj sie na istniejacych apkach (`linear_transforms`, `matrix_calculator`, `taylor_series`):

```python
from flask import Flask, render_template, jsonify, request
import numpy as np
import os
import sys

from common.flask_app import register_common_static


def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(__file__)


bundle_dir = get_bundle_dir()
app = Flask(__name__,
            template_folder=os.path.join(bundle_dir, 'templates'),
            static_folder=os.path.join(bundle_dir, 'static'))

register_common_static(app, bundle_dir if getattr(sys, 'frozen', False) else None)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/compute', methods=['POST'])
def compute():
    try:
        data = request.json
        if data is None:
            raise ValueError("Wymagane dane w formacie JSON")

        # === TUTAJ TWOJA LOGIKA ===

        return jsonify({'success': True, 'result': ...})

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        return jsonify({'success': False, 'error': 'Nieoczekiwany blad serwera'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5XXX)
```

**Kluczowe punkty**:
- Uzywaj `common.flask_app.register_common_static` do wspolnego CSS
- Uzywaj `get_bundle_dir()` dla kompatybilnosci z PyInstaller
- Zawsze zwracaj `{'success': True/False, ...}`
- Obsluguj bledy z try/except

---

## Krok 3: Frontend (HTML/CSS/JS)

### 3.1 HTML (`templates/index.html`)

Uzywaj wspolnego systemu CSS (shared.css) i klas `st-*`:

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nazwa Zabawki</title>
    <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='favicon.svg') }}">
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <link rel="stylesheet" href="/common/shared.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body class="st-app st-page">
    <div class="st-card st-card--wide">
        <header class="st-header">
            <h1 class="st-header__title">Nazwa Zabawki</h1>
            <p class="st-header__subtitle">Krotki opis</p>
        </header>

        <div class="st-layout-2col">
            <aside class="st-sidebar">
                <!-- Kontrolki -->
            </aside>
            <main>
                <div class="st-plot">
                    <div id="plot"></div>
                </div>
            </main>
        </div>
    </div>

    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
```

### 3.2 CSS (`static/style.css`)

Dodaj tylko style specyficzne dla swojej apki. Wspolny design system jest w `shared.css`.

### 3.3 JavaScript (`static/script.js`)

Wzorzec: stan aplikacji -> fetch do API -> aktualizacja Plotly:

```javascript
const state = { /* parametry */ };
let debounceTimer = null;

document.addEventListener('DOMContentLoaded', function() {
    setupInputs();
    triggerComputation();
});

async function triggerComputation() {
    const response = await fetch('/api/compute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
    });
    const data = await response.json();
    if (data.success) {
        updatePlot(data);
    }
}
```

---

## Krok 4: PyWebView Wrapper

Stworz `main.py`:

```python
import webview
from threading import Thread
import time
from app import app

PORT = 15XXX  # Uzywaj portow 15005+

def start_flask():
    app.run(port=PORT, debug=False, use_reloader=False)

def main():
    flask_thread = Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(1)
    webview.create_window(
        title='Nazwa Zabawki',
        url=f'http://127.0.0.1:{PORT}',
        width=1400, height=900,
        resizable=True, min_size=(900, 600)
    )
    webview.start()

if __name__ == '__main__':
    main()
```

---

## Krok 5: Testowanie Lokalne

```bash
cd toys/nazwa_zabawki
python main.py
```

Powinna otworzyc sie okno aplikacji. Przetestuj:
- [ ] Kontrolki dzialaja
- [ ] Wykres sie aktualizuje
- [ ] Brak bledow w konsoli

**Debugowanie**: Uruchom samego Flask: `python app.py` i otworz http://localhost:5XXX

---

## Krok 6: Budowanie .exe

### 6.1 Stworz `build.py`

```python
import PyInstaller.__main__
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=NazwaZabawki',
    f'--add-data={templates_dir};templates',
    f'--add-data={static_dir};static',
    '--clean',
    '--noconfirm'
])
```

### 6.2 Zbuduj

```bash
python build.py
```

---

## Best Practices

### Organizacja Kodu
- Trzymaj logike matematyczna w oddzielnych funkcjach (latwiejsze testy)
- Nie mieszaj backendu i frontendu - komunikacja tylko przez API
- Uzywaj try/except dla bledow uzytkownika

### Wydajnosc
- **Debouncing**: Dla suwakoow dodaj opoznienie 200-300ms
- **Limit danych**: Nie wysylaj gigantycznych tablic (max 10000 punktow)

### UI/UX
- Responsywny design (dziala na malych ekranach)
- Loading indicator dla wolnych obliczen
- Sensowne domyslne wartosci parametrow

---

## Troubleshooting

### PyInstaller nie znajduje templates/static
Upewnij sie ze sciezki w `build.py` sa poprawne. Windows wymaga `;` a nie `:`.

### PyWebView nie startuje (Windows)
Zainstaluj Edge WebView2 Runtime.

### Import errors po zbudowaniu .exe
Dodaj `--hidden-import=nazwa_modulu` do build.py.

---

## Checklist Przed Publishem

- [ ] Aplikacja dziala lokalnie (`python main.py`)
- [ ] `.exe` buduje sie bez bledow
- [ ] `.exe` dziala standalone
- [ ] Kontrolki dzialaja
- [ ] Wykres sie aktualizuje poprawnie
- [ ] Bledy sa obslugiwane (nie crashuje)
- [ ] Dodane testy w `tests/`
- [ ] Przetestowane na czystym Windows

---

## Przyklady Referencyjne

Zobacz istniejace zabawki jako kompletne przyklady:
- `toys/linear_transforms/` - wizualizacja z Plotly, presety, panel wynikow
- `toys/matrix_calculator/` - tabela edytowalna, krok po kroku
- `toys/taylor_series/` - suwaki + wykres, tabela wspolczynnikow

---

## Potrzebujesz Pomocy?

- Sprawdz istniejace zabawki jako referencje
- Dokumentacja Flask: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- Dokumentacja Plotly: [plotly.com/javascript/](https://plotly.com/javascript/)
- Dokumentacja PyWebView: [pywebview.flowrl.com](https://pywebview.flowrl.com/)
