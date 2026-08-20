# Uvicorn Reload Policy

The AI Software Company generates files inside:

backend/app/workspace/

Generated workspace files are runtime artifacts and should not cause
the development server to restart.

For stable development, start Uvicorn without `--reload`.

Use:

backend\uvicorn_dev.ps1

Do not use:

uvicorn ... --reload

while testing agent workspace generation.
