"""
Kalkulator macierzy - interaktywne operacje na macierzach.

Backend Flask obliczajacy wyznacznik, rzad, RREF, macierz odwrotna,
wartosci wlasne oraz eliminacje Gaussa krok po kroku.
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


PRESETS = {
    'identity_3': {
        'name': 'Jednostkowa 3x3',
        'matrix': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    },
    'invertible': {
        'name': 'Odwracalna 3x3',
        'matrix': [[2, 1, 0], [1, 3, 1], [0, 1, 2]],
    },
    'singular': {
        'name': 'Osobliwa 3x3',
        'matrix': [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    },
    'symmetric': {
        'name': 'Symetryczna 3x3',
        'matrix': [[4, 2, 1], [2, 5, 3], [1, 3, 6]],
    },
    'upper_triangular': {
        'name': 'Trojkatna gorna',
        'matrix': [[3, 1, 4], [0, 2, 5], [0, 0, 1]],
    },
    'rank_2_4x4': {
        'name': 'Rzad 2 (4x4)',
        'matrix': [[1, 2, 3, 4], [2, 4, 6, 8], [1, 1, 1, 1], [2, 2, 2, 2]],
    },
}


def safe_float(val):
    """Bezpieczna konwersja na float - zwraca None dla NaN/Inf."""
    try:
        f = float(val)
    except (ValueError, TypeError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def _validate_request_json():
    """Waliduje ze request zawiera poprawny JSON."""
    data = request.json
    if data is None:
        raise ValueError("Wymagane dane w formacie JSON")
    return data


def _validate_matrix(matrix_raw):
    """Waliduje i zwraca macierz NxM."""
    if not isinstance(matrix_raw, list) or len(matrix_raw) < 1:
        raise ValueError("Macierz musi byc niepusta lista wierszy")

    if len(matrix_raw) > 6:
        raise ValueError("Maksymalny rozmiar macierzy to 6 wierszy")

    n_cols = None
    for i, row in enumerate(matrix_raw):
        if not isinstance(row, list) or len(row) < 1:
            raise ValueError(f"Wiersz {i+1} musi byc niepusta lista")
        if n_cols is None:
            n_cols = len(row)
        elif len(row) != n_cols:
            raise ValueError("Wszystkie wiersze musza miec taka sama liczbe kolumn")
        if len(row) > 6:
            raise ValueError("Maksymalny rozmiar macierzy to 6 kolumn")
        for j, val in enumerate(row):
            f = safe_float(val)
            if f is None:
                raise ValueError(f"Element [{i+1},{j+1}] musi byc liczba skonczona")
            if abs(f) > 10000:
                raise ValueError(f"Element [{i+1},{j+1}] musi byc z zakresu [-10000, 10000]")

    return np.array(matrix_raw, dtype=float)


def _gauss_elimination_steps(matrix):
    """
    Wykonuje eliminacje Gaussa z czesciowym wyborem elementu
    glownego, zwracajac kazdy krok.

    Returns:
        list of dicts z krokami
    """
    m = matrix.copy().astype(float)
    rows, cols = m.shape
    steps = []
    pivot_row = 0

    steps.append({
        'description': 'Macierz wejsciowa',
        'matrix': _matrix_to_safe_list(m),
        'operation': None,
    })

    for col in range(cols):
        if pivot_row >= rows:
            break

        # Znajdz wiersz z max wartoscia w kolumnie
        max_idx = pivot_row
        max_val = abs(m[pivot_row, col])
        for i in range(pivot_row + 1, rows):
            if abs(m[i, col]) > max_val:
                max_val = abs(m[i, col])
                max_idx = i

        if max_val < 1e-12:
            continue

        # Zamien wiersze
        if max_idx != pivot_row:
            m[[pivot_row, max_idx]] = m[[max_idx, pivot_row]]
            steps.append({
                'description': f'Zamiana w{pivot_row+1} <-> w{max_idx+1}',
                'matrix': _matrix_to_safe_list(m),
                'operation': 'swap',
            })

        # Normalizuj wiersz glowny
        pivot_val = m[pivot_row, col]
        if abs(pivot_val - 1.0) > 1e-12:
            m[pivot_row] = m[pivot_row] / pivot_val
            steps.append({
                'description': f'w{pivot_row+1} := w{pivot_row+1} / {pivot_val:.4g}',
                'matrix': _matrix_to_safe_list(m),
                'operation': 'scale',
            })

        # Eliminuj inne wiersze
        for i in range(rows):
            if i == pivot_row:
                continue
            factor = m[i, col]
            if abs(factor) < 1e-12:
                continue
            m[i] = m[i] - factor * m[pivot_row]
            steps.append({
                'description': f'w{i+1} := w{i+1} - ({factor:.4g}) * w{pivot_row+1}',
                'matrix': _matrix_to_safe_list(m),
                'operation': 'eliminate',
            })

        pivot_row += 1

    return steps, m


def _matrix_to_safe_list(m):
    """Konwertuje macierz numpy na liste z bezpiecznymi floatami."""
    result = []
    for row in m:
        safe_row = []
        for val in row:
            s = safe_float(val)
            if s is not None:
                # Zaokraglij bliskie zeru wartosci
                if abs(s) < 1e-12:
                    s = 0.0
                safe_row.append(round(s, 8))
            else:
                safe_row.append(0.0)
        result.append(safe_row)
    return result


def _compute_matrix(matrix):
    """
    Oblicza wszystkie wlasciwosci macierzy.

    Returns:
        dict z wynikami gotowymi do jsonify
    """
    rows, cols = matrix.shape
    is_square = rows == cols

    result = {
        'rows': rows,
        'cols': cols,
        'is_square': is_square,
    }

    # Rzad
    rank = int(np.linalg.matrix_rank(matrix))
    result['rank'] = rank

    # Wyznacznik (tylko kwadratowe)
    if is_square:
        det = float(np.linalg.det(matrix))
        result['det'] = round(safe_float(det), 8) if safe_float(det) is not None else 0
    else:
        result['det'] = None

    # Slad (tylko kwadratowe)
    if is_square:
        trace = float(np.trace(matrix))
        result['trace'] = round(safe_float(trace), 8) if safe_float(trace) is not None else 0
    else:
        result['trace'] = None

    # Macierz odwrotna (kwadratowa + pelny rzad)
    if is_square and rank == rows:
        try:
            inv = np.linalg.inv(matrix)
            result['inverse'] = _matrix_to_safe_list(inv)
        except np.linalg.LinAlgError:
            result['inverse'] = None
    else:
        result['inverse'] = None

    # Macierz transponowana
    result['transpose'] = _matrix_to_safe_list(matrix.T)

    # Wartosci wlasne (tylko kwadratowe)
    if is_square:
        try:
            eigvals = np.linalg.eigvals(matrix)
            all_real = np.all(np.isreal(eigvals))
            if all_real:
                eigvals_list = sorted(eigvals.real.tolist(), reverse=True)
                result['eigenvalues'] = [round(safe_float(v), 6) if safe_float(v) is not None else 0 for v in eigvals_list]
                result['eigenvalues_complex'] = False
            else:
                result['eigenvalues'] = [
                    {'re': round(safe_float(v.real), 6) if safe_float(v.real) is not None else 0,
                     'im': round(safe_float(v.imag), 6) if safe_float(v.imag) is not None else 0}
                    for v in eigvals
                ]
                result['eigenvalues_complex'] = True
        except np.linalg.LinAlgError:
            result['eigenvalues'] = None
            result['eigenvalues_complex'] = None
    else:
        result['eigenvalues'] = None
        result['eigenvalues_complex'] = None

    # Eliminacja Gaussa krok po kroku
    steps, rref = _gauss_elimination_steps(matrix)
    result['gauss_steps'] = steps
    result['rref'] = _matrix_to_safe_list(rref)

    return result


@app.route('/')
def index():
    """Strona glowna"""
    return render_template('index.html')


@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Oblicza wlasciwosci macierzy.

    Request JSON:
        matrix: 2D tablica

    Response JSON:
        rows, cols, is_square, rank, det, trace,
        inverse, transpose, eigenvalues, eigenvalues_complex,
        gauss_steps, rref
    """
    try:
        data = _validate_request_json()

        if 'matrix' not in data:
            raise ValueError("Brak wymaganego pola 'matrix'")

        matrix = _validate_matrix(data['matrix'])
        result = _compute_matrix(matrix)
        result['success'] = True
        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Nieoczekiwany blad serwera'
        }), 500


@app.route('/api/presets')
def presets():
    """Zwraca liste dostepnych presetow."""
    return jsonify({'success': True, 'presets': PRESETS})


if __name__ == '__main__':
    app.run(debug=True, port=5006)
