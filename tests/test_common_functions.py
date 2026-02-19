"""Tests for the shared function library (toys/common/functions.py)."""
import sys
import os
import numpy as np
import math

# Ensure toys/ is on path so common.functions can be imported
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
TOYS_DIR = os.path.join(ROOT_DIR, 'toys')
if TOYS_DIR not in sys.path:
    sys.path.insert(0, TOYS_DIR)

from common.functions import (
    FUNCTION_REGISTRY, evaluate_function, evaluate_derivative,
    get_all_functions, resolve_params
)


def test_all_functions_registered():
    expected = {'linear', 'quadratic', 'cubic', 'sin', 'cos',
                'exp', 'ln', 'power', 'sqrt', 'tan'}
    assert set(FUNCTION_REGISTRY.keys()) == expected


def test_linear_evaluation():
    x = np.array([0, 1, 2], dtype=float)
    y = evaluate_function('linear', x, {'a': 2, 'b': 3})
    np.testing.assert_allclose(y, [3, 5, 7])


def test_linear_derivative():
    x = np.array([0, 1, 2], dtype=float)
    y = evaluate_derivative('linear', x, {'a': 2, 'b': 3})
    np.testing.assert_allclose(y, [2, 2, 2])


def test_quadratic_evaluation():
    x = np.array([-1, 0, 1, 2], dtype=float)
    y = evaluate_function('quadratic', x, {'a': 1, 'b': 0, 'c': 0})
    np.testing.assert_allclose(y, [1, 0, 1, 4])


def test_quadratic_derivative():
    x = np.array([-1, 0, 1, 2], dtype=float)
    y = evaluate_derivative('quadratic', x, {'a': 1, 'b': 0, 'c': 0})
    np.testing.assert_allclose(y, [-2, 0, 2, 4])


def test_cubic_derivative():
    x = np.array([0, 1, 2], dtype=float)
    # f(x) = x^3, f'(x) = 3x^2
    y = evaluate_derivative('cubic', x, {'a': 1, 'b': 0, 'c': 0, 'd': 0})
    np.testing.assert_allclose(y, [0, 3, 12])


def test_sin_derivative_is_cos():
    x = np.linspace(-np.pi, np.pi, 100)
    dy = evaluate_derivative('sin', x, {'a': 1, 'b': 1, 'c': 0})
    expected = np.cos(x)
    np.testing.assert_allclose(dy, expected, atol=1e-10)


def test_cos_derivative_is_neg_sin():
    x = np.linspace(-np.pi, np.pi, 100)
    dy = evaluate_derivative('cos', x, {'a': 1, 'b': 1, 'c': 0})
    expected = -np.sin(x)
    np.testing.assert_allclose(dy, expected, atol=1e-10)


def test_exp_derivative_is_exp():
    x = np.array([0, 1, -1], dtype=float)
    dy = evaluate_derivative('exp', x, {'a': 1, 'b': 1})
    y = evaluate_function('exp', x, {'a': 1, 'b': 1})
    np.testing.assert_allclose(dy, y, atol=1e-10)


def test_ln_evaluation():
    x = np.array([-2, -1, 0, 1], dtype=float)
    y = evaluate_function('ln', x, {'a': 1, 'b': 1, 'c': 1})
    # inner = x + 1: [-1, 0, 1, 2]
    assert math.isnan(y[0])  # inner = -1 <= 0
    assert math.isnan(y[1])  # inner = 0 <= 0
    assert abs(y[2] - 0.0) < 1e-10  # ln(1) = 0
    assert abs(y[3] - math.log(2)) < 1e-10


def test_ln_derivative():
    x = np.array([0, 1, 3], dtype=float)
    # f(x) = ln(x + 1), f'(x) = 1/(x + 1)
    dy = evaluate_derivative('ln', x, {'a': 1, 'b': 1, 'c': 1})
    np.testing.assert_allclose(dy, [1.0, 0.5, 0.25])


def test_power_evaluation():
    x = np.array([1, 2, 3], dtype=float)
    y = evaluate_function('power', x, {'a': 2, 'n': 3})
    np.testing.assert_allclose(y, [2, 16, 54])


def test_power_derivative():
    x = np.array([1, 2, 3], dtype=float)
    # f(x) = x^3, f'(x) = 3x^2
    dy = evaluate_derivative('power', x, {'a': 1, 'n': 3})
    np.testing.assert_allclose(dy, [3, 12, 27])


def test_sqrt_evaluation():
    x = np.array([-2, 0, 4], dtype=float)
    y = evaluate_function('sqrt', x, {'a': 1, 'b': 1, 'c': 0})
    assert math.isnan(y[0])
    assert abs(y[1]) < 1e-10
    assert abs(y[2] - 2.0) < 1e-10


def test_sqrt_derivative():
    x = np.array([1, 4, 9], dtype=float)
    # f(x) = sqrt(x), f'(x) = 1/(2*sqrt(x))
    dy = evaluate_derivative('sqrt', x, {'a': 1, 'b': 1, 'c': 0})
    np.testing.assert_allclose(dy, [0.5, 0.25, 1.0/6], atol=1e-10)


def test_tan_asymptote_masking():
    # At x = pi/2, tan has asymptote
    x = np.array([0, math.pi / 2, math.pi], dtype=float)
    y = evaluate_function('tan', x, {'a': 1, 'b': 1, 'c': 0})
    assert abs(y[0]) < 1e-10
    assert math.isnan(y[1])  # asymptote
    assert abs(y[2]) < 1e-10


def test_resolve_params_fills_defaults():
    params = resolve_params('sin', {})
    assert params == {'a': 1, 'b': 1, 'c': 0}


def test_resolve_params_overrides():
    params = resolve_params('sin', {'a': 2})
    assert params == {'a': 2, 'b': 1, 'c': 0}


def test_resolve_params_unknown_function():
    try:
        resolve_params('nonexistent', {})
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_resolve_params_out_of_range():
    try:
        resolve_params('sin', {'a': 100})  # max is 10
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_get_all_functions():
    funcs = get_all_functions()
    assert len(funcs) == 10
    for key, info in funcs.items():
        assert 'name' in info
        assert 'params' in info
        assert 'formula' in info
        assert 'derivative_formula' in info
        assert 'default_range' in info


def test_parameterized_sin():
    """Test 2*sin(3x) and its derivative 6*cos(3x)."""
    x = np.array([0], dtype=float)
    y = evaluate_function('sin', x, {'a': 2, 'b': 3, 'c': 0})
    assert abs(y[0]) < 1e-10  # 2*sin(0) = 0
    dy = evaluate_derivative('sin', x, {'a': 2, 'b': 3, 'c': 0})
    assert abs(dy[0] - 6.0) < 1e-10  # 2*3*cos(0) = 6


def test_power_fractional_exponent_domain():
    """Fractional exponent: x^0.5 undefined for x < 0."""
    x = np.array([-1, 0, 1, 4], dtype=float)
    y = evaluate_function('power', x, {'a': 1, 'n': 0.5})
    assert math.isnan(y[0])
    assert abs(y[1]) < 1e-10
    assert abs(y[2] - 1.0) < 1e-10
    assert abs(y[3] - 2.0) < 1e-10
