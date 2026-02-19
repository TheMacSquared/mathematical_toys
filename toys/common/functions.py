"""
Wspolna biblioteka funkcji matematycznych z pochodnymi analitycznymi.

Uzywana przez function_derivatives i tangent_line.
Kazda funkcja ma konfigurowalne parametry, analityczna pochodna,
informacje o dziedzinie i zakresie domyslnym.
"""

import numpy as np
import math


FUNCTION_REGISTRY = {
    'linear': {
        'name': 'Liniowa: ax + b',
        'formula': 'f(x) = ax + b',
        'derivative_formula': "f'(x) = a",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-10, 10],
    },
    'quadratic': {
        'name': 'Kwadratowa: ax\u00b2 + bx + c',
        'formula': 'f(x) = ax\u00b2 + bx + c',
        'derivative_formula': "f'(x) = 2ax + b",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-5, 5],
    },
    'cubic': {
        'name': 'Szescienne: ax\u00b3 + bx\u00b2 + cx + d',
        'formula': 'f(x) = ax\u00b3 + bx\u00b2 + cx + d',
        'derivative_formula': "f'(x) = 3ax\u00b2 + 2bx + c",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'd', 'label': 'd', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-5, 5],
    },
    'sin': {
        'name': 'Sinus: a\u00b7sin(bx + c)',
        'formula': 'f(x) = a\u00b7sin(bx + c)',
        'derivative_formula': "f'(x) = ab\u00b7cos(bx + c)",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-2 * math.pi, 2 * math.pi],
    },
    'cos': {
        'name': 'Cosinus: a\u00b7cos(bx + c)',
        'formula': 'f(x) = a\u00b7cos(bx + c)',
        'derivative_formula': "f'(x) = -ab\u00b7sin(bx + c)",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-2 * math.pi, 2 * math.pi],
    },
    'exp': {
        'name': 'Eksponenta: a\u00b7e^(bx)',
        'formula': 'f(x) = a\u00b7e^(bx)',
        'derivative_formula': "f'(x) = ab\u00b7e^(bx)",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-4, 4],
    },
    'ln': {
        'name': 'Logarytm: a\u00b7ln(bx + c)',
        'formula': 'f(x) = a\u00b7ln(bx + c)',
        'derivative_formula': "f'(x) = ab/(bx + c)",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-5, 10],
    },
    'power': {
        'name': 'Potegowa: a\u00b7x^n',
        'formula': 'f(x) = a\u00b7x^n',
        'derivative_formula': "f'(x) = a\u00b7n\u00b7x^(n-1)",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'n', 'label': 'n', 'default': 2, 'min': -10, 'max': 10, 'step': 0.5},
        ],
        'default_range': [-5, 5],
    },
    'sqrt': {
        'name': 'Pierwiastek: a\u00b7\u221a(bx + c)',
        'formula': 'f(x) = a\u00b7\u221a(bx + c)',
        'derivative_formula': "f'(x) = ab/(2\u221a(bx + c))",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-1, 10],
    },
    'tan': {
        'name': 'Tangens: a\u00b7tan(bx + c)',
        'formula': 'f(x) = a\u00b7tan(bx + c)',
        'derivative_formula': "f'(x) = ab/cos\u00b2(bx + c)",
        'params': [
            {'id': 'a', 'label': 'a', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'b', 'label': 'b', 'default': 1, 'min': -10, 'max': 10, 'step': 0.1},
            {'id': 'c', 'label': 'c', 'default': 0, 'min': -10, 'max': 10, 'step': 0.1},
        ],
        'default_range': [-2 * math.pi, 2 * math.pi],
    },
}


def resolve_params(func_id, raw_params):
    """
    Laczy podane parametry z domyslnymi dla danej funkcji.

    Args:
        func_id: klucz z FUNCTION_REGISTRY
        raw_params: dict z wartosciami parametrow (moze byc niepelny)

    Returns:
        dict z kompletnymi parametrami

    Raises:
        ValueError: jesli func_id nie istnieje lub parametr poza zakresem
    """
    if func_id not in FUNCTION_REGISTRY:
        raise ValueError(f"Nieznana funkcja: {func_id}")

    func_def = FUNCTION_REGISTRY[func_id]
    if raw_params is None:
        raw_params = {}

    result = {}
    for p in func_def['params']:
        pid = p['id']
        if pid in raw_params:
            val = float(raw_params[pid])
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"Parametr {pid} musi byc liczba skonczona")
            if val < p['min'] or val > p['max']:
                raise ValueError(
                    f"Parametr {pid} musi byc z zakresu [{p['min']}, {p['max']}]"
                )
            result[pid] = val
        else:
            result[pid] = p['default']

    return result


