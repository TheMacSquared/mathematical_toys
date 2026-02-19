"""
Prosta styczna - interaktywna wizualizacja.

Backend Flask obliczajacy styczna do wykresu funkcji
w zadanym punkcie, z wykorzystaniem pochodnej analitycznej.
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
    """Zwraca sciezke do katalogu z plikami (dev vs .exe)"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(__file__)


bundle_dir = get_bundle_dir()
app = Flask(__name__,
            template_folder=os.path.join(bundle_dir, 'templates'),
            static_folder=os.path.join(bundle_dir, 'static'))

register_common_static(app, bundle_dir if getattr(sys, 'frozen', False) else None)

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
    """Konwertuje numpy array na liste bezpieczna dla JSON."""
    return [
        None if (math.isnan(v) or math.isinf(v)) else round(float(v), 8)
        for v in y_arr
    ]


def _format_tangent_equation(slope, y0, x0):
    """Formatuje rownanie stycznej jako string."""
    intercept = y0 - slope * x0

    if abs(slope) < 1e-10:
        return f"y = {y0:.4g}"

    # y = slope * x + intercept
    slope_str = f"{slope:.4g}"
    if abs(slope - 1) < 1e-10:
        slope_str = ""
    elif abs(slope + 1) < 1e-10:
        slope_str = "-"

    if abs(intercept) < 1e-10:
        return f"y = {slope_str}x"
    elif intercept > 0:
        return f"y = {slope_str}x + {intercept:.4g}"
    else:
        return f"y = {slope_str}x - {abs(intercept):.4g}"


def _validate_request_json():
    """Waliduje ze request zawiera poprawny JSON."""
    data = request.json
    if data is None:
        raise ValueError("Wymagane dane w formacie JSON")
    return data


@app.route('/')
def index():
    """Strona glowna"""
    return render_template('index.html')


@app.route('/api/functions')
def functions():
    """Zwraca liste dostepnych funkcji z parametrami."""
    return jsonify({'success': True, 'functions': get_all_functions()})


@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Oblicza styczna do wykresu funkcji w punkcie.

    Request JSON:
        func: string - identyfikator funkcji
        params: dict - parametry funkcji
        x0: float - punkt stycznosci
        x_min: float (opcjonalny) - poczatek zakresu
        x_max: float (opcjonalny) - koniec zakresu

    Response JSON:
        func_data: {x, y} - dane funkcji
        tangent_data: {x, y} - dane stycznej
        tangent_point: {x, y} - punkt stycznosci
        slope: float - nachylenie stycznej
        func_value_at_x0: float - f(x0)
        derivative_at_x0: float - f'(x0)
        tangent_equation: string - rownanie stycznej
        y_range: [min, max] - zakres Y
    """
    try:
        data = _validate_request_json()

        func_id = data.get('func', 'quadratic')
        if func_id not in FUNCTION_REGISTRY:
            raise ValueError(f"Nieznana funkcja: {func_id}")

        raw_params = data.get('params', {})
        params = resolve_params(func_id, raw_params)

        x0 = data.get('x0', 0)
        if x0 is None:
            raise ValueError("Wymagany punkt stycznosci x0")
        x0 = float(x0)
        if math.isnan(x0) or math.isinf(x0):
            raise ValueError("x0 musi byc liczba skonczona")

        func_info = FUNCTION_REGISTRY[func_id]

        # Zakres X
        x_min = data.get('x_min', func_info['default_range'][0])
        x_max = data.get('x_max', func_info['default_range'][1])
        x_min = float(x_min)
        x_max = float(x_max)

        if math.isnan(x_min) or math.isinf(x_min):
            raise ValueError("x_min musi byc liczba skonczona")
        if math.isnan(x_max) or math.isinf(x_max):
            raise ValueError("x_max musi byc liczba skonczona")
        if x_min >= x_max:
            raise ValueError("x_min musi byc mniejszy od x_max")
        if x_max - x_min > 200:
            raise ValueError("Zakres X nie moze przekraczac 200")

        # Oblicz f(x0) i f'(x0)
        x0_arr = np.array([x0], dtype=float)
        y0 = float(evaluate_function(func_id, x0_arr, params)[0])
        slope = float(evaluate_derivative(func_id, x0_arr, params)[0])

        if math.isnan(y0) or math.isinf(y0):
            raise ValueError(
                f"Funkcja nie jest zdefiniowana w punkcie x = {x0}"
            )
        if math.isnan(slope) or math.isinf(slope):
            raise ValueError(
                f"Pochodna nie istnieje w punkcie x = {x0}"
            )

        # Dane wykresu
        x_arr = np.linspace(x_min, x_max, NUM_POINTS)
        y_func = evaluate_function(func_id, x_arr, params)

        # Styczna: y = slope * (x - x0) + y0
        y_tangent = slope * (x_arr - x0) + y0

        # Zakres Y na podstawie funkcji i stycznej
        all_y = np.concatenate([
            y_func[np.isfinite(y_func)],
            y_tangent[np.isfinite(y_tangent)]
        ])
        y_range = _compute_y_range(all_y) if len(all_y) > 0 else [-10, 10]

        # Ogranicz styczna do rozsadnego zakresu
        y_tangent_clipped = np.clip(y_tangent, y_range[0], y_range[1])

        tangent_equation = _format_tangent_equation(slope, y0, x0)

        result = {
            'success': True,
            'func_data': {
                'x': x_arr.tolist(),
                'y': _safe_y_list(y_func),
            },
            'tangent_data': {
                'x': x_arr.tolist(),
                'y': _safe_y_list(y_tangent_clipped),
            },
            'tangent_point': {
                'x': round(x0, 8),
                'y': round(y0, 8),
            },
            'slope': round(slope, 8),
            'func_value_at_x0': round(y0, 8),
            'derivative_at_x0': round(slope, 8),
            'tangent_equation': tangent_equation,
            'y_range': y_range,
        }

        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Nieoczekiwany blad serwera'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5009)
