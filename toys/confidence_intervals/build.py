import PyInstaller.__main__
import os

def build_exe():
    """Buduj .exe dla aplikacji przedziałów ufności"""

    # Sprawdź czy katalogi istnieją
    if not os.path.exists('templates'):
        raise FileNotFoundError("Katalog 'templates' nie istnieje!")
    if not os.path.exists('static'):
        raise FileNotFoundError("Katalog 'static' nie istnieje!")
    if not os.path.exists('questions'):
        raise FileNotFoundError("Katalog 'questions' nie istnieje!")
    if not os.path.exists('ci_config.json'):
        raise FileNotFoundError("Plik 'ci_config.json' nie istnieje!")

    print("Budowanie confidence_intervals.exe...")

    PyInstaller.__main__.run([
        'main.py',
        '--name=confidence_intervals',
        '--onefile',
        '--windowed',
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--add-data=questions;questions',  # Pakuj cały katalog questions
        '--add-data=ci_config.json;.',     # Pakuj konfigurację
        '--hidden-import=bottle',
        '--hidden-import=proxy_tools',
        '--clean',
        '--noconfirm'
    ])

    print("\n✅ Build zakończony!")
    print("Plik .exe znajduje się w: dist/confidence_intervals.exe")

if __name__ == '__main__':
    build_exe()
