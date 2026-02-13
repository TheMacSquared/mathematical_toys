"""Tests for the taylor_series Flask backend."""
import math


def test_index_returns_200(taylor_series_client):
    resp = taylor_series_client.get('/')
    assert resp.status_code == 200


def test_compute_sin_default(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'sin',
        'degree': 5,
        'center': 0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'func_data' in data
    assert 'taylor_data' in data
    assert 'coefficients' in data
    assert len(data['coefficients']) == 6  # degree 5 -> 6 coefficients
    assert 'polynomial' in data
    assert data['convergence_radius'] is None  # sin has infinite R


def test_compute_exp(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'exp',
        'degree': 4,
        'center': 0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    # e^x coefficients: 1, 1, 1/2, 1/6, 1/24
    coeffs = data['coefficients']
    assert abs(coeffs[0] - 1.0) < 1e-8
    assert abs(coeffs[1] - 1.0) < 1e-8
    assert abs(coeffs[2] - 0.5) < 1e-8
    assert abs(coeffs[3] - 1.0/6) < 1e-8


def test_compute_cos_coefficients(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'cos',
        'degree': 4,
        'center': 0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    coeffs = data['coefficients']
    # cos: 1, 0, -1/2, 0, 1/24
    assert abs(coeffs[0] - 1.0) < 1e-8
    assert abs(coeffs[1]) < 1e-8
    assert abs(coeffs[2] - (-0.5)) < 1e-8
    assert abs(coeffs[3]) < 1e-8


def test_compute_ln1px_convergence_radius(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'ln1px',
        'degree': 3,
        'center': 0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['convergence_radius'] == 1


def test_compute_with_eval_point(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'sin',
        'degree': 10,
        'center': 0,
        'eval_point': 0.5,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    # With degree 10, sin(0.5) should be very well approximated
    assert data['error_at_point'] is not None
    assert data['error_at_point'] < 1e-6


def test_compute_unknown_function(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'nonexistent',
        'degree': 3,
        'center': 0,
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_degree_out_of_range(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'sin',
        'degree': 25,
        'center': 0,
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_missing_json_body(taylor_series_client):
    resp = taylor_series_client.post('/api/compute',
                                      data=b'',
                                      content_type='application/json')
    assert resp.status_code in (400, 500)
    assert resp.get_json()['success'] is False


def test_functions_endpoint(taylor_series_client):
    resp = taylor_series_client.get('/api/functions')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'functions' in data
    assert 'sin' in data['functions']
    assert 'exp' in data['functions']
    assert 'name' in data['functions']['sin']


def test_compute_nonzero_center(taylor_series_client):
    resp = taylor_series_client.post('/api/compute', json={
        'func': 'exp',
        'degree': 5,
        'center': 1.0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['center'] == 1.0
    assert len(data['coefficients']) == 6
