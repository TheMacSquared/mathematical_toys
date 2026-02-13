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

| Aplikacja | Co robi? | Pobierz |
|-----------|----------|---------|
| **Transformacje Liniowe 2D** | Wizualizacja jak macierz 2x2 przeksztalca plaszczyzne - obrot, odbicie, scinanie, projekcja | [Pobierz](../../releases) |
| **Kalkulator Macierzy** | Wyznacznik, rzad, RREF, macierz odwrotna, wartosci wlasne, eliminacja Gaussa krok po kroku | [Pobierz](../../releases) |
| **Szeregi Taylora** | Aproksymacja funkcji wielomianami Taylora z wizualizacja zbieznosci | [Pobierz](../../releases) |

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

## Dla Mac/Linux

Obecnie aplikacje sa dostepne tylko dla Windows. Uzytownicy Mac/Linux moga uruchomic aplikacje z kodu zrodlowego:

```bash
cd toys/nazwa_zabawki
pip install -r requirements.txt
python main.py
```

## Licencja

Projekt na licencji [CC BY 4.0](LICENSE) - mozesz swobodnie uzywac i udostepniac, pod warunkiem podania autorstwa.
