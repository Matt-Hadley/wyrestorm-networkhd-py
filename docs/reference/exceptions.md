# ⚠️ Exceptions

Exception classes for error handling.

{% set modules = discover_api_modules() %}

{% for module in modules.exceptions %}

## {{ get_module_icon(module) }} {{ get_module_title(module) }}

::: {{ module }}
    options:
      show_source: false
      members_order: source
      group_by_category: false
      show_if_no_docstring: false
      filters: ["!^_"]

{% endfor %}
