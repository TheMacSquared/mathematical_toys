"""
Kompozycja funkcji - interaktywna wizualizacja f(g(x)).

Backend Flask obliczający złożenia funkcji i generujący
dane do wykresu porównującego f(g(x)), g(f(x)) oraz
typowe błędy studentów.
"""

from flask import Flask, render_template, jsonify, request
import numpy as np
import math
import os
import sys

from common.flask_app import register_common_static


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


# Dostępne funkcje - wspólna lista dla f (zewnętrzna) i g (wewnętrzna)
FUNCTIONS = {
    'shift': {
        'name': 't + a',
        'description': 'Przesunięcie o a',
        'has_param': True,
        'param_label': 'przesunięcie',
        'param_min': -5,
        'param_max': 5,
        'param_step': 0.5,
        'param_default': 3,
    },
    'scale': {
        'name': 'a \u00b7 t',
        'description': 'Skalowanie przez a',
        'has_param': True,
        'param_label': 'wspolczynnik',
        'param_min': -3,
        'param_max': 3,
        'param_step': 0.5,
        'param_default': 2,
    },
    'power': {
        'name': 't^a',
        'description': 'Potęga a (t >= 0 dla niecałkowitych)',
        'has_param': True,
        'param_label': 'wykładnik',
        'param_values': [-2, -1, 0.5, 1, 2, 3],
        'param_default': 2,
    },
    'sin': {
        'name': 'sin(a\u00b7t)',
        'description': 'Sinus z częstotliwością a',
        'has_param': True,
        'param_label': 'częstotliwość',
        'param_min': 0.1,
        'param_max': 5,
        'param_step': 0.1,
        'param_default': 1,
    },
    'cos': {
        'name': 'cos(a\u00b7t)',
        'description': 'Cosinus z częstotliwością a',
        'has_param': True,
        'param_label': 'częstotliwość',
        'param_min': 0.1,
        'param_max': 5,
        'param_step': 0.1,
        'param_default': 1,
    },
    'exp': {
        'name': 'e^(a\u00b7t)',
        'description': 'Eksponenta ze współczynnikiem a',
        'has_param': True,
        'param_label': 'współczynnik',
        'param_min': -2,
        'param_max': 2,
        'param_step': 0.1,
        'param_default': 1,
    },
    'abs': {
        'name': '|t|',
        'description': 'Wartość bezwzględna',
        'has_param': False,
        'param_default': None,
    },
    'ln': {
        'name': 'ln(t)',
        'description': 'Logarytm naturalny (t > 0)',
        'has_param': False,
        'param_default': None,
    },
}


def _evaluate_func(func_id, param, t_arr):
    """Oblicza wartości funkcji na tablicy numpy."""
    with np.errstate(all='ignore'):
        if func_id == 'shift':
            return t_arr + param
        elif func_id == 'scale':
            return param * t_arr
        elif func_id == 'power':
            if param == int(param) and int(param) % 2 != 0 and param >= -3:
                # Nieparzyste całkowite potęgi: działają dla ujemnych t
                sign = np.sign(t_arr)
                return sign * (np.abs(t_arr) ** param)
            elif param < 0:
                # Ujemna potęga: unikaj dzielenia przez zero
                result = np.full_like(t_arr, np.nan, dtype=float)
                mask = np.abs(t_arr) > 1e-10
                result[mask] = np.power(np.abs(t_arr[mask]), param)
                neg_mask = mask & (t_arr < 0) & (param == int(param))
                if int(param) % 2 != 0:
                    result[neg_mask] = -result[neg_mask]
                return result
            else:
                # Niecałkowita lub parzysta potęga: wymaga t >= 0
                result = np.full_like(t_arr, np.nan, dtype=float)
                mask = t_arr >= 0
                result[mask] = np.power(t_arr[mask], param)
                return result
        elif func_id == 'sin':
            return np.sin(param * t_arr)
        elif func_id == 'cos':
            return np.cos(param * t_arr)
        elif func_id == 'exp':
            result = np.exp(param * t_arr)
            # Ograniczenie wartości żeby wykres nie uciekał
            result = np.where(np.isfinite(result), result, np.nan)
            return result
        elif func_id == 'abs':
            return np.abs(t_arr)
        elif func_id == 'ln':
            result = np.full_like(t_arr, np.nan, dtype=float)
            mask = t_arr > 0
            result[mask] = np.log(t_arr[mask])
            return result
    raise ValueError(f"Nieznana funkcja: {func_id}")


