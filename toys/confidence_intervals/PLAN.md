# Plan: Aplikacja Przedziały Ufności (Quiz + Wizualizacja)

## Problem dydaktyczny

**Obserwacja:** Studenci mają problem z interpretacją przedziałów ufności:
- Błędne wnioskowanie na podstawie jednego przedziału ("CI 95%: [14; 22] → czy średnia > 20?")
- Błędne porównywanie dwóch grup ("CI dla Warszawy vs Wrocławia")
- Mylenie przedziału ufności z przedziałem wartości możliwych

**Cel:** Interaktywny quiz + wizualizacja, który uczy:
1. Kiedy przedział ufności pozwala na wnioskowanie (tak/nie)
2. Różnica między przedziałami dla jednej próbki vs porównanie grup
3. Intuicja: im szerszy przedział, tym mniej informacji

---

## Koncepcja Aplikacji

### Nazwa
**"Przedziały Ufności - Quiz Interpretacyjny"**

### Typ
Quiz z wizualizacją + feedback edukacyjny

### Struktura
1. **Menu startowe** - wybór trybu:
   - **Tryb 1:** Pojedynczy przedział vs wartość (20 pytań)
   - **Tryb 2:** Porównanie dwóch grup (20 pytań)

2. **Ekran quizu:**
   - Treść zadania (np. "CI 95%: [14; 22]. Czy średnia > 20?")
   - **Wizualizacja:** Oś liczbowa z przedziałem CI + testowaną wartością
   - Przyciski: **TAK** / **NIE** / **NIE MOŻNA POWIEDZIEĆ**
   - Feedback po odpowiedzi:
     - Poprawna odpowiedź
     - Wyjaśnienie dlaczego (kluczowe zasady interpretacji)
     - Podświetlenie na wykresie (np. wartość poza/w/blisko przedziału)

3. **Wizualizacja:**
   - **Tryb 1:** Oś liczbowa + przedział CI + testowana wartość (pionowa kreska)
   - **Tryb 2:** Dwa przedziały CI na jednej osi + porównanie
   - Kolory:
     - Przedział CI: niebieski pasek
     - Testowana wartość: czerwona pionowa linia
     - Obszar przesądzający: podświetlony po odpowiedzi

---

## Pytania - Tryb 1 (Pojedynczy przedział vs wartość)

### Format JSON:
```json
{
  "id": 1,
  "question": "Przedział ufności 95% dla średniej ceny kawy w mieście wynosi [14; 22] zł. Czy można powiedzieć z ufnością 95%, że średnia cena kawy przekracza 20 zł?",
  "ci_lower": 14,
  "ci_upper": 22,
  "tested_value": 20,
  "correct": "nie_mozna_powiedziec",
  "explanation": "Wartość 20 zł znajduje się WEWNĄTRZ przedziału ufności [14; 22]. Przedział ufności nie pozwala na jednoznaczne stwierdzenie, czy średnia jest większa czy mniejsza od wartości znajdującej się wewnątrz tego przedziału. Możemy tylko stwierdzić z 95% ufnością, że średnia znajduje się gdzieś w przedziale [14; 22], ale nie wiemy dokładnie gdzie."
}
```

### Przykładowe pytania (20 pytań):

**Kategoria: Wartość poza przedziałem (łatwe)**
1. CI: [14; 22], test: 25 → **NIE** (25 > 22, średnia NIE przekracza 25)
2. CI: [50; 80], test: 40 → **TAK** (40 < 50, średnia PRZEKRACZA 40)
3. CI: [100; 150], test: 90 → **TAK** (90 < 100, średnia > 90)

**Kategoria: Wartość na granicy przedziału (średnie)**
4. CI: [14; 22], test: 14 → **NIE MOŻNA** (14 jest dolną granicą)
5. CI: [14; 22], test: 22 → **NIE MOŻNA** (22 jest górną granicą)

**Kategoria: Wartość w środku przedziału (trudne)**
6. CI: [14; 22], test: 18 → **NIE MOŻNA** (18 w środku przedziału)
7. CI: [14; 22], test: 20 → **NIE MOŻNA** (20 w środku przedziału)

