"""
Skrypt do budowania pliku .exe dla zabawki Histogram.

Używa PyInstaller do zapakowania aplikacji jako standalone executable.
"""

import PyInstaller.__main__
import os
import sys

# Dodaj katalog nadrzędny do ścieżki, aby zaimportować common
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.build_utils import add_data_arg

def build():
    """Zbuduj plik .exe"""
    # Ścieżki
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')

    # Sprawdź czy katalogi istnieją
    if not os.path.exists(templates_dir):
        print(f"ERROR: Katalog templates/ nie istnieje: {templates_dir}")
        sys.exit(1)

    if not os.path.exists(static_dir):
        print(f"ERROR: Katalog static/ nie istnieje: {static_dir}")
        sys.exit(1)

    print("="*60)
    print("Budowanie Histogram.exe")
    print("="*60)
    print(f"Katalog: {current_dir}")
    print(f"Templates: {templates_dir}")
    print(f"Static: {static_dir}")
    print()

    args = [
        'main.py',
        '--onefile',              # Pojedynczy plik .exe
        '--windowed',             # Bez okna konsoli
        '--name=Histogram',       # Nazwa .exe
        add_data_arg(templates_dir, 'templates'),
        add_data_arg(static_dir, 'static'),
        '--clean',                # Wyczyść cache przed buildem
        '--noconfirm',            # Nie pytaj o potwierdzenie
        # Hidden imports (czasem potrzebne dla niektórych pakietów)
        '--hidden-import=bottle',
        '--hidden-import=proxy_tools',
    ]

    print("Uruchamianie PyInstaller...")
    print()

    try:
        PyInstaller.__main__.run(args)
        print()
        print("="*60)
        print("Build completed successfully!")
        print("="*60)
        print(f"EXE file: {os.path.join(current_dir, 'dist', 'Histogram.exe')}")
    except Exception as e:
        print()
        print("="*60)
        print("Build FAILED!")
        print("="*60)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build()