def _evaluate_single(func_id, param, t):
    """Oblicza wartość funkcji w jednym punkcie."""
    arr = np.array([float(t)])
    result = _evaluate_func(func_id, param, arr)
    val = float(result[0])
    if math.isnan(val) or math.isinf(val):
        return None
    return val


def _make_label(func_id, param):
    """Generuje czytelną etykietę funkcji."""
    if func_id == 'shift':
        if param == 0:
            return 't'
        sign = '+' if param > 0 else '-'
        return f't {sign} {abs(param):g}'
    elif func_id == 'scale':
        if param == 1:
            return 't'
        if param == -1:
            return '-t'
        return f'{param:g}\u00b7t'
    elif func_id == 'power':
        if param == 0.5:
            return '\u221at'
        if param == -1:
            return '1/t'
        if param == -2:
            return '1/t\u00b2'
        if param == 1:
            return 't'
        if param == 2:
            return 't\u00b2'
        if param == 3:
            return 't\u00b3'
        return f't^{param:g}'
    elif func_id == 'sin':
        if param == 1:
            return 'sin(t)'
        return f'sin({param:g}\u00b7t)'
    elif func_id == 'cos':
        if param == 1:
            return 'cos(t)'
        return f'cos({param:g}\u00b7t)'
    elif func_id == 'exp':
        if param == 1:
            return 'e\u1d57'
        if param == -1:
            return 'e\u207b\u1d57'
        return f'e^({param:g}\u00b7t)'
    elif func_id == 'abs':
        return '|t|'
    elif func_id == 'ln':
        return 'ln(t)'
    return func_id


def _make_composition_label(f_id, f_param, g_id, g_param):
    """Generuje etykietę złożenia f(g(x))."""
    g_label = _make_label(g_id, g_param)
    # Zastap t przez x w etykiecie g
    g_of_x = g_label.replace('t', 'x')

    # Buduj f(g(x)) - zastap t w f przez wyrazenie g(x)
    if f_id == 'shift':
        if f_param == 0:
            return g_of_x
        sign = '+' if f_param > 0 else '-'
        return f'({g_of_x}) {sign} {abs(f_param):g}'
    elif f_id == 'scale':
        if f_param == 1:
            return g_of_x
        if f_param == -1:
            return f'-({g_of_x})'
        return f'{f_param:g}\u00b7({g_of_x})'
    elif f_id == 'power':
        if f_param == 0.5:
            return f'\u221a({g_of_x})'
        if f_param == 1:
            return g_of_x
        if f_param == 2:
            return f'({g_of_x})\u00b2'
        if f_param == 3:
            return f'({g_of_x})\u00b3'
        if f_param == -1:
            return f'1/({g_of_x})'
        if f_param == -2:
            return f'1/({g_of_x})\u00b2'
        return f'({g_of_x})^{f_param:g}'
    elif f_id == 'sin':
        if f_param == 1:
            return f'sin({g_of_x})'
        return f'sin({f_param:g}\u00b7({g_of_x}))'
    elif f_id == 'cos':
        if f_param == 1:
            return f'cos({g_of_x})'
        return f'cos({f_param:g}\u00b7({g_of_x}))'
    elif f_id == 'exp':
        if f_param == 1:
            return f'e^({g_of_x})'
        return f'e^({f_param:g}\u00b7({g_of_x}))'
    elif f_id == 'abs':
        return f'|{g_of_x}|'
    elif f_id == 'ln':
        return f'ln({g_of_x})'
    return f'f({g_of_x})'


def _format_detail(func_id, param, input_val, output_val):
    """Formatuje krok obliczeniowy pipeline."""
    if output_val is None:
        return 'niezdefiniowane'
    iv = f'{input_val:g}' if input_val is not None else '?'
    ov = f'{output_val:g}'

    if func_id == 'shift':
        return f'{iv} + {param:g} = {ov}'
    elif func_id == 'scale':
        return f'{param:g} \u00b7 {iv} = {ov}'
    elif func_id == 'power':
        if param == 2:
            return f'{iv}\u00b2 = {ov}'
        if param == 3:
            return f'{iv}\u00b3 = {ov}'
        if param == 0.5:
            return f'\u221a{iv} = {ov}'
        if param == -1:
            return f'1/{iv} = {ov}'
        return f'{iv}^{param:g} = {ov}'
    elif func_id == 'sin':
        if param == 1:
            return f'sin({iv}) = {ov}'
        return f'sin({param:g}\u00b7{iv}) = {ov}'
    elif func_id == 'cos':
        if param == 1:
            return f'cos({iv}) = {ov}'
        return f'cos({param:g}\u00b7{iv}) = {ov}'
    elif func_id == 'exp':
        if param == 1:
            return f'e^{iv} = {ov}'
        return f'e^({param:g}\u00b7{iv}) = {ov}'
    elif func_id == 'abs':
        return f'|{iv}| = {ov}'
    elif func_id == 'ln':
        return f'ln({iv}) = {ov}'
    return f'{ov}'


