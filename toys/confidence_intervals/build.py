import PyInstaller.__main__
import os
import sys

# Dodaj katalog nadrzędny do ścieżki, aby zaimportować common
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.build_utils import add_data_arg

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
        add_data_arg('templates', 'templates'),
        add_data_arg('static', 'static'),
        add_data_arg('questions', 'questions'),
        add_data_arg('ci_config.json', '.'),
        '--hidden-import=bottle',
        '--hidden-import=proxy_tools',
        '--clean',
        '--noconfirm'
    ])

    print("\nBuild zakończony!")
    print("Plik .exe znajduje się w: dist/confidence_intervals.exe")

if __name__ == '__main__':
    build_exe()
