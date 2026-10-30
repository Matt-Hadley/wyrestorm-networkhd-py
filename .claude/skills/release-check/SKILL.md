---
name: release-check
description: Check the library is ready to release, including that the Home Assistant integration still passes against it.
disable-model-invocation: true
---

# Release check

Run these in order and stop at the first failure, reporting its output.

1. **This repo:** `make health-check`. It runs config validation, format check, coverage tests, lint, type and security
   checks, the build and the docs build.
2. **What's going out:** list commits since the last tag with `git log $(git describe --tags --abbrev=0)..HEAD --oneline`.
   Flag any that release-please will skip because they aren't conventional commits (`feat:`, `fix:`, etc.), and any
   change to a public method's name, arguments or return type, which is a breaking change for the HA integration.
3. **Home Assistant integration** (`../wyrestorm-networkhd-ha`, which pins `wyrestorm-networkhd>=3.1.0,<4`):
   - `cd ../wyrestorm-networkhd-ha && make install` if it has no `.venv` yet.
   - Install this checkout over the released package: `.venv/bin/pip install -e ../wyrestorm-networkhd-py`.
   - Run `make test`.
   - Afterwards, put the released package back with `.venv/bin/pip install --force-reinstall wyrestorm-networkhd`.
4. **Report:** pass or fail for each step, the commits going out, and anything the HA integration needs changing.

Don't tag, push or merge the release-please PR. Releasing stays a manual step.
