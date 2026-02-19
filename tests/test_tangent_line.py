"""Tests for the tangent_line Flask backend."""
import math


def test_index_returns_200(tangent_line_client):
    resp = tangent_line_client.get('/')
    assert resp.status_code == 200


def test_functions_endpoint(tangent_line_client):
    resp = tangent_line_client.get('/api/functions')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'functions' in data
    assert 'sin' in data['functions']


def test_compute_quadratic_tangent_at_1(tangent_line_client):
    """f(x) = x^2, f'(1) = 2, f(1) = 1, tangent: y = 2x - 1."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'quadratic',
        'params': {'a': 1, 'b': 0, 'c': 0},
        'x0': 1.0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['slope'] - 2.0) < 1e-6
    assert abs(data['func_value_at_x0'] - 1.0) < 1e-6
    assert abs(data['tangent_point']['x'] - 1.0) < 1e-6
    assert abs(data['tangent_point']['y'] - 1.0) < 1e-6
    assert 'tangent_data' in data
    assert 'tangent_equation' in data


def test_compute_sin_tangent_at_0(tangent_line_client):
    """f(x) = sin(x), f'(0) = cos(0) = 1, f(0) = 0, tangent: y = x."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'sin',
        'params': {'a': 1, 'b': 1, 'c': 0},
        'x0': 0.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['slope'] - 1.0) < 1e-6
    assert abs(data['func_value_at_x0']) < 1e-6


def test_compute_exp_tangent_at_0(tangent_line_client):
    """f(x) = e^x, f'(0) = 1, f(0) = 1, tangent: y = x + 1."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'exp',
        'params': {'a': 1, 'b': 1},
        'x0': 0.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['slope'] - 1.0) < 1e-6
    assert abs(data['func_value_at_x0'] - 1.0) < 1e-6


def test_compute_with_custom_range(tangent_line_client):
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'x0': 0,
        'x_min': -3,
        'x_max': 3,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True


def test_compute_unknown_function(tangent_line_client):
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'nonexistent',
        'params': {},
        'x0': 0,
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_missing_json_body(tangent_line_client):
    resp = tangent_line_client.post('/api/compute',
                                     data=b'',
                                     content_type='application/json')
    assert resp.status_code in (400, 500)
    assert resp.get_json()['success'] is False


def test_compute_x0_outside_domain(tangent_line_client):
    """ln(x+1) is undefined at x=-2."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'ln',
        'params': {'a': 1, 'b': 1, 'c': 1},
        'x0': -2.0,
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['success'] is False


def test_compute_constant_tangent(tangent_line_client):
    """f(x) = 5 (linear with a=0, b=5), f'(x) = 0 everywhere."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'linear',
        'params': {'a': 0, 'b': 5},
        'x0': 3.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['slope']) < 1e-6


def test_compute_cubic_tangent(tangent_line_client):
    """f(x) = x^3, f'(2) = 12, f(2) = 8."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'cubic',
        'params': {'a': 1, 'b': 0, 'c': 0, 'd': 0},
        'x0': 2.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['slope'] - 12.0) < 1e-6
    assert abs(data['func_value_at_x0'] - 8.0) < 1e-6


def test_compute_tangent_equation_format(tangent_line_client):
    """Verify tangent equation string is returned."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'quadratic',
        'params': {'a': 1, 'b': 0, 'c': 0},
        'x0': 1.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert 'y =' in data['tangent_equation']


def test_compute_derivative_at_x0(tangent_line_client):
    """Verify derivative_at_x0 field."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'quadratic',
        'params': {'a': 1, 'b': 0, 'c': 0},
        'x0': 3.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['derivative_at_x0'] - 6.0) < 1e-6


def test_compute_tangent_data_length(tangent_line_client):
    """Tangent data should have 500 points like function data."""
    resp = tangent_line_client.post('/api/compute', json={
        'func': 'sin',
        'params': {},
        'x0': 0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert len(data['tangent_data']['x']) == 500
    assert len(data['func_data']['x']) == 500
