"""Smoke tests: verify all 5 app modules load and expose a Flask app."""
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


def test_function_derivatives_module_loads(function_derivatives_module):
    assert hasattr(function_derivatives_module, 'app')
    assert isinstance(function_derivatives_module.app, Flask)
    rules = [r.rule for r in function_derivatives_module.app.url_map.iter_rules()]
    assert '/api/compute' in rules
    assert '/api/functions' in rules


def test_tangent_line_module_loads(tangent_line_module):
    assert hasattr(tangent_line_module, 'app')
    assert isinstance(tangent_line_module.app, Flask)
    rules = [r.rule for r in tangent_line_module.app.url_map.iter_rules()]
    assert '/api/compute' in rules
    assert '/api/functions' in rules