def _build_pipeline(f_id, f_param, g_id, g_param, x0):
    """Buduje opisy kroków pipeline dla f(g(x)) i g(f(x))."""
    g_x0 = _evaluate_single(g_id, g_param, x0)
    f_x0 = _evaluate_single(f_id, f_param, x0)

    f_g_x0 = _evaluate_single(f_id, f_param, g_x0) if g_x0 is not None else None
    g_f_x0 = _evaluate_single(g_id, g_param, f_x0) if f_x0 is not None else None

    g_label = _make_label(g_id, g_param)
    f_label = _make_label(f_id, f_param)

    pipeline_fg = [
        {'label': 'x\u2080', 'value': safe_float(x0), 'detail': None},
        {
            'label': f'g(x\u2080)',
            'value': safe_float(g_x0),
            'detail': _format_detail(g_id, g_param, x0, g_x0),
        },
        {
            'label': f'f(g(x\u2080))',
            'value': safe_float(f_g_x0),
            'detail': _format_detail(f_id, f_param, g_x0, f_g_x0) if g_x0 is not None else 'niezdefiniowane',
        },
    ]

    pipeline_gf = [
        {'label': 'x\u2080', 'value': safe_float(x0), 'detail': None},
        {
            'label': f'f(x\u2080)',
            'value': safe_float(f_x0),
            'detail': _format_detail(f_id, f_param, x0, f_x0),
        },
        {
            'label': f'g(f(x\u2080))',
            'value': safe_float(g_f_x0),
            'detail': _format_detail(g_id, g_param, f_x0, g_f_x0) if f_x0 is not None else 'niezdefiniowane',
        },
    ]

    return pipeline_fg, pipeline_gf


def _validate_request_json():
    """Waliduje że request zawiera poprawny JSON."""
    data = request.json
    if data is None:
        raise ValueError("Wymagane dane w formacie JSON")
    return data


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
    return round(f, 8)


@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')


