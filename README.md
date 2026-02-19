# Matematyczne Zabawki

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Interaktywne aplikacje do nauki algebry liniowej i analizy matematycznej. Pobierz, uruchom i ucz sie przez eksploracje - bez instalacji dodatkowego oprogramowania!

## Co to jest?

**Matematyczne Zabawki** to zestaw prostych aplikacji edukacyjnych dla studentow pierwszego roku. Kazda aplikacja to jeden plik `.exe`, ktory:

- Dziala offline - nie wymaga internetu
- Nie wymaga instalacji - pobierasz i uruchamiasz
- Jest interaktywna - suwaki, przyciski, wykresy na zywo
- Pomaga zrozumiec matematyke przez zabawe

## Dostepne aplikacje

### Algebra liniowa

| Aplikacja | Co robi? | Pobierz |
|-----------|----------|---------|
| **Transformacje Liniowe 2D** | Wizualizacja jak macierz 2x2 przeksztalca plaszczyzne - obrot, odbicie, scinanie, projekcja | [Pobierz](../../releases) |
| **Kalkulator Macierzy** | Wyznacznik, rzad, RREF, macierz odwrotna, wartosci wlasne, eliminacja Gaussa krok po kroku | [Pobierz](../../releases) |

### Analiza matematyczna

| Aplikacja | Co robi? | Pobierz |
|-----------|----------|---------|
| **Szeregi Taylora** | Aproksymacja funkcji wielomianami Taylora z wizualizacja zbieznosci | [Pobierz](../../releases) |
| **Funkcja zlozona** | Wizualizacja skladania funkcji f(g(x)) i g(f(x)) z lancuchem operacji | [Pobierz](../../releases) |
| **Pochodne funkcji** | Wykresy funkcji i ich pochodnych analitycznych z interaktywnymi parametrami | [Pobierz](../../releases) |
| **Prosta styczna** | Wizualizacja prostej stycznej do wykresu funkcji z rownaniem i nachyleniem | [Pobierz](../../releases) |

## Jak pobrac i uruchomic?

1. Kliknij **[Releases](../../releases)** (lub link "Pobierz" przy wybranej aplikacji)
2. Znajdz najnowsza wersje i pobierz plik `.exe`
3. Dwuklik na pobranym pliku - aplikacja sie uruchomi
4. Gotowe!

## Czy to bezpieczne?

**Tak, aplikacje sa bezpieczne.**

Przy pierwszym uruchomieniu Windows Defender lub SmartScreen moga wyswietlic ostrzezenie. To normalne i nie oznacza, ze aplikacja jest niebezpieczna.

**Dlaczego pojawia sie ostrzezenie?**

Windows wyswietla takie komunikaty dla aplikacji, ktore nie maja platnego certyfikatu cyfrowego (kosztuje kilkaset dolarow rocznie). To samo ostrzezenie zobaczysz przy wielu darmowych programach edukacyjnych i open-source.

**Co mozesz zrobic:**
- Kliknij "Wiecej informacji" -> "Uruchom mimo to"
- Caly kod zrodlowy jest dostepny publicznie w tym repozytorium - mozesz go przejrzec

## Dla deweloperow

### Uruchamianie z kodu zrodlowego (Mac/Linux/Windows)

```bash
pip install -r requirements.txt
cd toys/nazwa_zabawki
python main.py
```

### Struktura projektu

```
mathematical_toys/
├── toys/                          # Aplikacje interaktywne
│   ├── common/                    # Wspolny kod (CSS, funkcje, budowanie)
│   ├── linear_transforms/         # Transformacje liniowe 2D (port 15005)
│   ├── matrix_calculator/         # Kalkulator macierzy (port 15006)
│   ├── taylor_series/             # Szeregi Taylora (port 15007)
│   ├── function_composition/      # Funkcja zlozona (port 15008)
│   ├── function_derivatives/      # Pochodne funkcji (port 15008)
│   └── tangent_line/              # Prosta styczna (port 15009)
├── tests/                         # Testy (pytest)
├── docs/                          # Dokumentacja deweloperska
└── build/                         # Skrypty budowania .exe
```

### Testy

```bash
python -m pytest
```

### Budowanie .exe

```bash
cd toys/nazwa_zabawki
python build.py
```

Wiecej informacji: [docs/TWORZENIE_ZABAWKI.md](docs/TWORZENIE_ZABAWKI.md)

## Licencja

Projekt na licencji [CC BY 4.0](LICENSE) - mozesz swobodnie uzywac i udostepniac, pod warunkiem podania autorstwa.
