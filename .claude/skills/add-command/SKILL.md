---
name: add-command
description: Add or change a NetworkHD API command in this library — the command method, its typed response model if it returns data, and its tests — following the API PDF and the existing patterns. Use when implementing a command from NetworkHD_API_v6.7.pdf or fixing how one is sent or parsed.
---

# Add a NetworkHD API command

The spec is `docs/resources/NetworkHD_API_v6.7.pdf`. Each module in `src/wyrestorm_networkhd/commands/` holds one
chapter of it, with methods grouped under `# ====` banners named after the PDF section (e.g. `# 4.1 Session Alias Mode`).

## Steps

1. **Find the section in the PDF.** Read the command structure, response structure, examples and "applies to" list.
   Pick the module whose chapter it belongs to. A new chapter gets a new module and class, which must be added to
   `NHDAPI.__init__` in `commands/__init__.py`.
2. **Write the method** in the section's place in the module, keeping the section order of the PDF:
   - Name it after the command words (`config set session alias` → `config_set_session_alias`).
   - Use `Literal[...]` for fixed options.
   - Docstring has two parts, as in every existing method: the Google-style docstring (`Args`, `Returns`,
     `Command applies to`, `Notes`), then a second string starting `"""NetworkHDReferenceAPI` that copies the PDF's
     command/response structure and examples.
   - Build the command string, `await self.client.send_command(command)`, then validate with a helper from
     `commands/_response_helpers.py`:
     - `require_command_mirror` when the device echoes the command back
     - `require_contains` / `require_success_indicator` for other acknowledgements; real controllers start every
       reply with the command echo, so pass `strip_echo(response, command)` where the check or parser expects the
       bare reply
3. **If it returns data, add a model** in `models/api_query.py` (or `api_notifications.py` for notifications): a
   `@dataclass` with a `parse(cls, response: str)` classmethod. Its docstring shows the raw response format and an
   example from the PDF. Raise `ResponseError` when required fields are missing. `Version` is a small example to copy.
4. **Test it.**
   - Command tests in `tests/commands/test_<module>.py` use `echoing_client()` from `tests/commands/__init__.py` (it prepends
     the command echo to the scripted reply, like a real controller) and Arrange / Act / Assert. Cover each option, the exact command string sent, and a response that fails validation.
   - Parser tests in `tests/models/` use the PDF's response example, plus noisy and malformed input.
5. **Check:** `make dev-workflow` (format, lint, type and security checks, fast tests).

## Don'ts

- Don't edit `CHANGELOG.md`; release-please writes it from conventional commit messages (`feat:`, `fix:`).
- Don't add the command to `docs/reference/` by hand; the page is generated from the modules.
- If the PDF and the real device disagree, follow the device and note it under `Notes` in the docstring.
