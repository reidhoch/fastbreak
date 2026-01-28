# Contributing to fastbreak

Thanks for your interest in contributing!

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/reidhoch/fastbreak.git
   cd fastbreak
   ```

2. Install dependencies with [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync --all-groups
   ```

3. Install pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

## Running Tests

```bash
uv run pytest -n auto tests/
```

## Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
uv run complexipy src/
uv run isort src/ tests/
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
```

## Pull Request Guidelines

1. Create a branch from `main`
2. Write tests for new functionality
3. Ensure all checks pass
4. Submit a PR with a clear description of changes

## Questions?

Open an issue if you have questions or need help.
