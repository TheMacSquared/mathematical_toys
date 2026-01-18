"""
Wspólne funkcje Flask dla zabawek statystycznych.

UWAGA: get_bundle_dir() powinno pozostać w każdym app.py osobno,
ponieważ przy PyInstaller bundle ścieżki są specyficzne dla aplikacji.

Użycie:
    from common.flask_app import load_json
"""
import os
import json


def load_json(filename, base_dir):
    """
    Wczytuje plik JSON.

    Args:
        filename: Nazwa pliku JSON (względna do base_dir)
        base_dir: Katalog bazowy (wynik get_bundle_dir())

    Returns:
        dict: Zawartość pliku JSON
    """
    json_path = os.path.join(base_dir, filename)

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
