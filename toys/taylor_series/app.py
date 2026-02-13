"""
Szeregi Taylora - interaktywna wizualizacja aproksymacji.

Backend Flask obliczajacy wielomiany Taylora dla wybranych
funkcji i porownujacy je z oryginalna funkcja.
"""

from flask import Flask, render_template, jsonify, request
import numpy as np
import math
import os
import sys

from common.flask_app import register_common_static


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


# Dostepne funkcje z ich pochodnymi wyznaczonymi analitycznie
FUNCTIONS = {
    'sin': {
        'name': 'sin(x)',
        'description': 'Sinus - klasyczny przyklad szeregu Taylora. Promien zbieznosci: nieskonczonosc.',
        'default_range': [-2 * math.pi, 2 * math.pi],
        'convergence_radius': None,  # None = nieskonczonosc
    },
    'cos': {
        'name': 'cos(x)',
        'description': 'Cosinus - podobny do sinusa, ale z parzystymi potegami. Promien zbieznosci: nieskonczonosc.',
        'default_range': [-2 * math.pi, 2 * math.pi],
        'convergence_radius': None,
    },
    'exp': {
        'name': 'e^x',
        'description': 'Eksponenta - jedyna funkcja rowna swojej pochodnej. Promien zbieznosci: nieskonczonosc.',
        'default_range': [-4, 4],
        'convergence_radius': None,
    },
    'ln1px': {
        'name': 'ln(1+x)',
        'description': 'Logarytm naturalny - zbiezny tylko dla |x| <= 1 (z wylaczeniem x = -1).',
        'default_range': [-1.5, 3],
        'convergence_radius': 1,
    },
    'atan': {
        'name': 'arctan(x)',
        'description': 'Arcus tangens - zbiezny dla |x| <= 1. Wzor Leibniza: arctan(1) = pi/4.',
        'default_range': [-3, 3],
        'convergence_radius': 1,
    },
    'one_over_1mx': {
        'name': '1/(1-x)',
        'description': 'Szereg geometryczny - najprostszy szereg potegowy. Zbiezny dla |x| < 1.',
        'default_range': [-2, 2],
        'convergence_radius': 1,
    },
    'sinh': {
        'name': 'sinh(x)',
        'description': 'Sinus hiperboliczny. Promien zbieznosci: nieskonczonosc.',
        'default_range': [-4, 4],
        'convergence_radius': None,
    },
    'sqrt1px': {
        'name': '\u221a(1+x)',
        'description': 'Pierwiastek - przyklad rozszerzenia dwumianowego. Zbiezny dla |x| <= 1.',
        'default_range': [-1.5, 3],
        'convergence_radius': 1,
    },
}


def _evaluate_function(func_id, x_arr):
    """Oblicza wartosci wybranej funkcji."""
    with np.errstate(all='ignore'):
        if func_id == 'sin':
            return np.sin(x_arr)
        elif func_id == 'cos':
            return np.cos(x_arr)
        elif func_id == 'exp':
            return np.exp(x_arr)
        elif func_id == 'ln1px':
            result = np.full_like(x_arr, np.nan)
            mask = x_arr > -1
            result[mask] = np.log(1 + x_arr[mask])
            return result
        elif func_id == 'atan':
            return np.arctan(x_arr)
        elif func_id == 'one_over_1mx':
            result = np.full_like(x_arr, np.nan)
            mask = np.abs(x_arr - 1) > 1e-10
            result[mask] = 1.0 / (1.0 - x_arr[mask])
            return result
        elif func_id == 'sinh':
            return np.sinh(x_arr)
        elif func_id == 'sqrt1px':
            result = np.full_like(x_arr, np.nan)
            mask = x_arr >= -1
            result[mask] = np.sqrt(1 + x_arr[mask])
            return result
    raise ValueError(f"Nieznana funkcja: {func_id}")


def _taylor_coefficients(func_id, a, degree):
    """
    Oblicza wspolczynniki szeregu Taylora wokol punktu a.

    Uzywa numerycznego rozniczkowania (finite differences)
    lub wzory analityczne dla a=0.
    """
    coeffs = []
    if a == 0:
        # Wzory analityczne dla rozwiniecia w 0 (Maclaurin)
        coeffs = _maclaurin_coefficients(func_id, degree)
    else:
        # Numeryczne rozniczkowanie
        coeffs = _numerical_taylor_coeffs(func_id, a, degree)
    return coeffs


