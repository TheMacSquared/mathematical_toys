"""
Transformacje liniowe 2D - interaktywna wizualizacja.

Backend Flask obliczajacy jak macierz 2x2 przeksztalca
wektory i figury na plaszczyznie.
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
    'identity': {
        'name': 'Macierz jednostkowa',
        'matrix': [[1, 0], [0, 1]],
        'description': 'Niczego nie zmienia - kazdy wektor pozostaje na miejscu.',
    },
    'rotation_90': {
        'name': 'Obrot o 90\u00b0',
        'matrix': [[0, -1], [1, 0]],
        'description': 'Obraca kazdy wektor o 90\u00b0 przeciwnie do ruchu wskazowek zegara.',
    },
    'rotation_45': {
        'name': 'Obrot o 45\u00b0',
        'matrix': [[0.7071, -0.7071], [0.7071, 0.7071]],
        'description': 'Obraca kazdy wektor o 45\u00b0 przeciwnie do ruchu wskazowek zegara.',
    },
    'reflection_x': {
        'name': 'Odbicie wzgl. osi X',
        'matrix': [[1, 0], [0, -1]],
        'description': 'Odbija wzgledem osi X (zmienia znak wspolrzednej y).',
    },
    'reflection_y': {
        'name': 'Odbicie wzgl. osi Y',
        'matrix': [[-1, 0], [0, 1]],
        'description': 'Odbija wzgledem osi Y (zmienia znak wspolrzednej x).',
    },
    'scale_2': {
        'name': 'Skalowanie \u00d72',
        'matrix': [[2, 0], [0, 2]],
        'description': 'Podwaja dlugosc kazdego wektora. Wyznacznik = 4 (pole x4).',
    },
    'shear_x': {
        'name': 'Scinanie w X',
        'matrix': [[1, 1], [0, 1]],
        'description': 'Przechyla figury w kierunku osi X. Wyznacznik = 1 (pole zachowane).',
    },
    'projection_x': {
        'name': 'Rzut na os X',
        'matrix': [[1, 0], [0, 0]],
        'description': 'Rzutuje na os X. Macierz osobliwa (det = 0) - wymiar spada.',
    },
    'singular': {
        'name': 'Macierz osobliwa',
        'matrix': [[1, 2], [2, 4]],
        'description': 'Kolumny sa liniowo zalezne. Cala plaszczyzna zostaje zgnieciona do prostej.',
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
    """Waliduje i zwraca macierz 2x2."""
    if not isinstance(matrix_raw, list) or len(matrix_raw) != 2:
        raise ValueError("Macierz musi byc lista 2 wierszy")
    for i, row in enumerate(matrix_raw):
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError(f"Wiersz {i+1} musi miec 2 elementy")
        for j, val in enumerate(row):
            f = safe_float(val)
            if f is None:
                raise ValueError(f"Element [{i+1},{j+1}] musi byc liczba skonczona")
            if abs(f) > 100:
                raise ValueError(f"Element [{i+1},{j+1}] musi byc z zakresu [-100, 100]")
    return np.array(matrix_raw, dtype=float)


def _compute_transform(matrix):
    """
    Oblicza transformacje macierzy 2x2.

    Returns:
        dict z wynikami gotowymi do jsonify
    """
    a, b = matrix[0]
    c, d = matrix[1]

    det = float(np.linalg.det(matrix))

    # Kwadrat jednostkowy
    unit_square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]).T
    transformed_square = matrix @ unit_square

    # Wektory bazowe e1, e2
    e1 = matrix @ np.array([1, 0])
    e2 = matrix @ np.array([0, 1])

    # Okrag jednostkowy
    theta = np.linspace(0, 2 * np.pi, 64)
    circle = np.array([np.cos(theta), np.sin(theta)])
    transformed_circle = matrix @ circle

    # Wartosci i wektory wlasne
    eigenvalues = None
    eigenvectors = None
    eigen_real = True
    try:
        eigvals, eigvecs = np.linalg.eig(matrix)
        eigen_real = bool(np.all(np.isreal(eigvals)))
        if eigen_real:
            eigvals = eigvals.real
            eigvecs = eigvecs.real
            eigenvalues = [safe_float(eigvals[0]), safe_float(eigvals[1])]
            eigenvectors = [
                [safe_float(eigvecs[0, 0]), safe_float(eigvecs[1, 0])],
                [safe_float(eigvecs[0, 1]), safe_float(eigvecs[1, 1])],
            ]
        else:
            eigenvalues = [
                safe_float(eigvals[0].real),
                safe_float(eigvals[1].real),
            ]
    except np.linalg.LinAlgError:
        pass

    # Rank
    rank = int(np.linalg.matrix_rank(matrix))

    # Trace
    trace = safe_float(float(np.trace(matrix)))

    # Typ transformacji
    transform_type = _classify_transform(matrix, det, rank)

    return {
        'det': round(safe_float(det), 6) if safe_float(det) is not None else 0,
        'rank': rank,
        'trace': round(trace, 6) if trace is not None else 0,
        'eigenvalues': eigenvalues,
        'eigenvectors': eigenvectors,
        'eigen_real': eigen_real,
        'transform_type': transform_type,
        'unit_square': {
            'x': unit_square[0].tolist(),
            'y': unit_square[1].tolist(),
        },
        'transformed_square': {
            'x': transformed_square[0].tolist(),
            'y': transformed_square[1].tolist(),
        },
        'e1': [safe_float(e1[0]), safe_float(e1[1])],
        'e2': [safe_float(e2[0]), safe_float(e2[1])],
        'circle': {
            'x': circle[0].tolist(),
            'y': circle[1].tolist(),
        },
        'transformed_circle': {
            'x': transformed_circle[0].tolist(),
            'y': transformed_circle[1].tolist(),
        },
    }


def _classify_transform(matrix, det, rank):
    """Klasyfikuje typ transformacji."""
    if rank < 2:
        if rank == 0:
            return "Macierz zerowa"
        return "Macierz osobliwa (projekcja na podprzestrzen)"

    a, b = matrix[0]
    c, d = matrix[1]

    # Sprawdz czy macierz jednostkowa
    if np.allclose(matrix, np.eye(2)):
        return "Tozsamosc"

    # Sprawdz skalowanie (macierz diagonalna z rownymi elementami)
    if np.allclose(matrix, a * np.eye(2)) and a != 0:
        return f"Skalowanie (wspolczynnik {a:.2f})"

    # Sprawdz obrot
    if np.allclose(matrix @ matrix.T, np.eye(2) * (a*a + b*b), atol=1e-6):
        if np.isclose(det, 1.0, atol=1e-6):
            angle = math.degrees(math.atan2(c, a))
            return f"Obrot o {angle:.1f}\u00b0"
        if np.isclose(det, -1.0, atol=1e-6):
            return "Odbicie"

    if np.isclose(det, 1.0, atol=1e-6):
        return "Przeksztalcenie zachowujace pole (det = 1)"

    return "Przeksztalcenie liniowe"


@app.route('/')
def index():
    """Strona glowna"""
    return render_template('index.html')


@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Oblicza transformacje dla podanej macierzy 2x2.

    Request JSON:
        matrix: [[a, b], [c, d]]

    Response JSON:
        det, rank, trace, eigenvalues, eigenvectors, eigen_real,
        transform_type, unit_square, transformed_square, e1, e2,
        circle, transformed_circle
    """
    try:
        data = _validate_request_json()

        if 'matrix' not in data:
            raise ValueError("Brak wymaganego pola 'matrix'")

        matrix = _validate_matrix(data['matrix'])
        result = _compute_transform(matrix)
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
    result = {}
    for key, preset in PRESETS.items():
        result[key] = {
            'name': preset['name'],
            'matrix': preset['matrix'],
            'description': preset['description'],
        }
    return jsonify({'success': True, 'presets': result})


if __name__ == '__main__':
    app.run(debug=True, port=5005)
