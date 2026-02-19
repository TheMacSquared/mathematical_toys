# Szybki Start - Windows PowerShell

Instrukcja uruchomienia aplikacji Matematyczne Zabawki na Windows.

## Pierwsze Uruchomienie

### 1. Otwórz PowerShell

Przejdź do katalogu projektu (tam gdzie masz README.md, toys/, docs/)

```powershell
cd D:\Uczelnia\toys
# (lub gdzie masz projekt)
```

### 2. Sprawdź Python

```powershell
python --version
```

Powinieneś zobaczyć `Python 3.10` lub nowszy.

**Nie masz Pythona?**
- Pobierz z [python.org](https://www.python.org/downloads/)
- Podczas instalacji ZAZNACZ "Add Python to PATH"

### 3. Stwórz Virtual Environment

```powershell
python -m venv venv
```

To stworzy folder `venv\` w katalogu projektu.

### 4. Aktywuj Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**Problem: "cannot be loaded because running scripts is disabled"?**

Uruchom PowerShell jako **Administrator** i wykonaj:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Potem zamknij PowerShell administratora, wróć do normalnego PowerShell i spróbuj znowu aktywacji.

Po aktywacji powinieneś zobaczyć `(venv)` na początku wiersza:

```
(venv) PS D:\Uczelnia\toys>
```

### 5. Zainstaluj Zależności

```powershell
pip install -r requirements.txt
```

To potrwa kilka minut. Instaluje Flask, PyWebView, NumPy, Matplotlib, PyInstaller.

### 6. Uruchom Aplikacje

Wybierz zabawke i uruchom ja:

```powershell
cd toys\linear_transforms
python main.py
```

Dostepne zabawki: `linear_transforms`, `matrix_calculator`, `taylor_series`, `function_composition`, `function_derivatives`, `tangent_line`.

## Kolejne Uruchomienia

Przy nastepnym razie wystarczy:

```powershell
# Z glownego katalogu projektu
.\venv\Scripts\Activate.ps1

cd toys\linear_transforms   # lub inna zabawka
python main.py
```

## Budowanie .exe (Opcjonalnie)

Aby stworzyc standalone `.exe` do dystrybucji:

```powershell
cd toys\linear_transforms
python build.py
```

Plik `.exe` bedzie w `toys\linear_transforms\dist\`.

Mozesz go skopiowac i wyslac komus - nie wymaga instalacji Pythona!

## Troubleshooting

### Problem 1: "python not found"

**Rozwiązanie**: Zainstaluj Python
- Pobierz z [python.org](https://www.python.org/downloads/)
- WAŻNE: Podczas instalacji zaznacz "Add Python to PATH"
- Po instalacji uruchom PowerShell ponownie

### Problem 2: "venv\Scripts\Activate.ps1 is not recognized"

**Rozwiązanie**: Jesteś w złym katalogu
```powershell
# Upewnij się że jesteś w głównym katalogu projektu
cd D:\Uczelnia\toys  # (lub gdzie masz projekt)
ls  # powinieneś zobaczyć README.md, venv\, toys\
```

### Problem 3: ExecutionPolicy

**Rozwiązanie**:
```powershell
# Uruchom PowerShell jako Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem 4: "No module named 'flask'"

**Rozwiazanie**: Aktywuj venv PRZED uruchomieniem
```powershell
.\venv\Scripts\Activate.ps1  # <- Pamietaj o tym!
cd toys\linear_transforms
python main.py
```

### Problem 5: PyWebView nie działa / czarny ekran

**Rozwiązanie**: Zainstaluj Microsoft Edge WebView2 Runtime
- Powinien być już w Windows 10/11
- Jeśli nie: [Pobierz WebView2](https://developer.microsoft.com/microsoft-edge/webview2/)

### Problem 6: Aplikacja nie otwiera się

**Testuj samego Flask (bez GUI)**:
```powershell
cd toys\linear_transforms
python app.py
```

Potem otworz http://localhost:5005 w przegladarce - aplikacja powinna dzialac.

## Dezaktywacja Virtual Environment

Gdy kończysz pracę:

```powershell
deactivate
```

## Struktura Plikow

Po setupie powinienes miec:

```
D:\Uczelnia\mathematical_toys\
├── venv\                          ← Virtual environment (nie commituj!)
├── toys\
│   ├── common\                    ← Wspolny kod
│   ├── linear_transforms\         ← Transformacje liniowe 2D
│   ├── matrix_calculator\         ← Kalkulator macierzy
│   ├── taylor_series\             ← Szeregi Taylora
│   ├── function_composition\      ← Funkcja zlozona
│   ├── function_derivatives\      ← Pochodne funkcji
│   └── tangent_line\              ← Prosta styczna
├── tests\                         ← Testy
├── README.md
└── requirements.txt
```

## Pomoc

- Dokumentacja tworzenia zabawek: `docs/TWORZENIE_ZABAWKI.md`
- Główne README: `README.md`
- GitHub Issues: (link do repo)

---

**Gotowe!** Aplikacja powinna działać. Eksperymentuj z parametrami i miłej zabawy! 📊