def _maclaurin_coefficients(func_id, degree):
    """Wzory analityczne wspolczynnikow Maclaurina (a=0)."""
    coeffs = [0.0] * (degree + 1)

    if func_id == 'sin':
        for n in range(degree + 1):
            if n % 2 == 1:
                k = (n - 1) // 2
                coeffs[n] = ((-1) ** k) / math.factorial(n)

    elif func_id == 'cos':
        for n in range(degree + 1):
            if n % 2 == 0:
                k = n // 2
                coeffs[n] = ((-1) ** k) / math.factorial(n)

    elif func_id == 'exp':
        for n in range(degree + 1):
            coeffs[n] = 1.0 / math.factorial(n)

    elif func_id == 'ln1px':
        coeffs[0] = 0.0
        for n in range(1, degree + 1):
            coeffs[n] = ((-1) ** (n + 1)) / n

    elif func_id == 'atan':
        for n in range(degree + 1):
            if n % 2 == 1:
                k = (n - 1) // 2
                coeffs[n] = ((-1) ** k) / n

    elif func_id == 'one_over_1mx':
        for n in range(degree + 1):
            coeffs[n] = 1.0

    elif func_id == 'sinh':
        for n in range(degree + 1):
            if n % 2 == 1:
                k = (n - 1) // 2
                coeffs[n] = 1.0 / math.factorial(n)

    elif func_id == 'sqrt1px':
        coeffs[0] = 1.0
        for n in range(1, degree + 1):
            # Wzor dwumianowy: C(1/2, n) = (1/2)(1/2-1)...(1/2-n+1) / n!
            c = 1.0
            for k in range(n):
                c *= (0.5 - k)
            c /= math.factorial(n)
            coeffs[n] = c

    return coeffs


def _numerical_taylor_coeffs(func_id, a, degree):
    """Numeryczne obliczanie wspolczynnikow Taylora."""
    h = 1e-5
    coeffs = []

    # Oblicz pochodne numerycznie uzywajac finite differences
    for n in range(degree + 1):
        # n-ta pochodna w punkcie a
        deriv = _nth_derivative_numerical(func_id, a, n, h)
        coeffs.append(deriv / math.factorial(n))

    return coeffs


def _nth_derivative_numerical(func_id, a, n, h):
    """Oblicza n-ta pochodna numerycznie."""
    if n == 0:
        x = np.array([a], dtype=float)
        return float(_evaluate_function(func_id, x)[0])

    # Centralne roznice skonczony
    result = 0.0
    for k in range(n + 1):
        sign = (-1) ** (n - k)
        binom = math.comb(n, k)
        x = np.array([a + (k - n / 2) * h], dtype=float)
        val = _evaluate_function(func_id, x)[0]
        if np.isnan(val) or np.isinf(val):
            return 0.0
        result += sign * binom * val

    return result / (h ** n)


def _evaluate_taylor(coeffs, a, x_arr):
    """Oblicza wartosc wielomianu Taylora."""
    result = np.zeros_like(x_arr)
    for n, c in enumerate(coeffs):
        result += c * ((x_arr - a) ** n)
    return result


def _format_polynomial(coeffs, a):
    """Formatuje wielomian Taylora jako string."""
    terms = []
    for n, c in enumerate(coeffs):
        if abs(c) < 1e-15:
            continue
        if n == 0:
            terms.append(f"{c:.6g}")
        elif n == 1:
            if a == 0:
                terms.append(f"{c:.6g}\u00b7x")
            else:
                terms.append(f"{c:.6g}\u00b7(x - {a})")
        else:
            if a == 0:
                terms.append(f"{c:.6g}\u00b7x\u00b2" if n == 2 else f"{c:.6g}\u00b7x^{n}")
            else:
                terms.append(f"{c:.6g}\u00b7(x - {a})^{n}")

    if not terms:
        return "0"
    return " + ".join(terms).replace("+ -", "- ")


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