@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Oblicza złożenie funkcji i dane do wykresu.

    Request JSON:
        f_id: string - identyfikator funkcji zewnętrznej
        f_param: float - parametr f (lub null)
        g_id: string - identyfikator funkcji wewnętrznej
        g_param: float - parametr g (lub null)
        x0: float - punkt ewaluacji łańcucha

    Response JSON:
        Krzywe g(x), f(x), f(g(x)), g(f(x)), ewaluacja w x0,
        pipeline steps, etykiety.
    """
    try:
        data = _validate_request_json()

        f_id = data.get('f_id', 'power')
        g_id = data.get('g_id', 'shift')
        if f_id not in FUNCTIONS:
            raise ValueError(f"Nieznana funkcja f: {f_id}")
        if g_id not in FUNCTIONS:
            raise ValueError(f"Nieznana funkcja g: {g_id}")

        f_info = FUNCTIONS[f_id]
        g_info = FUNCTIONS[g_id]

        # Parametry
        f_param = f_info['param_default']
        if f_info.get('has_param') and data.get('f_param') is not None:
            f_param = float(data['f_param'])
            if math.isnan(f_param) or math.isinf(f_param):
                raise ValueError("Parametr f musi być liczbą skończoną")

        g_param = g_info['param_default']
        if g_info.get('has_param') and data.get('g_param') is not None:
            g_param = float(data['g_param'])
            if math.isnan(g_param) or math.isinf(g_param):
                raise ValueError("Parametr g musi być liczbą skończoną")

        x0 = float(data.get('x0', 2.0))
        if math.isnan(x0) or math.isinf(x0):
            raise ValueError("x0 musi być liczbą skończoną")
        if abs(x0) > 100:
            raise ValueError("x0 musi być z zakresu [-100, 100]")

        # Zakres wykresu
        x_range = [-5, 5]
        x_arr = np.linspace(x_range[0], x_range[1], 500)

        # Krzywe
        g_y = _evaluate_func(g_id, g_param, x_arr)
        f_y = _evaluate_func(f_id, f_param, x_arr)
        fg_y = _evaluate_func(f_id, f_param, g_y)
        gf_y = _evaluate_func(g_id, g_param, f_y)

        # Ewaluacja w x0
        g_x0 = _evaluate_single(g_id, g_param, x0)
        f_x0 = _evaluate_single(f_id, f_param, x0)
        f_g_x0 = _evaluate_single(f_id, f_param, g_x0) if g_x0 is not None else None
        g_f_x0 = _evaluate_single(g_id, g_param, f_x0) if f_x0 is not None else None

        # Typowe bledy
        f_x0_plus_g_x0 = None
        f_x0_times_g_x0 = None
        if f_x0 is not None and g_x0 is not None:
            s = f_x0 + g_x0
            if not (math.isnan(s) or math.isinf(s)):
                f_x0_plus_g_x0 = round(s, 8)
            p = f_x0 * g_x0
            if not (math.isnan(p) or math.isinf(p)):
                f_x0_times_g_x0 = round(p, 8)

        # Pipeline
        pipeline_fg, pipeline_gf = _build_pipeline(
            f_id, f_param, g_id, g_param, x0
        )

        # Etykiety
        f_label = _make_label(f_id, f_param)
        g_label = _make_label(g_id, g_param)
        fg_label = _make_composition_label(f_id, f_param, g_id, g_param)
        gf_label = _make_composition_label(g_id, g_param, f_id, f_param)

        # Zakres Y - dynamiczny
        all_y = np.concatenate([g_y, f_y, fg_y, gf_y])
        finite_y = all_y[np.isfinite(all_y)]
        if len(finite_y) > 0:
            y_min = float(np.nanmin(finite_y))
            y_max = float(np.nanmax(finite_y))
        else:
            y_min, y_max = -10, 10
        y_pad = max((y_max - y_min) * 0.15, 2)
        # Ograniczenie zakresu żeby nie uciekał w nieskończoność
        y_display_min = max(y_min - y_pad, -50)
        y_display_max = min(y_max + y_pad, 50)

        # Konwersja do JSON-safe
        def to_json_list(arr):
            return [
                None if (math.isnan(float(v)) or math.isinf(float(v)))
                else round(float(v), 8)
                for v in arr
            ]

        result = {
            'success': True,
            'f_label': f_label,
            'g_label': g_label,
            'fg_label': fg_label,
            'gf_label': gf_label,

            'g_curve': {'x': x_arr.tolist(), 'y': to_json_list(g_y)},
            'f_curve': {'x': x_arr.tolist(), 'y': to_json_list(f_y)},
            'fg_curve': {'x': x_arr.tolist(), 'y': to_json_list(fg_y)},
            'gf_curve': {'x': x_arr.tolist(), 'y': to_json_list(gf_y)},

            'x0': safe_float(x0),
            'g_x0': safe_float(g_x0),
            'f_g_x0': safe_float(f_g_x0),
            'f_x0': safe_float(f_x0),
            'g_f_x0': safe_float(g_f_x0),
            'f_x0_plus_g_x0': f_x0_plus_g_x0,
            'f_x0_times_g_x0': f_x0_times_g_x0,

            'pipeline_fg': pipeline_fg,
            'pipeline_gf': pipeline_gf,

            'y_range': [round(y_display_min, 4), round(y_display_max, 4)],
        }

        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Nieoczekiwany błąd serwera'
        }), 500


@app.route('/api/functions')
def functions():
    """Zwraca listę dostępnych funkcji z metadanymi."""
    result = {}
    for key, info in FUNCTIONS.items():
        entry = {
            'name': info['name'],
            'description': info['description'],
            'has_param': info.get('has_param', False),
            'param_default': info.get('param_default'),
        }
        if info.get('has_param'):
            entry['param_label'] = info.get('param_label', 'a')
            if 'param_values' in info:
                entry['param_values'] = info['param_values']
            else:
                entry['param_min'] = info.get('param_min', -5)
                entry['param_max'] = info.get('param_max', 5)
                entry['param_step'] = info.get('param_step', 0.5)
        result[key] = entry
    return jsonify({'success': True, 'functions': result})


if __name__ == '__main__':
    app.run(debug=True, port=5008)
