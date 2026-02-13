"""Smoke tests: verify all 3 app modules load and expose a Flask app."""
from flask import Flask


def test_linear_transforms_module_loads(linear_transforms_module):
    assert hasattr(linear_transforms_module, 'app')
    assert isinstance(linear_transforms_module.app, Flask)
    rules = [r.rule for r in linear_transforms_module.app.url_map.iter_rules()]
    assert '/api/compute' in rules
    assert '/api/presets' in rules


def test_matrix_calculator_module_loads(matrix_calculator_module):
    assert hasattr(matrix_calculator_module, 'app')
    assert isinstance(matrix_calculator_module.app, Flask)
    rules = [r.rule for r in matrix_calculator_module.app.url_map.iter_rules()]
    assert '/api/compute' in rules
    assert '/api/presets' in rules


def test_taylor_series_module_loads(taylor_series_module):
    assert hasattr(taylor_series_module, 'app')
    assert isinstance(taylor_series_module.app, Flask)
    rules = [r.rule for r in taylor_series_module.app.url_map.iter_rules()]
    assert '/api/compute' in rules
    assert '/api/functions' in rules
