"""Tests for the function_composition Flask backend."""
import math


# --- Basic endpoint tests ---

def test_index_returns_200(function_composition_client):
    """GET / returns 200."""
    resp = function_composition_client.get('/')
    assert resp.status_code == 200


def test_functions_endpoint(function_composition_client):
    """GET /api/functions returns function list with metadata."""
    resp = function_composition_client.get('/api/functions')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'functions' in data
    funcs = data['functions']
    assert 'power' in funcs
    assert 'shift' in funcs
    assert 'scale' in funcs
    assert 'sin' in funcs
    assert 'ln' in funcs
    # Check metadata fields
    assert 'name' in funcs['power']
    assert funcs['power']['has_param'] is True
    assert funcs['abs']['has_param'] is False


# --- Compute: classic example f=t^2, g=t+3 ---

def test_compute_square_shift(function_composition_client):
    """f=t^2, g=t+3, x0=2: g(2)=5, f(g(2))=25."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 2.0,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['g_x0'] - 5.0) < 1e-6
    assert abs(data['f_g_x0'] - 25.0) < 1e-6
    assert abs(data['f_x0'] - 4.0) < 1e-6
    assert abs(data['g_f_x0'] - 7.0) < 1e-6
    # Common mistakes
    assert abs(data['f_x0_plus_g_x0'] - 9.0) < 1e-6   # f(2)+g(2) = 4+5
    assert abs(data['f_x0_times_g_x0'] - 20.0) < 1e-6  # f(2)*g(2) = 4*5
    # Curves present
    assert 'g_curve' in data
    assert 'f_curve' in data
    assert 'fg_curve' in data
    assert 'gf_curve' in data
    assert len(data['fg_curve']['x']) == 500
    assert len(data['gf_curve']['x']) == 500


def test_compute_reverse_composition(function_composition_client):
    """f(g(x)) != g(f(x)) for non-commuting functions."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 2.0,
    })
    data = resp.get_json()
    # f(g(2)) = (2+3)^2 = 25, g(f(2)) = 2^2 + 3 = 7
    assert data['f_g_x0'] != data['g_f_x0']
    assert abs(data['f_g_x0'] - 25.0) < 1e-6
    assert abs(data['g_f_x0'] - 7.0) < 1e-6


def test_compute_labels(function_composition_client):
    """Response includes human-readable labels."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 1.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert 'f_label' in data
    assert 'g_label' in data
    assert 'fg_label' in data
    assert 'gf_label' in data
    assert 't\u00b2' in data['f_label']  # t²


# --- Compute: linear composition (commutative) ---

def test_compute_linear_composition(function_composition_client):
    """f=2t, g=t+3, x0=2: f(g(2))=2*(2+3)=10."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'scale', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 2.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['f_g_x0'] - 10.0) < 1e-6
    # g(f(2)) = 2*2 + 3 = 7
    assert abs(data['g_f_x0'] - 7.0) < 1e-6


def test_compute_identity_composition(function_composition_client):
    """f=1*t (identity), g=t+0 (identity): f(g(x))=x."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'scale', 'f_param': 1,
        'g_id': 'shift', 'g_param': 0,
        'x0': 3.7,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['f_g_x0'] - 3.7) < 1e-6
    assert abs(data['g_f_x0'] - 3.7) < 1e-6


# --- Compute: trigonometric ---

def test_compute_sin_scale(function_composition_client):
    """f=sin(t), g=2t, x0=pi/4: f(g(pi/4))=sin(pi/2)=1."""
    x0 = math.pi / 4
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'sin', 'f_param': 1,
        'g_id': 'scale', 'g_param': 2,
        'x0': x0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['f_g_x0'] - 1.0) < 1e-6


# --- Compute: exponential ---

def test_compute_exp_shift(function_composition_client):
    """f=e^t, g=t+a: f(g(x))=e^(x+a)=e^x * e^a."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'exp', 'f_param': 1,
        'g_id': 'shift', 'g_param': 1,
        'x0': 1.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['f_g_x0'] - math.exp(2)) < 1e-4


# --- Compute: cube ---

