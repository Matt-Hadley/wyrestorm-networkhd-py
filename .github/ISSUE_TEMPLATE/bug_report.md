---
name: 🐛 Bug Report
about: Report a bug to help us improve
title: "[BUG] "
labels: ["bug"]
assignees: ""
---

## What happened?

<!-- Describe the bug in a few sentences, including the full traceback if there is one -->

## What did you expect to happen?

<!-- Describe what you expected to happen -->

## Steps to reproduce

<!-- The smallest piece of code that shows the problem -->

1.
2.
3.

## Environment

- Controller model: <!-- NHD-000-CTL or NHD-CTL-PRO -->
- Controller version: <!-- output of `config get version`, e.g. API version v1.28, System version v9.4.7(...) -->
- Endpoint models involved: <!-- e.g. NHD-400-TX, NHD-400-RX -->
- Connection type: <!-- SSH or RS232 -->
- Library version: <!-- python -c "import wyrestorm_networkhd; print(wyrestorm_networkhd.__version__)" -->
- Python version:
- OS:

## Debug log

<!--
Run your code after:

    from wyrestorm_networkhd.logging_config import setup_logging
    setup_logging(level="DEBUG")

and paste the relevant output. Remove passwords, IP addresses and site names first.
-->

```text

```

## Additional context

<!-- Any other details that might help -->
