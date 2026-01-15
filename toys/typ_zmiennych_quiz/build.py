import PyInstaller.__main__
import os

def build_exe():
    """Buduj .exe dla quizu"""

    # Sprawdź czy katalogi istnieją
    if not os.path.exists('templates'):
        raise FileNotFoundError("Katalog 'templates' nie istnieje!")
    if not os.path.exists('static'):
        raise FileNotFoundError("Katalog 'static' nie istnieje!")
    if not os.path.exists('questions.json'):
        raise FileNotFoundError("Plik 'questions.json' nie istnieje!")

    print("Budowanie typ_zmiennych_quiz.exe...")

    PyInstaller.__main__.run([
        'main.py',
        '--name=typ_zmiennych_quiz',
        '--onefile',
        '--windowed',
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--add-data=questions.json;.',  # Pakuj JSON w .exe
        '--hidden-import=bottle',
        '--hidden-import=proxy_tools',
        '--clean',
        '--noconfirm'
    ])

    print("\n✅ Build zakończony!")
    print("Plik .exe znajduje się w: dist/typ_zmiennych_quiz.exe")

if __name__ == '__main__':
    build_exe()
