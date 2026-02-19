"""
Wykresy funkcji i pochodnych - interaktywna wizualizacja.

Backend Flask obliczający wartości funkcji i ich pochodnych
analitycznych, z dwoma trybami wyświetlania (oddzielne/wspólny wykres).
"""

from flask import Flask, render_template, jsonify, request
import numpy as np
import math
import os
import sys

from common.flask_app import register_common_static
from common.functions import (
    FUNCTION_REGISTRY, evaluate_function, evaluate_derivative,
    get_all_functions, resolve_params
)


def get_bundle_dir():
    """Zwraca ścieżkę do katalogu z plikami (dev vs .exe)"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(__file__)


bundle_dir = get_bundle_dir()
app = Flask(__name__,
            template_folder=os.path.join(bundle_dir, 'templates'),
            static_folder=os.path.join(bundle_dir, 'static'))

register_common_static(app, bundle_dir if getattr(sys, 'frozen', False) else None)

VALID_VIEW_MODES = ('separate', 'combined')
NUM_POINTS = 500


def safe_float(val):
    """Bezpieczna konwersja na float."""
    if val is None:
        return None
    try:
        f = float(val)
    except (ValueError, TypeError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def _compute_y_range(y_arr):
    """Oblicza zakres Y z paddingiem."""
    finite = y_arr[np.isfinite(y_arr)]
    if len(finite) == 0:
        return [-10, 10]
    y_min = float(np.min(finite))
    y_max = float(np.max(finite))
    pad = max(abs(y_max - y_min) * 0.15, 1)
    return [round(y_min - pad, 4), round(y_max + pad, 4)]


def _safe_y_list(y_arr):
    """Konwertuje numpy array na listę bezpieczną dla JSON."""
    return [
        None if (math.isnan(v) or math.isinf(v)) else round(float(v), 8)
        for v in y_arr
    ]


def _validate_request_json():
    """Waliduje że request zawiera poprawny JSON."""
    data = request.json
    if data is None:
        raise ValueError("Wymagane dane w formacie JSON")
    return data


@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')


@app.route('/api/functions')
def functions():
    """Zwraca listę dostępnych funkcji z parametrami."""
    return jsonify({'success': True, 'functions': get_all_functions()})


@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Oblicza wartości funkcji i pochodnej.

    Request JSON:
        func: string - identyfikator funkcji
        params: dict - parametry funkcji
        view_mode: string - 'separate' lub 'combined'
        x_min: float (opcjonalny) - początek zakresu
        x_max: float (opcjonalny) - koniec zakresu

    Response JSON:
        func_data: {x, y} - dane funkcji
        derivative_data: {x, y} - dane pochodnej
        func_formula: string - wzór funkcji
        derivative_formula: string - wzór pochodnej
        y_range_func: [min, max] - zakres Y funkcji
        y_range_deriv: [min, max] - zakres Y pochodnej
        y_range_combined: [min, max] - zakres Y wspólny
    """
    try:
        data = _validate_request_json()

        func_id = data.get('func', 'sin')
        if func_id not in FUNCTION_REGISTRY:
            raise ValueError(f"Nieznana funkcja: {func_id}")

        view_mode = data.get('view_mode', 'separate')
        if view_mode not in VALID_VIEW_MODES:
            raise ValueError(
                f"Nieprawidłowy tryb widoku: {view_mode}. "
                f"Dozwolone: {', '.join(VALID_VIEW_MODES)}"
            )

        raw_params = data.get('params', {})
        params = resolve_params(func_id, raw_params)

        func_info = FUNCTION_REGISTRY[func_id]

        # Zakres X
        x_min = data.get('x_min', func_info['default_range'][0])
        x_max = data.get('x_max', func_info['default_range'][1])
        x_min = float(x_min)
        x_max = float(x_max)

        if math.isnan(x_min) or math.isinf(x_min):
            raise ValueError("x_min musi być liczbą skończoną")
        if math.isnan(x_max) or math.isinf(x_max):
            raise ValueError("x_max musi być liczbą skończoną")
        if x_min >= x_max:
            raise ValueError("x_min musi być mniejszy od x_max")
        if x_max - x_min > 200:
            raise ValueError("Zakres X nie może przekraczać 200")

        x_arr = np.linspace(x_min, x_max, NUM_POINTS)

        # Oblicz funkcję i pochodną
        y_func = evaluate_function(func_id, x_arr, params)
        y_deriv = evaluate_derivative(func_id, x_arr, params)

        # Zakresy Y
        y_range_func = _compute_y_range(y_func)
        y_range_deriv = _compute_y_range(y_deriv)

        # Zakres wspólny
        all_y = np.concatenate([
            y_func[np.isfinite(y_func)],
            y_deriv[np.isfinite(y_deriv)]
        ])
        y_range_combined = _compute_y_range(all_y) if len(all_y) > 0 else [-10, 10]

        result = {
            'success': True,
            'view_mode': view_mode,
            'func_data': {
                'x': x_arr.tolist(),
                'y': _safe_y_list(y_func),
            },
            'derivative_data': {
                'x': x_arr.tolist(),
                'y': _safe_y_list(y_deriv),
            },
            'func_formula': func_info['formula'],
            'derivative_formula': func_info['derivative_formula'],
            'y_range_func': y_range_func,
            'y_range_deriv': y_range_deriv,
            'y_range_combined': y_range_combined,
        }

        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Nieoczekiwany błąd serwera'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5008)
