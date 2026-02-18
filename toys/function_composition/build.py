"""Build script for Funkcja złożona."""
import os
import sys
import PyInstaller.__main__

# Dodaj toys/ do path żeby importy common działały
current_dir = os.path.dirname(os.path.abspath(__file__))
toys_dir = os.path.dirname(current_dir)
if toys_dir not in sys.path:
    sys.path.insert(0, toys_dir)

from common.build_utils import add_data_arg

templates_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')
common_static = os.path.join(toys_dir, 'common', 'static')

PyInstaller.__main__.run([
    os.path.join(current_dir, 'main.py'),
    '--onefile',
    '--windowed',
    '--name=KompozycjaFunkcji',
    add_data_arg(templates_dir, 'templates'),
    add_data_arg(static_dir, 'static'),
    add_data_arg(common_static, os.path.join('common', 'static')),
    '--hidden-import=bottle',
    '--hidden-import=proxy_tools',
    '--clean',
    '--noconfirm',
])
