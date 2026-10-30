# wyrestorm-networkhd-py

Async Python client for WyreStorm NetworkHD controllers (NHD-000-CTL, NHD-CTL-PRO), published on PyPI as
`wyrestorm-networkhd`. The Home Assistant integration in `../wyrestorm-networkhd-ha` depends on it, so a change to a
public method's name, arguments or return type breaks that integration.

## Layout

- `core/`: `NetworkHDClientSSH` and `NetworkHDClientRS232` on a shared `_client.py` base (sending, response
  handling, notification dispatch).
- `commands/`: one module per chapter of `docs/resources/NetworkHD_API_v6.7.pdf`, methods under `# ====` banners
  named after the PDF sections. `NHDAPI` (`commands/__init__.py`) creates one instance of each command class
  explicitly; a new module needs adding there.
- `models/`: dataclasses with a `parse()` classmethod for query responses (`api_query.py`) and notifications
  (`api_notifications.py`).
- `docs/`: MkDocs. The reference pages are generated from the modules; don't hand-edit them.

The PDF is the spec. To add or change a command, use the `add-command` skill. To compare a chapter of the PDF with the
code, use the `api-spec-auditor` agent.

## Commands

- `make install`: create `.venv` and install dev dependencies and pre-commit hooks. Run this first; there's no `.venv`
  until you do.
- `make dev-workflow`: format, lint, type and security checks, fast tests. Run before saying a change is done.
- `make test` / `make test-cov`: all tests, mocked clients only, no hardware needed.
- `make docs-serve`: preview the docs.
- `/release-check`: full pre-release check, including the HA integration's tests against this checkout.

## Conventions

- Ruff (line length 120) formats and fixes Python files after every edit via `.claude/settings.json`.
- Commits use conventional commit messages (`feat:`, `fix:`, `docs:`, `chore:`); release-please builds
  `CHANGELOG.md` and the version from them. Never edit `CHANGELOG.md` or `_version.py`.
- Each command method's docstring has the usual Google-style part, then a `"""NetworkHDReferenceAPI` part copied from
  the PDF.
