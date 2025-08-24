# 🎛️ Commands

All command modules for device control and API operations.

{% set modules = discover_api_modules() %}

{% for module in modules.commands %}

## {{ get_module_icon(module) }} {{ get_module_title(module) }}

::: {{ module }} options: show*source: false members_order: source group_by_category: false show_if_no_docstring: false
filters: ["!^*"]

{% endfor %}
