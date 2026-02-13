"""
Wspolne funkcje Flask dla zabawek matematycznych.

UWAGA: get_bundle_dir() powinno pozostac w kazdym app.py osobno,
poniewaz przy PyInstaller bundle sciezki sa specyficzne dla aplikacji.

Uzycie:
    from common.flask_app import load_json, register_common_static
"""
import os
import json
from flask import send_from_directory


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


def register_common_static(app, bundle_dir=None):
    """
    Rejestruje route /common/<filename> do serwowania wspólnych plików statycznych.

    W dev mode: serwuje z common/static/
    W PyInstaller bundle: serwuje z bundle_dir/common/static/

    Args:
        app: Instancja Flask
        bundle_dir: Opcjonalny katalog bazowy (dla PyInstaller)
    """
    if bundle_dir:
        common_dir = os.path.join(bundle_dir, 'common', 'static')
    else:
        common_dir = os.path.join(os.path.dirname(__file__), 'static')

    @app.route('/common/<path:filename>')
    def common_static(filename):
        return send_from_directory(common_dir, filename)
