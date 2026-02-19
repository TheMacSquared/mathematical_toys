"""Tests for the function_derivatives Flask backend."""
import math


def test_index_returns_200(function_derivatives_client):
    resp = function_derivatives_client.get('/')
    assert resp.status_code == 200


def test_functions_endpoint(function_derivatives_client):
    resp = function_derivatives_client.get('/api/functions')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'functions' in data
    assert 'sin' in data['functions']
    assert 'quadratic' in data['functions']
    assert 'params' in data['functions']['sin']


def test_compute_sin_default(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {'a': 1, 'b': 1, 'c': 0},
        'view_mode': 'separate',
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'func_data' in data
    assert 'derivative_data' in data
    assert len(data['func_data']['x']) == 500
    assert len(data['derivative_data']['x']) == 500


def test_compute_sin_derivative_values(function_derivatives_client):
    """sin'(x) = cos(x), check at x=0: f'(0)=1."""
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {'a': 1, 'b': 1, 'c': 0},
        'view_mode': 'combined',
    })
    data = resp.get_json()
    assert data['success'] is True
    # Find y value at x closest to 0 in derivative data
    x_vals = data['derivative_data']['x']
    y_vals = data['derivative_data']['y']
    idx_zero = min(range(len(x_vals)), key=lambda i: abs(x_vals[i]))
    # cos(0) = 1
    assert abs(y_vals[idx_zero] - 1.0) < 0.05


def test_compute_quadratic_derivative(function_derivatives_client):
    """f(x) = x^2, f'(x) = 2x."""
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'quadratic',
        'params': {'a': 1, 'b': 0, 'c': 0},
        'view_mode': 'separate',
    })
    data = resp.get_json()
    assert data['success'] is True
    # Check that derivative at x closest to 1 is close to 2
    x_vals = data['derivative_data']['x']
    y_vals = data['derivative_data']['y']
    idx_one = min(range(len(x_vals)), key=lambda i: abs(x_vals[i] - 1))
    assert abs(y_vals[idx_one] - 2.0) < 0.1


def test_compute_exp_derivative(function_derivatives_client):
    """f(x) = e^x, f'(x) = e^x. At x=0: f(0)=f'(0)=1."""
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'exp',
        'params': {'a': 1, 'b': 1},
        'view_mode': 'combined',
    })
    data = resp.get_json()
    assert data['success'] is True
    assert data['view_mode'] == 'combined'


def test_compute_view_mode_combined(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'view_mode': 'combined',
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['view_mode'] == 'combined'
    assert 'y_range_combined' in data


def test_compute_with_custom_range(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'view_mode': 'separate',
        'x_min': -3.14,
        'x_max': 3.14,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True


def test_compute_unknown_function(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'nonexistent',
        'params': {},
        'view_mode': 'separate',
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_invalid_view_mode(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'view_mode': 'invalid',
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_missing_json_body(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute',
                                             data=b'',
                                             content_type='application/json')
    assert resp.status_code in (400, 500)
    assert resp.get_json()['success'] is False


def test_compute_ln_domain(function_derivatives_client):
    """ln should have NaN values outside its domain."""
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'ln',
        'params': {'a': 1, 'b': 1, 'c': 1},
        'view_mode': 'separate',
        'x_min': -5,
        'x_max': 5,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    # Some y values should be None (outside domain where x + 1 <= 0)
    assert None in data['func_data']['y']


def test_compute_with_custom_params(function_derivatives_client):
    """Test parameterized sin: 2*sin(3x)."""
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {'a': 2, 'b': 3, 'c': 0},
        'view_mode': 'separate',
    })
    data = resp.get_json()
    assert data['success'] is True


def test_compute_formulas_returned(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'view_mode': 'separate',
    })
    data = resp.get_json()
    assert data['success'] is True
    assert 'func_formula' in data
    assert 'derivative_formula' in data
    assert 'sin' in data['func_formula']
    assert 'cos' in data['derivative_formula']


def test_compute_y_ranges_returned(function_derivatives_client):
    resp = function_derivatives_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'view_mode': 'separate',
    })
    data = resp.get_json()
    assert data['success'] is True
    assert 'y_range_func' in data
    assert 'y_range_deriv' in data
    assert 'y_range_combined' in data
    assert len(data['y_range_func']) == 2
    assert data['y_range_func'][0] < data['y_range_func'][1]
