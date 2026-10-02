# Contributing

## Development Setup

Follow the setup steps in [README.md](README.md), then activate the project virtual environment before making changes.

## Before Opening A Pull Request

- Run `python -m compileall -q app.py build_database.py`.
- Keep API keys, virtual environments, IDE metadata, and generated vector indexes out of commits.
- Explain data or dependency changes in the pull request description.
- Keep commits focused and describe the user-facing or maintenance change clearly.

## Pull Requests

Small, focused pull requests are easier to review. Include screenshots when changing the Gradio interface and note any required rebuild of `chroma_db/`.
