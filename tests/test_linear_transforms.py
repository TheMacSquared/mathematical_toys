"""Tests for the linear_transforms Flask backend."""


def test_index_returns_200(linear_transforms_client):
    resp = linear_transforms_client.get('/')
    assert resp.status_code == 200


def test_compute_identity(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={
        'matrix': [[1, 0], [0, 1]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['det'] - 1.0) < 1e-6
    assert data['rank'] == 2
    assert data['transform_type'] == 'Tozsamosc'
    assert 'e1' in data
    assert 'e2' in data
    assert 'transformed_square' in data


def test_compute_rotation_90(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={
        'matrix': [[0, -1], [1, 0]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['det'] - 1.0) < 1e-6
    assert data['rank'] == 2
    assert 'Obrot' in data['transform_type']


def test_compute_singular_matrix(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={
        'matrix': [[1, 2], [2, 4]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['det']) < 1e-6
    assert data['rank'] == 1


def test_compute_scaling(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={
        'matrix': [[3, 0], [0, 3]],
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert abs(data['det'] - 9.0) < 1e-6
    assert data['e1'] == [3.0, 0.0]
    assert data['e2'] == [0.0, 3.0]


def test_compute_missing_json_body(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute',
                                          data=b'',
                                          content_type='application/json')
    assert resp.status_code in (400, 500)
    assert resp.get_json()['success'] is False


def test_compute_missing_matrix_field(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={})
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_invalid_matrix_size(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={
        'matrix': [[1, 2, 3], [4, 5, 6]],
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_compute_element_out_of_range(linear_transforms_client):
    resp = linear_transforms_client.post('/api/compute', json={
        'matrix': [[999, 0], [0, 1]],
    })
    assert resp.status_code == 400
    assert resp.get_json()['success'] is False


def test_presets_endpoint(linear_transforms_client):
    resp = linear_transforms_client.get('/api/presets')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'presets' in data
    assert 'identity' in data['presets']
    assert 'rotation_90' in data['presets']
    assert 'matrix' in data['presets']['identity']
