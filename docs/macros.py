"""MkDocs macros for dynamic content generation."""

import importlib.util
import pkgutil
import sys
from pathlib import Path


def define_env(env):
    """Define macros for MkDocs."""

    @env.macro
    def list_resources() -> list[dict[str, str]]:
        """Dynamically discover all resource files in docs/resources/.

        Returns:
            List of dictionaries with file information
        """
        resources = []
        resources_path = Path("docs/resources")

        if resources_path.exists():
            # Find all files (not just PDFs, for flexibility)
            for file_path in resources_path.glob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    # Get file info
                    file_info = {
                        "name": file_path.stem.replace("_", " ").replace("-", " ").title(),
                        "filename": file_path.name,
                        "path": f"resources/{file_path.name}",
                        "extension": file_path.suffix.lower(),
                        "size": file_path.stat().st_size if file_path.exists() else 0,
                    }
                    resources.append(file_info)

        # Sort by name for consistent ordering
        return sorted(resources, key=lambda x: x["name"])

    @env.macro
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB"]
        size = size_bytes
        unit_index = 0

        while size >= 1024 and unit_index < len(size_names) - 1:
            size /= 1024.0
            unit_index += 1

        if unit_index == 0:
            return f"{size:.0f}{size_names[unit_index]}"
        else:
            return f"{size:.1f}{size_names[unit_index]}"

    @env.macro
    def get_file_type_icon(extension: str) -> str:
        """Get an appropriate icon for the file type.

        Args:
            extension: File extension (e.g., '.pdf')

        Returns:
            Icon string
        """
        icons = {
            ".pdf": "📄",
            ".doc": "📝",
            ".docx": "📝",
            ".txt": "📝",
            ".md": "📝",
            ".zip": "📦",
            ".tar": "📦",
            ".gz": "📦",
            ".json": "🔧",
            ".xml": "🔧",
            ".csv": "📊",
            ".xlsx": "📊",
            ".png": "🖼️",
            ".jpg": "🖼️",
            ".jpeg": "🖼️",
            ".gif": "🖼️",
            ".mp4": "🎥",
            ".avi": "🎥",
            ".mov": "🎥",
        }
        return icons.get(extension.lower(), "📎")

    def _discover_package_modules(package_name: str) -> list[str]:
        """Helper to discover modules in a package.

        Args:
            package_name: Full package name (e.g., 'wyrestorm_networkhd.core')

        Returns:
            List of discovered module paths
        """
        modules = []
        try:
            spec = importlib.util.find_spec(package_name)
            if spec and spec.submodule_search_locations:
                for location in spec.submodule_search_locations:
                    for _, name, _ in pkgutil.iter_modules([location]):
                        if not name.startswith("_") and name != "__init__":
                            modules.append(f"{package_name}.{name}")
        except (ImportError, AttributeError):
            pass
        return modules

    @env.macro
    def discover_api_modules() -> dict[str, list[str]]:
        """Dynamically discover all API modules in the package.

        Returns:
            Dictionary with categorized module information
        """
        # Add src to path if not already there
        src_path = Path("src").absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        modules = {"core": [], "commands": [], "models": [], "exceptions": []}

        # Check if main package is available
        if importlib.util.find_spec("wyrestorm_networkhd") is None:
            return modules

        # Discover modules by category
        modules["core"] = _discover_package_modules("wyrestorm_networkhd.core")
        modules["commands"] = _discover_package_modules("wyrestorm_networkhd.commands")
        modules["models"] = _discover_package_modules("wyrestorm_networkhd.models")

        # Add main API class at the beginning
        modules["core"].insert(0, "wyrestorm_networkhd.NHDAPI")

        # Add exceptions
        modules["exceptions"].append("wyrestorm_networkhd.exceptions")

        return modules

    def _format_title_from_parts(parts: list[str]) -> str:
        """Helper to format title from word parts."""
        return " ".join(parts).title()

    def _handle_client_pattern(parts: list[str]) -> str:
        """Handle client_* naming pattern."""
        protocol = " ".join(parts[1:]).upper()
        return f"{protocol} Client"

    def _handle_api_pattern(parts: list[str], name: str) -> str:
        """Handle api_* naming pattern."""
        category = " ".join(parts[1:]).title()
        command_indicators = ["query", "endpoint", "config"]
        if "command" in name.lower() or any(cmd in category.lower() for cmd in command_indicators):
            return f"API {category} Commands"
        return f"API {category}"

    def _handle_command_pattern(parts: list[str]) -> str:
        """Handle *_commands naming pattern."""
        category = " ".join(parts[:-1]).title().replace(" ", " & ")
        return f"{category} Commands"

    @env.macro
    def get_module_title(module_name: str) -> str:
        """Convert module name to human-readable title dynamically.

        Args:
            module_name: Full module name (e.g., 'wyrestorm_networkhd.commands.api_query')

        Returns:
            Human-readable title
        """
        # Extract and clean the module name
        name = module_name.split(".")[-1]
        if name.startswith("_"):
            name = name[1:]  # Remove leading underscore

        # Handle all-caps modules (like NHDAPI)
        if name.isupper():
            if name.endswith("API"):
                base = name[:-3]
                return f"{base} API Interface" if base else "Main API Interface"
            return f"{name} Module"

        # Handle compound words with underscores
        if "_" in name:
            parts = name.split("_")

            # Pattern matching for common naming conventions
            if parts[0] == "client":
                return _handle_client_pattern(parts)
            elif parts[0] == "api":
                return _handle_api_pattern(parts, name)
            elif name.endswith(("_commands", "_command")):
                return _handle_command_pattern(parts)
            elif parts[-1] in ["control", "switch", "overlay"]:
                return _format_title_from_parts(parts)
            else:
                return _format_title_from_parts(parts)

        # Handle single word patterns
        single_word_mappings = {"exceptions": "Exception Classes", "models": "Data Models", "model": "Data Models"}
        if name in single_word_mappings:
            return single_word_mappings[name]

        # Default: convert to title case
        return name.title()

    @env.macro
    def get_module_icon(module_name: str) -> str:
        """Get an appropriate icon for the module type.

        Args:
            module_name: Full module name

        Returns:
            Icon emoji
        """
        name = module_name.split(".")[-1].lower()

        # Icon mapping with priority order (most specific first)
        icon_patterns = [
            (["client"], "🔌"),
            (["command", "_commands"], "⚡"),
            (["nhdapi", "api"], "🎛️"),
            (["model"], "📊"),
            (["exception"], "⚠️"),
            (["video", "multiview"], "📺"),
            (["audio"], "🔊"),
            (["matrix"], "🔀"),
        ]

        for patterns, icon in icon_patterns:
            if any(pattern in name for pattern in patterns):
                return icon

        return "📋"  # Default icon
