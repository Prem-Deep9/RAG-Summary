# ai-generated-summaries

1. Install Python on your machine
   - Download and install from [python.org](https://python.org)
   - Version is mentioned in `.python-version` file
   - Ensure Python is added to your system PATH

2. Install uv globally
   - Run `pip install uv`
   - Run `uv --version` to check if uv is installed
   - Run `uv venv` to create a virtual environment and activate it

For new projects, you can use `uv init` to create a new project with uv.
uv add to install new libraries and add new dependencies to the pyproject.toml file.

3. Setup `.env` file with proper variables from `.env.example`

4. Install dependencies
   - Run `uv sync` to install all dependencies

5. Run `uv run uvicorn app.main:app --reload` to start the API

6. Updating Database Schema
   - Run `uv add psycopg2-binary`
   - Run `uv add sqlacodegen`
   They should be Installed automatically when you run `uv sync`
   - Run `uv run sqlacodegen postgresql://postgres:postgres@localhost:5432/postgres --outfile app/models/database.py` to generate/update the database schema