def evaluate_function(func_id, x_arr, params):
    """
    Oblicza wartosci funkcji z zadanymi parametrami.

    Args:
        func_id: klucz z FUNCTION_REGISTRY
        x_arr: numpy array wartosci x
        params: dict parametrow (wynik resolve_params)

    Returns:
        numpy array wartosci y (NaN poza dziedzina)
    """
    with np.errstate(all='ignore'):
        if func_id == 'linear':
            return params['a'] * x_arr + params['b']

        elif func_id == 'quadratic':
            a, b, c = params['a'], params['b'], params['c']
            return a * x_arr**2 + b * x_arr + c

        elif func_id == 'cubic':
            a, b, c, d = params['a'], params['b'], params['c'], params['d']
            return a * x_arr**3 + b * x_arr**2 + c * x_arr + d

        elif func_id == 'sin':
            return params['a'] * np.sin(params['b'] * x_arr + params['c'])

        elif func_id == 'cos':
            return params['a'] * np.cos(params['b'] * x_arr + params['c'])

        elif func_id == 'exp':
            result = params['a'] * np.exp(params['b'] * x_arr)
            result = np.where(np.isinf(result), np.nan, result)
            return result

        elif func_id == 'ln':
            inner = params['b'] * x_arr + params['c']
            result = np.full_like(x_arr, np.nan, dtype=float)
            mask = inner > 0
            result[mask] = params['a'] * np.log(inner[mask])
            return result

        elif func_id == 'power':
            a, n = params['a'], params['n']
            n_is_int = (n == int(n))
            if n_is_int:
                return a * x_arr ** n
            else:
                # Ulamkowy wykladnik - dziedzina x >= 0
                result = np.full_like(x_arr, np.nan, dtype=float)
                mask = x_arr >= 0
                result[mask] = a * x_arr[mask] ** n
                return result

        elif func_id == 'sqrt':
            inner = params['b'] * x_arr + params['c']
            result = np.full_like(x_arr, np.nan, dtype=float)
            mask = inner >= 0
            result[mask] = params['a'] * np.sqrt(inner[mask])
            return result

        elif func_id == 'tan':
            arg = params['b'] * x_arr + params['c']
            cos_val = np.cos(arg)
            result = params['a'] * np.tan(arg)
            # Maskuj asymptoty
            result = np.where(np.abs(cos_val) < 0.01, np.nan, result)
            return result

    raise ValueError(f"Nieznana funkcja: {func_id}")


def evaluate_derivative(func_id, x_arr, params):
    """
    Oblicza wartosci pochodnej analitycznej z zadanymi parametrami.

    Args:
        func_id: klucz z FUNCTION_REGISTRY
        x_arr: numpy array wartosci x
        params: dict parametrow (wynik resolve_params)

    Returns:
        numpy array wartosci f'(x) (NaN poza dziedzina)
    """
    with np.errstate(all='ignore'):
        if func_id == 'linear':
            return np.full_like(x_arr, params['a'], dtype=float)

        elif func_id == 'quadratic':
            return 2 * params['a'] * x_arr + params['b']

        elif func_id == 'cubic':
            a, b, c = params['a'], params['b'], params['c']
            return 3 * a * x_arr**2 + 2 * b * x_arr + c

        elif func_id == 'sin':
            a, b, c = params['a'], params['b'], params['c']
            return a * b * np.cos(b * x_arr + c)

        elif func_id == 'cos':
            a, b, c = params['a'], params['b'], params['c']
            return -a * b * np.sin(b * x_arr + c)

        elif func_id == 'exp':
            result = params['a'] * params['b'] * np.exp(params['b'] * x_arr)
            result = np.where(np.isinf(result), np.nan, result)
            return result

        elif func_id == 'ln':
            inner = params['b'] * x_arr + params['c']
            result = np.full_like(x_arr, np.nan, dtype=float)
            mask = inner > 0
            result[mask] = params['a'] * params['b'] / inner[mask]
            return result

        elif func_id == 'power':
            a, n = params['a'], params['n']
            n_is_int = (n == int(n))
            if n_is_int and n >= 1:
                return a * n * x_arr ** (n - 1)
            elif n_is_int and n == 0:
                return np.zeros_like(x_arr)
            else:
                # Ulamkowy wykladnik lub ujemny calkowity
                result = np.full_like(x_arr, np.nan, dtype=float)
                if n < 0:
                    # Pochodna istnieje dla x != 0
                    mask = x_arr != 0
                else:
                    mask = x_arr >= 0
                result[mask] = a * n * x_arr[mask] ** (n - 1)
                result = np.where(np.isinf(result), np.nan, result)
                return result

        elif func_id == 'sqrt':
            inner = params['b'] * x_arr + params['c']
            result = np.full_like(x_arr, np.nan, dtype=float)
            mask = inner > 0  # Pochodna nie istnieje w punkcie granicznym
            result[mask] = (params['a'] * params['b']) / (2 * np.sqrt(inner[mask]))
            return result

        elif func_id == 'tan':
            a, b, c = params['a'], params['b'], params['c']
            arg = b * x_arr + c
            cos_val = np.cos(arg)
            result = a * b / (cos_val ** 2)
            result = np.where(np.abs(cos_val) < 0.01, np.nan, result)
            return result

    raise ValueError(f"Nieznana funkcja: {func_id}")


def get_all_functions():
    """
    Zwraca metadane wszystkich dostepnych funkcji.

    Returns:
        dict z informacjami o funkcjach (bez logiki obliczeniowej)
    """
    result = {}
    for key, info in FUNCTION_REGISTRY.items():
        result[key] = {
            'name': info['name'],
            'formula': info['formula'],
            'derivative_formula': info['derivative_formula'],
            'params': info['params'],
            'default_range': info['default_range'],
        }
    return result
