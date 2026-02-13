# Mathematical Toys - Agent Instructions

## Testing
- Run tests before committing: `python -m pytest`
- All tests must pass before any push
- When modifying any `app.py`, run at minimum the corresponding test file:
  - `python -m pytest tests/test_linear_transforms.py`
  - `python -m pytest tests/test_matrix_calculator.py`
  - `python -m pytest tests/test_taylor_series.py`
- When adding a new endpoint, add tests for it in the corresponding test file

## Project structure
- 3 Flask desktop apps in `toys/` (linear_transforms, matrix_calculator, taylor_series)
- Shared code in `toys/common/`
- Single-user desktop apps using global in-memory sessions, ports 15005-15007
- Tests in `tests/` with importlib-based fixtures in `conftest.py`

## Dependencies
- `pip install -r requirements.txt` installs everything including pytest