@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Oblicza wielomian Taylora i dane do wykresu.

    Request JSON:
        func: string - identyfikator funkcji
        degree: int - stopien wielomianu (0-20)
        center: float - punkt rozwiniecia a

    Response JSON:
        func_data: {x, y} - dane oryginalnej funkcji
        taylor_data: {x, y} - dane wielomianu Taylora
        coefficients: list - wspolczynniki
        polynomial: string - wielomian jako tekst
        error_at_point: float - blad w wybranym punkcie
    """
    try:
        data = _validate_request_json()

        func_id = data.get('func', 'sin')
        if func_id not in FUNCTIONS:
            raise ValueError(f"Nieznana funkcja: {func_id}")

        degree = int(data.get('degree', 5))
        if degree < 0 or degree > 20:
            raise ValueError("Stopien wielomianu musi byc miedzy 0 a 20")

        center = float(data.get('center', 0))
        if math.isnan(center) or math.isinf(center):
            raise ValueError("Punkt rozwiniecia musi byc liczba skonczona")
        if abs(center) > 20:
            raise ValueError("Punkt rozwiniecia musi byc z zakresu [-20, 20]")

        eval_point = data.get('eval_point', None)
        if eval_point is not None:
            eval_point = float(eval_point)
            if math.isnan(eval_point) or math.isinf(eval_point):
                eval_point = None

        func_info = FUNCTIONS[func_id]

        # Zakres wykresu
        x_range = func_info['default_range']
        # Przesun zakres jesli centrum nie jest w srodku
        if center != 0:
            half_range = (x_range[1] - x_range[0]) / 2
            x_range = [center - half_range, center + half_range]

        x_arr = np.linspace(x_range[0], x_range[1], 500)

        # Oryginalna funkcja
        y_func = _evaluate_function(func_id, x_arr)

        # Wspolczynniki Taylora
        coeffs = _taylor_coefficients(func_id, center, degree)

        # Wielomian Taylora
        y_taylor = _evaluate_taylor(coeffs, center, x_arr)

        # Ogranicz wartosci Taylora do rozsadnego zakresu
        y_func_clean = np.where(np.isnan(y_func) | np.isinf(y_func), None, y_func)
        y_min = np.nanmin(y_func[np.isfinite(y_func)]) if np.any(np.isfinite(y_func)) else -10
        y_max = np.nanmax(y_func[np.isfinite(y_func)]) if np.any(np.isfinite(y_func)) else 10
        y_pad = max(abs(y_max - y_min) * 2, 5)

        # Ograniczenie zakresu Y zeby Taylor nie uciekal w nieskonczonosc
        display_min = y_min - y_pad
        display_max = y_max + y_pad

        y_taylor_display = np.clip(y_taylor, display_min, display_max)

        # Blad w wybranym punkcie
        error_at_point = None
        if eval_point is not None:
            ep_arr = np.array([eval_point])
            f_val = float(_evaluate_function(func_id, ep_arr)[0])
            t_val = float(_evaluate_taylor(coeffs, center, ep_arr)[0])
            if not (math.isnan(f_val) or math.isinf(f_val)):
                error_at_point = abs(f_val - t_val)

        # Formatuj wielomian
        polynomial_str = _format_polynomial(coeffs, center)

        # Przygotuj dane bezpieczne do JSON
        func_x = x_arr.tolist()
        func_y = [None if (v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))) else round(float(v), 8) for v in y_func_clean]
        taylor_y = [round(float(v), 8) for v in y_taylor_display]

        # Wspolczynniki bezpieczne
        safe_coeffs = []
        for c in coeffs:
            s = safe_float(c)
            safe_coeffs.append(round(s, 10) if s is not None else 0)

        result = {
            'success': True,
            'func_data': {'x': func_x, 'y': func_y},
            'taylor_data': {'x': func_x, 'y': taylor_y},
            'coefficients': safe_coeffs,
            'polynomial': polynomial_str,
            'error_at_point': round(safe_float(error_at_point), 10) if error_at_point is not None and safe_float(error_at_point) is not None else None,
            'y_range': [round(float(display_min), 4), round(float(display_max), 4)],
            'convergence_radius': func_info['convergence_radius'],
            'center': center,
        }

        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Nieoczekiwany blad serwera'
        }), 500


@app.route('/api/functions')
def functions():
    """Zwraca liste dostepnych funkcji."""
    result = {}
    for key, info in FUNCTIONS.items():
        result[key] = {
            'name': info['name'],
            'description': info['description'],
            'convergence_radius': info['convergence_radius'],
        }
    return jsonify({'success': True, 'functions': result})


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


if __name__ == '__main__':
    app.run(debug=True, port=5007)