def test_compute_cube(function_composition_client):
    """f=t^3, g=t+1, x0=2: f(g(2))=(2+1)^3=27."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 3,
        'g_id': 'shift', 'g_param': 1,
        'x0': 2.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['f_g_x0'] - 27.0) < 1e-6


# --- Pipeline ---

def test_pipeline_has_steps(function_composition_client):
    """Response includes pipeline_fg and pipeline_gf with 3 steps each."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 2.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert 'pipeline_fg' in data
    assert 'pipeline_gf' in data
    assert len(data['pipeline_fg']) == 3
    assert len(data['pipeline_gf']) == 3
    # First step is x0
    assert data['pipeline_fg'][0]['label'] == 'x\u2080'
    assert abs(data['pipeline_fg'][0]['value'] - 2.0) < 1e-6
    # Last step is f(g(x0))
    assert abs(data['pipeline_fg'][2]['value'] - 25.0) < 1e-6
    assert data['pipeline_fg'][2]['detail'] is not None


def test_common_mistakes_present(function_composition_client):
    """Response includes f(x0)+g(x0) and f(x0)*g(x0)."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 2.0,
    })
    data = resp.get_json()
    assert 'f_x0_plus_g_x0' in data
    assert 'f_x0_times_g_x0' in data
    assert data['f_x0_plus_g_x0'] is not None
    assert data['f_x0_times_g_x0'] is not None


# --- Error handling ---

def test_compute_unknown_function(function_composition_client):
    """Unknown function returns 400."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'nonexistent', 'f_param': 1,
        'g_id': 'shift', 'g_param': 0,
        'x0': 0,
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_missing_json(function_composition_client):
    """Missing JSON body returns error."""
    resp = function_composition_client.post('/api/compute',
                                            data=b'',
                                            content_type='application/json')
    assert resp.status_code in (400, 500)
    assert resp.get_json()['success'] is False


def test_compute_x0_out_of_range(function_composition_client):
    """x0 > 100 returns 400."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 0,
        'x0': 999.0,
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


# --- Domain handling ---

def test_compute_sqrt_composition(function_composition_client):
    """f=sqrt(t), g=t+5, x0=4: g(4)=9, f(g(4))=3."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 0.5,
        'g_id': 'shift', 'g_param': 5,
        'x0': 4.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['g_x0'] - 9.0) < 1e-6
    assert abs(data['f_g_x0'] - 3.0) < 1e-6


def test_compute_ln_composition(function_composition_client):
    """f=ln(t), g=t+1, x0=math.e-1: g(e-1)=e, f(g(e-1))=1."""
    x0 = math.e - 1
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'ln',
        'g_id': 'shift', 'g_param': 1,
        'x0': x0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['f_g_x0'] - 1.0) < 1e-6


def test_compute_abs_composition(function_composition_client):
    """f=|t|, g=t-5, x0=2: g(2)=-3, f(g(2))=3."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'abs',
        'g_id': 'shift', 'g_param': -5,
        'x0': 2.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['g_x0'] - (-3.0)) < 1e-6
    assert abs(data['f_g_x0'] - 3.0) < 1e-6


def test_gf_curve_differs_from_fg(function_composition_client):
    """g(f(x)) curve is different from f(g(x)) for non-commuting functions."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'power', 'f_param': 2,
        'g_id': 'shift', 'g_param': 3,
        'x0': 2.0,
    })
    data = resp.get_json()
    assert data['success'] is True
    # gf_curve should exist and differ from fg_curve
    fg_y = data['fg_curve']['y']
    gf_y = data['gf_curve']['y']
    assert len(gf_y) == 500
    # At x=2 (approximately index 350): fg = (2+3)^2 = 25, gf = 2^2 + 3 = 7
    # Curves should differ at most points
    diffs = sum(1 for a, b in zip(fg_y, gf_y)
                if a is not None and b is not None and abs(a - b) > 0.01)
    assert diffs > 100  # Most points differ
    # gf_label should be present
    assert 'gf_label' in data
    assert data['gf_label'] != data['fg_label']


def test_compute_y_range_present(function_composition_client):
    """Response includes y_range for plot."""
    resp = function_composition_client.post('/api/compute', json={
        'f_id': 'sin', 'f_param': 1,
        'g_id': 'scale', 'g_param': 1,
        'x0': 0,
    })
    data = resp.get_json()
    assert 'y_range' in data
    assert len(data['y_range']) == 2
    assert data['y_range'][0] < data['y_range'][1]
