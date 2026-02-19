"""
Shared pytest fixtures for mathematical_toys test suite.

Uses importlib to load Flask app modules from non-package directories
(toys/*) that import from a shared common/ package.
"""
import importlib.util
import sys
import os

import pytest

# ── Paths ──────────────────────────────────────────────────────────
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
TOYS_DIR = os.path.join(ROOT_DIR, 'toys')


# ── Module loader ──────────────────────────────────────────────────
def _load_toy_module(toy_name):
    """
    Load toys/<toy_name>/app.py via importlib.

    Each module gets a unique name (toy_<name>) to avoid collisions,
    since all toy apps share the filename 'app.py'.  toys/ is added
    to sys.path so that ``from common.flask_app import ...`` resolves.
    """
    module_key = f"toy_{toy_name}"
    if module_key in sys.modules:
        return sys.modules[module_key]

    app_path = os.path.join(TOYS_DIR, toy_name, 'app.py')
    if TOYS_DIR not in sys.path:
        sys.path.insert(0, TOYS_DIR)

    spec = importlib.util.spec_from_file_location(module_key, app_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_key] = module
    spec.loader.exec_module(module)
    return module


# ── Session-scoped module fixtures (loaded once) ───────────────────

@pytest.fixture(scope="session")
def linear_transforms_module():
    return _load_toy_module("linear_transforms")


@pytest.fixture(scope="session")
def matrix_calculator_module():
    return _load_toy_module("matrix_calculator")


@pytest.fixture(scope="session")
def taylor_series_module():
    return _load_toy_module("taylor_series")


# ── Function-scoped client fixtures (reset state each test) ────────

@pytest.fixture
def linear_transforms_client(linear_transforms_module):
    """Flask test client for linear_transforms (stateless)."""
    linear_transforms_module.app.config['TESTING'] = True
    with linear_transforms_module.app.test_client() as client:
        yield client


@pytest.fixture
def matrix_calculator_client(matrix_calculator_module):
    """Flask test client for matrix_calculator (stateless)."""
    matrix_calculator_module.app.config['TESTING'] = True
    with matrix_calculator_module.app.test_client() as client:
        yield client


@pytest.fixture
def taylor_series_client(taylor_series_module):
    """Flask test client for taylor_series (stateless)."""
    taylor_series_module.app.config['TESTING'] = True
    with taylor_series_module.app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def function_derivatives_module():
    return _load_toy_module("function_derivatives")


@pytest.fixture(scope="session")
def tangent_line_module():
    return _load_toy_module("tangent_line")


@pytest.fixture
def function_derivatives_client(function_derivatives_module):
    """Flask test client for function_derivatives (stateless)."""
    function_derivatives_module.app.config['TESTING'] = True
    with function_derivatives_module.app.test_client() as client:
        yield client


@pytest.fixture
def tangent_line_client(tangent_line_module):
    """Flask test client for tangent_line (stateless)."""
    tangent_line_module.app.config['TESTING'] = True
    with tangent_line_module.app.test_client() as client:
        yield client