**Kategoria: Różne konteksty (różnicowanie)**
8. CI: [5.2; 6.8] kg, test: 7 kg → **NIE** (waga NIE przekracza 7 kg)
9. CI: [120; 140] mmHg, test: 110 → **TAK** (ciśnienie PRZEKRACZA 110)
10. CI: [85; 95]%, test: 90% → **NIE MOŻNA** (90% w środku)

**Kategoria: Pytania odwrotne ("czy średnia jest mniejsza niż...")**
11. CI: [14; 22], test: 12 → czy średnia < 12? → **NIE** (12 < 14)
12. CI: [14; 22], test: 25 → czy średnia < 25? → **NIE MOŻNA** (nie wiemy, czy < 25)
13. CI: [14; 22], test: 30 → czy średnia < 30? → **TAK** (22 < 30)

**Kategoria: Wartości bliskie granicom (pułapki)**
14. CI: [14.0; 22.0], test: 14.1 → **NIE MOŻNA** (14.1 tuż nad dolną granicą)
15. CI: [14.0; 22.0], test: 21.9 → **NIE MOŻNA** (21.9 tuż pod górną granicą)

**Kategoria: Różne szerokości przedziałów (intuicja niepewności)**
16. CI: [18; 19], test: 20 → **NIE** (wąski przedział, 20 poza nim)
17. CI: [10; 30], test: 20 → **NIE MOŻNA** (szeroki przedział, 20 w środku)

**Kategoria: Wartości zerowe / ujemne**
18. CI: [-5; 5], test: 0 → **NIE MOŻNA** (0 w środku)
19. CI: [-10; -2], test: 0 → **NIE** (0 > -2, średnia NIE przekracza 0)
20. CI: [2; 10], test: 0 → **TAK** (0 < 2, średnia PRZEKRACZA 0)

---

## Pytania - Tryb 2 (Porównanie dwóch grup)

### Format JSON:
```json
{
  "id": 1,
  "question": "Przedział ufności 95% dla średniej ceny kawy w Warszawie: [18; 24] zł. We Wrocławiu: [14; 20] zł. Czy można powiedzieć z ufnością 95%, że średnia cena w Warszawie jest wyższa niż we Wrocławiu?",
  "ci1_lower": 18,
  "ci1_upper": 24,
  "ci1_label": "Warszawa",
  "ci2_lower": 14,
  "ci2_upper": 20,
  "ci2_label": "Wrocław",
  "correct": "nie_mozna_powiedziec",
  "explanation": "Przedziały ufności dla Warszawy [18; 24] i Wrocławia [14; 20] SIĘ NAKŁADAJĄ (część wspólna: [18; 20]). Nakładanie się przedziałów oznacza, że nie możemy z ufnością 95% stwierdzić, która średnia jest wyższa. Możliwe, że średnia w Warszawie to 19 zł, a we Wrocławiu 20 zł, czyli Wrocław byłby droższy. Aby stwierdzić różnicę, przedziały NIE MOGĄ się nakładać."
}
```

### Przykładowe pytania (20 pytań):

**Kategoria: Przedziały całkowicie rozdzielone (łatwe)**
1. Warszawa: [18; 24], Wrocław: [10; 16] → **TAK** (Warszawa wyższa)
2. Warszawa: [50; 60], Wrocław: [70; 80] → **NIE** (Wrocław wyższy)
3. Grupa A: [100; 120], Grupa B: [80; 95] → **TAK** (A > B)

**Kategoria: Przedziały nakładają się (średnie)**
4. Warszawa: [18; 24], Wrocław: [14; 20] → **NIE MOŻNA** (nakładają się [18; 20])
5. Grupa A: [50; 70], Grupa B: [60; 80] → **NIE MOŻNA** (nakładają się [60; 70])

**Kategoria: Przedziały dotykają się na granicy (trudne)**
6. Warszawa: [18; 24], Wrocław: [12; 18] → **NIE MOŻNA** (stykają się w 18)
7. Grupa A: [50; 60], Grupa B: [60; 70] → **NIE MOŻNA** (stykają się w 60)

**Kategoria: Różne konteksty**
8. Mężczyźni: [175; 185] cm, Kobiety: [160; 170] cm → **TAK** (M > K)
9. Przed: [120; 140] mmHg, Po: [110; 130] → **NIE MOŻNA** (nakładają się)

**Kategoria: Przedziały identyczne (pułapka)**
10. Warszawa: [18; 24], Wrocław: [18; 24] → **NIE MOŻNA** (identyczne)

