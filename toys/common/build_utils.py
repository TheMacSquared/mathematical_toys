"""
Narzędzia do budowania .exe dla zabawek statystycznych.

Użycie:
    from common.build_utils import get_separator, add_data_arg
"""
import sys


def get_separator():
    """
    Zwraca separator dla PyInstaller --add-data.

    Windows używa ';', Linux/Mac używają ':'.

    Returns:
        str: ';' na Windows, ':' na innych systemach
    """
    return ';' if sys.platform == 'win32' else ':'


def add_data_arg(src, dst):
    """
    Generuje argument --add-data dla PyInstaller.

    Args:
        src: Ścieżka źródłowa (plik lub katalog)
        dst: Ścieżka docelowa w bundlu

    Returns:
        str: Argument w formacie '--add-data=src{sep}dst'

    Example:
        add_data_arg('templates', 'templates')
        # Na Windows: '--add-data=templates;templates'
        # Na Linux:   '--add-data=templates:templates'
    """
    sep = get_separator()
    return f'--add-data={src}{sep}{dst}'
