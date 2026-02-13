# Zabawki Matematyczne

Ten katalog zawiera wszystkie interaktywne zabawki. Kazda zabawka to oddzielny folder z kompletna aplikacja.

## Struktura

Kazda zabawka powinna miec nastepujaca strukture:

```
toys/nazwa_zabawki/
├── app.py              # Flask backend (logika, obliczenia)
├── main.py             # PyWebView wrapper (uruchamia aplikacje)
├── README.md           # Opis zabawki
├── templates/
│   └── index.html      # UI (interfejs uzytkownika)
└── static/
    ├── style.css       # Style
    ├── script.js       # Logika JavaScript
    └── favicon.svg     # Ikona aplikacji
```

## Dostepne Zabawki

### Algebra liniowa
- [x] **linear_transforms** - Transformacje liniowe 2D: wizualizacja dzialania macierzy 2x2 na plaszczyznie (port 15005)
- [x] **matrix_calculator** - Kalkulator macierzy: wyznacznik, rzad, RREF, eliminacja Gaussa krok po kroku (port 15006)

### Analiza matematyczna
- [x] **taylor_series** - Szeregi Taylora: aproksymacja funkcji wielomianami z wizualizacja zbieznosci (port 15007)

### Przyszle Pomysly
- Calki Riemanna (wizualizacja sum Riemanna)
- Granice i ciaglosc (definicja epsilon-delta)
- Ciagi i szeregi liczbowe (zbieznosc)
- Przestrzenie wektorowe (wizualizacja podprzestrzeni)
- Uklady rownan liniowych (geometryczna interpretacja)

## Jak Dodac Nowa Zabawke

1. Przeczytaj [../docs/TWORZENIE_ZABAWKI.md](../docs/TWORZENIE_ZABAWKI.md)
2. Stworz nowy folder `toys/nazwa_zabawki/`
3. Uzyj struktury opisanej powyzej
4. Testuj lokalnie: `cd toys/nazwa_zabawki && python main.py`
5. Zbuduj .exe: `python build.py`
6. Dodaj do listy powyzej

## Zasady

- Kazda zabawka jest **niezalezna** - oddzielny .exe
- Dokumentuj co zabawka robi (README w folderze zabawki)
- Testuj przed budowaniem .exe
- Uzywaj sensownych domyslnych wartosci parametrow