**Kategoria: Przedziały zawierają się w sobie**
11. Grupa A: [50; 70], Grupa B: [55; 65] → **NIE MOŻNA** (B zawiera się w A)

**Kategoria: Pytania odwrotne ("czy A jest niższa niż B?")**
12. Warszawa: [18; 24], Wrocław: [10; 16] → czy W < Wr? → **NIE** (W > Wr)
13. Warszawa: [18; 24], Wrocław: [26; 32] → czy W < Wr? → **TAK** (W < Wr)

**Kategoria: Małe odstępy między przedziałami (pułapki)**
14. A: [50; 55], B: [56; 60] → **TAK** (rozdzielone, choć blisko)
15. A: [50; 55], B: [54; 60] → **NIE MOŻNA** (nakładają się [54; 55])

**Kategoria: Wartości zerowe / ujemne**
16. Przed: [-5; 5], Po: [-10; 0] → **NIE MOŻNA** (nakładają się)
17. Przed: [2; 10], Po: [-5; 0] → **TAK** (Przed > Po)

**Kategoria: Różne szerokości przedziałów (intuicja niepewności)**
18. A: [18; 19], B: [10; 30] → **NIE MOŻNA** (szeroki B nakłada się na wąski A)
19. A: [50; 52], B: [55; 57] → **TAK** (oba wąskie, rozdzielone)

**Kategoria: Pytania kombinowane (3+ grupy - bonus)**
20. A: [50; 60], B: [70; 80], C: [55; 65] → czy A < B? → **TAK** (mimo że C się z nimi nakłada)

---

## Wizualizacja

### Tryb 1: Pojedynczy przedział vs wartość

**Diagram:**
```
          [────────────]   CI 95%
    ──────|──────────|──|────────────
         14         20  22          30
                     ↑
              wartość testowana
```

**Implementacja (JavaScript + SVG lub Canvas):**
- Oś X: od `min(ci_lower - 5, tested_value - 5)` do `max(ci_upper + 5, tested_value + 5)`
- Przedział CI: niebieski prostokąt (szerokość 10px)
- Testowana wartość: czerwona pionowa linia (przerywaną)
- Po odpowiedzi: podświetlenie obszaru decydującego (zielony/czerwony)

**Kolory po odpowiedzi:**
- **Poprawna odpowiedź "TAK":** przedział zielony, wartość czerwona (poza przedziałem)
- **Poprawna odpowiedź "NIE":** przedział zielony, wartość czerwona (poza przedziałem)
- **Poprawna odpowiedź "NIE MOŻNA":** przedział niebieski, wartość żółta (w środku)
- **Niepoprawna odpowiedź:** przedział czerwony, wyjaśnienie

### Tryb 2: Porównanie dwóch grup

**Diagram:**
```
Warszawa:     [───────────────]
              18              24

Wrocław:    [───────────────]
           14              20

    ──────|───|───────────|───|────────────
         14  18          20  24
              └───────────┘
             nakładanie się
```

**Implementacja:**
- Dwa przedziały CI na jednej osi
- Kolor 1: niebieski (grupa 1)
- Kolor 2: pomarańczowy (grupa 2)
- Po odpowiedzi: podświetlenie nakładania się (żółty obszar) lub rozdzielenia (zielone odstępy)

---

## Architektura Techniczna

### Zgodność z wytycznymi (TWORZENIE_ZABAWKI.md)

**Stack:**
- PyWebView + Flask + HTML/CSS/JS
- Zgodny z `histogram` i `quiz_app`

**Struktura katalogów:**
```
toys/confidence_intervals/
├── app.py                    # Flask backend
├── main.py                   # PyWebView wrapper
├── build.py                  # PyInstaller config
├── questions/
│   ├── single_interval.json  # 20 pytań - tryb 1
│   └── two_intervals.json    # 20 pytań - tryb 2
├── ci_config.json            # Konfiguracja trybów
├── requirements.txt
├── README.md
├── templates/
│   ├── menu.html             # Wybór trybu
│   └── quiz.html             # Quiz + wizualizacja
└── static/
    ├── style.css             # Style (bazowane na quiz_app)
    ├── script.js             # Logika quizu
    └── visualizer.js         # Rysowanie przedziałów CI
```

### Backend (app.py)

