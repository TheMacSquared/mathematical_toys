"""Tests for the matrix_calculator Flask backend."""


def test_index_returns_200(matrix_calculator_client):
    resp = matrix_calculator_client.get('/')
    assert resp.status_code == 200


def test_compute_identity_3x3(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['rows'] == 3
    assert data['cols'] == 3
    assert data['is_square'] is True
    assert data['rank'] == 3
    assert abs(data['det'] - 1.0) < 1e-6
    assert data['inverse'] is not None
    assert 'gauss_steps' in data
    assert len(data['gauss_steps']) >= 1


def test_compute_singular_matrix(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['rank'] == 2
    assert abs(data['det']) < 1e-6
    assert data['inverse'] is None


def test_compute_non_square(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': [[1, 2, 3], [4, 5, 6]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['rows'] == 2
    assert data['cols'] == 3
    assert data['is_square'] is False
    assert data['det'] is None
    assert data['trace'] is None
    assert data['inverse'] is None
    assert data['eigenvalues'] is None


def test_compute_2x2_invertible(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': [[2, 1], [1, 3]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['det'] - 5.0) < 1e-6
    assert data['inverse'] is not None
    assert data['eigenvalues'] is not None


def test_compute_eigenvalues_real(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': [[4, 1], [2, 3]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['eigenvalues'] is not None
    assert data['eigenvalues_complex'] is False
    assert len(data['eigenvalues']) == 2


def test_compute_missing_json_body(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute',
                                          data=b'',
                                          content_type='application/json')
    assert resp.status_code in (400, 500)
    assert resp.get_json()['success'] is False


def test_compute_missing_matrix_field(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_matrix_too_large(matrix_calculator_client):
    big = [[1] * 7 for _ in range(7)]
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': big,
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_element_out_of_range(matrix_calculator_client):
    resp = matrix_calculator_client.post('/api/compute', json={
        'matrix': [[99999, 0], [0, 1]],
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_presets_endpoint(matrix_calculator_client):
    resp = matrix_calculator_client.get('/api/presets')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'presets' in data
    assert 'identity_3' in data['presets']
    assert 'singular' in data['presets']
