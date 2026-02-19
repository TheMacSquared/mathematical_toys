# Mathematical Toys - Agent Instructions

## Testing
- Run tests before committing: `python -m pytest`
- All tests must pass before any push
- When modifying any `app.py`, run at minimum the corresponding test file:
  - `python -m pytest tests/test_linear_transforms.py`
  - `python -m pytest tests/test_matrix_calculator.py`
  - `python -m pytest tests/test_taylor_series.py`
  - `python -m pytest tests/test_function_composition.py`
  - `python -m pytest tests/test_function_derivatives.py`
  - `python -m pytest tests/test_tangent_line.py`
- When modifying `toys/common/functions.py`, run: `python -m pytest tests/test_common_functions.py`
- When adding a new endpoint, add tests for it in the corresponding test file

## Project structure
- 6 Flask desktop apps in `toys/` (linear_transforms, matrix_calculator, taylor_series, function_composition, function_derivatives, tangent_line)
- Shared code in `toys/common/` (flask_app.py, functions.py, build_utils.py)
- Single-user desktop apps using global in-memory sessions, ports 15005-15009
- Tests in `tests/` with importlib-based fixtures in `conftest.py`

## Dependencies
- `pip install -r requirements.txt` installs everything including pytest