**Endpointy:**
```python
@app.route('/')
def index():
    """Menu - wybór trybu (single_interval / two_intervals)"""
    return render_template('menu.html', modes=CI_CONFIG)

@app.route('/quiz/<mode_id>')
def quiz(mode_id):
    """Strona quizu dla trybu"""
    return render_template('quiz.html', mode=CI_CONFIG[mode_id])

@app.route('/api/quiz/<mode_id>/start', methods=['POST'])
def start_quiz(mode_id):
    """Inicjalizuje sesję, tasuje pytania"""
    pass

@app.route('/api/quiz/<mode_id>/next', methods=['GET'])
def next_question(mode_id):
    """Zwraca kolejne pytanie (bez odpowiedzi)"""
    pass

@app.route('/api/quiz/<mode_id>/check', methods=['POST'])
def check_answer(mode_id):
    """Sprawdza odpowiedź, zwraca feedback + dane do wizualizacji"""
    pass
```

**Sesja quizu (in-memory):**
```python
quiz_session = {
    'mode_id': 'single_interval',
    'remaining_questions': [1, 3, 5, 7, ...],  # Shuffled IDs
    'current_question_id': 1,
    'score': 0,
    'total': 20
}
```

### Frontend (script.js + visualizer.js)

**Workflow:**
1. Użytkownik wybiera tryb (menu)
2. POST `/api/quiz/<mode_id>/start` → shuffle pytań
3. GET `/api/quiz/<mode_id>/next` → pobierz pytanie
4. Wyświetl pytanie + wizualizację (`visualizer.js`)
5. Użytkownik wybiera odpowiedź (TAK / NIE / NIE MOŻNA)
6. POST `/api/quiz/<mode_id>/check` → sprawdź odpowiedź
7. Wyświetl feedback + zaktualizuj wizualizację (podświetlenie)
8. Przycisk "Następne pytanie" → goto 3

**visualizer.js (funkcja główna):**
```javascript
function drawCI(mode, data, isAnswered, isCorrect) {
    const svg = d3.select("#ci-visualization");

    if (mode === 'single_interval') {
        // Rysuj przedział CI + testowaną wartość
        drawSingleCI(svg, data.ci_lower, data.ci_upper, data.tested_value);
    } else if (mode === 'two_intervals') {
        // Rysuj dwa przedziały CI
        drawTwoCI(svg, data.ci1_lower, data.ci1_upper, data.ci2_lower, data.ci2_upper);
    }

    if (isAnswered) {
        // Podświetl decydujący obszar (zielony/czerwony/żółty)
        highlightDecisionRegion(svg, data, isCorrect);
    }
}
```

**D3.js lub Canvas?**
- **D3.js:** Łatwiejsze manipulacje SVG, animacje, etykiety
- **Canvas:** Lżejsze, ale trudniejsze do aktualizacji
- **Rekomendacja:** D3.js (zgodne z `histogram`, łatwa integracja)

---

## Format Danych

### ci_config.json
```json
{
  "modes": [
    {
      "id": "single_interval",
      "name": "Pojedynczy przedział vs wartość",
      "emoji": "📊",
      "description": "Naucz się interpretować przedziały ufności: kiedy przedział pozwala na wnioskowanie o wartości parametru?",
      "answers": ["TAK", "NIE", "NIE MOŻNA POWIEDZIEĆ"]
    },
    {
      "id": "two_intervals",
      "name": "Porównanie dwóch grup",
      "emoji": "📈",
      "description": "Porównuj przedziały ufności dla dwóch grup: kiedy możemy stwierdzić różnicę między średnimi?",
      "answers": ["TAK", "NIE", "NIE MOŻNA POWIEDZIEĆ"]
    }
  ]
}
```

