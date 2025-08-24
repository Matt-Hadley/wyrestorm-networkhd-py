# 📚 Resources

Additional documentation and reference materials.

{% set resources = list_resources() %}

{% if resources %}

## Documentation Files

{% for file in resources %} {{ get_file_type_icon(file.extension) }} **[{{ file.name }}]({{ file.path }})**  
_{{ file.filename }}_ ({{ format_file_size(file.size) }})

{% endfor %}

---

**💡 Tip**: To add new resources, simply place files in the `docs/resources/` directory and they will automatically
appear here when the documentation is built.

{% else %} _No additional resources available at this time._

**📁 To add resources:**

1. Place files in `docs/resources/` directory
2. Rebuild the documentation with `make docs`
3. Files will automatically appear in this section

{% endif %}
