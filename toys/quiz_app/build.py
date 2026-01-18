import PyInstaller.__main__
import os
import sys

# Dodaj katalog nadrzędny do ścieżki, aby zaimportować common
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.build_utils import add_data_arg

def build_exe():
    """Buduj .exe dla aplikacji quizów"""

    # Sprawdź czy katalogi istnieją
    if not os.path.exists('templates'):
        raise FileNotFoundError("Katalog 'templates' nie istnieje!")
    if not os.path.exists('static'):
        raise FileNotFoundError("Katalog 'static' nie istnieje!")
    if not os.path.exists('questions'):
        raise FileNotFoundError("Katalog 'questions' nie istnieje!")
    if not os.path.exists('quiz_config.json'):
        raise FileNotFoundError("Plik 'quiz_config.json' nie istnieje!")

    print("Budowanie quiz_app.exe...")

    PyInstaller.__main__.run([
        'main.py',
        '--name=quiz_app',
        '--onefile',
        '--windowed',
        add_data_arg('templates', 'templates'),
        add_data_arg('static', 'static'),
        add_data_arg('questions', 'questions'),
        add_data_arg('quiz_config.json', '.'),
        '--hidden-import=bottle',
        '--hidden-import=proxy_tools',
        '--clean',
        '--noconfirm'
    ])

    print("\nBuild zakończony!")
    print("Plik .exe znajduje się w: dist/quiz_app.exe")

if __name__ == '__main__':
    build_exe()