### single_interval.json (przykład)
```json
{
  "questions": [
    {
      "id": 1,
      "question": "Przedział ufności 95% dla średniej ceny kawy w mieście wynosi [14; 22] zł. Czy można powiedzieć z ufnością 95%, że średnia cena kawy przekracza 20 zł?",
      "ci_lower": 14,
      "ci_upper": 22,
      "tested_value": 20,
      "unit": "zł",
      "correct": "nie_mozna_powiedziec",
      "explanation": "Wartość 20 zł znajduje się WEWNĄTRZ przedziału ufności [14; 22]. Przedział ufności nie pozwala na jednoznaczne stwierdzenie, czy średnia jest większa czy mniejsza od wartości znajdującej się wewnątrz tego przedziału. Możemy tylko stwierdzić z 95% ufnością, że średnia znajduje się gdzieś w przedziale [14; 22], ale nie wiemy dokładnie gdzie."
    },
    {
      "id": 2,
      "question": "Przedział ufności 95% dla średniej wagi paczek: [5.2; 6.8] kg. Czy średnia waga przekracza 7 kg?",
      "ci_lower": 5.2,
      "ci_upper": 6.8,
      "tested_value": 7,
      "unit": "kg",
      "correct": "nie",
      "explanation": "Wartość 7 kg znajduje się POWYŻEJ górnej granicy przedziału ufności (6.8 kg). Z ufnością 95% możemy stwierdzić, że średnia waga NIE PRZEKRACZA 7 kg, ponieważ cały przedział [5.2; 6.8] jest poniżej 7 kg."
    }
  ]
}
```

### two_intervals.json (przykład)
```json
{
  "questions": [
    {
      "id": 1,
      "question": "Przedział ufności 95% dla średniej ceny kawy w Warszawie: [18; 24] zł. We Wrocławiu: [14; 20] zł. Czy można powiedzieć z ufnością 95%, że średnia cena w Warszawie jest wyższa niż we Wrocławiu?",
      "ci1_lower": 18,
      "ci1_upper": 24,
      "ci1_label": "Warszawa",
      "ci2_lower": 14,
      "ci2_upper": 20,
      "ci2_label": "Wrocław",
      "unit": "zł",
      "correct": "nie_mozna_powiedziec",
      "explanation": "Przedziały ufności dla Warszawy [18; 24] i Wrocławia [14; 20] SIĘ NAKŁADAJĄ (część wspólna: [18; 20]). Nakładanie się przedziałów oznacza, że nie możemy z ufnością 95% stwierdzić, która średnia jest wyższa. Możliwe, że średnia w Warszawie to 19 zł, a we Wrocławiu 20 zł, czyli Wrocław byłby droższy. Aby stwierdzić różnicę, przedziały NIE MOGĄ się nakładać."
    },
    {
      "id": 2,
      "question": "Przedział ufności 95% dla średniego wzrostu mężczyzn: [175; 185] cm. Kobiet: [160; 170] cm. Czy średni wzrost mężczyzn jest wyższy niż kobiet?",
      "ci1_lower": 175,
      "ci1_upper": 185,
      "ci1_label": "Mężczyźni",
      "ci2_lower": 160,
      "ci2_upper": 170,
      "ci2_label": "Kobiety",
      "unit": "cm",
      "correct": "tak",
      "explanation": "Przedziały ufności dla mężczyzn [175; 185] i kobiet [160; 170] SĄ CAŁKOWICIE ROZDZIELONE (nie nakładają się). Najniższa wartość dla mężczyzn (175 cm) jest wyższa niż najwyższa wartość dla kobiet (170 cm). Z ufnością 95% możemy stwierdzić, że średni wzrost mężczyzn JEST WYŻSZY niż kobiet."
    }
  ]
}
```

---

## UI/UX

### Layout quizu

```
┌─────────────────────────────────────────────────────┐
│  📊 Przedziały Ufności - Pojedynczy przedział       │
│  Pytanie 5 / 20                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Przedział ufności 95% dla średniej ceny kawy      │
│  w mieście wynosi [14; 22] zł.                     │
│                                                     │
│  Czy można powiedzieć z ufnością 95%,              │
│  że średnia cena kawy przekracza 20 zł?            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  WIZUALIZACJA:                                      │
│                                                     │
│          [────────────────]                         │
│    ──────|──────────────|──|────────────            │
│         14             20  22                       │
│                         ↑                           │
│                  wartość testowana                  │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│   [ TAK ]  [ NIE ]  [ NIE MOŻNA POWIEDZIEĆ ]       │
│                                                     │
├─────────────────────────────────────────────────────┤
│  (Po odpowiedzi:)                                   │
│                                                     │
│  ✅ Poprawna odpowiedź: NIE MOŻNA POWIEDZIEĆ        │
│                                                     │
│  Wyjaśnienie: Wartość 20 zł znajduje się WEWNĄTRZ  │
│  przedziału ufności [14; 22]. Przedział ufności    │
│  nie pozwala na jednoznaczne stwierdzenie, czy     │
│  średnia jest większa czy mniejsza od wartości     │
│  znajdującej się wewnątrz tego przedziału.         │
│                                                     │
│   [ Następne pytanie → ]                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Kolory i style

**Zgodność z quiz_app:**
- Tło: gradient purpurowy (jak histogram/quiz_app)
- Przyciski: zaokrąglone, cień, hover
- Wizualizacja: jasne tło (białe SVG), wyraźne kontrasty

**Kolory wizualizacji:**
- Przedział CI: `#4A90E2` (niebieski)
- Testowana wartość: `#E74C3C` (czerwony)
- Nakładanie się (tryb 2): `#F39C12` (pomarańczowy)
- Podświetlenie poprawne: `#27AE60` (zielony)
- Podświetlenie błędne: `#E74C3C` (czerwony)
- Podświetlenie "nie można": `#F1C40F` (żółty)

---

## Kluczowe zasady interpretacji (do wyjaśnień)

### Tryb 1: Pojedynczy przedział vs wartość

**Zasada 1:** Jeśli testowana wartość znajduje się **poza przedziałem** CI, możemy z ufnością 95% stwierdzić, czy średnia jest większa/mniejsza od tej wartości.

- **Wartość powyżej CI:** średnia < wartość → odpowiedź **NIE** (średnia NIE przekracza wartości)
- **Wartość poniżej CI:** średnia > wartość → odpowiedź **TAK** (średnia PRZEKRACZA wartość)

**Zasada 2:** Jeśli testowana wartość znajduje się **wewnątrz przedziału** CI (lub na granicy), **NIE MOŻEMY** z ufnością 95% stwierdzić, czy średnia jest większa/mniejsza.

**Zasada 3:** Przedział ufności mówi: "średnia znajduje się gdzieś w tym przedziale z ufnością 95%", ale nie mówi, gdzie dokładnie.

### Tryb 2: Porównanie dwóch grup

**Zasada 1:** Jeśli przedziały CI **nie nakładają się** (są rozdzielone), możemy z ufnością 95% stwierdzić, która średnia jest wyższa.

- Jeśli CI1 całkowicie powyżej CI2 → średnia 1 > średnia 2 → **TAK**
- Jeśli CI1 całkowicie poniżej CI2 → średnia 1 < średnia 2 → **NIE**

**Zasada 2:** Jeśli przedziały CI **nakładają się** (mają część wspólną), **NIE MOŻEMY** z ufnością 95% stwierdzić różnicy.

**Zasada 3:** "Nakładanie się" oznacza, że możliwe scenariusze obejmują zarówno średnią 1 > średnią 2, jak i średnią 1 < średnią 2.

**Zasada 4:** Przedziały "stykające się" na granicy (np. [10; 20] i [20; 30]) są traktowane jak nakładające się → **NIE MOŻNA**.

---

## Rozszerzenia (opcjonalne, na przyszłość)

### Poziom zaawansowany:
1. **Tryb 3:** Przedziały ufności dla różnicy średnich (CI dla μ1 - μ2)
   - Pytanie: "CI 95% dla różnicy [Warszawa - Wrocław]: [-2; 8] zł. Czy Warszawa jest droższa?"
   - Odpowiedź: NIE MOŻNA (0 znajduje się w przedziale [-2; 8])

2. **Tryb 4:** Przedziały ufności dla proporcji
   - Pytanie: "CI 95% dla odsetka poparcia: [45%; 55%]. Czy poparcie przekracza 50%?"
   - Odpowiedź: NIE MOŻNA (50% w przedziale)

3. **Tryb interaktywny:** Użytkownik przesuwa suwak "testowana wartość" i widzi, kiedy przedział CI pozwala na wnioskowanie.

4. **Statystyki:** Po zakończeniu quizu pokazać:
   - Procent poprawnych odpowiedzi
   - Które kategorie pytań sprawiały problemy
   - Sugerowane materiały do nauki

---

## Implementacja - Kolejność kroków

### Faza 1: Setup projektu
1. Utworzyć katalog `toys/confidence_intervals/`
2. Skopiować szkielet z `quiz_app` (struktura katalogów, requirements.txt)
3. Przygotować `ci_config.json` (2 tryby)
4. Przygotować `questions/single_interval.json` (20 pytań)
5. Przygotować `questions/two_intervals.json` (20 pytań)

### Faza 2: Backend
6. Implementować `app.py`:
   - Routing: `/`, `/quiz/<mode_id>`
   - API: `/api/quiz/<mode_id>/start`, `/next`, `/check`
   - Sesja: tasowanie pytań, śledzenie postępu
7. Implementować `main.py` (PyWebView wrapper)
8. Implementować `build.py` (PyInstaller config)

### Faza 3: Frontend UI
9. Implementować `templates/menu.html` (wybór trybu)
10. Implementować `templates/quiz.html` (pytanie + wizualizacja + przyciski + feedback)
11. Implementować `static/script.js` (logika quizu, API calls)
12. Implementować `static/style.css` (bazowane na quiz_app)

### Faza 4: Wizualizacja
13. Implementować `static/visualizer.js`:
    - Funkcja `drawSingleCI()` - rysowanie przedziału + wartość
    - Funkcja `drawTwoCI()` - rysowanie dwóch przedziałów
    - Funkcja `highlightDecisionRegion()` - podświetlanie po odpowiedzi
14. Integracja z D3.js (dodać do `requirements.txt` - CDN w HTML)

### Faza 5: Testowanie
15. Testować w dev mode (`python main.py`)
16. Sprawdzić wszystkie pytania (poprawność, wizualizacje)
17. Testować build `.exe` (opcjonalnie, tylko Windows)

### Faza 6: Dokumentacja i commit
18. Napisać `README.md` (opis, instalacja, użycie)
19. Git commit + push

---

## Checklist przed Implementacją

- [ ] Przygotować 20 pytań - tryb 1 (single_interval.json)
- [ ] Przygotować 20 pytań - tryb 2 (two_intervals.json)
- [ ] Zweryfikować poprawność odpowiedzi (zasady interpretacji CI)
- [ ] Zweryfikować jakość wyjaśnień (jasne, edukacyjne)
- [ ] Zaprojektować layout wizualizacji (oś, przedziały, etykiety)
- [ ] Wybrać bibliotekę do wizualizacji (D3.js vs Canvas)

---

## Pytania do Użytkownika

1. **Szerokość ekranu wizualizacji:** Czy wizualizacja ma być responsywna (dopasowywać się do szerokości okna)?
2. **Animacje:** Czy wizualizacja ma być animowana (np. przedziały pojawiają się z animacją)?
3. **Statystyki:** Czy po zakończeniu quizu pokazać podsumowanie wyników (procent poprawnych odpowiedzi)?
4. **Poziom ufności:** Czy pytania zawsze używają 95% CI, czy może też 90% lub 99%?
5. **Jednostki:** Czy w pytaniach używać różnych jednostek (zł, kg, cm, mmHg, %) dla różnorodności?
6. **Kategorie pytań:** Czy pytania mają być losowane równomiernie z różnych kategorii (łatwe/średnie/trudne)?
7. **Feedback rozszerzony:** Czy po odpowiedzi pokazać także "reguły ogólne" (np. "Zapamiętaj: wartość poza przedziałem → możemy wnioskować")?

---

## Podsumowanie

**Aplikacja:** Quiz z wizualizacją przedziałów ufności + feedback edukacyjny

**Korzyści:**
- Interaktywne uczenie się interpretacji CI
- Wizualizacja pomaga zrozumieć, dlaczego odpowiedź jest poprawna/błędna
- Różnorodność pytań (różne konteksty, wartości, szerokości przedziałów)
- Łatwe dodawanie nowych pytań przez edycję JSON

**Zgodność z wytycznymi:**
- Stack: PyWebView + Flask + HTML/CSS/JS (jak histogram, quiz_app)
- Struktura: Menu → Quiz → Feedback
- Build: PyInstaller → .exe (wszystko spakowane)
- Dane: JSON (łatwa edycja przez twórcę)

**Gotowość do implementacji:** TAK
- Plan szczegółowy ✓
- Przykładowe pytania ✓
- Format danych ✓
- Architektura techniczna ✓

**Następne kroki:**
1. Zatwierdzenie planu przez użytkownika
2. Przygotowanie pełnej bazy pytań (40 pytań)
3. Implementacja (fazy 1-6)
